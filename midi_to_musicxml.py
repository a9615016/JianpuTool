import sys
from pathlib import Path

from music21 import converter, stream, meter, note, chord, tempo


def clean_midi_score(score):

    print("重新整理樂譜...")

    # 建立新的單聲部
    new_score = stream.Score()
    part = stream.Part()

    part.insert(0, meter.TimeSignature("4/4"))

    # 加 tempo
    part.insert(0, tempo.MetronomeMark(number=80))


    notes = []

    for element in score.flatten().notes:

        # chord 取最高音
        if isinstance(element, chord.Chord):

            n = element.sortAscending()[0]

            new_note = note.Note(
                n.pitch,
                quarterLength=element.duration.quarterLength
            )

            notes.append(new_note)


        elif isinstance(element, note.Note):

            new_note = note.Note(
                element.pitch,
                quarterLength=element.duration.quarterLength
            )

            notes.append(new_note)



    print("原始音符:", len(notes))


    # =========================
    # duration quantize
    # =========================

    print("duration quantize")


    allowed = [
        0.25,
        0.5,
        1.0,
        2.0,
        4.0
    ]


    for n in notes:

        q = n.duration.quarterLength

        closest = min(
            allowed,
            key=lambda x: abs(x-q)
        )

        n.duration.quarterLength = closest



    # =========================
    # 填入 part
    # =========================

    current = 0

    for n in notes:

        part.append(n)
        current += n.duration.quarterLength


    new_score.append(part)


    # =========================
    # rebuild measures
    # =========================

    print("rebuild measures")

    new_score = new_score.makeMeasures(
        inPlace=False
    )


    # =========================
    # split cross measure
    # =========================

    print("split cross measure notes")

    try:
        new_score = new_score.makeTies(
            inPlace=False
        )
    except:
        pass


    return new_score



def main():

    if len(sys.argv) < 3:

        print(
            "usage:\n"
            "python midi_to_musicxml_v3.py input.mid output.musicxml"
        )

        sys.exit(1)


    input_mid = sys.argv[1]
    output_xml = sys.argv[2]


    print("================")
    print("MIDI TO MUSICXML V3")
    print("JIANPU STABLE VERSION")
    print("================")


    print("輸入 MIDI:")
    print(input_mid)


    print("讀取 MIDI...")


    score = converter.parse(
        input_mid
    )


    score = clean_midi_score(score)


    print("FINAL CHECK")


    measures = score.parts[0].getElementsByClass(
        stream.Measure
    )


    for m in measures:

        length = m.duration.quarterLength

        print(
            "Measure",
            m.number,
            length
        )


    print("寫入 MusicXML...")


    score.write(
        "musicxml",
        fp=output_xml
    )


    print("完成:")
    print(output_xml)



if __name__ == "__main__":
    main()