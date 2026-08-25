import os
import sys
import shutil
import subprocess
import tempfile


# ============================================================
# JianpuTool Professional MVP 3.0
#
# MusicXML -> Jianpu PDF
#
# Windows / Linux / Streamlit Cloud
#
# Pipeline:
#
# MusicXML
#    ↓
# jianpu-ly
#    ↓
# score.ly
#    ↓
# LilyPond
#    ↓
# jianpu.pdf
# ============================================================


# ============================================================
# 基本設定
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# ============================================================
# 找 LilyPond
# ============================================================

def find_lilypond():

    candidates = []

    # --------------------------------------------------------
    # Windows 常見位置
    # --------------------------------------------------------

    if os.name == "nt":

        candidates.extend([
            r"C:\lilypond-2.26.0\bin\lilypond.exe",
            r"C:\lilypond-2.24.4\bin\lilypond.exe",
            r"C:\lilypond-2.22.0\bin\lilypond.exe",
            r"C:\lilypond-2.20.0\bin\lilypond.exe",
        ])

    # --------------------------------------------------------
    # Linux / Streamlit Cloud
    # --------------------------------------------------------

    candidates.extend([
        "/usr/bin/lilypond",
        "/usr/local/bin/lilypond",
    ])

    # --------------------------------------------------------
    # PATH
    # --------------------------------------------------------

    path_lilypond = shutil.which(
        "lilypond"
    )

    if path_lilypond:
        candidates.append(
            path_lilypond
        )

    # --------------------------------------------------------
    # 實際檢查
    # --------------------------------------------------------

    checked = set()

    for path in candidates:

        if not path:
            continue

        path = os.path.abspath(path)

        if path in checked:
            continue

        checked.add(path)

        if os.path.isfile(path):

            return path

    raise FileNotFoundError(
        "找不到 LilyPond。\n\n"
        "已檢查：\n"
        + "\n".join(candidates)
    )


# ============================================================
# 找 jianpu-ly
# ============================================================

def find_jianpu_ly():

    path = shutil.which(
        "jianpu-ly"
    )

    if path:

        return path

    # Python module fallback
    try:

        import jianpu_ly

        module_path = os.path.dirname(
            os.path.abspath(
                jianpu_ly.__file__
            )
        )

        possible = [
            os.path.join(
                module_path,
                "jianpu-ly"
            ),
            os.path.join(
                module_path,
                "__main__.py"
            ),
        ]

        for p in possible:

            if os.path.isfile(p):

                return p

    except Exception:
        pass

    raise FileNotFoundError(
        "找不到 jianpu-ly。"
    )


# ============================================================
# 執行命令
# ============================================================

def run_command(
    cmd,
    name,
    cwd=None
):

    print()
    print("=" * 60)
    print(name)
    print("=" * 60)

    print(
        "Command:"
    )

    print(
        " ".join(
            f'"{x}"' if " " in str(x)
            else str(x)
            for x in cmd
        )
    )

    print()

    env = os.environ.copy()

    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    try:

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=cwd,
            env=env
        )

    except Exception as e:

        raise RuntimeError(
            f"{name} 執行例外：\n{e}"
        ) from e

    output = result.stdout or ""

    print(output)

    if result.returncode != 0:

        raise RuntimeError(
            f"\n"
            f"{name} 失敗\n\n"
            f"Exit code: {result.returncode}\n\n"
            f"===== 完整輸出 =====\n"
            f"{output}"
        )

    print(
        f"✅ {name} 成功"
    )

    return output


# ============================================================
# 檢查 LilyPond 版本
# ============================================================

def check_lilypond_version(
    lilypond
):

    print()
    print("=" * 60)
    print("檢查 LilyPond")
    print("=" * 60)

    print(
        f"LilyPond: {lilypond}"
    )

    try:

        result = subprocess.run(
            [
                lilypond,
                "--version"
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

    except Exception as e:

        print(
            "⚠ LilyPond 版本檢查失敗:",
            e
        )


# ============================================================
# 檢查 MusicXML
# ============================================================

def check_input(
    input_xml
):

    if not os.path.isfile(
        input_xml
    ):

        raise FileNotFoundError(
            f"找不到 MusicXML：\n"
            f"{input_xml}"
        )

    size = os.path.getsize(
        input_xml
    )

    if size <= 0:

        raise RuntimeError(
            "MusicXML 是空檔案"
        )

    print(
        f"✓ MusicXML："
        f"{input_xml}"
    )

    print(
        f"✓ 大小："
        f"{size:,} bytes"
    )


# ============================================================
# 找 PDF
# ============================================================

def find_generated_pdf(
    output_dir,
    basename
):

    expected = os.path.join(
        output_dir,
        basename + ".pdf"
    )

    if os.path.isfile(
        expected
    ):

        return expected

    # LilyPond 有時會使用 .pdf
    # 搜尋目錄

    if os.path.isdir(
        output_dir
    ):

        for name in os.listdir(
            output_dir
        ):

            if (
                name.lower().endswith(".pdf")
                and
                os.path.splitext(name)[0]
                == basename
            ):

                return os.path.join(
                    output_dir,
                    name
                )

    return None


# ============================================================
# MusicXML -> Jianpu PDF
# ============================================================

def convert(
    input_xml,
    output_pdf
):

    print()
    print("=" * 70)
    print("🎼 MusicXML -> 數字簡譜 PDF")
    print("Professional MVP 3.0")
    print("=" * 70)

    input_xml = os.path.abspath(
        input_xml
    )

    output_pdf = os.path.abspath(
        output_pdf
    )

    # --------------------------------------------------------
    # 檢查輸入
    # --------------------------------------------------------

    check_input(
        input_xml
    )

    # --------------------------------------------------------
    # Output directory
    # --------------------------------------------------------

    output_dir = os.path.dirname(
        output_pdf
    )

    if not output_dir:

        output_dir = BASE_DIR

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    # --------------------------------------------------------
    # 找工具
    # --------------------------------------------------------

    lilypond = find_lilypond()

    jianpu = find_jianpu_ly()

    print()
    print(
        f"LilyPond: {lilypond}"
    )

    print(
        f"jianpu-ly: {jianpu}"
    )

    # --------------------------------------------------------
    # LilyPond version
    # --------------------------------------------------------

    check_lilypond_version(
        lilypond
    )

    # --------------------------------------------------------
    # 建立暫存目錄
    # --------------------------------------------------------

    temp_dir = tempfile.mkdtemp(
        prefix="jianputool_"
    )

    print()
    print(
        f"暫存目錄：{temp_dir}"
    )

    # --------------------------------------------------------
    # score.ly
    # --------------------------------------------------------

    ly_path = os.path.join(
        temp_dir,
        "score.ly"
    )

    # --------------------------------------------------------
    # 產生 LilyPond
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("轉換 jianpu-ly")
    print("=" * 60)

    # --------------------------------------------------------
    # jianpu-ly CLI
    #
    # 正常使用：
    #
    # jianpu-ly input.musicxml
    #
    # stdout → .ly
    # --------------------------------------------------------

    try:

        result = subprocess.run(
            [
                jianpu,
                input_xml
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

    except Exception as e:

        raise RuntimeError(
            f"jianpu-ly 執行失敗：\n{e}"
        ) from e

    ly_output = result.stdout or ""

    print(
        ly_output
    )

    if result.returncode != 0:

        raise RuntimeError(
            "jianpu-ly 轉換失敗\n\n"
            f"Exit code: {result.returncode}\n\n"
            "===== jianpu-ly 完整輸出 =====\n"
            f"{ly_output}"
        )

    # --------------------------------------------------------
    # 判斷 stdout 是否真的有 LilyPond
    # --------------------------------------------------------

    if (
        "\\version" not in ly_output
        and
        "\\score" not in ly_output
    ):

        raise RuntimeError(
            "jianpu-ly 沒有產生有效 LilyPond 程式碼。\n\n"
            "===== jianpu-ly output =====\n"
            f"{ly_output}"
        )

    # --------------------------------------------------------
    # 寫入 score.ly
    # --------------------------------------------------------

    with open(
        ly_path,
        "w",
        encoding="utf-8",
        newline="\n"
    ) as f:

        f.write(
            ly_output
        )

    if not os.path.isfile(
        ly_path
    ):

        raise RuntimeError(
            "score.ly 建立失敗"
        )

    ly_size = os.path.getsize(
        ly_path
    )

    print()
    print(
        f"✓ score.ly："
        f"{ly_path}"
    )

    print(
        f"✓ score.ly 大小："
        f"{ly_size:,} bytes"
    )

    # --------------------------------------------------------
    # 修正 output basename
    # --------------------------------------------------------

    final_basename = os.path.splitext(
        os.path.basename(
            output_pdf
        )
    )[0]

    # --------------------------------------------------------
    # LilyPond
    # --------------------------------------------------------

    lily_cmd = [
        lilypond,
        "--pdf",
        "-o",
        os.path.join(
            output_dir,
            final_basename
        ),
        ly_path
    ]

    lily_output = run_command(
        lily_cmd,
        "LilyPond PDF 編譯",
        cwd=temp_dir
    )

    # --------------------------------------------------------
    # 找 PDF
    # --------------------------------------------------------

    generated_pdf = find_generated_pdf(
        output_dir,
        final_basename
    )

    # --------------------------------------------------------
    # 有些 LilyPond 版本輸出在 temp_dir
    # --------------------------------------------------------

    if generated_pdf is None:

        temp_pdf = os.path.join(
            temp_dir,
            final_basename + ".pdf"
        )

        if os.path.isfile(
            temp_pdf
        ):

            import shutil as _shutil

            _shutil.copy2(
                temp_pdf,
                output_pdf
            )

            generated_pdf = output_pdf

    # --------------------------------------------------------
    # 最終檢查
    # --------------------------------------------------------

    if generated_pdf is None:

        raise RuntimeError(
            "LilyPond 編譯完成但找不到 PDF。\n\n"
            f"預期：{output_pdf}\n\n"
            "===== LilyPond 完整輸出 =====\n"
            f"{lily_output}"
        )

    # --------------------------------------------------------
    # 如果產生的檔名不同，複製到指定位置
    # --------------------------------------------------------

    if os.path.abspath(
        generated_pdf
    ) != os.path.abspath(
        output_pdf
    ):

        shutil.copy2(
            generated_pdf,
            output_pdf
        )

    # --------------------------------------------------------
    # 最終確認
    # --------------------------------------------------------

    if not os.path.isfile(
        output_pdf
    ):

        raise RuntimeError(
            f"PDF 產生失敗：\n"
            f"{output_pdf}"
        )

    pdf_size = os.path.getsize(
        output_pdf
    )

    if pdf_size <= 0:

        raise RuntimeError(
            "PDF 是空檔案"
        )

    print()
    print("=" * 70)
    print("🎉🎉🎉 PDF 成功產生 🎉🎉🎉")
    print("=" * 70)

    print(
        f"MusicXML：{input_xml}"
    )

    print(
        f"LilyPond：{lilypond}"
    )

    print(
        f"jianpu-ly：{jianpu}"
    )

    print(
        f"PDF：{output_pdf}"
    )

    print(
        f"大小：{pdf_size:,} bytes"
    )

    print("=" * 70)

    return output_pdf


# ============================================================
# CMD
# ============================================================

if __name__ == "__main__":

    if len(sys.argv) < 3:

        print(
            "用法："
        )

        print(
            "python jianpu_pdf.py "
            "input.musicxml "
            "output.pdf"
        )

        sys.exit(1)

    input_xml = sys.argv[1]

    output_pdf = sys.argv[2]

    try:

        convert(
            input_xml,
            output_pdf
        )

    except Exception as e:

        print()
        print("=" * 70)
        print("❌ MusicXML -> PDF 失敗")
        print("=" * 70)

        print(
            str(e)
        )

        print("=" * 70)

        sys.exit(1)