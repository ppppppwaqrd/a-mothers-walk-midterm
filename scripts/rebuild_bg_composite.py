"""Build one correct composite parallax BG for the game viewport."""
from __future__ import annotations

import os
from PIL import Image

BASE = r"c:\Users\jakkr\OneDrive\เดสก์ท็อป\Gamedev\lab4\2D-Platformer-Starter-Kit-main\Assets\Generated\BG"
W, H = 1280, 720


def knock_white(im: Image.Image, thresh: int = 242, soft: int = 20) -> Image.Image:
    im = im.convert("RGBA")
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            if r >= thresh and g >= thresh and b >= thresh:
                px[x, y] = (r, g, b, 0)
            elif min(r, g, b) >= thresh - soft:
                t = (min(r, g, b) - (thresh - soft)) / soft
                px[x, y] = (r, g, b, int(a * (1.0 - t)))
    return im


def fit_width(im: Image.Image, width: int) -> Image.Image:
    im = im.convert("RGBA")
    h = int(im.height * (width / im.width))
    return im.resize((width, h), Image.Resampling.LANCZOS)


def main() -> None:
    sky = Image.open(os.path.join(BASE, "bg_sky_full.png")).convert("RGBA")
    sky = sky.resize((W, H), Image.Resampling.LANCZOS)

    mt = knock_white(Image.open(os.path.join(BASE, "bg_mountains_full.png")))
    mt = fit_width(mt, W)
    # place mountains so peaks sit in lower-mid sky
    mt_y = H - mt.height + 40
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.paste(sky, (0, 0))
    layer.alpha_composite(mt, (0, mt_y))

    rice = knock_white(Image.open(os.path.join(BASE, "bg_rice_full.png")))
    # keep lower 50% of rice scene
    rice = rice.crop((0, int(rice.height * 0.48), rice.width, rice.height))
    rice = fit_width(rice, W)
    rice_y = H - rice.height + 10
    layer.alpha_composite(rice, (0, rice_y))

    # Soft bottom vignette so it meets ground tiles cleanly
    layer.save(os.path.join(BASE, "bg_main.png"))

    # Foreground trees: thin strip only
    trees = Image.open(os.path.join(BASE, "bg_trees_full.png")).convert("RGBA")
    trees = trees.crop((0, int(trees.height * 0.68), trees.width, trees.height))
    trees = fit_width(trees, W)
    trees = knock_white(trees, thresh=250, soft=8)
    # fade top + lower opacity
    px = trees.load()
    th = trees.height
    for y in range(th):
        top_mul = min(1.0, y / max(1, int(th * 0.4)))
        for x in range(trees.width):
            r, g, b, a = px[x, y]
            px[x, y] = (r, g, b, int(a * top_mul * 0.55))
    trees.save(os.path.join(BASE, "bg_trees.png"))

    # Keep individual names used by scene — point sky/mountains/rice to split roles
    # sky = main composite (so old 3-layer setup can be simplified in tscn)
    layer.save(os.path.join(BASE, "bg_sky.png"))
    # empty transparent placeholders so leftover refs don't block
    Image.new("RGBA", (W, H), (0, 0, 0, 0)).save(os.path.join(BASE, "bg_mountains.png"))
    Image.new("RGBA", (W, 1), (0, 0, 0, 0)).save(os.path.join(BASE, "bg_rice.png"))

    print("bg_main/sky", layer.size, "trees", trees.size)
    print("center sky", layer.getpixel((W // 2, H // 2)))
    print("bottom sky", layer.getpixel((W // 2, H - 20)))


if __name__ == "__main__":
    main()
