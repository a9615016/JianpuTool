"""
midi_to_musicxml.py

補回舊版 main.py 呼叫、但實際不存在的 "midi_to_musicxml_clean.py" 這一步。

跟舊的 final_quantize.py 不同的地方:
    - 不再對音符長度做「第二次量化」。量化已經在 melody_clean_quantize.py
      (MIDI 階段、且已用真實BPM校正)做完了,這裡如果再量化一次,
      量化格點不一致會讓節奏被二次破壞。
    - 會從 key_detect.py 產生的 info.json 讀取偵測到的調性,寫入
      MusicXML 的 <key> 標籤,讓 jianpu-ly 輸出正確的 "1=xx" 調號,
      而不是永遠假設 C 大調。

用法:
    python midi_to_musicxml.py input.mid output.musicxml [info.json]
"""

import sys
import json
import os

from music21 import converter, stream, meter, key as m21key


def load_key(info_json):

    if not info_json or not os.path.isfile(info_json):
        print("⚠ 找不到 info.json,MusicXML 調號預設為 C major")
        return m21key.Key("C", "major")

    with open(info_json, "r", encoding="utf-8") as f:
        info = json.load(f)

    tonic = info.get("key_tonic", "C")
    mode = info.get("key_mode", "major")

    print(f"✓ 套用偵測到的調性: {tonic} {mode}")

    return m21key.Key(tonic, mode)


def convert(input_midi, output_xml, info_json=None):

    print("[4/6] MIDI -> MusicXML:", input_midi)

    score = converter.parse(input_midi)

    detected_key = load_key(info_json)

    new_score = stream.Score()

    for part in score.parts:

        p = stream.Part()
        p.insert(0, meter.TimeSignature("4/4"))
        p.insert(0, detected_key)

        for n in part.recurse().notesAndRests:
            p.append(n)

        new_score.append(p)

    new_score = new_score.makeMeasures()

    new_score.write("musicxml", fp=output_xml)

    print("[4/6] 完成 ->", output_xml)


if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("用法: python midi_to_musicxml.py input.mid output.musicxml [info.json]")
        sys.exit(1)

    input_midi = sys.argv[1]
    output_xml = sys.argv[2]
    info_json = sys.argv[3] if len(sys.argv) > 3 else None

    convert(input_midi, output_xml, info_json)
