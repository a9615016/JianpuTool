import sys
from music21 import converter, stream, note, chord, meter, bar


VERSION = "CLEAN MUSICXML V22.4"


def split_crossing_notes(score, ticks_per_measure=64):

    print("split crossing notes")

    for part in score.parts:

        new_part = stream.Part()

        current_tick = 0

        for element in part.flatten().notesAndRests:

            if isinstance(element, note.Note):

                dur = element.duration.quarterLength

                start = current_tick
                end = current_tick + dur * 16

                while end > ticks_per_measure:

                    remain = ticks_per_measure - start

                    if remain > 0:

                        n = note.Note(element.pitch)
                        n.duration.quarterLength = remain / 16
                        new_part.append(n)

                    element.duration.quarterLength = (
                        (end - ticks_per_measure) / 16
                    )

                    start = 0
                    end = element.duration.quarterLength * 16

                    current_tick = 0

                new_part.append(element)

            elif isinstance(element, chord.Chord):

                # chord 改成最高音
                n = note.Note(element.pitches[-1])
                n.duration.quarterLength = element.duration.quarterLength
                new_part.append(n)

            else:
                new_part.append(element)


            current_tick += element.duration.quarterLength * 16


        part.coreElementsChanged()
        part.replace(part.elements, new_part.elements)



def clean_musicxml(input_file, output_file):

    print("================")
    print(VERSION)
    print("================")

    print("input:", input_file)

    print("read")

    score = converter.parse(input_file)


    print("remove voices")

    for part in score.parts:
        for v in part.voices:
            part.remove(v)


    print("remove chords")

    for part in score.parts:

        for c in list(part.recurse().getElementsByClass(chord.Chord)):

            n = note.Note(c.pitches[-1])
            n.duration = c.duration
            c.activeSite.replace(c, n)


    print("quantize")

    for n in score.recurse().notes:

        q = round(n.duration.quarterLength * 4) / 4
        n.duration.quarterLength = max(q,0.25)



    print("force 4/4")

    score.insert(
        0,
        meter.TimeSignature("4/4")
    )


    print("rebuild measures")

    score.makeMeasures(
        inPlace=True
    )


    split_crossing_notes(score)


    print("write")

    score.write(
        "musicxml",
        fp=output_file
    )


    print()
    print("DONE", output_file)



if __name__ == "__main__":

    if len(sys.argv) < 3:
        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )
        sys.exit(1)


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )