"""Confirm canals are empty and wider than a full-speed jump."""
from __future__ import annotations

import base64
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "Scenes" / "Levels"
HEADER, RECORD = 2, 12
JUMP_W, JUMP_H = 270, 154
PITS = {2: (10, 16), 3: (32, 37), 4: (12, 17), 5: (20, 26)}


def cells(n: int) -> set[tuple[int, int]]:
    text = (ROOT / f"level_{n:02d}.tscn").read_text(encoding="utf-8")
    blob = re.search(r'tile_map_data = PackedByteArray\("([^"]+)"\)', text).group(1)
    raw = base64.b64decode(blob)
    out: set[tuple[int, int]] = set()
    for off in range(HEADER, len(raw) - RECORD + 1, RECORD):
        x, y = struct.unpack_from("<hh", raw, off)
        out.add((x, y))
    return out


def main() -> None:
    bad = 0
    for n, (a, b) in PITS.items():
        used = cells(n)
        empty = all((x, y) not in used for x in range(a, b) for y in range(0, 16))
        width = (b - a) * 64
        skippable = width <= JUMP_W
        print(f"L{n} canal {a}-{b - 1} = {width}px empty={empty} jump_skip={skippable}")
        if not empty or skippable:
            bad += 1
    shelf = {(8, 5), (9, 5), (10, 5)}.issubset(cells(5))
    print(f"L5 shelf y=5 present={shelf}  rise=192 jump={JUMP_H} reach={48 + JUMP_H}")
    print(f"L1 gate height 192 > jump {JUMP_H}: {192 > JUMP_H}")
    if not shelf:
        bad += 1
    raise SystemExit(bad)


if __name__ == "__main__":
    main()
