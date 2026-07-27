import sys
import music21
from music21 import converter, stream, meter, note, chord, tie


print("================")
print("CLEAN MUSICXML V27")
print("JIANPU FINAL COMPATIBLE")
print("================")


def quantize_duration(q):

    allowed = [
        4,
        2,
        1,
        0.5,
        0.25
    ]

    return min(
        allowed,
        key=lambda x: abs(x-q)
    )



def remove_chords(score):

    print("remove chords")

    for part in score.parts:

        for c in list(
            part.recurse().getElementsByClass(
                chord.Chord
            )
        ):

            n = note.Note(
                c.pitches[0]
            )

            n.duration = c.duration

            c.activeSite.replace(
                c,
                n
            )



def clean_notes(score):

    print("clean notes")


    for part in score.parts:


        for n in part.recurse().notesAndRests:


            # remove ties

            if hasattr(n, "tie"):

                n.tie = None



            # remove beams

            if hasattr(n, "beams"):

                n.beams = []


            # reset offset

            n.offset = None



            # quantize

            q = float(
                n.duration.quarterLength
            )


            new_q = quantize_duration(q)


            if abs(q-new_q)>0.01:

                print(
                    "duration:",
                    q,
                    "->",
                    new_q
                )


            n.duration.quarterLength = new_q



def rebuild_measure(score):

    print("rebuild measures")


    ts = meter.TimeSignature(
        "4/4"
    )


    for part in score.parts:


        part.insert(
            0,
            ts
        )


        measures = stream.Measure()


        new_part = stream.Part()


        current = 0



        for n in part.recurse().notesAndRests:


            dur = float(
                n.duration.quarterLength
            )


            # 超過小節直接切開

            if current + dur > 4:


                remain = 4-current


                if remain > 0:


                    first = n.clone()


                    first.duration.quarterLength = remain

                    new_part.append(
                        first
                    )


                new_part.append(
                    stream.Measure()
                )


                current = 0


                remain2 = dur-remain


                if remain2 > 0:

                    second = n.clone()

                    second.duration.quarterLength = remain2

                    new_part.append(
                        second
                    )

                    current += remain2


            else:

                new_part.append(
                    n
                )

                current += dur



            if current == 4:

                current = 0



        score.replace(
            part,
            new_part
        )



def final_measure_check(score):

    print("FINAL CHECK")


    for i, m in enumerate(
        score.parts[0].getElementsByClass(
            stream.Measure
        ),
        1
    ):


        total = sum(
            float(
                n.duration.quarterLength
            )
            for n in m.notesAndRests
        )


        print(
            "Measure",
            i,
            total
        )


        if abs(total-4)>0.01:

            print(
                "FIX measure",
                i
            )


            diff = 4-total


            r = note.Rest()

            r.duration.quarterLength = diff

            m.append(r)



def main():

    if len(sys.argv)<3:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        return



    infile=sys.argv[1]

    outfile=sys.argv[2]


    print("read")

    score = converter.parse(
        infile
    )



    print("remove voices")

    score.removeByClass(
        "Voice"
    )



    remove_chords(
        score
    )



    clean_notes(
        score
    )


    rebuild_measure(
        score
    )


    final_measure_check(
        score
    )



    print("write")


    score.write(
        "musicxml",
        fp=outfile
    )


    print(
        "DONE"
    )

    print(outfile)



if __name__=="__main__":

    main()