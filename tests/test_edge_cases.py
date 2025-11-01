import sys
import os
import unittest
import sqlite3

# Ensure project root on sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import importlib
http_server_mod = importlib.import_module('src.http_server.app')
app = getattr(http_server_mod, 'app')
DB_PATH = getattr(http_server_mod, 'DB_PATH')

from tools import generate_data_dat
from src.data_parser import parse_bytes


class TestEdgeCases(unittest.TestCase):
    def setUp(self):
        # ensure DB fresh
        dbdir = os.path.dirname(DB_PATH)
        os.makedirs(dbdir, exist_ok=True)
        try:
            if os.path.exists(DB_PATH):
                os.remove(DB_PATH)
        except Exception:
            pass
        try:
            http_server_mod.init_db()
        except Exception:
            pass

    def test_partial_stream_trimmed(self):
        # create 5 full records then add 3 extra bytes (partial)
        blob = b''
        for i in range(5):
            blob += generate_data_dat.generate_record(i+1)
        blob += b'ABC'  # partial tail

        # parse_bytes should ignore the partial tail and return 5 records
        parsed = parse_bytes(blob)
        self.assertEqual(len(parsed), 5)

    def test_corrupt_stream_results_zero_or_fails_gracefully(self):
        # Random bytes not matching record size
        corrupt = b'\x00\xFF\xAA' * 7
        parsed = parse_bytes(corrupt)
        # May parse 1 or 0 depending on alignment; ensure it doesn't crash
        self.assertIsInstance(parsed, list)

    def test_invalid_json_upload(self):
        with app.test_client() as c:
            r = c.post('/upload-json', data='not-a-json', content_type='application/json')
            # server should respond 400 for invalid json
            self.assertIn(r.status_code, (400,))


if __name__ == '__main__':
    unittest.main()
