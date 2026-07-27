from music21 import converter, stream, meter, note, chord, tie
import sys


VERSION = "CLEAN MUSICXML V23.7.1 FINAL MEASURE SPLIT SAFE"


def remove_bad_elements(score):

    print("remove voices")

    for part in score.parts:

        for v in list(part.voices):
            try:
                part.remove(v)
            except:
                pass


    print("remove chords")

    for c in score.recurse().getElementsByClass(chord.Chord):
        try:
            n = c.notes[0]
            c.activeSite.replace(c, n)
        except:
            pass


    print("remove beams")

    for n in score.recurse().notes:
        try:
            n.beams = None
        except:
            pass


    print("remove ties")

    for n in score.recurse().notes:
        try:
            n.tie = None
        except:
            pass



def force_time_signature(score):

    print("force 4/4")

    for part in score.parts:

        ts = meter.TimeSignature("4/4")

        part.insert(0, ts)



def split_long_measures(score):

    print("measure split")

    for part in score.parts:

        old_measures = list(
            part.getElementsByClass(stream.Measure)
        )

        new_measures = []


        for measure in old_measures:

            ql = measure.duration.quarterLength

            print(
                "Measure",
                measure.number,
                ql
            )


            if ql <= 4:
                new_measures.append(measure)
                continue


            print(
                "split measure",
                measure.number
            )


            current = stream.Measure(
                number=measure.number
            )

            total = 0


            for element in measure.notesAndRests:

                length = element.duration.quarterLength


                if total + length > 4:

                    new_measures.append(current)

                    current = stream.Measure(
                        number=measure.number
                    )

                    total = 0


                current.append(element)

                total += length


                if total == 4:

                    new_measures.append(current)

                    current = stream.Measure(
                        number=measure.number
                    )

                    total = 0



            if len(current.notesAndRests) > 0:
                new_measures.append(current)



        # 清除舊 measures
        for m in old_measures:

            try:
                part.remove(m)

            except Exception:
                pass



        # 放回新 measures
        for m in new_measures:

            part.append(m)



def clean_musicxml(input_file, output_file):

    print("================")
    print(VERSION)
    print("================")


    print("read")

    score = converter.parse(input_file)


    remove_bad_elements(score)


    force_time_signature(score)


    split_long_measures(score)


    print("clear notation cache")

    try:
        score.streamStatus.clear()
    except:
        pass


    print("FINAL WRITE")


    score.write(
        "musicxml",
        fp=output_file
    )


    print()
    print("DONE")
    print(output_file)



if __name__ == "__main__":

    if len(sys.argv) < 3:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )