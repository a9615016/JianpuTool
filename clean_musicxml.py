import sys
import os
import music21


def clean(input_file, output_file):

    print("================")
    print("CLEAN MUSICXML")
    print("================")

    print("input:", input_file)

    score = music21.converter.parse(input_file)

    print("remove voices")

    # 移除 voice 標記
    for part in score.parts:
        for el in part.recurse():
            if hasattr(el, "voice"):
                try:
                    el.voice = None
                except:
                    pass


    print("remove chords")

    # Chord 改成最高音 Note
    for part in score.parts:

        chords = list(
            part.recurse().getElementsByClass(
                music21.chord.Chord
            )
        )

        for c in chords:

            if len(c.notes) > 0:

                highest = max(
                    c.notes,
                    key=lambda n: n.pitch.midi
                )

                n = music21.note.Note(
                    highest.pitch
                )

                n.duration = c.duration

                c.activeSite.replace(
                    c,
                    n
                )


    print("remove grace notes")

    for n in score.recurse().notes:

        try:
            if n.duration.isGrace:
                n.activeSite.remove(n)
        except:
            pass



    print("fix duration")

    # 量化節奏
    for n in score.recurse().notesAndRests:

        try:

            q = n.duration.quarterLength

            allowed = [
                0.25,
                0.5,
                0.75,
                1,
                1.5,
                2,
                3,
                4
            ]

            closest = min(
                allowed,
                key=lambda x: abs(x-q)
            )

            n.duration.quarterLength = closest

        except:
            pass



    print("force 4/4")

    for part in score.parts:

        part.insert(
            0,
            music21.meter.TimeSignature("4/4")
        )


    print("remove empty")

    for part in score.parts:

        for m in list(part.getElementsByClass("Measure")):

            if len(m.notesAndRests) == 0:

                part.remove(m)



    print("write")

    score.write(
        "musicxml",
        fp=output_file
    )


    print("DONE")
    print(output_file)



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