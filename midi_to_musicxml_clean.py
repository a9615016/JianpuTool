# midi_to_musicxml_clean.py
# VERSION v7
# MIDI -> MusicXML strict rebuild for jianpu_ly


from music21 import converter
from music21 import stream
from music21 import note
from music21 import chord
from music21 import meter
import sys



def convert_midi_to_musicxml(
        midi_file,
        output_file
):

    print("==============================")
    print("MIDI TO MUSICXML CLEAN v7")
    print("==============================")


    # --------------------------
    # read midi
    # --------------------------

    src = converter.parse(
        midi_file
    )


    notes = src.flatten().notes


    print(
        "SOURCE NOTES:",
        len(notes)
    )


    # --------------------------
    # create new part
    # --------------------------

    part = stream.Part()


    part.insert(
        0,
        meter.TimeSignature("4/4")
    )


    current_offset = 0


    count = 0



    # --------------------------
    # rebuild notes
    # --------------------------

    for n in notes:


        # chord -> highest pitch

        if isinstance(
            n,
            chord.Chord
        ):

            pitch = n.pitches[-1]

        else:

            pitch = n.pitch



        dur = float(
            n.duration.quarterLength
        )


        # remove strange duration

        if dur <= 0:

            dur = 0.25



        # minimum 16th

        if dur < 0.25:

            dur = 0.25



        # quantize

        dur = round(
            dur * 4
        ) / 4



        new_note = note.Note(
            pitch
        )


        new_note.duration.quarterLength = dur



        # IMPORTANT
        # rebuild timeline

        part.insert(
            current_offset,
            new_note
        )


        current_offset += dur


        count += 1



    print(
        "NEW NOTES:",
        count
    )


    print(
        "TOTAL QUARTER:",
        current_offset
    )



    # --------------------------
    # rebuild score
    # --------------------------

    score = stream.Score()


    score.append(
        part
    )


    print(
        "MAKE MEASURES"
    )


    score.makeMeasures(
        inPlace=True
    )



    # --------------------------
    # check measures
    # --------------------------

    print(
        "FINAL CHECK"
    )


    bad = False


    for m in score.parts[0].getElementsByClass(
        "Measure"
    ):


        length = float(
            m.duration.quarterLength
        )


        print(
            "Measure",
            m.number,
            length
        )


        if abs(length - 4.0) > 0.01:

            bad = True



    if bad:

        print(
            "WARNING measure mismatch"
        )

    else:

        print(
            "ALL MEASURES OK"
        )



    # --------------------------
    # write
    # --------------------------

    print(
        "WRITE MUSICXML"
    )


    score.write(
        "musicxml",
        fp=output_file
    )


    print(
        "DONE"
    )

    print(
        output_file
    )





if __name__ == "__main__":


    if len(sys.argv) < 3:

        print(
            "usage:"
        )

        print(
            "python midi_to_musicxml_clean.py input.mid output.musicxml"
        )

        sys.exit(1)



    convert_midi_to_musicxml(
        sys.argv[1],
        sys.argv[2]
    )