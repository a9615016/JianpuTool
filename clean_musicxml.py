import sys
import music21
from music21 import stream, note, chord, meter, duration


VERSION = "V18"


def clean(input_file, output_file):

    print("================")
    print(f"CLEAN MUSICXML {VERSION}")
    print("================")
    print("input:", input_file)


    score = music21.converter.parse(input_file)


    # --------------------------
    # remove voices
    # --------------------------
    print("remove voices")

    for part in score.parts:
        for v in part.voices:
            try:
                v.flatten()
            except:
                pass


    # --------------------------
    # remove chords
    # --------------------------
    print("remove chords")

    for part in score.parts:

        for c in list(part.recurse().getElementsByClass('Chord')):

            n = note.Note(
                c.pitches[0],
                quarterLength=c.duration.quarterLength
            )

            c.activeSite.replace(c, n)


    # --------------------------
    # quantize
    # --------------------------
    print("quantize")

    try:
        score.quantize(
            quarterLengthDivisors=[
                1,
                2,
                4
            ]
        )
    except Exception as e:
        print("quantize skip:", e)



    # --------------------------
    # force 4/4
    # --------------------------
    print("force 4/4")

    for part in score.parts:

        part.insert(
            0,
            meter.TimeSignature("4/4")
        )


    # --------------------------
    # fix measures
    # --------------------------
    print("fix measures")


    for part in score.parts:


        measures = part.makeMeasures()


        new_part = stream.Part()


        for m in measures:

            total = 0

            fixed = stream.Measure(
                number=m.number
            )


            for element in m.notesAndRests:

                ql = element.duration.quarterLength


                # 太長切掉
                if ql > 4:

                    print(
                        "trim long:",
                        ql
                    )

                    element.duration.quarterLength = 4


                # 修正怪長度
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


                q = element.duration.quarterLength


                closest = min(
                    allowed,
                    key=lambda x:abs(x-q)
                )


                element.duration.quarterLength = closest


                # 防止超過4拍
                if total + closest > 4:

                    remain = 4-total

                    if remain > 0:

                        r = note.Rest(
                            quarterLength=remain
                        )

                        fixed.append(r)

                    break


                fixed.append(element)

                total += closest



            # 不足補休止
            if total < 4:

                fixed.append(
                    note.Rest(
                        quarterLength=4-total
                    )
                )


            new_part.append(fixed)



        part.clear()

        for x in new_part:

            part.append(x)



    # --------------------------
    # remove empty measures
    # --------------------------

    print("remove empty measures")

    for part in score.parts:

        for m in list(
            part.getElementsByClass("Measure")
        ):

            if len(m.notesAndRests)==0:

                part.remove(m)



    # --------------------------
    # write
    # --------------------------

    print("write")

    score.write(
        "musicxml",
        fp=output_file
    )


    print()
    print("DONE", output_file)



if __name__ == "__main__":


    if len(sys.argv)<3:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit(1)


    clean(
        sys.argv[1],
        sys.argv[2]
    )