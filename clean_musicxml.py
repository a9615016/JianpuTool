import sys
import music21


# ==========================
# 量化
# ==========================

def quantize_length(value):

    value = float(value)

    # 最小 1/16 音符
    steps = round(value * 4)

    if steps <= 0:
        steps = 1

    return steps / 4



# ==========================
# 清理
# ==========================

def clean_musicxml(input_file, output_file):

    print("CLEAN VERSION 20260726 V6")
    print("input:", input_file)


    score = music21.converter.parse(input_file)



    # ==========================
    # Remove Voices
    # ==========================

    print("remove voices")


    for part in score.parts:

        for measure in part.getElementsByClass(
            music21.stream.Measure
        ):

            voices = list(
                measure.getElementsByClass(
                    music21.stream.Voice
                )
            )


            if voices:

                elements = []

                for v in voices:

                    for e in v.notesAndRests:
                        elements.append(e)


                measure.removeByClass(
                    music21.stream.Voice
                )


                offset = 0

                for e in elements:

                    e.offset = offset

                    measure.insert(
                        offset,
                        e
                    )

                    offset += e.quarterLength



    # ==========================
    # Remove Chords
    # ==========================

    print("remove chords")


    for chord in list(
        score.recurse()
        .getElementsByClass(
            music21.chord.Chord
        )
    ):

        note = chord.notes[0]

        note.duration = chord.duration

        chord.activeSite.replace(
            chord,
            note
        )



    # ==========================
    # Remove Grace
    # ==========================

    print("remove grace")


    for n in list(
        score.recurse()
        .notesAndRests
    ):

        if n.duration.isGrace:

            n.activeSite.remove(n)



    # ==========================
    # Duration Normalize
    # ==========================

    print("fix duration")


    for n in score.recurse().notesAndRests:

        n.duration.clear()

        n.duration.quarterLength = quantize_length(
            n.duration.quarterLength
        )



    # ==========================
    # Remove Tuplets
    # ==========================

    print("remove tuplets")


    for n in score.recurse().notesAndRests:

        if n.duration.tuplets:

            q = quantize_length(
                n.duration.quarterLength
            )

            n.duration.clear()

            n.duration.quarterLength = q



    # ==========================
    # Fix Bars
    # ==========================

    print("fix bars")


    for part in score.parts:


        for measure in part.getElementsByClass(
            music21.stream.Measure
        ):


            expected = 4.0


            elements = list(
                measure.notesAndRests
            )


            total = sum(
                float(e.duration.quarterLength)
                for e in elements
            )


            diff = expected - total



            # 少拍補休止

            if diff > 0.01:


                rest = music21.note.Rest()

                rest.duration.quarterLength = quantize_length(
                    diff
                )

                measure.append(rest)



            # 超拍修最後元素

            elif diff < -0.01:


                print(
                    "trim measure",
                    measure.number,
                    total
                )


                remain = expected


                for e in elements:


                    if remain <= 0:
                        break


                    length = float(
                        e.duration.quarterLength
                    )


                    if length > remain:


                        e.duration.quarterLength = remain

                        remain = 0


                    else:

                        remain -= length



    # ==========================
    # Final Check
    # ==========================

    print("final cleanup")


    for n in score.recurse().notesAndRests:

        n.duration.quarterLength = quantize_length(
            n.duration.quarterLength
        )



    # 不重新 makeMeasures
    # 避免破壞 bar


    # ==========================
    # Write
    # ==========================

    print("write")


    score.write(
        "musicxml",
        fp=output_file
    )


    print(
        "done:",
        output_file
    )



if __name__ == "__main__":


    if len(sys.argv) < 2:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit(1)



    input_file = sys.argv[1]


    if len(sys.argv) >= 3:

        output_file = sys.argv[2]

    else:

        output_file = input_file.replace(
            ".musicxml",
            "_clean.musicxml"
        )


    clean_musicxml(
        input_file,
        output_file
    )