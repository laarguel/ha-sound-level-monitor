import subprocess
import numpy as np
import time
import json
import os
import paho.mqtt.client as mqtt
from collections import deque

CONFIG_PATH = "/data/options.json"

with open(CONFIG_PATH) as f:
    config = json.load(f)

mqtt_conf = config["mqtt"]
client = mqtt.Client()
client.username_pw_set(mqtt_conf["username"], mqtt_conf["password"])

def connect_mqtt():
    while True:
        try:
            client.connect(mqtt_conf["host"], 1883, 60)
            client.loop_start()
            return
        except:
            time.sleep(5)

connect_mqtt()

def start_ffmpeg(rtsp):
    return subprocess.Popen(
        [
            "ffmpeg",
            "-rtsp_transport", "tcp",
            "-i", rtsp,
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "44100",
            "-ac", "1",
            "-f", "s16le",
            "-"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL
    )

def publish_discovery(name):
    base = f"homeassistant/sensor/{name}_sound/config"
    payload = {
        "name": f"{name} Sound Level",
        "state_topic": f"home/sound/{name}/db",
        "unit_of_measurement": "dB",
        "state_class": "measurement",
        "device_class": "sound_pressure",
        "unique_id": f"{name}_sound"
    }
    client.publish(base, json.dumps(payload), retain=True)

    base_bin = f"homeassistant/binary_sensor/{name}_loud/config"
    payload_bin = {
        "name": f"{name} Loud",
        "state_topic": f"home/sound/{name}/loud",
        "payload_on": "ON",
        "payload_off": "OFF",
        "unique_id": f"{name}_loud"
    }
    client.publish(base_bin, json.dumps(payload_bin), retain=True)

class CameraWorker:
    def __init__(self, name, rtsp):
        self.name = name
        self.rtsp = rtsp
        self.proc = None
        self.buffer = deque(maxlen=config["smoothing_window"])
        publish_discovery(name)

    def restart(self):
        if self.proc:
            self.proc.kill()
        self.proc = start_ffmpeg(self.rtsp)

    def run(self):
        chunk = int(44100 * config["sampling_seconds"])
        while True:
            try:
                if not self.proc:
                    self.restart()

                raw = self.proc.stdout.read(chunk * 2)
                if not raw:
                    self.restart()
                    continue

                audio = np.frombuffer(raw, dtype=np.int16)
                rms = np.sqrt(np.mean(audio**2))
                db = 20 * np.log10(rms + 1)

                self.buffer.append(db)
                smooth_db = sum(self.buffer) / len(self.buffer)

                topic_base = f"home/sound/{self.name}"

                client.publish(f"{topic_base}/db", round(smooth_db, 2))

                if smooth_db > config["noise_threshold_db"]:
                    client.publish(f"{topic_base}/loud", "ON")
                else:
                    client.publish(f"{topic_base}/loud", "OFF")

            except Exception:
                time.sleep(2)
                self.restart()

workers = []

for cam in config["cameras"]:
    workers.append(CameraWorker(cam["name"], cam["rtsp"]))

for w in workers:
    import threading
    threading.Thread(target=w.run, daemon=True).start()

while True:
    time.sleep(60)