from music21 import converter, stream, note, meter, tempo, tie
import sys


VERSION = "V12.1 SPLIT ENGINE"


def rebuild(input_file, output_file):

    print("====================")
    print("JIANPU FIX MUSICXML")
    print(VERSION)
    print("====================")


    old = converter.parse(input_file)

    score = stream.Score()

    part = stream.Part()

    part.append(meter.TimeSignature("4/4"))
    part.append(tempo.MetronomeMark(number=100))


    events = []

    print("extract notes")


    for n in old.recurse().notesAndRests:

        if isinstance(n, note.Note):

            events.append(
                (
                    "note",
                    n.pitch,
                    float(n.duration.quarterLength)
                )
            )

        elif isinstance(n, note.Rest):

            events.append(
                (
                    "rest",
                    None,
                    float(n.duration.quarterLength)
                )
            )


    print("events:", len(events))


    measure_no = 1
    current_measure = stream.Measure(number=measure_no)

    used = 0.0


    def add_measure():

        nonlocal current_measure
        nonlocal measure_no

        if current_measure.notesAndRests:

            # 補滿4拍

            remain = 4.0 - current_measure.duration.quarterLength

            if remain > 0.001:

                r = note.Rest()
                r.duration.quarterLength = remain
                current_measure.append(r)


            part.append(current_measure)

            print(
                "Measure",
                measure_no,
                current_measure.duration.quarterLength
            )


        measure_no += 1

        current_measure = stream.Measure(
            number=measure_no
        )


    print("split crossing notes")


    for typ, pitch, dur in events:


        remain_note = dur


        while remain_note > 0:


            space = 4.0 - current_measure.duration.quarterLength


            take = min(space, remain_note)


            if typ == "note":

                n = note.Note(pitch)

            else:

                n = note.Rest()


            n.duration.quarterLength = take


            # 跨小節標記tie

            if typ == "note" and take < remain_note:

                n.tie = tie.Tie("start")


            elif typ == "note" and remain_note < dur:

                n.tie = tie.Tie("stop")


            current_measure.append(n)


            remain_note -= take


            if current_measure.duration.quarterLength >= 4.0 - 0.001:

                add_measure()



    if current_measure.notesAndRests:

        add_measure()



    score.append(part)



    print()
    print("FINAL CHECK")


    ok = True


    for m in part.getElementsByClass(stream.Measure):

        length = float(
            m.duration.quarterLength
        )

        print(
            "Measure",
            m.number,
            length
        )


        if abs(length-4.0) > 0.001:

            ok=False



    if ok:

        print("ALL MEASURES SAFE")

    else:

        print("WARNING")


    print("WRITE")

    score.write(
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


    rebuild(
        sys.argv[1],
        sys.argv[2]
    )