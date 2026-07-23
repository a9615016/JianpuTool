@app.get("/", response_class=HTMLResponse)
def home():

    return """
    <!DOCTYPE html>
    <html>

    <head>
        <meta charset="utf-8">
        <title>JianpuTool</title>
    </head>


    <body>

        <h1>🎵 JianpuTool</h1>

        <h2>MIDI → 數字簡譜 PDF</h2>


        <form action="/midi" method="post" enctype="multipart/form-data">

            <input 
                type="file" 
                name="file"
                accept=".mid,.midi"
            >

            <br><br>


            <button type="submit">

                產生簡譜 PDF

            </button>


        </form>


    </body>

    </html>
    