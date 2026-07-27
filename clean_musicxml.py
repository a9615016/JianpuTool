from music21 import converter, stream, note, chord, meter, beam
import sys
import os


VERSION = "CLEAN MUSICXML V22.8 FINAL SAFE BEAM"


def clean_musicxml(input_file, output_file):

    print("================")
    print(VERSION)
    print("================")

    print("input:", input_file)

    print("read")

    score = converter.parse(input_file)


    print("remove voices")

    for part in score.parts:

        for measure in part.getElementsByClass("Measure"):

            # 不直接設定 measure.voices
            # 避免 music21 property error

            for element in list(measure.notesAndRests):

                if hasattr(element, "voice"):
                    try:
                        element.voice = None
                    except:
                        pass



    print("remove chords")

    for c in score.recurse().getElementsByClass("Chord"):

        try:
            highest = c.closedPosition(forceOctave=4)

            if highest:
                n = note.Note(
                    highest[-1].pitch
                )
                n.duration = c.duration

                c.replace(n)

        except Exception:

            try:
                c.notes[0].duration = c.duration
                c.replace(c.notes[0])

            except:
                pass



    print("remove ties + beams")

    for n in score.recurse().notes:

        # remove tie

        try:
            n.tie = None
        except:
            pass


        # SAFE remove beams

        try:
            n.beams = beam.Beams()

        except Exception:
            pass



    print("quantize")

    try:
        score.quantize(
            quarterLengthDivisors=[
                1,2,4,8,16
            ],
            processOffsets=True,
            processDurations=True
        )

    except Exception:
        pass



    print("force 4/4")

    for part in score.parts:

        part.insert(
            0,
            meter.TimeSignature("4/4")
        )



    print("rebuild measures")

    try:

        score.makeMeasures(
            inPlace=True
        )

    except Exception:
        pass



    print("split crossing notes")

    try:

        score.makeNotation(
            inPlace=True
        )

    except Exception:

        pass



    print("bar normalize")


    for part in score.parts:

        measures = part.getElementsByClass(
            "Measure"
        )

        for m in measures:

            total = 0

            for n in m.notesAndRests:

                total += n.duration.quarterLength


            target = 4.0


            if total != target:

                diff = target - total


                if len(m.notesAndRests) > 0:

                    last = m.notesAndRests[-1]

                    last.duration.quarterLength += diff



    print("rebuild measures")

    try:
        score.makeMeasures(
            inPlace=True
        )

    except:
        pass



    print("check measures")

    for part in score.parts:

        for m in part.getElementsByClass("Measure"):

            total = 0

            for n in m.notesAndRests:

                total += n.duration.quarterLength


            print(
                "Measure",
                m.number,
                total
            )



    print("write")


    score.write(
        "musicxml",
        fp=output_file
    )


    print()
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


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )