from music21 import converter, stream, note, meter
import sys
import copy

VERSION = "######## USING V84 PURE JIANPU XML SANITIZER ########"


# jianpu_ly 最安全節奏
SAFE_DURATIONS = [
    4.0,
    2.0,
    1.0,
    0.5,
    0.25,
    0.125
]


def quantize(d):

    x = float(d)

    return min(
        SAFE_DURATIONS,
        key=lambda v: abs(v-x)
    )


def get_notes(score):

    result=[]

    print("extract notes")

    for n in score.recurse().notesAndRests:

        obj = copy.deepcopy(n)


        # remove notation
        obj.expressions=[]
        obj.lyrics=[]


        # remove chord
        if obj.isChord:

            obj = note.Note(
                obj.pitches[0]
            )


        obj.duration.quarterLength = quantize(
            obj.duration.quarterLength
        )


        result.append(obj)


    return result



def rebuild(notes):

    print("PURE REBUILD")


    score = stream.Score()

    part = stream.Part()


    part.insert(
        0,
        meter.TimeSignature("4/4")
    )


    measure = stream.Measure(
        number=1
    )


    beat=0
    number=1



    for n in notes:


        dur=float(
            n.duration.quarterLength
        )


        while dur > 0:


            remain = 4-beat


            take=min(
                dur,
                remain
            )


            obj=copy.deepcopy(n)

            obj.duration.quarterLength=take


            measure.append(obj)


            beat += take

            dur -= take



            if abs(beat-4)<0.0001:


                part.append(measure)

                number+=1

                measure=stream.Measure(
                    number=number
                )

                beat=0



    if beat>0:


        r=note.Rest()

        r.duration.quarterLength=4-beat

        measure.append(r)


    part.append(measure)

    score.append(part)


    return score




def check(score):

    print("V84 FINAL CHECK")


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


        if abs(total-4)>0.001:

            raise Exception(
                "BAD MEASURE"
            )


    print("ALL MEASURES SAFE")





def clean(inp,out):


    print("================")
    print(VERSION)
    print("================")


    old=converter.parse(inp)


    print("remove voices")
    print("remove beams")
    print("remove ties")


    notes=get_notes(old)


    new=rebuild(notes)


    check(new)


    print("sanitize xml")


    new.write(
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