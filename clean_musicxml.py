import sys
import music21
import os


def clean(input_file, output_file):

    print("================")
    print("CLEAN MUSICXML")
    print("================")

    print("input:", input_file)

    score = music21.converter.parse(input_file)

    # ==========================
    # 移除 voices
    # ==========================

    print("remove voices")

    for part in score.parts:
        for measure in part.getElementsByClass('Measure'):
            for voice in list(measure.voices):
                measure.remove(voice)


    # ==========================
    # 移除 chords
    # ==========================

    print("remove chords")

    for part in score.parts:

        for chord in list(part.recurse().getElementsByClass('Chord')):

            notes = chord.notes

            if len(notes) > 0:

                for n in notes:
                    chord.activeSite.insert(
                        chord.offset,
                        n
                    )

            chord.activeSite.remove(chord)



    # ==========================
    # Quantize
    # ==========================

    print("quantize")

    for part in score.parts:

        part.quantize(
            quarterLengthDivisors=[
                4,
                3,
                2,
                1
            ],
            processOffsets=True,
            processDurations=True
        )


    # ==========================
    # 強制 4/4
    # ==========================

    print("force 4/4")

    for part in score.parts:

        for measure in part.getElementsByClass("Measure"):

            measure.timeSignature = music21.meter.TimeSignature("4/4")



    # ==========================
    # 修正 duration
    # ==========================

    print("fix duration")

    for part in score.parts:

        for measure in part.getElementsByClass("Measure"):

            total = 0

            for n in measure.notesAndRests:

                total += n.duration.quarterLength


            target = 4


            # 超過小節
            if total > target:

                diff = total - target

                for n in reversed(measure.notesAndRests):

                    if diff <= 0:
                        break

                    remove = min(
                        diff,
                        n.duration.quarterLength
                    )

                    n.duration.quarterLength -= remove
                    diff -= remove



            # 不足補 rest
            elif total < target:

                rest = music21.note.Rest()

                rest.duration.quarterLength = target - total

                measure.append(rest)



    # ==========================
    # 移除空小節
    # ==========================

    print("remove empty measures")

    for part in score.parts:

        for m in list(part.getElementsByClass("Measure")):

            if len(m.notesAndRests)==0:

                part.remove(m)



    print("write")

    score.write(
        "musicxml",
        fp=output_file
    )


    print("DONE", output_file)



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