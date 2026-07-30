from music21 import stream, note, chord, meter, duration, expressions


# ==========================
# V25 Split Measure Overflow
# ==========================

def split_measure_overflow(score):

    print("split measure overflow V25")


    new_score = stream.Score()


    for part in score.parts:

        new_part = stream.Part()

        current_measure = stream.Measure(
            number=1
        )

        current_beats = 0.0


        for element in part.flatten().notesAndRests:


            dur = element.duration.quarterLength


            # 超長音符切割
            while current_beats + dur > 4.0:


                remain = 4.0 - current_beats


                if remain > 0:

                    if element.isNote:

                        n = note.Note(
                            element.pitch
                        )

                        n.duration = duration.Duration(
                            remain
                        )

                        current_measure.append(n)


                    elif element.isRest:

                        r = note.Rest()

                        r.duration = duration.Duration(
                            remain
                        )

                        current_measure.append(r)



                new_part.append(
                    current_measure
                )


                current_measure = stream.Measure(
                    number=current_measure.number + 1
                )


                dur -= remain
                current_beats = 0



            # 剩餘部分加入

            if element.isNote:

                n = note.Note(
                    element.pitch
                )

                n.duration = duration.Duration(
                    dur
                )

                current_measure.append(n)



            elif element.isRest:

                r = note.Rest()

                r.duration = duration.Duration(
                    dur
                )

                current_measure.append(r)



            current_beats += dur



            # 剛好滿小節

            if abs(current_beats - 4.0) < 0.001:

                new_part.append(
                    current_measure
                )

                current_measure = stream.Measure(
                    number=current_measure.number + 1
                )

                current_beats = 0



        # 最後不足補休止符

        if current_beats > 0:

            r = note.Rest()

            r.duration = duration.Duration(
                4.0-current_beats
            )

            current_measure.append(r)


            new_part.append(
                current_measure
            )


        new_score.append(
            new_part
        )


    return new_score