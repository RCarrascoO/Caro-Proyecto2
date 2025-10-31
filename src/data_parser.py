"""
Parser para `data.dat` con la estructura mostrada en el PDF:
TRegistro = record
  id : Byte
  te : Byte
  hr : Byte
  mp01 : Word
  mp25 : Word
  mp10 : Word
  h01 : Word
  h25 : Word
  h50 : Word
  h10 : Word
end;

Se asume little-endian por defecto (ajustable).

Funciones principales:
- parse_file(path, endian='<') -> list[dict]

Cada dict contiene: id, te, hr, mp01, mp25, mp10, h01, h25, h50, h10
"""
from __future__ import annotations
import struct
from typing import List, Dict

RECORD_FORMAT_LE = '<BBB7H'  # 3 unsigned bytes + 7 unsigned shorts (words) little-endian
RECORD_SIZE = struct.calcsize(RECORD_FORMAT_LE)


def parse_file(path: str, little_endian: bool = True) -> List[Dict]:
    """Parsea el archivo binario y devuelve una lista de registros.

    Args:
        path: ruta al archivo data.dat
        little_endian: True para little-endian (por defecto)

    Returns:
        lista de diccionarios con campos: id, te, hr, mp01, mp25, mp10, h01, h25, h50, h10
    """
    fmt = RECORD_FORMAT_LE if little_endian else '>BBB7H'
    size = struct.calcsize(fmt)
    records = []
    with open(path, 'rb') as f:
        data = f.read()
    if not data:
        return records
    if len(data) % size != 0:
        # allow trailing bytes but warn (we won't raise here)
        # Trim to nearest record
        trimmed_len = (len(data) // size) * size
        data = data[:trimmed_len]
    offset = 0
    while offset + size <= len(data):
        chunk = data[offset:offset+size]
        vals = struct.unpack(fmt, chunk)
        # unpack: (id, te, hr, mp01, mp25, mp10, h01, h25, h50, h10)
        rec = {
            'id': int(vals[0]),
            'te': int(vals[1]),
            'hr': int(vals[2]),
            'mp01': int(vals[3]),
            'mp25': int(vals[4]),
            'mp10': int(vals[5]),
            'h01': int(vals[6]),
            'h25': int(vals[7]),
            'h50': int(vals[8]),
            'h10': int(vals[9]),
        }
        records.append(rec)
        offset += size
    return records


def parse_bytes(blob: bytes, little_endian: bool = True) -> List[Dict]:
    """Parsea un blob de bytes que contiene registros consecutivos.

    Args:
        blob: contenido binario
        little_endian: True para little-endian

    Returns:
        lista de diccionarios como en parse_file
    """
    fmt = RECORD_FORMAT_LE if little_endian else '>BBB7H'
    size = struct.calcsize(fmt)
    records: List[Dict] = []
    if not blob:
        return records
    if len(blob) % size != 0:
        blob = blob[:(len(blob)//size)*size]
    offset = 0
    while offset + size <= len(blob):
        chunk = blob[offset:offset+size]
        vals = struct.unpack(fmt, chunk)
        rec = {
            'id': int(vals[0]),
            'te': int(vals[1]),
            'hr': int(vals[2]),
            'mp01': int(vals[3]),
            'mp25': int(vals[4]),
            'mp10': int(vals[5]),
            'h01': int(vals[6]),
            'h25': int(vals[7]),
            'h50': int(vals[8]),
            'h10': int(vals[9]),
        }
        records.append(rec)
        offset += size
    return records
