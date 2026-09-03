"""Report which tileset atlas cells each level's TileMapLayers actually use."""

from __future__ import annotations

import base64
import glob
import os
import re
import struct
from collections import Counter

# Godot stores a uint16 format tag, then one 12-byte record per cell:
# cell x/y (int16), source id, atlas x/y and alternative tile (uint16).
HEADER = 2
RECORD = 12


def cells_of(blob: str) -> Counter:
    raw = base64.b64decode(blob)
    used: Counter = Counter()
    for offset in range(HEADER, len(raw) - RECORD + 1, RECORD):
        _x, _y, _source, sx, sy, _alt = struct.unpack_from("<hhHHHH", raw, offset)
        used[(sx, sy)] += 1
    return used


def main() -> None:
    total: Counter = Counter()
    for path in sorted(glob.glob("Scenes/Levels/level_0*.tscn")):
        text = open(path, encoding="utf-8").read()
        print("==", os.path.basename(path))
        for match in re.finditer(r'\[node name="(\w+)" type="TileMapLayer"(.*?)(?=\n\[node|\n\[connection|\Z)', text, re.S):
            name = match.group(1)
            blob = re.search(r'tile_map_data = PackedByteArray\("([^"]+)"\)', match.group(2))
            if blob is None:
                print(f"   {name:<12} (empty)")
                continue
            used = cells_of(blob.group(1))
            total.update(used)
            listing = ", ".join(f"({x},{y})x{n}" for (x, y), n in used.most_common())
            print(f"   {name:<12} {sum(used.values()):>4} cells: {listing}")
    print("\nall levels combined:")
    for (x, y), n in total.most_common():
        print(f"   atlas ({x},{y})  {n}")


if __name__ == "__main__":
    main()
