import sys
from music21 import converter, stream, instrument, note, chord, meter


print("CLEAN VERSION 20260724 V7")


def clean_musicxml(input_file, output_file):

    print("開始 clean MusicXML")

    score = converter.parse(input_file)


    # =====================
    # 只保留第一個 Part
    # =====================

    if len(score.parts) > 1:
        score = stream.Score(
            score.parts[0]
        )


    part = score.parts[0]


    # =====================
    # 移除 Instrument
    # =====================

    for ins in part.recurse().getElementsByClass(
        instrument.Instrument
    ):
        ins.activeSite.remove(ins)


    # =====================
    # 清除空元素
    # =====================

    new_part = stream.Part()


    for element in part.flatten().notesAndRests:


        # 保留音符
        if isinstance(
            element,
            note.Note
        ):
            new_part.append(element)


        # 保留和弦第一音
        elif isinstance(
            element,
            chord.Chord
        ):

            new_part.append(
                note.Note(
                    element.pitches[0]
                )
            )


        # 不保留休止
        # 避免 jianpu_ly 出現大量 0


    # =====================
    # 加回拍號
    # =====================

    new_part.insert(
        0,
        meter.TimeSignature("4/4")
    )


    new_score = stream.Score()
    new_score.append(new_part)


    new_score.write(
        "musicxml",
        fp=output_file
    )


    print(
        "clean完成",
        output_file
    )



if __name__ == "__main__":


    if len(sys.argv) < 3:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )