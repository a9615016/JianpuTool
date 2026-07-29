# CLEAN MUSICXML V30
# FINAL PUBLISH SCORE FORMAT
# MIDI free rhythm -> jianpu_ly compatible

from music21 import converter, stream, note, chord, meter
import sys


ALLOWED_DURATIONS = [
    0.25,   # 16th
    0.5,    # eighth
    1.0,    # quarter
    2.0,    # half
    4.0     # whole
]


def quantize_duration(q):

    best = min(
        ALLOWED_DURATIONS,
        key=lambda x: abs(x-q)
    )

    return best



def clean(input_file, output_file):

    print("================")
    print("CLEAN MUSICXML V30")
    print("FINAL PUBLISH SCORE FORMAT")
    print("================")

    print("read")

    score = converter.parse(input_file)


    # remove voices
    print("remove voices")

    for p in score.parts:
        for el in p.recurse():
            if hasattr(el,"voice"):
                el.voice = None



    # remove chords
    print("remove chords")

    for p in score.parts:

        for c in list(p.recurse().getElementsByClass(chord.Chord)):

            n = note.Note(c.root())

            n.duration = c.duration

            c.activeSite.replace(c,n)



    # remove ties beams
    print("remove beams ties")

    for n in score.recurse().notes:

        n.beams.fill(0)

        n.tie = None



    # force 4/4
    print("force 4/4")

    for m in score.recurse().getElementsByClass(
            stream.Measure):

        m.timeSignature = meter.TimeSignature("4/4")



    # duration quantize
    print("duration quantize")

    for n in score.recurse().notes:

        d = float(n.duration.quarterLength)

        n.duration.quarterLength = quantize_duration(d)



    # rebuild measures
    print("rebuild measures")

    score.makeMeasures(inPlace=True)



    # split / repair measures
    print("BAR REPAIR V30")

    for p in score.parts:

        new_score = stream.Part()

        current = stream.Measure()

        beat = 0


        for n in p.recurse().notesAndRests:


            length = float(n.duration.quarterLength)


            # 超過4拍切斷
            if beat + length > 4:

                remain = 4 - beat


                if remain > 0:

                    n.duration.quarterLength = remain
                    current.append(n)


                current.number = len(
                    new_score.getElementsByClass(
                    stream.Measure
                    )
                ) + 1

                new_score.append(current)


                current = stream.Measure()
                beat = 0



            n.duration.quarterLength = min(
                n.duration.quarterLength,
                4
            )


            current.append(n)

            beat += float(
                n.duration.quarterLength
            )



        if current.notesAndRests:

            while beat < 4:

                r = note.Rest()

                r.duration.quarterLength = 4-beat

                current.append(r)

                beat += 4-beat


            new_score.append(current)



        p.coreElementsChanged()


    print("clear notation cache")

    score.coreElementsChanged()


    print("FINAL CHECK")


    for i,m in enumerate(
        score.recurse().getElementsByClass(stream.Measure),
        1):

        total=sum(
            x.duration.quarterLength
            for x in m.notesAndRests
        )

        print(
            "Measure",
            i,
            float(total)
        )



    print("FINAL WRITE")

    score.write(
        "musicxml",
        fp=output_file
    )


    print("DONE")
    print(output_file)



if __name__=="__main__":

    if len(sys.argv)<3:

        print(
        "python clean_musicxml.py input.musicxml output.musicxml"
        )

        exit()


    clean(
        sys.argv[1],
        sys.argv[2]
    )