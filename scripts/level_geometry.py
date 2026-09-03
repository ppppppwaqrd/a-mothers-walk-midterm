"""Report the world-space extent of each level's ground and its parallax layers.

The parallax layers are anchored in world space, so their vertical placement has
to be derived from where the ground actually sits rather than guessed.

Usage: python scripts/level_geometry.py
"""

from __future__ import annotations

import base64
import re
import struct
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
LEVELS = ROOT / "Scenes" / "Levels"
BG = ROOT / "Assets" / "Generated" / "BG"
TILE = 64
HEADER, RECORD = 2, 12

DATA = re.compile(r'tile_map_data = PackedByteArray\("([^"]+)"\)')


def main() -> None:
    for level in range(1, 7):
        nn = f"{level:02d}"
        text = (LEVELS / f"level_{nn}.tscn").read_text(encoding="utf-8")
        xs: list[int] = []
        ys: list[int] = []
        for match in DATA.finditer(text):
            raw = base64.b64decode(match.group(1))
            for off in range(HEADER, len(raw) - RECORD + 1, RECORD):
                x, y = struct.unpack_from("<hh", raw, off)
                xs.append(x)
                ys.append(y)
        print(
            f"level_{nn}: ground world x {min(xs) * TILE}..{(max(xs) + 1) * TILE}"
            f"  y {min(ys) * TILE}..{(max(ys) + 1) * TILE}"
        )

    print()
    for prefix in ("sky", "far", "mid", "near"):
        w, h = Image.open(BG / f"{prefix}_01.png").size
        print(f"{prefix}: {w}x{h}")


if __name__ == "__main__":
    main()
