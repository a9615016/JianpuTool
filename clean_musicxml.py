from music21 import converter, stream, meter, note, chord, bar
import sys
import copy


DIVISION = 16
BAR_TICKS = 64   # 4/4


def quantize_duration(q):
    """
    quarterLength -> 1/16 quantize
    """
    ticks = round(float(q) * DIVISION)

    if ticks < 1:
        ticks = 1

    return ticks / DIVISION


def remove_notation(score):

    print("remove voices")
    for el in score.recurse():
        if hasattr(el, "voice"):
            try:
                el.voice = None
            except:
                pass


    print("remove chords")

    for n in list(score.recurse().getElementsByClass(chord.Chord)):
        new_notes = []

        for p in n.pitches:
            nn = note.Note(p)
            nn.duration = copy.deepcopy(n.duration)
            new_notes.append(nn)

        n.activeSite.replace(n, new_notes[0])



    print("remove beams")

    for n in score.recurse().notes:

        try:
            n.beams = None
        except:
            pass


    print("remove ties")

    for n in score.recurse().notes:

        try:
            n.tie = None
        except:
            pass



def force_4_4(score):

    print("force 4/4")

    for p in score.parts:

        p.insert(
            0,
            meter.TimeSignature("4/4")
        )



def quantize_notes(score):

    print("duration quantize")

    for n in score.recurse().notes:

        n.duration.quarterLength = (
            quantize_duration(
                n.duration.quarterLength
            )
        )



def rebuild_measures(score):

    print("rebuild measures")

    result = stream.Score()

    for part in score.parts:

        new_part = stream.Part()

        current = 0
        measure_no = 1

        m = stream.Measure(
            number=measure_no
        )

        for n in part.recurse().notes:

            length = int(
                round(
                    n.duration.quarterLength
                    *
                    DIVISION
                )
            )


            # split over measure

            while current + length > BAR_TICKS:

                remain = BAR_TICKS-current

                if remain > 0:

                    nn = copy.deepcopy(n)

                    nn.duration.quarterLength = (
                        remain / DIVISION
                    )

                    m.append(nn)


                m.duration.quarterLength = 4

                new_part.append(m)


                length -= remain

                measure_no += 1

                m = stream.Measure(
                    number=measure_no
                )

                current = 0



            nn = copy.deepcopy(n)

            nn.duration.quarterLength = (
                length / DIVISION
            )

            m.append(nn)

            current += length



        if current < BAR_TICKS:

            r = note.Rest()

            r.duration.quarterLength = (
                (BAR_TICKS-current)
                /
                DIVISION
            )

            m.append(r)



        m.duration.quarterLength = 4

        new_part.append(m)


        result.insert(0,new_part)


    return result



def final_check(score):

    print("FINAL CHECK")

    for i,m in enumerate(
        score.parts[0].getElementsByClass(stream.Measure),
        1
    ):

        dur = float(
            m.duration.quarterLength
        )

        print(
            "Measure",
            i,
            dur
        )

        if abs(dur-4.0)>0.01:

            raise Exception(
                f"Measure {i} invalid {dur}"
            )


    print("ALL MEASURES SAFE")



def main():

    if len(sys.argv)<2:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        return


    inp=sys.argv[1]

    out=sys.argv[2] if len(sys.argv)>2 else "clean.musicxml"



    print("================")
    print(
        "CLEAN MUSICXML V25 JIANPU FINAL"
    )
    print("================")


    print("read")

    score=converter.parse(inp)


    remove_notation(score)

    force_4_4(score)

    quantize_notes(score)


    score=rebuild_measures(score)


    score=rebuild_measures(score)


    print(
        "clear notation cache"
    )


    final_check(score)


    print(
        "FINAL WRITE"
    )


    score.write(
        "musicxml",
        fp=out
    )


    print("DONE")
    print(out)



if __name__=="__main__":
    main()