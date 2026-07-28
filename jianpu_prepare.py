#!/usr/bin/env python3
# ==========================================
# Jianpu Prepare FINAL
# MusicXML -> jianpu_ly compatible
# ==========================================

import sys
from music21 import converter, stream, note, meter, chord


QUARTER = 0.25


def quantize_duration(q):
    """
    四分音符量化
    """
    return round(q / QUARTER) * QUARTER


def clean_measure(m):

    total = 0

    new_elements = []

    for e in m.notesAndRests:

        # chord 取最高音
        if isinstance(e, chord.Chord):
            n = note.Note(e.pitches[-1])
            n.duration.quarterLength = quantize_duration(
                e.duration.quarterLength
            )
            e = n


        if isinstance(e, note.Note):

            dur = quantize_duration(
                e.duration.quarterLength
            )

            if dur <= 0:
                continue

            e.duration.quarterLength = dur


        elif isinstance(e, note.Rest):

            e.duration.quarterLength = quantize_duration(
                e.duration.quarterLength
            )


        # 移除 notation
        if hasattr(e, "beams"):
            e.beams = None

        if hasattr(e, "tie"):
            e.tie = None


        total += e.duration.quarterLength

        new_elements.append(e)


    # 重建小節
    m.clear()

    current = 0

    for e in new_elements:

        if current >= 4:
            break


        remain = 4 - current


        if e.duration.quarterLength > remain:

            e.duration.quarterLength = remain


        m.append(e)

        current += e.duration.quarterLength


    # 不足補休止
    if current < 4:

        r = note.Rest()

        r.duration.quarterLength = round(
            4-current,
            2
        )

        m.append(r)



def prepare(input_file, output_file):

    print("================")
    print("JIANPU PREPARE FINAL")
    print("================")


    print("read musicxml")

    score = converter.parse(input_file)


    print("remove voices")

    for p in score.parts:

        # 強制4/4
        p.insert(
            0,
            meter.TimeSignature("4/4")
        )


        print("process measures")


        for m in p.getElementsByClass(
            stream.Measure
        ):

            clean_measure(m)


    print("clear cache")

    score.makeNotation(
        inPlace=True
    )


    print("FINAL CHECK")


    for p in score.parts:

        for m in p.getElementsByClass(
            stream.Measure
        ):

            length = sum(
                x.duration.quarterLength
                for x in m.notesAndRests
            )


            print(
                "Measure",
                m.number,
                length
            )


    print("WRITE")

    score.write(
        "musicxml",
        fp=output_file
    )


    print("DONE")
    print(output_file)



if __name__ == "__main__":

    if len(sys.argv) < 3:

        print(
            "python jianpu_prepare.py input.musicxml output.musicxml"
        )

        sys.exit(1)


    prepare(
        sys.argv[1],
        sys.argv[2]
    )