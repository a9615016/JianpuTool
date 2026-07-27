import sys
import copy
import music21


print("================")
print("CLEAN MUSICXML V21.1")
print("================")


def clean_musicxml(input_file, output_file):

    print("input:", input_file)

    print("read")
    score = music21.converter.parse(input_file)


    print("remove voices")
    for part in score.parts:
        for element in part.recurse():
            if isinstance(element, music21.note.Note):
                pass


    print("remove chords")

    for part in score.parts:
        for chord in list(part.recurse().getElementsByClass('Chord')):
            notes = chord.notes
            for n in notes:
                part.insert(chord.offset, n)
            chord.activeSite.remove(chord)


    print("quantize")

    for part in score.parts:
        for n in part.recurse().notes:
            n.duration.quarterLength = round(
                n.duration.quarterLength * 4
            ) / 4


    print("force 4/4")

    score.insert(0, music21.meter.TimeSignature('4/4'))


    print("rebuild measures")

    new_score = music21.stream.Score()

    for part in score.parts:

        new_part = music21.stream.Part()

        measure_no = 1
        current_measure = music21.stream.Measure(number=measure_no)

        total = 0

        for element in part.recurse().notesAndRests:

            # V21.1 修正：
            # clone() 不存在，改 deepcopy()
            element2 = copy.deepcopy(element)

            length = element2.duration.quarterLength


            if total + length > 4:

                while total < 4:
                    rest = music21.note.Rest()
                    rest.duration.quarterLength = 4 - total
                    current_measure.append(rest)
                    total += rest.duration.quarterLength


                new_part.append(current_measure)

                measure_no += 1
                current_measure = music21.stream.Measure(
                    number=measure_no
                )
                total = 0


            current_measure.append(element2)
            total += length


        if total < 4:

            rest = music21.note.Rest()
            rest.duration.quarterLength = 4 - total
            current_measure.append(rest)


        new_part.append(current_measure)

        new_score.append(new_part)


    print("remove empty measures")

    for part in new_score.parts:
        for m in list(part.getElementsByClass('Measure')):
            if len(m.notesAndRests) == 0:
                part.remove(m)


    print("write")

    new_score.write(
        "musicxml",
        fp=output_file
    )


    print()
    print("DONE", output_file)



if __name__ == "__main__":

    if len(sys.argv) < 3:
        print(
            "usage: python clean_musicxml.py input.musicxml output.musicxml"
        )
        sys.exit()


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )