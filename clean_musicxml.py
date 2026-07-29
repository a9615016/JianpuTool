# clean_musicxml.py
# V80
# jianpu_ly minimal MusicXML generator


from music21 import converter, stream, note, meter, tempo, chord
import sys
from fractions import Fraction
import copy


VERSION = "CLEAN MUSICXML V80"


DIVISIONS = 16
BAR_LENGTH = 64


# =========================
# duration quantize
# =========================

def quantize_duration(q):

    values = [
        Fraction(64,16), # whole
        Fraction(32,16), # half
        Fraction(16,16), # quarter
        Fraction(8,16),  # eighth
        Fraction(4,16),  # 16th
    ]

    q = Fraction(q)

    return min(
        values,
        key=lambda x:abs(x-q)
    )



# =========================
# extract melody
# =========================

def extract_notes(score):

    result=[]


    part=score.parts[0]


    for n in part.recurse().notesAndRests:


        if isinstance(n,chord.Chord):

            # 只取最高音
            nn=n.notes[-1]

            item=copy.deepcopy(nn)

        else:

            item=copy.deepcopy(n)


        dur=quantize_duration(
            item.duration.quarterLength
        )


        item.duration.quarterLength=dur

        result.append(item)



    return result



# =========================
# rebuild score
# =========================

def rebuild(notes):


    score=stream.Score()

    part=stream.Part()


    part.append(
        meter.TimeSignature("4/4")
    )


    measure=stream.Measure(
        number=1
    )


    pos=0



    for n in notes:


        dur=int(
            Fraction(
                n.duration.quarterLength
            )
            *
            DIVISIONS
        )


        # 防止超小節

        if pos + dur > BAR_LENGTH:


            rest=note.Rest()

            rest.duration.quarterLength = (
                Fraction(
                    BAR_LENGTH-pos,
                    DIVISIONS
                )
            )

            measure.append(rest)


            part.append(measure)


            measure=stream.Measure(
                number=len(
                    part.getElementsByClass(
                        stream.Measure
                    )
                )+1
            )


            pos=0



        new=copy.deepcopy(n)


        new.duration.quarterLength = (
            Fraction(dur,DIVISIONS)
        )


        # remove notation

        new.tie=None

        if hasattr(new,"beams"):
            new.beams=[]


        measure.append(new)

        pos+=dur



        if pos==BAR_LENGTH:


            part.append(measure)


            measure=stream.Measure(
                number=len(
                    part.getElementsByClass(
                        stream.Measure
                    )
                )+1
            )


            pos=0



    # last measure

    if len(measure.notesAndRests):


        while pos < BAR_LENGTH:

            r=note.Rest()

            remain=min(
                16,
                BAR_LENGTH-pos
            )

            r.duration.quarterLength=(
                Fraction(
                    remain,
                    DIVISIONS
                )
            )

            measure.append(r)

            pos+=remain



        part.append(measure)



    score.append(part)


    return score



# =========================
# check
# =========================

def check(score):

    print("V80 FINAL CHECK")


    for i,m in enumerate(
        score.parts[0].getElementsByClass(
            stream.Measure
        ),
        1
    ):

        total=sum(
            n.duration.quarterLength
            for n in m.notesAndRests
        )


        print(
            "Measure",
            i,
            float(total)
        )



# =========================
# main
# =========================


def clean(inp,out):


    print(VERSION)


    src=converter.parse(inp)


    # remove tempo

    for t in src.recurse().getElementsByClass(
        tempo.MetronomeMark
    ):

        t.activeSite.remove(t)



    notes=extract_notes(src)


    new_score=rebuild(notes)


    check(new_score)



    print("WRITE")

    new_score.write(
        "musicxml",
        fp=out
    )


    print("DONE")
    print(out)



if __name__=="__main__":


    inp=sys.argv[1]


    if len(sys.argv)>2:

        out=sys.argv[2]

    else:

        out="clean.musicxml"



    clean(
        inp,
        out
    )