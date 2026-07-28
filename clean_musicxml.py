from music21 import converter, stream, note, chord, meter
import sys
import copy


VERSION = "CLEAN MUSICXML V82 REBUILD TIMELINE"


def quantize_duration(dur, divisions=16):
    """
    量化到 16 分音符
    """
    q = round(dur * divisions) / divisions

    if q <= 0:
        q = 0.25

    return q


def rebuild_timeline(src):

    print("================")
    print(VERSION)
    print("================")

    print("read")

    score = converter.parse(src)

    part = score.parts[0]

    print("remove voices")
    print("remove chords")
    print("remove beams")
    print("remove ties")

    events = []

    # 收集全部音符
    for n in part.recurse().notes:

        if isinstance(n, chord.Chord):
            n = n.notes[0]

        if isinstance(n, note.Note):

            events.append(
                (
                    n.offset,
                    copy.deepcopy(n),
                    n.duration.quarterLength
                )
            )


    print("TOTAL NOTES:", len(events))


    # 時間排序
    events.sort(key=lambda x:x[0])


    print("rebuild timeline")


    new_part = stream.Part()

    new_part.append(
        meter.TimeSignature("4/4")
    )


    current_time = 0

    BAR = 4.0


    measure = stream.Measure(number=1)

    measure.insert(0,
        meter.TimeSignature("4/4")
    )


    measure_time = 0

    bar_no = 1


    for old_offset,n,dur in events:


        dur = quantize_duration(
            dur
        )


        # 超過小節直接切
        while measure_time + dur > BAR:

            remain = BAR - measure_time

            if remain > 0:

                nn = copy.deepcopy(n)
                nn.duration.quarterLength = remain

                measure.insert(
                    measure_time,
                    nn
                )

            new_part.append(measure)

            bar_no += 1

            measure = stream.Measure(
                number=bar_no
            )

            measure.insert(
                0,
                meter.TimeSignature("4/4")
            )

            dur -= remain

            measure_time = 0


        nn = copy.deepcopy(n)

        nn.duration.quarterLength = dur

        measure.insert(
            measure_time,
            nn
        )


        measure_time += dur



        if measure_time >= BAR-0.0001:

            new_part.append(measure)

            bar_no += 1

            measure = stream.Measure(
                number=bar_no
            )

            measure.insert(
                0,
                meter.TimeSignature("4/4")
            )

            measure_time=0



    # 最後補休止

    if measure_time < BAR:

        r = note.Rest()

        r.duration.quarterLength = (
            BAR-measure_time
        )

        measure.insert(
            measure_time,
            r
        )


    new_part.append(measure)


    out_score = stream.Score()

    out_score.append(new_part)


    print("FINAL CHECK")


    for i,m in enumerate(
        new_part.getElementsByClass(
            stream.Measure
        ),
        1
    ):

        length = m.duration.quarterLength

        print(
            "Measure",
            i,
            length
        )


        if abs(length-4.0)>0.001:

            print(
                "ERROR measure",
                i,
                length
            )

            raise Exception(
                "measure rebuild failed"
            )


    print("ALL MEASURES SAFE")


    return out_score



if __name__=="__main__":

    inp=sys.argv[1]

    out=sys.argv[2]


    score=rebuild_timeline(inp)


    print("FINAL WRITE")

    score.write(
        "musicxml",
        fp=out
    )

    print("DONE")
    print(out)