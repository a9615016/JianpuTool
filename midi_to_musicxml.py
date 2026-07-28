# midi_to_musicxml_v3.py
# Jianpu Stable Version
# MIDI -> MusicXML
# For jianpu_ly compatibility

import sys
from music21 import converter
from music21 import stream
from music21 import note
from music21 import meter
from music21 import tempo
from music21 import instrument


# 小於這個長度的音刪除
MIN_DURATION = 0.125

# 16分音符量化
QUANTIZE = 0.25


def quantize(value):
    """
    四捨五入到 16 分音符
    """
    return round(value / QUANTIZE) * QUANTIZE



def rebuild_melody(src):

    score = stream.Score()

    part = stream.Part()

    # 固定樂器
    part.insert(
        0,
        instrument.Piano()
    )

    # 固定 4/4
    part.append(
        meter.TimeSignature("4/4")
    )

    # 固定速度
    part.insert(
        0,
        tempo.MetronomeMark(
            number=120
        )
    )


    melody = []


    print("extract notes")


    for n in src.flat.notes:

        # 只接受單音
        if not isinstance(n, note.Note):
            continue


        dur = n.duration.quarterLength


        # 太短音符移除
        if dur < MIN_DURATION:
            continue


        new_note = note.Note(
            n.pitch
        )


        # duration quantize
        new_duration = quantize(dur)


        if new_duration <= 0:
            new_duration = QUANTIZE


        new_note.duration.quarterLength = (
            new_duration
        )


        # offset quantize
        new_offset = quantize(
            n.offset
        )


        melody.append(
            (
                new_offset,
                new_note
            )
        )


    # 排序
    melody.sort(
        key=lambda x:x[0]
    )


    print(
        "notes:",
        len(melody)
    )


    # 寫入單聲部
    for offset, n in melody:

        part.insert(
            offset,
            n
        )


    # 補滿最後小節
    total = part.duration.quarterLength

    remain = total % 4


    if remain != 0:

        rest = note.Rest()

        rest.duration.quarterLength = (
            4 - remain
        )

        part.append(
            rest
        )


    score.append(
        part
    )


    return score



def main():

    if len(sys.argv) < 3:

        print(
            "Usage:"
        )

        print(
            "python midi_to_musicxml_v3.py input.mid output.musicxml"
        )

        return



    midi_file = sys.argv[1]

    output_file = sys.argv[2]


    print("====================")
    print("MIDI TO MUSICXML V3")
    print("JIANPU STABLE")
    print("====================")


    print(
        "input:",
        midi_file
    )


    print(
        "read MIDI..."
    )


    midi = converter.parse(
        midi_file
    )


    print(
        "rebuild melody..."
    )


    score = rebuild_melody(
        midi
    )


    print(
        "write MusicXML..."
    )


    score.write(
        "musicxml",
        fp=output_file
    )


    print(
        "DONE:"
    )

    print(
        output_file
    )



if __name__ == "__main__":
    main()