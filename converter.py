# converter.py
# CLEAN MUSICXML FOR JIANPU_LY

from music21 import converter, stream, meter, note, chord
import os


def rebuild_for_jianpu(input_file, output_file):

    print("READ SOURCE")
    src = converter.parse(input_file)

    print("EXTRACT NOTES")

    notes = []

    for n in src.recurse().notes:

        if isinstance(n, chord.Chord):
            # 只取最高音旋律
            n = n.sortAscending().notes[-1]

        if isinstance(n, note.Note):
            notes.append(n)


    print("TOTAL NOTES:", len(notes))


    print("BUILD NEW SCORE")

    score = stream.Score()
    part = stream.Part()

    part.append(meter.TimeSignature("4/4"))


    measure = stream.Measure(number=1)

    current = 0.0


    for n in notes:

        dur = n.duration.quarterLength


        # 超過小節直接切
        if current + dur > 4:

            # 補休止
            rest_time = 4-current

            if rest_time > 0:
                r = note.Rest()
                r.duration.quarterLength = rest_time
                measure.append(r)


            part.append(measure)

            measure = stream.Measure(
                number=len(part.getElementsByClass(
                    stream.Measure
                ))+1
            )

            current = 0


        new_note = note.Note(
            n.pitch
        )

        new_note.duration.quarterLength = dur

        measure.append(new_note)

        current += dur



    # 最後小節補滿

    if current < 4:

        r = note.Rest()
        r.duration.quarterLength = 4-current
        measure.append(r)


    part.append(measure)

    score.append(part)


    print("WRITE MUSICXML")

    score.write(
        "musicxml",
        fp=output_file
    )


    print("DONE:", output_file)



if __name__ == "__main__":

    import sys

    if len(sys.argv)<3:
        print(
          "python converter.py input.musicxml output.musicxml"
        )
        exit()


    rebuild_for_jianpu(
        sys.argv[1],
        sys.argv[2]
    )