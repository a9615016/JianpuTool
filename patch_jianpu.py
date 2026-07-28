# patch_jianpu_v2.py
# Fix MusicXML for jianpu_ly
# clean.musicxml -> jianpu_ready.musicxml

import sys
from music21 import converter
from music21 import stream
from music21 import note
from music21 import meter
from music21 import chord


BAR_LENGTH = 4.0


def fix_measure(measure):

    new_measure = stream.Measure(
        number=measure.number
    )

    new_measure.append(
        meter.TimeSignature("4/4")
    )


    current = 0.0


    for element in measure.flat.notesAndRests:


        # chord 轉最高音
        if isinstance(element, chord.Chord):

            n = note.Note(
                element.highestNote.pitch
            )

        elif isinstance(element, note.Note):

            n = note.Note(
                element.pitch
            )

        elif isinstance(element, note.Rest):

            n = note.Rest()

        else:
            continue


        dur = float(
            element.duration.quarterLength
        )


        # 超過小節直接裁切
        if current + dur > BAR_LENGTH:

            dur = BAR_LENGTH - current


        if dur <= 0:
            continue


        n.duration.quarterLength = dur


        new_measure.append(
            n
        )


        current += dur


        if current >= BAR_LENGTH:
            break



    # 不足補休止

    if current < BAR_LENGTH:

        r = note.Rest()

        r.duration.quarterLength = (
            BAR_LENGTH-current
        )

        new_measure.append(
            r
        )


    return new_measure



def patch_musicxml(src, out):

    print("================")
    print("PATCH JIANPU V2")
    print("================")


    score = converter.parse(
        src
    )


    result = stream.Score()


    for part in score.parts:

        new_part = stream.Part()


        measures = part.getElementsByClass(
            stream.Measure
        )


        for m in measures:

            fixed = fix_measure(
                m
            )

            print(
                "Measure",
                m.number,
                fixed.duration.quarterLength
            )


            new_part.append(
                fixed
            )


        result.append(
            new_part
        )


    result.write(
        "musicxml",
        fp=out
    )


    print("DONE")
    print(out)



def main():

    if len(sys.argv)<3:

        print(
            "Usage:"
        )

        print(
            "python patch_jianpu_v2.py input.musicxml output.musicxml"
        )

        return


    patch_musicxml(
        sys.argv[1],
        sys.argv[2]
    )


if __name__=="__main__":
    main()