"""Rebuild parallax BG layers: remove opaque white so layers stack correctly."""
from __future__ import annotations

import os
from PIL import Image

BASE = r"c:\Users\jakkr\OneDrive\เดสก์ท็อป\Gamedev\lab4\2D-Platformer-Starter-Kit-main\Assets\Generated\BG"
W, H = 1280, 720


def knock_white(im: Image.Image, thresh: int = 245, soft: int = 18) -> Image.Image:
    """Make near-white pixels transparent (AI gens have solid white sky)."""
    im = im.convert("RGBA")
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if r >= thresh and g >= thresh and b >= thresh:
                px[x, y] = (r, g, b, 0)
            elif r >= thresh - soft and g >= thresh - soft and b >= thresh - soft:
                # soft edge
                whiteness = min(r, g, b)
                t = (whiteness - (thresh - soft)) / soft
                px[x, y] = (r, g, b, int(a * (1.0 - t)))
    return im


def fade_top_alpha(im: Image.Image, frac: float) -> Image.Image:
    im = im.copy()
    w, h = im.size
    px = im.load()
    y1 = max(1, int(h * frac))
    for y in range(y1):
        mul = y / y1
        for x in range(w):
            r, g, b, a = px[x, y]
            px[x, y] = (r, g, b, int(a * mul))
    return im


def cover_crop(im: Image.Image, tw: int, th: int) -> Image.Image:
    im = im.convert("RGBA")
    scale = max(tw / im.width, th / im.height)
    nw, nh = int(im.width * scale), int(im.height * scale)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - tw) // 2
    top = (nh - th) // 2
    return im.crop((left, top, left + tw, top + th))


def main() -> None:
    # --- Sky: full gradient, no white knock needed ---
    sky = cover_crop(Image.open(os.path.join(BASE, "bg_sky_full.png")), W, H)
    sky.save(os.path.join(BASE, "bg_sky.png"))

    # --- Mountains: full frame, knock white, keep mountains in lower half ---
    mt = cover_crop(Image.open(os.path.join(BASE, "bg_mountains_full.png")), W, H)
    mt = knock_white(mt, thresh=242, soft=20)
    mt = fade_top_alpha(mt, 0.15)
    mt.save(os.path.join(BASE, "bg_mountains.png"))

    # --- Rice: ONLY bottom field band (no opaque sky sitting in front) ---
    rice_full = Image.open(os.path.join(BASE, "bg_rice_full.png")).convert("RGBA")
    # take lower 45% of source
    top = int(rice_full.height * 0.52)
    band = rice_full.crop((0, top, rice_full.width, rice_full.height))
    band = band.resize((W, 340), Image.Resampling.LANCZOS)
    band = knock_white(band, thresh=240, soft=22)
    band = fade_top_alpha(band, 0.35)
    band.save(os.path.join(BASE, "bg_rice.png"))

    # --- Trees: thin dark foliage strip, semi-transparent ---
    trees_full = Image.open(os.path.join(BASE, "bg_trees_full.png")).convert("RGBA")
    top = int(trees_full.height * 0.62)
    strip = trees_full.crop((0, top, trees_full.width, trees_full.height))
    strip = strip.resize((W, 220), Image.Resampling.LANCZOS)
    strip = knock_white(strip, thresh=250, soft=10)
    strip = fade_top_alpha(strip, 0.55)
    # reduce overall opacity so it doesn't dominate
    px = strip.load()
    for y in range(strip.height):
        for x in range(strip.width):
            r, g, b, a = px[x, y]
            px[x, y] = (r, g, b, int(a * 0.75))
    strip.save(os.path.join(BASE, "bg_trees.png"))

    # verify
    for name in ["bg_sky.png", "bg_mountains.png", "bg_rice.png", "bg_trees.png"]:
        im = Image.open(os.path.join(BASE, name)).convert("RGBA")
        a = im.getchannel("A")
        hist = a.histogram()
        clear = sum(hist[:10])
        opaque = sum(hist[240:])
        cx, cy = im.size[0] // 2, im.size[1] // 2
        print(f"{name}: {im.size} clear={clear} opaque={opaque} center={im.getpixel((cx, cy))}")


if __name__ == "__main__":
    main()
