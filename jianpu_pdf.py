import os
import sys
import subprocess
import shutil
import tempfile
import re
import xml.etree.ElementTree as ET


# ============================================================
# JianpuTool - jianpu_pdf.py
#
# MusicXML -> jianpu-ly -> LilyPond -> PDF
#
# 支援：
# Windows
# Linux
# Hugging Face Spaces
# Docker
#
# jianpu-ly 1.872
# LilyPond 2.22 / 2.26
# ============================================================


# ============================================================
# LilyPond 路徑
# ============================================================

def find_lilypond():

    env_path = os.environ.get("LILYPOND_PATH")

    if env_path and os.path.isfile(env_path):
        return env_path

    exe = shutil.which("lilypond")

    if exe:
        return exe

    if os.name == "nt":

        candidates = [
            r"C:\lilypond-2.22.2\usr\bin\lilypond.exe",
            r"C:\lilypond-2.26.0\bin\lilypond.exe",
            r"C:\Program Files\LilyPond\usr\bin\lilypond.exe",
        ]

        for path in candidates:
            if os.path.isfile(path):
                return path

    linux_candidates = [
        "/usr/bin/lilypond",
        "/usr/local/bin/lilypond",
        "/opt/lilypond/bin/lilypond",
    ]

    for path in linux_candidates:
        if os.path.isfile(path):
            return path

    raise Exception(
        "找不到 LilyPond。\n\n"
        "Windows：請確認已安裝 LilyPond。\n"
        "Linux/Docker：請確認 Dockerfile 已安裝 LilyPond。\n"
        "也可以設定 LILYPOND_PATH。"
    )


# ============================================================
# 找 jianpu-ly
# ============================================================

def find_jianpu_ly():

    candidates = [
        shutil.which("jianpu-ly"),
        shutil.which("jianpu_ly"),
    ]

    for exe in candidates:
        if exe:
            return exe

    if os.name == "nt":

        candidates = [

            r"C:\Users\user\AppData\Local\Programs\Python\Python310\Scripts\jianpu-ly.exe",

            r"C:\Users\user\AppData\Roaming\Python\Python310\Scripts\jianpu-ly.exe",

        ]

        for path in candidates:
            if os.path.isfile(path):
                return path

    candidates = [
        "/home/adminuser/venv/bin/jianpu-ly",
        "/usr/local/bin/jianpu-ly",
        "/usr/bin/jianpu-ly",
    ]

    for path in candidates:
        if os.path.isfile(path):
            return path

    raise Exception(
        "找不到 jianpu-ly。\n\n"
        "請確認 requirements.txt 包含：\n"
        "jianpu-ly==1.872"
    )


# ============================================================
# MusicXML 音域安全處理
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

        while octave < 1:

            octave += 1
            octave_element.text = str(octave)
            changed += 1

    if changed == 0:

        print("[6/6] 音域正常")

        return musicxml_file

    work_dir = os.path.dirname(
        os.path.abspath(musicxml_file)
    )

    filename = os.path.basename(
        musicxml_file
    )

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
# 清理 LilyPond 前方訊息
# ============================================================

def clean_lilypond_file(ly_file):

    with open(
        ly_file,
        "r",
        encoding="utf-8",
        errors="replace"
    ) as f:

        content = f.read()

    if not content.strip():
        raise Exception(
            "jianpu-ly 產生的 LilyPond 檔案是空的"
        )

    lines = content.splitlines()

    valid_start = None

    for i, line in enumerate(lines):

        stripped = line.strip()

        if (
            stripped.startswith(r"\version")
            or stripped.startswith("#(")
            or stripped.startswith(r"\header")
            or stripped.startswith(r"\paper")
            or stripped.startswith(r"\layout")
        ):

            valid_start = i
            break

    if valid_start is not None and valid_start > 0:

        print(
            f"⚠ 清除 LilyPond 前方 "
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
# 搜尋 jianpu-ly 產生的 .ly
# ============================================================

def find_generated_ly(output_text, before_files):

    # --------------------------------------------------------
    # 方法 1：
    # 從 jianpu-ly 輸出：
    #
    # Outputting to C:\...\Temp/test_new.ly
    #
    # --------------------------------------------------------

    patterns = [
        r"Outputting to\s+(.+\.ly)",
        r"outputting to\s+(.+\.ly)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            output_text,
            re.IGNORECASE
        )

        if match:

            path = match.group(1).strip()

            # 去掉可能的引號
            path = path.strip('"').strip("'")

            if os.path.isfile(path):
                return os.path.abspath(path)

    # --------------------------------------------------------
    # 方法 2：
    # 比較 TEMP 目錄前後差異
    # --------------------------------------------------------

    temp_dir = tempfile.gettempdir()

    try:
        after_files = {
            os.path.abspath(
                os.path.join(temp_dir, f)
            )
            for f in os.listdir(temp_dir)
            if f.lower().endswith(".ly")
        }

    except Exception:
        after_files = set()

    new_files = after_files - before_files

    if new_files:

        newest = max(
            new_files,
            key=lambda p: os.path.getmtime(p)
        )

        if os.path.isfile(newest):
            return newest

    # --------------------------------------------------------
    # 方法 3：
    # 搜尋最近修改的 .ly
    # --------------------------------------------------------

    try:

        candidates = []

        for filename in os.listdir(temp_dir):

            if not filename.lower().endswith(".ly"):
                continue

            path = os.path.join(
                temp_dir,
                filename
            )

            if os.path.isfile(path):

                candidates.append(path)

        if candidates:

            candidates.sort(
                key=lambda p: os.path.getmtime(p),
                reverse=True
            )

            return os.path.abspath(
                candidates[0]
            )

    except Exception:
        pass

    return None


# ============================================================
# MusicXML -> LilyPond
#
# 重要：
#
# jianpu-ly 1.872 不是單純把 LilyPond
# 程式碼輸出到 stdout。
#
# 它會：
#
# MusicXML
#    ↓
# Temp/test_new.ly
#
# 所以這裡必須抓取實際產生的 .ly。
# ============================================================

def run_jianpu_ly(
    musicxml_file,
    ly_file
):

    jianpu_ly_exe = find_jianpu_ly()

    print(
        "jianpu-ly:",
        jianpu_ly_exe
    )

    temp_dir = tempfile.gettempdir()

    # --------------------------------------------------------
    # 記錄執行前的 .ly
    # --------------------------------------------------------

    try:

        before_files = {
            os.path.abspath(
                os.path.join(temp_dir, f)
            )
            for f in os.listdir(temp_dir)
            if f.lower().endswith(".ly")
        }

    except Exception:

        before_files = set()

    # --------------------------------------------------------
    # 執行 jianpu-ly
    # --------------------------------------------------------

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

    combined_output = (
        result.stdout
        + "\n"
        + result.stderr
    )

    print(
        combined_output
    )

    # --------------------------------------------------------
    # jianpu-ly 失敗
    # --------------------------------------------------------

    if result.returncode != 0:

        raise Exception(
            "jianpu-ly 轉換失敗\n\n"
            + combined_output
        )

    # --------------------------------------------------------
    # 找實際產生的 .ly
    # --------------------------------------------------------

    generated_ly = find_generated_ly(
        combined_output,
        before_files
    )

    if not generated_ly:

        raise Exception(
            "jianpu-ly 已執行完成，"
            "但找不到產生的 .ly 檔案。\n\n"
            "jianpu-ly 輸出：\n"
            + combined_output
        )

    print(
        "✓ jianpu-ly 產生：",
        generated_ly
    )

    # --------------------------------------------------------
    # 複製到指定 score.ly
    # --------------------------------------------------------

    os.makedirs(
        os.path.dirname(
            os.path.abspath(ly_file)
        ),
        exist_ok=True
    )

    shutil.copyfile(
        generated_ly,
        ly_file
    )

    # --------------------------------------------------------
    # 確認
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
    # 清理
    # --------------------------------------------------------

    clean_lilypond_file(
        ly_file
    )

    print(
        "✓ score.ly：",
        ly_file
    )

    print(
        "✓ score.ly 大小：",
        os.path.getsize(ly_file),
        "bytes"
    )


# ============================================================
# LilyPond 編譯
# ============================================================

def run_lilypond(
    ly_file,
    output_prefix
):

    print(
        "LilyPond 編譯..."
    )

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
    # 確保輸出目錄
    # --------------------------------------------------------

    output_dir = os.path.dirname(
        os.path.abspath(output_prefix)
    )

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    # --------------------------------------------------------
    # LilyPond
    # --------------------------------------------------------

    result = subprocess.run(

        [
            lilypond,
            "-o",
            output_prefix,
            ly_file
        ],

        cwd=output_dir,

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
    # PDF
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

    print(
        "✓ LilyPond PDF：",
        generated_pdf
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
    # 輸出資料夾
    # --------------------------------------------------------

    work_dir = (
        os.path.dirname(
            os.path.abspath(pdf_file)
        )
        or "."
    )

    os.makedirs(
        work_dir,
        exist_ok=True
    )

    # --------------------------------------------------------
    # 環境
    # --------------------------------------------------------

    print(
        "作業系統:",
        os.name
    )

    print(
        "LilyPond:",
        find_lilypond()
    )

    print(
        "jianpu-ly:",
        find_jianpu_ly()
    )

    # ========================================================
    # 1. MusicXML 音域安全處理
    # ========================================================

    safe_musicxml = fix_low_octaves(
        musicxml_file
    )

    # ========================================================
    # 2. MusicXML -> LilyPond
    # ========================================================

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
    # 前 5 行
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

            for _ in range(5):

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

    # ========================================================
    # 3. LilyPond
    # ========================================================

    output_prefix = os.path.splitext(
        os.path.abspath(pdf_file)
    )[0]

    generated_pdf = run_lilypond(
        ly_file,
        output_prefix
    )

    # ========================================================
    # 4. 最終 PDF
    # ========================================================

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

    # --------------------------------------------------------
    # 最終確認
    # --------------------------------------------------------

    if not os.path.isfile(
        pdf_file
    ):

        raise Exception(
            "最終 PDF 不存在：\n"
            + pdf_file
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
        "PDF 大小:",
        f"{os.path.getsize(pdf_file):,}",
        "bytes"
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
            "python jianpu_pdf.py "
            "input.musicxml output.pdf"
        )

        sys.exit(1)

    musicxml_file = sys.argv[1]
    pdf_file = sys.argv[2]

    try:

        create_pdf(
            musicxml_file,
            pdf_file
        )

    except Exception as e:

        print()
        print(
            "❌ 錯誤:"
        )

        print(
            str(e)
        )

        sys.exit(1)