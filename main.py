@app.post("/midi")
async def midi(file: UploadFile = File(...)):

    try:

        import subprocess


        # ============
        # 儲存 MIDI
        # ============

        midi_name = str(uuid.uuid4()) + ".mid"

        midi_path = os.path.join(
            UPLOAD_DIR,
            midi_name
        )

        with open(midi_path, "wb") as f:
            f.write(await file.read())


        # ============
        # MIDI → MusicXML
        # ============

        score = converter.parse(
            midi_path
        )


        xml_name = midi_name.replace(
            ".mid",
            ".musicxml"
        )

        xml_path = os.path.join(
            OUTPUT_DIR,
            xml_name
        )


        score.write(
            "musicxml",
            fp=xml_path
        )



        # ============
        # MusicXML → LY
        # ============

        ly_name = xml_name.replace(
            ".musicxml",
            ".ly"
        )

        ly_path = os.path.join(
            OUTPUT_DIR,
            ly_name
        )


        with open(
            ly_path,
            "w",
            encoding="utf-8"
        ) as f:


            subprocess.run(
                [
                    "python",
                    "-m",
                    "jianpu_ly",
                    xml_path
                ],
                stdout=f,
                stderr=subprocess.PIPE,
                check=True
            )



        # ============
        # LY → PDF
        # ============

        subprocess.run(
            [
                "lilypond",
                "-o",
                OUTPUT_DIR,
                ly_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )


        pdf_name = ly_name.replace(
            ".ly",
            ".pdf"
        )


        return {

            "status": "success",

            "midi": midi_name,

            "musicxml": xml_name,

            "jianpu_pdf": pdf_name

        }


    except subprocess.CalledProcessError as e:

        return {

            "status": "command error",

            "error": e.stderr.decode(
                "utf-8",
                errors="ignore"
            )

        }


    except Exception as e:

        return {

            "status": "error",

            "error": str(e)

        }