from music21 import converter, stream, meter, note, chord
import sys


print("==============================")
print("MIDI TO MUSICXML V2")
print("JIANPU COMPATIBLE")
print("==============================")


if len(sys.argv) < 3:
    print(
        "python midi_to_musicxml.py input.mid output.musicxml"
    )
    sys.exit()



input_file = sys.argv[1]
output_file = sys.argv[2]


print("輸入:")
print(input_file)



# =========================
# READ MIDI
# =========================

print("讀取 MIDI...")


score = converter.parse(
    input_file
)



# =========================
# REMOVE CHORD
# =========================

print("remove chords")


for part in score.parts:


    for c in list(
        part.recurse().getElementsByClass(chord.Chord)
    ):


        if len(c.pitches):

            n = note.Note(
                c.pitches[0]
            )

            n.duration = c.duration


            c.activeSite.replace(
                c,
                n
            )



# =========================
# FORCE 4/4
# =========================

print("force 4/4")


for part in score.parts:

    part.insert(
        0,
        meter.TimeSignature("4/4")
    )



# =========================
# QUANTIZE
# =========================

print("quantize MIDI duration")


for n in score.recurse().notesAndRests:


    q = float(
        n.duration.quarterLength
    )


    # 16分音符格
    q = round(
        q * 4
    ) / 4



    if q <= 0:

        q = 0.25



    n.duration.quarterLength = q



# =========================
# CLEAN NOTATION
# =========================

print("remove notation")


for n in score.recurse().notesAndRests:


    if hasattr(n, "beams"):

        n.beams = []


    n.tie = None



# =========================
# REBUILD MEASURES
# =========================

print("rebuild measures")


for part in score.parts:


    part.makeMeasures(
        inPlace=True
    )



# =========================
# FINAL CHECK
# =========================

print("FINAL CHECK")


for part in score.parts:


    for m in part.getElementsByClass(
        stream.Measure
    ):


        size = sum(
            float(x.duration.quarterLength)
            for x in m.notesAndRests
        )


        print(
            "Measure",
            m.number,
            size
        )



# =========================
# WRITE
# =========================

print("寫入 MusicXML")


score.write(
    "musicxml",
    fp=output_file
)


print("================")
print("完成:")
print(output_file)
print("================")