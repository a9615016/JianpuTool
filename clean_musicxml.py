# clean_musicxml.py
# CLEAN VERSION 20260728
# Fix jianpu_ly barcheck fail

import sys
from music21 import converter, meter, note, chord, stream


def remove_chords(score):
    print("remove chords")

    for p in score.parts:
        for c in list(p.recurse().getElementsByClass('Chord')):
            n = note.Note(c.pitches[0])
            n.duration = c.duration
            c.activeSite.replace(c, n)


def remove_ties(score):
    print("remove ties")

    for n in score.recurse().notes:
        n.tie = None


def force_44(score):
    print("force 4/4")

    for p in score.parts:
        for m in p.getElementsByClass('Measure'):
            m.timeSignature = meter.TimeSignature('4/4')


def duration_quantize(score):
    print("duration quantize")

    allowed = [
        4,
        2,
        1,
        0.5,
        0.25,
        1.5,
        3
    ]

    for n in score.recurse().notes:

        q = n.duration.quarterLength

        closest = min(
            allowed,
            key=lambda x: abs(x-q)
        )

        n.duration.quarterLength = closest


def split_cross_measure_notes(score):
    print("split cross measure notes")

    for part in score.parts:

        for measure in part.getElementsByClass('Measure'):

            current = 0

            elements = list(measure.notesAndRests)

            for n in elements:

                dur = n.duration.quarterLength

                if current + dur > 4:

                    remain = 4 - current

                    if remain > 0:

                        n.duration.quarterLength = remain

                    current = 0

                    continue

                current += dur


def rebuild_measures(score):

    print("rebuild measures")

    for part in score.parts:

        notes = list(part.recurse().notesAndRests)

        new_part = stream.Part()

        measure = stream.Measure(number=1)

        beat = 0


        for n in notes:

            dur = n.duration.quarterLength


            if beat + dur > 4:

                rest = note.Rest()

                rest.duration.quarterLength = 4 - beat

                if rest.duration.quarterLength > 0:
                    measure.append(rest)


                new_part.append(measure)


                measure = stream.Measure(
                    number=measure.number + 1
                )

                beat = 0


            measure.append(n)

            beat += dur



        if beat < 4:

            rest = note.Rest()

            rest.duration.quarterLength = 4 - beat

            measure.append(rest)


        new_part.append(measure)


        part.remove(
            part.getElementsByClass('Measure')
        )


        for m in new_part.getElementsByClass('Measure'):

            m.timeSignature = meter.TimeSignature('4/4')

            part.append(m)



def fill_measure_rest(score):

    print("fill measure rest")

    for part in score.parts:

        for m in part.getElementsByClass('Measure'):

            length = m.duration.quarterLength

            if length < 4:

                r = note.Rest()

                r.duration.quarterLength = 4-length

                m.append(r)



def final_check(score):

    print("FINAL CHECK")

    for part in score.parts:

        for m in part.getElementsByClass('Measure'):

            length = m.duration.quarterLength

            print(
                "Measure",
                m.number,
                length
            )

            if abs(length-4) > 0.01:

                raise Exception(
                    f"Measure {m.number} invalid {length}"
                )


    print("ALL MEASURES SAFE")



def clean(input_file, output_file):

    print("================")
    print("CLEAN VERSION 20260728")
    print("================")


    score = converter.parse(input_file)


    remove_chords(score)

    remove_ties(score)

    force_44(score)

    duration_quantize(score)

    split_cross_measure_notes(score)

    rebuild_measures(score)

    fill_measure_rest(score)

    rebuild_measures(score)


    final_check(score)


    print("FINAL WRITE")


    score.write(
        "musicxml",
        fp=output_file
    )


    print("DONE")
    print(output_file)



if __name__ == "__main__":

    if len(sys.argv) < 2:

        print(
            "python clean_musicxml.py input.musicxml [output.musicxml]"
        )

        sys.exit()


    input_file = sys.argv[1]


    if len(sys.argv) >= 3:

        output_file = sys.argv[2]

    else:

        output_file = "clean.musicxml"



    clean(
        input_file,
        output_file
    )