"""Generate Godot 4 level scenes — playable gaps (≤2 tiles) + creative layouts."""
from __future__ import annotations

import base64
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "Scenes" / "Levels"
T = 64  # tile size px


def enc_cells(cells: list[tuple[int, int, int, int]]) -> str:
    """Godot 4.3+ TileMapLayer binary format (see tile_map_layer.cpp)."""
    # uint16 format_version (= TILE_MAP_LAYER_DATA_FORMAT_MAX - 1 = 0)
    raw = struct.pack("<H", 0)
    for x, y, ax, ay in cells:
        # int16 x,y | uint16 source_id, atlas_x, atlas_y, alternative
        raw += struct.pack("<hhHHHH", int(x), int(y), 0, int(ax), int(ay), 0)
    return base64.b64encode(raw).decode("ascii")


def rect(cells, x0, y0, w, h, ax=3, ay=1):
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            cells.append((x, y, ax, ay))


def platform(cells, x0, y, w, ax=3, ay=1):
    for x in range(x0, x0 + w):
        cells.append((x, y, ax, ay))


def stairs_up(cells, x0, y_ground, steps, width=2):
    """Each step rises 1 tile — always within single-jump height."""
    for i in range(steps):
        platform(cells, x0 + i * width, y_ground - 1 - i, width)


def wx(tile_x: float) -> float:
    return tile_x * T


def wy_top(tile_y: int) -> float:
    """World Y of the top surface of a tile row."""
    return tile_y * T


# Ground top row for all levels
G = 8


def build_level1():
    """หมู่บ้าน: ทางเดินยาว อ่างน้ำเล็ก เนินชมวิว 1 จุด."""
    c = []
    rect(c, -2, G, 16, 4)         # ลานยาว x=-2..13
    # คูน้ำ 1 ช่อง
    rect(c, 15, G, 14, 4)         # ต่อ x=15..28
    # เนินชมวิวเล็ก (เก็บของ)
    platform(c, 8, G - 1, 4)
    # จุดพักก่อนประตู
    platform(c, 22, G - 1, 3)
    rect(c, 30, G, 10, 4)         # ปลายด่าน x=30..39
    return c


def build_level2():
    """ป่าไผ่: พื้นยาว + แพข้ามบ่อ + คอนอีกาสูง."""
    c = []
    rect(c, -2, G, 12, 4)         # ต้นทาง
    # บ่อกว้าง 3 ช่อง (ใช้แพเลื่อน)
    rect(c, 14, G, 16, 4)         # ฝั่งโน้น x=14..29
    # คอนไม้ไผ่ให้อีกา / ของ
    platform(c, 18, G - 3, 4)
    platform(c, 24, G - 1, 3)
    rect(c, 31, G, 10, 4)         # ปลาย
    return c


def build_level3():
    """ทางขรุขระ: เกาะกลางทุ่ง 2 ก้อน + ลิฟต์."""
    c = []
    rect(c, -2, G, 10, 4)
    platform(c, 10, G, 3)         # หินก้าว
    platform(c, 14, G, 4)         # เกาะกลาง
    platform(c, 20, G, 3)
    rect(c, 24, G, 8, 4)          # ก่อนลิฟต์
    platform(c, 28, G - 2, 3)     # จุดสูง
    rect(c, 34, G, 12, 4)         # ปลาย
    return c


def build_level4():
    """ทุ่งนาไอ้ทอง: ทุ่งกว้าง ช่องคู กระดานดีด ขึ้นบ้าน."""
    c = []
    rect(c, -2, G, 14, 4)         # ทุ่งแรก
    rect(c, 14, G, 12, 4)         # ทุ่งสอง (คู 1 ที่ x=13)
    platform(c, 20, G - 1, 4)     # คันนา
    rect(c, 28, G, 10, 4)
    platform(c, 34, G - 2, 3)
    rect(c, 40, G, 12, 4)         # บ้านไอ้ทอง
    return c


LEVELS = {
    1: {
        "uid": "uid://dekkdb3a0eifd",
        "next": ("uid://cppg5yoxwv0dy", "res://Scenes/Levels/level_02.tscn"),
        "title": "ด่าน 1 — ออกจากหมู่บ้าน",
        "cells": build_level1,
        "door": (wx(36), wy_top(G - 1)),
        "extras": """
[ext_resource type="PackedScene" path="res://Scenes/Prefabs/trap_thorns.tscn" id="10_a"]
[ext_resource type="PackedScene" path="res://Scenes/Prefabs/kratib_item.tscn" id="11_a"]
[ext_resource type="PackedScene" path="res://Scenes/Prefabs/heart_item.tscn" id="12_a"]
[ext_resource type="PackedScene" path="res://Scenes/Actors/enemy_boar.tscn" id="14_a"]
[ext_resource type="PackedScene" path="res://Scenes/Actors/enemy_snake.tscn" id="15_a"]
""",
        "nodes": f"""
[node name="TrapThorns" parent="." instance=ExtResource("10_a")]
position = Vector2({wx(10)}, {wy_top(G)})

[node name="TrapThorns2" parent="." instance=ExtResource("10_a")]
position = Vector2({wx(20)}, {wy_top(G)})

[node name="KratibItem" parent="Coins" index="0" instance=ExtResource("11_a")]
position = Vector2({wx(4)}, {wy_top(G) - 28})

[node name="KratibItem2" parent="Coins" index="1" instance=ExtResource("11_a")]
position = Vector2({wx(9.5)}, {wy_top(G - 1) - 28})

[node name="HeartItem" parent="Coins" index="2" instance=ExtResource("12_a")]
position = Vector2({wx(23)}, {wy_top(G - 1) - 28})

[node name="Boar1" parent="Enemies" index="0" instance=ExtResource("14_a")]
position = Vector2({wx(12)}, {wy_top(G)})
direction = 1

[node name="Snake1" parent="Enemies" index="1" instance=ExtResource("15_a")]
position = Vector2({wx(26)}, {wy_top(G)})
direction = -1
""",
    },
    2: {
        "uid": "uid://cppg5yoxwv0dy",
        "next": ("uid://towe6jtciome", "res://Scenes/Levels/level_03.tscn"),
        "title": "ด่าน 2 — ป่าไผ่",
        "cells": build_level2,
        "door": (wx(38), wy_top(G - 1)),
        "extras": """
[ext_resource type="PackedScene" path="res://Scenes/Prefabs/trap_spear.tscn" id="10_a"]
[ext_resource type="PackedScene" path="res://Scenes/Prefabs/trap_thorns.tscn" id="11_a"]
[ext_resource type="PackedScene" path="res://Scenes/Prefabs/moving_platform.tscn" id="12_a"]
[ext_resource type="PackedScene" path="res://Scenes/Prefabs/kratib_item.tscn" id="13_a"]
[ext_resource type="PackedScene" path="res://Scenes/Prefabs/speed_gourd.tscn" id="14_a"]
[ext_resource type="PackedScene" path="res://Scenes/Actors/enemy_snake.tscn" id="15_a"]
[ext_resource type="PackedScene" path="res://Scenes/Actors/enemy_crow.tscn" id="16_a"]
""",
        "nodes": f"""
[node name="MovingPlatform" parent="." instance=ExtResource("12_a")]
position = Vector2({wx(11)}, {wy_top(G) - 8})
move_offset = Vector2(160, 0)
move_duration = 2.4

[node name="TrapSpear" parent="." instance=ExtResource("10_a")]
position = Vector2({wx(22)}, {wy_top(G)})

[node name="TrapThorns" parent="." instance=ExtResource("11_a")]
position = Vector2({wx(28)}, {wy_top(G)})

[node name="KratibItem" parent="Coins" index="0" instance=ExtResource("13_a")]
position = Vector2({wx(6)}, {wy_top(G) - 28})

[node name="SpeedGourd" parent="Coins" index="1" instance=ExtResource("14_a")]
position = Vector2({wx(19.5)}, {wy_top(G - 3) - 28})

[node name="Snake1" parent="Enemies" index="0" instance=ExtResource("15_a")]
position = Vector2({wx(17)}, {wy_top(G)})
direction = 1

[node name="Crow1" parent="Enemies" index="1" instance=ExtResource("16_a")]
position = Vector2({wx(20)}, {wy_top(G - 5)})
direction = 1
patrol_width = 280.0
""",
    },
    3: {
        "uid": "uid://towe6jtciome",
        "next": ("uid://level04amotherwalk", "res://Scenes/Levels/level_04.tscn"),
        "title": "ด่าน 3 — ทางขรุขระ",
        "cells": build_level3,
        "door": (wx(42), wy_top(G - 1)),
        "extras": """
[ext_resource type="PackedScene" path="res://Scenes/Prefabs/trap_blade.tscn" id="10_a"]
[ext_resource type="PackedScene" path="res://Scenes/Prefabs/elevator.tscn" id="12_a"]
[ext_resource type="PackedScene" path="res://Scenes/Prefabs/kratib_item.tscn" id="14_a"]
[ext_resource type="PackedScene" path="res://Scenes/Prefabs/heart_item.tscn" id="15_a"]
[ext_resource type="PackedScene" path="res://Scenes/Actors/enemy_buffalo.tscn" id="16_a"]
[ext_resource type="PackedScene" path="res://Scenes/Actors/enemy_crow.tscn" id="17_a"]
""",
        "nodes": f"""
[node name="TrapBlade" parent="." instance=ExtResource("10_a")]
position = Vector2({wx(16)}, {wy_top(G) - 36})

[node name="Elevator" parent="." instance=ExtResource("12_a")]
position = Vector2({wx(30)}, {wy_top(G)})
move_offset = Vector2(0, -140)
move_duration = 2.5

[node name="KratibItem" parent="Coins" index="0" instance=ExtResource("14_a")]
position = Vector2({wx(15.5)}, {wy_top(G) - 28})

[node name="HeartItem" parent="Coins" index="1" instance=ExtResource("15_a")]
position = Vector2({wx(29)}, {wy_top(G - 2) - 28})

[node name="Buffalo1" parent="Enemies" index="0" instance=ExtResource("16_a")]
position = Vector2({wx(26)}, {wy_top(G)})
direction = -1

[node name="Crow1" parent="Enemies" index="1" instance=ExtResource("17_a")]
position = Vector2({wx(18)}, {wy_top(G - 4)})
direction = 1
patrol_width = 240.0
""",
    },
    4: {
        "uid": "uid://level04amotherwalk",
        "next": ("uid://b46lxwc5r3dy4", "res://Scenes/Levels/game_win.tscn"),
        "title": "ด่าน 4 — ทุ่งนาของไอ้ทอง",
        "cells": build_level4,
        "door": (wx(48), wy_top(G - 1)),
        "extras": """
[ext_resource type="PackedScene" path="res://Scenes/Prefabs/portal_gate.tscn" id="11_a"]
[ext_resource type="PackedScene" path="res://Scenes/Prefabs/kratib_item.tscn" id="12_a"]
[ext_resource type="PackedScene" path="res://Scenes/Prefabs/heart_item.tscn" id="13_a"]
[ext_resource type="PackedScene" path="res://Scenes/Prefabs/trap_thorns.tscn" id="14_a"]
[ext_resource type="PackedScene" path="res://Scenes/Prefabs/jump_board.tscn" id="15_a"]
[ext_resource type="PackedScene" path="res://Scenes/Actors/enemy_boar.tscn" id="16_a"]
[ext_resource type="PackedScene" path="res://Scenes/Actors/enemy_buffalo.tscn" id="17_a"]
[ext_resource type="PackedScene" path="res://Scenes/Actors/enemy_crow.tscn" id="18_a"]
[ext_resource type="Texture2D" path="res://Assets/Generated/Spritesheet/aitong.png" id="19_a"]
""",
        "nodes": f"""
[node name="TrapThorns" parent="." instance=ExtResource("14_a")]
position = Vector2({wx(10)}, {wy_top(G)})

[node name="JumpBoard" parent="." instance=ExtResource("15_a")]
position = Vector2({wx(21)}, {wy_top(G)})

[node name="PortalGate" parent="." instance=ExtResource("11_a")]
position = Vector2({wx(49)}, {wy_top(G) - 32})
next_scene = ExtResource("2_next")

[node name="AiTong" type="Sprite2D" parent="."]
position = Vector2({wx(50.5)}, {wy_top(G) - 48})
texture = ExtResource("19_a")

[node name="KratibItem" parent="Coins" index="0" instance=ExtResource("12_a")]
position = Vector2({wx(6)}, {wy_top(G) - 28})

[node name="KratibItem2" parent="Coins" index="1" instance=ExtResource("12_a")]
position = Vector2({wx(21.5)}, {wy_top(G - 1) - 28})

[node name="HeartItem" parent="Coins" index="2" instance=ExtResource("13_a")]
position = Vector2({wx(35)}, {wy_top(G - 2) - 28})

[node name="Boar1" parent="Enemies" index="0" instance=ExtResource("16_a")]
position = Vector2({wx(8)}, {wy_top(G)})
direction = 1

[node name="Buffalo1" parent="Enemies" index="1" instance=ExtResource("17_a")]
position = Vector2({wx(30)}, {wy_top(G)})
direction = -1

[node name="Crow1" parent="Enemies" index="2" instance=ExtResource("18_a")]
position = Vector2({wx(36)}, {wy_top(G - 5)})
direction = 1
patrol_width = 260.0
""",
    },
}


def write_level(n: int) -> None:
    m = LEVELS[n]
    data = enc_cells(m["cells"]())
    dx, dy = m["door"]
    next_uid, next_path = m["next"]
    text = f"""[gd_scene format=4 uid="{m['uid']}"]

[ext_resource type="PackedScene" uid="uid://bjntpxb1c8jxn" path="res://Scenes/Levels/base_level.tscn" id="1_base"]
[ext_resource type="PackedScene" uid="{next_uid}" path="{next_path}" id="2_next"]
[ext_resource type="TileSet" uid="uid://gtilelevel0{n}amw" path="res://Scenes/Prefabs/ground_tile_set_0{n}.tres" id="3_tiles"]
{m['extras']}
[node name="BaseLevel" instance=ExtResource("1_base")]

[node name="LevelFinishDoor" parent="." index="1"]
position = Vector2({dx}, {dy})
next_scene = ExtResource("2_next")

[node name="Ground" type="TileMapLayer" parent="Level" index="1"]
tile_map_data = PackedByteArray("{data}")
tile_set = ExtResource("3_tiles")

{m['nodes']}
[node name="Label" parent="UserInterface" index="1"]
text = "{m['title']}"
"""
    path = ROOT / f"level_0{n}.tscn"
    path.write_text(text, encoding="utf-8")
    print("wrote", path.name, "tiles=", len(m["cells"]()))


def main():
    import sys

    targets = [int(a) for a in sys.argv[1:]] if len(sys.argv) > 1 else list(range(1, 5))
    for n in targets:
        write_level(n)


if __name__ == "__main__":
    main()
