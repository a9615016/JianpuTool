import sys
import music21
from music21 import stream, note, chord, meter, duration


print("================")
print("CLEAN MUSICXML V19")
print("================")


def clean(input_file, output_file):

    print("input:", input_file)

    score = music21.converter.parse(input_file)

    print("remove voices")
    for p in score.parts:
        for v in p.recurse().getElementsByClass('Voice'):
            v.activeSite.remove(v)

    print("remove chords")

    for p in score.parts:
        for c in list(p.recurse().getElementsByClass('Chord')):
            n = note.Note(c.pitch)
            n.duration = c.duration
            c.replace(n)


    print("quantize")

    for n in score.recurse().notesAndRests:
        try:
            n.duration.quarterLength = round(
                float(n.duration.quarterLength) * 4
            ) / 4
        except:
            pass


    print("force 4/4")

    for p in score.parts:
        p.insert(0, meter.TimeSignature("4/4"))


    print("fix measures")

    for p in score.parts:

        measures = p.makeMeasures()

        for m in measures:

            total = 0

            elements = list(m.notesAndRests)

            for n in elements:

                q = float(n.duration.quarterLength)

                # 防止超長音符
                if q > 4:
                    n.duration.quarterLength = 4

                total += float(n.duration.quarterLength)


            # 超過4拍刪除多餘
            while total > 4 and len(m.notesAndRests):

                last = m.notesAndRests[-1]

                total -= float(last.duration.quarterLength)

                m.remove(last)


            # 不足補休止符
            if total < 4:

                rest = note.Rest(
                    quarterLength=4-total
                )

                m.append(rest)



    print("remove empty measures")

    for p in score.parts:

        for m in list(p.getElementsByClass('Measure')):

            if len(m.notesAndRests) == 0:
                p.remove(m)


    print("write")

    score.write(
        "musicxml",
        fp=output_file
    )

    print("DONE", output_file)



if __name__ == "__main__":

    if len(sys.argv) < 3:
        print(
            "usage: python clean_musicxml.py input.musicxml output.musicxml"
        )
        sys.exit(1)


    clean(
        sys.argv[1],
        sys.argv[2]
    )
