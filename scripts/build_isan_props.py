"""Paint Isan gameplay props: finish door, pushables, puzzle skins, minigame bits."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

# Reuse the same ink-on-paper painter as the HUD kit.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_storybook_ui import (  # noqa: E402
    INK,
    Pen,
    blank,
    over,
    paint,
    save,
    wash,
    wobble,
)

OUT_SPRITES = Path(__file__).resolve().parent.parent / "Assets" / "Generated" / "Spritesheet"
OUT_UI = Path(__file__).resolve().parent.parent / "Assets" / "Generated" / "UI"

WOOD = (148, 102, 62)
WOOD_DARK = (104, 70, 44)
STRAW = (206, 170, 96)
BAMBOO = (168, 156, 72)
LATERITE = (176, 96, 62)
LATERITE_DARK = (128, 64, 44)
GREEN = (86, 116, 66)
GOLD = (214, 162, 72)


def _save_sprite(layer: np.ndarray, name: str) -> None:
    from build_storybook_ui import SS

    OUT_SPRITES.mkdir(parents=True, exist_ok=True)
    arr = (np.clip(layer, 0, 1) * 255.0).round().astype(np.uint8)
    img = Image.fromarray(arr, "RGBA")
    img = img.resize((img.width // SS, img.height // SS), Image.LANCZOS)
    path = OUT_SPRITES / f"{name}.png"
    img.save(path, optimize=True)
    print(f"  sprites/{name}.png  {img.width}x{img.height}")


def finish_door() -> np.ndarray:
    w, h = 96, 128
    posts = Pen(w, h)
    posts.rect(10, 18, 22, 118, 2)
    posts.rect(74, 18, 86, 118, 2)
    lintel = Pen(w, h)
    lintel.poly([(6, 16), (90, 16), (86, 30), (10, 30)])
    door = Pen(w, h)
    door.rect(24, 32, 72, 116, 3)
    slats = Pen(w, h)
    for y in (48, 66, 84, 102):
        slats.line([(28, y), (68, y)], 1.4)
    kratib = Pen(w, h)
    kratib.poly([(38, 6), (58, 6), (56, 22), (40, 22)])
    kratib.ellipse(48, 6, 10, 3)
    layer = paint(
        w,
        h,
        [
            (wobble(posts.arr(), 0.35, 1), WOOD_DARK),
            (wobble(lintel.arr(), 0.4, 2), WOOD),
            (wobble(door.arr(), 0.3, 3), (168, 118, 72)),
            (slats.arr() * 0.7, WOOD_DARK),
            (wobble(kratib.arr(), 0.4, 4), STRAW),
        ],
        line=1.6,
        seed=301,
    )
    return layer


def push_laterite() -> np.ndarray:
    w, h = 80, 64
    rock = Pen(w, h)
    rock.poly([(8, 50), (18, 18), (40, 8), (66, 16), (74, 48), (60, 58), (16, 58)])
    m = wobble(rock.arr(), 0.55, 11)
    layer = paint(w, h, [(m, LATERITE)], line=1.7, seed=311)
    speck = Pen(w, h)
    speck.ellipse(28, 28, 4, 3)
    speck.ellipse(52, 36, 5, 3)
    return over(layer, wash(speck.arr() * m * 0.5, LATERITE_DARK, pool=0.0, seed=312))


def push_bamboo() -> np.ndarray:
    w, h = 96, 40
    poles = Pen(w, h)
    for i, y in enumerate((10, 18, 26, 32)):
        poles.rect(6 + i, y - 4, 90 - i, y + 4, 3)
    bind = Pen(w, h)
    bind.rect(18, 6, 26, 36, 1)
    bind.rect(70, 6, 78, 36, 1)
    return paint(
        w,
        h,
        [
            (wobble(poles.arr(), 0.35, 21), BAMBOO),
            (wobble(bind.arr(), 0.3, 22), STRAW),
        ],
        line=1.5,
        seed=321,
    )


def bamboo_gate() -> np.ndarray:
    w, h = 72, 112
    poles = Pen(w, h)
    poles.rect(8, 8, 18, 108, 2)
    poles.rect(54, 8, 64, 108, 2)
    slats = Pen(w, h)
    for y in range(16, 100, 12):
        slats.rect(16, y, 56, y + 6, 2)
    return paint(
        w,
        h,
        [
            (wobble(poles.arr(), 0.3, 31), WOOD_DARK),
            (wobble(slats.arr(), 0.35, 32), BAMBOO),
        ],
        line=1.6,
        seed=331,
    )


def bamboo_lever() -> np.ndarray:
    w, h = 56, 28
    base = Pen(w, h)
    base.rect(6, 16, 50, 26, 3)
    stick = Pen(w, h)
    stick.poly([(24, 22), (44, 6), (50, 10), (28, 24)])
    return paint(
        w,
        h,
        [
            (wobble(base.arr(), 0.35, 41), WOOD),
            (wobble(stick.arr(), 0.4, 42), BAMBOO),
        ],
        line=1.4,
        seed=341,
    )


def bamboo_can() -> np.ndarray:
    w, h = 28, 48
    body = Pen(w, h)
    body.rect(6, 8, 22, 42, 6)
    rim = Pen(w, h)
    rim.ellipse(14, 10, 8, 3)
    return paint(
        w,
        h,
        [
            (wobble(body.arr(), 0.35, 51), BAMBOO),
            (wobble(rim.arr(), 0.3, 52), (188, 176, 96)),
        ],
        line=1.4,
        seed=351,
    )


def mini_buffalo() -> np.ndarray:
    w, h = 80, 48
    body = Pen(w, h)
    body.ellipse(40, 28, 26, 14)
    head = Pen(w, h)
    head.ellipse(68, 20, 10, 8)
    legs = Pen(w, h)
    for x in (22, 34, 46, 56):
        legs.rect(x, 36, x + 5, 46, 1)
    horn = Pen(w, h)
    horn.line([(62, 14), (56, 4), (70, 8)], 2.2)
    return paint(
        w,
        h,
        [
            (wobble(body.arr(), 0.4, 61), (86, 78, 70)),
            (wobble(head.arr(), 0.35, 62), (74, 66, 58)),
            (legs.arr(), (58, 50, 44)),
            (horn.arr(), (40, 36, 32)),
        ],
        line=1.5,
        seed=361,
    )


def mini_crow() -> np.ndarray:
    w, h = 48, 36
    body = Pen(w, h)
    body.ellipse(22, 20, 14, 8)
    wing = Pen(w, h)
    wing.poly([(8, 20), (4, 8), (26, 16), (20, 22)])
    head = Pen(w, h)
    head.ellipse(36, 16, 6, 5)
    beak = Pen(w, h)
    beak.poly([(41, 15), (48, 17), (41, 19)])
    tail = Pen(w, h)
    tail.poly([(8, 20), (2, 18), (8, 26)])
    return paint(
        w,
        h,
        [
            (wobble(body.arr(), 0.4, 111), (52, 46, 44)),
            (wobble(wing.arr(), 0.35, 112), (36, 32, 30)),
            (wobble(head.arr(), 0.3, 113), (44, 40, 38)),
            (beak.arr(), (186, 150, 82)),
            (tail.arr(), (32, 28, 26)),
        ],
        line=1.3,
        seed=411,
    )


def mini_chicken() -> np.ndarray:
    w, h = 40, 36
    body = Pen(w, h)
    body.ellipse(18, 20, 12, 9)
    head = Pen(w, h)
    head.ellipse(30, 12, 6, 6)
    beak = Pen(w, h)
    beak.poly([(35, 12), (40, 14), (35, 16)])
    comb = Pen(w, h)
    comb.ellipse(28, 6, 3, 3)
    return paint(
        w,
        h,
        [
            (wobble(body.arr(), 0.4, 71), (214, 196, 150)),
            (wobble(head.arr(), 0.35, 72), (232, 220, 180)),
            (beak.arr(), GOLD),
            (comb.arr(), (186, 72, 62)),
        ],
        line=1.3,
        seed=371,
    )


def rice_mat() -> np.ndarray:
    w, h = 120, 48
    mat = Pen(w, h)
    mat.rect(4, 10, 116, 40, 4)
    grains = Pen(w, h)
    rng = np.random.default_rng(81)
    for _ in range(40):
        grains.ellipse(float(rng.integers(10, 110)), float(rng.integers(14, 36)), 2.2, 1.4)
    return paint(
        w,
        h,
        [
            (wobble(mat.arr(), 0.3, 81), (186, 150, 82)),
            (grains.arr() * 0.8, STRAW),
        ],
        line=1.4,
        seed=381,
    )


def mini_villager() -> np.ndarray:
    w, h = 36, 56
    body = Pen(w, h)
    body.rect(10, 22, 26, 48, 4)
    head = Pen(w, h)
    head.ellipse(18, 14, 8, 8)
    wrap = Pen(w, h)
    wrap.rect(8, 34, 28, 50, 3)
    return paint(
        w,
        h,
        [
            (wobble(head.arr(), 0.35, 91), (214, 178, 140)),
            (wobble(body.arr(), 0.3, 92), (96, 122, 86)),
            (wobble(wrap.arr(), 0.35, 93), (186, 86, 62)),
        ],
        line=1.4,
        seed=391,
    )


def deva() -> np.ndarray:
    """Standing thevada in white/gold cloth, grounded at the hem."""
    w, h = 56, 96
    halo = Pen(w, h)
    halo.ellipse(28, 18, 16, 11)
    crown = Pen(w, h)
    crown.poly([(20, 18), (28, 4), (36, 18)])
    head = Pen(w, h)
    head.ellipse(28, 24, 8, 8)
    robe = Pen(w, h)
    robe.poly([(18, 34), (38, 34), (48, 92), (8, 92)])
    sash = Pen(w, h)
    sash.poly([(16, 46), (40, 44), (42, 54), (14, 56)])
    arm_l = Pen(w, h)
    arm_l.poly([(18, 38), (8, 56), (14, 58), (22, 42)])
    arm_r = Pen(w, h)
    arm_r.poly([(38, 38), (50, 28), (46, 24), (36, 36)])
    return paint(
        w,
        h,
        [
            (wobble(halo.arr(), 0.35, 121), (244, 220, 140)),
            (wobble(robe.arr(), 0.35, 122), (236, 228, 210)),
            (wobble(sash.arr(), 0.3, 123), GOLD),
            (wobble(arm_l.arr(), 0.3, 124), (236, 228, 210)),
            (wobble(arm_r.arr(), 0.3, 125), (236, 228, 210)),
            (wobble(head.arr(), 0.3, 126), (214, 178, 140)),
            (wobble(crown.arr(), 0.35, 127), GOLD),
        ],
        line=1.5,
        seed=421,
    )


def icon_godmode() -> np.ndarray:
    w, h = 32, 32
    wing = Pen(w, h)
    wing.poly([(4, 18), (16, 6), (28, 18), (16, 14)])
    star = Pen(w, h)
    star.ellipse(16, 20, 5, 5)
    return paint(w, h, [(wobble(wing.arr(), 0.4, 101), GOLD), (star.arr(), (244, 228, 160))], line=1.4, seed=401)


MANIFEST = {
    "finish_door": finish_door,
    "push_laterite": push_laterite,
    "push_bamboo": push_bamboo,
    "bamboo_gate": bamboo_gate,
    "bamboo_lever": bamboo_lever,
    "bamboo_can": bamboo_can,
    "mini_buffalo": mini_buffalo,
    "mini_crow": mini_crow,
    "mini_chicken": mini_chicken,
    "rice_mat": rice_mat,
    "mini_villager": mini_villager,
    "deva": deva,
}


def main() -> None:
    import build_storybook_ui as ui

    wanted = sys.argv[1:] or list(MANIFEST)
    for name in wanted:
        if name == "icon_godmode":
            ui.OUT = OUT_UI
            ui.save(icon_godmode(), "icon_godmode")
            continue
        fn = MANIFEST.get(name)
        if fn is None:
            print("unknown", name)
            continue
        _save_sprite(fn(), name)
    if not sys.argv[1:]:
        ui.OUT = OUT_UI
        ui.save(icon_godmode(), "icon_godmode")
    print("done")


if __name__ == "__main__":
    main()
