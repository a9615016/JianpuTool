from music21 import converter
import sys

score = converter.parse(sys.argv[1])

low = 200
high = 0
count = 0

for n in score.recurse().notes:
    if hasattr(n, "pitch"):
        p = n.pitch.midi
        low = min(low, p)
        high = max(high, p)
        count += 1

print("音符數:", count)
print("最低 MIDI:", low)
print("最高 MIDI:", high)