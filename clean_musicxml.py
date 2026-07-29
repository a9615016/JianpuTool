from music21 import *
import sys
import copy


print("==============================")
print("CLEAN MUSICXML V90")
print("JIANPU_LY STRICT 4/4 MODE")
print("==============================")


if len(sys.argv) < 3:
    print(
        "usage: python clean_musicxml.py input.musicxml output.musicxml"
    )
    sys.exit(1)


input_file = sys.argv[1]
output_file = sys.argv[2]


print("read")

score = converter.parse(input_file)



# ==========================
# remove voices
# ==========================

print("remove voices")

for part in score.parts:

    for el in part.recurse():

        if isinstance(el, note.NotRest):

            if hasattr(el, "voice"):
                el.voice = None




# ==========================
# remove chords
# ==========================

print("remove chords")

for part in score.parts:

    for c in list(part.recurse().getElementsByClass(chord.Chord)):

        n = c.notes[0]

        n.duration = c.duration

        c.activeSite.replace(c,n)



# ==========================
# remove beams
# ==========================

print("remove beams")

for n in score.recurse().notes:

    n.beams = beam.Beams()



# ==========================
# remove ties
# ==========================

print("remove ties")

for n in score.recurse().notes:

    n.tie = None



# ==========================
# force 4/4
# ==========================

print("force 4/4")


for part in score.parts:

    for m in part.getElementsByClass(stream.Measure):

        ts = meter.TimeSignature("4/4")

        m.timeSignature = ts



# ==========================
# quantize duration
# ==========================


print("duration quantize")


allowed = [
    0.25,
    0.5,
    0.75,
    1,
    1.5,
    2,
    3,
    4
]


def quantize(q):

    return min(
        allowed,
        key=lambda x:abs(x-q)
    )


for n in score.recurse().notesAndRests:

    q = float(n.duration.quarterLength)

    n.duration.quarterLength = quantize(q)



# ==========================
# rebuild measures
# ==========================

print("rebuild measures")

for p in score.parts:

    p.makeMeasures(inPlace=True)



# ==========================
# STRICT JIANPU 4/4 FIX
# ==========================

print("jianpu_ly strict normalize")


for part in score.parts:


    measures = list(
        part.getElementsByClass(stream.Measure)
    )


    for m in measures:


        total = float(
            m.duration.quarterLength
        )


        print(
            "Measure",
            m.number,
            total
        )


        # too long
        if total > 4:


            print(
                "trim measure",
                m.number
            )


            remain = 4.0
            remove=[]


            for n in list(m.notesAndRests):

                length=float(
                    n.duration.quarterLength
                )


                if remain <=0:

                    remove.append(n)

                elif length <= remain:

                    remain -= length

                else:

                    n.duration.quarterLength = remain
                    remain=0


            for n in remove:

                m.remove(n)



        # too short
        total=float(
            m.duration.quarterLength
        )


        if total < 4:


            rest = note.Rest()

            rest.duration.quarterLength = (
                4-total
            )

            print(
                "fill rest",
                m.number,
                rest.duration.quarterLength
            )

            m.append(rest)



# ==========================
# rebuild again
# ==========================

print("final rebuild")

for p in score.parts:

    p.makeMeasures(inPlace=True)



# ==========================
# remove bad time signatures
# ==========================


print("clear invalid signatures")


for ts in score.recurse().getElementsByClass(
    meter.TimeSignature
):

    ts.ratioString = "4/4"



# ==========================
# final check
# ==========================


print("FINAL CHECK")


for m in score.parts[0].getElementsByClass(stream.Measure):

    print(
        "Measure",
        m.number,
        float(m.duration.quarterLength)
    )



print("FINAL WRITE")


score.write(
    "musicxml",
    fp=output_file
)


print("DONE")
print(output_file)