from music21 import converter, stream, meter, note, chord
import sys


print("MIDI TO MUSICXML CLEAN 20260729")


def clean_midi_to_xml(input_mid, output_xml):

    print("LOAD MIDI")

    score = converter.parse(input_mid)


    print("FLATTEN")

    flat = score.flatten()


    melody = stream.Part()


    print("REMOVE CHORD")


    for element in flat.notesAndRests:


        if isinstance(element, chord.Chord):

            # 只取最高音當旋律

            n = note.Note(
                element.highest.pitch
            )

            n.duration = element.duration

            melody.append(n)



        elif isinstance(element, note.Note):

            melody.append(
                element
            )



    print("QUANTIZE")


    melody.quantize(
        quarterLengthDivisors=[
            4,
            8,
            16
        ],
        processOffsets=True,
        processDurations=True
    )


    print("FORCE 4/4")


    melody.insert(
        0,
        meter.TimeSignature("4/4")
    )


    print("FIX OVERLONG NOTES")


    for n in melody.notes:


        if n.duration.quarterLength > 4:

            print(
                "trim",
                n.pitch,
                n.duration.quarterLength
            )


            n.duration.quarterLength = 4



    print("CREATE SCORE")


    new_score = stream.Score()

    new_score.append(
        melody
    )


    print("WRITE MUSICXML")


    new_score.write(
        "musicxml",
        fp=output_xml
    )


    print("DONE")

    print(output_xml)



if __name__=="__main__":


    if len(sys.argv)<2:

        print(
            "python midi_to_musicxml_clean.py input.mid output.musicxml"
        )

        exit()


    inp=sys.argv[1]


    if len(sys.argv)>=3:

        out=sys.argv[2]

    else:

        out="clean.musicxml"



    clean_midi_to_xml(
        inp,
        out
    )