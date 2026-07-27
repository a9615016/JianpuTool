import sys
import music21
from music21 import stream, note, meter, duration


VERSION = "CLEAN MUSICXML V23.6 FINAL DURATION SPLIT SAFE"


SAFE_DURATIONS = [
    0.25,
    0.5,
    0.75,
    1,
    1.5,
    2,
    3,
    4
]


def split_duration_value(q):

    result = []

    while q > 4:
        result.append(4)
        q -= 4

    if q > 0:
        result.append(q)

    return result



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



def remove_chords(score):

    print("remove chords")

    for c in list(score.recurse().getElementsByClass("Chord")):

        notes = []

        for p in c.pitches:

            n = note.Note(p)
            n.duration = c.duration
            notes.append(n)

        c.activeSite.replace(c, notes)



def remove_voices(score):

    print("remove voices")

    for v in score.recurse().getElementsByClass("Voice"):

        try:
            v.activeSite.remove(v)

        except:
            pass



def duration_split(score):

    print("duration split")

    for part in score.parts:

        new_part = stream.Part()

        for elem in part.flatten().notesAndRests:

            q = elem.duration.quarterLength


            # 正常長度
            if q in SAFE_DURATIONS:

                new_part.append(elem)

            else:

                values = split_duration_value(q)


                for d in values:

                    if isinstance(elem, note.Note):

                        n = note.Note(elem.pitch)

                    else:

                        n = note.Rest()


                    n.duration = duration.Duration(d)

                    new_part.append(n)



        part.clear()

        for x in new_part:

            part.append(x)



def force_time_signature(score):

    print("force 4/4")

    for part in score.parts:

        found = False

        for m in part.getElementsByClass("Measure"):

            for ts in m.getTimeSignatures():

                ts.numerator = 4
                ts.denominator = 4
                found = True


        if not found:

            part.insert(
                0,
                meter.TimeSignature("4/4")
            )



def check_duration(score):

    print("final duration check")

    for n in score.recurse().notes:

        q = n.duration.quarterLength

        if q not in SAFE_DURATIONS:

            print(
                "WARNING duration:",
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


    remove_voices(score)

    remove_chords(score)

    remove_beams(score)

    remove_ties(score)

    force_time_signature(score)

    duration_split(score)

    remove_beams(score)

    remove_ties(score)

    check_duration(score)


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
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )