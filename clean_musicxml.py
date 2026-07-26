import sys
import music21


def clean_musicxml(input_file, output_file):

    print("CLEAN VERSION 20260726 MVP")

    print("input:", input_file)


    score = music21.converter.parse(input_file)


    # =========================
    # remove voices
    # =========================

    print("remove voices")


    for part in score.parts:

        for measure in part.getElementsByClass(
            music21.stream.Measure
        ):

            voices = list(
                measure.getElementsByClass(
                    music21.stream.Voice
                )
            )


            if voices:

                notes=[]

                for v in voices:
                    notes.extend(
                        list(v.notesAndRests)
                    )


                measure.removeByClass(
                    music21.stream.Voice
                )


                offset=0


                for n in notes:

                    n.offset=offset

                    measure.insert(
                        offset,
                        n
                    )

                    offset += n.quarterLength



    # =========================
    # remove chords
    # =========================

    print("remove chords")


    for c in list(
        score.recurse()
        .getElementsByClass(
            music21.chord.Chord
        )
    ):

        n=c.notes[0]

        n.duration=c.duration

        c.activeSite.replace(
            c,
            n
        )



    # =========================
    # remove grace
    # =========================

    print("remove grace")


    for n in list(
        score.recurse()
        .notes
    ):

        if n.duration.isGrace:

            n.activeSite.remove(n)



    # =========================
    # force duration
    # =========================

    print("fix duration")
    print("remove unsupported durations")


    for n in score.recurse().notesAndRests:

    if n.duration.type in [
        "128th",
        "256th"
    ]:

        print(
            "fix:",
            n.duration.type
        )

        n.duration.quarterLength = 0.125


    for n in score.recurse().notesAndRests:


        q=float(
            n.duration.quarterLength
        )


        if q <=0:

            q=0.25


        # 四分音符量化
        q=round(q*4)/4


        if q<=0:

            q=0.25


        n.duration.quarterLength=q



    # =========================
    # rebuild measures
    # =========================

    print("rebuild measures")


    for part in score.parts:

        part.makeMeasures(
            inPlace=True
        )



    # =========================
    # force 4/4 bars
    # =========================

    print("fix bars")


    for part in score.parts:


        for measure in part.getElementsByClass(
            music21.stream.Measure
        ):


            total=sum(
                e.duration.quarterLength
                for e in measure.notesAndRests
            )


            # 4/4 = 4拍

            if total > 4:


                print(
                    "trim measure",
                    measure.number,
                    total
                )


                remain=4


                for e in list(
                    measure.notesAndRests
                ):

                    if remain<=0:

                        measure.remove(e)

                        continue


                    if e.duration.quarterLength > remain:

                        e.duration.quarterLength=remain


                    remain -= e.duration.quarterLength



    # =========================
    # final
    # =========================

    print("write")


    score.write(
        "musicxml",
        fp=output_file
    )


    print(
        "done:",
        output_file
    )



if __name__=="__main__":


    input_file=sys.argv[1]


    if len(sys.argv)>=3:

        output_file=sys.argv[2]

    else:

        output_file=input_file.replace(
            ".musicxml",
            "_clean.musicxml"
        )


    clean_musicxml(
        input_file,
        output_file
    )