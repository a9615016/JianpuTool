import sys
import music21
from music21 import stream, note, chord, meter


VERSION = "CLEAN MUSICXML V22.1"


def clean_musicxml(input_file, output_file):

    print("================")
    print(VERSION)
    print("================")

    print("input:", input_file)

    score = music21.converter.parse(input_file)

    print("read")

    # remove voices
    print("remove voices")

    for part in score.parts:
        for el in part.recurse():
            if hasattr(el, "voice"):
                el.voice = None


    # remove chords
    print("remove chords")

    for part in score.parts:
        for c in list(part.recurse().getElementsByClass('Chord')):
            n = note.Note(c.pitches[0])
            n.duration = c.duration
            c.replace(n)


    print("quantize")

    for part in score.parts:
        for n in part.recurse().notes:
            n.duration.quarterLength = round(
                n.duration.quarterLength * 4
            ) / 4


    print("force 4/4")

    for part in score.parts:
        part.insert(
            0,
            meter.TimeSignature("4/4")
        )


    print("rebuild measures")

    new_score = stream.Score()

    for part in score.parts:

        new_part = stream.Part()

        current_measure = stream.Measure()
        current_length = 0

        for element in part.recurse().notesAndRests:

            ql = element.duration.quarterLength

            # 4/4 = 4 quarter notes
            limit = 4

            # 超過小節
            if current_length + ql > limit:

                remain = limit - current_length

                # 還剩空間
                if remain > 0:

                    if isinstance(element, note.Note):
                        n = note.Note(element.pitch)
                    elif isinstance(element, chord.Chord):
                        n = chord.Chord(element.pitches)
                    else:
                        n = note.Rest()

                    n.duration.quarterLength = remain
                    current_measure.append(n)


                # 完成小節
                new_part.append(current_measure)

                current_measure = stream.Measure()

                current_length = 0


                # 剩餘音符放下一小節
                remain_note = ql - remain

                if remain_note > 0:

                    if isinstance(element, note.Note):
                        n = note.Note(element.pitch)
                    elif isinstance(element, chord.Chord):
                        n = chord.Chord(element.pitches)
                    else:
                        n = note.Rest()

                    n.duration.quarterLength = remain_note

                    current_measure.append(n)

                    current_length = remain_note

                continue


            # 正常加入
            current_measure.append(element)
            current_length += ql



        if current_measure.duration.quarterLength < 4:

            rest = note.Rest()

            rest.duration.quarterLength = (
                4 - current_measure.duration.quarterLength
            )

            current_measure.append(rest)


        new_part.append(current_measure)

        new_score.append(new_part)


    print("final measure fix")

    # 最後檢查
    for part in new_score.parts:

        for m in part.getElementsByClass("Measure"):

            total = m.duration.quarterLength

            if total > 4:

                print(
                    "trim measure:",
                    m.number,
                    total
                )

                while m.duration.quarterLength > 4:

                    last = m[-1]

                    if last.duration.quarterLength > 0.25:

                        last.duration.quarterLength -= 0.25

                    else:
                        m.pop(-1)


            elif total < 4:

                r = note.Rest()
                r.duration.quarterLength = 4 - total
                m.append(r)


    print("write")

    new_score.write(
        "musicxml",
        fp=output_file
    )


    print()
    print("DONE", output_file)



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