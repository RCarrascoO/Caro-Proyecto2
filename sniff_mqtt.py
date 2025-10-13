#!/usr/bin/env python3
"""Pequeño subscriber para depuración: imprime payloads recibidos en un topic MQTT."""
import argparse
import time
import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, rc):
    print(f"Connected to broker, rc={rc}. Subscribing to {userdata['topic']}")
    client.subscribe(userdata['topic'])


def on_message(client, userdata, msg):
    print(f"RECEIVED [{msg.topic}] -> {msg.payload.decode(errors='ignore')}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--broker', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=1883)
    parser.add_argument('--topic', default='DATA/MP')
    args = parser.parse_args()

    userdata = {'topic': args.topic}
    client = mqtt.Client(userdata=userdata)
    client.user_data_set(userdata)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(args.broker, args.port, 60)
    client.loop_start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('Interrupted')
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == '__main__':
    main()
