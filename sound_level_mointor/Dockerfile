ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM $BUILD_FROM

# Use built-in python from HA base image
RUN python3 -m ensurepip \
    && pip3 install numpy paho-mqtt

WORKDIR /app
COPY run.py .

CMD ["python3", "run.py"]
