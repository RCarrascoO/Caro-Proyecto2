import argparse
import json
import time
import requests
import os
import importlib.util
import sys


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


def send_stream(server, data_bytes, headers=None):
    url = server.rstrip('/') + '/upload-stream'
    hdrs = {'Content-Type': 'application/octet-stream'}
    if headers:
        hdrs.update(headers)
    r = requests.post(url, data=data_bytes, headers=hdrs, timeout=20)
    r.raise_for_status()
    return r.json()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', default=DEFAULT_SERVER)
    parser.add_argument('--client-id', default='client1')
    parser.add_argument('--simulate', action='store_true')
    parser.add_argument('--json-file', help='Path to JSON payload (if provided, send this)')
    parser.add_argument('--stream-file', help='Path to a binary file to send as stream')
    parser.add_argument('--data-file', help='Path to data.dat (binary) to parse and send')
    args = parser.parse_args()

    # Helper: try to import the local src.data_parser or load by path
    def _load_parse_file():
        try:
            from src.data_parser import parse_file
            return parse_file
        except Exception:
            # Try loading relative to src folder
            base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            module_path = os.path.join(base, 'data_parser.py')
            if os.path.exists(module_path):
                spec = importlib.util.spec_from_file_location('data_parser', module_path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                return mod.parse_file
        return None

    parse_file = _load_parse_file()

    if args.json_file:
        with open(args.json_file, 'r', encoding='utf-8') as f:
            payload = json.load(f)
    else:
        # If a data file is provided, parse it and build payload
        if args.data_file and parse_file and os.path.exists(args.data_file):
            records = parse_file(args.data_file)
            # Convert parser records to server-expected samples
            samples = []
            now = int(time.time())
            # assign timestamps decreasing for readability
            for i, r in enumerate(records[-10:]):
                samples.append({
                    'ts': now - (len(records[-10:]) - 1 - i) * 60,
                    'mp01': r.get('mp01'),
                    'mp25': r.get('mp25'),
                    'mp10': r.get('mp10'),
                    'temp': r.get('te'),
                    'hr': r.get('hr')
                })
            payload = {'client_id': f'client{records[-1].get("id") if records else args.client_id}', 'samples': samples}
        else:
            payload = make_sample_payload(args.client_id)

    print('Sending JSON to', args.server)
    res = send_json(args.server, payload)
    print('JSON response:', res)

    # For stream: prefer sending the raw binary data file if provided, otherwise stream-file, otherwise JSON bytes
    headers = None
    if args.data_file and os.path.exists(args.data_file):
        with open(args.data_file, 'rb') as f:
            data_bytes = f.read()
        # instruct server to parse the uploaded stream
        headers = {'X-PARSE': '1'}
    elif args.stream_file and os.path.exists(args.stream_file):
        with open(args.stream_file, 'rb') as f:
            data_bytes = f.read()
    else:
        data_bytes = json.dumps(payload).encode('utf-8')

    print('Sending stream to', args.server)
    res2 = send_stream(args.server, data_bytes, headers=headers)
    print('Stream response:', res2)


if __name__ == '__main__':
    main()
