"""Make parallax BG layers fit platformer view (trees were full-frame opaque bamboo)."""
from __future__ import annotations

import os
from PIL import Image

BASE = r"c:\Users\jakkr\OneDrive\เดสก์ท็อป\Gamedev\lab4\2D-Platformer-Starter-Kit-main\Assets\Generated\BG"


def backup(name: str) -> str:
    src = os.path.join(BASE, name)
    bak = os.path.join(BASE, name.replace(".png", "_full.png"))
    im = Image.open(src).convert("RGBA")
    if not os.path.exists(bak):
        im.save(bak)
        print("backed up", name)
    return bak


def fade_bottom(im: Image.Image, start_frac: float = 0.65) -> Image.Image:
    im = im.copy()
    w, h = im.size
    px = im.load()
    y0 = int(h * start_frac)
    for y in range(y0, h):
        mul = 1.0 - (y - y0) / max(1, h - y0)
        for x in range(w):
            r, g, b, a = px[x, y]
            px[x, y] = (r, g, b, int(a * mul))
    return im


def fade_top(im: Image.Image, end_frac: float = 0.35) -> Image.Image:
    im = im.copy()
    w, h = im.size
    px = im.load()
    y1 = int(h * end_frac)
    for y in range(0, y1):
        mul = y / max(1, y1)
        for x in range(w):
            r, g, b, a = px[x, y]
            px[x, y] = (r, g, b, int(a * mul))
    return im


def main() -> None:
    for n in ["bg_sky.png", "bg_mountains.png", "bg_rice.png", "bg_trees.png"]:
        backup(n)

    sky = Image.open(os.path.join(BASE, "bg_sky_full.png")).convert("RGBA")
    sky.save(os.path.join(BASE, "bg_sky.png"))

    mt = fade_bottom(Image.open(os.path.join(BASE, "bg_mountains_full.png")).convert("RGBA"), 0.62)
    mt.save(os.path.join(BASE, "bg_mountains.png"))

    rice = fade_top(Image.open(os.path.join(BASE, "bg_rice_full.png")).convert("RGBA"), 0.38)
    rice = fade_bottom(rice, 0.88)
    rice.save(os.path.join(BASE, "bg_rice.png"))

    trees = Image.open(os.path.join(BASE, "bg_trees_full.png")).convert("RGBA")
    w, h = trees.size
    # bottom foliage strip only
    strip = trees.crop((0, int(h * 0.55), w, h))
    strip = fade_top(strip, 0.5)
    strip.save(os.path.join(BASE, "bg_trees.png"))
    print("trees strip", strip.size)
    print("done")


if __name__ == "__main__":
    main()
