# midi_to_musicxml.py
# V2.2
# MIDI -> MusicXML
# Jianpu compatible version

from music21 import converter, stream, note, meter, tempo
import sys


print("================")
print("MIDI TO MUSICXML V2.2")
print("================")


if len(sys.argv) < 3:
    print(
        "Usage: python midi_to_musicxml.py input.mid output.musicxml"
    )
    sys.exit(1)


input_mid = sys.argv[1]
output_xml = sys.argv[2]


print("讀取 MIDI...")
score = converter.parse(input_mid)


new_score = stream.Score()


# 量化到簡譜常用節奏
def quantize_duration(x):

    values = [
        0.25,   # 四分之一拍
        0.5,
        0.75,
        1.0,
        1.5,
        2.0,
        3.0,
        4.0
    ]

    return min(
        values,
        key=lambda v: abs(v-x)
    )


for old_part in score.parts:

    print("重新建立 Part")

    new_part = stream.Part()

    new_part.append(
        meter.TimeSignature("4/4")
    )


    current_measure = stream.Measure(
        number=1
    )


    beat_position = 0


    notes = list(
        old_part.recurse().notes
    )


    for n in notes:


        if not isinstance(n, note.Note):
            continue


        dur = float(
            n.duration.quarterLength
        )


        dur = quantize_duration(
            dur
        )


        remain = dur


        while remain > 0:


            space = 4 - beat_position


            length = min(
                remain,
                space
            )


            new_note = note.Note(
                n.pitch
            )


            new_note.duration.quarterLength = length


            current_measure.append(
                new_note
            )


            beat_position += length
            remain -= length



            # 小節完成

            if beat_position >= 4:


                new_part.append(
                    current_measure
                )


                current_measure = stream.Measure(
                    number=current_measure.number + 1
                )


                beat_position = 0



    # 補最後小節休止

    if beat_position > 0:

        rest = note.Rest()

        rest.duration.quarterLength = (
            4 - beat_position
        )

        current_measure.append(rest)

        new_part.append(
            current_measure
        )


    new_score.append(
        new_part
    )


print("寫入 MusicXML...")


new_score.write(
    "musicxml",
    fp=output_xml
)


print("完成:")
print(output_xml)