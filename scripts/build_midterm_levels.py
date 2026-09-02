"""Generate level_05 and level_06 for midterm, and print helper paths."""
from __future__ import annotations

import base64
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "Scenes" / "Levels"
T = 64
G = 8


def enc_cells(cells: list[tuple[int, int, int, int]]) -> str:
    raw = struct.pack("<H", 0)
    for x, y, ax, ay in cells:
        raw += struct.pack("<hhHHHH", int(x), int(y), 0, int(ax), int(ay), 0)
    return base64.b64encode(raw).decode("ascii")


def rect(cells, x0, y0, w, h, ax=3, ay=1):
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            cells.append((x, y, ax, ay))


def platform(cells, x0, y, w, ax=3, ay=1):
    for x in range(x0, x0 + w):
        cells.append((x, y, ax, ay))


def wx(tx: float) -> float:
    return tx * T


def wy(ty: int) -> float:
    return ty * T


def build_level5():
    """Night canal â€” blocked path needs switch to open gate."""
    c = []
    rect(c, -2, G, 18, 4)          # start land through switch area
    platform(c, 8, G - 2, 3)        # high shelf for switch
    # far side after gate wall at ~x=15
    rect(c, 16, G, 16, 4)
    platform(c, 20, G - 2, 4)
    platform(c, 26, G - 1, 3)
    rect(c, 32, G, 12, 4)           # exit land
    return c


def build_level6():
    """Deliver rice to Ai Tong â€” short climax."""
    c = []
    rect(c, -2, G, 16, 4)
    platform(c, 10, G - 1, 4)
    rect(c, 16, G, 10, 4)
    platform(c, 22, G - 2, 3)
    rect(c, 28, G, 14, 4)
    return c


def write_l5(data: str) -> None:
    text = f"""[gd_scene format=4 uid="uid://level05amotherwalk"]

[ext_resource type="PackedScene" uid="uid://bjntpxb1c8jxn" path="res://Scenes/Levels/base_level.tscn" id="1_base"]
[ext_resource type="PackedScene" uid="uid://level06amotherwalk" path="res://Scenes/Levels/level_06.tscn" id="2_next"]
[ext_resource type="TileSet" uid="uid://dpk7f214d463s" path="res://Scenes/Prefabs/ground_tile_set_03.tres" id="3_tiles"]
[ext_resource type="PackedScene" path="res://Scenes/Prefabs/trap_thorns.tscn" id="10_a"]
[ext_resource type="PackedScene" path="res://Scenes/Prefabs/trap_pendulum.tscn" id="11_a"]
[ext_resource type="PackedScene" path="res://Scenes/Prefabs/kratib_item.tscn" id="12_a"]
[ext_resource type="PackedScene" path="res://Scenes/Prefabs/stone_ammo_item.tscn" id="13_a"]
[ext_resource type="PackedScene" path="res://Scenes/Prefabs/jump_leaf.tscn" id="14_a"]
[ext_resource type="PackedScene" path="res://Scenes/Prefabs/checkpoint_shrine.tscn" id="15_a"]
[ext_resource type="PackedScene" path="res://Scenes/Prefabs/villager_help.tscn" id="16_a"]
[ext_resource type="PackedScene" path="res://Scenes/Prefabs/puzzle_switch.tscn" id="17_a"]
[ext_resource type="PackedScene" path="res://Scenes/Prefabs/puzzle_gate.tscn" id="18_a"]
[ext_resource type="PackedScene" path="res://Scenes/Actors/enemy_snake.tscn" id="19_a"]
[ext_resource type="PackedScene" path="res://Scenes/Actors/enemy_crow.tscn" id="20_a"]
[ext_resource type="PackedScene" path="res://Scenes/Actors/enemy_boar.tscn" id="21_a"]

[node name="BaseLevel" instance=ExtResource("1_base")]

[node name="LevelFinishDoor" parent="." index="1"]
position = Vector2({wx(40)}, {wy(G - 1)})
next_scene = ExtResource("2_next")

[node name="Ground" type="TileMapLayer" parent="Level" index="1"]
tile_map_data = PackedByteArray("{data}")
tile_set = ExtResource("3_tiles")

[node name="PuzzleGate" parent="." instance=ExtResource("18_a")]
position = Vector2({wx(14.5)}, {wy(G)})

[node name="PuzzleSwitch" parent="." instance=ExtResource("17_a")]
position = Vector2({wx(9)}, {wy(G - 2)})
gate_paths = [NodePath("../PuzzleGate")]

[node name="CheckpointShrine" parent="." instance=ExtResource("15_a")]
position = Vector2({wx(20)}, {wy(G)})

[node name="VillagerHelp" parent="." instance=ExtResource("16_a")]
position = Vector2({wx(4)}, {wy(G)})
help_message = "à¸Šà¸²à¸§à¸šà¹‰à¸²à¸™à¸‚à¸­à¸šà¸„à¸¸à¸“ â€” à¸„à¸§à¸²à¸¡à¸­à¸”à¸—à¸™à¹„à¸­à¹‰à¸—à¸­à¸‡à¹€à¸žà¸´à¹ˆà¸¡à¸‚à¸¶à¹‰à¸™"

[node name="TrapThorns" parent="." instance=ExtResource("10_a")]
position = Vector2({wx(24)}, {wy(G)})

[node name="TrapPendulum" parent="." instance=ExtResource("11_a")]
position = Vector2({wx(28)}, {wy(G - 3)})

[node name="KratibItem" parent="Coins" index="0" instance=ExtResource("12_a")]
position = Vector2({wx(8)}, {wy(G - 2) - 20})

[node name="StoneAmmoItem" parent="Coins" index="1" instance=ExtResource("13_a")]
position = Vector2({wx(22)}, {wy(G - 2) - 20})

[node name="JumpLeaf" parent="Coins" index="2" instance=ExtResource("14_a")]
position = Vector2({wx(26)}, {wy(G - 1) - 20})

[node name="Snake1" parent="Enemies" index="0" instance=ExtResource("19_a")]
position = Vector2({wx(18)}, {wy(G)})

[node name="Boar1" parent="Enemies" index="1" instance=ExtResource("21_a")]
position = Vector2({wx(34)}, {wy(G)})

[node name="Crow1" parent="Enemies" index="2" instance=ExtResource("20_a")]
position = Vector2({wx(22)}, {wy(G - 4)})
patrol_width = 260.0

[node name="Label" parent="UserInterface" index="1"]
text = "à¸”à¹ˆà¸²à¸™ 5 â€” à¸„à¸¹à¸™à¹‰à¸³à¸à¸¥à¸²à¸‡à¸„à¸·à¸™"
"""
    (ROOT / "level_05.tscn").write_text(text, encoding="utf-8")
    print("wrote level_05.tscn")


def write_l6(data: str) -> None:
    text = f"""[gd_scene format=4 uid="uid://level06amotherwalk"]

[ext_resource type="PackedScene" uid="uid://bjntpxb1c8jxn" path="res://Scenes/Levels/base_level.tscn" id="1_base"]
[ext_resource type="PackedScene" uid="uid://b46lxwc5r3dy4" path="res://Scenes/Levels/game_win.tscn" id="2_next"]
[ext_resource type="TileSet" uid="uid://dpk7f214d563s" path="res://Scenes/Prefabs/ground_tile_set_04.tres" id="3_tiles"]
[ext_resource type="PackedScene" path="res://Scenes/Prefabs/portal_gate.tscn" id="10_a"]
[ext_resource type="PackedScene" path="res://Scenes/Prefabs/kratib_item.tscn" id="11_a"]
[ext_resource type="PackedScene" path="res://Scenes/Prefabs/heart_item.tscn" id="12_a"]
[ext_resource type="PackedScene" path="res://Scenes/Prefabs/stone_ammo_item.tscn" id="13_a"]
[ext_resource type="PackedScene" path="res://Scenes/Prefabs/trap_thorns.tscn" id="14_a"]
[ext_resource type="PackedScene" path="res://Scenes/Actors/enemy_buffalo.tscn" id="15_a"]
[ext_resource type="PackedScene" path="res://Scenes/Actors/enemy_crow.tscn" id="16_a"]
[ext_resource type="Texture2D" path="res://Assets/Generated/Spritesheet/aitong.png" id="17_a"]

[node name="BaseLevel" instance=ExtResource("1_base")]

[node name="LevelFinishDoor" parent="." index="1"]
position = Vector2({wx(36)}, {wy(G - 1)})
next_scene = ExtResource("2_next")

[node name="Ground" type="TileMapLayer" parent="Level" index="1"]
tile_map_data = PackedByteArray("{data}")
tile_set = ExtResource("3_tiles")

[node name="TrapThorns" parent="." instance=ExtResource("14_a")]
position = Vector2({wx(14)}, {wy(G)})

[node name="KratibItem" parent="Coins" index="0" instance=ExtResource("11_a")]
position = Vector2({wx(6)}, {wy(G) - 28})

[node name="HeartItem" parent="Coins" index="1" instance=ExtResource("12_a")]
position = Vector2({wx(22)}, {wy(G - 2) - 20})
give_extra_life = true

[node name="StoneAmmoItem" parent="Coins" index="2" instance=ExtResource("13_a")]
position = Vector2({wx(12)}, {wy(G - 1) - 20})

[node name="Buffalo1" parent="Enemies" index="0" instance=ExtResource("15_a")]
position = Vector2({wx(18)}, {wy(G)})
direction = -1

[node name="Crow1" parent="Enemies" index="1" instance=ExtResource("16_a")]
position = Vector2({wx(26)}, {wy(G - 4)})
patrol_width = 200.0

[node name="PortalGate" parent="." instance=ExtResource("10_a")]
position = Vector2({wx(38)}, {wy(G)})
next_scene = ExtResource("2_next")

[node name="AiTong" type="Sprite2D" parent="."]
position = Vector2({wx(39)}, {wy(G) - 48})
texture = ExtResource("17_a")

[node name="Label" parent="UserInterface" index="1"]
text = "à¸”à¹ˆà¸²à¸™ 6 â€” à¸ªà¹ˆà¸‡à¸à¸¥à¹ˆà¸­à¸‡à¸‚à¹‰à¸²à¸§à¹ƒà¸«à¹‰à¸­à¹‰à¸²à¸¢à¸—à¸­à¸‡"
"""
    (ROOT / "level_06.tscn").write_text(text, encoding="utf-8")
    print("wrote level_06.tscn")


def main() -> None:
    write_l5(enc_cells(build_level5()))
    write_l6(enc_cells(build_level6()))


if __name__ == "__main__":
    main()

