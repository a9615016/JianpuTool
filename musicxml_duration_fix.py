import sys
import copy
import xml.etree.ElementTree as ET


# ============================================================
# jianpu-ly 可以直接處理的 duration
# ============================================================

SUPPORTED = {
    0.25,
    0.5,
    0.75,
    1.0,
    1.5,
    2.0,
    3.0,
    4.0,
    6.0,
    8.0,
    12.0,
}


# ============================================================
# duration 拆分
# ============================================================

def split_duration(value):
    """
    將 duration 拆成 jianpu-ly 支援的值。

    優先使用最大的合法 duration。
    """

    value = round(float(value), 6)

    if value <= 0:
        return []

    if value in SUPPORTED:
        return [value]

    result = []

    remaining = value

    # 從大到小
    candidates = sorted(
        SUPPORTED,
        reverse=True
    )

    while remaining > 0.000001:

        found = False

        for candidate in candidates:

            if candidate <= remaining + 0.000001:

                result.append(candidate)

                remaining = round(
                    remaining - candidate,
                    6
                )

                found = True
                break

        if not found:

            # 理論上不應該發生
            # 最小單位 0.25
            raise RuntimeError(
                f"無法拆分 duration={value}"
            )

    return result


# ============================================================
# duration → MusicXML type
# ============================================================

def duration_to_type(duration):

    mapping = {

        0.25: ("16th", 0),
        0.5: ("eighth", 0),
        0.75: ("eighth", 1),
        1.0: ("quarter", 0),
        1.5: ("quarter", 1),
        2.0: ("half", 0),
        3.0: ("half", 1),
        4.0: ("whole", 0),
        6.0: ("whole", 1),
        8.0: ("breve", 0),
        12.0: ("breve", 1),
    }

    key = round(float(duration), 6)

    if key not in mapping:

        raise RuntimeError(
            f"沒有對應的 MusicXML type: {duration}"
        )

    return mapping[key]


# ============================================================
# 找 namespace
# ============================================================

def get_namespace(root):

    if root.tag.startswith("{"):

        return root.tag.split("}")[0][1:]

    return ""


# ============================================================
# 建立 note
# ============================================================

def make_note_copy(
    original,
    duration_divisions,
    divisions
):

    note = copy.deepcopy(original)

    duration = note.find("duration")

    if duration is None:

        duration = ET.Element("duration")

        # duration 放在 voice 前
        children = list(note)

        insert_index = 0

        for i, child in enumerate(children):

            if child.tag in (
                "voice",
                "type",
                "dot"
            ):

                insert_index = i
                break

        note.insert(
            insert_index,
            duration
        )

    duration.text = str(
        int(round(duration_divisions))
    )

    beats = (
        duration_divisions
        / float(divisions)
    )

    note_type, dots = duration_to_type(
        beats
    )

    # 移除舊 type
    for child in list(note):

        if child.tag == "type":

            note.remove(child)

    # 移除舊 dots
    for child in list(note):

        if child.tag == "dot":

            note.remove(child)

    # type 放在 duration 後面
    children = list(note)

    duration_index = 0

    for i, child in enumerate(children):

        if child.tag == "duration":

            duration_index = i
            break

    type_element = ET.Element("type")
    type_element.text = note_type

    note.insert(
        duration_index + 1,
        type_element
    )

    for _ in range(dots):

        dot = ET.Element("dot")

        note.insert(
            duration_index + 2,
            dot
        )

    return note


# ============================================================
# 修正單一小節
# ============================================================

def fix_measure(
    measure,
    divisions
):

    new_children = []

    changed = False

    for child in list(measure):

        if child.tag != "note":

            new_children.append(child)

            continue

        duration = child.find("duration")

        if duration is None:

            new_children.append(child)

            continue

        try:

            duration_divisions = int(
                duration.text
            )

        except Exception:

            new_children.append(child)

            continue

        duration_beats = (
            duration_divisions
            / float(divisions)
        )

        duration_beats = round(
            duration_beats,
            6
        )

        # ----------------------------------------------------
        # 正常 duration
        # ----------------------------------------------------

        if duration_beats in SUPPORTED:

            new_children.append(child)

            continue

        # ----------------------------------------------------
        # 不支援 duration
        # ----------------------------------------------------

        parts = split_duration(
            duration_beats
        )

        print(
            f"    修正 duration "
            f"{duration_beats} → {parts}"
        )

        changed = True

        for part in parts:

            part_divisions = (
                part * divisions
            )

            new_note = make_note_copy(
                child,
                part_divisions,
                divisions
            )

            new_children.append(
                new_note
            )

    # --------------------------------------------------------
    # 重新寫入 measure
    # --------------------------------------------------------

    if changed:

        for child in list(measure):

            measure.remove(child)

        for child in new_children:

            measure.append(child)

    return changed


# ============================================================
# 小節總時值
# ============================================================

def get_measure_total(
    measure,
    divisions
):

    total = 0

    for note in measure.findall("note"):

        duration = note.find("duration")

        if duration is None:
            continue

        try:

            total += int(
                duration.text
            )

        except Exception:

            pass

    return total / float(divisions)


# ============================================================
# 主程式
# ============================================================

def fix_musicxml(
    input_path,
    output_path
):

    print("=" * 60)
    print("MusicXML Duration Fix")
    print("=" * 60)

    tree = ET.parse(
        input_path
    )

    root = tree.getroot()

    total_fixed = 0

    divisions = 1

    # --------------------------------------------------------
    # 處理所有 part
    # --------------------------------------------------------

    for part in root.iter("part"):

        for measure in part.findall("measure"):

            # ------------------------------------------------
            # 取得 divisions
            # ------------------------------------------------

            attributes = measure.find(
                "attributes"
            )

            if attributes is not None:

                d = attributes.find(
                    "divisions"
                )

                if (
                    d is not None
                    and d.text
                ):

                    try:

                        divisions = int(
                            d.text
                        )

                    except Exception:

                        pass

            # ------------------------------------------------
            # 修正
            # ------------------------------------------------

            before = get_measure_total(
                measure,
                divisions
            )

            changed = fix_measure(
                measure,
                divisions
            )

            after = get_measure_total(
                measure,
                divisions
            )

            if changed:

                total_fixed += 1

                print(
                    f"  小節 "
                    f"{measure.get('number', '?')}: "
                    f"{before:.3f} → "
                    f"{after:.3f}"
                )

                # ------------------------------------------------
                # 嚴格檢查
                # ------------------------------------------------

                if abs(before - after) > 0.001:

                    raise RuntimeError(
                        "❌ 修正後小節總時值改變："
                        f"{before} → {after}"
                    )

    # --------------------------------------------------------
    # 寫出
    # --------------------------------------------------------

    tree.write(
        output_path,
        encoding="utf-8",
        xml_declaration=True
    )

    print()
    print(
        f"修正小節數：{total_fixed}"
    )

    print(
        f"輸出：{output_path}"
    )

    print("=" * 60)


# ============================================================
# CLI
# ============================================================

def main():

    if len(sys.argv) < 3:

        print(
            "用法："
        )

        print(
            "python musicxml_duration_fix.py "
            "input.musicxml output.musicxml"
        )

        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    fix_musicxml(
        input_path,
        output_path
    )


if __name__ == "__main__":

    main()