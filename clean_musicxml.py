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

    for v in part.recurse().getElementsByClass(
        'Voice'
    ):

        try:
            v.activeSite.remove(v)

        except:
            pass



print("remove chords")


for part in score.parts:

    elements = list(
        part.recurse()
    )


    for e in elements:


        if isinstance(
            e,
            music21.chord.Chord
        ):

            print(
                "Chord:",
                e.pitchNames
            )


            # 只保留最高音
            note = e.notes[-1]


            e.activeSite.replace(
                e,
                note
            )




print("fix duration")


for n in score.recurse().notesAndRests:


    try:

        if n.duration.quarterLength < 0.0625:


            print(
                "tiny:",
                n,
                n.duration.quarterLength
            )


            n.duration.quarterLength = 0.25



    except:

        pass



print("remove duplicate notes")


for part in score.parts:


    last_pitch = None


    for n in list(
        part.recurse().notes
    ):


        if last_pitch == n.pitch:


            print(
                "duplicate:",
                n.pitch
            )


            try:

                n.activeSite.remove(
                    n
                )

            except:

                pass


        else:

            last_pitch = n.pitch




print("write clean xml")


score.write(
    "musicxml",
    fp=output_file
)


print(
    "完成:",
    output_file
)