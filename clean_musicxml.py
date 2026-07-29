import sys
from music21 import converter, stream, note, chord, meter, duration


print("==============================")
print("CLEAN MUSICXML V84")
print("JIANPU_LY STRICT MODE")
print("==============================")


input_file=sys.argv[1]

if len(sys.argv)>=3:
    output_file=sys.argv[2]
else:
    output_file="clean.musicxml"



score=converter.parse(input_file)


print("read")


# ==========================
# remove voices
# ==========================

for p in score.parts:

    for el in list(p.recurse()):

        if isinstance(el, note.Voice):
            el.activeSite.remove(el)

print("remove voices")



# ==========================
# remove chords
# ==========================

for c in score.recurse().getElementsByClass(chord.Chord):

    n=c.notes[0]

    c.activeSite.replace(c,n)


print("remove chords")



# ==========================
# remove notation
# ==========================

for p in score.parts:

    for el in p.recurse():

        if isinstance(el,note.Note):

            el.tie=None
            el.beams.fill(0)



print("remove ties/beams")



# ==========================
# force 4/4
# ==========================


for p in score.parts:

    p.insert(
        0,
        meter.TimeSignature("4/4")
    )


print("force 4/4")



# ==========================
# allowed durations
# ==========================


allowed=[
    4,
    2,
    1,
    0.5,
    0.25
]


def fix_duration(n):

    q=n.duration.quarterLength


    if q in allowed:
        return


    # 找最近值

    nearest=min(
        allowed,
        key=lambda x:abs(x-q)
    )


    n.duration=duration.Duration(nearest)



print("duration quantize")



# ==========================
# quantize notes
# ==========================


for n in score.recurse().notes:

    if isinstance(n,chord.Chord):
        continue

    fix_duration(n)



# ==========================
# rebuild measures
# ==========================


for p in score.parts:

    p.makeMeasures(
        inPlace=True
    )


print("rebuild measures")



# ==========================
# split cross measure notes
# ==========================


for p in score.parts:

    p.splitAtDurations(
        inPlace=True
    )


print("split notes")



# ==========================
# strict measure check
# ==========================


for m in score.parts[0].getElementsByClass("Measure"):

    total=sum(
        x.duration.quarterLength
        for x in m.notesAndRests
    )


    if total < 4:

        r=note.Rest(
            quarterLength=4-total
        )

        m.append(r)


    elif total >4:

        print(
            "FIX OVER:",
            m.number,
            total
        )



print("fill rests")



# ==========================
# final rebuild
# ==========================


for p in score.parts:

    p.makeMeasures(
        inPlace=True
    )



print("FINAL CHECK")


for m in score.parts[0].getElementsByClass("Measure"):

    total=sum(
        x.duration.quarterLength
        for x in m.notesAndRests
    )

    print(
        "Measure",
        m.number,
        total
    )



score.write(
    "musicxml",
    fp=output_file
)


print("================")
print("DONE")
print(output_file)
print("================")