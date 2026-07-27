import music21
import sys
import os
import copy


VERSION = "CLEAN MUSICXML V22"


def clean_musicxml(input_file, output_file):

    print("================")
    print(VERSION)
    print("================")

    print("input:", input_file)

    score = music21.converter.parse(input_file)

    print("read")

    # 移除 voices / chords
    print("remove voices")
    for part in score.parts:
        for element in list(part.recurse()):
            if isinstance(element, music21.note.Note):
                element.volume.velocity = None

    print("remove chords")
    for part in score.parts:
        for chord in list(part.recurse().getElementsByClass('Chord')):
            notes = chord.notes
            for n in notes:
                chord.activeSite.insert(chord.offset, n)
            chord.activeSite.remove(chord)

    print("quantize")

    # 4/4
    print("force 4/4")

    score.insert(0, music21.meter.TimeSignature("4/4"))


    # 重新建立 measures
    print("rebuild measures")

    for part in score.parts:

        new_part = music21.stream.Part()

        measure = music21.stream.Measure(number=1)

        current = 0
        measure_length = 4.0


        for element in part.flatten().notesAndRests:

            dur = element.duration.quarterLength


            # 超過小節，切割
            while current + dur > measure_length:

                remain = measure_length - current


                if remain > 0:

                    first = copy.deepcopy(element)
                    first.duration.quarterLength = remain
                    measure.insert(current, first)


                new_part.append(measure)

                print(
                    "split measure",
                    measure.number
                )


                measure = music21.stream.Measure(
                    number=measure.number + 1
                )

                dur -= remain
                current = 0


                if dur > 0:

                    second = copy.deepcopy(element)
                    second.duration.quarterLength = dur
                    element = second



            measure.insert(current, element)

            current += dur


            if current >= measure_length:

                new_part.append(measure)

                measure = music21.stream.Measure(
                    number=measure.number + 1
                )

                current = 0



        # 最後小節
        if len(measure.notesAndRests) > 0:
            new_part.append(measure)


        part.clear()
        part.insert(0,new_part)


    print("remove empty measures")


    # 寫出

    print("write")

    score.write(
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


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )