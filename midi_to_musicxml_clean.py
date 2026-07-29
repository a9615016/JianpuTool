from music21 import converter
from music21 import stream
from music21 import note
from music21 import chord
from music21 import meter
import sys


def convert(
    midi_file,
    output
):

    print("MIDI TO MUSICXML CLEAN v8")


    src = converter.parse(
        midi_file
    )


    notes = src.flatten().notes


    score = stream.Score()

    part = stream.Part()


    part.insert(
        0,
        meter.TimeSignature("4/4")
    )


    measure_no = 1

    measure = stream.Measure(
        number=measure_no
    )


    beat_used = 0


    count = 0



    for n in notes:


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


        if dur < 0.25:

            dur = 0.25


        # 強制16分音符網格

        dur = round(
            dur * 4
        ) / 4



        # 防止跨小節

        if beat_used + dur > 4:


            rest = 4 - beat_used


            if rest > 0:

                r = note.Rest()

                r.duration.quarterLength = rest

                measure.append(r)



            part.append(
                measure
            )


            measure_no += 1


            measure = stream.Measure(
                number=measure_no
            )


            beat_used = 0



        nn = note.Note(
            pitch
        )


        nn.duration.quarterLength = dur


        measure.append(
            nn
        )


        beat_used += dur


        count += 1



    # 最後補滿

    if beat_used < 4:

        r = note.Rest()

        r.duration.quarterLength = (
            4 - beat_used
        )

        measure.append(r)



    part.append(
        measure
    )


    score.append(
        part
    )



    print(
        "FINAL CHECK"
    )


    for m in part.getElementsByClass(
        "Measure"
    ):

        print(
            "Measure",
            m.number,
            float(m.duration.quarterLength)
        )



    score.write(
        "musicxml",
        fp=output
    )


    print(
        "DONE",
        output
    )



if __name__=="__main__":

    convert(
        sys.argv[1],
        sys.argv[2]
    )