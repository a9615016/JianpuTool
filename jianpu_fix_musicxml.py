from music21 import converter, stream, note, meter, tempo
import sys


VERSION = "V12 REBUILD"


def rebuild_musicxml(input_file, output_file):

    print("======================")
    print("JIANPU FIX MUSICXML")
    print(VERSION)
    print("======================")

    print("read input")

    old = converter.parse(input_file)

    # 建立全新 Score
    new_score = stream.Score()

    part = stream.Part()

    # 4/4
    part.append(meter.TimeSignature("4/4"))

    # tempo
    part.append(tempo.MetronomeMark(number=100))


    print("extract notes")

    notes = []

    for n in old.recurse().notesAndRests:

        if isinstance(n, note.Note):

            notes.append(
                (
                    n.pitch,
                    n.duration.quarterLength
                )
            )

        elif isinstance(n, note.Rest):

            notes.append(
                (
                    None,
                    n.duration.quarterLength
                )
            )


    print("total events:", len(notes))


    print("rebuild measures")

    measure = stream.Measure()
    measure.number = 1

    current = 0.0


    for pitch, duration in notes:


        # 防止超過4拍
        if current + duration > 4.0:

            remain = 4.0 - current

            if remain > 0:

                if pitch:

                    nn = note.Note(pitch)
                else:
                    nn = note.Rest()

                nn.duration.quarterLength = remain
                measure.append(nn)


            part.append(measure)


            print(
                "Measure",
                measure.number,
                measure.duration.quarterLength
            )


            measure = stream.Measure()
            measure.number += 1

            current = 0


            duration -= remain


        if pitch:

            nn = note.Note(pitch)

        else:

            nn = note.Rest()


        nn.duration.quarterLength = duration

        measure.append(nn)

        current += duration


        if abs(current - 4.0) < 0.0001:


            part.append(measure)


            print(
                "Measure",
                measure.number,
                measure.duration.quarterLength
            )


            measure = stream.Measure()
            measure.number += 1

            current = 0



    # 最後不足補休止

    if measure.notesAndRests:

        remain = 4.0 - current

        if remain > 0:

            r = note.Rest()
            r.duration.quarterLength = remain
            measure.append(r)


        part.append(measure)



    new_score.append(part)


    print("FINAL CHECK")


    for m in part.getElementsByClass(stream.Measure):

        length = float(m.duration.quarterLength)

        print(
            "Measure",
            m.number,
            length
        )

        if abs(length-4.0)>0.001:

            print(
                "WARNING",
                m.number,
                length
            )


    print("write MusicXML")

    new_score.write(
        "musicxml",
        fp=output_file
    )


    print("DONE")
    print(output_file)



if __name__ == "__main__":

    if len(sys.argv)<3:

        print(
            "usage:"
        )

        print(
            "python jianpu_fix_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()


    rebuild_musicxml(
        sys.argv[1],
        sys.argv[2]
    )