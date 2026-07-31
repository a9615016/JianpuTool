from pathlib import Path
import re

p = Path("outputs/vocals.ly")

s = p.read_text(encoding="utf-8")

# 移除 note-mod "?? 
s = re.sub(
    r'\\note-mod "\?\?[^\n]*?r\d+',
    'r4',
    s
)

# 移除剩餘錯誤文字
s = s.replace('"??', '""')

p.write_text(s, encoding="utf-8")

print("fixed bad notes")