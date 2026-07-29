# midi_to_musicxml_clean.py
# VERSION: v6
# MIDI -> MusicXML strict rebuild

from music21 import converter, stream, meter, note, chord
import sys


def convert_midi_to_musicxml(
    midi_file,
    output_file
):

    print("================================")
    print("MIDI TO MUSICXML CLEAN v6")
    print("================================")


    # -------------------------
    # Load MIDI
    # -------------------------

    score = converter.parse(
        midi_file
    )


    flat = score.flatten()


    print(
        "TOTAL NOTES:",
        len(flat.notes)
    )


    # -------------------------
    # New clean part
    # -------------------------

    part = stream.Part()


    part.insert(
        0,
        meter.TimeSignature("4/4")
    )


    print(
        "EXTRACT NOTES"
    )


    count = 0


    for n in flat.notes:


        # chord 只取最高音

        if isinstance(
            n,
            chord.Chord
        ):

            pitch = n.pitches[-1]


        else:

            pitch = n.pitch



        new_note = note.Note(
            pitch
        )


        # -------------------------
        # duration quantize
        # -------------------------

        dur = float(
            n.duration.quarterLength
        )


        # 最短16分音符

        if dur < 0.25:

            dur = 0.25



        # 四分音符網格

        dur = round(
            dur * 4
        ) / 4



        new_note.duration.quarterLength = dur


        part.append(
            new_note
        )


        count += 1



    print(
        "NEW NOTES:",
        count
    )



    # -------------------------
    # rebuild score
    # -------------------------

    print(
        "REBUILD MEASURES"
    )


    new_score = stream.Score()


    new_score.append(
        part
    )


    new_score.makeMeasures(
        inPlace=True
    )



    # -------------------------
    # Final check
    # -------------------------

    print(
        "FINAL CHECK"
    )


    bad = False


    for m in new_score.parts[0].getElementsByClass("Measure"):


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



    # -------------------------
    # Write MusicXML
    # -------------------------

    print(
        "WRITE XML"
    )


    new_score.write(
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