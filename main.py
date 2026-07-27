# main.py
import os
import uuid
import subprocess
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home():
    return '''
    <html><body style="font-family:Arial;text-align:center;margin-top:80px">
    <h1>JianpuTool 簡譜產生器</h1>
    <h2>MP3 → MIDI → MusicXML → 簡譜 PDF</h2>
    <form action="/upload" method="post" enctype="multipart/form-data">
    <input type="file" name="file" accept=".mp3,.wav"><br><br>
    <button type="submit">開始轉換</button>
    </form></body></html>'''

def run_cmd(cmd):
    print("RUN:", " ".join(cmd))
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print(r.stdout)
    return r

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    work_dir=os.path.join("outputs",str(uuid.uuid4()))
    os.makedirs(work_dir,exist_ok=True)
    input_audio=os.path.join(work_dir,file.filename)
    with open(input_audio,"wb") as f:
        f.write(await file.read())

    midi=os.path.join(work_dir,"melody.mid")
    r=run_cmd(["python","basic_pitch_convert.py",input_audio,midi])
    if r.returncode:return {"error":"BasicPitch failed","log":r.stdout}

    qmidi=os.path.join(work_dir,"melody_clean.mid")
    r=run_cmd(["python","midi_quantize.py",midi,qmidi])
    if r.returncode:return {"error":"Quantize failed","log":r.stdout}

    xml=os.path.join(work_dir,"input.musicxml")
    r=run_cmd(["python","midi_to_musicxml.py",qmidi,xml])
    if r.returncode:return {"error":"MusicXML failed","log":r.stdout}

    clean=os.path.join(work_dir,"clean.musicxml")
    r=run_cmd(["python","clean_musicxml.py",xml,clean])
    if r.returncode:return {"error":"Clean failed","log":r.stdout}

    ly=os.path.join(work_dir,"jianpu.ly")
    r=run_cmd(["python","-m","jianpu_ly",clean])
    if r.returncode:return {"error":"jianpu_ly failed","log":r.stdout}
    with open(ly,"w",encoding="utf-8") as f:f.write(r.stdout)

    r=run_cmd(["lilypond","-o",work_dir,ly])
    if r.returncode:return {"error":"lilypond failed","log":r.stdout}

    pdf=os.path.join(work_dir,"jianpu.pdf")
    if not os.path.exists(pdf):
        return {"error":"PDF not created","log":r.stdout}
    return FileResponse(pdf,media_type="application/pdf",filename="jianpu.pdf")
