from music21 import converter, stream, note, meter, tempo
import sys


print("==============================")
print("MIDI TO MUSICXML V2.1")
print("BASICPITCH COMPATIBLE")
print("==============================")


if len(sys.argv) < 3:
    print(
        "usage: python midi_to_musicxml.py input.mid output.musicxml"
    )
    sys.exit()


input_file = sys.argv[1]
output_file = sys.argv[2]


print("開始 MIDI → MusicXML")
print("輸入:", input_file)



# ==========================
# read midi
# ==========================

print("讀取 MIDI...")


midi_score = converter.parse(
    input_file
)



# ==========================
# get notes
# ==========================

print("整理音符...")


events=[]


part = midi_score.parts[0]


for n in part.recurse().notes:


    if isinstance(n, note.Note):

        start=float(n.offset)

        dur=float(
            n.duration.quarterLength
        )


        pitch=n.pitch


        events.append(
            (
                start,
                dur,
                pitch
            )
        )



print(
    "notes:",
    len(events)
)



# ==========================
# quantize
# ==========================

print("節奏量化")


GRID=0.25


fixed=[]


for start,dur,pitch in events:


    start=round(start/GRID)*GRID

    dur=round(dur/GRID)*GRID


    if dur<=0:

        dur=GRID


    fixed.append(
        (
            start,
            dur,
            pitch
        )
    )



# ==========================
# create score
# ==========================

print("建立 MusicXML")


score=stream.Score()


new_part=stream.Part()


new_part.insert(
    0,
    meter.TimeSignature("4/4")
)


# tempo

new_part.insert(
    0,
    tempo.MetronomeMark(
        number=80
    )
)



# ==========================
# split measure
# ==========================

print("切割跨小節音符")


measures={}



for start,dur,pitch in fixed:


    remaining=dur

    current=start


    while remaining>0:


        measure_no=int(
            current//4
        )+1


        pos=current%4


        available=4-pos


        length=min(
            remaining,
            available
        )


        if measure_no not in measures:

            measures[measure_no]=[]



        measures[measure_no].append(
            (
                pos,
                length,
                pitch
            )
        )


        remaining-=length


        current+=length



# ==========================
# write measures
# ==========================

print("建立小節")


for m_no in sorted(measures):


    m=stream.Measure(
        number=m_no
    )


    current=0


    notes=sorted(
        measures[m_no],
        key=lambda x:x[0]
    )


    for pos,length,pitch in notes:


        # 補休止

        if pos>current:

            m.append(
                note.Rest(
                    quarterLength=pos-current
                )
            )



        n=note.Note(
            pitch
        )


        n.duration.quarterLength=length


        m.append(n)


        current=pos+length



    # 補滿4拍

    if current<4:


        m.append(
            note.Rest(
                quarterLength=4-current
            )
        )



    new_part.append(m)



score.append(new_part)



# ==========================
# final check
# ==========================

print("FINAL CHECK")


for m in new_part.getElementsByClass(
    stream.Measure
):


    print(
        "Measure",
        m.number,
        float(m.duration.quarterLength)
    )



# ==========================
# write
# ==========================

print("寫入 MusicXML")


score.write(
    "musicxml",
    fp=output_file
)


print("完成:")
print(output_file)