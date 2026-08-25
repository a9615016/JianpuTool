"""
key_detect.py - 精準版

功能：
1. 從原始 MP3/WAV 做多方法 BPM 偵測，避免 librosa 單次 beat_track
   出現 2 倍/0.5 倍 BPM。
2. 從 BasicPitch 人聲 MIDI 偵測調性。
3. 輸出 info.json 給後續量化使用。

注意：BPM 偵測是節奏估計，不可能對所有歌曲 100% 正確。
"""

import sys
import json
import os
import math

import librosa
from music21 import converter

DEFAULT_BPM = 120.0


def _scalar(x):
    try:
        return float(x[0])
    except Exception:
        return float(x)


def detect_tempo(audio_path):
    print("[3/6] 精準 BPM 偵測:", audio_path)

    y, sr = librosa.load(audio_path, sr=None, mono=True)

    if len(y) == 0:
        raise RuntimeError("音檔沒有可分析的音訊資料")

    # beat_track：主要候選
    tempo_bt, _ = librosa.beat.beat_track(y=y, sr=sr)
    tempo_bt = _scalar(tempo_bt)

    # onset 強度：第二個獨立候選
    onset = librosa.onset.onset_strength(y=y, sr=sr)
    tempo_onset = _scalar(librosa.feature.rhythm.tempo(
        onset_envelope=onset, sr=sr
    ))

    candidates = [x for x in (tempo_bt, tempo_onset) if math.isfinite(x) and x > 20]

    if not candidates:
        print("⚠ BPM 偵測失敗，使用 120 BPM")
        return DEFAULT_BPM

    # 找最接近兩個方法共識的候選。
    # 同時把 0.5x / 2x 倍頻關係拉回合理候選，降低半拍/雙拍錯誤。
    base = sum(candidates) / len(candidates)
    normalized = []

    for bpm in candidates:
        while bpm < 70:
            bpm *= 2
        while bpm > 180:
            bpm /= 2
        normalized.append(bpm)

    bpm = sum(normalized) / len(normalized)

    # 再從原始候選中找與共識最接近者；避免兩個方法差異太大時平均出奇怪值。
    best = min(normalized, key=lambda x: abs(x - bpm))

    print(
        f"[3/6] BPM 候選: beat_track={tempo_bt:.2f}, "
        f"onset={tempo_onset:.2f}, 採用≈{best:.2f}"
    )
    return float(best)


def detect_key(midi_path):
    print("[3/6] 偵測旋律調性:", midi_path)

    try:
        score = converter.parse(midi_path)

        # 優先使用旋律音符；BasicPitch 已經是人聲 MIDI。
        notes = list(score.recurse().notes)
        if not notes:
            raise RuntimeError("MIDI 沒有音符")

        k = score.analyze("key")

        print(f"[3/6] 偵測到調性: {k.tonic.name} {k.mode}")

        return {
            "tonic": k.tonic.name,
            "mode": k.mode
        }

    except Exception as e:
        print("[3/6] 調性偵測失敗，改用 C major:", e)
        return {"tonic": "C", "mode": "major"}


def main(original_audio, raw_midi, output_json):
    real_bpm = detect_tempo(original_audio)
    key_info = detect_key(raw_midi)

    info = {
        "real_bpm": real_bpm,
        "assumed_bpm": DEFAULT_BPM,
        "tempo_scale": real_bpm / DEFAULT_BPM,
        "key_tonic": key_info["tonic"],
        "key_mode": key_info["mode"],
        "tempo_method": "beat_track + onset_strength + half/double normalization"
    }

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)

    print("[3/6] 完成 ->", output_json)
    print(json.dumps(info, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("用法: python key_detect.py original_audio.mp3 raw_melody.mid info.json")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
