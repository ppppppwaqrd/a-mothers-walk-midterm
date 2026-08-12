"""Build 4 full-bleed level backgrounds (no tiling seams)."""
from __future__ import annotations

import os
from PIL import Image, ImageEnhance, ImageFilter

BASE = r"c:\Users\jakkr\OneDrive\เดสก์ท็อป\Gamedev\lab4\2D-Platformer-Starter-Kit-main\Assets\Generated\BG"
W, H = 1280, 720


def load(name: str) -> Image.Image:
    return Image.open(os.path.join(BASE, name)).convert("RGBA")


def cover(im: Image.Image, tw: int = W, th: int = H) -> Image.Image:
    im = im.convert("RGBA")
    scale = max(tw / im.width, th / im.height)
    nw, nh = max(1, int(im.width * scale)), max(1, int(im.height * scale))
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - tw) // 2
    top = (nh - th) // 2
    return im.crop((left, top, left + tw, top + th))


def knock_near_white(im: Image.Image, thresh: int = 245) -> Image.Image:
    im = im.copy()
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a and r >= thresh and g >= thresh and b >= thresh:
                px[x, y] = (r, g, b, 0)
    return im


def tint(im: Image.Image, rgb: tuple[float, float, float], strength: float = 0.25) -> Image.Image:
    overlay = Image.new("RGBA", im.size, (
        int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255), int(255 * strength)
    ))
    return Image.alpha_composite(im.convert("RGBA"), overlay)


def save(im: Image.Image, name: str) -> None:
    path = os.path.join(BASE, name)
    im.convert("RGBA").save(path)
    print("wrote", name, im.size)


def main() -> None:
    sky = cover(load("bg_sky_full.png"))
    mountains = knock_near_white(cover(load("bg_mountains_full.png")))
    rice = knock_near_white(cover(load("bg_rice_full.png")))
    trees = cover(load("bg_trees_full.png"))

    # --- Level 1: village evening (sky + rice fields) ---
    l1 = sky.copy()
    # soften mountains into sky
    mt = mountains.copy()
    mt.putalpha(mt.getchannel("A").point(lambda a: int(a * 0.85) if a else 0))
    l1 = Image.alpha_composite(l1, mt)
    # rice only lower half
    rice_band = rice.crop((0, int(H * 0.42), W, H))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.paste(rice_band, (0, int(H * 0.42)))
    # fade top of rice band
    px = layer.load()
    fade = int(H * 0.12)
    y0 = int(H * 0.42)
    for y in range(y0, min(H, y0 + fade)):
        mul = (y - y0) / max(1, fade)
        for x in range(W):
            r, g, b, a = px[x, y]
            px[x, y] = (r, g, b, int(a * mul))
    l1 = Image.alpha_composite(l1, layer)
    l1 = ImageEnhance.Color(l1).enhance(1.05)
    save(l1, "bg_level_01.png")

    # --- Level 2: bamboo / jungle (soft sky blend, no hard seam) ---
    l2 = trees.copy()
    l2 = ImageEnhance.Brightness(l2).enhance(1.2)
    l2 = ImageEnhance.Contrast(l2).enhance(1.02)
    sky2 = tint(sky.copy(), (0.12, 0.28, 0.22), 0.28)
    # Wide soft gradient so sky melts into canopy (no hard bar)
    mask = Image.new("L", (W, H), 0)
    mp = mask.load()
    for y in range(H):
        t = y / float(H)
        if t < 0.18:
            v = 255
        elif t < 0.55:
            v = int(255 * (1.0 - (t - 0.18) / 0.37))
        else:
            v = 0
        for x in range(W):
            mp[x, y] = v
    mask = mask.filter(ImageFilter.GaussianBlur(radius=18))
    l2 = Image.composite(sky2, l2, mask)
    save(l2, "bg_level_02.png")

    # --- Level 3: mountain trail (mountains dominate, cool dusk) ---
    sky3 = tint(sky.copy(), (0.25, 0.2, 0.45), 0.22)
    sky3 = ImageEnhance.Color(sky3).enhance(0.85)
    # Scale mountains larger / lower so peaks fill more of frame
    mt_big = cover(load("bg_mountains_full.png"), W, int(H * 1.15))
    mt_big = knock_near_white(mt_big)
    layer_mt = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer_mt.paste(mt_big.crop((0, mt_big.height - H, W, mt_big.height)), (0, 0))
    l3 = Image.alpha_composite(sky3, layer_mt)
    l3 = tint(l3, (0.2, 0.15, 0.35), 0.08)
    save(l3, "bg_level_03.png")

    # --- Level 4: Ai Tong golden fields (warm sunset) ---
    sky4 = tint(sky.copy(), (1.0, 0.55, 0.25), 0.28)
    sky4 = ImageEnhance.Color(sky4).enhance(1.15)
    rice4 = knock_near_white(cover(load("bg_rice_full.png")), thresh=248)
    rice4 = ImageEnhance.Color(rice4).enhance(1.25)
    rice4 = ImageEnhance.Brightness(rice4).enhance(1.1)
    # warm overlay on lower fields
    warm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wp = warm.load()
    for y in range(int(H * 0.4), H):
        a = int(90 * ((y - H * 0.4) / (H * 0.6)))
        for x in range(W):
            wp[x, y] = (255, 160, 60, a)
    l4 = Image.alpha_composite(sky4, rice4)
    l4 = Image.alpha_composite(l4, warm)
    save(l4, "bg_level_04.png")

    # also refresh bg_main as level 1 alias for safety
    l1.save(os.path.join(BASE, "bg_main.png"))
    print("done")


if __name__ == "__main__":
    main()
