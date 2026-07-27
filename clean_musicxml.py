# clean_musicxml.py
# CLEAN MUSICXML V22.8 FINAL SAFE BEAM

import sys
import music21
from music21 import stream


def reset_beams(score):
    """
    SAFE BEAM RESET
    music21 不接受 list
    """

    print("safe beam reset")

    for n in score.recurse().notes:
        try:
            n.beams = None
        except Exception:
            pass



def remove_voices(score):

    print("remove voices")

    for m in score.recurse().getElementsByClass('Measure'):

        try:
            m.removeByClass('Voice')
        except:
            pass



def remove_chords(score):

    print("remove chords")

    for element in list(score.recurse()):

        if isinstance(element, music21.chord.Chord):

            notes = element.notes

            for n in notes:
                element.activeSite.insert(
                    element.offset,
                    n
                )

            element.activeSite.remove(element)



def quantize(score):

    print("quantize")

    try:
        score.quantize(
            quarterLengthDivisors=[
                4,8,16
            ],
            processOffsets=True,
            processDurations=True
        )
    except:
        pass



def force_four_four(score):

    print("force 4/4")

    for part in score.parts:

        part.insert(
            0,
            music21.meter.TimeSignature("4/4")
        )



def rebuild_measures(score):

    print("rebuild measures")

    try:
        score.makeMeasures(
            inPlace=True
        )
    except:
        pass



def split_crossing_notes(score):

    print("split crossing notes")

    try:
        score.makeNotation(
            inPlace=True
        )
    except:
        pass



def bar_normalize(score):

    print("bar normalize")

    for part in score.parts:

        for measure in part.getElementsByClass(
            music21.stream.Measure
        ):

            total = 0

            for n in measure.notesAndRests:
                total += n.duration.quarterLength


            # 4/4 = 4拍
            if abs(total-4.0) > 0.001:

                print(
                    "fix measure",
                    measure.number,
                    total
                )

                # 不新增音符
                # 交給 jianpu_ly


def check_measure(score):

    print("check measures")

    for m in score.recurse().getElementsByClass(
        music21.stream.Measure
    ):

        length = 0

        for n in m.notesAndRests:
            length += n.duration.quarterLength


        print(
            "Measure",
            m.number,
            length
        )



def clean_musicxml(input_file, output_file):

    print("================")
    print("CLEAN MUSICXML V22.8 FINAL SAFE BEAM")
    print("================")

    print("input:", input_file)


    score = music21.converter.parse(
        input_file
    )


    print("read")


    remove_voices(score)

    remove_chords(score)


    # V22.8 FIX
    reset_beams(score)


    quantize(score)

    force_four_four(score)

    rebuild_measures(score)

    split_crossing_notes(score)

    bar_normalize(score)

    rebuild_measures(score)


    # 再次保護
    reset_beams(score)


    check_measure(score)


    print("write")


    score.write(
        "musicxml",
        fp=output_file
    )


    print()
    print("DONE", output_file)



if __name__ == "__main__":

    if len(sys.argv)<3:

        print(
            "usage: python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit(1)


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )