# CLEAN MUSICXML V31
VERSION = "V31"

print("CLEAN MUSICXML", VERSION)

from music21 import converter, stream, note, chord, meter
import sys


def fix_measure_overflow(score):

    print("split overflow notes")

    for part in score.parts:

        new_measures = []

        for m in part.getElementsByClass('Measure'):

            new_m = stream.Measure(number=m.number)
            current = 0.0
            limit = 4.0

            for n in m.notesAndRests:

                dur = n.duration.quarterLength

                # 超過小節
                if current + dur > limit:

                    remain = limit - current

                    if remain > 0:

                        nn = n.deepcopy()
                        nn.duration.quarterLength = remain
                        new_m.append(nn)

                    new_measures.append(new_m)

                    new_m = stream.Measure(number=m.number+0.1)

                    left = dur - remain

                    if left > 0:
                        nn = n.deepcopy()
                        nn.duration.quarterLength = left
                        new_m.append(nn)

                    current = left

                else:
                    new_m.append(n)
                    current += dur


            if len(new_m.notesAndRests):
                new_measures.append(new_m)


        part.removeByClass('Measure')

        for nm in new_measures:
            part.append(nm)


    return score



def clean(input_file, output_file):

    score = converter.parse(input_file)

    print("remove chords")

    for p in score.parts:
        for c in p.recurse().getElementsByClass(chord.Chord):
            c.notes[0].duration = c.duration
            c.activeSite.replace(c.notes[0])
            c.activeSite.remove(c)


    print("remove beams")

    for n in score.recurse().notes:
        n.beams = []


    print("remove ties")

    for n in score.recurse().notes:
        n.tie = None


    print("force 4/4")

    for p in score.parts:
        p.insert(0,meter.TimeSignature("4/4"))


    print("split overflow")

    score = fix_measure_overflow(score)


    print("FINAL CHECK")

    for m in score.parts[0].getElementsByClass('Measure'):
        length = m.duration.quarterLength
        print(
            "Measure",
            m.number,
            length
        )


    score.write(
        "musicxml",
        fp=output_file
    )


if __name__ == "__main__":

    clean(
        sys.argv[1],
        sys.argv[2]
    )