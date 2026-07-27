import sys
import music21
from music21 import note, stream


VERSION = "CLEAN MUSICXML V24.4 FINAL JIANPU TICK ALIGN"


def remove_bad_elements(score):

    print("remove voices")

    for part in score.parts:

        for el in list(part.recurse()):
            if isinstance(el, stream.Voice):
                try:
                    el.remove(el.notes)
                except:
                    pass


    print("remove chords")

    for part in score.parts:
        for c in list(part.recurse().getElementsByClass("Chord")):
            n = note.Note(
                c.pitches[-1],
                quarterLength=c.duration.quarterLength
            )
            c.activeSite.replace(c, n)



    print("remove beams")

    for n in score.recurse().notes:
        try:
            n.beams = music21.beam.Beams()
        except:
            pass



    print("remove ties")

    for n in score.recurse().notes:
        try:
            n.tie = None
        except:
            pass



def force_time(score):

    print("force 4/4")

    for part in score.parts:

        for m in part.getElementsByClass("Measure"):

            m.timeSignature = music21.meter.TimeSignature("4/4")



def quantize_duration(score):

    print("duration quantize")

    values = [
        0.25,
        0.5,
        1,
        2,
        4
    ]

    for n in score.recurse().notesAndRests:

        q = n.duration.quarterLength

        nearest = min(
            values,
            key=lambda x: abs(x-q)
        )

        n.duration.quarterLength = nearest



def rebuild_measure(score):

    print("rebuild measures")

    for part in score.parts:

        part.makeMeasures(
            inPlace=True
        )



def split_cross_measure_notes(score):

    print("split cross measure notes")

    for part in score.parts:

        for m in part.getElementsByClass("Measure"):

            if m.duration.quarterLength > 4:

                excess = (
                    m.duration.quarterLength - 4
                )

                for n in reversed(
                    list(m.notesAndRests)
                ):

                    if excess <= 0:
                        break

                    if n.duration.quarterLength <= excess:

                        excess -= n.duration.quarterLength
                        n.duration.quarterLength = 0

                    else:

                        n.duration.quarterLength -= excess
                        excess = 0



def fill_empty_measure(score):

    print("fill measure rest")

    for part in score.parts:

        for m in part.getElementsByClass("Measure"):

            length = m.duration.quarterLength

            if length < 4:

                r = note.Rest(
                    quarterLength=4-length
                )

                m.append(r)



def jianpu_tick_align(score):

    print("jianpu_ly final tick align")


    for part in score.parts:


        for m in part.getElementsByClass("Measure"):


            total = m.duration.quarterLength


            target = 4.0


            # 超過小節
            if total > target:


                overflow = total-target


                notes = list(
                    m.notesAndRests
                )


                for n in reversed(notes):


                    if overflow <= 0:
                        break


                    length = n.duration.quarterLength


                    if length <= overflow:

                        n.duration.quarterLength = 0

                        overflow -= length


                    else:

                        n.duration.quarterLength = (
                            length-overflow
                        )

                        overflow = 0



            # 不足補 Rest

            elif total < target:


                r = note.Rest(
                    quarterLength=target-total
                )

                m.append(r)



def final_check(score):

    print("FINAL CHECK")


    ok=True


    for i,m in enumerate(
        score.parts[0].getElementsByClass("Measure"),
        1
    ):


        length=m.duration.quarterLength


        print(
            "Measure",
            i,
            length
        )


        if abs(length-4)>0.001:

            ok=False



    if ok:

        print("ALL MEASURES SAFE")

    else:

        print("WARNING MEASURE ERROR")



def clean_musicxml(input_file, output_file):

    print("================")
    print(VERSION)
    print("================")


    print("read")


    score = music21.converter.parse(
        input_file
    )


    remove_bad_elements(score)


    force_time(score)


    quantize_duration(score)


    rebuild_measure(score)


    split_cross_measure_notes(score)


    rebuild_measure(score)


    fill_empty_measure(score)


    rebuild_measure(score)


    jianpu_tick_align(score)


    print("clear notation cache")


    score.stripTies()


    final_check(score)


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
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit(1)



    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )