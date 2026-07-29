# ================================
# CLEAN MUSICXML V83
# JIANPU STRICT MODE
# ================================

print("================")
print("CLEAN MUSICXML V83 JIANPU STRICT")
print("================")


from music21 import converter, stream, note, chord


def strict_fix_measures(score):

    print("JIANPU STRICT FIX")

    for part in score.parts:

        measures = list(
            part.getElementsByClass("Measure")
        )

        for m in measures:

            length = float(
                m.duration.quarterLength
            )

            if length > 4.0:

                print(
                    "TRIM measure",
                    m.number,
                    length
                )

                used = 0.0
                keep = []


                for element in list(
                    m.notesAndRests
                ):

                    dur = float(
                        element.duration.quarterLength
                    )


                    if used >= 4.0:
                        break


                    remain = 4.0 - used


                    if dur <= remain:

                        keep.append(element)
                        used += dur


                    else:

                        # cut note/rest
                        element.duration.quarterLength = remain
                        keep.append(element)
                        used = 4.0



                # remove old content

                for el in list(
                    m.notesAndRests
                ):
                    m.remove(el)


                offset = 0

                for el in keep:

                    m.insert(
                        offset,
                        el
                    )

                    offset += float(
                        el.duration.quarterLength
                    )


            elif length < 4.0:

                print(
                    "FILL rest",
                    m.number,
                    length
                )

                rest_time = 4.0 - length

                m.append(
                    note.Rest(
                        quarterLength=rest_time
                    )
                )


    return score



# ================================
# APPLY STRICT FIX
# ================================

score = strict_fix_measures(score)



# ================================
# FINAL CHECK
# ================================

print("FINAL V83 CHECK")


for m in score.parts[0].getElementsByClass("Measure"):

    q = float(
        m.duration.quarterLength
    )

    print(
        "Measure",
        m.number,
        q
    )


# ================================
# WRITE
# ================================

print("FINAL WRITE")
score.write(
    "musicxml",
    fp=output_file
)

print("DONE")
print(output_file)