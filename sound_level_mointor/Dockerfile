FROM ghcr.io/home-assistant/amd64-base-python:3.19

WORKDIR /app

RUN pip3 install numpy paho-mqtt

COPY run.py .

CMD ["python3", "run.py"]
