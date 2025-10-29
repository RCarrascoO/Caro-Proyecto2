from flask import Flask, request, jsonify, send_file
import sqlite3
import os
import time
from io import BytesIO

from src.plot_utils import build_timeseries_plot

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
DB_PATH = os.path.join(DATA_DIR, 'data.db')

os.makedirs(DATA_DIR, exist_ok=True)

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id TEXT,
            ts INTEGER,
            mp01 REAL,
            mp25 REAL,
            mp10 REAL,
            temp REAL,
            hr REAL
        )
    ''')
    conn.commit()
    conn.close()


init_db()


@app.route('/upload-json', methods=['POST'])
def upload_json():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'json required'}), 400

    client_id = data.get('client_id', 'unknown')
    samples = data.get('samples')
    if not samples or not isinstance(samples, list):
        return jsonify({'error': 'samples list required'}), 400

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for s in samples:
        ts = int(s.get('ts', time.time()))
        c.execute('INSERT INTO measurements (client_id, ts, mp01, mp25, mp10, temp, hr) VALUES (?,?,?,?,?,?,?)',
                  (client_id, ts, s.get('mp01'), s.get('mp25'), s.get('mp10'), s.get('temp'), s.get('hr')))
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok', 'inserted': len(samples)})


@app.route('/upload-stream', methods=['POST'])
def upload_stream():
    data_bytes = request.get_data()
    if not data_bytes:
        return jsonify({'error': 'no bytes received'}), 400
    # Save raw stream for later parsing
    ts = int(time.time())
    stream_dir = os.path.join(DATA_DIR, 'streams')
    os.makedirs(stream_dir, exist_ok=True)
    fname = os.path.join(stream_dir, f'stream_{ts}.bin')
    with open(fname, 'wb') as f:
        f.write(data_bytes)
    return jsonify({'status': 'ok', 'saved': fname})


@app.route('/plot/<client_id>', methods=['GET'])
def plot_client(client_id):
    # fetch last 10 samples for client_id
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT mp01, mp25, mp10, temp, hr, ts FROM measurements WHERE client_id = ? ORDER BY ts DESC LIMIT 10', (client_id,))
    rows = c.fetchall()
    conn.close()
    if not rows:
        return jsonify({'error': 'no data'}), 404
    # rows are newest first; reverse to chronological
    rows = list(reversed(rows))
    samples = []
    for r in rows:
        samples.append({'mp01': r[0], 'mp25': r[1], 'mp10': r[2], 'temp': r[3], 'hr': r[4], 'ts': r[5]})

    img_buf = build_timeseries_plot(samples)
    return send_file(img_buf, mimetype='image/png', download_name=f'{client_id}.png')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
