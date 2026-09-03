"""Write one TileSet per level and point each level scene at its own.

Each tileset declares only the cells the levels actually place: four surface
variants and four soil variants, all with full-cell collision. The level scenes
also carried tileset UIDs that did not match the files they pointed at (Godot was
silently falling back to the path), so the references are rewritten here to keep
UID and path in agreement.

Usage: python scripts/make_level_tilesets.py
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PREFABS = ROOT / "Scenes" / "Prefabs"
LEVELS = ROOT / "Scenes" / "Levels"

TILESET_UID = {
    1: "uid://dpk7f214d263s",
    2: "uid://dpk7f214d363s",
    3: "uid://dpk7f214d463s",
    4: "uid://dpk7f214d563s",
    5: "uid://dpk7f214d663s",
    6: "uid://dpk7f214d763s",
}

FULL_CELL = "PackedVector2Array(-32, -32, 32, -32, 32, 32, -32, 32)"

# Surface variants on row 0, soil variants on row 1; see build_storybook_tiles.py.
VARIANTS = 4
FIRST_COL = 3

TEMPLATE = """[gd_resource type="TileSet" format=3 uid="{uid}"]

[ext_resource type="Texture2D" path="res://Assets/Generated/Tiles/tiles_level_{nn}.png" id="1_sheet"]

[sub_resource type="TileSetAtlasSource" id="TileSetAtlasSource_ground"]
texture = ExtResource("1_sheet")
texture_region_size = Vector2i(64, 64)
{cells}

[resource]
tile_size = Vector2i(64, 64)
physics_layer_0/collision_layer = 1
sources/0 = SubResource("TileSetAtlasSource_ground")
"""


def cell_block() -> str:
    lines = []
    for row in (0, 1):
        for v in range(VARIANTS):
            coord = f"{FIRST_COL + v}:{row}"
            lines.append(f"{coord}/0 = 0")
            lines.append(f"{coord}/0/physics_layer_0/polygon_0/points = {FULL_CELL}")
    return "\n".join(lines)


def main() -> None:
    cells = cell_block()
    for level, uid in TILESET_UID.items():
        nn = f"{level:02d}"
        path = PREFABS / f"ground_tile_set_{nn}.tres"
        path.write_text(TEMPLATE.format(uid=uid, nn=nn, cells=cells), encoding="utf-8")
        print(f"wrote {path.name}")

    pattern = re.compile(r'\[ext_resource type="TileSet" uid="[^"]*" path="res://Scenes/Prefabs/ground_tile_set_\d\d\.tres"')
    for level, uid in TILESET_UID.items():
        nn = f"{level:02d}"
        scene = LEVELS / f"level_{nn}.tscn"
        text = scene.read_text(encoding="utf-8")
        replacement = f'[ext_resource type="TileSet" uid="{uid}" path="res://Scenes/Prefabs/ground_tile_set_{nn}.tres"'
        new_text, count = pattern.subn(replacement, text)
        if count == 0:
            print(f"  !! no tileset reference found in level_{nn}.tscn")
            continue
        scene.write_text(new_text, encoding="utf-8")
        print(f"  level_{nn}.tscn -> ground_tile_set_{nn}.tres")


if __name__ == "__main__":
    main()
