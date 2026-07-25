from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
import os
import shutil
import uuid


app = FastAPI(
    title="JianpuTool",
    version="1.0"
)


# =========================
# 設定資料夾
# =========================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "outputs"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)



# =========================
# 首頁
# =========================

@app.api_route(
    "/",
    methods=["GET", "HEAD"],
    response_class=HTMLResponse
)
async def index():

    html_path = os.path.join(
        BASE_DIR,
        "index.html"
    )

    if not os.path.exists(html_path):

        return """
        <h1>JianpuTool Running</h1>
        <p>index.html missing</p>
        """


    with open(
        html_path,
        "r",
        encoding="utf-8"
    ) as f:

        return f.read()



# =========================
# 健康檢查
# =========================

@app.get("/health")
async def health():

    return {
        "status": "ok"
    }



# =========================
# 上傳 MP3
# =========================

@app.post("/upload")
async def upload(
    file: UploadFile = File(...)
):

    file_id = str(
        uuid.uuid4()
    )


    filename = (
        file_id
        +
        "_"
        +
        file.filename
    )


    input_path = os.path.join(
        OUTPUT_DIR,
        filename
    )


    print("===================")
    print("收到上傳:")
    print(file.filename)
    print("===================")


    # 儲存檔案

    with open(
        input_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )


    print("保存完成:")
    print(input_path)



    return JSONResponse(

        {
            "status": "upload success",

            "original_name":
                file.filename,

            "saved_file":
                filename,

            "path":
                input_path
        }

    )



# =========================
# 啟動測試
# =========================

@app.get("/test")
async def test():

    return {

        "message":
        "JianpuTool API running"

    }