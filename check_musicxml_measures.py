import sys
import xml.etree.ElementTree as ET

if len(sys.argv) < 2:
    print("用法：python check_musicxml_measures.py final.musicxml")
    sys.exit(1)

path = sys.argv[1]

tree = ET.parse(path)
root = tree.getroot()

divisions = 1
beats = 4
beat_type = 4

print("=" * 70)
print("MusicXML 深度檢查")
print("=" * 70)

for measure in root.iter("measure"):

    number = measure.get("number", "?")

    attributes = measure.find("attributes")

    if attributes is not None:

        d = attributes.find("divisions")

        if d is not None and d.text:
            try:
                divisions = int(d.text)
            except:
                pass

        time = attributes.find("time")

        if time is not None:

            b = time.find("beats")
            bt = time.find("beat-type")

            if b is not None and b.text:
                try:
                    beats = int(b.text)
                except:
                    pass

            if bt is not None and bt.text:
                try:
                    beat_type = int(bt.text)
                except:
                    pass

    expected = beats * (4.0 / beat_type)

    total_divisions = 0

    print()
    print(f"========== 小節 {number} ==========")
    print(
        f"拍號: {beats}/{beat_type}"
    )
    print(
        f"divisions: {divisions}"
    )

    note_index = 0

    for child in measure:

        if child.tag != "note":
            continue

        note_index += 1

        duration = child.find("duration")

        if duration is not None and duration.text:

            try:
                duration_value = int(duration.text)
            except:
                duration_value = 0

            duration_beat = (
                duration_value
                / float(divisions)
            )

            total_divisions += duration_value

        else:

            duration_value = 0
            duration_beat = 0

        pitch = child.find("pitch")

        if pitch is not None:

            step = pitch.findtext("step", "?")
            octave = pitch.findtext("octave", "?")
            alter = pitch.findtext("alter")

            pitch_text = (
                f"{step}{alter or ''}{octave}"
            )

        else:

            pitch_text = "REST"

        voice = child.findtext(
            "voice",
            "?"
        )

        note_type = child.findtext(
            "type",
            "?"
        )

        dots = len(
            child.findall("dot")
        )

        time_mod = child.find(
            "time-modification"
        )

        if time_mod is not None:

            actual = time_mod.findtext(
                "actual-notes",
                "?"
            )

            normal = time_mod.findtext(
                "normal-notes",
                "?"
            )

            tm_text = (
                f"{actual}:{normal}"
            )

        else:

            tm_text = "-"

        print(
            f"Note {note_index:>3} | "
            f"{pitch_text:>5} | "
            f"duration={duration_value:>5} | "
            f"beats={duration_beat:>6.3f} | "
            f"type={note_type:>5} | "
            f"dots={dots} | "
            f"voice={voice} | "
            f"time-mod={tm_text}"
        )

        # ----------------------------------------------------
        # 可疑時值
        # ----------------------------------------------------

        allowed = {
            0.5,
            0.75,
            1.0,
            1.5,
            2.0,
            3.0,
            4.0,
            6.0,
            8.0,
            12.0
        }

        if duration_beat not in allowed:

            print(
                "   ⚠️ 可疑時值："
                f"{duration_beat}"
            )

        # ----------------------------------------------------
        # 特殊：time-modification
        # ----------------------------------------------------

        if time_mod is not None:

            print(
                "   ⚠️ 發現 time-modification"
            )

    actual = (
        total_divisions
        / float(divisions)
    )

    print()
    print(
        f"小節總時值："
        f"{actual:.3f} / "
        f"{expected:.3f}"
    )

    if abs(actual - expected) > 0.001:

        print(
            "❌ 小節總時值錯誤"
        )

    else:

        print(
            "✅ 小節總時值正常"
        )

print()
print("=" * 70)
print("深度檢查完成")
print("=" * 70)