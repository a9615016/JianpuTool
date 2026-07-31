from pathlib import Path

p = Path("outputs/vocals.ly")

s = p.read_text(encoding="utf-8")

# 移除 unfoldRepeats 造成的錯誤區塊
s = s.replace("\\unfoldRepeats", "")

p.write_text(s, encoding="utf-8")

print("removed unfoldRepeats")