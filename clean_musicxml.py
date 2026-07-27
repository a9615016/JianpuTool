import sys
import music21
from music21 import stream, note, chord, meter


VERSION = "V18"


def clean(input_file, output_file):

    print("================")
    print(f"CLEAN MUSICXML {VERSION}")
    print("================")
    print("input:", input_file)


    score = music21.converter.parse(input_file)


    new_score = stream.Score()


    for old_part in score.parts:


        print("flatten notes")

        flat = old_part.flatten()


        events = []


        # -------------------------
        # 只保留 Note / Rest
        # -------------------------

        for e in flat.notesAndRests:


            if isinstance(e, chord.Chord):

                n = note.Note(
                    e.pitches[0],
                    quarterLength=e.duration.quarterLength
                )

                events.append(n)


            elif isinstance(e, note.Note):

                n = note.Note(
                    e.pitch,
                    quarterLength=e.duration.quarterLength
                )

                events.append(n)


            elif isinstance(e, note.Rest):

                r = note.Rest(
                    quarterLength=e.duration.quarterLength
                )

                events.append(r)



        print("rebuild measures")


        new_part = stream.Part()


        measure_no = 1
        current_measure = stream.Measure(
            number=measure_no
        )


        current_length = 0


        for e in events:


            ql = float(e.duration.quarterLength)


            # -------------------------
            # 修正奇怪 duration
            # -------------------------

            allowed = [
                0.25,
                0.5,
                0.75,
                1,
                1.5,
                2,
                3,
                4
            ]


            ql = min(
                allowed,
                key=lambda x: abs(x-ql)
            )


            e.duration.quarterLength = ql



            # -------------------------
            # 超過4拍
            # 換下一小節
            # -------------------------

            if current_length + ql > 4:


                remain = 4-current_length


                if remain > 0:

                    current_measure.append(
                        note.Rest(
                            quarterLength=remain
                        )
                    )


                new_part.append(
                    current_measure
                )


                measure_no += 1


                current_measure = stream.Measure(
                    number=measure_no
                )


                current_length = 0



            current_measure.append(e)

            current_length += ql



        # 最後不足補休止

        if current_length < 4:

            current_measure.append(
                note.Rest(
                    quarterLength=4-current_length
                )
            )


        new_part.append(
            current_measure
        )



        # -------------------------
        # 強制4/4
        # -------------------------

        print("force 4/4")


        new_part.insert(
            0,
            meter.TimeSignature("4/4")
        )


        new_score.append(
            new_part
        )



    print("remove empty measures")


    for part in new_score.parts:

        for m in list(
            part.getElementsByClass("Measure")
        ):

            if len(m.notesAndRests)==0:

                part.remove(m)



    print("write")


    new_score.write(
        "musicxml",
        fp=output_file
    )


    print()
    print("DONE", output_file)



if __name__ == "__main__":


    if len(sys.argv) < 3:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit(1)


    clean(
        sys.argv[1],
        sys.argv[2]
    )