from music21 import converter, stream, note, meter
import sys


print("================")
print("CLEAN MUSICXML V26 FINAL JIANPU SAFE")
print("================")


if len(sys.argv) < 3:
    print(
        "usage: python clean_musicxml.py input.musicxml output.musicxml"
    )
    sys.exit()


input_file = sys.argv[1]
output_file = sys.argv[2]


print("read")

score = converter.parse(input_file)



# =====================
# remove voices
# =====================

print("remove voices")

for p in score.parts:
    for n in p.recurse():
        if hasattr(n, "voice"):
            n.voice = None



# =====================
# remove chords
# =====================

print("remove chords")

for p in score.parts:

    for c in list(p.recurse().getElementsByClass("Chord")):

        pitches = c.pitches

        if len(pitches):

            n = note.Note(
                pitches[0],
                quarterLength=c.duration.quarterLength
            )

            c.activeSite.replace(c,n)



# =====================
# remove notation
# =====================

print("remove beams")
print("remove ties")


for n in score.recurse().notes:

    if hasattr(n,"beams"):
        n.beams = []

    n.tie = None



# =====================
# force 4/4
# =====================

print("force 4/4")


for p in score.parts:

    p.insert(
        0,
        meter.TimeSignature("4/4")
    )



# =====================
# duration quantize FINAL
# =====================

print("duration quantize FINAL")


SAFE = [
    4.0,
    2.0,
    1.0,
    0.5,
    0.25
]


for n in score.recurse().notesAndRests:

    d=float(
        n.duration.quarterLength
    )

    best=min(
        SAFE,
        key=lambda x:abs(x-d)
    )

    n.duration.quarterLength=best



# =====================
# rebuild measures
# =====================

print("rebuild measures")


for p in score.parts:

    p.makeMeasures(
        inPlace=True
    )



# =====================
# fix every measure 4 beats
# =====================

print("fix measures")


for p in score.parts:

    for m in p.getElementsByClass(stream.Measure):

        total=sum(
            float(x.duration.quarterLength)
            for x in m.notesAndRests
        )


        if total < 4:

            rest=note.Rest(
                quarterLength=4-total
            )

            m.append(rest)



        elif total > 4:

            print(
                "TRIM measure",
                m.number,
                total
            )

            remain=4.0

            for x in list(m.notesAndRests):

                if remain<=0:
                    m.remove(x)
                    continue


                d=float(
                    x.duration.quarterLength
                )


                if d>remain:

                    x.duration.quarterLength=remain

                remain-=d



# =====================
# rebuild again
# =====================

print("rebuild measures again")


for p in score.parts:

    p.makeMeasures(
        inPlace=True
    )



# =====================
# final check
# =====================

print("FINAL CHECK")


ok=True


for p in score.parts:

    for m in p.getElementsByClass(stream.Measure):

        total=sum(
            float(x.duration.quarterLength)
            for x in m.notesAndRests
        )

        print(
            "Measure",
            m.number,
            total
        )

        if abs(total-4)>0.001:
            ok=False



if ok:
    print("ALL MEASURES SAFE")
else:
    print("WARNING measure mismatch")



print("clear notation cache")

score.clearCache()



print("FINAL WRITE")


score.write(
    "musicxml",
    fp=output_file
)


print("DONE")
print(output_file)