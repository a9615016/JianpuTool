import sys
import os
import music21


VERSION = "CLEAN VERSION 20260726 V6"


def clean_musicxml(input_file, output_file):

    print(VERSION)
    print("input:", input_file)

    score = music21.converter.parse(input_file)

    print("remove voices")
    for part in score.parts:
        for n in part.recurse():
            if hasattr(n, "voice"):
                n.voice = None


    print("remove chords")
    for part in score.parts:
        for c in list(part.recurse().getElementsByClass("Chord")):
            c_notes = c.notes
            if len(c_notes) > 0:
                c.activeSite.replace(
                    c,
                    c_notes[0]
                )


    print("remove grace")
    for n in score.recurse():
        if hasattr(n, "grace"):
            try:
                n.duration = n.duration.getGraceDuration()
            except:
                pass


    print("fix duration")

    # 禁止過短音符
    print("limit short notes")

    for n in score.recurse().notes:

        q = n.duration.quarterLength

        # 128分音符以下全部提高
        if q < 0.0625:
            n.duration.quarterLength = 0.0625


    print("remove tuplets")

    for n in score.recurse().notes:

        if n.duration.tuplets:
            n.duration.quarterLength = (
                n.duration.quarterLength *
                n.duration.tuplets[0].tupletMultiplier()
            )

            n.duration.tuplets = []


    print("rebuild measures")

    score.makeMeasures(
        inPlace=True
    )


    print("fix bars")

    # 4/4
    target = 4.0

    for part in score.parts:

        for m in part.getElementsByClass("Measure"):

            length = m.duration.quarterLength

            # 超過小節
            if length > target:

                print(
                    "trim measure",
                    m.number,
                    length
                )

                remain = target

                for n in list(m.notesAndRests):

                    if remain <= 0:
                        m.remove(n)

                    else:

                        if n.duration.quarterLength > remain:
                            n.duration.quarterLength = remain

                        remain -= n.duration.quarterLength


            # 不足補休止
            elif length < target:

                diff = target - length

                r = music21.note.Rest()

                r.duration.quarterLength = diff

                m.insert(
                    m.duration.quarterLength,
                    r
                )


    print("final cleanup")


    # 再一次移除 tuplets
    for n in score.recurse().notes:

        n.duration.tuplets = []


    print("write")

    score.write(
        "musicxml",
        fp=output_file
    )


    print("done:", output_file)



if __name__ == "__main__":

    if len(sys.argv) < 2:
        print(
            "python clean_musicxml.py input.musicxml [output.musicxml]"
        )
        exit()


    input_file = sys.argv[1]

    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        base = os.path.splitext(input_file)[0]
        output_file = base + "_clean.musicxml"


    clean_musicxml(
        input_file,
        output_file
    )