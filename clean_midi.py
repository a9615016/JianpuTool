from music21 import converter, stream, note, tempo, meter
import sys


STEP = 0.25   # 16分音符


def quantize_time(x):
    return round(x / STEP) * STEP


def clean_midi(src, dst):

    print("================")
    print("CLEAN MIDI V3")
    print("================")

    score = converter.parse(src)


    part = score.parts[0]


    print("remove bad notes")

    notes = []

    for n in part.recurse().notes:

        if isinstance(n, note.Note):

            if n.duration.quarterLength > 0:

                notes.append(n)


    new_part = stream.Part()


    new_part.insert(
        0,
        meter.TimeSignature("4/4")
    )


    new_part.insert(
        0,
        tempo.MetronomeMark(number=80)
    )


    print("quantize notes")


    current = 0


    for n in notes:

        start = quantize_time(n.offset)

        dur = quantize_time(
            n.duration.quarterLength
        )


        if dur <= 0:
            dur = STEP


        nn = note.Note(
            n.pitch
        )

        nn.offset = start

        nn.duration.quarterLength = dur


        new_part.insert(
            start,
            nn
        )


    result = stream.Score()

    result.append(new_part)


    print("make measures")

    result.makeMeasures(
        inPlace=True
    )


    print("CHECK")


    for i,m in enumerate(
        result.parts[0].getElementsByClass(stream.Measure),
        1
    ):

        total=sum(
            x.duration.quarterLength
            for x in m.notesAndRests
        )

        print(
            "Measure",
            i,
            total
        )


    result.write(
        "midi",
        fp=dst
    )


    print("DONE")
    print(dst)



if __name__=="__main__":

    clean_midi(
        sys.argv[1],
        sys.argv[2]
    )