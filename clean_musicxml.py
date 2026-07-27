import sys
import music21
from music21 import stream, meter, note, chord, duration


print("================")
print("CLEAN MUSICXML V17")
print("================")


def clean(input_file, output_file):

    print("input:", input_file)

    score = music21.converter.parse(input_file)


    # remove voices
    print("remove voices")

    for part in score.parts:
        for element in part.recurse():

            if hasattr(element, "voices"):
                try:
                    element.voices.clear()
                except:
                    pass



    # remove chords
    print("remove chords")

    for part in score.parts:

        for c in list(part.recurse().getElementsByClass('Chord')):

            pitches = c.pitches

            if pitches:

                n = note.Note(
                    pitches[0]
                )

                n.duration = c.duration

                c.replace(n)



    # quantize
    print("quantize")

    for n in score.recurse().notes:

        try:
            n.duration.quarterLength = round(
                n.duration.quarterLength * 4
            ) / 4

        except:
            pass



    # force 4/4
    print("force 4/4")

    for part in score.parts:

        part.insert(
            0,
            meter.TimeSignature("4/4")
        )


    # NEW V17
    # rebuild measures
    print("rebuild measures")


    new_score = stream.Score()


    for part in score.parts:


        new_part = stream.Part()


        current = stream.Measure()

        current.number = 1


        total = 0


        measure_no = 1


        for n in part.recurse().notesAndRests:


            q = n.duration.quarterLength


            # 超過4拍，換小節
            if total + q > 4:


                current.rightBarline = "regular"

                new_part.append(current)


                measure_no += 1

                current = stream.Measure()

                current.number = measure_no

                total = 0



            current.append(n)

            total += q



        if len(current):

            new_part.append(current)



        new_score.append(new_part)



    score = new_score



    # remove empty measures

    print("remove empty measures")

    for part in score.parts:

        for m in list(part.getElementsByClass("Measure")):

            if len(m.notesAndRests)==0:

                part.remove(m)



    print("write")

    score.write(
        "musicxml",
        fp=output_file
    )


    print("DONE", output_file)



if __name__ == "__main__":

    if len(sys.argv)<3:

        print(
            "python clean_musicxml.py input.musicxml output.musicxml"
        )

        exit()


    clean(
        sys.argv[1],
        sys.argv[2]
    )