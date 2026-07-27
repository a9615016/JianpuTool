# clean_musicxml.py
# CLEAN MUSICXML V23 FINAL STREAM SAFE NOTE SPLIT

import sys
from music21 import converter, stream, meter, note, chord


print("================")
print("CLEAN MUSICXML V23 FINAL STREAM SAFE NOTE SPLIT")
print("================")


def safe_remove(part):

    print("SAFE REMOVE NOTES")

    remove_list = []

    for el in list(part.recurse()):
        if isinstance(el, (note.Note, note.Rest, chord.Chord)):
            remove_list.append(el)

    for el in remove_list:
        try:
            el.activeSite.remove(el)
        except:
            pass



def remove_chords(score):

    print("remove chords")

    for p in score.parts:
        for c in list(p.recurse().getElementsByClass(chord.Chord)):
            try:
                n = note.Note(
                    c.root().pitch
                )
                n.duration = c.duration
                c.activeSite.replace(c, n)
            except:
                pass



def remove_voice(score):

    print("remove voices")

    for p in score.parts:
        for el in list(p.recurse()):
            if hasattr(el, "voice"):
                try:
                    el.voice = None
                except:
                    pass



def remove_beams(score):

    print("safe beam reset")

    for n in score.recurse().notes:

        try:
            n.beams.clear()
        except:
            pass



def quantize(score):

    print("quantize")

    for n in score.recurse().notesAndRests:

        try:
            n.duration.quarterLength = round(
                float(n.duration.quarterLength) * 4
            ) / 4

        except:
            pass



def force_time(score):

    print("force 4/4")

    ts = meter.TimeSignature("4/4")

    for p in score.parts:

        try:
            p.insert(0, ts)
        except:
            pass



def rebuild_measures(score):

    print("rebuild measures")

    try:
        score.makeMeasures(inPlace=True)

    except Exception as e:
        print(e)



def split_crossing(score):

    print("FINAL NOTE SPLIT")

    try:
        score.makeNotation(inPlace=True)

    except:
        pass



def check(score):

    print("check measures")

    for i,m in enumerate(
        score.recurse().getElementsByClass(
            stream.Measure
        ),
        1
    ):

        try:
            print(
                "Measure",
                i,
                m.barDuration.quarterLength
            )

        except:
            pass



def clean_musicxml(input_file, output_file):

    print("read")

    score = converter.parse(input_file)


    remove_voice(score)

    remove_chords(score)

    remove_beams(score)


    quantize(score)

    force_time(score)

    rebuild_measures(score)


    split_crossing(score)


    safe_remove(score)


    rebuild_measures(score)


    remove_beams(score)


    check(score)


    print("write")

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
            "usage: python clean_musicxml.py input.musicxml output.musicxml"
        )
        sys.exit(1)


    clean_musicxml(
        sys.argv[1],
        sys.argv[2]
    )