# CLEAN MUSICXML V29
# JIANPU_LY FINAL BAR REPAIR


import sys
from music21 import converter
from music21 import stream
from music21 import note
from music21 import chord
from music21 import meter
from music21 import duration


print("================")
print("CLEAN MUSICXML V29")
print("FINAL BAR REPAIR")
print("================")


if len(sys.argv) < 3:
    print(
        "python clean_musicxml.py input.musicxml output.musicxml"
    )
    exit()


src = sys.argv[1]
dst = sys.argv[2]


print("read")

score = converter.parse(src)


clean = stream.Score()
part = stream.Part()


part.append(
    meter.TimeSignature("4/4")
)



print("remove voices")
print("remove chords")
print("remove ties")
print("remove beams")


def quantize_length(x):

    values = [
        0.25,
        0.5,
        1,
        2,
        4
    ]

    return min(
        values,
        key=lambda y:abs(y-x)
    )



events=[]


for n in score.flat.notesAndRests:


    if isinstance(n,chord.Chord):

        n=n.notes[0]


    n2=n.clone()


    q=float(
        n2.duration.quarterLength
    )


    q=quantize_length(q)


    n2.duration=duration.Duration(q)


    n2.tie=None


    events.append(n2)



print("rebuild measures")


current=0


for e in events:


    length=float(
        e.duration.quarterLength
    )


    # prevent over bar

    if current + length > 4:


        rest=note.Rest()

        rest.duration=duration.Duration(
            4-current
        )

        if current < 4:
            part.append(rest)


        current=0



    part.append(e)

    current += length



    if current == 4:

        current=0



# last bar fill

if current < 4 and current>0:

    r=note.Rest()

    r.duration=duration.Duration(
        4-current
    )

    part.append(r)



clean.append(part)



print("FINAL CHECK")


measures=clean.makeMeasures(
    inPlace=False
)


for i,m in enumerate(
    measures.parts[0].getElementsByClass("Measure"),
    1
):

    print(
        "Measure",
        i,
        float(m.duration.quarterLength)
    )



print("FINAL WRITE")


measures.write(
    "musicxml",
    fp=dst
)


print("DONE")
print(dst)