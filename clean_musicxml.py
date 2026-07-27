import sys
import os
import music21


def clean(input_file, output_file):

    print("================")
    print("CLEAN MUSICXML")
    print("================")

    print("input:", input_file)

    if not os.path.exists(input_file):
        raise FileNotFoundError(input_file)


    score = music21.converter.parse(input_file)


    print("remove voices")

    for part in score.parts:

        for measure in part.getElementsByClass('Measure'):

            # 移除 voice
            for voice in list(measure.getElementsByClass('Voice')):
                for element in list(voice):
                    voice.remove(element)
                    measure.insert(element)

                measure.remove(voice)



    print("remove chords")

    for part in score.parts:

        for measure in part.getElementsByClass('Measure'):

            chords = list(
                measure.getElementsByClass('Chord')
            )

            for chord in chords:

                # 取最高音
                if len(chord.pitches) > 0:

                    highest = max(
                        chord.pitches,
                        key=lambda p: p.pitch.ps
                    )

                    note = music21.note.Note(
                        highest
                    )

                    note.duration = chord.duration

                    measure.insert(
                        chord.offset,
                        note
                    )


                measure.remove(chord)



    print("remove grace notes")

    for n in score.recurse().notes:

        if n.duration.isGrace:

            n.activeSite.remove(n)



    print("fix duration")


    # 修正不合法 duration
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


    for n in score.recurse().notes:

        q = n.duration.quarterLength

        closest = min(
            allowed,
            key=lambda x: abs(x-q)
        )

        n.duration.quarterLength = closest



    print("quantize")

    try:
        score = score.quantize(
            quarterLengthDivisors=[
                4,
                8,
                16
            ]
        )
    except Exception as e:
        print(
            "quantize skip:",
            e
        )



    print("write")

    score.write(
        "musicxml",
        fp=output_file
    )


    print(
        "DONE",
        output_file
    )



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