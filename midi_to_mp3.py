"""
midi_to_mp3.py — 簡譜/旋律 MIDI -> MP3 合成器

補上 JianpuTool 原本沒有的「反向」流程：
    clean_melody.mid / score.mid (人聲主旋律 MIDI)
        -> [本檔案] 合成音訊
        -> WAV
        -> ffmpeg 轉檔
        -> MP3

因為部署環境不一定能安裝 FluidSynth / 下載 SoundFont，
這裡用 numpy 自己做一個「有泛音 + 包絡」的人聲/樂器音色，
不依賴任何外部音色檔，純 Python + numpy + ffmpeg 即可跑。

用法（命令列）：
    python midi_to_mp3.py clean_melody.mid output.mp3
    python midi_to_mp3.py clean_melody.mid output.mp3 --voice piano
    python midi_to_mp3.py clean_melody.mid output.mp3 --voice "la"

用法（當模組匯入）：
    from midi_to_mp3 import render_mp3
    render_mp3("clean_melody.mid", "song.mp3", voice="piano")
"""

import os
import io
import struct
import subprocess
import sys

import numpy as np
from scipy.io import wavfile


SAMPLE_RATE = 44100


# ============================================================
# 1) 極簡 Standard MIDI File (SMF) 解析器
#    只讀我們自己流程會用到的事件：
#    - Set Tempo (FF 51 03)
#    - Note On / Note Off (含 velocity=0 視為 note off)
#    - 支援 running status
# ============================================================

def _read_varlen(data, pos):
    value = 0
    while True:
        byte = data[pos]
        pos += 1
        value = (value << 7) | (byte & 0x7F)
        if not (byte & 0x80):
            break
    return value, pos


def parse_midi(path):
    """
    回傳: (notes, ticks_per_beat)
    notes = list of dict: {pitch, start_sec, end_sec, velocity}
    """
    with open(path, "rb") as f:
        data = f.read()

    if data[:4] != b"MThd":
        raise ValueError(f"不是合法的 MIDI 檔: {path}")

    header_len = struct.unpack(">I", data[4:8])[0]
    fmt, n_tracks, division = struct.unpack(">HHH", data[8:8 + header_len])

    if division & 0x8000:
        raise ValueError("暫不支援 SMPTE time division 的 MIDI")

    ticks_per_beat = division

    pos = 8 + header_len

    tempo_events = []       # (abs_tick, microseconds_per_beat)
    raw_note_events = []    # (abs_tick, type, channel, pitch, velocity)

    for _ in range(n_tracks):
        if data[pos:pos + 4] != b"MTrk":
            raise ValueError("MIDI track chunk 損毀")
        track_len = struct.unpack(">I", data[pos + 4:pos + 8])[0]
        track_end = pos + 8 + track_len
        pos += 8

        abs_tick = 0
        running_status = None

        while pos < track_end:
            delta, pos = _read_varlen(data, pos)
            abs_tick += delta

            status = data[pos]

            if status < 0x80:
                # running status：重用上一個 status byte，這個 byte 其實是資料
                if running_status is None:
                    raise ValueError("MIDI running status 遺失")
                status = running_status
            else:
                pos += 1
                running_status = status if status < 0xF0 else running_status

            if status == 0xFF:
                # Meta event
                meta_type = data[pos]
                pos += 1
                length, pos = _read_varlen(data, pos)
                meta_data = data[pos:pos + length]
                pos += length

                if meta_type == 0x51 and length == 3:
                    us_per_beat = (meta_data[0] << 16) | (meta_data[1] << 8) | meta_data[2]
                    tempo_events.append((abs_tick, us_per_beat))
                elif meta_type == 0x2F:
                    pass  # End of track

            elif status in (0xF0, 0xF7):
                length, pos = _read_varlen(data, pos)
                pos += length

            else:
                event_type = status & 0xF0
                channel = status & 0x0F

                if event_type in (0x80, 0x90):  # note off / note on
                    pitch = data[pos]
                    velocity = data[pos + 1]
                    pos += 2
                    kind = "on" if (event_type == 0x90 and velocity > 0) else "off"
                    raw_note_events.append((abs_tick, kind, channel, pitch, velocity))
                elif event_type in (0xA0, 0xB0, 0xE0):  # aftertouch / CC / pitch bend
                    pos += 2
                elif event_type in (0xC0, 0xD0):  # program change / channel pressure
                    pos += 1
                else:
                    pos += 2

        pos = track_end

    if not tempo_events:
        tempo_events = [(0, 500000)]  # 預設 120 BPM
    tempo_events.sort(key=lambda x: x[0])

    def tick_to_sec(tick):
        sec = 0.0
        last_tick = 0
        last_us = tempo_events[0][1]
        for ev_tick, us in tempo_events:
            if ev_tick >= tick:
                break
            sec += (ev_tick - last_tick) * last_us / 1_000_000.0 / ticks_per_beat
            last_tick = ev_tick
            last_us = us
        sec += (tick - last_tick) * last_us / 1_000_000.0 / ticks_per_beat
        return sec

    raw_note_events.sort(key=lambda x: x[0])

    active = {}
    notes = []
    for abs_tick, kind, channel, pitch, velocity in raw_note_events:
        key = (channel, pitch)
        t = tick_to_sec(abs_tick)
        if kind == "on":
            active[key] = (t, velocity)
        else:
            if key in active:
                start_sec, vel = active.pop(key)
                if t > start_sec:
                    notes.append({
                        "pitch": pitch,
                        "start_sec": start_sec,
                        "end_sec": t,
                        "velocity": vel,
                    })

    notes.sort(key=lambda n: n["start_sec"])
    return notes, ticks_per_beat


# ============================================================
# 2) 簡單但聽起來不刺耳的合成器
#    每個音符 = 基音 + 數個泛音（依 voice 調整權重）+ ADSR 包絡
# ============================================================

VOICE_PRESETS = {
    # 泛音權重 (相對於基音的倍頻), attack/decay/sustain/release (秒)
    "piano":  {"harmonics": [1.0, 0.55, 0.30, 0.18, 0.10, 0.06], "adsr": (0.008, 0.12, 0.55, 0.18), "vibrato": 0.0},
    "la":     {"harmonics": [1.0, 0.45, 0.55, 0.20, 0.12, 0.05], "adsr": (0.03, 0.08, 0.80, 0.15), "vibrato": 5.5},
    "flute":  {"harmonics": [1.0, 0.15, 0.08, 0.04], "adsr": (0.05, 0.05, 0.85, 0.12), "vibrato": 5.0},
    "strings": {"harmonics": [1.0, 0.5, 0.35, 0.2, 0.12, 0.08, 0.05], "adsr": (0.08, 0.10, 0.85, 0.25), "vibrato": 4.5},
}


def _midi_pitch_to_hz(pitch):
    return 440.0 * (2.0 ** ((pitch - 69) / 12.0))


def _adsr_envelope(n_samples, sr, attack, decay, sustain_level, release):
    env = np.ones(n_samples, dtype=np.float64)
    a = int(attack * sr)
    d = int(decay * sr)
    r = int(release * sr)
    a = min(a, n_samples)
    d = min(d, max(n_samples - a, 0))
    r = min(r, n_samples)

    if a > 0:
        env[:a] = np.linspace(0.0, 1.0, a)
    if d > 0:
        env[a:a + d] = np.linspace(1.0, sustain_level, d)
    sustain_end = max(a + d, 0)
    if sustain_end < n_samples - r:
        env[sustain_end:n_samples - r] = sustain_level
    if r > 0:
        start = max(n_samples - r, sustain_end)
        cur_val = env[start - 1] if start > 0 else sustain_level
        env[start:] = np.linspace(cur_val, 0.0, n_samples - start)
    return env


def synth_note(pitch, duration_sec, velocity, voice="piano", sr=SAMPLE_RATE):
    preset = VOICE_PRESETS.get(voice, VOICE_PRESETS["piano"])
    freq = _midi_pitch_to_hz(pitch)

    # 音符實際發聲時間比拍值稍短一點點，避免相鄰音黏在一起（legato 感太重）
    n_samples = max(int(duration_sec * sr), 1)
    t = np.arange(n_samples) / sr

    vibrato_hz = preset["vibrato"]
    if vibrato_hz > 0:
        vibrato_depth = 0.006  # 半音以內的輕微抖音
        freq_mod = freq * (1.0 + vibrato_depth * np.sin(2 * np.pi * vibrato_hz * t))
        phase = 2 * np.pi * np.cumsum(freq_mod) / sr
    else:
        phase = 2 * np.pi * freq * t

    signal = np.zeros(n_samples, dtype=np.float64)
    for i, weight in enumerate(preset["harmonics"]):
        harmonic_n = i + 1
        signal += weight * np.sin(harmonic_n * phase)

    signal /= sum(preset["harmonics"])

    attack, decay, sustain_level, release = preset["adsr"]
    env = _adsr_envelope(n_samples, sr, attack, decay, sustain_level, release)
    signal *= env

    gain = 0.15 + 0.55 * (velocity / 127.0)
    signal *= gain

    return signal


def render_mp3(midi_path, mp3_path, voice="piano", tail_sec=1.0, mp3_bitrate="192k"):
    """
    把 MIDI 檔渲染成 MP3。

    voice 可選: "piano" / "la" (哼唱人聲) / "flute" / "strings"
    """
    notes, _ = parse_midi(midi_path)

    if not notes:
        raise ValueError(f"這個 MIDI 檔沒有任何音符: {midi_path}")

    total_len_sec = max(n["end_sec"] for n in notes) + tail_sec
    n_total_samples = int(total_len_sec * SAMPLE_RATE) + 1
    mix = np.zeros(n_total_samples, dtype=np.float64)

    for note in notes:
        start_sample = int(note["start_sec"] * SAMPLE_RATE)
        duration = max(note["end_sec"] - note["start_sec"], 0.05)
        wave = synth_note(note["pitch"], duration, note["velocity"], voice=voice)
        end_sample = start_sample + len(wave)
        if end_sample > len(mix):
            wave = wave[: len(mix) - start_sample]
            end_sample = len(mix)
        mix[start_sample:end_sample] += wave

    # 正規化避免爆音 (leave headroom)
    peak = np.max(np.abs(mix)) if np.max(np.abs(mix)) > 0 else 1.0
    mix = mix / peak * 0.9

    pcm16 = (mix * 32767).astype(np.int16)

    wav_path = os.path.splitext(mp3_path)[0] + "_tmp.wav"
    wavfile.write(wav_path, SAMPLE_RATE, pcm16)

    cmd = [
        "ffmpeg", "-y",
        "-i", wav_path,
        "-codec:a", "libmp3lame",
        "-b:a", mp3_bitrate,
        mp3_path,
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    os.remove(wav_path)

    if result.returncode != 0 or not os.path.exists(mp3_path):
        raise RuntimeError(f"ffmpeg 轉檔失敗:\n{result.stdout}")

    return mp3_path


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python midi_to_mp3.py input.mid output.mp3 [--voice piano|la|flute|strings]")
        sys.exit(1)

    midi_in = sys.argv[1]
    mp3_out = sys.argv[2]
    voice = "piano"

    if "--voice" in sys.argv:
        voice = sys.argv[sys.argv.index("--voice") + 1]

    out = render_mp3(midi_in, mp3_out, voice=voice)
    print(f"✅ 完成: {out}")
