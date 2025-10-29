import argparse
import json
import time
import requests
import os

DEFAULT_SERVER = 'http://127.0.0.1:5000'


def make_sample_payload(client_id='clientX'):
    # Create a sample payload with 10 samples (simulate data.dat parsing)
    now = int(time.time())
    samples = []
    for i in range(10):
        samples.append({
            'ts': now - (9 - i) * 60,
            'mp01': round(1.0 + i * 0.1, 2),
            'mp25': round(5.0 + i * 0.5, 2),
            'mp10': round(10.0 + i * 0.7, 2),
            'temp': round(20.0 + i * 0.2, 2),
            'hr': round(40.0 + i * 0.3, 2)
        })
    return {'client_id': client_id, 'samples': samples}


def send_json(server, payload):
    url = server.rstrip('/') + '/upload-json'
    r = requests.post(url, json=payload, timeout=15)
    r.raise_for_status()
    return r.json()


def send_stream(server, data_bytes):
    url = server.rstrip('/') + '/upload-stream'
    r = requests.post(url, data=data_bytes, headers={'Content-Type': 'application/octet-stream'}, timeout=20)
    r.raise_for_status()
    return r.json()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', default=DEFAULT_SERVER)
    parser.add_argument('--client-id', default='client1')
    parser.add_argument('--simulate', action='store_true')
    parser.add_argument('--json-file', help='Path to JSON payload (if provided, send this)')
    parser.add_argument('--stream-file', help='Path to a binary file to send as stream')
    args = parser.parse_args()

    if args.json_file:
        with open(args.json_file, 'r', encoding='utf-8') as f:
            payload = json.load(f)
    else:
        payload = make_sample_payload(args.client_id)

    print('Sending JSON to', args.server)
    res = send_json(args.server, payload)
    print('JSON response:', res)

    # For stream, if provided, send file; otherwise send JSON bytes as example
    if args.stream_file and os.path.exists(args.stream_file):
        with open(args.stream_file, 'rb') as f:
            data_bytes = f.read()
    else:
        data_bytes = json.dumps(payload).encode('utf-8')

    print('Sending stream to', args.server)
    res2 = send_stream(args.server, data_bytes)
    print('Stream response:', res2)


if __name__ == '__main__':
    main()
