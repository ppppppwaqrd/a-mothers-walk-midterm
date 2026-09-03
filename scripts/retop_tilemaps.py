"""Give every level a proper ground surface row.

Levels 2-6 were painted with a single solid atlas cell, so their terrain had no
grass edge at all. This rewrites each Ground layer so any cell with nothing above
it uses a surface tile and everything buried uses a soil tile, picking among the
four variants of each by position so the terrain does not read as a grid.

Run with --apply to write the scenes; without it the script only reports.

Usage: python scripts/retop_tilemaps.py [--apply]
"""

from __future__ import annotations

import base64
import glob
import os
import re
import struct
import sys
from collections import Counter

HEADER = 2
RECORD = 12

VARIANTS = 4
FIRST_COL = 3
SURFACE_ROW = 0
SOIL_ROW = 1


def decode(blob: str) -> tuple[int, list[tuple[int, int, int, int, int, int]]]:
    raw = base64.b64decode(blob)
    fmt = struct.unpack_from("<H", raw, 0)[0]
    cells = []
    for offset in range(HEADER, len(raw) - RECORD + 1, RECORD):
        cells.append(struct.unpack_from("<hhHHHH", raw, offset))
    return fmt, cells


def encode(fmt: int, cells: list[tuple[int, int, int, int, int, int]]) -> str:
    raw = bytearray(struct.pack("<H", fmt))
    for cell in cells:
        raw += struct.pack("<hhHHHH", *cell)
    return base64.b64encode(bytes(raw)).decode("ascii")


def variant(x: int, y: int) -> int:
    """Pick a tile variant from the cell position, so runs stay stable on rerun."""
    h = (x * 73_856_093) ^ (y * 19_349_663)
    return (h >> 4) % VARIANTS


def retop(cells: list) -> tuple[list, Counter]:
    occupied = {(c[0], c[1]) for c in cells}
    changes: Counter = Counter()
    out = []
    for x, y, source, ax, ay, alt in cells:
        row = SURFACE_ROW if (x, y - 1) not in occupied else SOIL_ROW
        target = (FIRST_COL + variant(x, y), row)
        if (ax, ay) != target:
            changes["surface" if row == SURFACE_ROW else "soil"] += 1
        out.append((x, y, source, target[0], target[1], alt))
    return out, changes


def main() -> None:
    apply = "--apply" in sys.argv
    for path in sorted(glob.glob("Scenes/Levels/level_0*.tscn")):
        text = open(path, encoding="utf-8").read()
        name = os.path.basename(path)
        new_text = text
        touched = False
        for match in re.finditer(r'tile_map_data = PackedByteArray\("([^"]+)"\)', text):
            fmt, cells = decode(match.group(1))
            fixed, changes = retop(cells)
            if not changes:
                print(f"{name}: already correct ({len(cells)} cells)")
                continue
            summary = ", ".join(f"{k} x{v}" for k, v in changes.most_common())
            print(f"{name}: {len(cells)} cells | {summary}")
            new_text = new_text.replace(match.group(1), encode(fmt, fixed))
            touched = True
        if apply and touched:
            open(path, "w", encoding="utf-8").write(new_text)
    if not apply:
        print("\ndry run; pass --apply to write")


if __name__ == "__main__":
    main()
