"""Resize parallax layers to match 1280x720 play view."""
from __future__ import annotations

import os
from PIL import Image

BASE = r"c:\Users\jakkr\OneDrive\เดสก์ท็อป\Gamedev\lab4\2D-Platformer-Starter-Kit-main\Assets\Generated\BG"
W, H = 1280, 720


def cover_resize(im: Image.Image, tw: int, th: int) -> Image.Image:
    im = im.convert("RGBA")
    scale = max(tw / im.width, th / im.height)
    nw, nh = int(im.width * scale), int(im.height * scale)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - tw) // 2
    top = (nh - th) // 2
    return im.crop((left, top, left + tw, top + th))


def fade_top(im: Image.Image, frac: float = 0.4) -> Image.Image:
    im = im.copy()
    w, h = im.size
    px = im.load()
    y1 = int(h * frac)
    for y in range(y1):
        mul = y / max(1, y1)
        for x in range(w):
            r, g, b, a = px[x, y]
            px[x, y] = (r, g, b, int(a * mul))
    return im


def main() -> None:
    sky = cover_resize(Image.open(os.path.join(BASE, "bg_sky_full.png")), W, H)
    sky.save(os.path.join(BASE, "bg_sky.png"))

    mt = cover_resize(Image.open(os.path.join(BASE, "bg_mountains_full.png")), W, H)
    mt = fade_top(mt, 0.08)
    # fade bottom blend
    px = mt.load()
    for y in range(int(H * 0.7), H):
        mul = 1.0 - (y - int(H * 0.7)) / max(1, H - int(H * 0.7))
        for x in range(W):
            r, g, b, a = px[x, y]
            px[x, y] = (r, g, b, int(a * mul))
    mt.save(os.path.join(BASE, "bg_mountains.png"))

    rice = cover_resize(Image.open(os.path.join(BASE, "bg_rice_full.png")), W, H)
    rice = fade_top(rice, 0.35)
    rice.save(os.path.join(BASE, "bg_rice.png"))

    trees_full = Image.open(os.path.join(BASE, "bg_trees_full.png")).convert("RGBA")
    # bottom strip → 1280x280 foliage
    strip = trees_full.crop((0, int(trees_full.height * 0.55), trees_full.width, trees_full.height))
    strip = strip.resize((W, 280), Image.Resampling.LANCZOS)
    strip = fade_top(strip, 0.45)
    strip.save(os.path.join(BASE, "bg_trees.png"))
    print("wrote BGs at", W, "x", H, "| trees", strip.size)


if __name__ == "__main__":
    main()
