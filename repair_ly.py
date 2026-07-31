from pathlib import Path

p = Path("outputs/vocals.ly")

s = p.read_text(encoding="utf-8")


# 修正 jianpu-ly 產生的亂碼 note
s = s.replace(r'\note-mod "?? ', '')


# 移除 MIDI score
a = s.find("% === BEGIN MIDI STAFF ===")
b = s.find("% === END MIDI STAFF ===")

if a >= 0 and b >= 0:
    s = s[:a] + s[b + len("% === END MIDI STAFF ==="):]


# 修正三點符號
s = s.replace(
    '"?? #',
    '"... #"'
)


p.write_text(
    s,
    encoding="utf-8"
)

print("repair done")