FROM python:3.10-slim

WORKDIR /app

COPY . /app


RUN apt-get update && apt-get install -y \
    wget \
    xz-utils \
    ca-certificates \
    ffmpeg \
    musescore \
    && rm -rf /var/lib/apt/lists/*


# LilyPond
RUN wget https://gitlab.com/lilypond/lilypond/-/releases/v2.26.0/downloads/lilypond-2.26.0-linux-x86_64.tar.gz \
    && tar -xzf lilypond-2.26.0-linux-x86_64.tar.gz \
    && mv lilypond-2.26.0 /opt/lilypond \
    && ln -s /opt/lilypond/bin/lilypond /usr/local/bin/lilypond \
    && rm lilypond-2.26.0-linux-x86_64.tar.gz


# Python packages
RUN pip install --no-cache-dir -r requirements.txt


EXPOSE 10000


CMD ["uvicorn","main:app","--host","0.0.0.0","--port","10000"]