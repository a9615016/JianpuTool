"""
CLEAN MUSICXML V81
FINAL JIANPU COMPATIBLE
Cross Measure Split FORCE VERSION
"""

import sys
from music21 import converter, stream, note, chord, meter, tie


VERSION = "V81 CROSS MEASURE SPLIT FORCE"


def quantize_duration(n):

    q = n.duration.quarterLength

    allowed = [
        0.25,
        0.5,
        0.75,
        1,
        1.5,
        2,
        3,
        4
    ]

    closest = min(
        allowed,
        key=lambda x: abs(x-q)
    )

    n.duration.quarterLength = closest



def remove_unwanted(s):

    print("remove voices")

    for p in s.parts:
        for n in p.recurse():

            if hasattr(n,"voice"):
                n.voice = None


    print("remove chords")

    for p in s.parts:

        for c in list(p.recurse().getElementsByClass(chord.Chord)):

            if len(c.pitches):

                n = note.Note(c.pitches[0])
                n.duration = c.duration

                c.activeSite.insert(
                    c.offset,
                    n
                )

                c.activeSite.remove(c)



def force_44(s):

    print("force 4/4")

    for p in s.parts:

        p.insert(
            0,
            meter.TimeSignature("4/4")
        )



def split_cross_measure(part):

    print("split cross measure notes")


    new_part = stream.Part()


    measure_length = 4.0


    for m in part.getElementsByClass(stream.Measure):

        new_measure = stream.Measure(
            number=m.number
        )

        pos = 0


        for n in m.notesAndRests:


            dur = n.duration.quarterLength


            # 沒跨小節
            if pos + dur <= measure_length:

                new_measure.append(n)

            else:

                print(
                    "SPLIT:",
                    m.number,
                    pos,
                    dur
                )


                remain = measure_length - pos


                # 第一段

                n1 = n.clone()

                n1.duration.quarterLength = remain


                n1.tie = tie.Tie("start")


                new_measure.append(n1)



                # 第二段

                n2 = n.clone()

                n2.duration.quarterLength = dur-remain


                n2.tie = tie.Tie("stop")


                # 放到下一小節

                next_measure = stream.Measure(
                    number=m.number+1
                )

                next_measure.append(n2)


                part.insert(
                    m.offset+4,
                    next_measure
                )


            pos += dur


        new_part.append(new_measure)


    part.clear()

    for x in new_part:

        part.append(x)



def rebuild(part):

    print("rebuild measures")

    part.makeMeasures(
        inPlace=True
    )



def fill_empty(part):

    print("fill measure rest")

    for m in part.getElementsByClass(stream.Measure):

        if len(m.notes)==0:

            r = note.Rest()

            r.duration.quarterLength = 4

            m.append(r)



def check(part):

    print("FINAL CHECK")

    ok=True


    for m in part.getElementsByClass(stream.Measure):

        total = sum(
            n.duration.quarterLength
            for n in m.notesAndRests
        )

        print(
            "Measure",
            m.number,
            total
        )


        if total > 4.0001:

            ok=False


    if ok:

        print("ALL MEASURES SAFE")

    else:

        print("WARNING measure mismatch")



def clean(src,dst):

    print("================")
    print(VERSION)
    print("================")


    print("read")

    score = converter.parse(src)



    remove_unwanted(score)


    force_44(score)



    print("duration quantize")


    for p in score.parts:

        for n in p.recurse().notesAndRests:

            quantize_duration(n)



    rebuild(score.parts[0])


    split_cross_measure(
        score.parts[0]
    )


    rebuild(score.parts[0])


    fill_empty(
        score.parts[0]
    )


    rebuild(score.parts[0])


    print("clear notation cache")


    check(
        score.parts[0]
    )


    print("FINAL WRITE")


    score.write(
        "musicxml",
        fp=dst
    )


    print("DONE")
    print(dst)



if __name__=="__main__":

    if len(sys.argv)<3:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()


    clean(
        sys.argv[1],
        sys.argv[2]
    )