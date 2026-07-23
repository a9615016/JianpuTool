from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@app.get("/", response_class=HTMLResponse)
def home():

    index_path = os.path.join(
        BASE_DIR,
        "static",
        "index.html"
    )

    with open(index_path, encoding="utf-8") as f:
        return f.read()


@app.get("/status")
def status():
    return {
        "status": "JianpuTool running",
        "api": [
            "/convert",
            "/midi"
        ]
    }