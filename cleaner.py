from music21 import converter, stream


def clean_musicxml(input_file, output_file):

    score = converter.parse(input_file)

    part = stream.Part()

    notes = []

    for n in score.recurse().notes:

        if n.isNote:
            notes.append(n)


    # 按時間排序
    notes.sort(
        key=lambda x: x.offset
    )


    for n in notes:
        part.append(n)


    new_score = stream.Score()

    new_score.append(part)


    new_score.write(
        "musicxml",
        fp=output_file
    )


    print("clean musicxml:", output_file)