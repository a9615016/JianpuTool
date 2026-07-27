import sys
import os
import music21
from music21 import stream, meter, note, chord, tie


VERSION = "CLEAN MUSICXML V23.4 FINAL BAR QUANTIZE"


def remove_voices(score):
    print("remove voices")

    for p in score.parts:
        for n in p.recurse():
            if hasattr(n, "voice"):
                try:
                    n.voice = None
                except:
                    pass


def remove_chords(score):
    print("remove chords")

    for p in score.parts:
        for c in list(p.recurse().getElementsByClass(chord.Chord)):
            new_notes = []

            for pitch in c.pitches:
                n = note.Note(
                    pitch,
                    quarterLength=c.duration.quarterLength
                )
                new_notes.append(n)

            c.activeSite.replace(c, new_notes[0])


def remove_bad_beams(score):
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



def quantize_duration(n):

    q = n.duration.quarterLength

    # 16分音符格
    grid = 0.25

    q = round(q / grid) * grid


    if q <= 0:
        q = 0.25


    if q > 4:
        q = 4


    n.duration.quarterLength = q



def quantize_notes(score):

    print("duration quantize")

    for n in score.recurse().notes:

        quantize_duration(n)



def split_long_notes(part):

    print("split long notes")

    result = stream.Part()

    current = 0

    bar_length = 4


    for n in part.notes:

        remain = n.duration.quarterLength


        while remain > 0:

            pos = current % bar_length

            available = bar_length - pos


            length = min(
                remain,
                available
            )


            new = n.clone()

            new.duration.quarterLength = length

            result.append(new)


            remain -= length

            current += length


    return result



def rebuild_measure(part):

    print("rebuild measures")

    part2 = split_long_notes(part)

    measures = stream.Part()

    measures.append(
        meter.TimeSignature("4/4")
    )


    for n in part2.notes:

        measures.append(n)


    return measures



def check_bars(score):

    print("check measures")

    for p in score.parts:

        offset = 0

        bar = 1

        total = 0


        for n in p.notes:

            total += n.duration.quarterLength


            if total >= 4:

                print(
                    "Measure",
                    bar,
                    4.0
                )

                total = 0
                bar += 1



def clean_musicxml(src, dst):

    print("================")
    print(VERSION)
    print("================")


    print("read")

    score = music21.converter.parse(src)



    remove_voices(score)

    remove_chords(score)

    remove_bad_beams(score)

    remove_ties(score)


    print("force 4/4")


    for p in score.parts:

        p.insert(
            0,
            meter.TimeSignature("4/4")
        )


    quantize_notes(score)



    new_score = stream.Score()



    for p in score.parts:

        new_part = rebuild_measure(p)

        new_score.append(new_part)



    remove_bad_beams(new_score)

    remove_ties(new_score)



    check_bars(new_score)



    print("FINAL WRITE")


    new_score.write(
        "musicxml",
        fp=dst
    )


    print()
    print("DONE")
    print(dst)



if __name__ == "__main__":

    if len(sys.argv) < 3:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit(1)


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )