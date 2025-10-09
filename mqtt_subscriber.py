#!/usr/bin/env python3
"""
Cliente MQTT suscriptor genérico.
- Suscribe a un topic, parsea mensajes con 5 valores: mp01, mp25, mp10, temp, hr
- Mantiene un buffer circular de 10 muestras y genera un gráfico con matplotlib
- Envía la imagen a Telegram usando Bot API (requests)

Soporta modo simulado para pruebas sin broker.
"""
import argparse
import json
import logging
import signal
import sys
import time
from collections import deque
from io import BytesIO

import matplotlib
# Usar backend no interactivo para generar imágenes en background sin GUI
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import paho.mqtt.client as mqtt
import requests

LOG = logging.getLogger("mqtt_subscriber")


def default_config():
    return {
        "broker": "127.0.0.1",
        "port": 1883,
        "topic": "DATA/MP",
        "client_id": "cliente1",
        "bot_token": "",
        "chat_id": "",
        "simulate": False,
        "publish_interval": 2
    }


class MQTTClient:
    def __init__(self, cfg):
        self.cfg = cfg
        self.buffer = deque(maxlen=10)  # mantiene diccionarios con mp01,mp25,mp10,temp,hr
        self.running = True

        self.mqttc = mqtt.Client(client_id=cfg.get("client_id"))
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_message = self.on_message

    def start(self):
        if self.cfg.get("simulate"):
            LOG.info("Modo simulado ON: generando datos de prueba")
            self._simulate_loop()
            return

        try:
            self.mqttc.connect(self.cfg.get("broker"), int(self.cfg.get("port", 1883)), 60)
        except Exception as e:
            LOG.exception("No se pudo conectar al broker: %s", e)
            return
        self.mqttc.loop_start()
        # Mantener el proceso vivo
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            LOG.info("Interrumpido por usuario")
        finally:
            self.mqttc.loop_stop()
            self.mqttc.disconnect()

    def stop(self):
        self.running = False

    def on_connect(self, client, userdata, flags, rc):
        LOG.info("Conectado al broker, código %s. Suscribiendo a %s", rc, self.cfg.get("topic"))
        client.subscribe(self.cfg.get("topic"))

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode(errors="ignore").strip()
        LOG.debug("Mensaje recibido en %s: %s", msg.topic, payload)
        parsed = self.parse_payload(payload)
        if parsed is None:
            LOG.warning("Payload con formato inesperado: %s", payload)
            return
        self.buffer.append(parsed)
        # Generar y enviar gráfico cada vez (puedes cambiar la lógica para enviar solo con 10 muestras)
        try:
            img = self.generate_plot()
            if self.cfg.get("bot_token") and self.cfg.get("chat_id"):
                self.send_telegram(img)
        except Exception:
            LOG.exception("Error generando o enviando el gráfico")

    def parse_payload(self, payload: str):
        # Espera: mp01,mp25,mp10,temp,hr
        parts = [p.strip() for p in payload.replace("\n", "").split(",") if p.strip()]
        if len(parts) < 5:
            return None
        try:
            mp01, mp25, mp10, temp, hr = map(float, parts[:5])
            return {"mp01": mp01, "mp25": mp25, "mp10": mp10, "temp": temp, "hr": hr}
        except ValueError:
            return None

    def generate_plot(self):
        # Extraer series
        data = list(self.buffer)
        if not data:
            raise RuntimeError("Buffer vacío")

        xs = list(range(1, len(data) + 1))
        mp01 = [d["mp01"] for d in data]
        mp25 = [d["mp25"] for d in data]
        mp10 = [d["mp10"] for d in data]
        temp = [d["temp"] for d in data]
        hr = [d["hr"] for d in data]

        fig, axes = plt.subplots(5, 1, sharex=True, figsize=(8, 10))
        fig.suptitle("Medicion MP1, MP2.5, MP10um - Tempe, HR")

        axes[0].plot(xs, mp01, '-o', color='blue')
        axes[0].set_ylabel('ug/m3')
        axes[0].grid(True)
        axes[0].legend(['MP01'])

        axes[1].plot(xs, mp25, '-o', color='green')
        axes[1].set_ylabel('ug/m3')
        axes[1].grid(True)
        axes[1].legend(['MP25'])

        axes[2].plot(xs, mp10, '-o', color='red')
        axes[2].set_ylabel('ug/m3')
        axes[2].grid(True)
        axes[2].legend(['MP10'])

        axes[3].plot(xs, temp, '-o', color='blue')
        axes[3].set_ylabel('Tempe')
        axes[3].grid(True)
        axes[3].legend(['Tempe'])

        axes[4].plot(xs, hr, '-o', color='red')
        axes[4].set_ylabel('HR(%)')
        axes[4].grid(True)
        axes[4].legend(['HR(%)'])

        axes[-1].set_xlabel('Samples')

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])

        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=150)
        plt.close(fig)
        buf.seek(0)
        return buf

    def send_telegram(self, img_buf: BytesIO):
        token = self.cfg.get("bot_token")
        chat_id = self.cfg.get("chat_id")
        url = f"https://api.telegram.org/bot{token}/sendPhoto"
        files = {"photo": ("report.png", img_buf, "image/png")}
        data = {"chat_id": chat_id, "caption": f"Reporte {self.cfg.get('client_id')}"}
        try:
            resp = requests.post(url, data=data, files=files, timeout=15)
            resp.raise_for_status()
            LOG.info("Enviado gráfico a Telegram chat_id=%s", chat_id)
        except Exception:
            LOG.exception("Error enviando foto a Telegram")

    def _simulate_loop(self):
        import random

        try:
            while self.running:
                # Generar datos aleatorios realistas
                mp01 = random.uniform(0, 5)
                mp25 = random.uniform(5, 40)
                mp10 = random.uniform(10, 50)
                temp = random.uniform(15, 30)
                hr = random.uniform(30, 80)
                payload = f"{mp01:.2f},{mp25:.2f},{mp10:.2f},{temp:.2f},{hr:.2f}"
                parsed = self.parse_payload(payload)
                self.buffer.append(parsed)
                LOG.info("Sim: %s", payload)
                # Generar y guardar imagen localmente para verificación (y enviar si se configuró)
                img = self.generate_plot()
                # Guardar a disco con timestamp para inspección
                ts = int(time.time())
                with open(f"report_{self.cfg.get('client_id')}_{ts}.png", "wb") as f:
                    f.write(img.read())
                    img.seek(0)
                img.seek(0)
                if self.cfg.get("bot_token") and self.cfg.get("chat_id"):
                    self.send_telegram(img)
                time.sleep(float(self.cfg.get("publish_interval", 2)))
        except KeyboardInterrupt:
            LOG.info("Simulado: interrumpido por usuario")


def load_config(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', required=True, help='Ruta a config JSON')
    parser.add_argument('--loglevel', default='INFO')
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.loglevel.upper(), logging.INFO),
                        format='%(asctime)s [%(levelname)s] %(message)s')

    cfg = default_config()
    usercfg = load_config(args.config)
    cfg.update(usercfg)

    client = MQTTClient(cfg)

    def _sigint(signum, frame):
        LOG.info('Recibida señal de terminación')
        client.stop()

    signal.signal(signal.SIGINT, _sigint)
    signal.signal(signal.SIGTERM, _sigint)

    client.start()


if __name__ == '__main__':
    main()
