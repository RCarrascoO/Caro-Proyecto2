import sys
import os
import unittest
import time
import sqlite3

# Ensure project root on sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import importlib
http_server_mod = importlib.import_module('src.http_server.app')
app = getattr(http_server_mod, 'app')
DB_PATH = getattr(http_server_mod, 'DB_PATH')

from src.data_parser import parse_bytes
from tools import generate_data_dat


class TestEndpoints(unittest.TestCase):
    def setUp(self):
        # prepare a small data blob (30 records)
        blob = b''
        for i in range(30):
            st = (i % 5) + 1
            blob += generate_data_dat.generate_record(st)
        self.blob = blob

        # ensure DB dir exists and start with fresh DB
        dbdir = os.path.dirname(DB_PATH)
        os.makedirs(dbdir, exist_ok=True)
        try:
            if os.path.exists(DB_PATH):
                os.remove(DB_PATH)
        except Exception:
            pass
        # re-initialize DB schema (init_db was called at import time earlier but we removed DB)
        try:
            http_server_mod.init_db()
        except Exception:
            pass

    def test_upload_and_parse(self):
        # build JSON payload (last 10)
        parsed = parse_bytes(self.blob)
        last10 = parsed[-10:]
        now = int(time.time())
        samples = []
        for i, r in enumerate(last10):
            samples.append({'ts': now - (len(last10) - 1 - i) * 60,
                            'mp01': r['mp01'], 'mp25': r['mp25'], 'mp10': r['mp10'],
                            'temp': r['te'], 'hr': r['hr']})
        client_id = f"client{last10[-1]['id']}"
        payload = {'client_id': client_id, 'samples': samples}

        with app.test_client() as c:
            r = c.post('/upload-json', json=payload)
            self.assertEqual(r.status_code, 200)
            j = r.get_json()
            self.assertEqual(j.get('inserted'), 10)

            r2 = c.post('/upload-stream?parse=1', data=self.blob, headers={'Content-Type':'application/octet-stream'})
            self.assertEqual(r2.status_code, 200)
            j2 = r2.get_json()
            self.assertIn('inserted', j2)

        # verify DB has rows
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM measurements')
        total = cur.fetchone()[0]
        conn.close()
        self.assertGreaterEqual(total, 30)


if __name__ == '__main__':
    unittest.main()
