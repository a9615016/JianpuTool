import sys
import music21


print("CLEAN VERSION 20260724 V10")


if len(sys.argv) < 3:
    print(
        "usage: python clean_musicxml.py input.musicxml output.musicxml"
    )
    sys.exit(1)


input_file = sys.argv[1]
output_file = sys.argv[2]


print("input:", input_file)


score = music21.converter.parse(
    input_file
)


print("remove bad duration")


for part in score.parts:

    for n in part.recurse().notesAndRests:


        # 修正超短音符
        try:

            if n.duration.quarterLength < 0.0625:

                print(
                    "fix tiny note:",
                    n,
                    n.duration.quarterLength
                )

                n.duration.quarterLength = 0.25

        except:

            pass



print("remove voices")


for part in score.parts:

    try:

        part.removeByClass(
            'Voice'
        )

    except:

        pass



print("write clean xml")


score.write(
    "musicxml",
    fp=output_file
)


print(
    "clean完成",
    output_file
)