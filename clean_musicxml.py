import sys
import music21
from music21 import stream, note, chord, meter


print("CLEAN VERSION 20260726 V8")


def clean_musicxml(input_file, output_file):

    print("input:", input_file)

    score = music21.converter.parse(input_file)


    print("remove voices")
    for p in score.parts:
        for n in p.recurse():
            if hasattr(n, "voice"):
                n.voice = None


    print("remove chords")
    for p in score.parts:
        for c in list(p.recurse().getElementsByClass(chord.Chord)):
            n = note.Note(c.root())
            n.duration = c.duration
            c.activeSite.replace(c, n)



    print("remove grace")
    for n in score.recurse().notes:
        if n.duration.isGrace:
            n.duration = music21.duration.Duration(0.25)



    print("fix duration")

    # 移除太短音符
    for n in list(score.recurse().notes):

        if n.duration.quarterLength < 0.25:
            n.duration.quarterLength = 0.25



    print("remove tuplets")

    for n in score.recurse().notes:

        if n.duration.tuplets:
            n.duration.quarterLength = round(
                n.duration.quarterLength,
                2
            )

            n.duration.tuplets = []



    print("rebuild measures")


    for part in score.parts:

        part.makeMeasures(inPlace=True)


    print("fix bars")


    # 4/4
    for part in score.parts:

        ts = part.recurse().getElementsByClass(
            meter.TimeSignature
        )

        if not ts:
            part.insert(
                0,
                meter.TimeSignature("4/4")
            )


    for part in score.parts:

        for m in part.getElementsByClass(stream.Measure):

            total = m.duration.quarterLength


            # 太長
            while total > 4:

                for n in reversed(list(m.notes)):

                    if n.duration.quarterLength > 0.25:
                        n.duration.quarterLength -= 0.25
                        break

                total = m.duration.quarterLength



            # 太短補休止符

            if total < 4:

                r = note.Rest()
                r.duration.quarterLength = 4-total
                m.append(r)



    print("final cleanup")


    # 再次量化
    for n in score.recurse().notes:

        n.duration.quarterLength = round(
            n.duration.quarterLength,
            2
        )


    print("write")

    score.write(
        "musicxml",
        fp=output_file
    )


    print("done:",output_file)



if __name__=="__main__":

    if len(sys.argv)<2:
        print(
        "python clean_musicxml.py input.musicxml output.musicxml"
        )
        sys.exit()


    inp=sys.argv[1]

    if len(sys.argv)>=3:
        out=sys.argv[2]
    else:
        out=inp.replace(
            ".musicxml",
            "_clean.musicxml"
        )


    clean_musicxml(inp,out)