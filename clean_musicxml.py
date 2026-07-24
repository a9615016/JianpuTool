import sys
from music21 import converter, stream, note, chord, duration


print("CLEAN VERSION 20260724 V10")


def clean_musicxml(input_file, output_file):

    print("開始 clean MusicXML")

    score = converter.parse(input_file)

    new_score = stream.Score()

    for part in score.parts:

        new_part = stream.Part()


        for element in part.flatten().notesAndRests:


            # 處理和弦
            if isinstance(element, chord.Chord):

                n = note.Note(
                    element.pitches[0]
                )

                n.offset = element.offset


            else:

                n = element



            # 只保留音符
            if isinstance(n, note.Note):


                # 修正超短音符
                if n.duration.quarterLength < 0.25:

                    n.duration = duration.Duration(0.25)


                # 強制限制 type
                n.duration.type = "16th"



            new_part.insert(
                n.offset,
                n
            )


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