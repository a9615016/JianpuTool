# ==============================
# CLEAN MUSICXML V23.1
# FINAL DURATION LIMIT
# ==============================

from music21 import converter, meter
import sys


def remove_bad_duration(score):

    print("FINAL DURATION LIMIT")

    for note in score.recurse().notes:

        # jianpu_ly 不支援 128th
        if note.duration.type == "128th":

            print(
                "convert 128th -> 64th"
            )

            note.duration.type = "64th"


        # 避免過短音符
        if note.duration.quarterLength < 0.25:

            note.duration.quarterLength = 0.25



def reset_beams(score):

    print("safe beam reset")

    for n in score.recurse().notes:

        try:
            n.beams = []
        except:
            pass



def clean_musicxml(input_file, output_file):

    print("================")
    print("CLEAN MUSICXML V23.1 FINAL DURATION LIMIT")
    print("================")


    print("read")

    score = converter.parse(input_file)



    print("remove voices")

    for part in score.parts:

        for obj in part.recurse():

            if hasattr(obj, "voices"):

                try:
                    obj.voices = []
                except:
                    pass



    print("remove chords")

    for part in score.parts:

        chords = list(
            part.recurse().getElementsByClass("Chord")
        )

        for chord in chords:

            for n in chord.notes:

                part.insert(
                    chord.offset,
                    n
                )

            part.remove(chord)



    reset_beams(score)



    print("quantize")

    score.quantize(
        quarterLengthDivisors=[
            4,
            8,
            16
        ]
    )



    print("force 4/4")

    for part in score.parts:

        part.insert(
            0,
            meter.TimeSignature("4/4")
        )



    print("rebuild measures")

    score.makeMeasures(
        inPlace=True
    )



    print("FINAL NOTE SPLIT")
    print("FINAL REMOVE 128TH SAFE")


def remove_128th(score):

    for part in score.parts:

        for n in part.recurse().notesAndRests:

            try:
                if n.duration.type == "128th":

                    print(
                        "convert 128th -> 64th:",
                        n
                    )

                    n.duration.type = "64th"

                    # 移除 dotted 造成再次變短
                    n.duration.dots = 0

            except Exception:
                pass


remove_128th(score)

    # 保留 V23 的 note split



    remove_bad_duration(score)



    print("rebuild measures")

    score.makeMeasures(
        inPlace=True
    )



    reset_beams(score)



    print("check measures")

    for i,m in enumerate(
        score.parts[0]
        .getElementsByClass("Measure")
    ):

        print(
            "Measure",
            i+1,
            m.duration.quarterLength
        )



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



if __name__ == "__main__":

    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )