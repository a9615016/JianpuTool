import sys
import music21
from music21 import note, chord, stream, meter


print("CLEAN MUSICXML V4")


if len(sys.argv) < 3:
    print("usage:")
    print("python clean_musicxml_v4.py input.musicxml output.musicxml")
    sys.exit(1)


input_file = sys.argv[1]
output_file = sys.argv[2]


print("input:")
print(input_file)

print("output:")
print(output_file)


print("讀取 MusicXML")

score = music21.converter.parse(input_file)


print("開始清理")


# ==========================
# 移除多聲部
# ==========================

for part in score.parts:

    new_part = stream.Part()

    # 保留拍號
    ts = part.recurse().getElementsByClass(
        meter.TimeSignature
    )

    for t in ts:
        new_part.insert(0, t)


    # ======================
    # 單音旋律
    # ======================

    notes = []

    for n in part.flatten().notes:

        if isinstance(n, chord.Chord):

            # chord取最高音
            nn = n.sortAscending().notes[-1]

            new_note = note.Note(
                nn.pitch
            )

            new_note.duration = n.duration

            notes.append(new_note)


        elif isinstance(n, note.Note):

            notes.append(n)


    print(
        "notes:",
        len(notes)
    )


    # ======================
    # 建立 4/4 measure
    # ======================

    measure_num = 1

    m = stream.Measure(
        number=measure_num
    )

    current = 0


    LIMIT = 4.0


    for n in notes:

        dur = n.duration.quarterLength


        # 避免0長度
        if dur <= 0:
            continue


        # 超過小節
        if current + dur > LIMIT:


            remain = LIMIT-current


            if remain > 0:

                n2 = n.clone()

                n2.duration.quarterLength = remain

                m.append(n2)


            new_part.append(m)


            measure_num += 1

            m = stream.Measure(
                number=measure_num
            )

            current = 0


            # 剩餘部分放下一小節

            left = dur-remain


            if left > 0:

                n3 = n.clone()

                n3.duration.quarterLength = left

                m.append(n3)

                current += left


        else:

            m.append(n)

            current += dur



    if len(m.notes)>0:
        new_part.append(m)


    part.clear()

    for e in new_part:
        part.append(e)



print("重新整理小節")


# ==========================
# 強制4/4
# ==========================

for p in score.parts:

    for m in p.getElementsByClass(
        stream.Measure
    ):

        m.insert(
            0,
            meter.TimeSignature("4/4")
        )


print("寫入檔案")


score.write(
    "musicxml",
    fp=output_file
)


print("完成:")
print(output_file)


import os

print(
    "SIZE:",
    os.path.getsize(output_file)
)