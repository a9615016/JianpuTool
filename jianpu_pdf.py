import os
import sys
import subprocess
import shutil
import xml.etree.ElementTree as ET


# ============================================================
# JianpuTool - jianpu_pdf.py
#
# 支援：
# Windows
# Hugging Face / Linux / Docker
#
# jianpu-ly 1.872
# ============================================================


# ============================================================
# LilyPond 路徑
# ============================================================

def find_lilypond():

    # --------------------------------------------------------
    # 1. 優先使用環境變數
    # --------------------------------------------------------

    env_path = os.environ.get("LILYPOND_PATH")

    if env_path and os.path.isfile(env_path):
        return env_path

    # --------------------------------------------------------
    # 2. 從 PATH 找
    # --------------------------------------------------------

    exe = shutil.which("lilypond")

    if exe:
        return exe

    # --------------------------------------------------------
    # 3. Windows 常見位置
    # --------------------------------------------------------

    if os.name == "nt":

        candidates = [

            r"C:\lilypond-2.22.2\usr\bin\lilypond.exe",

            r"C:\lilypond-2.26.0\bin\lilypond.exe",

            r"C:\Program Files\LilyPond\usr\bin\lilypond.exe",

        ]

        for path in candidates:

            if os.path.isfile(path):
                return path

    # --------------------------------------------------------
    # 4. Linux 常見位置
    # --------------------------------------------------------

    linux_candidates = [

        "/usr/bin/lilypond",

        "/usr/local/bin/lilypond",

        "/opt/lilypond/bin/lilypond",

    ]

    for path in linux_candidates:

        if os.path.isfile(path):
            return path

    # --------------------------------------------------------
    # 找不到
    # --------------------------------------------------------

    raise Exception(
        "找不到 LilyPond。\n\n"
        "Windows：請確認已安裝 LilyPond。\n"
        "Linux/Docker：請確認 Dockerfile 已安裝 LilyPond。\n"
        "也可以設定環境變數 LILYPOND_PATH。"
    )


# ============================================================
# MusicXML 安全處理
# 避免過低音域造成 jianpu-ly 問題
# ============================================================

def fix_low_octaves(musicxml_file):

    print("[6/6] 檢查 MusicXML 音域...")

    tree = ET.parse(musicxml_file)
    root = tree.getroot()

    changed = 0

    for pitch in root.iter():

        if not pitch.tag.endswith("pitch"):
            continue

        octave_element = None

        for child in pitch:

            if child.tag.endswith("octave"):

                octave_element = child

                break

        if octave_element is None:
            continue

        try:

            octave = int(octave_element.text)

        except (TypeError, ValueError):

            continue

        # ----------------------------------------------------
        # 避免過低音域
        # ----------------------------------------------------

        while octave < 1:

            octave += 1

            octave_element.text = str(octave)

            changed += 1

    # --------------------------------------------------------
    # 不需要修改
    # --------------------------------------------------------

    if changed == 0:

        print("[6/6] 音域正常")

        return musicxml_file

    # --------------------------------------------------------
    # 建立安全版本
    # --------------------------------------------------------

    work_dir = os.path.dirname(musicxml_file)

    filename = os.path.basename(musicxml_file)

    name, ext = os.path.splitext(filename)

    safe_file = os.path.join(
        work_dir,
        name + "_jianpu_safe" + ext
    )

    tree.write(
        safe_file,
        encoding="utf-8",
        xml_declaration=True
    )

    print(
        f"[6/6] 已修正 {changed} 個過低音符"
    )

    print(
        "[6/6] 安全 MusicXML:",
        safe_file
    )

    return safe_file


# ============================================================
# 找 jianpu-ly
# ============================================================

def find_jianpu_ly():

    # --------------------------------------------------------
    # 1. PATH
    # --------------------------------------------------------

    candidates = [

        shutil.which("jianpu-ly"),

        shutil.which("jianpu_ly"),

    ]

    for exe in candidates:

        if exe:
            return exe

    # --------------------------------------------------------
    # 2. Windows Python Scripts
    # --------------------------------------------------------

    if os.name == "nt":

        candidates = [

            r"C:\Users\user\AppData\Local\Programs\Python\Python310\Scripts\jianpu-ly.exe",

            r"C:\Users\user\AppData\Roaming\Python\Python310\Scripts\jianpu-ly.exe",

        ]

        for path in candidates:

            if os.path.isfile(path):

                return path

    # --------------------------------------------------------
    # 3. Linux 常見 Python bin
    # --------------------------------------------------------

    candidates = [

        "/usr/local/bin/jianpu-ly",

        "/usr/bin/jianpu-ly",

    ]

    for path in candidates:

        if os.path.isfile(path):

            return path

    # --------------------------------------------------------
    # 找不到
    # --------------------------------------------------------

    raise Exception(
        "找不到 jianpu-ly。\n\n"
        "請確認 requirements.txt 包含：\n"
        "jianpu-ly==1.872"
    )


# ============================================================
# MusicXML -> LilyPond
#
# stdout = LilyPond 程式碼
# stderr = 警告 / 訊息
#
# 絕對不能把 stderr 寫入 score.ly
# ============================================================

def run_jianpu_ly(musicxml_file, ly_file):

    jianpu_ly_exe = find_jianpu_ly()

    print(
        "jianpu-ly:",
        jianpu_ly_exe
    )

    result = subprocess.run(

        [
            jianpu_ly_exe,
            musicxml_file
        ],

        stdout=subprocess.PIPE,

        stderr=subprocess.PIPE,

        text=True,

        encoding="utf-8",

        errors="replace"
    )

    # --------------------------------------------------------
    # stdout 才是真正 LilyPond 原始碼
    # --------------------------------------------------------

    with open(
        ly_file,
        "w",
        encoding="utf-8",
        newline="\n"
    ) as f:

        f.write(result.stdout)

    # --------------------------------------------------------
    # stderr 只顯示
    # --------------------------------------------------------

    if result.stderr:

        print(
            result.stderr,
            end=""
        )

    # --------------------------------------------------------
    # jianpu-ly 是否成功
    # --------------------------------------------------------

    if result.returncode != 0:

        raise Exception(
            "jianpu-ly 轉換失敗\n\n"
            + result.stderr
        )

    # --------------------------------------------------------
    # 確認 score.ly
    # --------------------------------------------------------

    if not os.path.isfile(ly_file):

        raise Exception(
            "找不到產生的 LilyPond 檔案：\n"
            + ly_file
        )

    if os.path.getsize(ly_file) == 0:

        raise Exception(
            "score.ly 是空檔案"
        )

    # --------------------------------------------------------
    # 清理前方非 LilyPond 訊息
    # --------------------------------------------------------

    with open(
        ly_file,
        "r",
        encoding="utf-8",
        errors="replace"
    ) as f:

        content = f.read()

    lines = content.splitlines()

    valid_start = None

    for i, line in enumerate(lines):

        stripped = line.strip()

        if (

            stripped.startswith(r"\version")

            or

            stripped.startswith("#(")

            or

            stripped.startswith(r"\header")

            or

            stripped.startswith(r"\paper")

        ):

            valid_start = i

            break

    if valid_start is not None and valid_start > 0:

        print(
            f"⚠ 清除 score.ly 前方 "
            f"{valid_start} 行非 LilyPond 訊息"
        )

        content = (
            "\n".join(lines[valid_start:])
            + "\n"
        )

        with open(
            ly_file,
            "w",
            encoding="utf-8",
            newline="\n"
        ) as f:

            f.write(content)


# ============================================================
# LilyPond 編譯
# ============================================================

def run_lilypond(
    ly_file,
    output_prefix
):

    print("LilyPond 編譯...")

    # --------------------------------------------------------
    # 自動尋找 LilyPond
    # --------------------------------------------------------

    lilypond = find_lilypond()

    print(
        "使用 LilyPond:",
        lilypond
    )

    if not os.path.isfile(lilypond):

        raise Exception(
            "找不到 LilyPond：\n"
            + lilypond
        )

    # --------------------------------------------------------
    # 執行 LilyPond
    # --------------------------------------------------------

    result = subprocess.run(

        [
            lilypond,
            "-o",
            output_prefix,
            ly_file
        ],

        stdout=subprocess.PIPE,

        stderr=subprocess.STDOUT,

        text=True,

        encoding="utf-8",

        errors="replace"
    )

    print(
        result.stdout
    )

    if result.returncode != 0:

        raise Exception(
            "LilyPond 編譯失敗\n\n"
            + result.stdout
        )

    # --------------------------------------------------------
    # 確認 PDF
    # --------------------------------------------------------

    generated_pdf = (
        output_prefix
        + ".pdf"
    )

    if not os.path.isfile(generated_pdf):

        raise Exception(
            "LilyPond 執行完成，"
            "但是找不到 PDF：\n"
            + generated_pdf
        )

    return generated_pdf


# ============================================================
# 主流程
# ============================================================

def create_pdf(
    musicxml_file,
    pdf_file
):

    print(
        "========================================"
    )

    print(
        "[6/6] MusicXML -> 數字簡譜 PDF"
    )

    print(
        "========================================"
    )

    # --------------------------------------------------------
    # 確認 MusicXML
    # --------------------------------------------------------

    if not os.path.isfile(
        musicxml_file
    ):

        raise Exception(
            f"找不到 MusicXML: {musicxml_file}"
        )

    # --------------------------------------------------------
    # 建立輸出資料夾
    # --------------------------------------------------------

    work_dir = (
        os.path.dirname(pdf_file)
        or "."
    )

    os.makedirs(
        work_dir,
        exist_ok=True
    )

    # --------------------------------------------------------
    # 顯示環境
    # --------------------------------------------------------

    print(
        "作業系統:",
        os.name
    )

    try:

        print(
            "LilyPond:",
            find_lilypond()
        )

    except Exception:

        print(
            "LilyPond: 尚未找到"
        )

    try:

        print(
            "jianpu-ly:",
            find_jianpu_ly()
        )

    except Exception:

        print(
            "jianpu-ly: 尚未找到"
        )

    # --------------------------------------------------------
    # 1. MusicXML 音域安全處理
    # --------------------------------------------------------

    safe_musicxml = fix_low_octaves(
        musicxml_file
    )

    # --------------------------------------------------------
    # 2. MusicXML -> score.ly
    # --------------------------------------------------------

    ly_file = os.path.join(
        work_dir,
        "score.ly"
    )

    print(
        "轉換 jianpu-ly..."
    )

    run_jianpu_ly(
        safe_musicxml,
        ly_file
    )

    print(
        "產生:",
        ly_file
    )

    # --------------------------------------------------------
    # 顯示 score.ly 前 5 行
    # --------------------------------------------------------

    print()

    print(
        "===== score.ly 前 5 行 ====="
    )

    try:

        with open(
            ly_file,
            "r",
            encoding="utf-8",
            errors="replace"
        ) as f:

            for i in range(5):

                line = f.readline()

                if not line:
                    break

                print(
                    line.rstrip()
                )

    except Exception as e:

        print(
            "無法讀取 score.ly:",
            e
        )

    print(
        "============================"
    )

    # --------------------------------------------------------
    # 3. LilyPond 編譯
    # --------------------------------------------------------

    output_prefix = os.path.splitext(
        pdf_file
    )[0]

    generated_pdf = run_lilypond(
        ly_file,
        output_prefix
    )

    # --------------------------------------------------------
    # 4. 最終 PDF
    # --------------------------------------------------------

    if os.path.abspath(
        generated_pdf
    ) != os.path.abspath(
        pdf_file
    ):

        if os.path.exists(
            pdf_file
        ):

            os.remove(
                pdf_file
            )

        shutil.move(
            generated_pdf,
            pdf_file
        )

    print()

    print(
        "========================================"
    )

    print(
        "[6/6] 完成"
    )

    print(
        "數字簡譜 PDF:",
        pdf_file
    )

    print(
        "========================================"
    )


# ============================================================
# CMD
# ============================================================

if __name__ == "__main__":

    if len(sys.argv) < 3:

        print(
            "用法:"
        )

        print(
            "python jianpu_pdf.py input.musicxml output.pdf"
        )

        sys.exit(1)

    try:

        create_pdf(
            sys.argv[1],
            sys.argv[2]
        )

    except Exception as e:

        print()

        print(
            "❌ 錯誤:"
        )

        print(
            e
        )

        sys.exit(1)