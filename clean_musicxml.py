import sys
import music21
from music21 import converter, meter, note, chord, stream


VERSION = "CLEAN MUSICXML V24.2 FINAL JIANPU COMPATIBLE"


def remove_bad_elements(score):

    print("remove voices")
    print("remove chords")

    for part in score.parts:

        for c in list(part.recurse().getElementsByClass('Chord')):
            try:
                n = note.Note(c.pitches[0])
                n.duration = c.duration
                c.activeSite.replace(c, n)
            except:
                pass


        for n in list(part.recurse().notes):

            if isinstance(n, chord.Chord):
                continue

            # 移除 tie
            n.tie = None

            # duration quantize
            q = round(n.duration.quarterLength * 4) / 4

            if q <= 0:
                q = 0.25

            n.duration.quarterLength = q


def force_timesig(score):

    print("force 4/4")

    for part in score.parts:

        part.insert(
            0,
            meter.TimeSignature("4/4")
        )


def quantize_measures(score):

    print("FINAL BAR QUANTIZE")

    for part in score.parts:

        measures = part.makeMeasures()

        for m in measures:

            total = 0

            for n in list(m.notesAndRests):

                dur = n.duration.quarterLength

                dur = round(dur * 4) / 4

                if dur <= 0:
                    dur = 0.25

                n.duration.quarterLength = dur

                total += dur


            # 4/4 = 4拍
            if total > 4:

                print(
                    "trim measure",
                    m.number,
                    total
                )

                remain = 4

                for n in list(m.notesAndRests):

                    if remain <= 0:
                        try:
                            m.remove(n)
                        except:
                            pass
                        continue


                    if n.duration.quarterLength > remain:

                        n.duration.quarterLength = remain


                    remain -= n.duration.quarterLength


        part.remove(
            part.recurse()
        )



def rebuild_clean(score):

    print("rebuild score")

    new_score = stream.Score()

    for part in score.parts:

        new_part = stream.Part()

        for n in part.flatten().notesAndRests:

            new_part.append(n)

        new_score.append(new_part)


    return new_score



def clean_musicxml(input_file, output_file):

    print("================")
    print(VERSION)
    print("================")


    print("read")

    score = converter.parse(input_file)


    remove_bad_elements(score)


    force_timesig(score)


    score = rebuild_clean(score)


    quantize_measures(score)


    print("clear notation cache")


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