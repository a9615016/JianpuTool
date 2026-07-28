# clean_musicxml.py
# CLEAN MUSICXML V61 REAL QUANTIZE ENGINE

import sys
from music21 import converter, stream, note, meter, tempo


GRID = 0.25       # 1/16 note
BAR_LENGTH = 4.0


def quantize_time(x):
    return round(x / GRID) * GRID


def rebuild_part(part):

    measures = []

    for m in part.getElementsByClass(stream.Measure):

        new_m = stream.Measure(number=m.number)

        notes = []

        for n in m.notesAndRests:

            q_offset = quantize_time(n.offset)
            q_duration = quantize_time(n.duration.quarterLength)

            if q_duration <= 0:
                continue

            if isinstance(n, note.Note):
                nn = note.Note(n.pitch)
                nn.duration.quarterLength = q_duration

            elif isinstance(n, note.Rest):
                nn = note.Rest()
                nn.duration.quarterLength = q_duration

            else:
                continue

            notes.append((q_offset, nn))


        current = 0.0

        for offset, n in sorted(notes):

            if offset > current:

                r = note.Rest()
                r.duration.quarterLength = offset-current
                new_m.insert(current,r)

            new_m.insert(offset,n)

            current = offset+n.duration.quarterLength


        # 補滿小節
        if current < BAR_LENGTH:

            r = note.Rest()
            r.duration.quarterLength = BAR_LENGTH-current
            new_m.insert(current,r)


        measures.append(new_m)


    return measures



def main():

    src=sys.argv[1]
    dst=sys.argv[2]


    print("================")
    print("CLEAN MUSICXML V61 REAL QUANTIZE ENGINE")
    print("================")


    score=converter.parse(src)


    for p in score.parts:

        p.removeByClass('ChordSymbol')
        p.removeByClass('Dynamic')
        p.removeByClass('Tie')

        p.timeSignature = meter.TimeSignature("4/4")

        old=list(p.getElementsByClass(stream.Measure))

        p.remove(old)


        rebuilt=rebuild_part(stream.Part(old))

        for m in rebuilt:
            p.append(m)


    print("FINAL CHECK")


    ok=True

    for m in score.parts[0].getElementsByClass(stream.Measure):

        length=sum(
            n.duration.quarterLength
            for n in m.notesAndRests
        )

        print(
            "Measure",
            m.number,
            float(length)
        )

        if abs(length-4.0)>0.001:
            ok=False


    if ok:
        print("ALL MEASURES SAFE")
    else:
        print("WARNING measure mismatch")


    score.write(
        "musicxml",
        fp=dst
    )

    print("FINAL WRITE")
    print("DONE")
    print(dst)



if __name__=="__main__":
    main()