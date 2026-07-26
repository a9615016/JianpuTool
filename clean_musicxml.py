import sys
import music21


print("CLEAN VERSION 20260726 V5")


# ==========================
# 強制量化
# 最小 1/16 拍
# ==========================

def quantize_length(value):

    value = float(value)

    value = round(value * 4) / 4

    if value <= 0:
        value = 0.25

    return value



# ==========================
# 清理
# ==========================

def clean_musicxml(input_file, output_file):

    print("input:", input_file)


    score = music21.converter.parse(input_file)



    # ==========================
    # Remove chords
    # ==========================

    print("remove chords")


    for chord in list(
        score.recurse()
        .getElementsByClass(
            music21.chord.Chord
        )
    ):

        note = chord.notes[-1]

        note.duration = chord.duration

        chord.activeSite.replace(
            chord,
            note
        )



    # ==========================
    # Remove grace
    # ==========================

    print("remove grace")


    for n in list(
        score.recurse().notes
    ):

        if n.duration.isGrace:

            n.activeSite.remove(n)



    # ==========================
    # Collect notes
    # ==========================

    print("collect notes")


    all_elements = []


    for part in score.parts:

        for e in part.flatten().notesAndRests:

            all_elements.append(e)



    # ==========================
    # Fix duration
    # ==========================

    print("fix duration")


    for e in all_elements:

        e.duration.quarterLength = quantize_length(
            e.duration.quarterLength
        )


        # 禁止128分音符

        if e.duration.quarterLength < 0.25:

            e.duration.quarterLength = 0.25



        # remove tuplet

        if e.duration.tuplets:

            e.duration.clear()



    # ==========================
    # 建立新的 Part
    # ==========================

    print("rebuild 4/4 measures")


    new_score = music21.stream.Score()


    new_part = music21.stream.Part()


    new_part.append(
        music21.instrument.Instrument()
    )


    new_measure = music21.stream.Measure(
        number=1
    )


    current = 0


    measure_no = 1



    for e in all_elements:


        length = float(
            e.duration.quarterLength
        )


        # 如果超過4拍

        if current + length > 4:


            remain = 4-current


            if remain > 0:


                r = music21.note.Rest()

                r.duration.quarterLength = remain

                new_measure.append(r)



            new_part.append(
                new_measure
            )


            measure_no += 1


            new_measure = music21.stream.Measure(
                number=measure_no
            )


            current = 0



        e.offset = current


        new_measure.insert(
            current,
            e
        )


        current += length



        # 滿4拍換小節

        if current >= 4:


            new_part.append(
                new_measure
            )


            measure_no += 1


            new_measure = music21.stream.Measure(
                number=measure_no
            )


            current = 0



    # 最後不足補休止符

    if current < 4:


        r = music21.note.Rest()

        r.duration.quarterLength = (
            4-current
        )

        new_measure.append(r)



    new_part.append(
        new_measure
    )


    new_score.append(
        new_part
    )



    # ==========================
    # Time signature
    # ==========================

    print("set 4/4")


    ts = music21.meter.TimeSignature(
        "4/4"
    )

    new_part.insert(
        0,
        ts
    )



    # ==========================
    # Write
    # ==========================

    print("write")


    new_score.write(
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