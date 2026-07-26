import sys
import music21
from music21 import note, chord, meter, stream


print("CLEAN VERSION 20260726 V8 QUANTIZE")


def quantize_duration(n):

    # 最小單位：16分音符
    step = 0.25

    q = round(
        n.duration.quarterLength / step
    ) * step


    if q < 0.25:
        q = 0.25


    n.duration.quarterLength = q



def clean_musicxml(input_file, output_file):

    print("input:", input_file)


    score = music21.converter.parse(input_file)



    print("remove voices")

    for n in score.recurse():

        if hasattr(n, "voice"):
            try:
                n.voice = None
            except:
                pass



    print("remove chords")

    for c in list(
        score.recurse()
        .getElementsByClass(chord.Chord)
    ):

        if len(c.pitches):

            new = note.Note(
                c.pitches[0]
            )

            new.duration = c.duration

            c.activeSite.replace(
                c,
                new
            )



    print("remove grace")

    for n in score.recurse().notes:

        if n.duration.isGrace:

            n.duration = music21.duration.Duration(
                0.25
            )



    print("QUANTIZE 1/16")

    for n in score.recurse().notes:

        quantize_duration(n)



    print("remove tuplets")

    for n in score.recurse().notes:

        if n.duration.tuplets:

            n.duration.tuplets = []



    print("remove ultra short notes")

    for n in list(score.recurse().notes):

        if n.duration.quarterLength < 0.25:

            n.duration.quarterLength = 0.25



    print("rebuild measures")


    for part in score.parts:

        part.makeMeasures(
            inPlace=True
        )



    print("force 4/4")


    for part in score.parts:

        ts = (
            part.recurse()
            .getElementsByClass(
                meter.TimeSignature
            )
        )


        if len(ts)==0:

            part.insert(
                0,
                meter.TimeSignature("4/4")
            )



    print("measure normalize")


    for part in score.parts:


        for m in part.getElementsByClass(
            stream.Measure
        ):


            total = m.duration.quarterLength


            # 太長
            if total > 4:


                diff = total - 4


                for n in reversed(
                    list(m.notes)
                ):

                    if diff <= 0:
                        break


                    remove = min(
                        diff,
                        n.duration.quarterLength-0.25
                    )


                    if remove > 0:

                        n.duration.quarterLength -= remove

                        diff -= remove



            # 太短補休止

            total = m.duration.quarterLength


            if total < 4:

                r = note.Rest()

                r.duration.quarterLength = (
                    4-total
                )

                m.append(r)



    print("FINAL QUANTIZE")


    for n in score.recurse().notes:

        quantize_duration(n)



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

        sys.exit()



    inp = sys.argv[1]


    if len(sys.argv)>=3:

        out = sys.argv[2]

    else:

        out = inp.replace(
            ".musicxml",
            "_clean.musicxml"
        )


    clean_musicxml(
        inp,
        out
    )