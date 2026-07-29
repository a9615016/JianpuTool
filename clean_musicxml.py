# clean_musicxml.py
# V35
# 出版級 quantize + rebuild measures + jianpu_ly compatible

from music21 import converter, stream, note, chord, meter, duration, tempo
import sys
import os
import copy
from fractions import Fraction


VERSION = "CLEAN MUSICXML V36"


def fix_time_signature(s):
    """
    強制 4/4
    """
    for part in s.parts:
        for m in part.getElementsByClass(stream.Measure):
            ts = m.getContextByClass(meter.TimeSignature)
            if ts:
                ts.numerator = 4
                ts.denominator = 4

    return s


def remove_bad_time_signatures(s):

    for part in s.parts:

        for ts in list(part.recurse().getElementsByClass(meter.TimeSignature)):
            if ts.ratioString != "4/4":
                ts.numerator = 4
                ts.denominator = 4

    return s


def quantize_notes(part):

    """
    四分音符 = 1
    最小 1/16
    """

    step = Fraction(1, 4)

    for n in part.recurse().notes:

        q = Fraction(n.duration.quarterLength)

        new_q = round(q / step) * step

        if new_q <= 0:
            new_q = step

        n.duration.quarterLength = new_q


def split_cross_measure_notes(part):

    """
    切斷跨小節音符
    """

    measures = list(part.getElementsByClass(stream.Measure))

    for m in measures:

        total = 0

        for n in list(m.notes):

            total += n.duration.quarterLength

            if total > 4:

                overflow = total - 4

                first = 4 - (total - n.duration.quarterLength)

                if first > 0:

                    n.duration.quarterLength = first

                    new_n = copy.deepcopy(n)
                    new_n.duration.quarterLength = overflow

                    try:
                        m.insert(
                            m.barDuration.quarterLength,
                            new_n
                        )
                    except:
                        pass


def rebuild_measures(part):

    """
    重新建立 4/4 小節
    """

    new_part = stream.Part()

    new_part.append(
        meter.TimeSignature("4/4")
    )

    BAR = Fraction(4, 1)

    measure_no = 1
    current = stream.Measure(number=measure_no)

    beat = Fraction(0, 1)


    for n in list(part.recurse().notesAndRests):

        dur = Fraction(n.duration.quarterLength)


        while dur > 0:

            remain = BAR - beat

            if dur <= remain:

                nn = copy.deepcopy(n)
                nn.duration.quarterLength = dur

                current.append(nn)

                beat += dur
                dur = Fraction(0, 1)


            else:

                nn = copy.deepcopy(n)
                nn.duration.quarterLength = remain

                current.append(nn)

                dur -= remain

                new_part.append(current)

                measure_no += 1

                current = stream.Measure(
                    number=measure_no
                )

                beat = Fraction(0, 1)


            if beat >= BAR:

                new_part.append(current)

                measure_no += 1

                current = stream.Measure(
                    number=measure_no
                )

                beat = Fraction(0, 1)


    if len(current.notesAndRests):

        while beat < BAR:

            r = note.Rest()
            r.duration.quarterLength = min(
                Fraction(1, 1),
                BAR - beat
            )

            current.append(r)

            beat += r.duration.quarterLength


        new_part.append(current)


    return new_part



def final_check(score):

    print("FINAL CHECK")

    for i,m in enumerate(
        score.parts[0].getElementsByClass(stream.Measure),
        1
    ):

        length = sum(
            Fraction(nr.duration.quarterLength)
            for nr in m.notesAndRests
        )

        print(
            "Measure",
            i,
            float(length)
        )

        if abs(length-4)>0.01:
            print(
                "WARNING measure mismatch"
            )



def clean(input_file, output_file):

    print(VERSION)

    score = converter.parse(input_file)


    # remove tempo problem
    for t in score.recurse().getElementsByClass(tempo.MetronomeMark):
        t.activeSite.remove(t)


    score = remove_bad_time_signatures(score)

    score = fix_time_signature(score)


    new_score = stream.Score()


    for part in score.parts:

        print(
            "processing part..."
        )

        quantize_notes(part)

        rebuild = rebuild_measures(part)

        new_score.append(rebuild)


    fix_time_signature(new_score)


    final_check(new_score)


    print("FINAL WRITE")

    new_score.write(
        "musicxml",
        fp=output_file
    )


    print("DONE")
    print(output_file)



if __name__ == "__main__":

    if len(sys.argv)<2:

        print(
            "usage: python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()


    inp=sys.argv[1]


    if len(sys.argv)>=3:
        out=sys.argv[2]

    else:
        out="clean.musicxml"


    clean(
        inp,
        out
    )