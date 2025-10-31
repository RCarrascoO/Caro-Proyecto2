"""
Generador sintético de `data.dat` para pruebas.

Uso:
    python tools/generate_data_dat.py --out test_data.dat --count 100 --stations 10

Genera `count` registros por estación (si stations>1, genera estaciones 1..stations repetidas).
Formato: same as src/data_parser.RECORD_FORMAT_LE
"""
from __future__ import annotations
import struct
import random
import argparse

RECORD_FMT = '<BBB7H'


def generate_record(station_id: int) -> bytes:
    # te: temperatura (0-50), hr: humedad (0-100)
    te = random.randint(0, 50)
    hr = random.randint(20, 90)
    # particulas y histograma valores razonables
    mp01 = random.randint(0, 300)
    mp25 = random.randint(0, 300)
    mp10 = random.randint(0, 300)
    h01 = random.randint(0, 300)
    h25 = random.randint(0, 300)
    h50 = random.randint(0, 300)
    h10 = random.randint(0, 300)
    return struct.pack(RECORD_FMT, station_id & 0xFF, te & 0xFF, hr & 0xFF,
                       mp01 & 0xFFFF, mp25 & 0xFFFF, mp10 & 0xFFFF,
                       h01 & 0xFFFF, h25 & 0xFFFF, h50 & 0xFFFF, h10 & 0xFFFF)


def main():
    p = argparse.ArgumentParser(description='Generador sintético de data.dat')
    p.add_argument('--out', '-o', default='data.dat', help='archivo de salida')
    p.add_argument('--count', '-n', type=int, default=10, help='cantidad de registros por estación')
    p.add_argument('--stations', '-s', type=int, default=10, help='número de estaciones diferentes')
    p.add_argument('--seed', type=int, default=None, help='seed para reproducibilidad')
    args = p.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    records = []
    for i in range(args.count):
        for st in range(1, args.stations + 1):
            records.append(generate_record(st))

    with open(args.out, 'wb') as f:
        for r in records:
            f.write(r)

    print(f'Generados {len(records)} registros en {args.out}')


if __name__ == '__main__':
    main()
