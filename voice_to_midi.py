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



def add_note(notes, midi_note, start_time):

    if midi_note is None:
        return

    # 過濾太低太高雜訊
    if midi_note < 36 or midi_note > 96:
        return


    # 合併相同音

    if len(notes) > 0:

        last = notes[-1]

        if last["pitch"] == midi_note:

            last["duration"] += 0.5

            return


    notes.append(
        {
            "pitch": midi_note,
            "duration": 0.5,
            "start": start_time
        }
    )



def voice_to_midi(
    input_wav,
    output_midi
):

    print("開始人聲轉 MIDI")
    print("輸入:", input_wav)



    y, sr = librosa.load(
        input_wav,
        sr=22050
    )


    print("分析音高")



    f0, voiced_flag, voiced_prob = librosa.pyin(
        y,
        fmin=librosa.note_to_hz("C2"),
        fmax=librosa.note_to_hz("C7"),
        sr=sr
    )



    notes = []

    hop_time = 512 / sr


    current_note = None
    start = 0



    for i, freq in enumerate(f0):

        time = i * hop_time


        if freq is not None and not np.isnan(freq):


            midi = hz_to_midi(freq)


            if midi is None:
                continue



            if midi != current_note:


                if current_note is not None:

                    add_note(
                        notes,
                        current_note,
                        start
                    )


                current_note = midi
                start = time



        else:


            if current_note is not None:

                add_note(
                    notes,
                    current_note,
                    start
                )

                current_note = None



    if current_note is not None:

        add_note(
            notes,
            current_note,
            start
        )



    print(
        "偵測音符:",
        len(notes)
    )



    if len(notes) == 0:

        print("沒有偵測到旋律")

        return



    # 建立 MIDI

    part = music21.stream.Part()



    for item in notes:


        n = music21.note.Note(
            item["pitch"]
        )


        # 固定八分音符
        # 方便 jianpu_ly 處理

        n.quarterLength = 0.5


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