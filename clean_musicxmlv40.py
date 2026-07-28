from music21 import converter, stream, note, meter
import sys


print("==============================")
print("CLEAN MUSICXML V26 REBUILD TIME AXIS")
print("==============================")


if len(sys.argv) < 3:
    print("usage: python clean_musicxml.py input.musicxml output.musicxml")
    sys.exit()


input_file = sys.argv[1]
output_file = sys.argv[2]


print("READ")

score = converter.parse(input_file)


# ==========================
# 取得第一聲部
# ==========================

part = score.parts[0]


print("COLLECT NOTES")


events = []


for n in part.recurse().notes:

    if isinstance(n, note.Note):

        start = float(n.offset)
        dur = float(n.duration.quarterLength)

        events.append(
            (
                start,
                dur,
                n.pitch
            )
        )


print("notes:", len(events))


# ==========================
# quantize 1/16
# ==========================

print("QUANTIZE")


GRID = 0.25


fixed=[]


for start,dur,pitch in events:

    start = round(start/GRID)*GRID
    dur = round(dur/GRID)*GRID


    if dur <=0:
        dur=GRID


    fixed.append(
        (
            start,
            dur,
            pitch
        )
    )



# ==========================
# 建立新的 score
# ==========================

print("REBUILD SCORE")


new_score = stream.Score()

new_part = stream.Part()

new_part.insert(
    0,
    meter.TimeSignature("4/4")
)


# ==========================
# 建立 4/4 measures
# ==========================

measure_map={}


for start,dur,pitch in fixed:


    measure_no = int(start // 4)+1

    pos = start % 4


    if measure_no not in measure_map:

        measure_map[measure_no]=[]


    measure_map[measure_no].append(
        (
            pos,
            dur,
            pitch
        )
    )



for m_no in sorted(measure_map):


    m = stream.Measure(
        number=m_no
    )


    current=0


    notes = sorted(
        measure_map[m_no],
        key=lambda x:x[0]
    )


    for pos,dur,pitch in notes:


        # 補空拍

        if pos > current:

            r = note.Rest(
                quarterLength=pos-current
            )

            m.append(r)


        n = note.Note(pitch)

        n.duration.quarterLength=dur


        m.append(n)


        current = pos+dur



    # 補滿4拍

    if current < 4:

        m.append(
            note.Rest(
                quarterLength=4-current
            )
        )


    new_part.append(m)



new_score.append(new_part)



# ==========================
# FINAL CHECK
# ==========================

print("FINAL CHECK")


bad=False


for m in new_part.getElementsByClass(stream.Measure):

    length=float(
        m.duration.quarterLength
    )


    print(
        "Measure",
        m.number,
        length
    )


    if abs(length-4)>0.01:
        bad=True



if bad:
    print("WARNING")
else:
    print("ALL MEASURES OK")



print("WRITE")

new_score.write(
    "musicxml",
    fp=output_file
)


print("DONE")
print(output_file)