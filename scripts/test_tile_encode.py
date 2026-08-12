"""Decode/verify and fix tile_map_data encoding for Godot 4.x TileMapLayer."""
from __future__ import annotations

import base64
import re
import struct
from pathlib import Path

# Correct layout (Godot 4.3+ / 4.7):
#   uint16 version
#   repeated:
#     int16 cell_x, int16 cell_y
#     uint16 source_id, uint16 atlas_x, uint16 atlas_y, uint16 alternative


def encode_cells(cells: list[tuple[int, int, int, int]], version: int = 0) -> str:
    raw = struct.pack("<H", version)
    for x, y, ax, ay in cells:
        raw += struct.pack("<hhHHHH", int(x), int(y), 0, int(ax), int(ay), 0)
    return base64.b64encode(raw).decode("ascii")


def decode_preview(b64: str, n: int = 3) -> None:
    raw = base64.b64decode(b64)
    ver = struct.unpack_from("<H", raw, 0)[0]
    print("bytes", len(raw), "version", ver, "cells", (len(raw) - 2) // 12)
    for i in range(n):
        off = 2 + i * 12
        x, y, src, ax, ay, alt = struct.unpack_from("<hhHHHH", raw, off)
        print(i, "pos", (x, y), "src", src, "atlas", (ax, ay), "alt", alt)


if __name__ == "__main__":
    # sanity: encode one cell and decode
    b64 = encode_cells([(-2, 8, 3, 1), (0, 8, 3, 1)])
    decode_preview(b64, 2)
