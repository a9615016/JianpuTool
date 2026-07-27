import sys
from music21 import converter, stream, meter, note, chord, duration
from music21.beam import Beams


VERSION = "CLEAN MUSICXML V22.9 FINAL BAR FORCE"


def reset_beams(score):
    for n in score.recurse().notes:
        try:
            n.beams = Beams()
        except Exception:
            n.beams = None


def remove_bad_elements(score):

    for part in score.parts:

        # remove voices
        for el in list(part.recurse()):
            if isinstance(el, stream.Voice):
                el.activeSite.remove(el)

        # remove chords
        for c in list(part.recurse().getElementsByClass(chord.Chord)):
            highest = c.normalOrder[0] if c.normalOrder else 60
            n = note.Note(highest)
            n.duration = c.duration
            c.activeSite.replace(c, n)


def force_time_signature(score):

    for part in score.parts:
        part.insert(0, meter.TimeSignature("4/4"))


def rebuild_measures(part):

    part.makeMeasures(
        inPlace=True,
        meterStream=part.recurse().getElementsByClass(
            meter.TimeSignature
        )
    )


def split_overfull_measures(part):

    new_part = stream.Part()

    for m in part.getElementsByClass(stream.Measure):

        total = m.duration.quarterLength

        if total <= 4:
            new_part.append(m)
            continue


        current = stream.Measure(
            number=m.number
        )

        current_len = 0


        for n in m.notesAndRests:

            length = n.duration.quarterLength


            # 超過小節
            if current_len + length > 4:

                remain = 4-current_len

                if remain > 0:
                    r = note.Rest()
                    r.duration = duration.Duration(remain)
                    current.append(r)


                new_part.append(current)


                current = stream.Measure(
                    number=m.number
                )

                current_len = 0


            current.append(n)
            current_len += length



        if current_len < 4:
            r = note.Rest()
            r.duration = duration.Duration(
                4-current_len
            )
            current.append(r)


        new_part.append(current)


    part.replace(
        part.getElementsByClass(stream.Measure),
        new_part.getElementsByClass(stream.Measure)
    )


def normalize_bars(score):

    for part in score.parts:

        rebuild_measures(part)

        split_overfull_measures(part)

        rebuild_measures(part)



def check(score):

    for m in score.recurse().getElementsByClass(
        stream.Measure
    ):
        print(
            "Measure",
            m.number,
            m.duration.quarterLength
        )


def clean_musicxml(input_file, output_file):

    print("================")
    print(VERSION)
    print("================")

    print("read")

    score = converter.parse(input_file)


    print("remove voices")
    remove_bad_elements(score)


    print("safe beam reset")
    reset_beams(score)


    print("quantize")

    score.quantize(
        quarterLengthDivisors=[
            4,8,16
        ]
    )


    print("force 4/4")
    force_time_signature(score)


    print("rebuild measures")
    rebuild_measures(
        score.parts[0]
    )


    print("FINAL BAR FORCE")

    normalize_bars(score)


    print("safe beam reset")
    reset_beams(score)


    print("check measures")

    check(score)


    print("write")

    score.write(
        "musicxml",
        fp=output_file
    )


    print()
    print("DONE",output_file)



if __name__=="__main__":

    if len(sys.argv)<3:
        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )
        sys.exit()


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )