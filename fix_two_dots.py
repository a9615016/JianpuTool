from pathlib import Path

p = Path("outputs/vocals.ly")

s = p.read_text(encoding="utf-8")

insert = r'''
two-dots =
#(make-articulation 'two-dots)

three-dots =
#(make-articulation 'three-dots)

'''

# 放在 note-mod 定義後面
pos = s.find("note-mod =")

if pos != -1:
    end = s.find("#(define-event-class", pos)
    s = s[:end] + insert + s[end:]
else:
    s = insert + s

p.write_text(s, encoding="utf-8")

print("two-dots restored")