import sys
import os
# Ensure project root is on sys.path so `src` package imports work when running the script directly
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from flask import Flask, request, jsonify, send_file
import sqlite3
import os
import time
import logging
from datetime import datetime
from io import BytesIO

from src.plot_utils import build_timeseries_plot
try:
    from src.data_parser import parse_bytes
except Exception:
    # dynamic load fallback
    parse_bytes = None

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
            hr REAL,
            h01 REAL,
            h25 REAL,
            h50 REAL,
            h10 REAL
        )
    ''')
    conn.commit()
    conn.close()
    logging.info(f"Base de datos inicializada: {DB_PATH}")


init_db()


@app.route('/upload-json', methods=['POST'])
def upload_json():
    logging.info(f"[REQUEST] POST /upload-json desde {request.remote_addr}")
    data = request.get_json()
    if not data:
        logging.warning("Request sin JSON válido")
        return jsonify({'error': 'json required'}), 400

    client_id = data.get('client_id', 'unknown')
    samples = data.get('samples')
    if not samples or not isinstance(samples, list):
        logging.warning(f"Request de {client_id} sin samples válidos")
        return jsonify({'error': 'samples list required'}), 400

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for s in samples:
        ts = int(s.get('ts', time.time()))
        c.execute('''INSERT INTO measurements 
                     (client_id, ts, mp01, mp25, mp10, temp, hr, h01, h25, h50, h10) 
                     VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
                  (client_id, ts, s.get('mp01'), s.get('mp25'), s.get('mp10'), 
                   s.get('temp'), s.get('hr'),
                   s.get('h01', 0), s.get('h25', 0), s.get('h50', 0), s.get('h10', 0)))
    conn.commit()
    conn.close()
    logging.info(f"[SUCCESS] Insertadas {len(samples)} muestras de {client_id}")
    return jsonify({'status': 'ok', 'inserted': len(samples)})


@app.route('/upload-stream', methods=['POST'])
def upload_stream():
    logging.info(f"[REQUEST] POST /upload-stream desde {request.remote_addr}")
    data_bytes = request.get_data()
    if not data_bytes:
        logging.warning("Request sin bytes")
        return jsonify({'error': 'no bytes received'}), 400
    # Save raw stream for later parsing
    ts = int(time.time())
    stream_dir = os.path.join(DATA_DIR, 'streams')
    os.makedirs(stream_dir, exist_ok=True)
    fname = os.path.join(stream_dir, f'stream_{ts}.bin')
    with open(fname, 'wb') as f:
        f.write(data_bytes)
    logging.info(f"[STREAM] Guardado: {fname} ({len(data_bytes)} bytes)")
    # Decide whether to attempt parsing: header X-PARSE: 1 or query ?parse=1
    do_parse = False
    try:
        hdr = request.headers.get('X-PARSE')
        if hdr and hdr.strip() == '1':
            do_parse = True
    except Exception:
        pass
    if not do_parse:
        parse_q = request.args.get('parse')
        if parse_q and parse_q in ('1', 'true', 'True'):
            do_parse = True

    inserted = 0
    if do_parse:
        # attempt to import parse_bytes if not available
        parser = parse_bytes
        if parser is None:
            try:
                from src.data_parser import parse_bytes as _pb
                parser = _pb
            except Exception:
                parser = None
        if parser:
            try:
                records = parser(data_bytes)
                if records:
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    now = int(time.time())
                    # Insert each record; use station id as client_id
                    total = len(records)
                    for i, r in enumerate(records):
                        # timestamp spread over last total samples 1 minute apart
                        ts_rec = now - (total - 1 - i) * 60
                        client_id = f'client{r.get("id")}'
                        c.execute('''INSERT INTO measurements 
                                     (client_id, ts, mp01, mp25, mp10, temp, hr, h01, h25, h50, h10) 
                                     VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
                                  (client_id, ts_rec, r.get('mp01'), r.get('mp25'), r.get('mp10'), 
                                   r.get('te'), r.get('hr'),
                                   r.get('h01', 0), r.get('h25', 0), r.get('h50', 0), r.get('h10', 0)))
                        inserted += 1
                    conn.commit()
                    conn.close()
                    logging.info(f"[PARSE] Stream parseado: {inserted} registros insertados")
            except Exception as e:
                # parsing attempted but failed; report but keep saved file
                return jsonify({'status': 'saved', 'saved': fname, 'parse_error': str(e)}), 500

    resp = {'status': 'ok', 'saved': fname}
    if inserted:
        resp['inserted'] = inserted
    return jsonify(resp)


@app.route('/plot/<client_id>', methods=['GET'])
def plot_client(client_id):
    logging.info(f"[REQUEST] GET /plot/{client_id} desde {request.remote_addr}")
    # fetch last 10 samples for client_id
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''SELECT mp01, mp25, mp10, temp, hr, ts, h01, h25, h50, h10 
                 FROM measurements WHERE client_id = ? ORDER BY ts DESC LIMIT 10''', (client_id,))
    rows = c.fetchall()
    conn.close()
    if not rows:
        logging.warning(f"No hay datos para {client_id}")
        return jsonify({'error': 'no data'}), 404
    # rows are newest first; reverse to chronological
    rows = list(reversed(rows))
    samples = []
    for r in rows:
        samples.append({
            'mp01': r[0], 'mp25': r[1], 'mp10': r[2], 
            'temp': r[3], 'hr': r[4], 'ts': r[5],
            'h01': r[6], 'h25': r[7], 'h50': r[8], 'h10': r[9]
        })

    img_buf = build_timeseries_plot(samples, title=f'Mediciones - {client_id}')
    logging.info(f"[SUCCESS] Gráfico generado para {client_id}")
    return send_file(img_buf, mimetype='image/png', download_name=f'{client_id}.png')


def print_banner():
    """Imprime banner de inicio en consola"""
    print("\n" + "="*60)
    print("  Flask HTTP Server - INFO1157 Proyecto #2")
    print("  Sistemas Inteligentes - Sistemas Embebidos + Sensores")
    print("  By Alberto Caro")
    print("="*60)
    print(f"  Servidor escuchando en: http://0.0.0.0:5000")
    print(f"  Base de datos: {DB_PATH}")
    print(f"  Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    print("\n  Endpoints disponibles:")
    print("    POST /upload-json     - Recibir datos JSON")
    print("    POST /upload-stream   - Recibir datos binarios")
    print("    GET  /plot/<client_id> - Descargar gráfico PNG")
    print("\n" + "="*60 + "\n")


if __name__ == '__main__':
    # Configurar logging para consola
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Mostrar banner de inicio
    print_banner()
    
    # Iniciar servidor Flask
    logging.info("Iniciando servidor Flask...")
    app.run(host='0.0.0.0', port=5000, debug=False)
