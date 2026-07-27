import os
import sys
from music21 import converter, stream


def midi_to_musicxml(input_file, output_file=None):

    print("開始 MIDI → MusicXML")
    print("輸入:", input_file)

    if not os.path.exists(input_file):
        raise FileNotFoundError(input_file)

    if output_file is None:
        output_file = os.path.splitext(input_file)[0] + ".musicxml"

    print("讀取 MIDI...")

    score = converter.parse(input_file)

    print("重新整理樂譜...")

    score = score.flatten()

    score = score.makeMeasures()

    score.makeAccidentals(inPlace=True)

    print("寫入 MusicXML...")

    score.write(
        "musicxml",
        fp=output_file
    )

    print("完成:")
    print(output_file)


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("python midi_to_musicxml.py input.mid output.musicxml")
        sys.exit(1)

    output = None
    if len(sys.argv) >= 3:
        output = sys.argv[2]

    midi_to_musicxml(
        sys.argv[1],
        output
    )