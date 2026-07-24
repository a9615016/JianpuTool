import music21
import sys


def rebuild(input_file, output_file):

    print("開始重建 MusicXML")


    score = music21.converter.parse(
        input_file
    )


    # 只取第一條旋律

    if len(score.parts):

        part = score.parts[0]

    else:

        part = score



    new_part = music21.stream.Part()



    for n in part.flatten().notesAndRests:


        if isinstance(
            n,
            music21.note.Note
        ):

            note = music21.note.Note(
                n.pitch
            )

            note.duration = n.duration

            new_part.append(note)



        elif isinstance(
            n,
            music21.note.Rest
        ):

            rest = music21.note.Rest()

            rest.duration = n.duration

            new_part.append(rest)



    # 固定調性

    new_part.insert(
        0,
        music21.key.Key("C")
    )


    # 固定拍號

    new_part.insert(
        0,
        music21.meter.TimeSignature("4/4")
    )



    new_part.write(
        "musicxml",
        fp=output_file
    )


    print(
        "完成",
        output_file
    )



if __name__=="__main__":


    rebuild(
        sys.argv[1],
        sys.argv[2]
    )