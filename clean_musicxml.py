from music21 import converter, stream, note, chord, meter
import sys
import copy


print("================")
print("CLEAN MUSICXML V28 JIANPU BARCHECK FIX")
print("================")


def clean_score(src, dst):

    print("read")
    score = converter.parse(src)


    print("flatten")
    flat = score.flatten()


    print("remove voices")
    for el in flat.recurse():
        if hasattr(el, "voice"):
            try:
                el.voice = None
            except:
                pass


    print("remove chords")
    notes = []

    for n in flat.notesAndRests:

        if isinstance(n, chord.Chord):
            # chord只取最高音
            nn = note.Note(n.sortAscending().notes[-1].pitch)
            nn.duration = copy.deepcopy(n.duration)
            notes.append(nn)

        else:
            notes.append(n)


    print("create new score")

    new_score = stream.Score()
    part = stream.Part()

    part.append(meter.TimeSignature("4/4"))


    print("quantize duration")

    allowed = [
        0.25,
        0.5,
        0.75,
        1,
        1.5,
        2,
        3,
        4
    ]


    for n in notes:

        q = float(n.duration.quarterLength)

        # 找最近值
        q2=min(
            allowed,
            key=lambda x:abs(x-q)
        )


        n.duration.quarterLength=q2


        # remove tie
        if hasattr(n,"tie"):
            n.tie=None


        # remove lyric
        try:
            n.lyric=None
        except:
            pass


        part.append(n)



    print("rebuild measures")


    measures = stream.makeMeasures(part)


    print("split cross measure notes")

    measures.makeNotation(
        inPlace=True
    )


    print("fill measure rest")


    for m in measures.getElementsByClass(
        stream.Measure
    ):

        dur=sum(
            x.duration.quarterLength
            for x in m.notesAndRests
        )


        if dur < 4:

            r=note.Rest()
            r.duration.quarterLength=4-dur
            m.append(r)


    print("FINAL CHECK")

    for i,m in enumerate(
        measures.getElementsByClass(stream.Measure),
        1
    ):

        total=sum(
            x.duration.quarterLength
            for x in m.notesAndRests
        )

        print(
            "Measure",
            i,
            total
        )


    new_score.append(measures)


    print("FINAL WRITE")

    new_score.write(
        "musicxml",
        fp=dst
    )


    print("DONE")
    print(dst)



if __name__=="__main__":

    if len(sys.argv)<3:
        print(
            "usage: python clean_musicxml_v28.py input.musicxml output.musicxml"
        )
        sys.exit()


    clean_score(
        sys.argv[1],
        sys.argv[2]
    )