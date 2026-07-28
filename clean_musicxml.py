# CLEAN MUSICXML V82 FINAL REBUILD TIMELINE
# Jianpu_ly compatible
# rebuild all measures from absolute timeline

import sys
from music21 import converter, stream, note, meter, tempo, clef


def quantize_duration(q):
    """
    強制量化到簡譜安全值
    """
    values = [
        4.0,
        3.0,
        2.0,
        1.5,
        1.0,
        0.75,
        0.5,
        0.25
    ]

    return min(values, key=lambda x: abs(x-q))


def clean(input_file, output_file):

    print("================")
    print("CLEAN MUSICXML V82 FINAL REBUILD TIMELINE")
    print("================")

    print("read")

    score = converter.parse(input_file)

    part = score.parts[0]


    print("extract notes")

    events=[]

    for n in part.flatten().notesAndRests:

        if isinstance(n, note.Note):

            events.append(
                (
                    n.offset,
                    n.pitch,
                    n.duration.quarterLength
                )
            )

        elif isinstance(n, note.Rest):

            events.append(
                (
                    n.offset,
                    None,
                    n.duration.quarterLength
                )
            )


    events.sort(key=lambda x:x[0])


    print("remove old measures")

    new_part = stream.Part()


    print("force 4/4")

    new_part.append(meter.TimeSignature("4/4"))


    print("rebuild timeline")


    measure_no = 1
    current = 0

    m = stream.Measure(number=measure_no)

    m.insert(0, meter.TimeSignature("4/4"))


    beat_position = 0


    for offset,pitch,dur in events:

        dur = quantize_duration(float(dur))


        # 防止跨小節
        if beat_position + dur > 4:

            remain = 4 - beat_position

            if remain > 0:

                r = note.Rest()
                r.duration.quarterLength = remain
                m.append(r)


            new_part.append(m)

            measure_no += 1

            m = stream.Measure(number=measure_no)

            beat_position = 0


        if pitch:

            n = note.Note(pitch)

        else:

            n = note.Rest()


        n.duration.quarterLength = dur

        m.append(n)

        beat_position += dur


        if beat_position >= 4:

            new_part.append(m)

            measure_no += 1

            m = stream.Measure(number=measure_no)

            beat_position = 0



    # 最後補滿

    if beat_position > 0:

        rest = note.Rest()

        rest.duration.quarterLength = 4-beat_position

        m.append(rest)

        new_part.append(m)


    print("clear notation cache")


    out = stream.Score()

    out.insert(0,new_part)


    print("FINAL CHECK")


    for i,m in enumerate(new_part.getElementsByClass(stream.Measure),1):

        total=sum(
            n.duration.quarterLength
            for n in m.notesAndRests
        )

        print(
            "Measure",
            i,
            float(total)
        )


    print("FINAL WRITE")


    out.write(
        "musicxml",
        fp=output_file
    )


    print("DONE")
    print(output_file)



if __name__=="__main__":

    if len(sys.argv)<3:
        print(
            "usage: python clean_musicxml.py input.musicxml output.musicxml"
        )
        sys.exit()


    clean(
        sys.argv[1],
        sys.argv[2]
    )