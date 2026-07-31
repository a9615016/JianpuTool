from pathlib import Path
import re

src = Path("outputs/vocals.ly")

text = src.read_text(encoding="utf-8")

# 移除 MIDI score
text = re.sub(
    r'% === BEGIN MIDI STAFF ===.*?% === END MIDI STAFF ===',
    '',
    text,
    flags=re.S
)

# 移除第二個 score 的 midi
text = re.sub(
    r'\\score\s*\{\s*\\unfoldRepeats.*?\\midi\s*\{.*?\}\s*\}',
    '',
    text,
    flags=re.S
)

# 移除 Global
text = text.replace(
    r'\Global',
    ''
)

# 移除錯誤 note-mod
text = re.sub(
    r'\\note-mod "\?\?"',
    '',
    text
)

# 修正 UTF-8
src.write_text(text, encoding="utf-8")

print("DONE")