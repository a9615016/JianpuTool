from music21 import converter, stream, note, meter, duration
import sys
import os


TARGET_BEATS = 4.0


def normalize_measure(measure):
    """
    強制每小節 4/4
    """

    new_elements = []

    current = 0.0

    for el in list(measure.notesAndRests):

        dur = el.duration.quarterLength

        # 超過小節
        if current + dur > TARGET_BEATS:

            remain = TARGET_BEATS - current

            if remain > 0:
                el2 = el.clone()
                el2.duration.quarterLength = remain
                new_elements.append(el2)

            overflow = current + dur - TARGET_BEATS

            if overflow > 0:
                rest = note.Rest()
                rest.duration.quarterLength = overflow
                new_elements.append(rest)

            current = TARGET_BEATS
            break

        else:
            new_elements.append(el)
            current += dur


    # 不足補休止符
    if current < TARGET_BEATS:

        r = note.Rest()
        r.duration.quarterLength = TARGET_BEATS-current
        new_elements.append(r)


    # 清除原內容
    for el in list(measure.notesAndRests):
        measure.remove(el)


    for el in new_elements:
        measure.append(el)


    return measure



def clean_musicxml(input_file, output_file):

    print("LOAD:", input_file)

    score = converter.parse(input_file)


    # 強制 4/4
    for part in score.parts:

        part.insert(
            0,
            meter.TimeSignature("4/4")
        )


        measures = part.makeMeasures()

        print(
            "MEASURES:",
            len(measures)
        )


        for m in measures:

            normalize_measure(m)


        part.removeByClass(stream.Measure)

        for m in measures:
            part.append(m)


    print("WRITE:", output_file)

    score.write(
        "musicxml",
        fp=output_file
    )


    print("DONE")



if __name__ == "__main__":

    if len(sys.argv)<3:
        print(
            "python midi_to_musicxml_clean.py input.musicxml output.musicxml"
        )
        sys.exit()


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )