# jianpu_fix_musicxml.py V1.0

import sys
from music21 import converter, stream, note, meter, chord


def fix_musicxml(src, dst):

    print("====================")
    print("JIANPU FIX MUSICXML V1.0")
    print("====================")

    score = converter.parse(src)

    print("load")

    # remove bad objects
    for part in score.parts:

        print("processing part")

        # force meter
        part.insert(0, meter.TimeSignature("4/4"))

        new_part = stream.Part()

        current = 0.0

        for m in part.getElementsByClass(stream.Measure):

            new_measure = stream.Measure()

            dur_sum = 0


            for n in m.notesAndRests:

                # chord -> highest note
                if isinstance(n, chord.Chord):
                    n = n.sortAscending().notes[-1]

                if isinstance(n, note.Note):

                    q = n.duration.quarterLength

                    # quantize
                    if q >= 1.75:
                        q = 2
                    elif q >= 0.75:
                        q = 1
                    elif q >= 0.35:
                        q = 0.5
                    else:
                        q = 0.25


                    nn = note.Note(
                        n.pitch,
                        quarterLength=q
                    )

                    new_measure.append(nn)

                    dur_sum += q


            # fill measure
            while dur_sum < 4:

                r = note.Rest(
                    quarterLength=min(
                        0.25,
                        4-dur_sum
                    )
                )

                new_measure.append(r)

                dur_sum += r.duration.quarterLength


            # trim overflow
            while dur_sum > 4:

                last = new_measure[-1]

                diff = dur_sum - 4

                if last.duration.quarterLength > diff:

                    last.duration.quarterLength -= diff
                    dur_sum = 4

                else:

                    new_measure.pop()
                    dur_sum -= last.duration.quarterLength


            new_part.append(new_measure)


        part = new_part



    score.write(
        "musicxml",
        fp=dst
    )


    print("====================")
    print("DONE")
    print(dst)



if __name__=="__main__":

    if len(sys.argv)<3:
        print(
        "python jianpu_fix_musicxml.py input.musicxml output.musicxml"
        )
        exit()


    fix_musicxml(
        sys.argv[1],
        sys.argv[2]
    )