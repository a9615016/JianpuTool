from music21 import converter


def clean_xml(input_file, output_file):

    score = converter.parse(input_file)

    new_score = score.parts[0]

    new_score.write(
        "musicxml",
        fp=output_file
    )


if __name__ == "__main__":

    clean_xml(
        "test.musicxml",
        "clean.musicxml"
    )

    print("clean完成")