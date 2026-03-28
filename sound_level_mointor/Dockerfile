FROM ghcr.io/home-assistant/base:3.19

# Install python + pip only (no ffmpeg via apk)
RUN apk add --no-cache python3 py3-pip \
    && pip3 install numpy paho-mqtt

WORKDIR /app
COPY run.py .

CMD ["python3", "run.py"]
