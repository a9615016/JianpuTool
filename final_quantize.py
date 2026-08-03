from music21 import converter, stream, meter, duration, note
import sys

src=sys.argv[1]
out=sys.argv[2]

score=converter.parse(src)

newScore=stream.Score()

for part in score.parts:

    p=stream.Part()
    p.insert(0, meter.TimeSignature("4/4"))

    current=0

    for n in part.recurse().notes:

        q=n.duration.quarterLength

        # 量化
        if q <= 0.25:
            q=0.25
        elif q <=0.5:
            q=0.5
        elif q<=1:
            q=1
        elif q<=2:
            q=2
        else:
            q=4

        # 超過小節先補滿
        if current + q > 4:
            rest_len = 4-current
            if rest_len > 0:
                r=note.Rest()
                r.duration=duration.Duration(rest_len)
                p.append(r)

            current=0


        nn=n
        nn.duration=duration.Duration(q)
        nn.tie=None

        p.append(nn)

        current += q

        if current == 4:
            current=0


    # 最後補滿
    if current>0:
        r=note.Rest()
        r.duration=duration.Duration(4-current)
        p.append(r)


    newScore.append(p)


newScore=newScore.makeMeasures()

newScore.write(
    "musicxml",
    fp=out
)

print("DONE",out)