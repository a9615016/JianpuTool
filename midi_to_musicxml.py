from music21 import converter, stream, note, meter, instrument, tempo
import sys


print("================")
print("MIDI TO MUSICXML V5 FINAL JIANPU SAFE")
print("================")


if len(sys.argv) < 3:
    print(
        "usage: python midi_to_musicxml.py input.mid output.musicxml"
    )
    sys.exit()


midi_file = sys.argv[1]
output_file = sys.argv[2]


print("開始 MIDI → MusicXML")
print("輸入:", midi_file)


# =====================
# Read MIDI
# =====================

print("讀取 MIDI...")


score = converter.parse(
    midi_file
)


# =====================
# Extract melody
# =====================

print("extract melody...")


notes = []


for n in score.recurse().notes:

    if isinstance(n, note.Note):

        offset = float(n.offset)

        dur = float(
            n.duration.quarterLength
        )


        # -----------------
        # 16分音符量化
        # -----------------

        offset = round(
            offset * 16
        ) / 16


        dur = round(
            dur * 16
        ) / 16


        if dur <= 0:
            continue


        if dur < 0.25:
            dur = 0.25


        notes.append(
            (
                offset,
                n.pitch,
                dur
            )
        )



print(
    "notes:",
    len(notes)
)



# =====================
# Remove overlap
# =====================

print("remove overlap")


notes.sort(
    key=lambda x:x[0]
)


clean=[]


last_end=0


for offset,pitch,dur in notes:

    if offset < last_end:

        continue


    clean.append(
        (
            offset,
            pitch,
            dur
        )
    )

    last_end = offset + dur



print(
    "clean notes:",
    len(clean)
)



# =====================
# Build Part
# =====================

print("build melody")


melody = stream.Part()


melody.insert(
    0,
    instrument.Vocal()
)


melody.insert(
    0,
    meter.TimeSignature("4/4")
)


# =====================
# Insert notes
# =====================

for offset,pitch,dur in clean:


    n = note.Note(
        pitch
    )


    n.duration.quarterLength = dur


    # 不設定 n.offset
    # 使用 insert


    melody.insert(
        offset,
        n
    )



# =====================
# Force measures
# =====================

print("make measures")


melody.makeMeasures(
    inPlace=True
)



# =====================
# Final score
# =====================

final = stream.Score()


final.insert(
    0,
    melody
)


final.clearCache()



# =====================
# Final check
# =====================

print("FINAL CHECK")


for m in melody.getElementsByClass(
    "Measure"
):

    length = float(
        m.duration.quarterLength
    )


    print(
        "Measure",
        m.number,
        length
    )



print("寫入 MusicXML...")


final.write(
    "musicxml",
    fp=output_file
)



print("完成:")
print(output_file)