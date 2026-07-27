import sys
import music21
import os


def clean(input_file, output_file):

    print("================")
    print("CLEAN MUSICXML")
    print("================")

    print("input:", input_file)

    score = music21.converter.parse(input_file)

    print("remove voices")

    # flatten
    flat = score.flatten()

    new_score = music21.stream.Score()
    part = music21.stream.Part()

    print("remove chords")

    for element in flat.notesAndRests:

        # 保留休止
        if isinstance(element, music21.note.Rest):
            part.append(element)

        # Note直接保留
        elif isinstance(element, music21.note.Note):
            part.append(element)

        # Chord只取最高音
        elif isinstance(element, music21.chord.Chord):

            if len(element.notes) > 0:

                highest = element.sortAscending().notes[-1]

                n = music21.note.Note(
                    highest.pitch
                )

                n.duration = element.duration

                part.append(n)


    print("rebuild measures")

    part.makeMeasures(
        inPlace=True
    )


    print("quantize")

    for n in part.recurse().notes:

        try:
            n.duration.quarterLength = round(
                n.duration.quarterLength * 4
            ) / 4

        except:
            pass


    new_score.append(part)


    print("write")

    new_score.write(
        "musicxml",
        fp=output_file
    )


    print("DONE", output_file)



if __name__ == "__main__":

    if len(sys.argv) < 3:
        print(
            "usage: python clean_musicxml.py input.musicxml output.musicxml"
        )
        sys.exit(1)


    clean(
        sys.argv[1],
        sys.argv[2]
    )
