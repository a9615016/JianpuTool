import sys
import music21


print("CLEAN VERSION 20260726 V5")


def quantize_length(value):

    value = float(value)

    # 只允許簡譜常用節奏
    allowed = [
        0.25,   # 16分音符
        0.5,    # 8分音符
        1.0,    # 4分音符
        2.0,    # 2分音符
        4.0     # 全音符
    ]

    nearest = min(
        allowed,
        key=lambda x: abs(x-value)
    )

    return nearest



def clean_musicxml(input_file, output_file):

    print("input:", input_file)


    score = music21.converter.parse(
        input_file
    )


    # =========================
    # remove voices
    # =========================

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


            for voice in voices:

                for n in voice.notesAndRests:

                    measure.insert(
                        n.offset,
                        n
                    )

                measure.remove(
                    voice
                )



    # =========================
    # remove chords
    # =========================

    print("remove chords")


    for c in list(
        score.recurse()
        .getElementsByClass(
            music21.chord.Chord
        )
    ):

        if len(c.notes) > 0:

            n = c.notes[-1]

            n.duration = c.duration

            c.activeSite.replace(
                c,
                n
            )



    # =========================
    # remove grace
    # =========================

    print("remove grace")


    for n in list(
        score.recurse()
        .notes
    ):

        if n.duration.isGrace:

            n.activeSite.remove(n)



    # =========================
    # fix duration
    # =========================

    print("fix duration")


    for n in score.recurse().notesAndRests:

        n.duration.quarterLength = quantize_length(
            n.duration.quarterLength
        )



    # =========================
    # remove tuplets
    # =========================

    print("remove tuplets")


    for n in score.recurse().notesAndRests:

        if n.duration.tuplets:

            n.duration.clear()

            n.duration.quarterLength = quantize_length(
                n.duration.quarterLength
            )



    # =========================
    # rebuild measures
    # =========================

    print("rebuild measures")


    for part in score.parts:

        part.makeMeasures(
            inPlace=True
        )



    # =========================
    # fix bars
    # =========================

    print("fix bars")


    for part in score.parts:


        for measure in part.getElementsByClass(
            music21.stream.Measure
        ):


            expected = float(
                measure.barDuration.quarterLength
            )


            total = sum(
                float(x.duration.quarterLength)
                for x in measure.notesAndRests
            )


            diff = expected - total


            # 缺拍補休止
            if diff > 0.01:


                r = music21.note.Rest()

                r.duration.quarterLength = quantize_length(
                    diff
                )

                measure.append(r)



            # 超拍縮短最後音符
            elif diff < -0.01:


                print(
                    "trim measure",
                    measure.number,
                    total,
                    expected
                )


                for x in reversed(
                    list(measure.notesAndRests)
                ):

                    new_len = (
                        x.duration.quarterLength
                        +
                        diff
                    )


                    if new_len > 0.25:

                        x.duration.quarterLength = quantize_length(
                            new_len
                        )

                        break



    # =========================
    # final rebuild
    # =========================

    print("final cleanup")


    score.makeMeasures(
        inPlace=True
    )


    # 移除非法 offset
    for n in score.recurse().notesAndRests:

        if n.duration.quarterLength < 0.25:

            n.duration.quarterLength = 0.25



    # =========================
    # write
    # =========================

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


    if len(sys.argv)>=3:

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