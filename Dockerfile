FROM python:3.10

# 安裝 LilyPond
RUN apt-get update && \
    apt-get install -y lilypond && \
    rm -rf /var/lib/apt/lists/*

# 工作目錄
WORKDIR /app

# 安裝 Python 套件
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# 複製專案
COPY . .

# 啟動 FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]