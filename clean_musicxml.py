# CLEAN MUSICXML V64
# Absolute Timeline Rebuilder
# BasicPitch + Render + jianpu_ly FINAL

import sys
from music21 import converter, stream, note, meter, tempo, clef


TARGET_BEATS = 4.0


def quantize_duration(q):

    allowed = [
        4.0,
        2.0,
        1.0,
        0.5,
        0.25
    ]

    best = min(
        allowed,
        key=lambda x: abs(x-q)
    )

    return best



def split_note(n, remain):

    result=[]

    dur=n.duration.quarterLength

    while dur > remain:

        x=n.__deepcopy__()

        x.duration.quarterLength=remain

        result.append(x)

        dur -= remain

        remain=TARGET_BEATS


    if dur>0:
        x=n.__deepcopy__()
        x.duration.quarterLength=dur
        result.append(x)

    return result



def rebuild(part):

    notes=[]

    for n in part.flatten().notesAndRests:

        if isinstance(n,note.Note):

            d=quantize_duration(
                float(n.duration.quarterLength)
            )

            n.duration.quarterLength=d

            notes.append(n)


        elif isinstance(n,note.Rest):

            r=n.__deepcopy__()

            r.duration.quarterLength=quantize_duration(
                float(r.duration.quarterLength)
            )

            notes.append(r)



    new_part=stream.Part()

    measure=stream.Measure(
        number=1
    )

    beat=0


    for n in notes:

        dur=float(n.duration.quarterLength)


        # 超過小節，自動切割
        while beat+dur > TARGET_BEATS:

            remain=TARGET_BEATS-beat


            if remain>0:

                pieces=split_note(
                    n,
                    remain
                )

                first=pieces[0]

                measure.append(first)


                dur-=remain

                beat=TARGET_BEATS


            new_part.append(measure)


            measure=stream.Measure(
                number=measure.number+1
            )

            beat=0


            if dur<=0:
                break


            n=n.__deepcopy__()
            n.duration.quarterLength=dur



        if dur>0:

            measure.append(n)

            beat+=dur



        if abs(beat-TARGET_BEATS)<0.001:

            new_part.append(measure)

            measure=stream.Measure(
                number=measure.number+1
            )

            beat=0



    # 最後補滿
    if beat>0:

        rest=note.Rest()

        rest.duration.quarterLength=TARGET_BEATS-beat

        measure.append(rest)

        new_part.append(measure)


    return new_part




def clean(inp,out):

    print("================")
    print("CLEAN MUSICXML V64")
    print("ABSOLUTE TIMELINE REBUILDER")
    print("================")


    score=converter.parse(inp)


    result=stream.Score()


    for p in score.parts:

        print("rebuild part")

        np=rebuild(p)

        result.insert(0,np)



    # 強制4/4

    for p in result.parts:

        p.insert(
            0,
            meter.TimeSignature("4/4")
        )

        p.insert(
            0,
            tempo.MetronomeMark(number=80)
        )



    print()
    print("FINAL CHECK")


    ok=True


    for i,m in enumerate(
        result.parts[0].getElementsByClass(stream.Measure),
        1
    ):

        length=sum(
            x.duration.quarterLength
            for x in m.notesAndRests
        )

        print(
            "Measure",
            i,
            float(length)
        )


        if abs(length-4)>0.01:
            ok=False



    if ok:
        print("ALL MEASURES SAFE")
    else:
        print("WARNING")


    print("FINAL WRITE")

    result.write(
        "musicxml",
        fp=out
    )


    print("DONE")
    print(out)



if __name__=="__main__":

    if len(sys.argv)<3:

        print(
            "usage: python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()


    clean(
        sys.argv[1],
        sys.argv[2]
    )