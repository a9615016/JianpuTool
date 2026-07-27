import sys
import music21
from music21 import converter, meter, note, chord, stream, bar


VERSION = "CLEAN MUSICXML V24.3 JIANPU BAR SAFE"


# jianpu_ly 一小節固定 4/4 = 16 格
GRID = 0.25


def remove_bad(score):

    print("remove voices")
    print("remove chords")
    print("remove beams")
    print("remove ties")

    for part in score.parts:

        for c in list(part.recurse().getElementsByClass(chord.Chord)):
            try:
                n = note.Note(c.pitches[0])
                n.duration = c.duration
                c.activeSite.replace(c, n)
            except:
                pass

        for n in part.recurse().notes:

            n.tie = None


def quantize_notes(score):

    print("duration quantize")

    for part in score.parts:

        for n in part.recurse().notesAndRests:

            q = round(
                n.duration.quarterLength / GRID
            ) * GRID

            if q <= 0:
                q = GRID

            n.duration.quarterLength = q


def force_time(score):

    print("force 4/4")

    for part in score.parts:

        part.insert(
            0,
            meter.TimeSignature("4/4")
        )


def rebuild_jianpu_measures(score):

    print("jianpu measure rebuild")


    new_score = stream.Score()


    for part in score.parts:

        new_part = stream.Part()

        current = 0


        for element in part.flatten().notesAndRests:

            dur = element.duration.quarterLength


            # 超過小節，自動切割
            while dur > 0:

                remain = 4 - current


                if dur <= remain:

                    element.duration.quarterLength = dur
                    new_part.append(element)

                    current += dur
                    dur = 0


                else:

                    # 前半段

                    first = element.clone()

                    first.duration.quarterLength = remain

                    new_part.append(first)


                    dur -= remain


                    # 新小節

                    current = 0


                    second = element.clone()

                    second.duration.quarterLength = dur

                    element = second


        # 補滿最後小節

        if current > 0:

            rest = note.Rest()

            rest.duration.quarterLength = 4-current

            new_part.append(rest)


        new_score.append(new_part)


    return new_score



def check(score):

    print("FINAL JIANPU CHECK")

    for i, part in enumerate(score.parts):

        pos = 0
        measure = 1

        for n in part.flatten().notesAndRests:

            pos += n.duration.quarterLength


            if pos > 4.001:

                print(
                    "BAD MEASURE",
                    measure,
                    pos
                )

                raise Exception(
                    "jianpu measure overflow"
                )


            if abs(pos-4) < 0.001:

                print(
                    "Measure",
                    measure,
                    "4.0"
                )

                measure += 1
                pos = 0


def clean_musicxml(input_file, output_file):

    print("================")
    print(VERSION)
    print("================")


    print("read")

    score = converter.parse(input_file)


    remove_bad(score)

    force_time(score)

    quantize_notes(score)


    score = rebuild_jianpu_measures(score)


    check(score)


    print("FINAL WRITE")


    score.write(
        "musicxml",
        fp=output_file
    )


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