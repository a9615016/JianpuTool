import sys
import music21


print("CLEAN VERSION 20260724 V11")


if len(sys.argv) < 3:
    print(
        "usage: python clean_musicxml.py input.musicxml output.musicxml"
    )
    sys.exit(1)


input_file = sys.argv[1]
output_file = sys.argv[2]


print("input:", input_file)


score = music21.converter.parse(
    input_file
)


print("force 4/4")


# ==========================
# 強制4/4
# ==========================

for part in score.parts:

    # 移除舊拍號
    for ts in part.recurse().getElementsByClass(
        music21.meter.TimeSignature
    ):
        ts.ratioString = "4/4"


    # 沒拍號補一個
    if len(
        part.recurse().getElementsByClass(
            music21.meter.TimeSignature
        )
    ) == 0:

        part.insert(
            0,
            music21.meter.TimeSignature("4/4")
        )



print("remove voices")


# ==========================
# 移除voice
# ==========================

for part in score.parts:

    for v in part.recurse().getElementsByClass(
        music21.stream.Voice
    ):

        try:
            v.flatten()
        except:
            pass



print("fix duration")


# ==========================
# 修正過短音符
# ==========================

count = 0


for n in score.recurse().notesAndRests:


    try:

        if n.duration.quarterLength < 0.25:

            print(
                "fix:",
                n.duration.quarterLength
            )

            n.duration.quarterLength = 0.25

            count += 1


    except:
        pass



print(
    "fixed:",
    count
)



print("make measures")


# ==========================
# 重新建立小節
# ==========================

try:

    score.makeMeasures(
        inPlace=True
    )

except Exception as e:

    print(
        "makeMeasures error:",
        e
    )



print("force divisions")


# ==========================
# divisions統一
# ==========================

for part in score.parts:

    for m in part.getElementsByClass(
        music21.stream.Measure
    ):

        m.paddingLeft = 0
        m.paddingRight = 0



print("write clean xml")


score.write(
    "musicxml",
    fp=output_file
)


print(
    "clean完成",
    output_file
)