#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
clean_musicxml.py
V80 TRUE ABSOLUTE GRID ENGINE

MIDI/MusicXML -> Jianpu compatible MusicXML
"""

import sys
from music21 import converter, stream, meter, note, chord, duration


print("================")
print("CLEAN MUSICXML V80 TRUE ABSOLUTE GRID ENGINE")
print("================")


if len(sys.argv) < 2:
    print("usage:")
    print("python clean_musicxml.py input.musicxml output.musicxml")
    sys.exit()


input_file = sys.argv[1]

if len(sys.argv) >= 3:
    output_file = sys.argv[2]
else:
    output_file = "clean.musicxml"


print("read")

score = converter.parse(input_file)


# -------------------------
# remove voices
# -------------------------
print("remove voices")

for p in score.parts:
    for el in list(p.recurse()):
        if hasattr(el, "voice"):
            try:
                el.voice = None
            except:
                pass


# -------------------------
# remove chords
# -------------------------
print("remove chords")

for p in score.parts:
    for c in list(p.recurse().getElementsByClass(chord.Chord)):
        notes = c.notes

        if len(notes):
            n = notes[0]
            c.activeSite.replace(c, n)


# -------------------------
# remove notation
# -------------------------
print("remove beams")
print("remove ties")

for n in score.recurse().notes:

    try:
        n.beams = []
    except:
        pass

    try:
        n.tie = None
    except:
        pass


# -------------------------
# force 4/4
# -------------------------
print("force 4/4")

for p in score.parts:
    p.insert(
        0,
        meter.TimeSignature("4/4")
    )


# =========================
# V80 ABSOLUTE GRID ENGINE
# =========================

print("absolute offset quantize")

GRID = 0.25


def quantize(value):
    return round(float(value) / GRID) * GRID


for p in score.parts:

    for n in p.recurse().notesAndRests:

        # offset snap
        try:
            n.offset = quantize(n.offset)
        except:
            pass


print("absolute duration quantize")


valid = [
    4.0,
    2.0,
    1.0,
    0.5,
    0.25
]


def nearest_duration(x):

    return min(
        valid,
        key=lambda y: abs(y-x)
    )


for n in score.recurse().notes:

    q = nearest_duration(
        float(n.duration.quarterLength)
    )

    n.duration = duration.Duration(q)



# -------------------------
# rebuild measures
# -------------------------

print("rebuild measures")


new_score = stream.Score()


for part in score.parts:

    new_part = stream.Part()

    for n in part.recurse().notesAndRests:

        new_part.append(n)

    new_score.append(new_part)


score = new_score



# -------------------------
# split cross measure notes
# -------------------------

print("split cross measure notes")


for p in score.parts:

    try:
        p.makeMeasures(
            inPlace=True
        )
    except:
        pass



# -------------------------
# fill rests
# -------------------------

print("fill measure rest")


for p in score.parts:

    for m in p.getElementsByClass("Measure"):

        try:
            m.makeRests(
                inPlace=True
            )
        except:
            pass



# -------------------------
# final rebuild
# -------------------------

print("rebuild measures")

for p in score.parts:
    try:
        p.makeMeasures(
            inPlace=True
        )
    except:
        pass



print("clear notation cache")


# -------------------------
# FINAL CHECK
# -------------------------

print("FINAL CHECK")


safe = True


for p in score.parts:

    for m in p.getElementsByClass("Measure"):

        total = 0

        for n in m.notesAndRests:
            total += float(
                n.duration.quarterLength
            )

        print(
            "Measure",
            m.number,
            total
        )


        if abs(total-4.0) > 0.001:
            safe = False



if safe:

    print("ALL MEASURES SAFE")

else:

    print("WARNING measure mismatch")



print("FINAL WRITE")


score.write(
    "musicxml",
    fp=output_file
)


print("DONE")
print(output_file)