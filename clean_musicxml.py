from music21 import converter, stream, meter, note, chord, duration, tie
import sys
import copy


print("==============================")
print("CLEAN MUSICXML V42 JIANPU SAFE")
print("==============================")


INPUT = sys.argv[1]

if len(sys.argv) >= 3:
    OUTPUT = sys.argv[2]
else:
    OUTPUT = INPUT.replace(
        ".musicxml",
        "_clean.musicxml"
    )


print("read")

score = converter.parse(INPUT)



# =========================
# remove voices
# =========================

print("remove voices")

for n in score.flatten().notesAndRests:
    try:
        n.voice = None
    except:
        pass



# =========================
# remove chords
# =========================

print("remove chords")


for p in score.parts:

    for c in list(p.flatten().notes):

        if isinstance(c, chord.Chord):

            n = note.Note(
                c.pitches[-1]
            )

            n.duration = copy.deepcopy(
                c.duration
            )

            c.activeSite.replace(
                c,
                n
            )



# =========================
# remove beams
# =========================

print("remove beams")

for n in score.flatten().notes:

    try:
        n.beams = []
    except:
        pass



# =========================
# remove ties
# =========================

print("remove ties")

for n in score.flatten().notes:

    try:
        n.tie = None
    except:
        pass



# =========================
# remove tuplets
# =========================

print("remove tuplets")

for n in score.flatten().notesAndRests:

    try:

        n.duration.clear()
        n.duration.quarterLength = \
            n.duration.quarterLength

    except:
        pass



# =========================
# force 4/4
# =========================

print("force 4/4")


for p in score.parts:

    p.insert(
        0,
        meter.TimeSignature("4/4")
    )



# =========================
# quantize
# =========================

print("duration quantize")


allowed = [
    4,
    2,
    1,
    0.5,
    0.25,
    0.125
]


def quantize(x):

    return min(
        allowed,
        key=lambda a: abs(a-x)
    )


for n in score.flatten().notesAndRests:

    q = quantize(
        float(n.duration.quarterLength)
    )

    n.duration.quarterLength = q



# =========================
# rebuild measures
# =========================

print("rebuild measures")


for p in score.parts:

    p.makeMeasures(
        inPlace=True
    )



# =========================
# rebuild every measure offset
# =========================

print("rebuild measure offsets")


for p in score.parts:

    measures = list(
        p.getElementsByClass("Measure")
    )


    for m in measures:


        new_stream = stream.Measure(
            number=m.number
        )


        pos = 0.0


        for element in list(
            m.notesAndRests
        ):


            dur = float(
                element.duration.quarterLength
            )


            # 防止跨小節

            if pos + dur > 4:

                remain = 4-pos


                if remain > 0:

                    first = copy.deepcopy(
                        element
                    )

                    first.duration.quarterLength = remain

                    new_stream.insert(
                        pos,
                        first
                    )


                remain2 = dur-remain


                if remain2 > 0:

                    second = copy.deepcopy(
                        element
                    )

                    second.duration.quarterLength = remain2

                    # 下一小節處理
                    pass


                break


            else:

                element.offset = pos

                new_stream.insert(
                    pos,
                    element
                )

                pos += dur



        # 補滿 4 拍

        if pos < 4:

            r = note.Rest()

            r.duration.quarterLength = 4-pos

            new_stream.insert(
                pos,
                r
            )


        m.clear()

        for e in new_stream:

            m.insert(
                e.offset,
                e
            )



# =========================
# final rebuild
# =========================

print("final rebuild")


for p in score.parts:

    p.makeMeasures(
        inPlace=True
    )



# =========================
# jianpu check
# =========================

print("JIANPU SAFE CHECK")


safe=True


for p in score.parts:

    for m in p.getElementsByClass("Measure"):

        total=0

        for n in m.notesAndRests:

            total += float(
                n.duration.quarterLength
            )


        print(
            "Measure",
            m.number,
            total
        )


        if abs(total-4)>0.01:

            safe=False



if safe:

    print(
        "READY FOR JIANPU_LY"
    )

else:

    print(
        "WARNING"
    )



# =========================
# write
# =========================

print("FINAL WRITE")


score.write(
    "musicxml",
    fp=OUTPUT
)


print("DONE")
print(OUTPUT)