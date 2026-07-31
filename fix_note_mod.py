from pathlib import Path

p = Path("outputs/vocals.ly")

s = p.read_text(encoding="utf-8")

# 移除損壞的 note-mod
s = s.replace(r'\note-mod "?? ', '')

# 保留正常的 note-mod
s = s.replace(r'\note-mod "0" ', '')

p.write_text(s, encoding="utf-8")

print("fixed note-mod")