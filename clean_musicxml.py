import sys
import music21
from music21 import stream, meter, note, chord, duration


VERSION = "CLEAN MUSICXML V24.4 FINAL JIANPU TICK SAFE"


print("================")
print(VERSION)
print("================")


def remove_voices(score):

    print("remove voices")

    for part in score.parts:
        for v in list(part.recurse().getElementsByClass(stream.Voice)):
            try:
                v.flatten()
                v.remove(v)
            except:
                pass



def remove_chords(score):

    print("remove chords")

    for c in score.recurse().getElementsByClass(chord.Chord):

        n = note.Note(
            c.pitches[-1],
            quarterLength=c.duration.quarterLength
        )

        c.activeSite.replace(c, n)



def remove_beams(score):

    print("remove beams")

    for n in score.recurse().notes:

        try:
            n.beams = None
        except:
            pass



def remove_ties(score):

    print("remove ties")

    for n in score.recurse().notes:

        try:
            n.tie = None
        except:
            pass



def force_time(score):

    print("force 4/4")

    for part in score.parts:

        part.insert(
            0,
            meter.TimeSignature("4/4")
        )



def duration_quantize(score):

    print("duration quantize")

    for n in score.recurse().notesAndRests:

        q = n.quarterLength

        # 16分音符格
        q = round(q * 4) / 4

        if q <= 0:
            q = 0.25

        n.quarterLength = q



def rebuild_measures(score):

    print("rebuild measures")

    score.makeMeasures(
        inPlace=True
    )



def split_cross_measure_notes(score):

    print("split cross measure notes")

    for part in score.parts:

        measures = list(
            part.getElementsByClass(
                stream.Measure
            )
        )

        for m in measures:

            total = 0

            for n in list(
                m.notesAndRests
            ):

                total += n.quarterLength

                if total > 4:

                    overflow = total - 4

                    n.quarterLength -= overflow

                    if n.quarterLength <= 0:
                        n.quarterLength = 0.25



def fill_measure_rest(score):

    print("fill measure rest")

    for part in score.parts:

        for m in part.getElementsByClass(stream.Measure):

            length = 0

            for n in m.notesAndRests:
                length += n.quarterLength


            if length < 4:

                r = note.Rest(
                    quarterLength=4-length
                )

                m.append(r)



def jianpu_tick_quantize(score):

    print("jianpu tick quantize")


    # jianpu_ly divisions = 16
    # 1 beat = 4 ticks

    for n in score.recurse().notesAndRests:


        q = n.quarterLength


        # 強制對齊 1/16 音符
        q = round(q * 4) / 4


        if q < 0.25:

            q = 0.25


        n.duration = duration.Duration(q)



def final_check(score):

    print("FINAL CHECK")


    ok = True


    for i,m in enumerate(
        score.parts[0].getElementsByClass(stream.Measure),
        1
    ):

        total = 0


        for n in m.notesAndRests:

            total += n.quarterLength


        print(
            "Measure",
            i,
            total
        )


        if abs(total-4) > 0.01:

            ok=False


    if ok:

        print("ALL MEASURES SAFE")

    else:

        print("WARNING MEASURE ERROR")



def clean_musicxml(input_file, output_file):


    print("read")

    score = music21.converter.parse(
        input_file
    )


    remove_voices(score)

    remove_chords(score)

    remove_beams(score)

    remove_ties(score)

    force_time(score)


    duration_quantize(score)


    rebuild_measures(score)


    split_cross_measure_notes(score)


    rebuild_measures(score)


    fill_measure_rest(score)


    rebuild_measures(score)


    jianpu_tick_quantize(score)


    rebuild_measures(score)


    score.stripTies(inPlace=True)


    print("clear notation cache")


    final_check(score)


    print("FINAL WRITE")


    score.write(
        "musicxml",
        fp=output_file
    )


    print("DONE")
    print(output_file)



if __name__ == "__main__":


    if len(sys.argv)<3:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )