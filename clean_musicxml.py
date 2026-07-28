from music21 import converter, stream, meter, note, chord, tie
import sys


VERSION = "CLEAN MUSICXML V26 FINAL JIANPU SAFE"


def clean_musicxml(src, dst):

    print("================")
    print(VERSION)
    print("================")


    print("read")

    score = converter.parse(src)


    print("remove voices")

    for p in score.parts:
        for n in p.recurse():
            if hasattr(n, "voice"):
                n.voice = None


    print("remove chords")


    new_score = stream.Score()


    for part in score.parts:

        new_part = stream.Part()

        new_part.append(
            meter.TimeSignature("4/4")
        )


        for n in part.recurse().notesAndRests:


            # chord 取最高音
            if isinstance(n, chord.Chord):

                nn = note.Note(
                    n.highestPitch
                )

                nn.duration.quarterLength = (
                    n.duration.quarterLength
                )

                new_part.append(nn)
                continue



            if isinstance(n, note.Note):

                nn = note.Note(n.pitch)

                q = round(
                    float(n.duration.quarterLength) * 4
                ) / 4


                if q <= 0:
                    continue


                nn.duration.quarterLength = q


                # remove tie
                nn.tie = None


                new_part.append(nn)



            elif isinstance(n, note.Rest):

                r = note.Rest()

                q = round(
                    float(n.duration.quarterLength)*4
                )/4


                if q > 0:

                    r.duration.quarterLength=q

                    new_part.append(r)



        new_score.append(new_part)



    score = new_score



    print("force 4/4")

    for p in score.parts:

        p.insert(
            0,
            meter.TimeSignature("4/4")
        )



    print("duration quantize")


    for n in score.recurse().notesAndRests:

        q = round(
            float(n.duration.quarterLength)*4
        )/4

        if q <=0:
            q=0.25

        n.duration.quarterLength=q



    print("rebuild measures")

    score.makeMeasures(
        inPlace=True
    )



    print("split cross measure notes")


    # 重新檢查 offset overflow

    fixed = stream.Score()


    for part in score.parts:


        np = stream.Part()

        np.append(
            meter.TimeSignature("4/4")
        )


        current = 0


        for n in part.recurse().notesAndRests:


            length = float(
                n.duration.quarterLength
            )


            # 每小節最多4拍

            remain = 4 - (current % 4)


            if length > remain:


                first = n.duration.quarterLength

                first = remain


                if isinstance(n,note.Note):

                    a = note.Note(n.pitch)
                    a.duration.quarterLength=first

                    np.append(a)


                else:

                    r=note.Rest()
                    r.duration.quarterLength=first
                    np.append(r)



                current += first


                second = length-first


                if second>0:


                    if isinstance(n,note.Note):

                        b=note.Note(n.pitch)
                        b.duration.quarterLength=second

                        np.append(b)

                    else:

                        r=note.Rest()
                        r.duration.quarterLength=second

                        np.append(r)


                    current += second



            else:

                np.append(n)

                current += length



        fixed.append(np)



    score=fixed



    print("fill measure rest")


    score.makeMeasures(
        inPlace=True
    )



    print("clear notation cache")


    score.makeNotation(
        inPlace=True
    )



    print("FINAL CHECK")


    for i,m in enumerate(
        score.recurse().getElementsByClass("Measure"),
        1
    ):

        dur=float(
            m.duration.quarterLength
        )

        print(
            "Measure",
            i,
            dur
        )


        if dur > 4.01:

            raise Exception(
                "OFFSET OVERFLOW measure "
                +str(i)
            )


    print("NO OFFSET OVERFLOW")
    print("JIANPU SAFE")



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

        exit()


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )