from pathlib import Path
import re

p = Path("outputs/vocals.ly")

s = p.read_text(encoding="utf-8")

# 移除第二個 MIDI score
pattern = r'\\score\s*\{\s*\\unfoldRepeats.*?\\midi\s*\{.*?\}\s*\}'

s = re.sub(pattern, '', s, flags=re.S)

# 如果標記存在，再移除
s = re.sub(
    r'% === BEGIN MIDI STAFF ===.*?% === END MIDI STAFF ===',
    '',
    s,
    flags=re.S
)

p.write_text(s, encoding="utf-8")

print("MIDI removed")