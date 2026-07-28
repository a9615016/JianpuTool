from music21 import converter, stream, note, chord, meter, duration
import sys
import copy


print("==============================")
print("CLEAN MUSICXML V61 QUANTIZE ENGINE")
print("==============================")


def quantize_length(q):

    values = [
        4.0,    # whole
        2.0,    # half
        1.0,    # quarter
        0.5,    # eighth
        0.25    # sixteenth
    ]

    return min(
        values,
        key=lambda x: abs(x-q)
    )


def clean_notes(s):

    result = stream.Part()

    for el in s.flatten().notesAndRests:

        if isinstance(el, chord.Chord):
            # 保留最高音
            n = note.Note(el[-1].pitch)
        else:
            n = copy.deepcopy(el)


        old = n.duration.quarterLength

        new = quantize_length(float(old))

        n.duration = duration.Duration(new)

        result.append(n)


    return result



def rebuild_measure(part):

    score = stream.Score()
    p = stream.Part()

    p.append(meter.TimeSignature("4/4"))

    current = 0

    for n in part.notesAndRests:

        length = float(n.duration.quarterLength)


        # 超過小節直接切
        if current + length > 4:

            rest_len = 4-current

            if rest_len > 0:
                r = note.Rest()
                r.duration = duration.Duration(rest_len)
                p.append(r)

            current = 0


        p.append(n)

        current += length


        if abs(current-4)<0.001:

            current = 0


    # 最後補滿
    if current > 0:

        r = note.Rest()
        r.duration = duration.Duration(4-current)
        p.append(r)



    p.makeMeasures(inPlace=True)

    score.append(p)

    return score



def check(score):

    print("FINAL CHECK")

    ok=True

    for i,m in enumerate(score.parts[0].getElementsByClass("Measure")):

        length=float(m.duration.quarterLength)

        print(
            "Measure",
            i+1,
            length
        )

        if abs(length-4)>0.01:
            ok=False


    if ok:
        print("ALL MEASURES SAFE")
    else:
        print("WARNING measure mismatch")


    return ok



def main():

    inp=sys.argv[1]

    out=sys.argv[2]


    print("read")

    score=converter.parse(inp)


    print("remove voices")

    score.removeByClass("Voice")


    print("remove chords beams ties")

    part=score.parts[0]


    cleaned=clean_notes(part)


    print("quantize")


    final=rebuild_measure(cleaned)


    final.stripTies()


    check(final)


    print("FINAL WRITE")

    final.write(
        "musicxml",
        fp=out
    )


    print("DONE")
    print(out)



if __name__=="__main__":
    main()