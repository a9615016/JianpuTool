\version "2.20.0"
#(set-global-staff-size 20)

% un-comment the next line to remove Lilypond tagline:
% \header { tagline="" }

% comment out the next line if you're debugging jianpu-ly
% (but best leave it un-commented in production, since
% the point-and-click locations won't go to the user input)
\pointAndClickOff

\paper {
  print-all-headers = ##t %% allow per-score headers

  % un-comment the next line for A5:
  % #(set-default-paper-size "a5" )

  % un-comment the next line for no page numbers:
  % print-page-number = ##f

  % un-comment the next 3 lines for a binding edge:
  % two-sided = ##t
  % inner-margin = 20\mm
  % outer-margin = 10\mm

  % un-comment the next line for a more space-saving header layout:
  % scoreTitleMarkup = \markup { \center-column { \fill-line { \magnify #1.5 { \bold { \fromproperty #'header:dedication } } \magnify #1.5 { \bold { \fromproperty #'header:title } } \fromproperty #'header:composer } \fill-line { \fromproperty #'header:instrument \fromproperty #'header:subtitle \smaller{\fromproperty #'header:subsubtitle } } } }
}

%% 2-dot and 3-dot articulations
#(append! default-script-alist
   (list
    `(two-dots
       . (
           (stencil . ,ly:text-interface::print)
           (text . ,#{ \markup \override #'(font-encoding . latin1) \center-align \bold ":" #})
           (padding . 0.20)
           (avoid-slur . inside)
           (side-axis . ,Y)
           (direction . ,UP)))))
#(append! default-script-alist
   (list
    `(three-dots
       . (
           (stencil . ,ly:text-interface::print)
           (text . ,#{ \markup \override #'(font-encoding . latin1) \center-align \bold "⋮" #})
           (padding . 0.30)
           (avoid-slur . inside)
           (side-axis . ,Y)
           (direction . ,UP)))))
"two-dots" =
#(make-articulation 'two-dots)

"three-dots" =
#(make-articulation 'three-dots)

\layout {
  \context {
    \Score
    scriptDefinitions = #default-script-alist
  }
}

note-mod =
#(define-music-function
     (text note)
     (markup? ly:music?)
   #{
     \tweak NoteHead.stencil #ly:text-interface::print
     \tweak NoteHead.text
        \markup \lower #0.5 \sans \bold #text
     \tweak Rest.stencil #ly:text-interface::print
     \tweak Rest.text
        \markup \lower #0.5 \sans \bold #text
     #note
   #})
#(define (flip-beams grob)
   (ly:grob-set-property!
    grob 'stencil
    (ly:stencil-translate
     (let* ((stl (ly:grob-property grob 'stencil))
            (centered-stl (ly:stencil-aligned-to stl Y DOWN)))
       (ly:stencil-translate-axis
        (ly:stencil-scale centered-stl 1 -1)
        (* (- (car (ly:stencil-extent stl Y)) (car (ly:stencil-extent centered-stl Y))) 0) Y))
     (cons 0 -0.8))))

%=======================================================
#(define-event-class 'jianpu-grace-curve-event 'span-event)

#(define (add-grob-definition grob-name grob-entry)
   (set! all-grob-descriptions
         (cons ((@@ (lily) completize-grob-entry)
                (cons grob-name grob-entry))
               all-grob-descriptions)))

#(define (jianpu-grace-curve-stencil grob)
   (let* ((elts (ly:grob-object grob 'elements))
          (refp-X (ly:grob-common-refpoint-of-array grob elts X))
          (X-ext (ly:relative-group-extent elts refp-X X))
          (refp-Y (ly:grob-common-refpoint-of-array grob elts Y))
          (Y-ext (ly:relative-group-extent elts refp-Y Y))
          (direction (ly:grob-property grob 'direction RIGHT))
          (x-start (* 0.5 (+ (car X-ext) (cdr X-ext))))
          (y-start (+ (car Y-ext) 0.32))
          (x-start2 (if (eq? direction RIGHT)(+ x-start 0.5)(- x-start 0.5)))
          (x-end (if (eq? direction RIGHT)(+ (cdr X-ext) 0.2)(- (car X-ext) 0.2)))
          (y-end (- y-start 0.5))
          (stil (ly:make-stencil `(path 0.1
                                        (moveto ,x-start ,y-start
                                         curveto ,x-start ,y-end ,x-start ,y-end ,x-start2 ,y-end
                                         lineto ,x-end ,y-end))
                                  X-ext
                                  Y-ext))
          (offset (ly:grob-relative-coordinate grob refp-X X)))
     (ly:stencil-translate-axis stil (- offset) X)))

#(add-grob-definition
  'JianpuGraceCurve
  `(
     (stencil . ,jianpu-grace-curve-stencil)
     (meta . ((class . Spanner)
              (interfaces . ())))))

#(define jianpu-grace-curve-types
   '(
      (JianpuGraceCurveEvent
       . ((description . "Used to signal where curve encompassing music start and stop.")
          (types . (general-music jianpu-grace-curve-event span-event event))
          ))
      ))

#(set!
  jianpu-grace-curve-types
  (map (lambda (x)
         (set-object-property! (car x)
           'music-description
           (cdr (assq 'description (cdr x))))
         (let ((lst (cdr x)))
           (set! lst (assoc-set! lst 'name (car x)))
           (set! lst (assq-remove! lst 'description))
           (hashq-set! music-name-to-property-table (car x) lst)
           (cons (car x) lst)))
    jianpu-grace-curve-types))

#(set! music-descriptions
       (append jianpu-grace-curve-types music-descriptions))

#(set! music-descriptions
       (sort music-descriptions alist<?))


#(define (add-bound-item spanner item)
   (if (null? (ly:spanner-bound spanner LEFT))
       (ly:spanner-set-bound! spanner LEFT item)
       (ly:spanner-set-bound! spanner RIGHT item)))

jianpuGraceCurveEngraver =
#(lambda (context)
   (let ((span '())
         (finished '())
         (current-event '())
         (event-start '())
         (event-stop '()))
     `(
       (listeners
        (jianpu-grace-curve-event .
          ,(lambda (engraver event)
             (if (= START (ly:event-property event 'span-direction))
                 (set! event-start event)
                 (set! event-stop event)))))

       (acknowledgers
        (note-column-interface .
          ,(lambda (engraver grob source-engraver)
             (if (ly:spanner? span)
                 (begin
                  (ly:pointer-group-interface::add-grob span 'elements grob)
                  (add-bound-item span grob)))
             (if (ly:spanner? finished)
                 (begin
                  (ly:pointer-group-interface::add-grob finished 'elements grob)
                  (add-bound-item finished grob)))))
        (inline-accidental-interface .
          ,(lambda (engraver grob source-engraver)
             (if (ly:spanner? span)
                 (begin
                  (ly:pointer-group-interface::add-grob span 'elements grob)))
             (if (ly:spanner? finished)
                 (ly:pointer-group-interface::add-grob finished 'elements grob))))
        (script-interface .
          ,(lambda (engraver grob source-engraver)
             (if (ly:spanner? span)
                 (begin
                  (ly:pointer-group-interface::add-grob span 'elements grob)))
             (if (ly:spanner? finished)
                 (ly:pointer-group-interface::add-grob finished 'elements grob)))))
       
       (process-music .
         ,(lambda (trans)
            (if (ly:stream-event? event-stop)
                (if (null? span)
                    (ly:warning "No start to this curve.")
                    (begin
                     (set! finished span)
                     (ly:engraver-announce-end-grob trans finished event-start)
                     (set! span '())
                     (set! event-stop '()))))
            (if (ly:stream-event? event-start)
                (begin
                 (set! span (ly:engraver-make-grob trans 'JianpuGraceCurve event-start))
                 (set! event-start '())))))
       
       (stop-translation-timestep .
         ,(lambda (trans)
            (if (and (ly:spanner? span)
                     (null? (ly:spanner-bound span LEFT)))
                (ly:spanner-set-bound! span LEFT
                  (ly:context-property context 'currentMusicalColumn)))
            (if (ly:spanner? finished)
                (begin
                 (if (null? (ly:spanner-bound finished RIGHT))
                     (ly:spanner-set-bound! finished RIGHT
                       (ly:context-property context 'currentMusicalColumn)))
                 (set! finished '())
                 (set! event-start '())
                 (set! event-stop '())))))
       
       (finalize
        (lambda (trans)
          (if (ly:spanner? finished)
              (begin
               (if (null? (ly:spanner-bound finished RIGHT))
                   (set! (ly:spanner-bound finished RIGHT)
                         (ly:context-property context 'currentMusicalColumn)))
               (set! finished '())))))
       )))

jianpuGraceCurveStart =
#(make-span-event 'JianpuGraceCurveEvent START)

jianpuGraceCurveEnd =
#(make-span-event 'JianpuGraceCurveEvent STOP)
%===========================================================

%{ The jianpu-ly input was:
OctavesAfter
title=Music21 Fragment
composer=Music21
instrument=Electric Piano
4/4
4=120
0  - -  
7,,bs   
0s   
3,q   
0s   
3,q   
2,q.   
0d   
1,s   ~
1,   
0   
7,,q   
1s1,
0s   
7,,q   
6,,q6,
0q   
0   
1,q   
0   
1,q   
6,q   ~
6,s   
0s   
1,s   ~
]
1,s   
0d   
1s   ~
1d   
]
0s   
6,q   
0d   
1q   
5,   ~
]
5,d   
]
0s   
1q   
3,q   ~
3,q   
0q   
1,q   
0q   
1q   
]
6,q   
1s   
0s   
6,   
5,#q   
]
7,q.   
0s   
5,q   
3,q   
0q   
3,q.   
0   
0q   
4,s4
0s   
4,q   
0s   
3,q   
0s   
7,bs   
0s   
3,q   
2,s   
0s   
2,s   
2,q.   
0  - -  
1,q.   
7,,bs   
0s   
2,2
0q   
2,q   
5,q   
0s   
1,s   
0s   
7,,q   
]
1,q   
0q   
]
7,s   
0q.   
1q   
0d   
]
6,q.   
0d   
1s   ~
]
1q   
]
5,q   
0   
0q   
1q   
6,q   
0q   
1q   
6,q   
1s   
0s   
5,q   
0s   
5,s   
0s   
3,q   
0d   
1,q   
0q   
]
5,q   ~
5,q   
1,q   
]
7,,q   
0q   
]
5,q   
0q   
3,q   ~
3,s   
0d   
2,s   ~
2,   
1,   
0d   
1,   
0s   
7,,q   ~
7,,q   
]
0s   
1,q   
1,   ~
]
1,  - - -  
]
1,   ~
1,s   
0.   
4,,   ~
4,,q.   
7,,q   
0   
]
0  -  
0q   
WithStaff NextPart
instrument=Electric Piano
4/4
0  - -  
3,s   ~
0q   
0q. 0d 0s 0 0 0q 0s 0s 0q 0q 0q 0 0q 0 0q 0q 0s 0s 0s ] 0s 0d 0s 0d ] 0s 0q 0d 0q 0 ] 0d ] 0s 0q 0q 0q 0q 0q 0q 0q ] 0q 0s 0s 0 0q ]
0.   
2,   
0  -  
0s   
0  -  
4,q   
0  - - -  
0s 0q. 0 - -
0.   
2,s2
0  -  
0q ] 0q 0q ] 0s 0q. 0q 0d ] 0q. 0d 0s ] 0q ]
0  -  
6,q   
0   
0   
0q 0s 0s 0s 0q 0d 0q 0q ] 0q 0q 0q ] 0q 0q ]
0s   
4,q   
0.   
1's   
0.   
0q ] 0s 0q 0 ] 0 - - - ] 0 0s 0. 0 0q. 0q 0 ] 0 - 0q
WithStaff NextPart
instrument=Electric Piano
4/4
0 - -
0s
0s
0q
0s
0  -  
1q   
0   
1,q   
0   
0s   
0  -  
7,,q   
0.   
0s 0s 0s ] 0s 0d 0s 0d ] 0s 0q 0d 0q 0 ] 0d ] 0s 0q 0q 0q 0q 0q 0q 0q ] 0q 0s 0s 0 0q ] 0q. 0s 0q 0q 0q 0q. 0 0q 0s 0s 0q 0s 0q 0s 0s 0s 0q 0s 0s 0s 0q. 0 - - 0q. 0s 0s 0 0q 0q 0q 0s 0s 0s 0q ] 0q 0q ] 0s 0q. 0q 0d ] 0q. 0d 0s ] 0q ] 0q 0 0q 0q 0q 0q 0q 0q 0s 0s 0q 0s 0s 0s 0q 0d 0q 0q ] 0q 0q 0q ] 0q 0q ] 0q 0q 0q 0s 0d 0s 0 0 0d 0 0s 0q 0q ] 0s 0q 0 ] 0 - - - ] 0 0s 0. 0 0q. 0q 0 ] 0 - 0q
WithStaff NextPart
%}


\score {
<< \override Score.BarNumber #'break-visibility = #center-visible
\override Score.BarNumber #'Y-offset = -1
\set Score.barNumberVisibility = #(every-nth-bar-number-visible 5)

%% === BEGIN JIANPU STAFF ===
    \new RhythmicStaff \with {
    \consists "Accidental_engraver" 
    \consists \jianpuGraceCurveEngraver
   %% Limit space between Jianpu and corresponding-Western staff
   \override VerticalAxisGroup.staff-staff-spacing = #'((minimum-distance . 7) (basic-distance . 7) (stretchability . 0))

    % Get rid of the stave but not the barlines:
    \override StaffSymbol #'line-count = #0 % tested in 2.15.40, 2.16.2, 2.18.0, 2.18.2, 2.20.0 and 2.22.2
    \override BarLine #'bar-extent = #'(-2 . 2) % LilyPond 2.18: please make barlines as high as the time signature even though we're on a RhythmicStaff (2.16 and 2.15 don't need this although its presence doesn't hurt; Issue 3685 seems to indicate they'll fix it post-2.18)
    $(add-grace-property 'Voice 'Stem 'direction DOWN)
    $(add-grace-property 'Voice 'Slur 'direction UP)
    $(add-grace-property 'Voice 'Stem 'length-fraction 0.5)
    $(add-grace-property 'Voice 'Beam 'beam-thickness 0.1)
    $(add-grace-property 'Voice 'Beam 'length-fraction 0.3)
    $(add-grace-property 'Voice 'Beam 'after-line-breaking flip-beams)
    $(add-grace-property 'Voice 'Beam 'Y-offset 2.5)
    $(add-grace-property 'Voice 'NoteHead 'Y-offset 2.5)
    }
    { \new Voice="W" {
    \override Beam #'transparent = ##f
    \override Stem #'direction = #DOWN
    \override Tie #'staff-position = #2.5
    \tupletUp
    \tieUp
    \override Stem #'length-fraction = #0.5
    \override Beam #'beam-thickness = #0.1
    \override Beam #'length-fraction = #0.5
    \override Beam.after-line-breaking = #flip-beams
    \override Voice.Rest #'style = #'neomensural % this size tends to line up better (we'll override the appearance anyway)
    \override Accidental #'font-size = #-4
    \override TupletBracket #'bracket-visibility = ##t

    \override Staff.TimeSignature #'style = #'numbered
    \override Staff.Stem #'transparent = ##t
     \time 4/4 \tempo 4=120  \note-mod "0" r4  \note-mod "–" r4  \note-mod "–" r4 \set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "7" \once \tweak Accidental.extra-offset #'(0 . 0.7)bes16-\tweak #'X-offset #0.6 _\two-dots [
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "3" e8-\tweak #'X-offset #0.6 _. ]
| %{ bar 2: %} \set stemLeftBeamCount = #0
\set stemRightBeamCount = #2
 \note-mod "0" c16[
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "3" e8-\tweak #'X-offset #0.6 _. 
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "2" d8.-\tweak #'X-offset #0.6 _. 
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #3
 \note-mod "0" r32
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "1" c16-\tweak #'X-offset #0.6 _. 
]  ~  \note-mod "1" c4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
 \note-mod "0" r4 \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "7" b8-\tweak #'X-offset #0.6 _\two-dots [
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #2
< \note-mod "1" c'  \tweak #'Y-offset #2.0 \note-mod "1" c'  >16-\tweak #'X-offset #0.6 _. 
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "7" b8-\tweak #'X-offset #0.6 _\two-dots 
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
< \note-mod "6" a'  \tweak #'Y-offset #3.0 \note-mod "6" a \tweak #'Y-offset #1.7 -\tweak #'X-offset #0.6 _.  >8-\tweak #'X-offset #0.6 _\two-dots 
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
]   \note-mod "0" r4 \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" c8-\tweak #'X-offset #0.6 _. [
]   \note-mod "0" r4 \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" c8-\tweak #'X-offset #0.6 _. [
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "6" a8-\tweak #'X-offset #0.6 _. 
~ \set stemLeftBeamCount = #1
\set stemRightBeamCount = #2
 \note-mod "6" a16-\tweak #'X-offset #0.6 _. 
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "1" c16-\tweak #'X-offset #0.6 _. 
~ } \set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "1" c16-\tweak #'X-offset #0.6 _. 
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #3
 \note-mod "0" r32]
\set stemLeftBeamCount = #0
\set stemRightBeamCount = #2
 \note-mod "1" c16[
~ \set stemLeftBeamCount = #2
\set stemRightBeamCount = #3
 \note-mod "1" c32
} \set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "6" a8-\tweak #'X-offset #0.6 _. 
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #3
 \note-mod "0" r32
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "1" c8
]   \note-mod "5" g4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
~ } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #3
 \note-mod "5" g32-\tweak #'X-offset #0.6 _. [
} \set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "1" c8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "3" e8-\tweak #'X-offset #0.6 _. 
~ \set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "3" e8-\tweak #'X-offset #0.6 _. 
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "1" c8-\tweak #'X-offset #0.6 _. 
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "1" c8
} \set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "6" a8-\tweak #'X-offset #0.6 _. 
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #2
 \note-mod "1" c16
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "0" r16
]   \note-mod "6" a4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "5" \once \tweak Accidental.extra-offset #'(0 . 0.7)gis8-\tweak #'X-offset #0.6 _. [
} \set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "7" b8.-\tweak #'X-offset #0.6 _. 
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "5" \once \tweak Accidental.extra-offset #'(0 . 0.7)g8-\tweak #'X-offset #0.6 _. 
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "3" e8-\tweak #'X-offset #0.6 _. 
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "3" e8.-\tweak #'X-offset #0.6 _. 
]   \note-mod "0" r4 \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "0" c8[
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #2
< \note-mod "4" f'  \tweak #'Y-offset #2.0 \note-mod "4" f'  >16-\tweak #'X-offset #0.6 _. 
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "4" f8-\tweak #'X-offset #0.6 _. 
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "3" e8-\tweak #'X-offset #0.6 _. 
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "7" \once \tweak Accidental.extra-offset #'(0 . 0.7)bes16-\tweak #'X-offset #0.6 _. 
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "3" e8-\tweak #'X-offset #0.6 _. 
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #2
 \note-mod "2" d16-\tweak #'X-offset #0.6 _. 
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "2" d16-\tweak #'X-offset #0.6 _. 
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "2" d8.-\tweak #'X-offset #0.6 _. 
]   \note-mod "0" r4  \note-mod "–" r4  \note-mod "–" r4 \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" c8.-\tweak #'X-offset #0.6 _. [
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "7" \once \tweak Accidental.extra-offset #'(0 . 0.7)bes16-\tweak #'X-offset #0.6 _\two-dots 
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "0" r16
]  < \note-mod "2" d'  \tweak #'Y-offset #2.0 \note-mod "2" d'  >4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
\set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "0" c8[
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "2" d8-\tweak #'X-offset #0.6 _. 
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "5" g8-\tweak #'X-offset #0.6 _. 
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "1" c16-\tweak #'X-offset #0.6 _. 
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "7" \once \tweak Accidental.extra-offset #'(0 . 0.7)b8-\tweak #'X-offset #0.6 _\two-dots 
} \set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "1" c8-\tweak #'X-offset #0.6 _. 
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
} \set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "7" \once \tweak Accidental.extra-offset #'(0 . 0.7)b16-\tweak #'X-offset #0.6 _. 
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8.
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "1" c8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #3
 \note-mod "0" r32]
} \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "6" a8.-\tweak #'X-offset #0.6 _. [
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #3
 \note-mod "0" r32
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "1" c16
~ } \set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "1" c8
} \set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "5" g8-\tweak #'X-offset #0.6 _. 
]   \note-mod "0" r4 \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "0" c8[
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "1" c8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "6" a8-\tweak #'X-offset #0.6 _. 
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "1" c8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "6" a8-\tweak #'X-offset #0.6 _. 
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #2
 \note-mod "1" c16
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "5" g8-\tweak #'X-offset #0.6 _. 
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "5" g16-\tweak #'X-offset #0.6 _. 
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "3" e8-\tweak #'X-offset #0.6 _. 
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #3
 \note-mod "0" r32
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "1" c8-\tweak #'X-offset #0.6 _. ]
\set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "0" c8[
} \set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "5" g8-\tweak #'X-offset #0.6 _. ]
~ \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" g8-\tweak #'X-offset #0.6 _. [
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "1" c8-\tweak #'X-offset #0.6 _. ]
} \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "7" b8-\tweak #'X-offset #0.6 _\two-dots [
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8]
} \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "5" g8-\tweak #'X-offset #0.6 _. [
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8]
\set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "3" e8-\tweak #'X-offset #0.6 _. [
~ \set stemLeftBeamCount = #1
\set stemRightBeamCount = #2
 \note-mod "3" e16-\tweak #'X-offset #0.6 _. 
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #3
 \note-mod "0" r32
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "2" d16-\tweak #'X-offset #0.6 _. 
]  ~  \note-mod "2" d4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
 \note-mod "1" c4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
\set stemLeftBeamCount = #0
\set stemRightBeamCount = #3
 \note-mod "0" c32[
]   \note-mod "1" c4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
\set stemLeftBeamCount = #0
\set stemRightBeamCount = #2
 \note-mod "0" c16[
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "7" b8-\tweak #'X-offset #0.6 _\two-dots ]
~ \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "7" b8-\tweak #'X-offset #0.6 _\two-dots [
} \set stemLeftBeamCount = #1
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "1" c8-\tweak #'X-offset #0.6 _. 
]   \note-mod "1" c4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
~ } \once \override Tie #'transparent = ##t \once \override Tie #'staff-position = #0  \note-mod "1" c4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
 ~ \once \override Tie #'transparent = ##t \once \override Tie #'staff-position = #0  \note-mod "–" c4
 ~ \once \override Tie #'transparent = ##t \once \override Tie #'staff-position = #0  \note-mod "–" c4
 ~  \note-mod "–" c4 }  \note-mod "1" c4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
~ \set stemLeftBeamCount = #0
\set stemRightBeamCount = #2
 \note-mod "1" c16-\tweak #'X-offset #0.6 _. [
]   \note-mod "0" r4.  \note-mod "4" f4-\tweak #'Y-offset #-2 -\tweak #'X-offset #0.6 _\two-dots 
~ \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "4" f8.-\tweak #'X-offset #0.6 _\two-dots [
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "7" b8-\tweak #'X-offset #0.6 _\two-dots 
]   \note-mod "0" r4 }  \note-mod "0" r4  \note-mod "–" r4 \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "0" c8[]
\bar "|." } }
% === END JIANPU STAFF ===


%% === BEGIN JIANPU STAFF ===
    \new RhythmicStaff \with {
    \consists "Accidental_engraver" 
    \consists \jianpuGraceCurveEngraver
   %% Limit space between Jianpu and corresponding-Western staff
   \override VerticalAxisGroup.staff-staff-spacing = #'((minimum-distance . 7) (basic-distance . 7) (stretchability . 0))

    % Get rid of the stave but not the barlines:
    \override StaffSymbol #'line-count = #0 % tested in 2.15.40, 2.16.2, 2.18.0, 2.18.2, 2.20.0 and 2.22.2
    \override BarLine #'bar-extent = #'(-2 . 2) % LilyPond 2.18: please make barlines as high as the time signature even though we're on a RhythmicStaff (2.16 and 2.15 don't need this although its presence doesn't hurt; Issue 3685 seems to indicate they'll fix it post-2.18)
    $(add-grace-property 'Voice 'Stem 'direction DOWN)
    $(add-grace-property 'Voice 'Slur 'direction UP)
    $(add-grace-property 'Voice 'Stem 'length-fraction 0.5)
    $(add-grace-property 'Voice 'Beam 'beam-thickness 0.1)
    $(add-grace-property 'Voice 'Beam 'length-fraction 0.3)
    $(add-grace-property 'Voice 'Beam 'after-line-breaking flip-beams)
    $(add-grace-property 'Voice 'Beam 'Y-offset 2.5)
    $(add-grace-property 'Voice 'NoteHead 'Y-offset 2.5)
    }
    { \new Voice="X" {
    \override Beam #'transparent = ##f
    \override Stem #'direction = #DOWN
    \override Tie #'staff-position = #2.5
    \tupletUp
    \tieUp
    \override Stem #'length-fraction = #0.5
    \override Beam #'beam-thickness = #0.1
    \override Beam #'length-fraction = #0.5
    \override Beam.after-line-breaking = #flip-beams
    \override Voice.Rest #'style = #'neomensural % this size tends to line up better (we'll override the appearance anyway)
    \override Accidental #'font-size = #-4
    \override TupletBracket #'bracket-visibility = ##t

    \override Staff.TimeSignature #'style = #'numbered
    \override Staff.Stem #'transparent = ##t
     \time 4/4  \note-mod "0" r4  \note-mod "–" r4  \note-mod "–" r4 \set stemLeftBeamCount = #0
\set stemRightBeamCount = #2
 \note-mod "3" e16-\tweak #'X-offset #0.6 _. [
~ \set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8.
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #3
 \note-mod "0" r32
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "0" r16
]   \note-mod "0" r4  \note-mod "0" r4 \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "0" c8[
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
]   \note-mod "0" r4 \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "0" c8[
]   \note-mod "0" r4 \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "0" c8[
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "0" r16
} \set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #3
 \note-mod "0" r32]
\set stemLeftBeamCount = #0
\set stemRightBeamCount = #2
 \note-mod "0" c16[
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #3
 \note-mod "0" r32
} \set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #3
 \note-mod "0" r32
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
]   \note-mod "0" r4 } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #3
 \note-mod "0" c32[
} \set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
} \set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "0" r16
]   \note-mod "0" r4 \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "0" c8[
]  }  \note-mod "0" r4.  \note-mod "2" d4-\tweak #'Y-offset #-1.2 -\tweak #'X-offset #0.6 _. 
 \note-mod "0" r4  \note-mod "–" r4 \set stemLeftBeamCount = #0
\set stemRightBeamCount = #2
 \note-mod "0" c16[
]   \note-mod "0" r4  \note-mod "–" r4 \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "4" f8-\tweak #'X-offset #0.6 _. [
]   \note-mod "0" r4  \note-mod "–" r4  \note-mod "–" r4  \note-mod "–" r4 \set stemLeftBeamCount = #0
\set stemRightBeamCount = #2
 \note-mod "0" c16[
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8.
]   \note-mod "0" r4  \note-mod "–" r4  \note-mod "–" r4  \note-mod "0" r4. \set stemLeftBeamCount = #0
\set stemRightBeamCount = #2
< \note-mod "2" d'  \tweak #'Y-offset #2.0 \note-mod "2" d'  >16-\tweak #'X-offset #0.6 _. [
]   \note-mod "0" r4  \note-mod "–" r4 \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "0" c8[
} \set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
} \set stemLeftBeamCount = #1
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8.
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #3
 \note-mod "0" r32
} \set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8.]
\set stemLeftBeamCount = #0
\set stemRightBeamCount = #3
 \note-mod "0" c32[
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "0" r16
} \set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
]  }  \note-mod "0" r4  \note-mod "–" r4 \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "6" a8-\tweak #'X-offset #0.6 _. [
]   \note-mod "0" r4  \note-mod "0" r4 \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "0" c8[
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #3
 \note-mod "0" r32
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
} \set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
} \set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
} \set stemLeftBeamCount = #1
\set stemRightBeamCount = #2
 \note-mod "0" r16]
\set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "4" f8-\tweak #'X-offset #0.6 _. [
]   \note-mod "0" r4. \set stemLeftBeamCount = #0
\set stemRightBeamCount = #2
 \note-mod "1" c16^.[
]   \note-mod "0" r4. \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "0" c8[
} \set stemLeftBeamCount = #1
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8]
 \note-mod "0" r4 }  \note-mod "0" r4  \note-mod "–" r4  \note-mod "–" r4  \note-mod "–" r4 }  \note-mod "0" r4 \set stemLeftBeamCount = #0
\set stemRightBeamCount = #2
 \note-mod "0" c16[
]   \note-mod "0" r4.  \note-mod "0" r4 \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "0" c8.[
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8]
 \note-mod "0" r4 }  \note-mod "0" r4  \note-mod "–" r4 \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "0" c8[] } }
% === END JIANPU STAFF ===


%% === BEGIN JIANPU STAFF ===
    \new RhythmicStaff \with {
    \consists "Accidental_engraver" 
    \consists \jianpuGraceCurveEngraver
   %% Limit space between Jianpu and corresponding-Western staff
   \override VerticalAxisGroup.staff-staff-spacing = #'((minimum-distance . 7) (basic-distance . 7) (stretchability . 0))

    % Get rid of the stave but not the barlines:
    \override StaffSymbol #'line-count = #0 % tested in 2.15.40, 2.16.2, 2.18.0, 2.18.2, 2.20.0 and 2.22.2
    \override BarLine #'bar-extent = #'(-2 . 2) % LilyPond 2.18: please make barlines as high as the time signature even though we're on a RhythmicStaff (2.16 and 2.15 don't need this although its presence doesn't hurt; Issue 3685 seems to indicate they'll fix it post-2.18)
    $(add-grace-property 'Voice 'Stem 'direction DOWN)
    $(add-grace-property 'Voice 'Slur 'direction UP)
    $(add-grace-property 'Voice 'Stem 'length-fraction 0.5)
    $(add-grace-property 'Voice 'Beam 'beam-thickness 0.1)
    $(add-grace-property 'Voice 'Beam 'length-fraction 0.3)
    $(add-grace-property 'Voice 'Beam 'after-line-breaking flip-beams)
    $(add-grace-property 'Voice 'Beam 'Y-offset 2.5)
    $(add-grace-property 'Voice 'NoteHead 'Y-offset 2.5)
    }
    { \new Voice="Y" {
    \override Beam #'transparent = ##f
    \override Stem #'direction = #DOWN
    \override Tie #'staff-position = #2.5
    \tupletUp
    \tieUp
    \override Stem #'length-fraction = #0.5
    \override Beam #'beam-thickness = #0.1
    \override Beam #'length-fraction = #0.5
    \override Beam.after-line-breaking = #flip-beams
    \override Voice.Rest #'style = #'neomensural % this size tends to line up better (we'll override the appearance anyway)
    \override Accidental #'font-size = #-4
    \override TupletBracket #'bracket-visibility = ##t

    \override Staff.TimeSignature #'style = #'numbered
    \override Staff.Stem #'transparent = ##t
     \time 4/4  \note-mod "0" r4  \note-mod "–" r4  \note-mod "–" r4 \set stemLeftBeamCount = #0
\set stemRightBeamCount = #2
 \note-mod "0" c16[
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8]
| %{ bar 2: %} \set stemLeftBeamCount = #0
\set stemRightBeamCount = #2
 \note-mod "0" c16[
]   \note-mod "0" r4  \note-mod "–" r4 \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" c8[
]   \note-mod "0" r4 \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "1" c8-\tweak #'X-offset #0.6 _. [
]   \note-mod "0" r4 \set stemLeftBeamCount = #0
\set stemRightBeamCount = #2
 \note-mod "0" c16[
]   \note-mod "0" r4  \note-mod "–" r4 \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "7" b8-\tweak #'X-offset #0.6 _\two-dots []
 \note-mod "0" r4. \set stemLeftBeamCount = #0
\set stemRightBeamCount = #2
 \note-mod "0" c16[
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "0" r16]
\set stemLeftBeamCount = #0
\set stemRightBeamCount = #2
 \note-mod "0" c16[
} \set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #3
 \note-mod "0" r32
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #3
 \note-mod "0" r32]
} \set stemLeftBeamCount = #0
\set stemRightBeamCount = #2
 \note-mod "0" c16[
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #3
 \note-mod "0" r32
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
]   \note-mod "0" r4 } \set stemLeftBeamCount = #0
\set stemRightBeamCount = #3
 \note-mod "0" c32[
} \set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
} \set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #2
 \note-mod "0" r16]
\set stemLeftBeamCount = #0
\set stemRightBeamCount = #2
 \note-mod "0" c16[
]   \note-mod "0" r4 \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "0" c8[
} \set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8.
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8.]
 \note-mod "0" r4 \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "0" c8[
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "0" r16]
\set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "0" c8[
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "0" r16]
\set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "0" c8[
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "0" r16]
\set stemLeftBeamCount = #0
\set stemRightBeamCount = #2
 \note-mod "0" c16[
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8.]
 \note-mod "0" r4  \note-mod "–" r4  \note-mod "–" r4 \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "0" c8.[
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #2
 \note-mod "0" r16]
\set stemLeftBeamCount = #0
\set stemRightBeamCount = #2
 \note-mod "0" c16[
]   \note-mod "0" r4 \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "0" c8[
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #2
 \note-mod "0" r16]
\set stemLeftBeamCount = #0
\set stemRightBeamCount = #2
 \note-mod "0" c16[
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8]
} \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "0" c8[
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8]
} \set stemLeftBeamCount = #0
\set stemRightBeamCount = #2
 \note-mod "0" c16[
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8.]
\set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "0" c8[
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #3
 \note-mod "0" r32
} \set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8.
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #3
 \note-mod "0" r32
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "0" r16
} \set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
} \set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
]   \note-mod "0" r4 \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "0" c8[
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #2
 \note-mod "0" r16]
\set stemLeftBeamCount = #0
\set stemRightBeamCount = #2
 \note-mod "0" c16[
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #2
 \note-mod "0" r16]
\set stemLeftBeamCount = #0
\set stemRightBeamCount = #2
 \note-mod "0" c16[
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8]
\set stemLeftBeamCount = #0
\set stemRightBeamCount = #3
 \note-mod "0" c32[
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
} \set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
} \set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
} \set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #3
 \note-mod "0" r32
\set stemLeftBeamCount = #2
\set stemRightBeamCount = #2
 \note-mod "0" r16
]   \note-mod "0" r4  \note-mod "0" r4 \set stemLeftBeamCount = #0
\set stemRightBeamCount = #3
 \note-mod "0" c32[
]   \note-mod "0" r4 \set stemLeftBeamCount = #0
\set stemRightBeamCount = #2
 \note-mod "0" c16[
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
} \set stemLeftBeamCount = #1
\set stemRightBeamCount = #2
 \note-mod "0" r16
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
]   \note-mod "0" r4 }  \note-mod "0" r4  \note-mod "–" r4  \note-mod "–" r4  \note-mod "–" r4 }  \note-mod "0" r4 \set stemLeftBeamCount = #0
\set stemRightBeamCount = #2
 \note-mod "0" c16[
]   \note-mod "0" r4.  \note-mod "0" r4 \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "0" c8.[
\set stemLeftBeamCount = #1
\set stemRightBeamCount = #1
 \note-mod "0" r8
]   \note-mod "0" r4 }  \note-mod "0" r4  \note-mod "–" r4 \set stemLeftBeamCount = #0
\set stemRightBeamCount = #1
 \note-mod "0" c8[] } }
% === END JIANPU STAFF ===

>>
\header{
title="Music21 Fragment"
composer="Music21"
}
\layout{
  \context {
    \Global
    \grobdescriptions #all-grob-descriptions
  }
} }
\score {
\unfoldRepeats
<< 

% === BEGIN MIDI STAFF ===
    \new JianpuStaff { \new Voice="Z" { \time 4/4 \tempo 4=120 r2. bes,16 r16 e8 | %{ bar 2: %} r16 e8 d8. r32 c16 ~ c4 r4 b,8 < c c' >16 r16 b,8 < a, a >8 r8 r4 c8 r4 c8 a8 ~ a16 r16 c16 ~ } c16 r32 c'16 ~ c'32 } r16 a8 r32 c'8 g4 ~ } g32 } r16 c'8 e8 ~ e8 r8 c8 r8 c'8 } a8 c'16 r16 a4 gis8 } b8. r16 g8 e8 r8 e8. r4 r8 < f f' >16 r16 f8 r16 e8 r16 bes16 r16 e8 d16 r16 d16 d8. r2. c8. bes,16 r16 < d d' >4 r8 d8 g8 r16 c16 r16 b,8 } c8 r8 } b16 r8. c'8 r32 } a8. r32 c'16 ~ } c'8 } g8 r4 r8 c'8 a8 r8 c'8 a8 c'16 r16 g8 r16 g16 r16 e8 r32 c8 r8 } g8 ~ g8 c8 } b,8 r8 } g8 r8 e8 ~ e16 r32 d16 ~ d4 c4 r32 c4 r16 b,8 ~ b,8 } r16 c8 c4 ~ } c1 } c4 ~ c16 r4. f,4 ~ f,8. b,8 r4 } r2 r8 } }
% === END MIDI STAFF ===


% === BEGIN MIDI STAFF ===
    \new JianpuStaff { \new Voice="a" { \time 4/4 r2. e16 ~ r8 r8. r32 r16 r2 r8 r16 r16 r8 r8 r8 r4 r8 r4 r8 r8 r16 r16 r16 } r16 r32 r16 r32 } r16 r8 r32 r8 r4 } r32 } r16 r8 r8 r8 r8 r8 r8 r8 } r8 r16 r16 r4 r8 } r4. d4 r2 r16 r2 f8 r1 r16 r8. r1. < d d' >16 r2 r8 } r8 r8 } r16 r8. r8 r32 } r8. r32 r16 } r8 } r2 a8 r2 r8 r16 r16 r16 r8 r32 r8 r8 } r8 r8 r8 } r8 r8 } r16 f8 r4. c''16 r4. r8 } r16 r8 r4 } r1 } r4 r16 r4. r4 r8. r8 r4 } r2 r8 } }
% === END MIDI STAFF ===


% === BEGIN MIDI STAFF ===
    \new JianpuStaff { \new Voice="b" { \time 4/4 r2. r16 r16 r8 | %{ bar 2: %} r16 r2 c'8 r4 c8 r4 r16 r2 b,8 r4. r16 r16 r16 } r16 r32 r16 r32 } r16 r8 r32 r8 r4 } r32 } r16 r8 r8 r8 r8 r8 r8 r8 } r8 r16 r16 r4 r8 } r8. r16 r8 r8 r8 r8. r4 r8 r16 r16 r8 r16 r8 r16 r16 r16 r8 r16 r16 r16 r8. r2. r8. r16 r16 r4 r8 r8 r8 r16 r16 r16 r8 } r8 r8 } r16 r8. r8 r32 } r8. r32 r16 } r8 } r8 r4 r8 r8 r8 r8 r8 r8 r16 r16 r8 r16 r16 r16 r8 r32 r8 r8 } r8 r8 r8 } r8 r8 } r8 r8 r8 r16 r32 r16 r2 r32 r4 r16 r8 r8 } r16 r8 r4 } r1 } r4 r16 r4. r4 r8. r8 r4 } r2 r8 } }

