"""Carve mandatory canals into levels 2–5 and raise the L5 switch shelf.

Does not regenerate whole scenes — only rewrites Ground tile_map_data.
"""
from __future__ import annotations

import base64
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEVELS = ROOT / "Scenes" / "Levels"
HEADER = 2
RECORD = 12
DATA = re.compile(r'tile_map_data = PackedByteArray\("([^"]+)"\)')

# (level, x0 inclusive, x1 exclusive) columns to delete entirely.
PITS: dict[int, tuple[int, int]] = {
    2: (10, 16),  # 384px pond
    3: (32, 37),  # 320px canal before the far bank
    4: (12, 17),  # 320px rice canal
    5: (20, 26),  # 384px night canal
}

# Extra tiles to stamp: (x, y, atlas_x, atlas_y)
ADD: dict[int, list[tuple[int, int, int, int]]] = {
    5: [
        (8, 5, 4, 0),
        (9, 5, 6, 0),
        (10, 5, 4, 0),
    ],
}

# Extra tiles to drop after pit carve (old jumpable L5 ledge).
DROP: dict[int, set[tuple[int, int]]] = {
    5: {(8, 6), (9, 6), (10, 6)},
}


def decode(blob: str) -> list[tuple[int, int, int, int, int, int]]:
    raw = base64.b64decode(blob)
    cells: list[tuple[int, int, int, int, int, int]] = []
    for off in range(HEADER, len(raw) - RECORD + 1, RECORD):
        x, y, src, ax, ay, alt = struct.unpack_from("<hhHHHH", raw, off)
        cells.append((x, y, src, ax, ay, alt))
    return cells


def encode(cells: list[tuple[int, int, int, int, int, int]]) -> str:
    raw = struct.pack("<H", 0)
    for x, y, src, ax, ay, alt in cells:
        raw += struct.pack("<hhHHHH", x, y, src, ax, ay, alt)
    return base64.b64encode(raw).decode("ascii")


def patch_level(n: int) -> None:
    path = LEVELS / f"level_{n:02d}.tscn"
    text = path.read_text(encoding="utf-8")
    match = DATA.search(text)
    if match is None:
        raise SystemExit(f"no tile_map_data in {path.name}")
    cells = decode(match.group(1))
    x0, x1 = PITS.get(n, (0, 0))
    drop = DROP.get(n, set())
    kept: list[tuple[int, int, int, int, int, int]] = []
    for cell in cells:
        x, y = cell[0], cell[1]
        if x0 <= x < x1:
            continue
        if (x, y) in drop:
            continue
        kept.append(cell)
    have = {(c[0], c[1]) for c in kept}
    for x, y, ax, ay in ADD.get(n, []):
        if (x, y) not in have:
            kept.append((x, y, 0, ax, ay, 0))
    blob = encode(kept)
    new = DATA.sub(f'tile_map_data = PackedByteArray("{blob}")', text, count=1)
    path.write_text(new, encoding="utf-8")
    xs = sorted({c[0] for c in kept})
    missing = [x for x in range(min(xs), max(xs) + 1) if x not in set(xs)]
    print(f"level_{n:02d}: {len(cells)} -> {len(kept)} cells  gaps x={missing}")


def main() -> None:
    for n in sorted(set(PITS) | set(ADD)):
        patch_level(n)
    print("done")


if __name__ == "__main__":
    main()
