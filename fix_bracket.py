from pathlib import Path

p = Path("outputs/vocals.ly")

s = p.read_text(encoding="utf-8")

# 修正多餘的 r 後括號
s = s.replace(
    'r4  r4  r4  r4 }  \\note-mod "0" r4',
    'r4  r4  r4  r4  \\note-mod "0" r4'
)

# 移除最後多餘 }
while s.rstrip().endswith("} }"):
    s = s.rstrip()[:-3] + "\n"

p.write_text(s, encoding="utf-8")

print("bracket fixed")