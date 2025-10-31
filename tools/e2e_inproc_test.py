"""
Prueba E2E en proceso (sin arrancar servidor HTTP separado).
- Lee `data.dat` generado
- Usa `src.data_parser.parse_bytes` para obtener registros
- Usa `src.http_server.app` con `app.test_client()` para POST /upload-json y /upload-stream (con parse)
- Consulta la DB `data/data.db` y muestra filas insertadas
- Descarga /plot/<client_id> y guarda PNG
"""
import sys, os
# Ensure project root on sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.data_parser import parse_bytes
import importlib
http_server_mod = importlib.import_module('src.http_server.app')
app = getattr(http_server_mod, 'app')
import os
import sqlite3

DATA_FILE = 'data.dat'
DB_PATH = os.path.join('data', 'data.db')

if not os.path.exists(DATA_FILE):
    raise SystemExit('data.dat not found. Run tools/generate_data_dat.py first')

with open(DATA_FILE, 'rb') as f:
    blob = f.read()

records = parse_bytes(blob)
print('Parsed records:', len(records))
if not records:
    raise SystemExit('no records parsed')

# Build JSON payload similarly to send_data.py
samples = []
import time
now = int(time.time())
last10 = records[-10:]
for i, r in enumerate(last10):
    samples.append({'ts': now - (len(last10) - 1 - i) * 60,
                    'mp01': r['mp01'], 'mp25': r['mp25'], 'mp10': r['mp10'],
                    'temp': r['te'], 'hr': r['hr']})
client_id = f"client{last10[-1]['id']}"
payload = {'client_id': client_id, 'samples': samples}

with app.test_client() as c:
    print('POST /upload-json')
    r = c.post('/upload-json', json=payload)
    print('status', r.status_code, 'json', r.get_json())

    print('POST /upload-stream (with parse=1)')
    r2 = c.post('/upload-stream?parse=1', data=blob, headers={'Content-Type':'application/octet-stream'})
    print('status', r2.status_code, 'json', r2.get_json())

# Query DB
if not os.path.exists(DB_PATH):
    print('DB not found at', DB_PATH)
else:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT client_id, COUNT(*) FROM measurements GROUP BY client_id')
    rows = c.fetchall()
    print('DB rows:', rows)
    conn.close()

# Try to fetch plot
import urllib.parse
from src.plot_utils import build_timeseries_plot
# Use test_client get to obtain PNG
with app.test_client() as c:
    res = c.get(f'/plot/{client_id}')
    if res.status_code == 200:
        outname = f'plot_{client_id}.png'
        with open(outname, 'wb') as f:
            f.write(res.data)
        print('Saved plot to', outname)
    else:
        print('Plot request failed:', res.status_code, res.get_json())
