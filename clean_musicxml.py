from music21 import converter, stream, note, chord, meter, bar
import sys
import copy


print("==============================")
print("CLEAN MUSICXML V29 HARD RESET")
print("JIANPU_LY COMPATIBLE")
print("==============================")


DIVISIONS = 16


def remove_chords(score):
    print("remove chords")

    for part in score.parts:
        for c in list(part.recurse().getElementsByClass(chord.Chord)):
            n = note.Note(c.root())
            n.duration = c.duration
            c.activeSite.replace(c, n)



def clean_notes(score):

    print("clean notes")

    for n in score.recurse().notesAndRests:

        # remove tie
        n.tie = None

        # remove beams
        if hasattr(n, "beams"):
            n.beams = None

        # quantize
        q = n.duration.quarterLength

        allowed = [
            4,
            2,
            1,
            0.5,
            0.25,
            0.125
        ]

        n.duration.quarterLength = min(
            allowed,
            key=lambda x:abs(x-q)
        )



def remove_structure(score):

    print("remove voice / backup / forward")

    for el in score.recurse():

        try:
            if hasattr(el, "voice"):
                el.voice = None
        except:
            pass



def force_time(score):

    print("force 4/4")

    for p in score.parts:

        p.insert(
            0,
            meter.TimeSignature("4/4")
        )



def rebuild_score(score):

    print("REBUILD TIMELINE")


    new_score = stream.Score()


    part = stream.Part()


    current = 0
    measure_no = 1

    m = stream.Measure(number=measure_no)


    for n in score.recurse().notesAndRests:


        dur = n.duration.quarterLength


        while dur > 0:


            remain = 4 - current


            take = min(
                remain,
                dur
            )


            nn = copy.deepcopy(n)

            nn.duration.quarterLength = take


            m.append(nn)


            current += take
            dur -= take


            if abs(current-4)<0.001:

                part.append(m)

                measure_no += 1

                m = stream.Measure(
                    number=measure_no
                )

                current = 0



    if current > 0:

        r = note.Rest()
        r.duration.quarterLength = 4-current
        m.append(r)
        part.append(m)


    new_score.append(part)


    return new_score



def final_check(score):

    print("FINAL CHECK")


    ok=True


    for p in score.parts:

        for m in p.getElementsByClass(stream.Measure):

            total=sum(
                x.duration.quarterLength
                for x in m.notesAndRests
            )


            print(
                "Measure",
                m.number,
                total
            )


            if abs(total-4)>0.001:
                ok=False


    if ok:
        print("ALL MEASURES SAFE")

    else:
        print("WARNING")



def main():

    inp=sys.argv[1]
    out=sys.argv[2]


    print("READ")

    score=converter.parse(inp)


    remove_chords(score)

    clean_notes(score)

    remove_structure(score)

    force_time(score)


    score=rebuild_score(score)


    final_check(score)


    print("WRITE MUSICXML")


    score.write(
        "musicxml",
        fp=out
    )


    print("DONE")
    print(out)



if __name__=="__main__":
    main()