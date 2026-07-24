FROM python:3.10

RUN apt-get update && \
    apt-get install -y lilypond && \
    apt-get clean


WORKDIR /app


COPY . .


RUN pip install --no-cache-dir -r requirements.txt


EXPOSE 10000


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]