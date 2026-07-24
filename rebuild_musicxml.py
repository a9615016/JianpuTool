import sys
import music21


print("REBUILD VERSION 20260724 V4")


def fix_duration(obj):

    try:

        ql = obj.duration.quarterLength


        # jianpu_ly 支援的最大值
        allowed = [
            0.5,
            0.75,
            1,
            1.5,
            2,
            3,
            4,
            6,
            8,
            12
        ]


        # 超長音符拆開
        if ql > 12:

            obj.duration.quarterLength = 12


        # 不可表示的小數
        elif ql not in allowed:

            # 四捨五入到最近拍值
            nearest = min(
                allowed,
                key=lambda x:abs(x-ql)
            )

            obj.duration.quarterLength = nearest


    except Exception:

        pass



def rebuild(input_file, output_file):


    print("開始重建 MusicXML")


    score = music21.converter.parse(
        input_file
    )


    for part in score.parts:

        for element in part.recurse():

            if isinstance(
                element,
                (
                    music21.note.Note,
                    music21.note.Rest
                )
            ):

                fix_duration(element)



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