print("######## CLEAN MUSICXML V82 LOADED ########")
from music21 import converter, stream, note, chord, meter
import sys
import os


VERSION = "CLEAN MUSICXML V82 JIANPU_LY COMPATIBLE"


def split_long_note(n):
    """
    jianpu_ly 不喜歡跨小節長音
    強制拆成 <=1拍
    """

    ql = n.duration.quarterLength

    result = []

    while ql > 1:

        x = note.Note(
            n.pitch
        )

        x.duration.quarterLength = 1

        result.append(x)

        ql -= 1


    if ql > 0:

        x = note.Note(
            n.pitch
        )

        x.duration.quarterLength = ql

        result.append(x)


    return result



def clean(input_file, output_file):

    print("================")
    print(VERSION)
    print("================")


    score = converter.parse(
        input_file
    )


    print("remove voices")

    for p in score.parts:

        for n in list(p.recurse()):

            if isinstance(n, chord.Chord):

                n.notes[0].duration = n.duration

                n.activeSite.replace(
                    n,
                    n.notes[0]
                )


    print("remove ties")

    for n in score.recurse().notes:

        n.tie = None



    print("remove beams")


    print("force 4/4")

    for p in score.parts:

        p.insert(
            0,
            meter.TimeSignature("4/4")
        )



    new_score = stream.Score()



    for part in score.parts:


        new_part = stream.Part()

        new_part.id = part.id


        current_measure = stream.Measure(
            number=1
        )

        beat = 0



        for n in part.recurse().notesAndRests:


            if isinstance(n, note.Rest):

                pieces=[n]

            else:

                pieces=split_long_note(n)



            for x in pieces:


                dur=x.duration.quarterLength



                if beat + dur > 4:


                    remain = 4-beat


                    if remain > 0:

                        r = note.Rest()

                        r.duration.quarterLength=remain

                        current_measure.append(r)



                    new_part.append(
                        current_measure
                    )


                    print(
                        "Measure",
                        current_measure.number,
                        current_measure.duration.quarterLength
                    )


                    current_measure=stream.Measure(
                        number=current_measure.number+1
                    )


                    beat=0



                current_measure.append(x)

                beat += dur



                if beat >=4:


                    new_part.append(
                        current_measure
                    )


                    print(
                        "Measure",
                        current_measure.number,
                        current_measure.duration.quarterLength
                    )


                    current_measure=stream.Measure(
                        number=current_measure.number+1
                    )

                    beat=0



        if beat>0:


            r=note.Rest()

            r.duration.quarterLength=4-beat

            current_measure.append(r)


            new_part.append(
                current_measure
            )


        new_score.append(
            new_part
        )



    print("FINAL CHECK")


    for m in new_score.parts[0].getElementsByClass("Measure"):

        print(
            "Measure",
            m.number,
            m.duration.quarterLength
        )



    new_score.write(
        "musicxml",
        fp=output_file
    )


    print("DONE")
    print(output_file)



if __name__=="__main__":


    if len(sys.argv)<3:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        exit()


    clean(
        sys.argv[1],
        sys.argv[2]
    )