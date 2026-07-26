import sys
import music21


# ==========================
# 最小音符限制
# 1/16拍
# ==========================

def fix_length(value):

    value = float(value)

    # 四捨五入到 16 分音符
    value = round(value * 4) / 4

    if value <= 0:
        value = 0.25

    return value



def clean_musicxml(input_file, output_file):

    print("CLEAN VERSION 20260726 V4")
    print("input:", input_file)


    score = music21.converter.parse(input_file)



    # ==========================
    # Remove Voices
    # ==========================

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

                elements=[]


                for v in voices:

                    for e in v.notesAndRests:
                        elements.append(e)


                measure.removeByClass(
                    music21.stream.Voice
                )


                offset=0


                for e in elements:

                    e.offset=offset

                    measure.insert(
                        offset,
                        e
                    )

                    offset += e.quarterLength



    # ==========================
    # Remove Chords
    # ==========================

    print("remove chords")


    for chord in list(
        score.recurse()
        .getElementsByClass(
            music21.chord.Chord
        )
    ):

        n = chord.notes[-1]

        n.duration = chord.duration

        chord.activeSite.replace(
            chord,
            n
        )



    # ==========================
    # Remove Grace
    # ==========================

    print("remove grace")


    for n in list(
        score.recurse().notes
    ):

        if n.duration.isGrace:

            n.activeSite.remove(n)



    # ==========================
    # Fix Duration
    # ==========================

    print("fix duration")


    for n in score.recurse().notesAndRests:

        n.duration.quarterLength = fix_length(
            n.duration.quarterLength
        )



    # ==========================
    # Remove Tuplets
    # ==========================

    print("remove tuplets")


    for n in score.recurse().notesAndRests:


        if n.duration.tuplets:


            length = fix_length(
                n.duration.quarterLength
            )


            n.duration.clear()

            n.duration.quarterLength = length



    # ==========================
    # Rebuild measures
    # ==========================

    print("rebuild measures")


    score.makeMeasures(
        inPlace=True
    )



    # ==========================
    # Fix measure duration
    # ==========================

    print("fix bars")


    for part in score.parts:


        for measure in part.getElementsByClass(
            music21.stream.Measure
        ):


            expected = measure.barDuration.quarterLength


            total = sum(
                e.duration.quarterLength
                for e in measure.notesAndRests
            )


            diff = expected-total



            # 不足補休止符

            if diff > 0.01:


                r = music21.note.Rest()

                r.duration.quarterLength = fix_length(diff)

                measure.append(r)



            # 超過刪最後音符長度

            elif diff < -0.01:


                print(
                    "short measure",
                    measure.number,
                    total,
                    expected
                )


                for e in reversed(
                    list(measure.notesAndRests)
                ):

                    new_len = (
                        e.duration.quarterLength
                        +
                        diff
                    )


                    new_len = fix_length(
                        new_len
                    )


                    if new_len > 0:

                        e.duration.quarterLength = new_len

                        break



    # ==========================
    # Final check
    # ==========================

    print("final cleanup")


    for n in score.recurse().notesAndRests:

        n.duration.quarterLength = fix_length(
            n.duration.quarterLength
        )


    # 清除不可表達 duration

    for n in score.recurse().notesAndRests:

        if n.duration.type == "inexpressible":

            n.duration.quarterLength = 0.25



    # ==========================
    # Write
    # ==========================

    print("write")


    score.write(
        "musicxml",
        fp=output_file
    )


    print(
        "done:",
        output_file
    )



if __name__ == "__main__":


    if len(sys.argv)<2:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit(1)



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