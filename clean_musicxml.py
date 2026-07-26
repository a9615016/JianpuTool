import sys
import music21
from music21 import converter, stream, note, chord, meter, duration


print("CLEAN MUSICXML V2")


if len(sys.argv) < 3:
    print(
        "usage: python clean_musicxml.py input.musicxml output.musicxml"
    )
    sys.exit(1)


input_file = sys.argv[1]
output_file = sys.argv[2]


print("input:")
print(input_file)

print("output:")
print(output_file)



print("讀取 MusicXML")

score = converter.parse(input_file)



print("移除 voices / chords")


# 只保留第一個 part
if len(score.parts) > 0:
    part = score.parts[0]
else:
    part = score



new_part = stream.Part()


# 強制4/4
ts = meter.TimeSignature("4/4")
new_part.insert(0, ts)



print("開始清理")


current_measure = stream.Measure(
    number=1
)

current_time = 0.0

BAR_LENGTH = 4.0



for element in part.flatten().notesAndRests:


    # chord取最高音
    if isinstance(element, chord.Chord):

        n = note.Note(
            element.pitch
        )

        n.duration = element.duration


        element = n



    # 修正 duration
    ql = element.duration.quarterLength


    if ql <= 0:
        continue



    # quantize

    allowed = [
        0.25,
        0.5,
        0.75,
        1,
        1.5,
        2,
        3,
        4
    ]


    closest = min(
        allowed,
        key=lambda x: abs(x-ql)
    )


    element.duration = duration.Duration(
        closest
    )



    # 超過小節切割

    if current_time + closest > BAR_LENGTH:


        # 補休止

        remain = BAR_LENGTH-current_time


        if remain > 0:

            r = note.Rest(
                quarterLength=remain
            )

            current_measure.append(r)



        new_part.append(
            current_measure
        )


        current_measure = stream.Measure(
            number=current_measure.number+1
        )

        current_time = 0



    current_measure.append(
        element
    )


    current_time += closest



# 最後補滿

if current_time < BAR_LENGTH:


    r = note.Rest(
        quarterLength=BAR_LENGTH-current_time
    )

    current_measure.append(r)



new_part.append(
    current_measure
)



new_score = stream.Score()

new_score.insert(
    0,
    new_part
)



print("寫入 MusicXML")

new_score.write(
    "musicxml",
    fp=output_file
)



print("完成:")
print(output_file)