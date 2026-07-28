# CLEAN MUSICXML V35
# FORCE JIANPU SAFE MODE

import sys
from music21 import converter, stream, note, chord, meter, duration


print("================")
print("CLEAN MUSICXML V35")
print("FORCE SPLIT LONG NOTES")
print("================")


src = sys.argv[1]
dst = sys.argv[2]


score = converter.parse(src)

print("read")


# remove voices
print("remove voices")
for p in score.parts:
    for e in list(p.recurse()):
        if hasattr(e, "voices"):
            try:
                e.voices = []
            except:
                pass


# remove chords
print("remove chords")
for p in score.parts:
    for c in list(p.recurse().getElementsByClass(chord.Chord)):
        n = note.Note(c.root())
        n.duration = c.duration
        c.activeSite.replace(c, n)


# remove ties
print("remove ties")
for n in score.recurse().notes:
    n.tie = None


# remove beams
print("remove beams")
for n in score.recurse().notes:
    try:
        n.beams = []
    except:
        pass


# force 4/4
print("force 4/4")

for p in score.parts:
    p.insert(0, meter.TimeSignature("4/4"))


# split long notes
print("split long notes")

for p in score.parts:

    new = stream.Part()

    for n in p.recurse().notesAndRests:

        q = n.duration.quarterLength


        # 最大一拍
        while q > 1:

            x = n.clone()

            x.duration = duration.Duration(1)

            new.append(x)

            q -= 1


        if q > 0:

            x = n.clone()

            x.duration.quarterLength = q

            new.append(x)


    p.clear()
    p.append(new)


# rebuild measures
print("rebuild measures")

score.makeMeasures(inPlace=True)


# force measure length
print("force measure length")


for m in score.recurse().getElementsByClass(stream.Measure):

    total = sum(
        x.duration.quarterLength
        for x in m.notesAndRests
    )


    if total < 4:

        r = note.Rest()

        r.duration.quarterLength = 4-total

        m.append(r)


    elif total > 4:

        print(
            "truncate measure",
            m.number,
            total
        )

        remain = 4

        items=[]

        for x in m.notesAndRests:

            if remain <=0:
                break

            q=min(
                x.duration.quarterLength,
                remain
            )

            x.duration.quarterLength=q

            items.append(x)

            remain-=q


        if remain>0:
            r=note.Rest()
            r.duration.quarterLength=remain
            items.append(r)


        m.removeByClass(
            ['Note','Rest']
        )

        for x in items:
            m.append(x)



print("FINAL CHECK")


for m in score.recurse().getElementsByClass(stream.Measure):

    length=sum(
        x.duration.quarterLength
        for x in m.notesAndRests
    )

    print(
        "Measure",
        m.number,
        length
    )


print("FINAL WRITE")

score.write(
    "musicxml",
    fp=dst
)


print("DONE")
print(dst)