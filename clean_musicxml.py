print("==============================")
print("CLEAN MUSICXML V26 JIANPU SAFE")
print("==============================")




from music21 import converter, stream, note, chord, meter
import sys




src = sys.argv[1]
dst = sys.argv[2]


print("READ")

score = converter.parse(src)


# =========================
# 只保留第一個 part
# =========================

print("KEEP SINGLE PART")

if len(score.parts) > 0:
    part = score.parts[0]
else:
    part = score


new_part = stream.Part()


# =========================
# 清理音符
# =========================

print("CLEAN NOTES")


events = []


for n in part.recurse().notesAndRests:


    if isinstance(n, chord.Chord):

        n = note.Note(
            n.pitches[0]
        )


    if isinstance(n, note.Note):

        if n.duration.quarterLength <= 0:
            continue


        events.append(n)


    elif isinstance(n, note.Rest):

        if n.duration.quarterLength > 0:
            events.append(n)



# =========================
# 重新量化
# =========================

print("QUANTIZE")


def quantize_length(x):

    if x <= 0.25:
        return 0.25

    if x <= 0.5:
        return 0.5

    if x <= 1:
        return 1

    if x <= 2:
        return 2

    return 4



# =========================
# 重建小節
# =========================

print("REBUILD MEASURES")


measure_no = 1
current = stream.Measure(number=measure_no)

beat = 0


for n in events:


    ql = quantize_length(
        n.duration.quarterLength
    )


    # 超過小節
    if beat + ql > 4:

        remain = 4 - beat


        if remain > 0:

            r = note.Rest()

            r.duration.quarterLength = remain

            current.append(r)



        new_part.append(current)


        print(
            "Measure",
            measure_no,
            4.0
        )


        measure_no += 1

        current = stream.Measure(
            number=measure_no
        )

        beat = 0



    n.duration.quarterLength = ql

    current.append(n)

    beat += ql



    if beat == 4:


        new_part.append(current)


        print(
            "Measure",
            measure_no,
            4.0
        )


        measure_no += 1

        current = stream.Measure(
            number=measure_no
        )

        beat = 0



# =========================
# 最後補滿
# =========================


if beat > 0:


    r = note.Rest()

    r.duration.quarterLength = 4 - beat

    current.append(r)

    new_part.append(current)



# =========================
# 設定 4/4
# =========================

print("FORCE 4/4")


new_part.insert(
    0,
    meter.TimeSignature("4/4")
)



out = stream.Score()

out.append(new_part)



# =========================
# 移除所有 notation
# =========================


print("REMOVE NOTATION")


for x in out.recurse():

    try:
        x.tie = None
    except:
        pass

    try:
        x.beams = None
    except:
        pass



# =========================
# FINAL CHECK
# =========================


print("FINAL CHECK")


for m in new_part.getElementsByClass(
    stream.Measure
):

    total = sum(
        x.duration.quarterLength
        for x in m.notesAndRests
    )

    print(
        "Measure",
        m.number,
        total
    )


print("WRITE")


out.write(
    "musicxml",
    fp=dst
)


print("================")
print("V26 DONE")
print(dst)
print("================")