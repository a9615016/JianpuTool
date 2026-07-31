src = Path("outputs/vocals.ly")
data = src.read_text(encoding="utf-16")

src.write_text(data, encoding="utf-8")

print("Converted to UTF-8")