import sys

from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH


def convert(audio, midi):

    model_output = predict(
        audio,
        ICASSP_2022_MODEL_PATH
    )

    model_output[0].write(midi)


if __name__=="__main__":

    convert(
        sys.argv[1],
        sys.argv[2]
    )