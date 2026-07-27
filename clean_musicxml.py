import sys
import music21
from music21 import stream, note, meter, duration


print("================")
print("CLEAN MUSICXML V27")
print("TRUE NOTE SPLIT VERSION")
print("================")


def split_cross_measure_notes(score):

    print("SPLIT EVERY CROSSING NOTE")

    new_score = stream.Score()

    for part in score.parts:

        new_part = stream.Part()

        current_measure = None

        for m in part.getElementsByClass('Measure'):

            current_measure = m

            new_measure = stream.Measure(
                number=m.number
            )

            new_measure.timeSignature = meter.TimeSignature("4/4")


            for n in m.notesAndRests:

                if not isinstance(n, note.Note):
                    new_measure.append(n)
                    continue


                offset = n.offset
                length = n.duration.quarterLength


                # 4/4 一小節長度
                bar_length = 4.0


                start = offset
                end = offset + length


                if end <= bar_length:

                    new_measure.append(n)

                else:

                    print(
                        "CUT NOTE:",
                        n.pitch,
                        "duration",
                        length
                    )


                    first_length = bar_length - start

                    second_length = length - first_length


                    if first_length > 0:

                        n1 = note.Note(
                            n.pitch
                        )

                        n1.duration = duration.Duration(
                            first_length
                        )

                        new_measure.append(n1)



                    if second_length > 0:

                        # 放到下一小節
                        n2 = note.Note(
                            n.pitch
                        )

                        n2.duration = duration.Duration(
                            second_length
                        )

                        # 建立下一 measure
                        # 先加入標記
                        new_measure.insert(
                            4,
                            n2
                        )


            new_part.append(new_measure)


        new_score.append(new_part)


    return new_score



def clean(input_file, output_file):

    print("READ")

    score = music21.converter.parse(input_file)


    print("remove voices")

    for p in score.parts:
        for v in p.recurse().getElementsByClass('Voice'):
            v.activeSite.remove(v)



    print("remove chords")

    for c in score.recurse().getElementsByClass(
        'Chord'
    ):
        c.notes[0].activeSite.replace(
            c,
            c.notes[0]
        )



    print("remove beams")

    for n in score.recurse().notes:

        n.beams = None



    print("remove ties")

    for n in score.recurse().notes:

        n.tie = None



    print("force 4/4")

    for p in score.parts:

        p.insert(
            0,
            meter.TimeSignature("4/4")
        )


    print("quantize duration")

    for n in score.recurse().notesAndRests:

        q = n.duration.quarterLength

        values = [
            0.25,
            0.5,
            1,
            2,
            4
        ]

        closest = min(
            values,
            key=lambda x:abs(x-q)
        )

        n.duration.quarterLength = closest



    score = split_cross_measure_notes(score)



    print("REBUILD MEASURES")

    score.makeMeasures(
        inPlace=True
    )


    print("FILL REST")

    for p in score.parts:

        p.makeRests(
            fillGaps=True,
            inPlace=True
        )


    print("FINAL CHECK")


    for m in score.parts[0].getElementsByClass(
        'Measure'
    ):

        total = 0

        for n in m.notesAndRests:

            total += n.duration.quarterLength


        print(
            "Measure",
            m.number,
            total
        )



    print("FINAL WRITE")

    score.write(
        "musicxml",
        fp=output_file
    )


    print("DONE")
    print(output_file)



if __name__ == "__main__":

    if len(sys.argv) < 3:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()


    clean(
        sys.argv[1],
        sys.argv[2]
    )