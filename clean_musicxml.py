import sys
import music21
import os


print("================")
print("CLEAN MUSICXML V20")
print("================")


if len(sys.argv) < 3:
    print("usage: python clean_musicxml.py input.musicxml output.musicxml")
    sys.exit(1)


input_file = sys.argv[1]
output_file = sys.argv[2]


print("input:", input_file)


print("read")
score = music21.converter.parse(input_file)


# =========================
# remove voices
# =========================

print("remove voices")

for part in score.parts:
    for el in part.recurse():
        if hasattr(el, "voice"):
            try:
                el.voice = None
            except:
                pass


# =========================
# remove chords
# =========================

print("remove chords")

for part in score.parts:
    for chord in list(part.recurse().getElementsByClass("Chord")):
        notes = chord.notes

        for n in notes:
            chord.activeSite.insert(
                chord.offset,
                n
            )

        chord.activeSite.remove(chord)


# =========================
# quantize duration
# =========================

print("quantize")


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


def quantize_length(q):

    best = min(
        allowed,
        key=lambda x: abs(x-q)
    )

    return best



for n in score.recurse().notes:

    try:
        q = float(n.duration.quarterLength)

        n.duration.quarterLength = quantize_length(q)

    except:
        pass



# =========================
# force 4/4
# =========================

print("force 4/4")


for part in score.parts:

    part.makeMeasures(
        inPlace=True
    )


for ts in score.recurse().getElementsByClass(
        "TimeSignature"):

    ts.ratioString = "4/4"



# =========================
# FIX MEASURE OVERFLOW V20
# =========================

print("fix measure overflow")


for part in score.parts:

    measures = list(
        part.getElementsByClass("Measure")
    )


    for m in measures:

        total = 0

        for n in m.notesAndRests:

            total += float(
                n.duration.quarterLength
            )


        # 超過4拍直接修正
        if total > 4:

            print(
                "trim measure",
                m.number,
                total
            )


            remain = 4


            for n in list(m.notesAndRests):

                if remain <= 0:

                    m.remove(n)

                    continue


                length = float(
                    n.duration.quarterLength
                )


                if length > remain:

                    n.duration.quarterLength = remain


                remain -= min(
                    length,
                    remain
                )



# =========================
# remove empty measures
# =========================

print("remove empty measures")


for part in score.parts:

    for m in list(
        part.getElementsByClass("Measure")
    ):

        if len(m.notesAndRests)==0:

            part.remove(m)



# =========================
# final make measures
# =========================

print("rebuild measures")

for part in score.parts:

    part.makeMeasures(
        inPlace=True
    )


# =========================
# write
# =========================

print("write")


score.write(
    "musicxml",
    fp=output_file
)


print()
print(
    "DONE",
    output_file
)
