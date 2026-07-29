from music21 import converter, stream, meter, note, chord
import sys
import os


def convert_midi_to_musicxml(
    midi_file,
    output_file
):

    print("MIDI TO MUSICXML CLEAN v6")

    # =====================
    # LOAD MIDI
    # =====================

    score = converter.parse(
        midi_file
    )


    flat = score.flatten()


    print(
        "TOTAL EVENTS:",
        len(flat.notes)
    )


    # =====================
    # NEW PART
    # =====================

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


        # 移除 chord
        if isinstance(
            n,
            chord.Chord
        ):

            pitch = n.pitches[0]


        else:

            pitch = n.pitch



        new_note = note.Note(
            pitch
        )


        # =====================
        # 強制節奏量化
        # =====================

        dur = float(
            n.duration.quarterLength
        )


        # 最小16分音符
        if dur < 0.25:

            dur = 0.25



        # 四分之一拍網格
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



    # =====================
    # REBUILD MEASURES
    # =====================

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



    # =====================
    # FINAL CHECK
    # =====================

    print(
        "FINAL CHECK"
    )


    for m in new_score.parts[0].getElementsByClass("Measure"):

        print(
            "Measure",
            m.number,
            m.duration.quarterLength
        )



    print(
        "WRITE XML"
    )


    new_score.write(
        "musicxml",
        fp=output_file
    )


    print(
        "DONE",
        output_file
    )




if __name__ == "__main__":


    if len(sys.argv) < 3:

        print(
            "usage: python midi_to_musicxml_clean.py input.mid output.musicxml"
        )

        sys.exit(1)



    convert_midi_to_musicxml(

        sys.argv[1],

        sys.argv[2]

    )