import sys
import os
import music21


print("CLEAN VERSION 20260724 V13")


if len(sys.argv) < 3:
    print(
        "使用方式: python clean_musicxml.py input.musicxml output.musicxml"
    )
    sys.exit(1)


input_file = sys.argv[1]
output_file = sys.argv[2]


print("input:", input_file)


# ==========================
# Load
# ==========================

score = music21.converter.parse(
    input_file
)


# ==========================
# Remove voices
# ==========================

print("remove voices")


for part in score.parts:

    for measure in part.getElementsByClass(
        "Measure"
    ):

        voices = measure.getElementsByClass(
            "Voice"
        )

        for v in list(voices):

            measure.remove(v)



# ==========================
# Chord -> Note
# ==========================

print("remove chords")


for chord in list(
    score.recurse()
    .getElementsByClass("Chord")
):

    try:

        if len(chord.notes):

            n = chord.notes[0]

            chord.activeSite.replace(
                chord,
                n
            )

    except:

        pass



# ==========================
# Remove grace
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
# Fix duration
# ==========================

print("fix duration")


for n in score.recurse().notesAndRests:

    try:

        # 清除所有 tuplets
        if n.duration.tuplets:

            n.duration.clearTuplet()



        ql = n.duration.quarterLength


        # 負值修正
        if ql <= 0:

            n.duration.quarterLength = 0.25



        # 太短修正
        elif ql < 0.25:

            n.duration.quarterLength = 0.25



    except Exception:

        pass



# ==========================
# Final hard cleanup
# ==========================

print("final cleanup")


for n in score.recurse().notesAndRests:

    try:

        # 再清一次 tuplet

        n.duration.clearTuplet()


        # 強制移除不可匯出的 duration

        if n.duration.type in [

            "2048th",
            "1024th",
            "512th",
            "256th",
            "128th"

        ]:

            n.duration.quarterLength = 0.25



        # 防止 MusicXML 太短

        if n.duration.quarterLength < 0.25:

            n.duration.quarterLength = 0.25



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
# Write
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