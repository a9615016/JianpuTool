import sys
import music21
from music21 import stream, note, chord, meter, duration


VERSION = "CLEAN MUSICXML V22.6"


def remove_voices(score):
    print("remove voices")

    for part in score.parts:
        for measure in part.getElementsByClass(stream.Measure):

            for element in list(measure.elements):
                if isinstance(element, stream.Voice):
                    measure.remove(element)

            # 把 voice 裡面的內容拉回 measure
            for v in list(measure.getElementsByClass(stream.Voice)):
                for e in list(v):
                    measure.insert(e.offset, e)
                measure.remove(v)



def remove_chords(score):
    print("remove chords")

    for part in score.parts:
        for measure in part.getElementsByClass(stream.Measure):

            for c in list(measure.getElementsByClass(chord.Chord)):
                pitches = c.pitches

                if pitches:
                    n = note.Note(pitches[-1])
                    n.duration = c.duration
                    measure.replace(c, n)



def quantize_score(score):
    print("quantize")

    for part in score.parts:
        for n in part.recurse().notesAndRests:
            try:
                n.duration.quarterLength = round(
                    n.duration.quarterLength * 4
                ) / 4
            except:
                pass



def force_time_signature(score):
    print("force 4/4")

    for part in score.parts:
        for measure in part.getElementsByClass(stream.Measure):

            ts = measure.getTimeSignatures()

            if not ts:
                measure.insert(
                    0,
                    meter.TimeSignature("4/4")
                )



def split_crossing_notes(score):
    print("split crossing notes")

    for part in score.parts:

        for measure in part.getElementsByClass(stream.Measure):

            new_elements = []

            for n in measure.notesAndRests:

                if n.duration.quarterLength > 4:

                    remain = n.duration.quarterLength

                    while remain > 4:

                        nn = n.clone()
                        nn.duration.quarterLength = 4
                        new_elements.append(nn)
                        remain -= 4

                    nn = n.clone()
                    nn.duration.quarterLength = remain
                    new_elements.append(nn)

                else:
                    new_elements.append(n)



def bar_normalize(score):
    print("bar normalize")

    target = 4.0

    for part in score.parts:

        for measure in part.getElementsByClass(stream.Measure):

            total = sum(
                e.duration.quarterLength
                for e in measure.notesAndRests
            )


            diff = target - total


            # 不足補 rest
            if diff > 0.001:

                r = note.Rest()
                r.duration.quarterLength = diff
                measure.append(r)


            # 超過修最後音
            elif diff < -0.001:

                remain = abs(diff)

                for e in reversed(
                    list(measure.notesAndRests)
                ):

                    if remain <= 0:
                        break

                    old = e.duration.quarterLength

                    if old > remain:

                        e.duration.quarterLength = old - remain
                        remain = 0

                    else:

                        measure.remove(e)
                        remain -= old



def validate(score):

    print("validate bars")

    for i, part in enumerate(score.parts):

        for m in part.getElementsByClass(stream.Measure):

            total = sum(
                e.duration.quarterLength
                for e in m.notesAndRests
            )

            if abs(total-4.0) > 0.01:

                print(
                    "WARNING measure",
                    m.number,
                    "duration",
                    total
                )



def clean_musicxml(input_file, output_file):

    print("================")
    print(VERSION)
    print("================")

    print("read")

    score = music21.converter.parse(
        input_file
    )


    remove_voices(score)

    remove_chords(score)

    quantize_score(score)

    force_time_signature(score)

    print("rebuild measures")

    split_crossing_notes(score)

    bar_normalize(score)

    validate(score)


    print("write")

    score.write(
        "musicxml",
        fp=output_file
    )


    print()
    print("DONE", output_file)



if __name__ == "__main__":

    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )