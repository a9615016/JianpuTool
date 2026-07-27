import sys
from music21 import converter, stream, meter, note, chord
from music21.beam import Beams


VERSION = "CLEAN MUSICXML V22.9 FINAL NOTE SPLIT"


def reset_beams(score):
    print("safe beam reset")

    for n in score.recurse().notes:
        try:
            n.beams = Beams()
        except:
            pass


def remove_bad(score):

    print("remove voices")
    for v in score.recurse().getElementsByClass(stream.Voice):
        try:
            v.activeSite.remove(v)
        except:
            pass


    print("remove chords")

    for c in list(score.recurse().getElementsByClass(chord.Chord)):

        n = note.Note(
            c.pitches[-1]
        )

        n.duration = c.duration

        c.activeSite.replace(
            c,
            n
        )


def force_meter(score):

    for p in score.parts:
        p.insert(
            0,
            meter.TimeSignature("4/4")
        )


def split_overflow(measure):

    result = []

    new_measure = stream.Measure(
        number=measure.number
    )

    pos = 0


    for element in measure.notesAndRests:

        length = element.duration.quarterLength


        # 正常放入
        if pos + length <= 4:

            new_measure.append(element)
            pos += length


        else:

            remain = 4 - pos


            # 前半段
            if remain > 0:

                first = element.clone()

                first.duration.quarterLength = remain

                new_measure.append(first)



            result.append(new_measure)



            # 後半段
            second = element.clone()

            second.duration.quarterLength = length - remain


            new_measure = stream.Measure(
                number=measure.number + 1
            )

            new_measure.append(second)

            pos = length-remain



    if new_measure.duration.quarterLength < 4:

        r = note.Rest()

        r.duration.quarterLength = (
            4-new_measure.duration.quarterLength
        )

        new_measure.append(r)



    result.append(new_measure)


    return result



def rebuild_force(part):

    measures=[]


    for m in part.getElementsByClass(
        stream.Measure
    ):

        if m.duration.quarterLength > 4:

            print(
                "split overflow measure",
                m.number,
                m.duration.quarterLength
            )

            measures.extend(
                split_overflow(m)
            )

        else:

            measures.append(m)


    part.remove(
        part.getElementsByClass(stream.Measure)
    )


    for m in measures:

        part.append(m)



def check(score):

    print("check measures")

    for m in score.recurse().getElementsByClass(
        stream.Measure
    ):

        print(
            "Measure",
            m.number,
            m.duration.quarterLength
        )



def clean_musicxml(
    input_file,
    output_file
):

    print("================")
    print(VERSION)
    print("================")


    print("read")

    score = converter.parse(
        input_file
    )


    remove_bad(score)


    reset_beams(score)


    print("quantize")

    score.quantize(
        quarterLengthDivisors=[
            4,8,16
        ]
    )


    print("force 4/4")

    force_meter(score)



    print("rebuild measures")

    for p in score.parts:

        p.makeMeasures(
            inPlace=True
        )


    print("FINAL NOTE SPLIT")

    for p in score.parts:

        rebuild_force(p)



    reset_beams(score)



    check(score)


    print("write")


    score.write(
        "musicxml",
        fp=output_file
    )


    print()
    print(
        "DONE",
        output_file
    )



if __name__=="__main__":

    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )