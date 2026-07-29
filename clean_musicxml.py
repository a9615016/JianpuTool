# clean_musicxml.py
# V36
# jianpu_ly compatibility edition

from music21 import converter, stream, note, chord, meter, tempo
import copy
import sys


VERSION = "CLEAN MUSICXML V36"


def remove_bad_elements(score):

    print("remove unsupported notation")

    for part in score.parts:

        # 移除 voices
        for v in list(part.recurse().getElementsByClass(stream.Voice)):
            try:
                v.activeSite.remove(v)
            except:
                pass


        # chord -> 單音
        for c in list(part.recurse().getElementsByClass(chord.Chord)):

            try:
                n = note.Note(c.pitches[0])
                n.duration = copy.deepcopy(c.duration)

                c.activeSite.replace(c, n)

            except:
                pass


        # 移除 tie / dot
        for n in part.recurse().notes:

            n.tie = None

            try:
                n.duration.dots = 0
            except:
                pass


    return score



def quantize_duration(score):

    print("duration quantize")

    # 16分音符網格
    step = 0.25


    for n in score.recurse().notes:

        q = n.duration.quarterLength

        q = round(q / step) * step


        if q <= 0:
            q = step


        n.duration.quarterLength = q


    return score



def force_44(score):

    print("force 4/4")


    for part in score.parts:

        for ts in list(
            part.recurse()
            .getElementsByClass(meter.TimeSignature)
        ):

            ts.numerator = 4
            ts.denominator = 4


        if not part.recurse().getElementsByClass(
            meter.TimeSignature
        ):

            part.insert(
                0,
                meter.TimeSignature("4/4")
            )


    return score



def rebuild_measures(score):

    print("rebuild measures")

    new_score = stream.Score()


    for old_part in score.parts:

        new_part = stream.Part()


        current = stream.Measure(number=1)

        beat = 0
        measure_no = 1


        for item in old_part.recurse().notesAndRests:


            dur = item.duration.quarterLength


            while dur > 0:


                remain = 4 - beat


                if dur <= remain:

                    obj = copy.deepcopy(item)

                    obj.duration.quarterLength = dur

                    current.append(obj)

                    beat += dur

                    dur = 0


                else:

                    obj = copy.deepcopy(item)

                    obj.duration.quarterLength = remain

                    current.append(obj)


                    dur -= remain


                    new_part.append(current)


                    measure_no += 1

                    current = stream.Measure(
                        number=measure_no
                    )

                    beat = 0



            if abs(beat-4) < 0.001:

                new_part.append(current)

                measure_no += 1

                current = stream.Measure(
                    number=measure_no
                )

                beat = 0



        # 補滿最後小節

        while beat < 4:

            r = note.Rest()

            r.duration.quarterLength = min(
                1,
                4-beat
            )

            current.append(r)

            beat += r.duration.quarterLength



        if len(current.notesAndRests):

            new_part.append(current)


        new_score.append(new_part)



    return new_score



def final_check(score):

    print("FINAL CHECK")


    for i,m in enumerate(
        score.parts[0]
        .getElementsByClass(stream.Measure),
        1
    ):

        length = m.barDuration.quarterLength


        print(
            "Measure",
            i,
            float(length)
        )


        if abs(length-4)>0.01:

            print(
                "WARNING measure mismatch"
            )



def clean(input_file, output_file):

    print(VERSION)


    score = converter.parse(
        input_file
    )


    # 移除 tempo 問題

    for t in score.recurse().getElementsByClass(
        tempo.MetronomeMark
    ):

        try:
            t.activeSite.remove(t)
        except:
            pass



    score = remove_bad_elements(score)


    score = quantize_duration(score)


    score = force_44(score)


    score = rebuild_measures(score)


    score = force_44(score)


    final_check(score)


    print("FINAL WRITE")


    score.write(
        "musicxml",
        fp=output_file
    )


    print("DONE")
    print(output_file)



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
        out = "clean.musicxml"



    clean(
        inp,
        out
    )