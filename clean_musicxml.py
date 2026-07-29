from music21 import converter, stream, note, meter, clef
import sys


VERSION = "CLEAN MUSICXML V90 JIANPU LY PURE SANITIZER"


# 以四分音符為最小單位
GRID = 0.25



def quantize_duration(x):

    x = float(x)

    q = round(x / GRID) * GRID

    if q <= 0:
        q = GRID

    return q



def clean_note(old, duration):

    """
    建立全新的 note/rest
    不保留任何舊 MusicXML 資訊
    """

    if old.isRest:

        obj = note.Rest()

    else:

        obj = note.Note(
            old.pitch.pitchClassString
        )

        obj.pitch.octave = old.pitch.octave


    obj.duration.quarterLength = duration


    # 清除所有附加資訊

    obj.tie = None

    obj.lyric = None

    obj.expressions = []

    obj.articulations = []

    obj.beams = []


    return obj




def rebuild_from_zero(score):

    print("V90 PURE REBUILD")


    result = stream.Score()


    part = stream.Part()


    part.insert(
        0,
        meter.TimeSignature("4/4")
    )


    part.insert(
        0,
        clef.TrebleClef()
    )


    measure_no = 1


    measure = stream.Measure(
        number=measure_no
    )


    beat = 0.0



    for old in score.recurse().notesAndRests:


        duration = quantize_duration(
            old.duration.quarterLength
        )


        remain = duration



        while remain > 0:


            space = 4.0 - beat


            use = min(
                remain,
                space
            )


            obj = clean_note(
                old,
                use
            )


            measure.append(obj)


            beat += use


            remain -= use



            # 完成一小節

            if beat >= 4.0 - 0.0001:


                part.append(measure)


                measure_no += 1


                measure = stream.Measure(
                    number=measure_no
                )


                beat = 0.0



    # 最後補滿

    if beat > 0:


        rest = note.Rest()


        rest.duration.quarterLength = round(
            4.0 - beat,
            2
        )


        measure.append(rest)


        part.append(measure)



    result.append(part)


    return result





def jianpu_check(score):


    print("V90 FINAL CHECK")


    for m in score.parts[0].getElementsByClass(
        "Measure"
    ):


        total = sum(
            n.duration.quarterLength
            for n in m.notesAndRests
        )


        print(
            "Measure",
            m.number,
            float(total)
        )


        if abs(total - 4.0) > 0.001:

            raise Exception(
                "BAD BAR "
                + str(m.number)
            )


    print("V90 SAFE")





def clean(inp, out):


    print("====================")
    print(VERSION)
    print("====================")


    old = converter.parse(inp)


    print("REMOVE EVERYTHING")


    new = rebuild_from_zero(old)



    # 重新建立 measure

    new.parts[0].makeMeasures(
        inPlace=True
    )



    # 清除 offset / cache

    for n in new.recurse().notesAndRests:

        n.tie = None

        n.beams = []



    new.parts[0].flatten()



    jianpu_check(new)



    print("WRITE MUSICXML")



    new.write(
        "musicxml",
        fp=out
    )


    print("DONE")

    print(out)





if __name__ == "__main__":


    if len(sys.argv) < 3:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()



    clean(
        sys.argv[1],
        sys.argv[2]
    )