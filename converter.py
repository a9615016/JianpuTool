import os
import sys
import music21



def midi_to_musicxml(input_file):

    print("開始 MIDI → MusicXML")

    print(
        "輸入:",
        input_file
    )


    # 輸出檔名
    base = os.path.splitext(
        input_file
    )[0]


    output_file = base + ".musicxml"



    # 讀取 MIDI

    score = music21.converter.parse(
        input_file
    )



    # ==========================
    # 只保留第一軌旋律
    # ==========================

    if len(score.parts) > 1:

        print(
            "偵測多軌，保留第一軌"
        )

        score = score.parts[0]



    # ==========================
    # 移除複雜資訊
    # ==========================


    for element in score.recurse():


        # 移除和弦
        if isinstance(
            element,
            music21.chord.Chord
        ):

            element.pitches = [
                element.pitches[0]
            ]



    # ==========================
    # 限制音域
    # ==========================


    for note in score.recurse().notes:


        if hasattr(
            note,
            "pitch"
        ):


            if note.pitch.octave < 3:

                note.pitch.octave = 3



            if note.pitch.octave > 6:

                note.pitch.octave = 6



    # ==========================
    # 輸出 MusicXML
    # ==========================


    score.write(
        "musicxml",
        fp=output_file
    )



    print(
        "完成:",
        output_file
    )


    return output_file





# ==========================
# Render 呼叫入口
# ==========================

if __name__ == "__main__":


    if len(sys.argv) < 2:


        print(
            "使用方式:"
        )

        print(
            "python converter.py input.mid"
        )


        sys.exit(1)



    midi_file = sys.argv[1]



    midi_to_musicxml(
        midi_file
    )