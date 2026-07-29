print("######## JIANPU PREPARE V3 ########")

import sys
from music21 import converter, note, stream


print("######## JIANPU PREPARE V3 ########")


def fix_measure(measure):

    target = 4.0

    total = 0.0
    new_elements = []

    for e in list(measure.notesAndRests):

        dur = float(e.duration.quarterLength)

        if total >= target:
            break

        remain = target - total


        # 完整放入
        if dur <= remain:

            new_elements.append(e)
            total += dur


        # 超過切割
        else:

            try:

                e2 = e

                e2.duration.quarterLength = remain

                new_elements.append(e2)

                total = target

            except:
                pass



    # 不足補休止符

    if total < target:

        r = note.Rest()

        r.duration.quarterLength = target-total

        new_elements.append(r)

        total = target



    # 清除舊內容

    for e in list(measure.notesAndRests):

        measure.remove(e)


    for e in new_elements:

        measure.append(e)



    return total



def process(input_xml, output_xml):


    print("READ:", input_xml)


    score = converter.parse(input_xml)



    print("REMOVE VOICES")

    for part in score.parts:

        for m in part.getElementsByClass("Measure"):

            # 移除 chord
            for c in list(m.notes):

                if c.isChord:

                    n = c.notes[0]

                    m.replace(c,n)



    print("######## FORCE 4/4 ########")


    for part in score.parts:


        measures = part.getElementsByClass("Measure")


        for m in measures:

            before = float(
                m.duration.quarterLength
            )


            after = fix_measure(m)


            print(
                "Measure",
                m.number,
                before,
                "=>",
                after
            )



    print("######## FINAL CHECK ########")


    for part in score.parts:

        for m in part.getElementsByClass("Measure"):


            d=float(
                m.duration.quarterLength
            )


            print(
                "CHECK",
                m.number,
                d
            )


            if abs(d-4.0)>0.01:

                print(
                    "WARNING",
                    m.number,
                    d
                )



    print("WRITE")

    score.write(
        "musicxml",
        fp=output_xml
    )


    print("DONE")




if __name__=="__main__":


    if len(sys.argv)<3:

        print(
            "usage: python jianpu_prepare_v3.py input.musicxml output.musicxml"
        )

        sys.exit(1)



    process(
        sys.argv[1],
        sys.argv[2]
    )