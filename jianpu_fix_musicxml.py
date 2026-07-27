import sys

from music21 import converter
from music21 import stream
from music21 import note
from music21 import meter
from music21 import duration


VERSION = "JIANPU FIX MUSICXML V26.1 FINAL TICK ALIGN MAKE MEASURES"


# 四分音符 = 16 ticks
TICKS_PER_QUARTER = 16

# 4/4 = 64 ticks
BAR_TICKS = 64



def quantize_ticks(q):

    ticks = round(
        q * TICKS_PER_QUARTER
    )


    values = [
        64,
        48,
        32,
        24,
        16,
        12,
        8,
        6,
        4,
        2,
        1
    ]


    return min(
        values,
        key=lambda x:
        abs(x - ticks)
    )



def rebuild_part(part):

    print("rebuild part")


    events = []


    for n in part.recurse().notesAndRests:


        if isinstance(n, note.Note):

            tick = quantize_ticks(
                n.duration.quarterLength
            )


            events.append(
                (
                    n.pitch,
                    tick
                )
            )


        elif isinstance(n, note.Rest):

            tick = quantize_ticks(
                n.duration.quarterLength
            )


            events.append(
                (
                    None,
                    tick
                )
            )



    new_part = stream.Part()


    new_part.insert(
        0,
        meter.TimeSignature("4/4")
    )



    current = 0



    for pitch, tick in events:


        # 超過小節線
        if current + tick > BAR_TICKS:


            remain = BAR_TICKS - current


            if remain > 0:


                r = note.Rest()


                r.duration = duration.Duration(
                    remain /
                    TICKS_PER_QUARTER
                )


                new_part.append(r)



            current = 0



        if pitch is None:

            obj = note.Rest()

        else:

            obj = note.Note(
                pitch
            )



        obj.duration = duration.Duration(
            tick /
            TICKS_PER_QUARTER
        )


        new_part.append(obj)


        current += tick



    # 補最後小節

    if current < BAR_TICKS:


        r = note.Rest()


        r.duration = duration.Duration(
            (BAR_TICKS-current)
            /
            TICKS_PER_QUARTER
        )


        new_part.append(r)



    return new_part




def check_measures(score, title):


    print(title)


    measures = (
        score
        .parts[0]
        .getElementsByClass("Measure")
    )


    for i,m in enumerate(
        measures,
        1
    ):


        ticks = round(
            m.duration.quarterLength
            *
            TICKS_PER_QUARTER
        )


        print(
            "Measure",
            i,
            "ticks",
            ticks
        )




def fix_musicxml(
        input_file,
        output_file
):


    print("================")
    print(VERSION)
    print("================")


    print("read")


    score = converter.parse(
        input_file
    )



    new_score = stream.Score()



    for part in score.parts:


        fixed = rebuild_part(
            part
        )


        new_score.append(
            fixed
        )



    print("before makeMeasures")


    new_score = new_score.makeMeasures()



    check_measures(
        new_score,
        "CHECK AFTER MAKE MEASURES"
    )



    print("write")


    new_score.write(
        "musicxml",
        fp=output_file
    )


    print("DONE")
    print(output_file)




if __name__ == "__main__":


    if len(sys.argv) < 3:


        print(
            "python jianpu_fix_musicxml.py input.musicxml output.musicxml"
        )


        sys.exit(1)



    fix_musicxml(
        sys.argv[1],
        sys.argv[2]
    )