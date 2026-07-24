import sys
from music21 import converter, stream, note, chord, duration


print("CLEAN VERSION 20260724 V9")


def clean_musicxml(input_file, output_file):

    print("開始 clean MusicXML")


    score = converter.parse(input_file)


    part = score.parts[0]


    new_part = stream.Part()


    # 保留拍號
    for ts in part.recurse().getElementsByClass(
        "TimeSignature"
    ):
        new_part.insert(0, ts)



    for n in part.flatten().notes:


        if isinstance(n, chord.Chord):

            n = note.Note(
                n.pitches[0]
            )


        if isinstance(n, note.Note):


            # =====================
            # 修正超短音符
            # =====================

            if n.duration.quarterLength < 0.25:

                n.duration = duration.Duration(
                    0.25
                )


            new_part.append(
                n
            )



    new_score = stream.Score()

    new_score.insert(
        0,
        new_part
    )


    new_score.write(
        "musicxml",
        fp=output_file
    )


    print(
        "clean完成",
        output_file
    )



if __name__ == "__main__":


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )