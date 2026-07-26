import sys
import os
import music21


def clean_musicxml(input_file, output_file):

    print("CLEAN MUSICXML V2")
    print("input:")
    print(input_file)

    print("output:")
    print(output_file)

    if not os.path.exists(input_file):
        print("ERROR: input not found")
        return False


    print("讀取 MusicXML")

    score = music21.converter.parse(input_file)


    print("開始清理")


    # 移除不必要元素
    for part in score.parts:

        # 移除 chord
        for chord in part.recurse().getElementsByClass(
            'Chord'
        ):
            chord.remove()

        # 移除 grace note
        for grace in part.recurse().getElementsByClass(
            'GraceNote'
        ):
            grace.remove()



        # 修正所有 note
        for n in part.recurse().notes:

            # 移除 tie
            if hasattr(n, "tie"):
                n.tie = None


        # 修正休止符
        for r in part.recurse().getElementsByClass(
            'Rest'
        ):
            if r.duration.quarterLength <= 0:
                r.duration.quarterLength = 1



    print("重新整理小節")


    # 強制 4/4
    for part in score.parts:

        measures = part.makeMeasures()

        for m in measures:

            # 確保 measure duration
            total = m.duration.quarterLength

            if total != 4:

                diff = 4 - total

                if diff > 0:

                    rest = music21.note.Rest()
                    rest.duration.quarterLength = diff
                    m.append(rest)


    print("移除複雜節奏")


    # quantize
    score.quantize(
        quarterLengthDivisors=[
            4,
            3,
            2,
            1
        ]
    )


    print("寫入檔案")

    score.write(
        "musicxml",
        fp=output_file
    )


    print("完成:")
    print(output_file)

    print(
        "SIZE:",
        os.path.getsize(output_file)
    )

    return True



if __name__ == "__main__":


    if len(sys.argv) < 3:

        print(
            "使用方法:"
        )

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit(1)



    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )