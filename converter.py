import music21
import os


def midi_to_musicxml(input_file, output_file=None):

    print("開始 MIDI -> MusicXML")
    print("輸入:", input_file)


    if output_file is None:
        base = os.path.splitext(input_file)[0]
        output_file = base + ".musicxml"


    # 讀 MIDI
    score = music21.converter.parse(input_file)


    # 只保留第一聲部(主旋律)
    parts = score.parts

    if len(parts) > 0:
        melody = parts[0]
    else:
        melody = score


    # 建立新樂譜
    new_score = music21.stream.Score()

    new_part = music21.stream.Part()


    # 設定拍號
    new_part.append(
        music21.meter.TimeSignature("4/4")
    )


    # 設定調性
    try:
        key = melody.analyze("key")
        new_part.append(key)
    except:
        pass


    # 只加入單音
    for element in melody.flatten().notesAndRests:

        if isinstance(element, music21.note.Note):

            n = music21.note.Note()

            n.pitch = element.pitch

            n.duration = element.duration

            # 清除不必要資訊
            n.tie = None

            new_part.append(n)


        elif isinstance(element, music21.note.Rest):

            r = music21.note.Rest()

            r.duration = element.duration

            new_part.append(r)


    new_score.append(new_part)


    # 修正 offset
    new_score.makeMeasures(
        inPlace=True
    )


    # 寫 MusicXML
    new_score.write(
        "musicxml",
        fp=output_file
    )


    print("完成:")
    print(output_file)


    return output_file