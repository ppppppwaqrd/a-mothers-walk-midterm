"""Build 4 themed ground tilesheets (same atlas layout as platformPack)."""
from __future__ import annotations

import colorsys
import os
from PIL import Image

ROOT = r"c:\Users\jakkr\OneDrive\เดสก์ท็อป\Gamedev\lab4\2D-Platformer-Starter-Kit-main"
SRC = os.path.join(ROOT, "Assets", "Spritesheet", "platformPack_tilesheet.png")
OUT = os.path.join(ROOT, "Assets", "Generated", "Tiles")

# Target mid-tone RGB for the grey-blue riveted blocks used as ground (atlas 3,1).
THEMES = {
    1: {  # village clay / rice earth
        "name": "tiles_level_01.png",
        "mid": (168, 118, 72),
        "sat_boost": 0.15,
    },
    2: {  # bamboo forest green
        "name": "tiles_level_02.png",
        "mid": (72, 128, 78),
        "sat_boost": 0.2,
    },
    3: {  # mountain cool stone
        "name": "tiles_level_03.png",
        "mid": (98, 112, 138),
        "sat_boost": 0.05,
    },
    4: {  # Ai Tong golden straw
        "name": "tiles_level_04.png",
        "mid": (198, 152, 58),
        "sat_boost": 0.22,
    },
}


def is_platform_grey(r: int, g: int, b: int, a: int) -> bool:
    """Detect Kenney blue-grey riveted platform / rock tiles (not grass, sand, liquids)."""
    if a < 8:
        return False
    # Skip bright saturated colors (keys, gems, liquids, grass tops)
    mx, mn = max(r, g, b), min(r, g, b)
    if mx - mn > 55 and not (abs(r - g) < 25 and abs(g - b) < 35 and abs(r - b) < 40):
        # allow only near-neutral greys/blues
        if b > r + 25 and b > g + 10:
            pass  # blue-ish platform accents ok
        else:
            return False
    # Grey-blue family used by platform blocks (approx 80-180 midtones)
    if 55 <= r <= 200 and 70 <= g <= 210 and 80 <= b <= 220:
        # Prefer cooler / desaturated
        if abs(r - g) <= 40 and abs(g - b) <= 45:
            return True
        if b >= r and b >= g - 5 and (b - r) <= 60:
            return True
    return False


def recolor_pixel(r: int, g: int, b: int, a: int, mid: tuple[int, int, int], sat_boost: float):
    # Relative luminance vs theme mid
    src_lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
    mid_lum = (0.299 * mid[0] + 0.587 * mid[1] + 0.114 * mid[2]) / 255.0
    # Scale theme color by luminance ratio
    scale = src_lum / max(0.08, mid_lum)
    nr = min(255, int(mid[0] * scale))
    ng = min(255, int(mid[1] * scale))
    nb = min(255, int(mid[2] * scale))
    # Mild saturation boost in HLS
    h, l, s = colorsys.rgb_to_hls(nr / 255.0, ng / 255.0, nb / 255.0)
    s = min(1.0, s + sat_boost * (1.0 - abs(l - 0.5) * 1.2))
    nr, ng, nb = colorsys.hls_to_rgb(h, l, s)
    return int(nr * 255), int(ng * 255), int(nb * 255), a


def build_theme(src: Image.Image, mid: tuple[int, int, int], sat_boost: float) -> Image.Image:
    im = src.copy()
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if is_platform_grey(r, g, b, a):
                px[x, y] = recolor_pixel(r, g, b, a, mid, sat_boost)
    return im


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    src = Image.open(SRC).convert("RGBA")
    for n, cfg in THEMES.items():
        out = build_theme(src, cfg["mid"], cfg["sat_boost"])
        path = os.path.join(OUT, cfg["name"])
        out.save(path)
        # verify atlas 3,1 center
        c = out.getpixel((3 * 64 + 32, 1 * 64 + 32))
        print("wrote", cfg["name"], "atlas3,1=", c)
    print("done")


if __name__ == "__main__":
    main()
