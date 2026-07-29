# midi_to_musicxml_clean.py v7
# FINAL VERSION
# MIDI -> MusicXML -> jianpu_ly friendly

import sys
from pathlib import Path

from music21 import converter, stream, note, meter, tempo


TARGET_BEATS = 4.0


def clean_note(n):

    # remove chord
    if isinstance(n, note.Note):
        return n

    if isinstance(n, note.Rest):
        return n

    return None



def rebuild_measure(measure):

    new_measure = stream.Measure(
        number=measure.number
    )

    total = 0.0


    for element in measure.flatten().notesAndRests:

        obj = clean_note(element)

        if obj is None:
            continue


        dur = obj.duration.quarterLength


        # 超過小節直接裁掉
        if total + dur > TARGET_BEATS:

            remain = TARGET_BEATS - total

            if remain > 0:
                obj.duration.quarterLength = remain
                new_measure.append(obj)

            total = TARGET_BEATS
            break


        new_measure.append(obj)

        total += dur


        if total >= TARGET_BEATS:
            break



    # 不足補 rest

    if total < TARGET_BEATS:

        r = note.Rest()

        r.duration.quarterLength = TARGET_BEATS-total

        new_measure.append(r)


    return new_measure



def clean_part(part):

    new_part = stream.Part()

    new_part.id = part.id


    # 保留 4/4

    ts = meter.TimeSignature("4/4")

    new_part.append(ts)


    for m in part.getElementsByClass(stream.Measure):

        nm = rebuild_measure(m)

        new_part.append(nm)


    return new_part




def convert(input_file, output_file):

    print("LOAD MIDI")

    score = converter.parse(input_file)


    print("REMOVE OLD MEASURES")


    new_score = stream.Score()


    # tempo

    for t in score.flatten().getElementsByClass(
        tempo.MetronomeMark
    ):
        new_score.append(t)


    for part in score.parts:

        print(
            "PROCESS PART",
            part.id
        )

        new_score.append(
            clean_part(part)
        )


    print("FINAL CHECK")


    for p in new_score.parts:

        for m in p.getElementsByClass(
            stream.Measure
        ):

            length = m.duration.quarterLength

            print(
                "Measure",
                m.number,
                length
            )


    print("WRITE MUSICXML")


    new_score.write(
        "musicxml",
        fp=output_file
    )


    print("DONE")
    print(output_file)



if __name__ == "__main__":

    if len(sys.argv)<3:

        print(
            "python midi_to_musicxml_clean.py input.mid output.musicxml"
        )

        sys.exit(1)


    convert(
        sys.argv[1],
        sys.argv[2]
    )