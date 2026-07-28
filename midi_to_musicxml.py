from music21 import converter, stream, meter, note, chord
import sys


def midi_to_musicxml(mid_file, out_file):

    print("開始 MIDI → MusicXML V2")

    print("讀取 MIDI...")
    score = converter.parse(mid_file)


    print("整理樂譜...")


    # 只保留第一聲部
    if len(score.parts) > 0:
        part = score.parts[0]
    else:
        part = score


    new_part = stream.Part()


    # 4/4
    new_part.append(meter.TimeSignature('4/4'))


    last_end = 0


    for n in part.recurse().notesAndRests:


        # chord取最高音
        if isinstance(n, chord.Chord):

            n = n.highestTime

            continue


        if isinstance(n, note.Note):

            nn = note.Note(n.pitch)

            # quantize
            nn.duration.quarterLength = round(
                float(n.duration.quarterLength) * 4
            ) / 4


            if nn.duration.quarterLength <= 0:
                continue


            new_part.append(nn)



        elif isinstance(n, note.Rest):

            r = note.Rest()

            r.duration.quarterLength = round(
                float(n.duration.quarterLength) * 4
            ) / 4

            if r.duration.quarterLength > 0:
                new_part.append(r)



    score2 = stream.Score()
    score2.append(new_part)


    print("重新切小節...")

    score2.makeMeasures(
        inPlace=True
    )


    print("補充 offset...")


    score2.makeNotation(
        inPlace=True
    )


    print("寫入 MusicXML...")


    score2.write(
        "musicxml",
        fp=out_file
    )


    print("完成:")
    print(out_file)



if __name__ == "__main__":

    if len(sys.argv)<3:
        print(
        "python midi_to_musicxml.py input.mid output.musicxml"
        )
        exit()


    midi_to_musicxml(
        sys.argv[1],
        sys.argv[2]
    )