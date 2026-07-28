# jianpu_fix_musicxml.py
# V15 REBUILD ENGINE
# 完全重建 Measure，避免 jianpu_ly barcheck fail

import sys
from music21 import converter, stream, meter, note, tie


def rebuild_musicxml(input_file, output_file):

    print("===== V15 REBUILD ENGINE =====")

    score = converter.parse(input_file)

    # 只取第一旋律聲部
    part = score.parts[0]

    print("extract melody")

    events = []

    for n in part.recurse().notes:

        dur = float(n.duration.quarterLength)

        if dur <= 0:
            continue

        events.append(
            (
                float(n.offset),
                dur,
                n.pitch
            )
        )


    events.sort(key=lambda x:x[0])


    print("notes:", len(events))


    new_part = stream.Part()

    new_part.insert(
        0,
        meter.TimeSignature("4/4")
    )


    measure = stream.Measure()
    measure.number = 1

    current = 0.0


    print("rebuild measures")


    for offset, dur, pitch in events:

        remain = dur


        while remain > 0:


            space = 4.0 - current


            # 跨小節切割
            if remain > space:

                n = note.Note(pitch)

                n.duration.quarterLength = space

                n.tie = tie.Tie("start")

                measure.append(n)


                new_part.append(measure)


                measure = stream.Measure()

                measure.number += 1

                current = 0

                remain -= space


            else:

                n = note.Note(pitch)

                n.duration.quarterLength = remain

                measure.append(n)

                current += remain

                remain = 0



        # 小節滿
        if abs(current-4.0) < 0.001:

            new_part.append(measure)

            measure = stream.Measure()

            measure.number += 1

            current = 0



    # 補最後小節休止

    if current > 0:

        r = note.Rest()

        r.duration.quarterLength = 4-current

        measure.append(r)

        new_part.append(measure)



    print("FINAL CHECK")


    for i,m in enumerate(
        new_part.getElementsByClass("Measure")
    ):

        print(
            "Measure",
            i+1,
            float(m.duration.quarterLength)
        )


    new_score = stream.Score()

    new_score.append(new_part)


    print("WRITE")

    new_score.write(
        "musicxml",
        fp=output_file
    )


    print("DONE")
    print(output_file)



if __name__ == "__main__":


    if len(sys.argv)<3:

        print(
            "python jianpu_fix_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()


    rebuild_musicxml(
        sys.argv[1],
        sys.argv[2]
    )