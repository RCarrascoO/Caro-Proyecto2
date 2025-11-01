"""Run the full E2E flow locally (cross-platform).

Usage: python run_all.py [--no-install] [--no-generate]

Steps performed:
 - Optionally install requirements from requirements.txt
 - Generate synthetic data.dat (tools/generate_data_dat.py)
 - Start Flask server as a subprocess (module src.http_server.app)
 - Wait until server accepts connections on port 5000
 - Run client to send JSON + stream (src/http_client/send_data.py)
 - Download plot for the client and save locally
 - Stop server subprocess

This provides a single-entry point from project root.
"""
from __future__ import annotations
import argparse
import subprocess
import sys
import time
import urllib.request
import os

ROOT = os.path.abspath(os.path.dirname(__file__))
PY = sys.executable or 'python'


def run(cmd, **kwargs):
    print('>', ' '.join(cmd))
    return subprocess.run(cmd, check=True, **kwargs)


def wait_port(host='127.0.0.1', port=5000, timeout=30.0):
    import socket
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except Exception:
            time.sleep(0.5)
    return False


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--no-install', action='store_true')
    p.add_argument('--no-generate', action='store_true')
    p.add_argument('--server-url', default='http://127.0.0.1:5000')
    p.add_argument('--port', type=int, default=5000)
    args = p.parse_args()
    
    if not args.no_install:
        print('Installing requirements...')
        run([PY, '-m', 'pip', 'install', '-r', 'requirements.txt'])

    if not args.no_generate:
        print('Generating data.dat...')
        run([PY, os.path.join(ROOT, 'tools', 'generate_data_dat.py'), '--out', 'data.dat', '--count', '10', '--stations', '10', '--seed', '42'])

    print('Starting server...')
    server_proc = subprocess.Popen([PY, '-m', 'src.http_server.app'], cwd=ROOT)

    try:
        ok = wait_port(port=args.port, timeout=30.0)
        if not ok:
            print('Server did not start in time; check logs.')
            server_proc.kill()
            raise SystemExit(1)
        print('Server started')

        print('Sending data via client...')
        run([PY, os.path.join(ROOT, 'src', 'http_client', 'send_data.py'), '--server', args.server_url, '--data-file', 'data.dat', '--client-id', 'client1'])

        # download plot
        plot_url = args.server_url.rstrip('/') + '/plot/client1'
        print('Downloading plot from', plot_url)
        try:
            with urllib.request.urlopen(plot_url, timeout=10) as r:
                data = r.read()
                with open('plot_client1.png', 'wb') as f:
                    f.write(data)
                print('Saved plot_client1.png')
        except Exception as e:
            print('Failed to download plot:', e)

    finally:
        print('Stopping server...')
        server_proc.terminate()
        try:
            server_proc.wait(timeout=5)
        except Exception:
            server_proc.kill()
