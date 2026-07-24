import sys
import os
import music21


print("CLEAN VERSION 20260724 V12")


if len(sys.argv) < 3:
    print(
        "使用方式: python clean_musicxml.py input.musicxml output.musicxml"
    )
    sys.exit(1)


input_file = sys.argv[1]
output_file = sys.argv[2]


print("input:", input_file)


# ==========================
# 讀取 MusicXML
# ==========================

score = music21.converter.parse(
    input_file
)


# ==========================
# 清理
# ==========================

for part in score.parts:

    print("remove voices")


    # 移除 Voice
    for measure in part.getElementsByClass(
        "Measure"
    ):

        voices = measure.getElementsByClass(
            "Voice"
        )

        for v in list(voices):
            measure.remove(v)



    print("remove chords")


    # Chord 只留第一音
    for chord in list(
        part.recurse()
        .getElementsByClass("Chord")
    ):

        try:

            if len(chord.notes) > 0:

                note = chord.notes[0]

                chord.activeSite.replace(
                    chord,
                    note
                )

        except:

            pass



    print("remove grace notes")


    # 移除裝飾音
    for n in list(
        part.recurse()
        .notesAndRests
    ):

        try:

            if n.duration.isGrace:

                n.activeSite.remove(n)

        except:

            pass



    print("fix duration")


    # 修正超短 duration
    for n in part.recurse().notesAndRests:

        try:

            ql = n.duration.quarterLength


            # 小於16分音符全部修正
            if ql < 0.25:

                n.duration.quarterLength = 0.25



            # 清除 tuplet
            if n.duration.tuplets:

                n.duration.tuplets = []



        except:

            pass



print("remove extreme durations")


# ==========================
# 全局修正
# ==========================

for n in score.recurse().notesAndRests:

    try:

        if n.duration.type in [

            "2048th",
            "1024th",
            "512th",
            "256th",
            "128th"

        ]:

            n.duration.quarterLength = 0.25



        if n.duration.quarterLength <= 0:

            n.duration.quarterLength = 0.25



    except:

        pass



# ==========================
# 重新量化
# ==========================

print("quantize")


try:

    score.quantize(
        quarterLengthDivisors=[
            4,
            8,
            16
        ]
    )

except Exception as e:

    print(
        "quantize skip:",
        e
    )



# ==========================
# 輸出
# ==========================

print("write")


os.makedirs(
    os.path.dirname(output_file),
    exist_ok=True
)


score.write(
    "musicxml",
    fp=output_file
)


print(
    "完成:",
    output_file
)