import sys
import os

from basic_pitch.inference import predict_and_save


if __name__ == "__main__":

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    print("開始 BasicPitch")
    print("輸入:", input_file)

    predict_and_save(
        [input_file],
        output_dir,
        True,
        True,
        False
    )

    print("BasicPitch完成")