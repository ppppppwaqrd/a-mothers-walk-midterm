"""Paint the storybook UI kit: paper panels, ink buttons and hand-drawn icons.

Everything here is drawn the same way as the parallax backgrounds so the HUD
looks like it was inked onto the same page: a shape mask, a watercolour wash that
pools darker where it dried against an edge, then a jittered ink contour.

Shapes are drawn at SS times the final size and reduced at the end, which is what
gives the curves and ink lines their soft edges at HUD sizes.

Output: Assets/Generated/UI/*.png -- see MANIFEST at the bottom for the list and
the nine-patch margins that storybook_theme.tres relies on.

Usage: python scripts/build_storybook_ui.py [name ...]
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "Assets" / "Generated" / "UI"

SS = 4

INK = (58, 42, 30)
PAPER = (244, 234, 212)
PAPER_EDGE = (206, 188, 158)

GOLD = (214, 162, 72)
RED = (186, 72, 62)
GREEN = (118, 152, 78)
BLUE = (94, 126, 158)
STONE = (150, 138, 124)
STRAW = (206, 170, 96)
PLUM = (132, 92, 118)


# --------------------------------------------------------------------------- #
# Drawing primitives
# --------------------------------------------------------------------------- #


class Pen:
    """A supersampled greyscale mask with a PIL drawing surface."""

    def __init__(self, w: int, h: int):
        self.w, self.h = w * SS, h * SS
        self.img = Image.new("L", (self.w, self.h), 0)
        self.d = ImageDraw.Draw(self.img)

    def s(self, *vals: float) -> list[float]:
        return [v * SS for v in vals]

    def ellipse(self, cx: float, cy: float, rx: float, ry: float) -> None:
        x0, y0, x1, y1 = self.s(cx - rx, cy - ry, cx + rx, cy + ry)
        self.d.ellipse([x0, y0, x1, y1], fill=255)

    def rect(self, x0: float, y0: float, x1: float, y1: float, r: float = 0.0) -> None:
        box = self.s(x0, y0, x1, y1)
        if r > 0.0:
            self.d.rounded_rectangle(box, radius=r * SS, fill=255)
        else:
            self.d.rectangle(box, fill=255)

    def poly(self, pts: list[tuple[float, float]]) -> None:
        self.d.polygon([(x * SS, y * SS) for x, y in pts], fill=255)

    def line(self, pts: list[tuple[float, float]], width: float) -> None:
        self.d.line([(x * SS, y * SS) for x, y in pts], fill=255, width=max(1, int(width * SS)), joint="curve")

    def arr(self) -> np.ndarray:
        return np.asarray(self.img, dtype=np.float64) / 255.0


def wobble(m: np.ndarray, amount: float, seed: int) -> np.ndarray:
    """Nudge a mask's outline about so it reads as drawn by hand."""
    rng = np.random.default_rng(seed)
    h, w = m.shape
    warp = amount * SS
    dy = ndimage.gaussian_filter(rng.standard_normal((h, w)), 9.0 * SS) * warp * 60.0
    dx = ndimage.gaussian_filter(rng.standard_normal((h, w)), 9.0 * SS) * warp * 60.0
    yy, xx = np.mgrid[0:h, 0:w]
    return ndimage.map_coordinates(m, [yy + dy, xx + dx], order=1, mode="nearest")


def contour(m: np.ndarray, width: float) -> np.ndarray:
    """The band straddling a mask's boundary, i.e. where the ink line goes."""
    r = width * SS * 0.5
    grown = ndimage.grey_dilation(m, size=(int(r * 2) | 1, int(r * 2) | 1))
    shrunk = ndimage.grey_erosion(m, size=(int(r * 2) | 1, int(r * 2) | 1))
    return np.clip(grown - shrunk, 0.0, 1.0)


def wash(m: np.ndarray, color: tuple[int, int, int], pool: float = 0.30, seed: int = 0) -> np.ndarray:
    """Fill a mask with pigment that gathers darker toward its edges."""
    rgb = np.array(color, dtype=np.float64) / 255.0
    solid = m > 0.5
    if solid.any():
        dist = ndimage.distance_transform_edt(solid)
        rim = np.clip(1.0 - dist / (5.0 * SS), 0.0, 1.0) ** 1.6
    else:
        rim = np.zeros_like(m)
    grain = ndimage.gaussian_filter(np.random.default_rng(seed).random(m.shape), 2.2 * SS)
    grain = (grain - grain.mean()) * 6.0
    shade = 1.0 - pool * rim + 0.10 * grain
    out = np.dstack([np.clip(rgb[None, None, :] * shade[:, :, None], 0, 1), m])
    return out


def over(base: np.ndarray, top: np.ndarray) -> np.ndarray:
    a = top[:, :, 3:4]
    rgb = top[:, :, :3] * a + base[:, :, :3] * (1 - a)
    alpha = np.clip(a[:, :, 0] + base[:, :, 3] * (1 - a[:, :, 0]), 0, 1)
    return np.dstack([rgb, alpha])


def blank(w: int, h: int) -> np.ndarray:
    return np.zeros((h * SS, w * SS, 4))


def ink(m: np.ndarray, width: float = 1.4, alpha: float = 0.92, seed: int = 0, color=INK) -> np.ndarray:
    band = contour(wobble(m, 0.30, seed + 5), width)
    return wash(band, color, pool=0.0, seed=seed) * np.array([1, 1, 1, alpha])


def paint(w: int, h: int, parts: list[tuple[np.ndarray, tuple[int, int, int]]], line: float = 1.4, seed: int = 0, outline: bool = True) -> np.ndarray:
    """Wash every part in order, then run one ink contour around their union."""
    layer = blank(w, h)
    union = np.zeros_like(parts[0][0])
    for i, (m, color) in enumerate(parts):
        layer = over(layer, wash(m, color, seed=seed + i * 31))
        union = np.maximum(union, m)
    if outline:
        layer = over(layer, ink(union, width=line, seed=seed))
    return layer


def save(layer: np.ndarray, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    arr = (np.clip(layer, 0, 1) * 255.0).round().astype(np.uint8)
    img = Image.fromarray(arr, "RGBA")
    img = img.resize((img.width // SS, img.height // SS), Image.LANCZOS)
    path = OUT / f"{name}.png"
    img.save(path, optimize=True)
    print(f"  {name}.png  {img.width}x{img.height}  {path.stat().st_size / 1024:.1f} KB")


# --------------------------------------------------------------------------- #
# Paper surfaces
# --------------------------------------------------------------------------- #


def paper_card(w: int, h: int, radius: float, seed: int, tone=PAPER) -> np.ndarray:
    """A leaf of paper: torn-looking edge, warm grain, ink border."""
    pen = Pen(w, h)
    pen.rect(2, 2, w - 2, h - 2, radius)
    sheet = wobble(pen.arr(), 0.55, seed)

    rgb = np.array(tone, dtype=np.float64) / 255.0
    grain = ndimage.gaussian_filter(np.random.default_rng(seed + 1).random(sheet.shape), 1.6 * SS)
    fibre = ndimage.gaussian_filter(np.random.default_rng(seed + 2).random(sheet.shape), (0.6 * SS, 7.0 * SS))
    tint = 1.0 + 0.05 * (grain - grain.mean()) * 12.0 + 0.03 * (fibre - fibre.mean()) * 12.0

    solid = sheet > 0.5
    dist = ndimage.distance_transform_edt(solid) if solid.any() else np.zeros_like(sheet)
    rim = np.clip(1.0 - dist / (7.0 * SS), 0.0, 1.0) ** 2.0
    edge = np.array(PAPER_EDGE, dtype=np.float64) / 255.0
    body = rgb[None, None, :] * tint[:, :, None]
    body = body * (1 - 0.55 * rim[:, :, None]) + edge[None, None, :] * 0.55 * rim[:, :, None]

    layer = np.dstack([np.clip(body, 0, 1), sheet])
    return over(layer, ink(sheet, width=1.7, alpha=0.55, seed=seed + 3))


def nine(w: int, h: int, fn) -> np.ndarray:
    return fn(w, h)


# --------------------------------------------------------------------------- #
# Icon shapes
# --------------------------------------------------------------------------- #


def heart(filled: bool) -> np.ndarray:
    w = h = 32
    pen = Pen(w, h)
    pen.ellipse(11.0, 12.0, 7.2, 6.6)
    pen.ellipse(21.0, 12.0, 7.2, 6.6)
    pen.poly([(4.0, 14.0), (28.0, 14.0), (16.0, 29.0)])
    m = wobble(pen.arr(), 0.4, 11)
    if filled:
        layer = paint(w, h, [(m, RED)], line=1.5, seed=11)
        gleam = Pen(w, h)
        gleam.ellipse(11.5, 10.0, 2.6, 1.9)
        return over(layer, wash(wobble(gleam.arr(), 0.3, 12) * 0.55, (252, 236, 224), pool=0.0, seed=13))
    hollow = np.clip(m - ndimage.grey_erosion(m, size=(int(2.6 * SS) | 1,) * 2), 0.0, 1.0)
    return over(blank(w, h), wash(hollow, (156, 138, 118), pool=0.0, seed=14) * np.array([1, 1, 1, 0.75]))


def kratib() -> np.ndarray:
    """The woven sticky-rice basket the player is delivering; the score icon."""
    w = h = 32
    body = Pen(w, h)
    body.poly([(8.0, 12.0), (24.0, 12.0), (22.0, 27.0), (10.0, 27.0)])
    body.ellipse(16.0, 27.0, 6.0, 2.4)
    lid = Pen(w, h)
    lid.poly([(6.5, 12.0), (25.5, 12.0), (23.0, 6.0), (9.0, 6.0)])
    lid.ellipse(16.0, 5.6, 7.0, 2.4)
    strap = Pen(w, h)
    strap.line([(16.0, 5.0), (16.0, 2.0)], 1.6)

    b = wobble(body.arr(), 0.35, 21)
    layer = paint(w, h, [(b, STRAW), (wobble(lid.arr(), 0.35, 22), (188, 150, 82)), (strap.arr(), (140, 108, 62))], line=1.5, seed=21)

    weave = Pen(w, h)
    for y in (16.0, 20.0, 24.0):
        weave.line([(9.0, y), (23.0, y)], 0.8)
    return over(layer, wash(weave.arr() * b * 0.5, (128, 96, 54), pool=0.0, seed=23))


def stone() -> np.ndarray:
    w = h = 32
    pen = Pen(w, h)
    pen.ellipse(16.0, 17.0, 11.0, 9.0)
    m = wobble(pen.arr(), 0.7, 31)
    layer = paint(w, h, [(m, STONE)], line=1.5, seed=31)
    facet = Pen(w, h)
    facet.line([(9.0, 15.0), (15.0, 11.0), (23.0, 14.0)], 1.0)
    return over(layer, wash(facet.arr() * m * 0.55, (104, 96, 88), pool=0.0, seed=32))


def note(muted: bool) -> np.ndarray:
    w = h = 32
    pen = Pen(w, h)
    pen.ellipse(12.0, 22.0, 5.4, 4.4)
    pen.rect(16.0, 5.0, 18.4, 22.0)
    pen.poly([(16.0, 5.0), (26.0, 8.0), (26.0, 12.0), (16.0, 9.0)])
    m = wobble(pen.arr(), 0.35, 41)
    layer = paint(w, h, [(m, PLUM if not muted else (150, 140, 132))], line=1.5, seed=41)
    if muted:
        return over(layer, cross_out(w, h, 42))
    return layer


def speaker(muted: bool) -> np.ndarray:
    w = h = 32
    pen = Pen(w, h)
    pen.rect(5.0, 12.0, 11.0, 20.0)
    pen.poly([(11.0, 12.0), (19.0, 5.0), (19.0, 27.0), (11.0, 20.0)])
    m = wobble(pen.arr(), 0.35, 51)
    parts = [(m, BLUE if not muted else (150, 140, 132))]
    layer = paint(w, h, parts, line=1.5, seed=51)
    if muted:
        return over(layer, cross_out(w, h, 52))
    waves = Pen(w, h)
    for r in (5.0, 8.5):
        waves.d.arc([(19.0 - r) * SS, (16.0 - r) * SS, (19.0 + r) * SS, (16.0 + r) * SS], -60, 60, fill=255, width=int(1.3 * SS))
    return over(layer, wash(waves.arr(), INK, pool=0.0, seed=53) * np.array([1, 1, 1, 0.8]))


def cross_out(w: int, h: int, seed: int) -> np.ndarray:
    pen = Pen(w, h)
    pen.line([(6.0, 6.0), (26.0, 26.0)], 2.2)
    return wash(wobble(pen.arr(), 0.4, seed), (168, 62, 54), pool=0.0, seed=seed) * np.array([1, 1, 1, 0.95])


def bookmark() -> np.ndarray:
    """Save: a ribbon bookmark slipped into the page."""
    w = h = 32
    pen = Pen(w, h)
    pen.poly([(10.0, 3.0), (22.0, 3.0), (22.0, 27.0), (16.0, 21.0), (10.0, 27.0)])
    m = wobble(pen.arr(), 0.4, 61)
    layer = paint(w, h, [(m, RED)], line=1.5, seed=61)
    fold = Pen(w, h)
    fold.line([(13.0, 7.0), (19.0, 7.0)], 1.0)
    return over(layer, wash(fold.arr() * m * 0.6, (128, 46, 40), pool=0.0, seed=62))


def pause_icon() -> np.ndarray:
    w = h = 32
    pen = Pen(w, h)
    pen.rect(9.0, 6.0, 14.0, 26.0, 1.5)
    pen.rect(18.0, 6.0, 23.0, 26.0, 1.5)
    return paint(w, h, [(wobble(pen.arr(), 0.35, 71), (96, 82, 68))], line=1.5, seed=71)


def chevron(direction: str) -> np.ndarray:
    """A pen-stroke arrow for the touch pad."""
    w = h = 40
    pen = Pen(w, h)
    if direction == "left":
        pts = [(26.0, 8.0), (13.0, 20.0), (26.0, 32.0)]
    elif direction == "right":
        pts = [(14.0, 8.0), (27.0, 20.0), (14.0, 32.0)]
    else:
        pts = [(8.0, 26.0), (20.0, 13.0), (32.0, 26.0)]
    pen.line(pts, 4.2)
    m = wobble(pen.arr(), 0.5, 81)
    return over(blank(w, h), wash(m, (74, 60, 48), pool=0.20, seed=81) * np.array([1, 1, 1, 0.9]))


def throw_icon() -> np.ndarray:
    """Throw: a stone in flight, trailing speed lines."""
    w = h = 40
    trail = Pen(w, h)
    for y, x1 in ((13.0, 15.0), (20.0, 12.0), (27.0, 17.0)):
        trail.line([(4.0, y + 3.0), (x1, y)], 1.8)
    rock = Pen(w, h)
    rock.ellipse(26.0, 18.0, 9.0, 7.6)
    layer = over(blank(w, h), wash(wobble(trail.arr(), 0.35, 91), (120, 100, 82), pool=0.0, seed=91) * np.array([1, 1, 1, 0.8]))
    m = wobble(rock.arr(), 0.6, 92)
    layer = over(layer, paint(w, h, [(m, STONE)], line=1.6, seed=92))
    facet = Pen(w, h)
    facet.line([(20.0, 16.0), (26.0, 12.5), (32.0, 16.0)], 1.1)
    return over(layer, wash(facet.arr() * m * 0.55, (104, 96, 88), pool=0.0, seed=93))


def quill() -> np.ndarray:
    """Back / return: a feather quill pointing away."""
    w = h = 32
    feather = Pen(w, h)
    feather.poly([(26.0, 4.0), (28.0, 12.0), (12.0, 24.0), (7.0, 26.0), (9.0, 20.0)])
    shaft = Pen(w, h)
    shaft.line([(26.0, 5.0), (8.0, 26.0)], 1.2)
    layer = paint(w, h, [(wobble(feather.arr(), 0.4, 101), (198, 206, 210))], line=1.5, seed=101)
    return over(layer, wash(shaft.arr(), INK, pool=0.0, seed=102) * np.array([1, 1, 1, 0.7]))


# --------------------------------------------------------------------------- #
# Nine-patch pieces
# --------------------------------------------------------------------------- #


def panel() -> np.ndarray:
    return paper_card(96, 96, 10.0, 201)


def panel_dark() -> np.ndarray:
    return paper_card(96, 96, 10.0, 202, tone=(58, 50, 44))


def button(state: str) -> np.ndarray:
    w = h = 48
    tone = {
        "normal": (236, 222, 196),
        "hover": (247, 234, 200),
        "pressed": (206, 188, 152),
        "disabled": (218, 212, 202),
    }[state]
    seed = {"normal": 211, "hover": 212, "pressed": 213, "disabled": 214}[state]
    card = paper_card(w, h, 7.0, seed, tone=tone)
    if state == "pressed":
        return card
    # A second contour just inside the edge, the way a drawn box gets gone over twice.
    pen = Pen(w, h)
    pen.rect(5, 5, w - 5, h - 5, 5.5)
    return over(card, ink(wobble(pen.arr(), 0.4, seed + 9), width=1.2, alpha=0.34, seed=seed + 9))


def bar_trough() -> np.ndarray:
    w, h = 48, 24
    pen = Pen(w, h)
    pen.rect(1, 1, w - 1, h - 1, 6.0)
    m = wobble(pen.arr(), 0.4, 221)
    layer = over(blank(w, h), wash(m, (74, 62, 52), pool=0.35, seed=221) * np.array([1, 1, 1, 0.82]))
    return over(layer, ink(m, width=1.5, alpha=0.7, seed=222))


def bar_fill(color: tuple[int, int, int], seed: int) -> np.ndarray:
    w, h = 48, 24
    pen = Pen(w, h)
    pen.rect(0, 0, w, h, 5.0)
    m = wobble(pen.arr(), 0.3, seed)
    layer = over(blank(w, h), wash(m, color, pool=0.28, seed=seed))
    sheen = Pen(w, h)
    sheen.rect(2, 3, w - 2, h * 0.42, 3.0)
    return over(layer, wash(sheen.arr() * m * 0.30, (255, 250, 236), pool=0.0, seed=seed + 1))


def slider_track(filled: bool = False) -> np.ndarray:
    """A ruled groove. Godot stretches this to the whole widget, so the
    groove is inset vertically and the art keeps its own breathing room."""
    w, h = 32, 18
    pen = Pen(w, h)
    pen.rect(1, 6, w - 1, h - 6, 3.0)
    m = wobble(pen.arr(), 0.3, 231)
    tint = (150, 118, 78) if filled else (206, 192, 168)
    layer = over(blank(w, h), wash(m, tint, pool=0.34, seed=231))
    return over(layer, ink(m, width=1.3, alpha=0.75, seed=232))


def slider_grabber() -> np.ndarray:
    w = h = 26
    pen = Pen(w, h)
    pen.ellipse(13.0, 13.0, 9.0, 9.0)
    m = wobble(pen.arr(), 0.5, 241)
    layer = paint(w, h, [(m, GOLD)], line=1.6, seed=241)
    gleam = Pen(w, h)
    gleam.ellipse(10.0, 10.0, 2.8, 2.2)
    return over(layer, wash(gleam.arr() * 0.6, (255, 246, 224), pool=0.0, seed=242))


def check(on: bool) -> np.ndarray:
    w = h = 28
    box = Pen(w, h)
    box.rect(3, 3, w - 3, h - 3, 3.0)
    m = wobble(box.arr(), 0.45, 251)
    hollow = np.clip(m - ndimage.grey_erosion(m, size=(int(2.2 * SS) | 1,) * 2), 0.0, 1.0)
    layer = over(blank(w, h), wash(hollow, INK, pool=0.0, seed=251) * np.array([1, 1, 1, 0.85]))
    if not on:
        return layer
    tick = Pen(w, h)
    tick.line([(8.0, 15.0), (12.5, 20.0), (21.0, 8.0)], 2.6)
    return over(layer, wash(wobble(tick.arr(), 0.4, 252), (120, 148, 76), pool=0.0, seed=252))


def page_frame() -> np.ndarray:
    """Vignette that keeps gameplay looking like it sits inside an open book."""
    w = h = 128
    edge = 26
    yy, xx = np.mgrid[0 : h * SS, 0 : w * SS]
    d = np.minimum(np.minimum(xx, w * SS - 1 - xx), np.minimum(yy, h * SS - 1 - yy))
    fall = np.clip(1.0 - d / (edge * SS), 0.0, 1.0) ** 1.9
    grain = ndimage.gaussian_filter(np.random.default_rng(261).random((h * SS, w * SS)), 2.0 * SS)
    fall *= 0.82 + 0.36 * (grain - grain.mean()) * 8.0
    rgb = np.array((52, 38, 26), dtype=np.float64) / 255.0
    return np.dstack([np.broadcast_to(rgb, (h * SS, w * SS, 3)), np.clip(fall * 0.5, 0, 1)])


# --------------------------------------------------------------------------- #
# Manifest
# --------------------------------------------------------------------------- #

MANIFEST: dict[str, object] = {
    # Nine-patch surfaces. Margins for storybook_theme.tres, in final pixels:
    #   panel/panel_dark 32, button_* 16, bar_* 8, slider_track 5, page_frame 40
    "panel": panel,
    "panel_dark": panel_dark,
    "button_normal": lambda: button("normal"),
    "button_hover": lambda: button("hover"),
    "button_pressed": lambda: button("pressed"),
    "button_disabled": lambda: button("disabled"),
    "bar_trough": bar_trough,
    "bar_fill_hp": lambda: bar_fill(RED, 223),
    "bar_fill_patience": lambda: bar_fill(GOLD, 224),
    "bar_fill_music": lambda: bar_fill(GREEN, 225),
    "slider_track": slider_track,
    "slider_fill": lambda: slider_track(filled=True),
    "slider_grabber": slider_grabber,
    "page_frame": page_frame,
    # Icons.
    "icon_heart_full": lambda: heart(True),
    "icon_heart_empty": lambda: heart(False),
    "icon_kratib": kratib,
    "icon_stone": stone,
    "icon_music_on": lambda: note(False),
    "icon_music_off": lambda: note(True),
    "icon_sound_on": lambda: speaker(False),
    "icon_sound_off": lambda: speaker(True),
    "icon_save": bookmark,
    "icon_pause": pause_icon,
    "icon_back": quill,
    "icon_arrow_left": lambda: chevron("left"),
    "icon_arrow_right": lambda: chevron("right"),
    "icon_arrow_up": lambda: chevron("up"),
    "icon_throw": throw_icon,
    "check_on": lambda: check(True),
    "check_off": lambda: check(False),
}


def main() -> None:
    wanted = sys.argv[1:] or list(MANIFEST)
    for name in wanted:
        fn = MANIFEST.get(name)
        if fn is None:
            print(f"  !! no such asset: {name}")
            continue
        save(fn(), name)
    print("done")


if __name__ == "__main__":
    main()
