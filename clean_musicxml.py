import sys
import music21
from music21 import stream, note, meter, duration, instrument


print("================")
print("CLEAN MUSICXML V28")
print("TRUE BAR SPLIT VERSION")
print("================")


BAR_LENGTH = 4.0


def quantize_length(q):

    values = [
        0.25,
        0.5,
        0.75,
        1.0,
        1.5,
        2.0,
        3.0,
        4.0
    ]

    return min(
        values,
        key=lambda x: abs(x-q)
    )


def split_measure_notes(part):

    print("TRUE NOTE SPLIT")

    new_part = stream.Part()

    measures = list(
        part.getElementsByClass("Measure")
    )


    measure_no = 1


    for m in measures:

        new_measure = stream.Measure(
            number=measure_no
        )

        new_measure.insert(
            0,
            meter.TimeSignature("4/4")
        )


        current_time = 0.0


        for n in m.notesAndRests:


            dur = float(
                n.duration.quarterLength
            )


            # rest 直接處理
            if isinstance(n, note.Rest):

                if current_time + dur <= BAR_LENGTH:

                    new_measure.append(n)
                    current_time += dur

                continue



            # note 跨小節
            while current_time + dur > BAR_LENGTH:


                remain = BAR_LENGTH - current_time


                if remain > 0:

                    n1 = note.Note(
                        n.pitch
                    )

                    n1.duration = duration.Duration(
                        quantize_length(remain)
                    )

                    new_measure.append(n1)



                print(
                    "SPLIT:",
                    n.pitch,
                    "remain",
                    remain
                )


                new_part.append(
                    new_measure
                )


                measure_no += 1


                new_measure = stream.Measure(
                    number=measure_no
                )

                new_measure.insert(
                    0,
                    meter.TimeSignature("4/4")
                )


                dur -= remain

                current_time = 0



            if dur > 0:

                n2 = note.Note(
                    n.pitch
                )

                n2.duration = duration.Duration(
                    quantize_length(dur)
                )

                new_measure.append(n2)

                current_time += dur



        if len(new_measure.notesAndRests) > 0:

            new_part.append(
                new_measure
            )

            measure_no += 1



    return new_part



def clean(input_file, output_file):

    print("READ")

    score = music21.converter.parse(
        input_file
    )


    print("REMOVE VOICES")

    for p in score.parts:

        for v in p.recurse().getElementsByClass(
            "Voice"
        ):
            v.activeSite.remove(v)



    print("REMOVE CHORDS")

    for c in score.recurse().getElementsByClass(
        "Chord"
    ):

        c.activeSite.replace(
            c,
            c.notes[0]
        )



    print("REMOVE BEAMS")

    for n in score.recurse().notes:

        n.beams = None



    print("REMOVE TIES")

    for n in score.recurse().notes:

        n.tie = None



    print("FORCE 4/4")


    new_score = stream.Score()



    for p in score.parts:


        print(
            "PROCESS PART"
        )


        new_part = split_measure_notes(
            p
        )


        new_score.append(
            new_part
        )



    print("FINAL CHECK")


    for m in new_score.parts[0].getElementsByClass(
        "Measure"
    ):

        total = sum(
            n.duration.quarterLength
            for n in m.notesAndRests
        )


        print(
            "Measure",
            m.number,
            float(total)
        )



    print("WRITE")


    new_score.write(
        "musicxml",
        fp=output_file
    )


    print("================")
    print("DONE")
    print(output_file)
    print("================")



if __name__ == "__main__":


    if len(sys.argv) < 3:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()


    clean(
        sys.argv[1],
        sys.argv[2]
    )