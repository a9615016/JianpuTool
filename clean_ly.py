from pathlib import Path

src = Path("outputs/vocals.ly")

text = src.read_text(encoding="utf-8")

# 1. 移除錯誤 note-mod 亂碼
text = text.replace(r'\note-mod "?? ', '')

# 2. 修正 three-dots 亂碼
text = text.replace(
    r'\center-align \bold "?? #',
    r'\center-align \bold "... " #'
)

# 3. 移除 MIDI block
start = text.find("% === BEGIN MIDI STAFF ===")

if start != -1:
    end = text.find("% === END MIDI STAFF ===")

    if end != -1:
        end = end + len("% === END MIDI STAFF ===")
        text = text[:start] + text[end:]


# 4. 修正被破壞的 grobdescriptions
text = text.replace(
    r'\grobdescriptions\"',
    r'\grobdescriptions'
)

# 5. 修正可能破壞的 quote
text = text.replace(
    r'\consists " Accidental_engraver"',
    r'\consists "Accidental_engraver"'
)


out = Path("outputs/vocals_clean.ly")
out.write_text(text, encoding="utf-8")

print("saved:", out)