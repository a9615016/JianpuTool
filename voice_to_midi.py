import librosa
import numpy as np
import music21
import sys



def hz_to_midi(hz):

    if hz is None:
        return None

    if np.isnan(hz):
        return None

    return int(
        round(
            69 + 12 * np.log2(hz / 440.0)
        )
    )



def voice_to_midi(
    input_wav,
    output_midi
):

    print("開始人聲轉 MIDI")
    print("輸入:", input_wav)


    # 讀取 WAV

    y, sr = librosa.load(
        input_wav,
        sr=22050
    )


    print("分析音高")


    # 人聲音高偵測

    f0, voiced_flag, voiced_prob = librosa.pyin(
        y,
        fmin=librosa.note_to_hz("C2"),
        fmax=librosa.note_to_hz("C7"),
        sr=sr
    )



    notes = []


    hop_time = 512 / sr


    current_note = None
    start_time = 0
    duration = 0



    for i, freq in enumerate(f0):


        time = i * hop_time



        # 過濾 NaN

        if freq is not None and not np.isnan(freq):


            midi = hz_to_midi(freq)


            if midi is None:
                continue



            # 音高變化

            if midi != current_note:


                # 儲存上一個音

                if current_note is not None and duration >= 0.12:


                    n = music21.note.Note(
                        current_note
                    )

                    n.offset = start_time

                    n.quarterLength = max(
                        duration * 2,
                        0.25
                    )

                    notes.append(n)



                current_note = midi

                start_time = time

                duration = hop_time



            else:

                duration += hop_time



        else:


            # 無聲

            if current_note is not None:


                if duration >= 0.12:


                    n = music21.note.Note(
                        current_note
                    )

                    n.offset = start_time

                    n.quarterLength = max(
                        duration * 2,
                        0.25
                    )

                    notes.append(n)



                current_note = None

                duration = 0



    # 最後音符

    if current_note is not None and duration >= 0.12:


        n = music21.note.Note(
            current_note
        )

        n.offset = start_time

        n.quarterLength = max(
            duration * 2,
            0.25
        )

        notes.append(n)



    print(
        "偵測音符:",
        len(notes)
    )



    if len(notes) == 0:

        print(
            "沒有偵測到人聲"
        )

        return



    print("旋律:")


    for n in notes[:30]:

        print(
            n.pitch.nameWithOctave,
            n.quarterLength
        )



    # 建立 MIDI

    part = music21.stream.Part()



    for n in notes:

        part.append(n)



    score = music21.stream.Score()

    score.append(part)



    score.write(
        "midi",
        fp=output_midi
    )


    print(
        "完成:",
        output_midi
    )





if __name__ == "__main__":


    if len(sys.argv) < 3:

        print(
            "使用方式:"
        )

        print(
            "python voice_to_midi.py input.wav output.mid"
        )

        sys.exit(1)



    voice_to_midi(
        sys.argv[1],
        sys.argv[2]
    )