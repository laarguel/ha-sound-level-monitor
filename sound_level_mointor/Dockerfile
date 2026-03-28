ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:3.19
FROM $BUILD_FROM

RUN apk add --no-cache ffmpeg python3 py3-pip \
    && pip3 install numpy paho-mqtt

WORKDIR /app
COPY run.py .

CMD ["python3", "run.py"]
