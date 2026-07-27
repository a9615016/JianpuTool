import sys
from music21 import converter, meter, note, chord, stream


VERSION = "CLEAN MUSICXML V23.5 FINAL TIMESIG SAFE"


def clean_musicxml(input_file, output_file):

    print("================")
    print(VERSION)
    print("================")

    print("read")

    score = converter.parse(input_file)


    print("remove voices")

    for part in score.parts:

        # remove voices
        for v in list(part.recurse().getElementsByClass('Voice')):
            v.activeSite.remove(v)


        print("remove chords")

        for c in list(part.recurse().getElementsByClass('Chord')):
            n = note.Note(c.root())
            n.duration = c.duration
            c.activeSite.replace(c, n)


        print("remove beams")

        for n in part.recurse().notes:
            try:
                n.beams = None
            except:
                pass


        print("remove ties")

        for n in part.recurse().notes:
            try:
                n.tie = None
            except:
                pass


        print("duration safe")

        for n in part.recurse().notes:

            if n.duration.quarterLength <= 0:
                n.duration.quarterLength = 1



    print("force 4/4")

    for part in score.parts:

        # 清掉舊拍號
        for ts in list(part.recurse().getElementsByClass(meter.TimeSignature)):
            ts.activeSite.remove(ts)

        part.insert(
            0,
            meter.TimeSignature("4/4")
        )



    print("remove anacrusis")

    try:
        score.anacrusis = False
    except:
        pass



    print("rebuild measures")


    for part in score.parts:

        try:
            part.makeMeasures(
                meterStream=part.recurse().getElementsByClass(
                    meter.TimeSignature
                )
            )
        except Exception as e:
            print("measure rebuild skip:", e)



    print("split long notes")


    for part in score.parts:

        for n in list(part.recurse().notes):

            if n.duration.quarterLength > 4:

                remain = n.duration.quarterLength

                n.duration.quarterLength = 4

                remain -= 4

                while remain > 0:

                    new_n = note.Note(n.pitch)

                    length = min(remain,4)

                    new_n.duration.quarterLength = length

                    part.insert(
                        n.offset + 4,
                        new_n
                    )

                    remain -= length



    print("final timesig check")


    for part in score.parts:

        measures = part.getElementsByClass(
            stream.Measure
        )

        for m in measures:

            if len(
                m.getElementsByClass(
                    meter.TimeSignature
                )
            ) == 0:

                m.insert(
                    0,
                    meter.TimeSignature("4/4")
                )



    print("clear notation cache")

    try:
        score.streamStatus._beams = None
    except:
        pass


    print("FINAL WRITE")


    score.write(
        "musicxml",
        fp=output_file
    )


    print()
    print("DONE")
    print(output_file)



if __name__ == "__main__":

    if len(sys.argv) < 3:
        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )
        sys.exit(1)


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )