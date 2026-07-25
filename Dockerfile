FROM python:3.10-slim


WORKDIR /app


COPY . /app


# 安裝系統套件
RUN apt-get update && apt-get install -y \
    lilypond \
    musescore \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*


# 安裝 Python 套件
RUN pip install --no-cache-dir -r requirements.txt


EXPOSE 10000


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]