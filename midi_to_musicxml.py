from music21 import converter, stream, note, meter, instrument
import sys


print("================")
print("MIDI TO MUSICXML V5 JIANPU SAFE")
print("================")


if len(sys.argv) < 3:
    sys.exit(
        "usage: python midi_to_musicxml.py input.mid output.musicxml"
    )


midi_file = sys.argv[1]
output_file = sys.argv[2]


print("讀取 MIDI")
score = converter.parse(midi_file)



print("extract melody")


melody = stream.Part()

melody.insert(
    0,
    instrument.Vocal()
)



print("quantize")


raw_notes=[]


for n in score.recurse().notes:

    if isinstance(n,note.Note):

        dur=float(
            n.duration.quarterLength
        )


        # 16分音符
        dur=round(dur*4)/4


        if dur < 0.25:
            dur=0.25


        raw_notes.append(
            (
                n.pitch,
                dur
            )
        )



print(
    "notes:",
    len(raw_notes)
)



# =========================
# 重新排列時間
# =========================

print("rebuild timeline")


current=0


for pitch,dur in raw_notes:


    nn=note.Note(
        pitch
    )


    nn.duration.quarterLength=dur


    melody.insert(
        current,
        nn
    )


    current += dur



print(
    "total beats:",
    current
)



# =========================
# 4/4
# =========================


print("force 4/4")


melody.insert(
    0,
    meter.TimeSignature("4/4")
)



print("make measures")


melody.makeMeasures(
    inPlace=True
)



print("CHECK MEASURES")


for m in melody.getElementsByClass("Measure"):

    print(
        "Measure",
        m.number,
        m.duration.quarterLength
    )



final=stream.Score()


final.insert(
    0,
    melody
)


final.clearCache()



print("WRITE")


final.write(
    "musicxml",
    fp=output_file
)


print("DONE")
print(output_file)