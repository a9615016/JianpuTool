import sys
from music21 import converter, stream, note, chord


print("CLEAN VERSION 20260724 V8")


def clean_musicxml(input_file, output_file):

    print("開始 clean MusicXML")


    score = converter.parse(input_file)


    # ======================
    # 只取第一聲部
    # ======================

    part = score.parts[0]


    new_part = stream.Part()


    # 保留拍號
    for ts in part.recurse().getElementsByClass(
        'TimeSignature'
    ):
        new_part.insert(0, ts)


    # ======================
    # 只留下 Note
    # ======================

    for n in part.flatten().notes:


        if isinstance(n, note.Note):

            new_part.append(
                n
            )


        elif isinstance(n, chord.Chord):

            # 和弦只取最高音
            new_part.append(
                note.Note(
                    n.pitches[0]
                )
            )


    new_score = stream.Score()

    new_score.append(
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


    if len(sys.argv) != 3:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit(1)


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )