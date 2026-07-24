import sys
import music21


print("CLEAN VERSION 20260724 V12")


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


# ==========================
# 強制 4/4
# ==========================

print("force 4/4")


for part in score.parts:

    old_ts = list(
        part.recurse().getElementsByClass(
            music21.meter.TimeSignature
        )
    )

    for ts in old_ts:
        ts.ratioString = "4/4"


    if len(old_ts) == 0:

        part.insert(
            0,
            music21.meter.TimeSignature("4/4")
        )



# ==========================
# 移除 Voice
# ==========================

print("remove voices")


for part in score.parts:

    voices = list(
        part.recurse().getElementsByClass(
            music21.stream.Voice
        )
    )

    for v in voices:

        try:
            v.flatten()
        except:
            pass



# ==========================
# 移除和弦
# ==========================

print("remove chords")


for part in score.parts:


    chords = list(
        part.recurse().getElementsByClass(
            music21.chord.Chord
        )
    )


    for c in chords:

        try:

            # 只保留最高音
            n = c.notes[-1]

            c.activeSite.replace(
                c,
                n
            )

        except:

            pass



# ==========================
# 移除重複音
# ==========================

print("remove duplicate notes")


for part in score.parts:

    seen = set()


    for n in list(
        part.recurse().notes
    ):


        try:

            key = (
                n.offset,
                n.pitch.ps
            )


            if key in seen:

                n.activeSite.remove(
                    n
                )


            else:

                seen.add(
                    key
                )

        except:

            pass



# ==========================
# 修正過短音符
# ==========================

print("fix duration")


count = 0


for n in score.recurse().notesAndRests:


    try:

        if n.duration.quarterLength < 0.25:

            print(
                "fix tiny:",
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



# ==========================
# 重新建立小節
# ==========================

print("make measures")


try:

    score.makeMeasures(
        inPlace=True
    )


except Exception as e:

    print(
        "measure error:",
        e
    )



# ==========================
# 輸出
# ==========================

print("write clean xml")


score.write(
    "musicxml",
    fp=output_file
)


print(
    "clean完成:",
    output_file
)