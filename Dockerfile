FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# ============================================================
# 系統套件
# ============================================================

RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    curl \
    git \
    ca-certificates \
    build-essential \
    pkg-config \
    libsndfile1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# ============================================================
# 安裝 LilyPond 2.22.2
# ============================================================

RUN wget -q \
    https://lilypond.org/download/binaries/linux-64/lilypond-2.22.2-1.linux-64.sh \
    -O /tmp/lilypond.sh \
    && chmod +x /tmp/lilypond.sh \
    && /tmp/lilypond.sh --batch \
    && rm -f /tmp/lilypond.sh

# ============================================================
# 工作目錄
# ============================================================

WORKDIR /app

# ============================================================
# Python 套件
# ============================================================

COPY requirements.txt /app/requirements.txt

RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install -r /app/requirements.txt

# ============================================================
# JianpuTool
# ============================================================

COPY . /app

# ============================================================
# Hugging Face Spaces
# Docker 預設使用 7860
# ============================================================

EXPOSE 7860

# ============================================================
# Streamlit
# ============================================================

CMD ["streamlit", "run", "streamlit_app.py", "--server.address=0.0.0.0", "--server.port=7860", "--server.headless=true"]