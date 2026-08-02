from pathlib import Path
import sys

def fix_ly(filename):
    p = Path(filename)

    text = p.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    # 修改 LilyPond 版本
    text = text.replace(
        '\\version "2.20.0"',
        '\\version "2.26.0"'
    )

    # 移除第二個 MIDI score
    pos = text.find("\\score {\n\\unfoldRepeats")

    if pos != -1:
        text = text[:pos]

    p.write_text(
        text,
        encoding="utf-8",
        newline="\n"
    )

    print("FIX DONE", filename)

if __name__ == "__main__":
    fix_ly(sys.argv[1])