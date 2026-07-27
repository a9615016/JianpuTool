from music21 import converter, stream, note, meter
import sys


print("================")
print("CLEAN MUSICXML V26 BAR SAFE")
print("================")


src = sys.argv[1]

if len(sys.argv) >= 3:
    out = sys.argv[2]
else:
    out = "clean.musicxml"


print("read")

score = converter.parse(src)


print("remove voices")
for p in score.parts:
    for el in p.recurse():
        if hasattr(el, "voice"):
            el.voice = None


print("remove chords")
for p in score.parts:
    for ch in list(p.recurse().getElementsByClass("Chord")):
        n = ch.sortAscending().notes[0]
        ch.replace(ch, n)


print("force 4/4")

for p in score.parts:
    p.insert(0, meter.TimeSignature("4/4"))



print("rebuild measures")


newScore = stream.Score()


for p in score.parts:

    np = stream.Part()

    offset = 0


    for n in p.flatten().notesAndRests:

        dur = n.duration.quarterLength


        while dur > 0:

            beatPos = offset % 4

            remain = 4 - beatPos


            take = min(dur, remain)


            if isinstance(n, note.Rest):

                nn = note.Rest()

            else:

                nn = note.Note(
                    n.pitch
                )


            nn.duration.quarterLength = take

            np.insert(offset, nn)


            offset += take
            dur -= take


    newScore.append(np)



print("fill measures")


for p in newScore.parts:

    p.makeMeasures(
        inPlace=True
    )


print("FINAL CHECK")


for p in newScore.parts:

    for m in p.getElementsByClass("Measure"):

        q = m.duration.quarterLength

        print(
            "Measure",
            m.number,
            q
        )


print("WRITE")


newScore.write(
    "musicxml",
    fp=out
)


print("DONE")
print(out)