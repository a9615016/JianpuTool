# midi_to_musicxml.py
# V2.3
# MIDI -> MusicXML
# Jianpu compatible

from music21 import converter, stream, note, meter
import sys


print("================")
print("MIDI TO MUSICXML V2.3")
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



def quantize_duration(value):

    allowed = [
        0.25,
        0.5,
        0.75,
        1.0
    ]

    return min(
        allowed,
        key=lambda x: abs(x-value)
    )



new_score = stream.Score()



for old_part in score.parts:

    print("重新建立 Part")

    new_part = stream.Part()


    new_part.insert(
        0,
        meter.TimeSignature("4/4")
    )


    measure_no = 1

    measure = stream.Measure(
        number=measure_no
    )


    beat = 0



    for n in old_part.recurse().notes:


        if not isinstance(n, note.Note):
            continue


        raw_duration = float(
            n.duration.quarterLength
        )


        # 防止超長音

        if raw_duration > 1:
            raw_duration = 1


        duration = quantize_duration(
            raw_duration
        )


        remaining = duration



        while remaining > 0:


            space = 4 - beat


            length = min(
                remaining,
                space
            )


            new_note = note.Note(
                n.pitch
            )


            new_note.duration.quarterLength = length


            measure.append(
                new_note
            )


            beat += length
            remaining -= length



            # 完成小節

            if beat >= 4:


                new_part.append(
                    measure
                )


                measure_no += 1


                measure = stream.Measure(
                    number=measure_no
                )


                beat = 0



    # 補最後不足小節

    if beat > 0:

        rest = note.Rest()

        rest.duration.quarterLength = (
            4 - beat
        )

        measure.append(rest)


        new_part.append(
            measure
        )


    new_score.append(
        new_part
    )



print("寫入 MusicXML...")


new_score.write(
    "musicxml",
    fp=output_xml
)


print("================")
print("完成:")
print(output_xml)
print("================")