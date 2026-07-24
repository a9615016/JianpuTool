import sys
from music21 import converter, meter, stream


print("REBUILD VERSION 20260724 V5")


def rebuild(input_file, output_file):

    print("開始重建 MusicXML")


    score = converter.parse(
        input_file
    )


    for part in score.parts:


        # 移除原本怪拍號
        for ts in part.recurse().getElementsByClass(
            meter.TimeSignature
        ):
            ts.activeSite.remove(ts)


        # 加入4/4
        part.insert(
            0,
            meter.TimeSignature("4/4")
        )


        # 重新建立 measure
        measures = []


        current = stream.Measure(
            number=1
        )


        total = 0


        for n in part.flat.notesAndRests:


            ql = n.duration.quarterLength


            # 修正非法長度
            if ql <= 0:
                continue


            # 超過一拍拆掉
            while ql > 4:

                n.duration.quarterLength = 4
                ql = 4


            # 小節滿了換下一小節

            if total + ql > 4:


                measures.append(
                    current
                )


                current = stream.Measure(
                    number=len(measures)+1
                )


                total = 0



            current.append(
                n
            )


            total += ql



            if total == 4:


                measures.append(
                    current
                )


                current = stream.Measure(
                    number=len(measures)+1
                )


                total = 0



        if len(current.notesAndRests) > 0:

            measures.append(
                current
            )


        new_part = stream.Part()


        new_part.insert(
            0,
            meter.TimeSignature("4/4")
        )


        for m in measures:

            new_part.append(
                m
            )



        score.remove(
            part
        )


        score.insert(
            0,
            new_part
        )



    score.write(
        "musicxml",
        fp=output_file
    )


    print(
        "完成",
        output_file
    )



if __name__ == "__main__":


    rebuild(
        sys.argv[1],
        sys.argv[2]
    )