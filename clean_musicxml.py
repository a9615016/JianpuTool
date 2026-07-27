import sys
import music21


VERSION = "CLEAN MUSICXML V22"


def clean_musicxml(input_file, output_file):

    print("================")
    print(VERSION)
    print("================")

    print("input:", input_file)

    print("read")
    score = music21.converter.parse(input_file)


    print("remove voices")
    for part in score.parts:
        for element in list(part.recurse()):
            if isinstance(element, music21.stream.Voice):
                element.activeSite.remove(element)


    print("remove chords")
    for part in score.parts:
        for chord in list(part.recurse().getElementsByClass("Chord")):
            notes = chord.notes
            for n in notes:
                chord.activeSite.insert(chord.offset, n)
            chord.activeSite.remove(chord)


    print("quantize")

    for part in score.parts:

        for n in part.recurse().notesAndRests:

            try:
                q = n.duration.quarterLength

                # 常用音符量化
                values = [
                    0.25,
                    0.5,
                    1,
                    1.5,
                    2,
                    3,
                    4
                ]

                n.duration.quarterLength = min(
                    values,
                    key=lambda x: abs(x-q)
                )

            except:
                pass


    print("force 4/4")

    score.timeSignature = music21.meter.TimeSignature("4/4")


    print("rebuild measures")


    for part in score.parts:

        old = list(part.recurse().notesAndRests)


        part.remove(
            list(part.getElementsByClass("Measure"))
        )


        measure_no = 1
        current = music21.stream.Measure(
            number=measure_no
        )

        total = 0


        for element in old:

            length = element.duration.quarterLength


            # 超過小節線
            if total + length > 4:

                # 補滿休止
                remain = 4-total

                if remain > 0:
                    rest = music21.note.Rest(
                        quarterLength=remain
                    )
                    current.append(rest)


                part.append(current)


                measure_no += 1

                current = music21.stream.Measure(
                    number=measure_no
                )

                total = 0


            current.append(element)
            total += length


        if len(current)>0:

            remain = 4-total

            if remain > 0:
                current.append(
                    music21.note.Rest(
                        quarterLength=remain
                    )
                )

            part.append(current)



    print("write")

    score.write(
        "musicxml",
        fp=output_file
    )


    print()
    print("DONE", output_file)



if __name__ == "__main__":

    if len(sys.argv)<3:
        print(
            "usage: python clean_musicxml.py input.musicxml output.musicxml"
        )
        sys.exit(1)


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )