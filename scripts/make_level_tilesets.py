"""Create ground_tile_set_01..04.tres + .import stubs."""
from pathlib import Path

ROOT = Path(r"c:\Users\jakkr\OneDrive\เดสก์ท็อป\Gamedev\lab4\2D-Platformer-Starter-Kit-main")
src = (ROOT / "Scenes/Prefabs/ground_tile_set.tres").read_text(encoding="utf-8")

UIDS = {
    1: "uid://gtilelevel01amw",
    2: "uid://gtilelevel02amw",
    3: "uid://gtilelevel03amw",
    4: "uid://gtilelevel04amw",
}
TEX_UIDS = {
    1: "uid://texlevel01tiles",
    2: "uid://texlevel02tiles",
    3: "uid://texlevel03tiles",
    4: "uid://texlevel04tiles",
}

IMPORT = """[remap]

importer="texture"
type="CompressedTexture2D"
uid="{uid}"
path="res://.godot/imported/{name}-placeholder.ctex"
metadata={{
"vram_texture": false
}}

[deps]

source_file="res://Assets/Generated/Tiles/{name}"
dest_files=["res://.godot/imported/{name}-placeholder.ctex"]

[params]

compress/mode=0
compress/high_quality=false
compress/lossy_quality=0.7
compress/uastc_level=0
compress/rdo_quality_loss=0.0
compress/hdr_compression=1
compress/normal_map=0
compress/channel_pack=0
mipmaps/generate=false
mipmaps/limit=-1
roughness/mode=0
roughness/src_normal=""
process/channel_remap/red=0
process/channel_remap/green=1
process/channel_remap/blue=2
process/channel_remap/alpha=3
process/fix_alpha_border=true
process/premult_alpha=false
process/normal_map_invert_y=false
process/hdr_as_srgb=false
process/hdr_clamp_exposure=false
process/size_limit=0
detect_3d/compress_to=1
"""

for n in range(1, 5):
    name = f"tiles_level_0{n}.png"
    tex = f"res://Assets/Generated/Tiles/{name}"
    body = src.replace("uid://bvk6vx5i1riqd", UIDS[n])
    body = body.replace("uid://jaegp53ccc7w", TEX_UIDS[n])
    body = body.replace("res://Assets/Spritesheet/platformPack_tilesheet.png", tex)
    out = ROOT / f"Scenes/Prefabs/ground_tile_set_0{n}.tres"
    out.write_text(body, encoding="utf-8")
    imp = ROOT / "Assets/Generated/Tiles" / f"{name}.import"
    imp.write_text(IMPORT.format(uid=TEX_UIDS[n], name=name), encoding="utf-8")
    print("wrote", out.name)

print("done")
