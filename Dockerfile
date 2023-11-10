FROM python:3.11.4-alpine3.18 as builder

WORKDIR /app
COPY . .

RUN apk add --no-cache ffmpeg && \
    pip install --no-cache -r requirements.txt

USER 1000

ENTRYPOINT python3 /app/main.py
