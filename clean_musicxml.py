from music21 import converter, stream, meter, note, chord
import sys


VERSION = "CLEAN MUSICXML V23 FINAL STREAM SAFE NOTE SPLIT"


def remove_chords(part):
    for c in list(part.recurse().getElementsByClass(chord.Chord)):
        n = note.Note(c.pitches[0])
        n.duration = c.duration
        c.activeSite.replace(c, n)


def remove_voices(part):

    for v in list(part.recurse().getElementsByClass(stream.Voice)):
        notes = list(v.notesAndRests)

        for x in notes:
            v.activeSite.insert(x.offset, x)

        if v.activeSite:
            v.activeSite.remove(v)


def reset_beams(score):

    for n in score.recurse().notes:
        try:
            n.beams.clear()
        except:
            pass



def quantize_notes(part):

    for n in part.recurse().notesAndRests:

        q = round(n.duration.quarterLength * 4) / 4

        if q <= 0:
            q = 0.25

        n.duration.quarterLength = q



def force_44(score):

    for p in score.parts:

        p.insert(
            0,
            meter.TimeSignature("4/4")
        )



def rebuild_measures(part):

    part.makeMeasures(
        inPlace=True
    )



def split_crossing_notes(part):

    print("FINAL NOTE SPLIT")

    measure_length = 4.0

    notes = list(
        part.recurse().notes
    )


    for n in notes:

        start = n.offset
        dur = n.duration.quarterLength

        end = start + dur

        current_bar_end = (
            int(start / measure_length) + 1
        ) * measure_length


        if end > current_bar_end:

            first_len = (
                current_bar_end - start
            )

            second_len = (
                end - current_bar_end
            )


            if first_len > 0 and second_len > 0:

                print(
                    "split:",
                    start,
                    dur,
                    "=>",
                    first_len,
                    second_len
                )


                n.duration.quarterLength = first_len


                new_note = note.Note(
                    n.pitch
                )

                new_note.duration.quarterLength = second_len


                part.insert(
                    current_bar_end,
                    new_note
                )



def normalize_bars(score):

    for p in score.parts:

        for m in p.getElementsByClass(
            stream.Measure
        ):

            total = 0

            for n in m.notesAndRests:
                total += n.duration.quarterLength


            if abs(total - 4.0) > 0.01:

                print(
                    "fix measure",
                    m.number,
                    total
                )



def clean_musicxml(
        input_file,
        output_file
):

    print("================")
    print(VERSION)
    print("================")

    print("read")

    score = converter.parse(
        input_file
    )


    print("remove voices")

    for p in score.parts:
        remove_voices(p)


    print("remove chords")

    for p in score.parts:
        remove_chords(p)


    print("safe beam reset")

    reset_beams(score)



    print("quantize")

    for p in score.parts:
        quantize_notes(p)



    print("force 4/4")

    force_44(score)



    print("rebuild measures")

    for p in score.parts:
        rebuild_measures(p)



    print("FINAL NOTE SPLIT")

    for p in score.parts:
        split_crossing_notes(p)



    print("rebuild measures")

    for p in score.parts:
        rebuild_measures(p)



    print("safe beam reset")

    reset_beams(score)



    print("check measures")

    normalize_bars(score)


    print("write")


    score.write(
        "musicxml",
        fp=output_file
    )


    print()
    print("DONE", output_file)



if __name__ == "__main__":

    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )