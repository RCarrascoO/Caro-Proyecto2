import json
import time
import threading
import argparse
import paho.mqtt.client as mqtt

results = []
lock = threading.Lock()


def on_connect(client, userdata, flags, rc):
    print('connected rc=', rc)
    client.subscribe(userdata['topic'])


def on_message(client, userdata, msg):
    payload = msg.payload.decode(errors='ignore')
    print('got message', payload)
    with lock:
        results.append({'topic': msg.topic, 'payload': payload, 'ts': int(time.time())})
        if len(results) >= userdata.get('max_messages', 10):
            # stop loop
            client.disconnect()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--broker', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=1883)
    parser.add_argument('--topic', default='DATA/MP')
    parser.add_argument('--timeout', type=int, default=20)
    parser.add_argument('--max', type=int, default=10)
    args = parser.parse_args()

    userdata = {'topic': args.topic, 'max_messages': args.max}
    client = mqtt.Client(userdata=userdata)
    client.user_data_set(userdata)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(args.broker, args.port, 60)
    # run loop in this thread; will exit when disconnect called or on timeout
    def run_loop():
        client.loop_forever()

    t = threading.Thread(target=run_loop, daemon=True)
    t.start()

    start = time.time()
    try:
        while time.time() - start < args.timeout:
            with lock:
                if len(results) >= args.max:
                    break
            time.sleep(0.2)
    except KeyboardInterrupt:
        pass
    # ensure disconnect
    try:
        client.disconnect()
    except Exception:
        pass

    # write results
    with open('sniff_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print('Wrote sniff_results.json with', len(results), 'entries')


if __name__ == '__main__':
    main()
