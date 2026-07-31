from pathlib import Path

p = Path("outputs/vocals.ly")

data = p.read_text(encoding="utf-16")

p.write_text(data, encoding="utf-8")

print("OK UTF-8")