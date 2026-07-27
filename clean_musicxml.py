import sys
from music21 import converter, stream, note, chord, meter


VERSION = "CLEAN MUSICXML V22.7"


def fix_note(n):

    # 移除 tie
    if hasattr(n, "tie"):
        n.tie = None

    # 移除 beam
    if hasattr(n, "beams"):
        n.beams = []


def clean_musicxml(input_file, output_file):

    print("================")
    print(VERSION)
    print("================")

    print("read")
    score = converter.parse(input_file)


    print("remove voices")
    for part in score.parts:
        for m in part.getElementsByClass('Measure'):

            # 不直接設定 voices
            # music21 voices 是唯讀
            for v in m.voices:
                v.activeSite = None



    print("remove chords")
    for part in score.parts:

        for m in part.getElementsByClass('Measure'):

            replace = []

            for element in m.notes:

                if isinstance(element, chord.Chord):

                    # 取最高音
                    n = note.Note(
                        element.pitches[-1]
                    )
                    n.duration = element.duration

                    replace.append(
                        (element,n)
                    )


            for old,new in replace:
                old.activeSite.remove(old)
                m.insert(
                    old.offset,
                    new
                )



    print("remove ties + beams")

    for n in score.recurse().notes:

        fix_note(n)



    print("quantize")

    score.quantize(
        quarterLengthDivisors=[
            1,
            2,
            4
        ]
    )



    print("force 4/4")

    for part in score.parts:

        ts = part.recurse().getElementsByClass(
            meter.TimeSignature
        )

        if len(ts)==0:
            part.insert(
                0,
                meter.TimeSignature("4/4")
            )



    print("rebuild measures")

    score.makeMeasures(
        inPlace=True
    )



    print("bar normalize")

    for part in score.parts:

        for m in part.getElementsByClass(
            'Measure'
        ):

            total = m.duration.quarterLength


            if total > 4:

                print(
                    "split measure",
                    m.number,
                    total
                )

                for n in m.notes:

                    fix_note(n)



    print("check measures")

    for part in score.parts:

        for m in part.getElementsByClass(
            'Measure'
        ):

            print(
                "Measure",
                m.number,
                m.duration.quarterLength
            )



    print("write")

    score.write(
        "musicxml",
        fp=output_file
    )


    print()
    print("DONE",output_file)



if __name__=="__main__":

    if len(sys.argv)<3:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )