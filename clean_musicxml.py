import sys
from music21 import converter, stream, note, chord, meter, duration


VERSION = "CLEAN MUSICXML V23.3 FINAL BAR SAFE"


def remove_bad_objects(score):

    print("remove voices")
    print("remove chords")

    for part in score.parts:

        remove_list = []

        for el in part.recurse():

            if isinstance(el, chord.Chord):
                remove_list.append(el)

            if isinstance(el, note.Note):

                # remove tiny duration
                if el.duration.quarterLength < 0.25:
                    remove_list.append(el)

        for el in remove_list:
            try:
                el.activeSite.remove(el)
            except Exception:
                pass



def remove_beams(score):

    print("remove beams")

    for n in score.recurse().notes:

        try:
            n.beams = []
        except Exception:
            pass



def fix_duration(score):

    print("fix duration")

    allowed = [
        0.25,
        0.5,
        1,
        2,
        4
    ]

    for n in score.recurse().notes:

        q = float(n.duration.quarterLength)

        closest = min(
            allowed,
            key=lambda x: abs(x-q)
        )

        n.duration = duration.Duration(closest)



def force_meter(score):

    print("force 4/4")

    for part in score.parts:

        ts = part.recurse().getElementsByClass(
            meter.TimeSignature
        )

        if len(ts)==0:
            part.insert(
                0,
                meter.TimeSignature("4/4")
            )



def split_crossing_notes(score):

    print("split crossing notes")

    for part in score.parts:

        measures = list(
            part.getElementsByClass(
                stream.Measure
            )
        )

        for m in measures:

            pos = 0

            for n in list(m.notesAndRests):

                length = n.duration.quarterLength

                if pos + length > 4:

                    remain = 4-pos
                    extra = length-remain

                    if remain > 0:

                        n.duration = duration.Duration(remain)

                        new_note = n.__deepcopy__()

                        new_note.duration = duration.Duration(extra)

                        try:
                            m.insert(
                                n.offset+remain,
                                new_note
                            )
                        except Exception:
                            pass

                pos += n.duration.quarterLength



def rebuild_measures(score):

    print("rebuild measures")

    for part in score.parts:

        try:
            part.makeMeasures(
                inPlace=True
            )
        except Exception:
            pass



def final_bar_check(score):

    print("final bar check")

    for part in score.parts:

        for m in part.getElementsByClass(
            stream.Measure
        ):

            q = float(
                m.duration.quarterLength
            )

            print(
                "Measure",
                m.number,
                q
            )



def clean_musicxml(input_file, output_file):

    print("================")
    print(VERSION)
    print("================")

    print("read")

    score = converter.parse(
        input_file
    )


    remove_bad_objects(score)

    remove_beams(score)

    fix_duration(score)

    force_meter(score)

    rebuild_measures(score)

    split_crossing_notes(score)

    fix_duration(score)

    rebuild_measures(score)

    remove_beams(score)

    final_bar_check(score)


    print("write")

    score.write(
        "musicxml",
        fp=output_file
    )


    print()
    print(
        "DONE",
        output_file
    )



if __name__=="__main__":

    if len(sys.argv)<3:

        print(
            "usage: python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit(1)


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )