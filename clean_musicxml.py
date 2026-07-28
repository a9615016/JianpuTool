from music21 import converter, stream, note, meter, tie
import sys
import copy


VERSION = "######## CLEAN MUSICXML V86 TIE SPLITTER FINAL ########"


QUANTIZE_VALUES = [
    4.0,
    2.0,
    1.0,
    0.5,
    0.25,
    0.125
]


def quantize_duration(d):

    x = float(d)

    return min(
        QUANTIZE_VALUES,
        key=lambda v: abs(v-x)
    )



def clean_note(n):

    item = copy.deepcopy(n)


    # remove notation
    item.expressions = []

    item.lyrics = []


    if hasattr(item,"beams"):
        item.beams = []


    # quantize
    item.duration.quarterLength = quantize_duration(
        item.duration.quarterLength
    )


    return item




def extract_notes(score):

    result=[]


    for n in score.recurse().notesAndRests:

        result.append(
            clean_note(n)
        )


    return result




def split_note(note_obj, remain, rest):

    left = copy.deepcopy(note_obj)

    right = copy.deepcopy(note_obj)


    left.duration.quarterLength = remain

    right.duration.quarterLength = rest


    # tie only notes
    if isinstance(left,note.Note):

        left.tie = tie.Tie("start")
        right.tie = tie.Tie("stop")


    return left,right




def rebuild_measure(notes):


    print("rebuild measures + tie split")


    score = stream.Score()

    part = stream.Part()


    part.insert(
        0,
        meter.TimeSignature("4/4")
    )


    measure_no=1

    m = stream.Measure(
        number=measure_no
    )


    beat=0.0



    for n in notes:


        dur=float(
            n.duration.quarterLength
        )


        while beat + dur > 4.0:


            remain = 4.0 - beat


            if remain > 0:


                left,right = split_note(
                    n,
                    remain,
                    dur-remain
                )


                m.append(left)

            else:

                right=copy.deepcopy(n)


            part.append(m)


            measure_no += 1


            m = stream.Measure(
                number=measure_no
            )


            beat=0.0


            n = right


            dur=float(
                n.duration.quarterLength
            )


        if dur > 0:


            m.append(n)

            beat += dur



    # fill last measure

    if beat < 4:


        r = note.Rest()

        r.duration.quarterLength = 4-beat

        m.append(r)



    part.append(m)


    score.append(part)


    return score





def final_check(score):


    print("FINAL CHECK")


    for m in score.parts[0].getElementsByClass(
        "Measure"
    ):


        total=sum(
            float(x.duration.quarterLength)
            for x in m.notesAndRests
        )


        print(
            "Measure",
            m.number,
            total
        )


        if abs(total-4.0)>0.001:

            print(
                "WARNING",
                m.number,
                total
            )


    print(
        "ALL MEASURES SAFE"
    )





def clean(inp,out):


    print("================")
    print(VERSION)
    print("================")


    print("read")

    old=converter.parse(inp)



    print("remove voices")

    print("remove chords")

    print("remove beams")

    print("remove ties")


    notes=extract_notes(old)


    new_score=rebuild_measure(
        notes
    )


    final_check(
        new_score
    )


    print("FINAL WRITE")


    new_score.write(
        "musicxml",
        fp=out
    )


    print("DONE")
    print(out)





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