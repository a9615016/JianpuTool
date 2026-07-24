import sys
import os
import music21


print("CLEAN VERSION 20260724 V14")


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
# 移除 Voice
# ==========================

print("remove voices")


for part in score.parts:

    for measure in part.getElementsByClass("Measure"):

        voices = measure.getElementsByClass("Voice")

        for v in list(voices):

            measure.remove(v)



# ==========================
# Chord 只留第一音
# ==========================

print("remove chords")


for chord in list(
    score.recurse()
    .getElementsByClass("Chord")
):

    try:

        if len(chord.notes):

            note = chord.notes[0]

            chord.activeSite.replace(
                chord,
                note
            )

    except:

        pass



# ==========================
# 移除 Grace Note
# ==========================

print("remove grace notes")


for n in list(
    score.recurse()
    .notesAndRests
):

    try:

        if n.duration.isGrace:

            n.activeSite.remove(n)

    except:

        pass



# ==========================
# 修正 duration
# ==========================

print("fix duration")


for n in score.recurse().notesAndRests:

    try:

        # 清除 tuplet
        n.duration.tuplets = []


        if hasattr(n.duration, "_tuplets"):

            n.duration._tuplets = []



        # 太短音符修正

        if n.duration.quarterLength <= 0:

            n.duration.quarterLength = 0.25


        elif n.duration.quarterLength < 0.25:

            n.duration.quarterLength = 0.25



    except:

        pass



# ==========================
# Final 強制清理
# ==========================

print("final cleanup")


for n in score.recurse().notesAndRests:

    try:

        # 再清一次所有 tuplet

        n.duration.tuplets = []


        if hasattr(n.duration, "_tuplets"):

            n.duration._tuplets = []



        # 防止 2048th / 1024th

        if n.duration.quarterLength < 0.25:

            n.duration.quarterLength = 0.25



        # 移除 type 問題

        if n.duration.type in [

            "2048th",
            "1024th",
            "512th",
            "256th",
            "128th"

        ]:

            n.duration.type = "16th"



    except:

        pass



# ==========================
# Quantize
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
# 最後移除 Rest tuplet
# ==========================

print("REMOVE ALL TUPLETS FINAL")


for n in score.recurse().notesAndRests:

    try:

        n.duration.tuplets = []


        if hasattr(n.duration, "_tuplets"):

            n.duration._tuplets = []


    except:

        pass



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