from music21 import converter, stream, note, chord, meter
import sys


print("================")
print("CLEAN MUSICXML V25 JIANPU HARD FIX")
print("================")


src = sys.argv[1]
dst = sys.argv[2]


print("read")

score = converter.parse(src)


# remove voices
print("remove voices")

for p in score.parts:
    for el in list(p.recurse()):
        if hasattr(el, "voice"):
            try:
                el.voice = None
            except:
                pass


# remove chords
print("remove chords")

for p in score.parts:
    for c in list(p.recurse().getElementsByClass('Chord')):
        n = c.closedPosition(forceOctave=4)

        new = note.Note(
            n.pitch,
            quarterLength=c.duration.quarterLength
        )

        c.activeSite.replace(c,new)



# remove beams ties
print("remove beams ties")

for n in score.recurse().notes:
    try:
        n.beams = None
    except:
        pass

    try:
        n.tie = None
    except:
        pass



# force 4/4
print("force 4/4")

for p in score.parts:

    p.insert(
        0,
        meter.TimeSignature("4/4")
    )


# flatten
print("flatten")


for p in score.parts:

    notes = []

    for n in p.recurse().notesAndRests:

        if isinstance(n, chord.Chord):
            n = note.Note(
                n.pitches[0],
                quarterLength=n.duration.quarterLength
            )


        # remove invalid
        if n.duration.quarterLength <= 0:
            continue


        notes.append(n)


    p.remove(
        p.recurse().notesAndRests
    )


    offset = 0


    print("rebuild measures")


    measure_no = 1
    current = stream.Measure(number=measure_no)

    beat = 0


    for n in notes:


        ql = n.duration.quarterLength


        # quantize
        if ql < 0.25:
            ql = 0.25

        elif ql < 0.5:
            ql = 0.5

        elif ql < 1:
            ql = 1

        elif ql < 2:
            ql = 2

        else:
            ql = 4


        n.duration.quarterLength = ql


        # split crossing bar
        if beat + ql > 4:

            rest = 4-beat

            if rest > 0:
                r = note.Rest()
                r.duration.quarterLength = rest
                current.append(r)


            p.append(current)

            print(
                "Measure",
                measure_no,
                4.0
            )


            measure_no += 1
            current = stream.Measure(
                number=measure_no
            )

            beat = 0



        current.append(n)

        beat += ql



        if beat >=4:

            p.append(current)

            print(
                "Measure",
                measure_no,
                4.0
            )


            measure_no +=1
            current = stream.Measure(
                number=measure_no
            )

            beat=0



    # fill last measure

    if beat>0:

        r = note.Rest()

        r.duration.quarterLength = 4-beat

        current.append(r)

        p.append(current)



print("clear cache")


score.removeByClass('Barline')


print("FINAL CHECK")


for m in score.parts[0].getElementsByClass('Measure'):

    total=sum(
        x.duration.quarterLength
        for x in m.notesAndRests
    )

    print(
        "Measure",
        m.number,
        total
    )


print("FINAL WRITE")


score.write(
    "musicxml",
    fp=dst
)


print("DONE")
print(dst)