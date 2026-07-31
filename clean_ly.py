from pathlib import Path
import re

p = Path("outputs/vocals.ly")

s = p.read_text(encoding="utf-8")

# 移除 MIDI score
s = re.sub(
    r'\\score\s*\{\s*\\unfoldRepeats.*?\\midi\s*\{.*?\}\s*\}',
    '',
    s,
    flags=re.S
)

# 移除空 MIDI staff
s = re.sub(
    r'% === BEGIN MIDI STAFF ===.*?% === END MIDI STAFF ===',
    '',
    s,
    flags=re.S
)

# 移除 Global
s = s.replace("\\Global", "")

# 修正 jianpu-ly 舊語法
repls = {
"Stem #'direction": "Stem.direction",
"Tie #'staff-position": "Tie.staff-position",
"Stem #'length-fraction": "Stem.length-fraction",
"Beam #'beam-thickness": "Beam.beam-thickness",
"Beam #'length-fraction": "Beam.length-fraction",
"Voice.Rest #'style": "Voice.Rest.style",
"Accidental #'font-size": "Accidental.font-size",
"TupletBracket #'bracket-visibility": "TupletBracket.bracket-visibility",
"Staff.TimeSignature #'style": "Staff.TimeSignature.style",
"Staff.Stem #'transparent": "Staff.Stem.transparent",
}

for a,b in repls.items():
    s=s.replace(a,b)


# 移除所有 ?? 
s=re.sub(r'"\\?\\?.*?"','""',s)

p.write_text(s,encoding="utf-8")

print("clean ok")