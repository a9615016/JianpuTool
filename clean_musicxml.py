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


score = music21.converter.parse(input_file)



# =========================
# 1. 保留第一聲部
# =========================

for part in score.parts:

    if len(part.recurse().notes) > 0:

        print(
            "part:",
            part.id
        )



# =========================
# 2. 移除 chord
# =========================

print("remove chords")


for part in score.parts:

    for element in list(
        part.recurse()
    ):

        if isinstance(
            element,
            music21.chord.Chord
        ):

            print(
                "chord:",
                element.pitchNames
            )


            # 只留下最高音
            note = music21.note.Note(
                element.pitches[-1]
            )

            note.duration = element.duration


            element.activeSite.replace(
                element,
                note
            )



# =========================
# 3. 修正過短音
# =========================

print("fix tiny notes")


for n in score.recurse().notesAndRests:


    try:

        if n.duration.quarterLength < 0.0625:

            n.duration.quarterLength = 0.25


    except:

        pass



# =========================
# 4. 移除 Voice
# =========================


print("remove voices")


for part in score.parts:

    try:

        part.removeByClass(
            music21.stream.Voice
        )

    except:

        pass



# =========================
# 5. 輸出
# =========================

print("write")


score.write(
    "musicxml",
    fp=output_file
)


print(
    "完成:",
    output_file
)