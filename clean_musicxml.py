import sys
import music21


VERSION = "CLEAN MUSICXML V21"


def clean_musicxml(input_file, output_file):

    print("================")
    print(VERSION)
    print("================")
    print("input:", input_file)

    print("read")

    score = music21.converter.parse(input_file)


    # ==========================
    # remove voices
    # ==========================
    print("remove voices")

    for part in score.parts:
        for measure in part.getElementsByClass('Measure'):
            for note in measure.notes:
                if hasattr(note, "voice"):
                    note.voice = None


    # ==========================
    # remove chords
    # ==========================
    print("remove chords")

    for part in score.parts:

        for chord in list(part.recurse().getElementsByClass('Chord')):

            notes = chord.notes

            for n in notes:
                part.insert(chord.offset, n)

            chord.activeSite.remove(chord)



    # ==========================
    # quantize
    # ==========================
    print("quantize")

    score.quantize(
        quarterLengthDivisors=[
            1,
            2,
            4,
            8,
            16
        ]
    )


    # ==========================
    # force 4/4
    # ==========================
    print("force 4/4")

    for part in score.parts:

        ts = part.recurse().getElementsByClass(
            music21.meter.TimeSignature
        )

        if len(ts)==0:
            part.insert(
                0,
                music21.meter.TimeSignature("4/4")
            )



    # ==========================
    # rebuild measures
    # ==========================
    print("rebuild measures")


    new_score = music21.stream.Score()


    for part in score.parts:

        new_part = music21.stream.Part()


        current_measure = music21.stream.Measure()

        current_length = 0

        measure_number = 1


        for element in part.flatten().notesAndRests:

            dur = element.duration.quarterLength


            # 超過4拍
            if current_length + dur > 4:

                remain = 4 - current_length


                if remain > 0:

                    element2 = element.clone()

                    element2.duration.quarterLength = remain

                    current_measure.append(element2)


                current_measure.number = measure_number

                new_part.append(current_measure)


                measure_number += 1


                current_measure = music21.stream.Measure()

                current_length = 0


                # 剩餘部分
                remain2 = dur - remain


                if remain2 > 0:

                    element3 = element.clone()

                    element3.duration.quarterLength = remain2

                    current_measure.append(element3)

                    current_length = remain2


            else:

                current_measure.append(element)

                current_length += dur



        if len(current_measure):

            # 補滿4拍

            rest_length = 4-current_length


            if rest_length > 0:

                current_measure.append(
                    music21.note.Rest(
                        quarterLength=rest_length
                    )
                )


            current_measure.number = measure_number

            new_part.append(current_measure)



        new_score.append(new_part)



    score = new_score



    # ==========================
    # remove empty
    # ==========================

    print("remove empty measures")

    for part in score.parts:

        for m in list(
            part.getElementsByClass("Measure")
        ):

            if len(m.notesAndRests)==0:

                part.remove(m)



    # ==========================
    # write
    # ==========================

    print("write")

    score.write(
        "musicxml",
        fp=output_file
    )


    print()
    print("DONE", output_file)



if __name__ == "__main__":

    if len(sys.argv)<3:

        print(
            "usage: python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )