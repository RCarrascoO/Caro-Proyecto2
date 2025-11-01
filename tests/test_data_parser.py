import sys
import os
import unittest

# Ensure project root on sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.data_parser import parse_bytes
from tools import generate_data_dat


class TestDataParser(unittest.TestCase):
    def test_round_trip_parse(self):
        # build 25 records across 3 stations
        records = []
        blob = b''
        for i in range(25):
            st = (i % 3) + 1
            r = generate_data_dat.generate_record(st)
            blob += r

        parsed = parse_bytes(blob)
        self.assertEqual(len(parsed), 25)
        # spot check types and ranges
        for p in parsed:
            self.assertIn('id', p)
            self.assertIn('te', p)
            self.assertIn('mp01', p)
            self.assertIsInstance(p['id'], int)
            self.assertIsInstance(p['mp01'], int)
            self.assertGreaterEqual(p['te'], 0)
            self.assertLessEqual(p['te'], 255)


if __name__ == '__main__':
    unittest.main()
