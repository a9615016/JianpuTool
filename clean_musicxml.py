import sys
import music21
from music21 import stream, meter, note, chord, tie


VERSION = "CLEAN MUSICXML V23.7 FINAL MEASURE SPLIT SAFE"


def remove_bad_elements(score):

    print("remove voices")

    for part in score.parts:
        for el in list(part.recurse()):
            if hasattr(el, "voices"):
                try:
                    el.voices = []
                except:
                    pass


    print("remove chords")

    for part in score.parts:
        for c in list(part.recurse().getElementsByClass("Chord")):
            try:
                n = note.Note(c.pitches[0])
                n.duration = c.duration
                c.activeSite.replace(c, n)
            except:
                pass


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



def force_time_signature(score):

    print("force 4/4")

    for part in score.parts:

        # 清除舊拍號
        for ts in list(
            part.recurse()
            .getElementsByClass("TimeSignature")
        ):
            ts.activeSite.remove(ts)


        part.insert(
            0,
            meter.TimeSignature("4/4")
        )



def split_long_measures(score):

    print("measure split")

    for part in score.parts:

        measures = list(
            part.getElementsByClass("Measure")
        )

        new_measures = []

        for m in measures:

            q = m.duration.quarterLength

            print(
                "Measure",
                m.number,
                q
            )


            # 正常小節
            if q <= 4:
                new_measures.append(m)
                continue


            print(
                "SPLIT LONG MEASURE:",
                q
            )


            current = stream.Measure()
            current.number = m.number


            length = 0


            for el in m.notesAndRests:

                dur = el.duration.quarterLength


                # 超過4拍切斷
                if length + dur > 4:

                    remain = 4 - length

                    if remain > 0:

                        e1 = el.clone()
                        e1.duration.quarterLength = remain
                        current.append(e1)


                    new_measures.append(current)


                    current = stream.Measure()
                    current.number = m.number

                    length = 0


                current.append(el)

                length += dur


            if len(current.notesAndRests) > 0:
                new_measures.append(current)


        # 重建 part

        part.remove(
            part.getElementsByClass("Measure")
        )

        for m in new_measures:
            part.append(m)



def final_check(score):

    print("check measures")

    for m in score.recurse().getElementsByClass("Measure"):

        q = m.duration.quarterLength

        print(
            "Measure",
            m.number,
            q
        )

        if q > 4:
            print(
                "WARNING LONG MEASURE",
                q
            )



def clean_musicxml(input_file, output_file):

    print("================")
    print(VERSION)
    print("================")


    print("read")

    score = music21.converter.parse(
        input_file
    )


    remove_bad_elements(score)

    force_time_signature(score)

    split_long_measures(score)

    final_check(score)


    print("FINAL WRITE")


    score.write(
        "musicxml",
        fp=output_file
    )


    print()
    print("DONE")
    print(output_file)



if __name__ == "__main__":

    if len(sys.argv) < 3:

        print(
            "usage: python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )