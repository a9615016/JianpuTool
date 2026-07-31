from pathlib import Path

p = Path("outputs/vocals.ly")

s = p.read_text(encoding="utf-8")

# 移除亂碼文字 markup
s = s.replace('"??', '""')

p.write_text(s, encoding="utf-8")

print("fixed text")