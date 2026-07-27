import sys
import music21
from music21 import stream, note, chord, meter, duration


print("================")
print("CLEAN MUSICXML V17")
print("================")


def fix_duration(n):
    """
    將 duration 限制在 jianpu_ly 可接受範圍
    """

    allowed = [
        0.25,
        0.5,
        0.75,
        1,
        1.5,
        2,
        3,
        4,
        6,
        8
    ]

    q = float(n.duration.quarterLength)

    # 找最近合法值
    closest = min(
        allowed,
        key=lambda x: abs(x-q)
    )

    n.duration = duration.Duration(closest)



def remove_chords(score):

    for c in list(score.recurse().getElementsByClass(chord.Chord)):

        notes = []

        for p in c.pitches:

            n = note.Note(p)
            n.duration = c.duration

            notes.append(n)


        for n in notes:
            c.activeSite.insert(
                c.offset,
                n
            )

        c.activeSite.remove(c)


def clean(input_file, output_file):

    print("input:", input_file)


    score = music21.converter.parse(
        input_file
    )


    print("remove voices")

    for p in score.parts:

        for v in list(
            p.recurse()
             .getElementsByClass(
                 stream.Voice
             )
        ):
            v.flatten()



    print("remove chords")

    remove_chords(score)



    print("quantize")

    score.quantize(
        quarterLengthDivisors=[
            4,
            8,
            16
        ]
    )


    print("force 4/4")


    for p in score.parts:

        for m in p.getElementsByClass(
            stream.Measure
        ):

            m.timeSignature = meter.TimeSignature(
                "4/4"
            )



    print("fix duration")


    for n in score.recurse():

        if isinstance(
            n,
            note.Note
        ):

            fix_duration(n)



    print("fix measures")


    for p in score.parts:

        measures = list(
            p.getElementsByClass(
                stream.Measure
            )
        )


        for m in measures:

            total = 0

            for n in m.notesAndRests:

                total += float(
                    n.duration.quarterLength
                )


            # 4/4 一小節最多 4拍
            if total > 4:

                overflow = total - 4

                print(
                    "trim overflow:",
                    overflow
                )

                current = 0

                for n in list(m.notesAndRests):

                    length = float(
                        n.duration.quarterLength
                    )

                    if current + length > 4:

                        n.duration = duration.Duration(
                            max(
                                0.25,
                                4-current
                            )
                        )

                    current += float(
                        n.duration.quarterLength
                    )



    print("remove empty measures")


    for p in score.parts:

        for m in list(
            p.getElementsByClass(
                stream.Measure
            )
        ):

            if len(m.notesAndRests)==0:

                p.remove(m)



    print("write")


    score.write(
        "musicxml",
        fp=output_file
    )


    print(
        "DONE",
        output_file
    )



if __name__ == "__main__":


    if len(sys.argv)<3:

        print(
            "usage: python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit(1)


    clean(
        sys.argv[1],
        sys.argv[2]
    )