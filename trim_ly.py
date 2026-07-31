from pathlib import Path

p = Path("outputs/vocals.ly")

s = p.read_text(encoding="utf-8")

# 移除 MIDI / unfold 後面的錯誤區塊
pos = s.find("\\unfoldRepeats")

if pos != -1:
    s = s[:pos]

# 如果 unfold 已經刪掉，找殘留 MIDI 區塊
pos = s.find("<<")
if pos != -1:
    s = s[:pos]

p.write_text(s, encoding="utf-8")

print("trim done")