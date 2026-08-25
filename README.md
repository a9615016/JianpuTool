# JianpuTool Precision — MP3 → 人聲簡譜 PDF

這是以你原本 `jianpu3_fixed` 為基礎整理的「精準版」。

## 核心流程

MP3
→ Demucs 人聲分離
→ BasicPitch 人聲音高辨識
→ 多方法 BPM 偵測
→ 調性偵測
→ 人聲音域篩選
→ 短雜音過濾
→ 單音旋律選擇
→ 1/16 拍量化
→ MusicXML
→ jianpu-ly
→ LilyPond
→ **數字簡譜 PDF**

## 這版特別修正

### 1. 不直接分析整首混音
先使用 Demucs `--two-stems=vocals` 取得 vocals.wav，再讓 BasicPitch 分析。
這是提升「人聲主旋律」辨識率最重要的一步。

### 2. BPM 不再只相信一次 beat_track
`key_detect.py` 同時使用：
- librosa beat_track
- onset strength tempo
- 0.5x / 2x BPM 正規化

降低 60/120、70/140 這類半速/雙速錯誤。

### 3. BasicPitch 使用較保守的人聲設定
- onset threshold 0.55
- frame threshold 0.35
- minimum note length 80 ms
- 約 C3～C6 的人聲範圍

### 4. MIDI 只量化一次
先依偵測 BPM 將 BasicPitch 的時間軸換回原曲拍值，再做 1/16 拍量化。
MusicXML 階段不再二次量化。

### 5. jianpu-ly 使用正確命令列工具
使用 `jianpu-ly input.musicxml > score.ly` 的方式，不使用錯誤的
`python -m jianpu_ly`。

## Windows 使用

建議 Python 3.10。

### 第一次安裝

```bat
pip install -r requirements.txt
python check_env.py
```

另外必須安裝：
- FFmpeg
- LilyPond 2.26.x
- jianpu-ly 1.872

如果 LilyPond 不在 PATH，可設定：

```bat
set LILYPOND_PATH=C:\lilypond-2.26.0\bin\lilypond.exe
```

## 直接轉換

```bat
python main.py "C:\你的歌曲\song.mp3"
```

也可以：

```bat
run_mp3_to_jianpu.bat "C:\你的歌曲\song.mp3"
```

完成後會在：

```text
jianpu3_fixed\outputs\<UUID>\jianpu.pdf
```

以及同一個資料夾看到中間結果：

```text
vocals.wav
raw_melody.mid
info.json
clean_melody.mid
final.musicxml
score.ly
jianpu.pdf
```

## 網頁版

```bat
streamlit run streamlit_app.py
```

## 很重要：什麼叫「精準」

這套程式可以把「MP3 人聲旋律」自動轉成簡譜，但不能保證任何歌曲都 100% 一模一樣。

最容易影響結果的是：
1. 原 MP3 人聲是否清楚
2. 和聲、合唱是否很多
3. 歌手是否大量滑音、轉音
4. 歌曲是否自由速度/rubato
5. BPM 是否真的能被音訊穩定估計
6. BasicPitch 是否把泛音誤判成音符

因此這版的目標是「自動化流程中盡量提高穩定度」，不是宣稱 100% 音符正確。

如果你要追求商用級準確度，下一階段應該加入：
- vocal pitch contour 後處理
- 八度錯誤偵測
- 音符起點/終點重新校正
- 弱起拍偵測
- 1/8、1/16、三連音自適應量化
- 人聲音高人工校正介面
