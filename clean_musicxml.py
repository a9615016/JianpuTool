from music21 import converter, stream, note, chord, meter, duration
import sys
import copy


print("================")
print("CLEAN MUSICXML V25 JIANPU FINAL")
print("================")


def remove_bad_elements(score):

    print("remove voices")
    for el in score.recurse():
        if hasattr(el, "voice"):
            try:
                el.voice = None
            except:
                pass


    print("remove chords")
    for c in score.recurse().getElementsByClass(chord.Chord):
        if len(c.pitches) > 0:
            n = note.Note(c.pitches[0])
            n.duration = copy.deepcopy(c.duration)
            c.activeSite.replace(c, n)


    print("remove beams")
    for n in score.recurse().notes:
        try:
            n.beams = []
        except:
            pass


    print("remove ties")
    for n in score.recurse().notes:
        try:
            n.tie = None
        except:
            pass



def force_44(score):

    print("force 4/4")

    for p in score.parts:
        p.insert(0, meter.TimeSignature("4/4"))



def quantize_duration(score):

    print("duration quantize")

    allowed = [
        4.0,
        2.0,
        1.0,
        0.5,
        0.25
    ]

    for n in score.recurse().notes:

        q = n.duration.quarterLength

        closest = min(
            allowed,
            key=lambda x:abs(x-q)
        )

        n.duration = duration.Duration(closest)



def rebuild_measures(score):

    print("rebuild measures")

    for p in score.parts:

        p.makeMeasures(inPlace=True)



def split_cross_measure(score):

    print("split cross measure notes")

    for p in score.parts:

        for n in list(p.recurse().notes):

            try:

                if n.duration.quarterLength > 4:

                    remain = n.duration.quarterLength

                    n.duration = duration.Duration(4)

                    remain -= 4

                    while remain > 0:

                        nn = copy.deepcopy(n)

                        d=min(remain,4)

                        nn.duration=duration.Duration(d)

                        p.append(nn)

                        remain-=d

            except:
                pass



def fill_rests(score):

    print("fill measure rest")

    for m in score.recurse().getElementsByClass('Measure'):

        total=sum(
            n.duration.quarterLength
            for n in m.notesAndRests
        )

        diff=4-total

        if diff>0:

            r=note.Rest()

            r.duration=duration.Duration(diff)

            m.append(r)



def final_check(score):

    print("FINAL CHECK")

    for i,m in enumerate(
        score.recurse().getElementsByClass('Measure'),
        1
    ):

        total=sum(
            n.duration.quarterLength
            for n in m.notesAndRests
        )

        print(
            "Measure",
            i,
            total
        )

        if abs(total-4)>0.01:

            print(
                "WARNING",
                i,
                total
            )



def main():

    inp=sys.argv[1]
    out=sys.argv[2]


    print("read")

    score=converter.parse(inp)


    remove_bad_elements(score)

    force_44(score)

    quantize_duration(score)

    rebuild_measures(score)

    split_cross_measure(score)

    rebuild_measures(score)

    fill_rests(score)

    rebuild_measures(score)


    print("clear notation cache")

    final_check(score)


    print("FINAL WRITE")

    score.write(
        "musicxml",
        fp=out
    )


    print("DONE")
    print(out)



if __name__=="__main__":

    main()