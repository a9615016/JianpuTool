from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
import os
import uuid
import subprocess
from music21 import converter

app = FastAPI()


BASE_DIR = "outputs"
os.makedirs(BASE_DIR, exist_ok=True)


def check_musicxml_measures(xml_file):

    print("==============================")
    print("開始 MusicXML 小節檢查")
    print(xml_file)
    print("==============================")


    try:
        score = converter.parse(xml_file)

    except Exception as e:
        print("MusicXML讀取失敗")
        print(e)
        return False


    error_found = False


    for part in score.parts:

        print("Part:", part.id)

        for measure in part.getElementsByClass("Measure"):

            total = 0

            print("\n----------------")
            print("Measure", measure.number)


            for idx, n in enumerate(measure.notesAndRests):

                dur = float(n.duration.quarterLength)

                total += dur


                if n.isRest:
                    name = "REST"

                else:
                    name = n.pitch.nameWithOctave


                print(
                    f"{idx}: "
                    f"{name} "
                    f"duration={dur} "
                    f"offset={n.offset}"
                )


            print(
                "Measure total:",
                total
            )


            # 4/4檢查
            if abs(total - 4.0) > 0.001:

                error_found = True

                print("!!! ERROR !!!")
                print(
                    f"Measure {measure.number} "
                    f"不是4拍，目前={total}"
                )


    print("==============================")

    if error_found:
        print(
            "發現小節長度錯誤，停止送入 jianpu_ly"
        )

    else:
        print(
            "所有小節正常"
        )

    print("==============================")


    return not error_found



@app.get("/")
def home():

    return HTMLResponse(
        """
        <h2>JianpuTool</h2>

        <form action="/upload"
        method="post"
        enctype="multipart/form-data">

        <input type="file"
        name="file">

        <button>
        Upload
        </button>

        </form>
        """
    )



@app.post("/upload")
async def upload(
    file: UploadFile = File(...)
):

    uid = str(uuid.uuid4())

    workdir = os.path.join(
        BASE_DIR,
        uid
    )

    os.makedirs(
        workdir,
        exist_ok=True
    )


    input_xml = os.path.join(
        workdir,
        file.filename
    )


    with open(
        input_xml,
        "wb"
    ) as f:

        f.write(
            await file.read()
        )


    print("================")
    print("收到:")
    print(file.filename)
    print("================")


    # ==========================
    # 新增 MusicXML 檢查
    # ==========================

    ok = check_musicxml_measures(
        input_xml
    )


    if not ok:

        return {
            "error":
            "MusicXML小節長度錯誤，請查看Render Log"
        }


    # ==========================
    # jianpu_ly
    # ==========================


    ly_file = os.path.join(
        workdir,
        "output.ly"
    )


    print(
        "開始 jianpu_ly"
    )


    result = subprocess.run(
        [
            "python",
            "-m",
            "jianpu_ly",
            input_xml
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )


    print(
        result.stdout
    )


    if result.returncode != 0:

        return {
            "error":
            result.stdout
        }


    with open(
        ly_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            result.stdout
        )


    print(
        "jianpu_ly完成"
    )


    return {
        "status":
        "ok",
        "folder":
        workdir
    }