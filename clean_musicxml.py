# CLEAN MUSICXML V92
# Jianpu_ly dedicated version
# note stream rebuild

from music21 import converter, stream, meter, note, chord, tempo
import sys


STEP = 1 / 12   # jianpu_ly friendly resolution


def quantize_duration(q):
    """
    quantize to music21 quarterLength
    """

    values = [
        0.25,
        0.5,
        0.75,
        1,
        1.25,
        1.5,
        1.75,
        2,
        2.5,
        3,
        4
    ]

    return min(values, key=lambda x: abs(x-q))



def split_note(n, remain):

    result=[]

    length=n.duration.quarterLength

    while length > remain:

        part = remain

        nn = note.Note(
            n.pitch
        )

        nn.duration.quarterLength = part

        result.append(nn)

        length -= part

        remain = 4


    if length > 0:

        nn = note.Note(
            n.pitch
        )

        nn.duration.quarterLength = length

        result.append(nn)


    return result



def rebuild_part(src):

    new_part = stream.Part()

    new_part.insert(
        0,
        meter.TimeSignature("4/4")
    )


    current_measure = stream.Measure(
        number=1
    )

    beat = 0


    notes=[]


    for n in src.recurse():

        if isinstance(n, note.Note):

            notes.append(n)

        elif isinstance(n, chord.Chord):

            # 取最高音旋律
            nn = note.Note(
                n.pitches[-1]
            )

            nn.duration = n.duration

            notes.append(nn)



    for n in notes:


        dur = quantize_duration(
            n.duration.quarterLength
        )


        remain = 4 - beat


        if dur <= remain:

            nn = note.Note(
                n.pitch
            )

            nn.duration.quarterLength = dur

            current_measure.append(nn)

            beat += dur



        else:

            # split over bar

            first = remain

            if first > 0:

                nn = note.Note(
                    n.pitch
                )

                nn.duration.quarterLength = first

                current_measure.append(nn)



            new_part.append(
                current_measure
            )


            current_measure = stream.Measure(
                number=len(new_part.getElementsByClass("Measure"))+1
            )


            nn = note.Note(
                n.pitch
            )

            nn.duration.quarterLength = dur-first

            current_measure.append(nn)

            beat = dur-first



        if abs(beat-4)<0.001:


            new_part.append(
                current_measure
            )

            current_measure = stream.Measure(
                number=len(new_part.getElementsByClass("Measure"))+1
            )

            beat=0



    if len(current_measure.notes)>0:

        # 最後補休止

        rest_len = 4-beat

        if rest_len>0:

            r=note.Rest()

            r.duration.quarterLength=rest_len

            current_measure.append(r)


        new_part.append(
            current_measure
        )


    return new_part




def clean(input_file, output_file):

    print("================")
    print("CLEAN MUSICXML V92")
    print("NOTE STREAM REBUILD")
    print("================")


    score = converter.parse(input_file)


    out = stream.Score()


    for p in score.parts:

        print("rebuild part")

        np = rebuild_part(p)

        out.append(np)



    print("FINAL CHECK")


    for m in out.parts[0].getElementsByClass("Measure"):

        q = m.duration.quarterLength

        print(
            "Measure",
            m.number,
            q
        )

        if abs(q-4)>0.01:

            print(
                "WARNING",
                m.number,
                q
            )


    out.write(
        "musicxml",
        fp=output_file
    )


    print("DONE")
    print(output_file)



if __name__=="__main__":


    if len(sys.argv)<3:

        print(
            "usage: python clean_musicxml.py input.musicxml output.musicxml"
        )

        sys.exit()



    clean(
        sys.argv[1],
        sys.argv[2]
    )