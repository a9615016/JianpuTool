# clean_musicxml.py
# CLEAN MUSICXML V30
# MIDI -> JIANPU FINAL CLEANER

import sys
import music21


def clean_musicxml(input_file, output_file):

    print("================")
    print("CLEAN MUSICXML V30 MIDI JIANPU FINAL")
    print("================")


    print("read")

    score = music21.converter.parse(input_file)


    # -------------------------
    # 基本清理
    # -------------------------

    print("remove voices")

    for part in score.parts:
        for m in part.getElementsByClass('Measure'):
            for n in m.notesAndRests:
                if hasattr(n, "voice"):
                    n.voice = None


    print("remove chords")

    for part in score.parts:
        for chord in list(part.recurse().getElementsByClass('Chord')):
            notes = chord.notes
            for n in notes:
                chord.activeSite.replace(chord, n)



    print("remove notation")

    for obj in score.recurse():

        if hasattr(obj, "beams"):
            obj.beams = music21.beam.Beams()

        if hasattr(obj, "tie"):
            obj.tie = None



    # -------------------------
    # 強制單聲部
    # -------------------------

    print("flatten")

    score = score.flatten()



    # -------------------------
    # 強制 4/4
    # -------------------------

    print("force 4/4")

    for part in score.parts:

        ts = music21.meter.TimeSignature("4/4")

        part.insert(0, ts)



    # -------------------------
    # duration量化
    # -------------------------

    print("quantize duration")

    for n in score.notesAndRests:

        q = float(n.duration.quarterLength)


        # 最小16分音符
        values = [
            0.25,
            0.5,
            0.75,
            1,
            1.5,
            2,
            3,
            4
        ]

        closest = min(
            values,
            key=lambda x:abs(x-q)
        )

        n.duration.quarterLength = closest



    # -------------------------
    # 建立新小節
    # -------------------------

    print("rebuild measures")


    new_score = music21.stream.Score()


    for part in score.parts:


        new_part = music21.stream.Part()

        current_measure = music21.stream.Measure(
            number=1
        )

        beat = 0
        measure_no = 1


        for n in part.notesAndRests:


            dur = float(n.duration.quarterLength)



            # 超過小節
            if beat + dur > 4:

                remain = 4 - beat


                if remain > 0:

                    copy = n.__deepcopy__({})
                    copy.duration.quarterLength = remain
                    current_measure.append(copy)


                print(
                    "split note at measure",
                    measure_no
                )


                new_part.append(
                    current_measure
                )


                measure_no += 1


                current_measure = music21.stream.Measure(
                    number=measure_no
                )

                beat = 0


                extra = dur - remain


                if extra > 0:

                    copy = n.__deepcopy__({})
                    copy.duration.quarterLength = extra

                    current_measure.append(copy)

                    beat += extra


            else:

                current_measure.append(n)

                beat += dur



            if abs(beat-4)<0.001:


                new_part.append(
                    current_measure
                )


                measure_no += 1

                current_measure = music21.stream.Measure(
                    number=measure_no
                )

                beat=0



        if len(current_measure.notesAndRests)>0:

            # 補休止
            rest = music21.note.Rest()

            rest.duration.quarterLength = 4-beat

            if rest.duration.quarterLength>0:

                current_measure.append(rest)


            new_part.append(current_measure)



        new_score.append(new_part)



    score = new_score



    # -------------------------
    # 最終檢查
    # -------------------------

    print("FINAL CHECK")


    for part in score.parts:

        for m in part.getElementsByClass("Measure"):


            total=sum(
                n.duration.quarterLength
                for n in m.notesAndRests
            )


            print(
                "Measure",
                m.number,
                total
            )


            if abs(total-4)>0.001:

                print(
                    "WARNING BAD MEASURE",
                    m.number,
                    total
                )


    print("FINAL WRITE")


    score.write(
        "musicxml",
        fp=output_file
    )


    print("DONE")
    print(output_file)



if __name__=="__main__":

    if len(sys.argv)<3:

        print(
            "usage: python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )