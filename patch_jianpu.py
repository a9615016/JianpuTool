from music21 import converter, stream, note, chord, meter
import sys
import os


STEP = 0.25   # 四分音符=1，16分格=0.25


def quantize_duration(q):
    """
    量化音長
    """
    return round(q / STEP) * STEP


def patch_score(src, dst):

    print("================")
    print("PATCH JIANPU V1")
    print("================")

    print("read")
    score = converter.parse(src)


    print("remove bad notation")

    for part in score.parts:

        # 強制 4/4
        part.insert(0, meter.TimeSignature("4/4"))


        new_part = stream.Part()

        current_measure = 1
        current_pos = 0


        print("rebuild notes")


        for el in part.flatten().notesAndRests:

            if isinstance(el, chord.Chord):

                # chord 取最高音
                n = note.Note(
                    el.pitches[-1]
                )
                n.duration.quarterLength = (
                    el.duration.quarterLength
                )

            else:
                n = el


            dur = n.duration.quarterLength


            # 避免奇怪長度
            if dur <= 0:
                continue


            dur = quantize_duration(dur)

            if dur <= 0:
                dur = STEP


            # 避免超過小節
            if current_pos + dur > 4:

                rest = 4 - current_pos

                if rest > 0:
                    r = note.Rest()
                    r.duration.quarterLength = rest
                    new_part.append(r)

                current_measure += 1
                current_pos = 0


            n.duration.quarterLength = dur

            new_part.append(n)

            current_pos += dur


            if current_pos >= 4:

                current_pos = 0
                current_measure += 1



        score.parts.remove(part)
        score.insert(0,new_part)



    print("remove ties")

    for n in score.recurse().notes:
        n.tie = None


    print("write")

    score.write(
        "musicxml",
        fp=dst
    )


    print("DONE")
    print(dst)



if __name__ == "__main__":

    if len(sys.argv) < 3:
        print(
            "python patch_jianpu.py input.musicxml output.musicxml"
        )
        sys.exit(1)


    patch_score(
        sys.argv[1],
        sys.argv[2]
    )