import sys
import music21


print("CLEAN VERSION 20260724 V11")


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


print("remove voices")


for part in score.parts:

    # 移除 Voice 結構
    for measure in part.getElementsByClass(
        'Measure'
    ):

        voices = measure.getElementsByClass(
            'Voice'
        )

        for v in voices:
            measure.remove(v)



print("remove chords")


for part in score.parts:

    for element in part.recurse():

        if isinstance(
            element,
            music21.chord.Chord
        ):

            # 只留最高音
            note = element.notes[-1]

            element.activeSite.replace(
                element,
                note
            )



print("fix duration")


for part in score.parts:

    for n in part.recurse().notesAndRests:


        try:

            if n.duration.quarterLength < 0.0625:

                n.duration.quarterLength = 0.25


        except:

            pass



print("remove grace notes")


for part in score.parts:

    for n in list(
        part.recurse().notes
    ):

        if n.duration.isGrace:

            n.activeSite.remove(
                n
            )



print("normalize octave")


for part in score.parts:

    for n in part.recurse().notes:


        try:

            # 限制音域
            if n.pitch.octave < 3:

                n.pitch.octave = 3


            if n.pitch.octave > 6:

                n.pitch.octave = 6


        except:

            pass



print("write")


score.write(
    "musicxml",
    fp=output_file
)


print(
    "完成:",
    output_file
)