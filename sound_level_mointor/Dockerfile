FROM python:3.11-slim

RUN apt-get update && apt-get install -y ffmpeg && pip install numpy paho-mqtt

WORKDIR /app
COPY run.py .

CMD ["python", "run.py"]