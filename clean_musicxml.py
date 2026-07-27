from music21 import converter, stream, note, chord, meter, duration, tie
import sys
import os


print("================")
print("CLEAN MUSICXML V29")
print("TRUE NOTE DURATION SPLITTER")
print("================")


def split_note(note_obj, remain):
    """
    split note duration
    """

    first = note.Note(
        note_obj.pitch,
        quarterLength=remain
    )

    second = note.Note(
        note_obj.pitch,
        quarterLength=note_obj.duration.quarterLength - remain
    )

    return first, second



def clean(input_file, output_file):

    print("read")

    score = converter.parse(input_file)


    print("remove voices")
    print("remove chords")
    print("remove beams")
    print("remove ties")


    new_score = stream.Score()


    for part in score.parts:

        new_part = stream.Part()

        new_part.append(
            meter.TimeSignature("4/4")
        )


        current_measure = stream.Measure(number=1)

        pos = 0
        measure_length = 4.0


        for element in part.flat.notesAndRests:


            # remove chord
            if isinstance(element, chord.Chord):

                n = note.Note(
                    element.pitches[0],
                    quarterLength=element.duration.quarterLength
                )

            else:
                n = element


            ql = n.duration.quarterLength


            # skip invalid
            if ql <= 0:
                continue


            remain = ql


            while remain > 0:


                space = measure_length - pos


                # normal note
                if remain <= space:


                    new_element = n.__deepcopy__({})
                    new_element.duration = duration.Duration(remain)


                    # remove tie
                    new_element.tie = None


                    current_measure.append(
                        new_element
                    )


                    pos += remain
                    remain = 0



                else:

                    print(
                        "SPLIT NOTE:",
                        n,
                        "remain",
                        remain,
                        "space",
                        space
                    )


                    # first part
                    first = note.Note(
                        n.pitch,
                        quarterLength=space
                    )


                    first.tie = None


                    current_measure.append(first)


                    new_part.append(
                        current_measure
                    )


                    # new measure

                    current_measure = stream.Measure(
                        number=current_measure.number + 1
                    )


                    second_len = remain - space


                    n = note.Note(
                        n.pitch,
                        quarterLength=second_len
                    )


                    pos = 0
                    remain = second_len



                if pos >= measure_length:

                    new_part.append(
                        current_measure
                    )

                    current_measure = stream.Measure(
                        number=current_measure.number + 1
                    )

                    pos = 0



        # finish last measure


        if len(current_measure.notesAndRests):

            while pos < measure_length:

                r = note.Rest(
                    quarterLength=min(
                        measure_length-pos,
                        0.25
                    )
                )

                current_measure.append(r)

                pos += r.duration.quarterLength


            new_part.append(current_measure)


        new_score.append(new_part)



    print("FINAL CHECK")


    for m in new_score.parts[0].getElementsByClass("Measure"):

        total = m.duration.quarterLength

        print(
            "Measure",
            m.number,
            total
        )


    print("FINAL WRITE")


    new_score.write(
        "musicxml",
        fp=output_file
    )


    print("DONE")
    print(output_file)



if __name__ == "__main__":

    if len(sys.argv) < 3:

        print(
            "usage:"
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()


    clean(
        sys.argv[1],
        sys.argv[2]
    )