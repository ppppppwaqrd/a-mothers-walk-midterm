"""Paint the storybook parallax backgrounds for all six levels.

Every layer is drawn from scratch as a watercolour wash on paper: soft shapes,
pigment darkening where the wash dried against an edge, a jittered ink outline
and paper grain on top.

Shapes write into named channels of a `Scene` (trunk, leaf, roof, body, ...) so
each part gets its own colour instead of one flat silhouette, and each layer is
composited in an explicit back-to-front order.

All scrolling layers are horizontally tileable, so `level_background.gd` can wrap
them with a modulo and never run out of image no matter how long a level is.

Every scrolling layer ends with a SKIRT-deep pad, so its ground line — the line
that gets aligned with the level's ground tiles — is always `height - SKIRT`.

Output (per level NN = 01..06) in Assets/Generated/BG/:
    sky_NN.png   1920x720   opaque, pinned to the screen
    far_NN.png   1920x960   alpha, tileable, scroll 0.10
    mid_NN.png   1920x1040  alpha, tileable, scroll 0.28
    near_NN.png  1920x780   alpha, tileable, scroll 0.60

Usage: python scripts/build_storybook_bgs.py [level ...]
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "Assets" / "Generated" / "BG"

W = 1920
SKY_H = 720
FAR_H = 540
MID_H = 620
NEAR_H = 360

INK = (58, 42, 30)


# --------------------------------------------------------------------------- #
# Noise
# --------------------------------------------------------------------------- #


def noise_1d(width: int, cells: int, seed: int, octaves: int = 4) -> np.ndarray:
    """Periodic smooth noise in [0,1]; wraps exactly across `width`."""
    total = np.zeros(width)
    amp_sum = 0.0
    for o in range(octaves):
        c = max(2, cells * 2**o)
        amp = 0.5**o
        rng = np.random.default_rng(seed + o * 977)
        vals = rng.random(c)
        x = np.linspace(0, c, width, endpoint=False)
        i = np.floor(x).astype(int) % c
        f = x - np.floor(x)
        f = f * f * (3 - 2 * f)
        total += amp * (vals[i] * (1 - f) + vals[(i + 1) % c] * f)
        amp_sum += amp
    return total / amp_sum


def noise_2d(w: int, h: int, cells_x: int, cells_y: int, seed: int, octaves: int = 4) -> np.ndarray:
    """Smooth noise in [0,1], periodic along x only (y does not need to wrap)."""
    total = np.zeros((h, w))
    amp_sum = 0.0
    for o in range(octaves):
        cx = max(2, cells_x * 2**o)
        cy = max(2, cells_y * 2**o)
        amp = 0.5**o
        rng = np.random.default_rng(seed + o * 613)
        vals = rng.random((cy + 1, cx))
        xs = np.linspace(0, cx, w, endpoint=False)
        ys = np.linspace(0, cy, h, endpoint=False)
        ix = np.floor(xs).astype(int) % cx
        fx = xs - np.floor(xs)
        fx = fx * fx * (3 - 2 * fx)
        iy = np.floor(ys).astype(int)
        fy = ys - np.floor(ys)
        fy = fy * fy * (3 - 2 * fy)
        v00 = vals[np.ix_(iy, ix)]
        v01 = vals[np.ix_(iy, (ix + 1) % cx)]
        v10 = vals[np.ix_(iy + 1, ix)]
        v11 = vals[np.ix_(iy + 1, (ix + 1) % cx)]
        top = v00 * (1 - fx)[None, :] + v01 * fx[None, :]
        bot = v10 * (1 - fx)[None, :] + v11 * fx[None, :]
        total += amp * (top * (1 - fy)[:, None] + bot * fy[:, None])
        amp_sum += amp
    return total / amp_sum


# --------------------------------------------------------------------------- #
# Drawing targets
# --------------------------------------------------------------------------- #


def gblur(arr: np.ndarray, sigma: float) -> np.ndarray:
    """Gaussian blur that wraps along x so tileable layers keep no seam."""
    return ndimage.gaussian_filter(arr, sigma, mode=("reflect", "wrap"))


def erode(mask: np.ndarray, iterations: int) -> np.ndarray:
    """Binary erosion with the x axis treated as periodic."""
    pad = max(1, iterations + 1)
    wide = np.concatenate([mask[:, -pad:], mask, mask[:, :pad]], axis=1)
    out = ndimage.binary_erosion(wide, iterations=iterations)
    return out[:, pad:-pad]


class Mask:
    """Draw target that repeats every shape across the left/right seam."""

    def __init__(self, w: int, h: int):
        self.w, self.h = w, h
        self.img = Image.new("L", (w, h), 0)
        self.draw = ImageDraw.Draw(self.img)

    def polygon(self, pts: list[tuple[float, float]], value: int = 255) -> None:
        for dx in (-self.w, 0, self.w):
            self.draw.polygon([(x + dx, y) for x, y in pts], fill=value)

    def ellipse(self, box: tuple[float, float, float, float], value: int = 255) -> None:
        x0, y0, x1, y1 = box
        for dx in (-self.w, 0, self.w):
            self.draw.ellipse([x0 + dx, y0, x1 + dx, y1], fill=value)

    def line(self, pts: list[tuple[float, float]], width: int = 3, value: int = 255) -> None:
        for dx in (-self.w, 0, self.w):
            self.draw.line([(x + dx, y) for x, y in pts], fill=value, width=width, joint="curve")

    def array(self) -> np.ndarray:
        return np.asarray(self.img, dtype=np.float64) / 255.0


class Scene:
    """A set of named mask channels for one parallax layer."""

    def __init__(self, w: int, h: int):
        self.w, self.h = w, h
        self._channels: dict[str, Mask] = {}

    def ch(self, name: str) -> Mask:
        if name not in self._channels:
            self._channels[name] = Mask(self.w, self.h)
        return self._channels[name]

    def get(self, name: str) -> np.ndarray | None:
        m = self._channels.get(name)
        return None if m is None else m.array()


# --------------------------------------------------------------------------- #
# Terrain masks
# --------------------------------------------------------------------------- #


def ridge_mask(w: int, h: int, base_y: float, amp: float, cells: int, seed: int, sharp: float = 1.0) -> np.ndarray:
    """Fill everything below a noisy horizon line."""
    prof = noise_1d(w, cells, seed)
    if sharp != 1.0:
        prof = prof**sharp
    horizon = base_y - amp * prof
    yy = np.arange(h)[:, None]
    return np.clip((yy - horizon[None, :]) / 2.0 + 0.5, 0.0, 1.0)


def hills_mask(w: int, h: int, base_y: float, amp: float, cells: int, seed: int, humps: int = 6) -> np.ndarray:
    """Rounded overlapping hills: noise alone reads as a flat band, so mix in
    smooth humps to give the silhouette a legible shape."""
    xs = np.arange(w)
    prof = noise_1d(w, cells, seed)
    phase = noise_1d(w, 3, seed + 61) * 2 * np.pi
    hump = 0.5 + 0.5 * np.sin(2 * np.pi * xs / w * humps + phase)
    prof = 0.45 * prof + 0.55 * hump**1.35
    horizon = base_y - amp * prof
    yy = np.arange(h)[:, None]
    return np.clip((yy - horizon[None, :]) / 2.0 + 0.5, 0.0, 1.0)


def peaks_mask(w: int, h: int, base_y: float, count: int, height: float, seed: int) -> np.ndarray:
    """Triangular mountain peaks with a jittered profile."""
    rng = np.random.default_rng(seed)
    horizon = np.full(w, base_y)
    xs = np.arange(w)
    for k in range(count):
        cx = (k + rng.uniform(0.2, 0.8)) * w / count
        half = rng.uniform(0.10, 0.20) * w
        pk = base_y - height * rng.uniform(0.6, 1.0)
        d = np.abs(((xs - cx + w / 2) % w) - w / 2)
        tri = np.clip(1.0 - d / half, 0.0, 1.0) ** 1.25
        horizon = np.minimum(horizon, base_y - (base_y - pk) * tri)
    horizon += (noise_1d(w, 26, seed + 5) - 0.5) * 14.0
    yy = np.arange(h)[:, None]
    return np.clip((yy - horizon[None, :]) / 2.0 + 0.5, 0.0, 1.0)


# --------------------------------------------------------------------------- #
# Objects
# --------------------------------------------------------------------------- #


def blob(m: Mask, cx: float, cy: float, rx: float, ry: float, seed: int, lobes: int = 11) -> None:
    """Irregular soft blob used for canopies, clouds and rocks."""
    rng = np.random.default_rng(seed)
    pts = []
    for i in range(lobes * 3):
        a = 2 * np.pi * i / (lobes * 3)
        wob = 0.72 + 0.42 * rng.random()
        pts.append((cx + np.cos(a) * rx * wob, cy + np.sin(a) * ry * wob))
    m.polygon(pts)


def curved_blade(
    m: Mask,
    p0: tuple[float, float],
    ctrl: tuple[float, float],
    p1: tuple[float, float],
    max_w: float,
    seed: int,
    steps: int = 16,
) -> None:
    """Tapered leaf along a quadratic curve: zero width at base and tip."""
    rng = np.random.default_rng(seed)
    left: list[tuple[float, float]] = []
    right: list[tuple[float, float]] = []
    for i in range(steps + 1):
        t = i / steps
        u = 1.0 - t
        x = u * u * p0[0] + 2 * u * t * ctrl[0] + t * t * p1[0]
        y = u * u * p0[1] + 2 * u * t * ctrl[1] + t * t * p1[1]
        dx = 2 * u * (ctrl[0] - p0[0]) + 2 * t * (p1[0] - ctrl[0])
        dy = 2 * u * (ctrl[1] - p0[1]) + 2 * t * (p1[1] - ctrl[1])
        norm = np.hypot(dx, dy) + 1e-6
        nx, ny = -dy / norm, dx / norm
        wide = max_w * np.sin(np.pi * t) ** 0.55 * (0.86 + 0.28 * rng.random())
        left.append((x + nx * wide, y + ny * wide))
        right.append((x - nx * wide, y - ny * wide))
    m.polygon(left + right[::-1])


def tree(s: Scene, x: float, ground: float, scale: float, seed: int) -> None:
    """Broad-leaf tree: thick trunk under a wide multi-lobed canopy."""
    rng = np.random.default_rng(seed)
    trunk, leaf = s.ch("trunk"), s.ch("leaf")
    trunk_h = 58 * scale
    trunk.polygon(
        [
            (x - 8 * scale, ground),
            (x + 8 * scale, ground),
            (x + 4 * scale, ground - trunk_h),
            (x - 4 * scale, ground - trunk_h),
        ]
    )
    for side in (-1, 1):
        trunk.line([(x, ground - trunk_h * 0.65), (x + side * 20 * scale, ground - trunk_h * 1.1)], width=max(2, int(4 * scale)))
    crown_y = ground - trunk_h - 28 * scale
    crown_r = 64 * scale
    for k in range(5):
        a = 2 * np.pi * k / 5 + rng.uniform(-0.3, 0.3)
        blob(
            leaf,
            x + np.cos(a) * crown_r * 0.46,
            crown_y + np.sin(a) * crown_r * 0.26,
            crown_r * rng.uniform(0.50, 0.68),
            crown_r * rng.uniform(0.34, 0.48),
            seed + k * 31,
            lobes=9,
        )
    blob(leaf, x, crown_y, crown_r * 0.64, crown_r * 0.44, seed + 199, lobes=13)


def tree_line(s: Scene, ground: float, count: int, scale: float, seed: int, y_jitter: float = 26.0) -> None:
    """A continuous mass of canopies: reads as distant forest, not lollipops."""
    rng = np.random.default_rng(seed)
    trunk, leaf = s.ch("trunk"), s.ch("leaf")
    for k in range(count):
        x = (k + rng.uniform(-0.35, 0.35)) * W / count
        gy = ground - rng.uniform(0, y_jitter)
        r = rng.uniform(48, 86) * scale
        blob(leaf, x, gy - r * 0.58, r, r * rng.uniform(0.46, 0.64), seed + k * 53, lobes=11)
        trunk.polygon([(x - 5 * scale, gy + 8), (x + 5 * scale, gy + 8), (x + 3 * scale, gy - r * 0.4), (x - 3 * scale, gy - r * 0.4)])


def palm(s: Scene, x: float, ground: float, scale: float, seed: int) -> None:
    """Coconut palm: leaning trunk crowned with heavy drooping fronds."""
    rng = np.random.default_rng(seed)
    trunk, leaf = s.ch("trunk"), s.ch("leaf")
    top = ground - 132 * scale
    lean = rng.uniform(-18, 18) * scale
    tip_x = x + lean
    trunk.line([(x, ground), (x + lean * 0.35, ground - 70 * scale), (tip_x, top)], width=max(4, int(10 * scale)))
    crown = (tip_x, top - 4 * scale)
    for k in range(7):
        spread = -1.0 + 2.0 * k / 6.0
        spread += rng.uniform(-0.09, 0.09)
        reach = 74 * scale * (0.72 + 0.42 * (1.0 - abs(spread)))
        end = (tip_x + spread * reach, top + (10 + 44 * abs(spread)) * scale + rng.uniform(0, 12) * scale)
        ctrl = (tip_x + spread * reach * 0.55, top - (30 - 14 * abs(spread)) * scale)
        curved_blade(leaf, crown, ctrl, end, 11 * scale, seed + k * 37)
    leaf.ellipse([tip_x - 9 * scale, top - 10 * scale, tip_x + 9 * scale, top + 8 * scale])


def bamboo(s: Scene, x: float, ground: float, height: float, scale: float, seed: int) -> None:
    """Single culm: segmented stalk with a spray of long leaves near the top."""
    rng = np.random.default_rng(seed)
    stalk, leaf = s.ch("trunk"), s.ch("leaf")
    lean = rng.uniform(-16, 16)
    top = ground - height
    stalk.line([(x, ground), (x + lean * 0.5, ground - height * 0.5), (x + lean, top)], width=max(3, int(7 * scale)))
    nodes = max(3, int(height / (52 * scale)))
    for k in range(1, nodes):
        t = k / nodes
        ny = ground - height * t
        nx = x + lean * t
        stalk.line([(nx - 5 * scale, ny), (nx + 5 * scale, ny)], width=max(2, int(3 * scale)))
    for k in range(7):
        t = rng.uniform(0.62, 1.0)
        ly = ground - height * t
        lx = x + lean * t
        side = 1 if k % 2 else -1
        reach = rng.uniform(34, 62) * scale
        end = (lx + side * reach, ly + rng.uniform(14, 38) * scale)
        ctrl = (lx + side * reach * 0.55, ly - rng.uniform(6, 20) * scale)
        curved_blade(leaf, (lx, ly), ctrl, end, 5.0 * scale, seed + k * 29, steps=10)


def bamboo_clump(s: Scene, x: float, ground: float, height: float, scale: float, seed: int, culms: int = 3) -> None:
    """Bamboo grows in clumps, so plant a few culms of mixed height together."""
    rng = np.random.default_rng(seed)
    for k in range(culms):
        bamboo(
            s,
            x + rng.uniform(-26, 26) * scale,
            ground + rng.uniform(-4, 4) * scale,
            height * rng.uniform(0.72, 1.12),
            scale * rng.uniform(0.88, 1.08),
            seed + k * 101,
        )


def stilt_house(s: Scene, x: float, ground: float, scale: float, seed: int) -> None:
    """Isan stilt house: posts, plank wall, wide thatch roof."""
    rng = np.random.default_rng(seed)
    post, body, roof = s.ch("trunk"), s.ch("body"), s.ch("roof")
    bw = 82 * scale
    bh = 54 * scale
    floor = ground - 30 * scale
    for off in (-bw / 2 + 7 * scale, 0.0, bw / 2 - 7 * scale):
        post.polygon([(x + off - 4 * scale, ground), (x + off + 4 * scale, ground), (x + off + 4 * scale, floor), (x + off - 4 * scale, floor)])
    body.polygon([(x - bw / 2, floor), (x + bw / 2, floor), (x + bw / 2, floor - bh), (x - bw / 2, floor - bh)])
    over_hang = 16 * scale
    ridge_y = floor - bh - 44 * scale + rng.uniform(-4, 4) * scale
    roof.polygon([(x - bw / 2 - over_hang, floor - bh + 4 * scale), (x + bw / 2 + over_hang, floor - bh + 4 * scale), (x, ridge_y)])


def hut(s: Scene, x: float, ground: float, scale: float, seed: int) -> None:
    body, roof = s.ch("body"), s.ch("roof")
    bw = 70 * scale
    bh = 42 * scale
    body.polygon([(x - bw / 2, ground), (x + bw / 2, ground), (x + bw / 2, ground - bh), (x - bw / 2, ground - bh)])
    roof.polygon([(x - bw / 2 - 14 * scale, ground - bh + 3 * scale), (x + bw / 2 + 14 * scale, ground - bh + 3 * scale), (x, ground - bh - 48 * scale)])


def rock(m: Mask, cx: float, ground: float, w_: float, h_: float, seed: int) -> None:
    """Rounded boulder: a couple of overlapping humps, not a spiky ridge."""
    rng = np.random.default_rng(seed)
    humps = [(rng.uniform(0.26, 0.44), rng.uniform(0.82, 1.0)), (rng.uniform(0.56, 0.78), rng.uniform(0.52, 0.86))]
    pts = [(cx - w_ / 2, ground)]
    steps = 22
    for i in range(steps + 1):
        t = i / steps
        val = max(a * np.exp(-((t - c) ** 2) / 0.075) for c, a in humps)
        val = min(1.0, val) * np.sin(np.pi * t) ** 0.28
        pts.append((cx - w_ / 2 + w_ * t, ground - h_ * val))
    pts.append((cx + w_ / 2, ground))
    m.polygon(pts)


def grass_tuft(m: Mask, x: float, ground: float, scale: float, seed: int, blades: int = 6) -> None:
    rng = np.random.default_rng(seed)
    for _ in range(blades):
        bx = x + rng.uniform(-16, 16) * scale
        h_ = rng.uniform(28, 62) * scale
        bend = rng.uniform(-20, 20) * scale
        m.line([(bx, ground), (bx + bend * 0.4, ground - h_ * 0.6), (bx + bend, ground - h_)], width=max(2, int(3.5 * scale)))


def reed(s: Scene, x: float, ground: float, scale: float, seed: int) -> None:
    rng = np.random.default_rng(seed)
    stalk, head = s.ch("leaf"), s.ch("body")
    h_ = rng.uniform(95, 175) * scale
    bend = rng.uniform(-26, 26) * scale
    tip = (x + bend, ground - h_)
    stalk.line([(x, ground), (x + bend * 0.35, ground - h_ * 0.55), tip], width=max(2, int(4 * scale)))
    head.ellipse([tip[0] - 5.5 * scale, tip[1] - 24 * scale, tip[0] + 5.5 * scale, tip[1] + 6 * scale])


def rice_stalk(s: Scene, x: float, ground: float, scale: float, seed: int) -> None:
    """Rice plant: upright stalk, two blade leaves, and a heavy drooping ear."""
    rng = np.random.default_rng(seed)
    stalk, grain = s.ch("leaf"), s.ch("body")
    h_ = rng.uniform(78, 128) * scale
    side = 1 if rng.random() > 0.5 else -1
    lean = rng.uniform(4, 16) * scale * side
    tip = (x + lean, ground - h_)
    stalk.line([(x, ground), (x + lean * 0.4, ground - h_ * 0.6), tip], width=max(2, int(3.2 * scale)))
    for k in range(2):
        ly = ground - h_ * rng.uniform(0.32, 0.62)
        sgn = side if k == 0 else -side
        curved_blade(
            stalk,
            (x + lean * 0.3, ly),
            (x + sgn * 14 * scale, ly - 11 * scale),
            (x + sgn * 24 * scale, ly + 8 * scale),
            2.8 * scale,
            seed + 11 * k,
            steps=10,
        )
    droop = rng.uniform(26, 42) * scale
    ear_end = (tip[0] + side * droop, tip[1] + droop * 0.72)
    ear_ctrl = (tip[0] + side * droop * 0.5, tip[1] - 10 * scale)
    curved_blade(grain, tip, ear_ctrl, ear_end, 5.2 * scale, seed + 71, steps=12)
    for k in range(4):
        t = 0.25 + 0.22 * k
        u = 1.0 - t
        gx = u * u * tip[0] + 2 * u * t * ear_ctrl[0] + t * t * ear_end[0]
        gy = u * u * tip[1] + 2 * u * t * ear_ctrl[1] + t * t * ear_end[1]
        r = 3.4 * scale
        grain.ellipse([gx - r, gy - r, gx + r, gy + r])


def dead_tree(s: Scene, x: float, ground: float, scale: float, seed: int) -> None:
    rng = np.random.default_rng(seed)
    m = s.ch("trunk")
    top = ground - 150 * scale
    m.line([(x, ground), (x + rng.uniform(-8, 8) * scale, ground - 80 * scale), (x, top)], width=max(3, int(8 * scale)))
    for k in range(5):
        t = rng.uniform(0.45, 0.95)
        by = ground - (ground - top) * t
        side = -1 if k % 2 else 1
        m.line([(x, by), (x + side * 34 * scale, by - 26 * scale), (x + side * 58 * scale, by - 60 * scale)], width=max(2, int(4 * scale)))


# --------------------------------------------------------------------------- #
# Watercolour rendering
# --------------------------------------------------------------------------- #


def paper_grain(w: int, h: int, seed: int, strength: float = 0.055) -> np.ndarray:
    fibre = noise_2d(w, h, 60, 22, seed, octaves=3)
    speck = noise_2d(w, h, 220, 90, seed + 41, octaves=2)
    return 1.0 + strength * ((fibre - 0.5) * 1.2 + (speck - 0.5) * 0.8)


def wash(
    mask: np.ndarray,
    color: tuple[int, int, int],
    *,
    seed: int,
    blur: float = 1.6,
    edge: float = 0.30,
    mottle: float = 0.12,
    alpha: float = 1.0,
    wet: float = 0.0,
    wet_px: int = 14,
    fade: float = 0.0,
) -> np.ndarray:
    """Turn a mask into an RGBA watercolour wash.

    `wet` adds the darker rim real watercolour leaves where pigment dries against
    an edge; `fade` lightens the wash downward so big masses recede instead of
    reading as flat stickers.
    """
    h, w = mask.shape
    m = gblur(mask, blur)
    smooth = gblur(m, 4.0)
    gy, gx = np.gradient(smooth)
    grad = np.hypot(gx, gy)
    grad /= grad.max() + 1e-9
    shade = 1.0 - edge * np.clip(grad * 3.2, 0.0, 1.0)

    if wet > 0.0:
        solid = mask > 0.4
        rim = solid & ~erode(solid, max(1, wet_px))
        shade = shade * (1.0 - wet * gblur(rim.astype(np.float64), 2.5))

    if fade > 0.0:
        shade = shade * (1.0 + fade * (np.arange(h) / max(1, h - 1))[:, None])

    mottle_map = 1.0 + mottle * (noise_2d(w, h, 14, 7, seed + 7, octaves=3) - 0.5) * 2.0
    base = np.array(color, dtype=np.float64) / 255.0
    rgb = base[None, None, :] * (shade * mottle_map)[:, :, None]
    rgb *= paper_grain(w, h, seed + 3, 0.05)[:, :, None]
    a = np.clip(m * alpha, 0.0, 1.0)
    a = a * (0.94 + 0.06 * np.clip(smooth, 0, 1))
    return np.dstack([np.clip(rgb, 0, 1), a])


def ink_outline(mask: np.ndarray, *, seed: int, width: float = 2.0, alpha: float = 0.55, color=INK) -> np.ndarray:
    """Jittered ink line hugging a shape, like a dip pen run over dry paper."""
    solid = mask > 0.5
    inner = erode(solid, max(1, int(round(width))))
    line = (solid & ~inner).astype(np.float64)
    h, w = mask.shape
    breakup = noise_2d(w, h, 90, 40, seed + 19, octaves=2)
    line *= np.clip((breakup - 0.28) * 3.0, 0.0, 1.0)
    line = gblur(line, 0.7)
    rgb = np.array(color, dtype=np.float64) / 255.0
    flat = np.broadcast_to(rgb[None, None, :], (h, w, 3)).copy()
    return np.dstack([flat, np.clip(line * alpha, 0, 1)])


def over(base: np.ndarray, top: np.ndarray) -> np.ndarray:
    """Standard source-over compositing on float RGBA."""
    ta = top[:, :, 3:4]
    ba = base[:, :, 3:4]
    out_a = ta + ba * (1 - ta)
    safe = np.where(out_a > 1e-6, out_a, 1.0)
    out_rgb = (top[:, :, :3] * ta + base[:, :, :3] * ba * (1 - ta)) / safe
    return np.dstack([out_rgb, out_a])


def blank(w: int, h: int) -> np.ndarray:
    return np.zeros((h, w, 4))


def haze(layer: np.ndarray, sky_color: tuple[int, int, int], amount: float) -> np.ndarray:
    """Atmospheric perspective: blend a layer toward the sky colour."""
    sky = np.array(sky_color, dtype=np.float64) / 255.0
    rgb = layer[:, :, :3] * (1 - amount) + sky[None, None, :] * amount
    return np.dstack([rgb, layer[:, :, 3]])


def paint(
    layer: np.ndarray,
    scene: Scene,
    order: list[tuple[str, tuple[int, int, int]]],
    *,
    seed: int,
    ink_channels: tuple[str, ...] = (),
    ink_alpha: float = 0.45,
    ink_color=INK,
    wet: float = 0.24,
    wet_px: int = 8,
    alpha: float = 0.96,
) -> np.ndarray:
    """Composite named scene channels back-to-front, then ink the solid parts."""
    inked = np.zeros((scene.h, scene.w))
    for i, (name, color) in enumerate(order):
        mask = scene.get(name)
        if mask is None:
            continue
        layer = over(layer, wash(mask, color, seed=seed + i * 17, blur=1.5, edge=0.28, alpha=alpha, wet=wet, wet_px=wet_px))
        if name in ink_channels:
            inked = np.maximum(inked, mask)
    if inked.any():
        layer = over(layer, ink_outline(inked, seed=seed, width=2.0, alpha=ink_alpha, color=ink_color))
    return layer


def ground_plane(layer: np.ndarray, top: float, seed: int, fall: float = 0.30) -> np.ndarray:
    """Break the flat wash under a hill line into ground that recedes.

    A silhouette filled to the bottom of its layer leaves a slab of one colour,
    which reads as a painted wall rather than as distance. Real ground steps
    away from the viewer in bands and loses light as it goes, so tone it that
    way: soft terraces, a drift across the width, and a slow fall into shadow.
    """
    h, w, _ = layer.shape
    depth = np.clip((np.arange(h) - top) / max(h - top, 1.0), 0.0, 1.0)[:, None]

    terrace = noise_1d(h, 5, seed + 31, octaves=2)[:, None]
    mottle = noise_2d(w, h, 5, 3, seed + 37, octaves=3)
    shade = (1.0 + 0.14 * (terrace - 0.5) * 2.0 * depth) * (1.0 - fall * depth**1.25)
    shade = shade * (1.0 + 0.07 * (mottle - 0.5) * 2.0 * depth)

    out = layer.copy()
    out[:, :, :3] *= shade[:, :, None]
    return np.clip(out, 0.0, 1.0)


def add_skirt(layer: np.ndarray, px: int) -> np.ndarray:
    """Pad a layer downward so its ground line sits `px` above its bottom edge.

    Every scrolling layer carries the same size skirt, which is how
    `level_background.gd` locates the ground line without knowing how tall the
    layer's content is: it is always `texture_height - SKIRT`.

    The skirt repeats the bottom row and fades it toward shadow, so a pit in the
    terrain shows depth rather than a hard cut.
    """
    tail = np.repeat(layer[-1:, :, :], px, axis=0)
    tail[:, :, :3] *= np.linspace(1.0, 0.34, px)[:, None, None] ** 1.4
    return np.concatenate([layer, tail], axis=0)


def place_fringe(layer: np.ndarray, rise: int, skirt: int) -> np.ndarray:
    """Skirt the near layer and slide its plants to a fixed height above ground.

    Plant species differ wildly in height — reeds stand three times as tall as a
    grass tuft — so anchoring every level's fringe by its baseline would let some
    levels grow a wall across the play area. Aligning by the top of the tallest
    plant instead gives every level the same silhouette height, and the bases
    slide down into the skirt where the terrain hides them.
    """
    h, w, _ = layer.shape
    out = np.zeros((h + skirt, w, 4))
    rows = np.nonzero(layer[:, :, 3].max(axis=1) > 0.04)[0]
    top = int(rows[0]) if rows.size else h
    shift = max(0, (h - rise) - top)
    keep = min(h, out.shape[0] - shift)
    out[shift : shift + keep] = layer[:keep]
    return out


def save(layer: np.ndarray, name: str, opaque: bool = False) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rgb = np.clip(layer[:, :, :3], 0, 1)
    a = np.clip(layer[:, :, 3], 0, 1)
    # Posterise a touch so large flat washes compress well in PNG.
    rgb = np.round(rgb * 255.0 / 3.0) * 3.0
    a = np.round(a * 255.0 / 5.0) * 5.0
    arr = np.dstack([rgb, a]).astype(np.uint8)
    img = Image.fromarray(arr, "RGBA")
    if opaque:
        img = img.convert("RGB")
    path = OUT / name
    img.save(path, optimize=True)
    print(f"  {name}  {img.size[0]}x{img.size[1]}  {path.stat().st_size / 1024:.0f} KB")


# --------------------------------------------------------------------------- #
# Sky painting
# --------------------------------------------------------------------------- #


def gradient_sky(stops: list[tuple[float, tuple[int, int, int]]], seed: int) -> np.ndarray:
    ys = np.linspace(0.0, 1.0, SKY_H)
    rgb = np.zeros((SKY_H, 3))
    for c in range(3):
        rgb[:, c] = np.interp(ys, [s[0] for s in stops], [s[1][c] / 255.0 for s in stops])
    sky = np.repeat(rgb[:, None, :], W, axis=1)
    drift = noise_2d(W, SKY_H, 6, 4, seed, octaves=3)
    sky *= (0.965 + 0.07 * drift)[:, :, None]
    sky *= paper_grain(W, SKY_H, seed + 2, 0.045)[:, :, None]
    return np.dstack([np.clip(sky, 0, 1), np.ones((SKY_H, W))])


def add_disc(sky: np.ndarray, cx: float, cy: float, r: float, color, glow_color, glow_r: float) -> np.ndarray:
    yy, xx = np.mgrid[0:SKY_H, 0:W]
    d = np.hypot(xx - cx, yy - cy)
    glow = np.clip(1.0 - d / glow_r, 0.0, 1.0) ** 2.2
    g = np.array(glow_color, dtype=np.float64) / 255.0
    rgb = sky[:, :, :3] * (1 - glow[:, :, None] * 0.8) + g[None, None, :] * glow[:, :, None] * 0.8
    disc = np.clip((r - d) / 2.5 + 0.5, 0.0, 1.0)
    c = np.array(color, dtype=np.float64) / 255.0
    rgb = rgb * (1 - disc[:, :, None]) + c[None, None, :] * disc[:, :, None]
    return np.dstack([np.clip(rgb, 0, 1), sky[:, :, 3]])


def add_clouds(sky: np.ndarray, color, count: int, seed: int, y_lo: float, y_hi: float, scale: float, alpha: float) -> np.ndarray:
    m = Mask(W, SKY_H)
    rng = np.random.default_rng(seed)
    for k in range(count):
        cx = rng.uniform(0, W)
        cy = rng.uniform(y_lo, y_hi)
        rx = rng.uniform(90, 190) * scale
        ry = rx * rng.uniform(0.22, 0.36)
        for j in range(4):
            blob(
                m,
                cx + rng.uniform(-rx * 0.5, rx * 0.5),
                cy + rng.uniform(-ry * 0.4, ry * 0.4),
                rx * rng.uniform(0.4, 0.7),
                ry * rng.uniform(0.7, 1.2),
                seed + k * 17 + j,
            )
    cloud = gblur(m.array(), 7.0)
    return over(sky, wash(cloud, color, seed=seed + 3, blur=5.0, edge=0.10, mottle=0.16, alpha=alpha))


def add_dots(sky: np.ndarray, color, count: int, seed: int, y_lo: float, y_hi: float, r_lo: float, r_hi: float, alpha: float) -> np.ndarray:
    m = Mask(W, SKY_H)
    rng = np.random.default_rng(seed)
    for _ in range(count):
        cx, cy = rng.uniform(0, W), rng.uniform(y_lo, y_hi)
        r = rng.uniform(r_lo, r_hi)
        m.ellipse([cx - r, cy - r, cx + r, cy + r])
    dots = gblur(m.array(), 1.0)
    return over(sky, wash(dots, color, seed=seed + 5, blur=1.0, edge=0.0, mottle=0.0, alpha=alpha))


def add_birds(sky: np.ndarray, color, count: int, seed: int, y_lo: float, y_hi: float, alpha: float = 0.7) -> np.ndarray:
    m = Mask(W, SKY_H)
    rng = np.random.default_rng(seed)
    for _ in range(count):
        bx, by = rng.uniform(0, W), rng.uniform(y_lo, y_hi)
        s = rng.uniform(7, 13)
        m.line([(bx - s, by), (bx, by - s * 0.6), (bx + s, by - s * 0.05)], width=2)
    return over(sky, wash(m.array(), color, seed=seed + 8, blur=0.8, edge=0.0, mottle=0.0, alpha=alpha))


def add_light_shafts(sky: np.ndarray, color, seed: int, count: int = 7, alpha: float = 0.16) -> np.ndarray:
    m = Mask(W, SKY_H)
    rng = np.random.default_rng(seed)
    for _ in range(count):
        x0 = rng.uniform(0, W)
        wide = rng.uniform(40, 110)
        skew = rng.uniform(90, 240)
        m.polygon([(x0, -20), (x0 + wide, -20), (x0 + skew + wide * 1.6, SKY_H + 20), (x0 + skew, SKY_H + 20)])
    shaft = gblur(m.array(), 16.0)
    fade = np.clip(1.0 - np.arange(SKY_H) / (SKY_H * 0.9), 0, 1)[:, None]
    return over(sky, wash(shaft * fade, color, seed=seed + 9, blur=10.0, edge=0.0, mottle=0.0, alpha=alpha))


# --------------------------------------------------------------------------- #
# Per-level palettes
# --------------------------------------------------------------------------- #

SKY_TINT = {
    1: (206, 220, 208),
    2: (217, 228, 168),
    3: (204, 227, 238),
    4: (226, 210, 180),
    5: (58, 62, 96),
    6: (176, 118, 88),
}


def sky_for(level: int) -> np.ndarray:
    """Paint a sky for a high horizon.

    The mid layer's ground plane covers everything below roughly a third of the
    viewport, so the gradient's horizon and every sun, cloud and bird has to live
    in the top third or the player never sees it.
    """
    if level == 1:
        s = gradient_sky(
            [(0.0, (236, 210, 194)), (0.16, (246, 222, 198)), (0.28, (251, 234, 208)), (0.34, (206, 220, 208)), (1.0, (192, 212, 202))],
            101,
        )
        s = add_disc(s, W * 0.50, SKY_H * 0.23, 58, (255, 246, 220), (255, 228, 182), 330)
        s = add_clouds(s, (255, 248, 236), 8, 102, SKY_H * 0.04, SKY_H * 0.20, 1.0, 0.55)
        s = add_clouds(s, (234, 218, 208), 4, 103, SKY_H * 0.24, SKY_H * 0.32, 1.4, 0.32)
        return add_birds(s, (96, 84, 70), 9, 104, SKY_H * 0.08, SKY_H * 0.26, 0.45)
    if level == 2:
        s = gradient_sky([(0.0, (176, 200, 140)), (0.18, (204, 222, 158)), (0.30, (234, 240, 198)), (0.36, (226, 232, 180)), (1.0, (218, 226, 168))], 201)
        s = add_light_shafts(s, (255, 253, 226), 202, count=8, alpha=0.22)
        return add_clouds(s, (248, 250, 230), 5, 203, SKY_H * 0.03, SKY_H * 0.18, 0.95, 0.38)
    if level == 3:
        s = gradient_sky([(0.0, (150, 196, 224)), (0.18, (186, 216, 234)), (0.30, (216, 232, 240)), (1.0, (226, 236, 238))], 301)
        s = add_disc(s, W * 0.36, SKY_H * 0.11, 44, (255, 253, 238), (255, 250, 222), 240)
        s = add_clouds(s, (255, 255, 255), 6, 302, SKY_H * 0.10, SKY_H * 0.28, 0.85, 0.62)
        return add_birds(s, (108, 118, 128), 6, 303, SKY_H * 0.14, SKY_H * 0.28, 0.35)
    if level == 4:
        s = gradient_sky([(0.0, (128, 176, 210)), (0.14, (186, 212, 228)), (0.24, (238, 216, 168)), (0.32, (238, 192, 104)), (1.0, (232, 184, 75))], 401)
        s = add_disc(s, W * 0.26, SKY_H * 0.23, 52, (255, 248, 212), (255, 216, 146), 300)
        s = add_clouds(s, (255, 246, 226), 8, 402, SKY_H * 0.04, SKY_H * 0.20, 1.1, 0.6)
        s = add_clouds(s, (240, 198, 152), 4, 403, SKY_H * 0.24, SKY_H * 0.31, 1.4, 0.34)
        return add_birds(s, (110, 88, 68), 11, 404, SKY_H * 0.08, SKY_H * 0.26, 0.5)
    if level == 5:
        s = gradient_sky([(0.0, (26, 34, 68)), (0.16, (40, 52, 86)), (0.28, (74, 66, 104)), (0.34, (100, 80, 114)), (1.0, (107, 84, 118))], 501)
        s = add_dots(s, (240, 240, 226), 170, 502, 0, SKY_H * 0.28, 1.0, 2.2, 0.75)
        s = add_disc(s, W * 0.74, SKY_H * 0.12, 46, (246, 242, 214), (176, 178, 206), 260)
        return add_clouds(s, (72, 70, 106), 5, 503, SKY_H * 0.18, SKY_H * 0.31, 1.3, 0.45)
    s = gradient_sky([(0.0, (52, 52, 86)), (0.14, (96, 78, 102)), (0.24, (172, 108, 80)), (0.31, (204, 112, 62)), (1.0, (206, 110, 58))], 601)
    s = add_disc(s, W * 0.58, SKY_H * 0.26, 66, (255, 228, 172), (242, 164, 96), 340)
    s = add_dots(s, (238, 232, 216), 60, 602, 0, SKY_H * 0.14, 1.0, 1.8, 0.5)
    s = add_clouds(s, (242, 204, 164), 7, 603, SKY_H * 0.16, SKY_H * 0.30, 1.2, 0.5)
    return add_birds(s, (48, 38, 44), 13, 604, SKY_H * 0.08, SKY_H * 0.24, 0.75)


# --------------------------------------------------------------------------- #
# Far layer
# --------------------------------------------------------------------------- #


def far_for(level: int) -> np.ndarray:
    h = FAR_H
    layer = blank(W, h)
    ground = h - 6
    s = Scene(W, h)
    rng = np.random.default_rng(level * 700 + 3)

    if level == 1:
        back = hills_mask(W, h, ground - 210, 150, 4, 110, humps=5)
        layer = over(layer, wash(back, (150, 180, 166), seed=110, blur=3.4, edge=0.18, alpha=0.9, wet=0.26, wet_px=18, fade=0.30))
        front = hills_mask(W, h, ground - 120, 120, 6, 111, humps=8)
        layer = over(layer, wash(front, (144, 178, 158), seed=111, blur=3.0, edge=0.20, alpha=0.95, wet=0.32, wet_px=16, fade=0.26))
        tree_line(s, ground - 84, 22, 0.74, 112, y_jitter=34)
        layer = paint(layer, s, [("trunk", (108, 92, 78)), ("leaf", (126, 158, 132))], seed=112, ink_channels=(), wet=0.20, alpha=0.9)
        return haze(layer, SKY_TINT[1], 0.18)

    if level == 2:
        mass = hills_mask(W, h, ground - 150, 170, 5, 211, humps=6)
        layer = over(layer, wash(mass, (136, 172, 108), seed=211, blur=4.0, edge=0.18, alpha=0.93, wet=0.14, wet_px=18, fade=0.28))
        for _ in range(9):
            bamboo_clump(s, rng.uniform(0, W), ground - 60, rng.uniform(200, 300), 0.6, int(rng.integers(0, 9999)), culms=3)
        layer = paint(layer, s, [("trunk", (128, 156, 96)), ("leaf", (116, 152, 88))], seed=212, wet=0.14, alpha=0.68)
        return haze(layer, SKY_TINT[2], 0.20)

    if level == 3:
        peaks = peaks_mask(W, h, ground - 70, 5, 300, 311)
        layer = over(layer, wash(peaks, (130, 150, 178), seed=311, blur=3.0, edge=0.26, alpha=0.96, wet=0.34, wet_px=18, fade=0.34))
        layer = over(layer, ink_outline(peaks, seed=311, width=2.0, alpha=0.24, color=(84, 94, 116)))
        peaks2 = peaks_mask(W, h, ground - 16, 7, 180, 312)
        layer = over(layer, wash(peaks2, (158, 172, 192), seed=312, blur=2.6, edge=0.22, alpha=0.93, wet=0.26, wet_px=14, fade=0.24))
        return haze(layer, SKY_TINT[3], 0.22)

    if level == 4:
        back = hills_mask(W, h, ground - 190, 120, 4, 410, humps=5)
        layer = over(layer, wash(back, (142, 164, 134), seed=410, blur=3.4, edge=0.16, alpha=0.88, wet=0.24, wet_px=18, fade=0.28))
        hills = hills_mask(W, h, ground - 118, 100, 6, 411, humps=7)
        layer = over(layer, wash(hills, (136, 158, 120), seed=411, blur=3.0, edge=0.18, alpha=0.94, wet=0.30, wet_px=16, fade=0.26))
        tree_line(s, ground - 64, 20, 0.84, 412, y_jitter=40)
        layer = paint(layer, s, [("trunk", (104, 88, 68)), ("leaf", (118, 142, 104))], seed=412, wet=0.20, alpha=0.92)
        return haze(layer, SKY_TINT[4], 0.16)

    if level == 5:
        hills = hills_mask(W, h, ground - 140, 130, 5, 511, humps=6)
        layer = over(layer, wash(hills, (38, 46, 76), seed=511, blur=3.4, edge=0.14, alpha=0.96, wet=0.22, wet_px=16, fade=0.18))
        tree_line(s, ground - 74, 18, 0.92, 512, y_jitter=44)
        layer = paint(layer, s, [("trunk", (24, 28, 48)), ("leaf", (28, 34, 58))], seed=512, wet=0.12, alpha=0.95)
        return haze(layer, SKY_TINT[5], 0.16)

    hills = hills_mask(W, h, ground - 134, 118, 5, 611, humps=6)
    layer = over(layer, wash(hills, (84, 66, 86), seed=611, blur=3.2, edge=0.16, alpha=0.95, wet=0.24, wet_px=16, fade=0.20))
    tree_line(s, ground - 68, 17, 0.88, 612, y_jitter=40)
    layer = paint(layer, s, [("trunk", (54, 42, 56)), ("leaf", (62, 48, 68))], seed=612, wet=0.14, alpha=0.93)
    return haze(layer, SKY_TINT[6], 0.18)


# --------------------------------------------------------------------------- #
# Mid layer
# --------------------------------------------------------------------------- #


def mid_for(level: int) -> np.ndarray:
    h = MID_H
    layer = blank(W, h)
    ground = h - 8
    s = Scene(W, h)
    rng = np.random.default_rng(level * 1000 + 7)

    if level == 1:
        bank = hills_mask(W, h, ground - 150, 90, 7, 121, humps=9)
        layer = over(layer, wash(bank, (122, 150, 96), seed=121, blur=2.4, edge=0.24, alpha=0.96, wet=0.34, wet_px=16, fade=0.30))
        base = ground - 120
        for x in (150, 520, 980, 1450, 1780):
            stilt_house(s, x + rng.uniform(-40, 40), base - rng.uniform(0, 26), 1.2, int(rng.integers(0, 9999)))
        for _ in range(9):
            tree(s, rng.uniform(0, W), base - rng.uniform(0, 30), 1.05, int(rng.integers(0, 9999)))
        for _ in range(6):
            palm(s, rng.uniform(0, W), base - rng.uniform(0, 26), 1.0, int(rng.integers(0, 9999)))
        layer = paint(
            layer,
            s,
            [("trunk", (118, 92, 64)), ("leaf", (96, 138, 90)), ("body", (176, 148, 108)), ("roof", (128, 96, 66))],
            seed=122,
            ink_channels=("body", "roof", "trunk"),
            ink_alpha=0.5,
        )
        return haze(layer, SKY_TINT[1], 0.07)

    if level == 2:
        for _ in range(11):
            bamboo_clump(s, rng.uniform(0, W), ground - 90, rng.uniform(300, 400), 0.95, int(rng.integers(0, 9999)), culms=3)
        layer = paint(
            layer,
            s,
            [("trunk", (154, 172, 100)), ("leaf", (86, 128, 66))],
            seed=221,
            ink_channels=("trunk",),
            ink_alpha=0.30,
            ink_color=(48, 64, 38),
        )
        floor = hills_mask(W, h, ground - 90, 56, 8, 222, humps=9)
        layer = over(layer, wash(floor, (78, 110, 58), seed=222, blur=2.0, edge=0.24, alpha=0.96, wet=0.30, wet_px=14, fade=0.24))
        return haze(layer, SKY_TINT[2], 0.06)

    if level == 3:
        stones = s.ch("body")
        for _ in range(10):
            rock(stones, rng.uniform(0, W), ground - 70 - rng.uniform(0, 24), rng.uniform(150, 320), rng.uniform(80, 150), int(rng.integers(0, 9999)))
        dry = s.ch("leaf")
        for _ in range(18):
            grass_tuft(dry, rng.uniform(0, W), ground - 76 - rng.uniform(0, 14), 0.95, int(rng.integers(0, 9999)), blades=4)
        layer = paint(
            layer,
            s,
            [("body", (158, 134, 112)), ("leaf", (146, 126, 84))],
            seed=321,
            ink_channels=("body",),
            ink_alpha=0.44,
            ink_color=(74, 59, 47),
            wet=0.34,
            wet_px=14,
        )
        floor = hills_mask(W, h, ground - 84, 54, 8, 322, humps=7)
        layer = over(layer, wash(floor, (150, 128, 100), seed=322, blur=2.2, edge=0.22, alpha=0.96, wet=0.30, wet_px=12, fade=0.22))
        return haze(layer, SKY_TINT[3], 0.05)

    if level == 4:
        for k, (y_off, col) in enumerate([(250, (134, 164, 88)), (176, (152, 178, 88)), (104, (174, 190, 84))]):
            band = ridge_mask(W, h, ground - y_off, 28, 10, 421 + k)
            layer = over(layer, wash(band, col, seed=421 + k, blur=2.2, edge=0.22, alpha=0.96, wet=0.30, wet_px=12, fade=0.22))
        base = ground - 210
        for _ in range(8):
            palm(s, rng.uniform(0, W), base - rng.uniform(0, 40), 1.05, int(rng.integers(0, 9999)))
        hut(s, 1320, base - 10, 1.2, 4242)
        layer = paint(
            layer,
            s,
            [("trunk", (112, 88, 60)), ("leaf", (104, 140, 82)), ("body", (188, 158, 112)), ("roof", (134, 100, 66))],
            seed=424,
            ink_channels=("body", "roof", "trunk"),
            ink_alpha=0.46,
        )
        return haze(layer, SKY_TINT[4], 0.06)

    if level == 5:
        water = ridge_mask(W, h, ground - 170, 30, 12, 521)
        layer = over(layer, wash(water, (34, 46, 84), seed=521, blur=3.0, edge=0.12, alpha=0.92, wet=0.20, wet_px=12, fade=0.24))
        for _ in range(9):
            dead_tree(s, rng.uniform(0, W), ground - 150 - rng.uniform(0, 40), 1.2, int(rng.integers(0, 9999)))
        layer = paint(
            layer,
            s,
            [("trunk", (20, 24, 44))],
            seed=522,
            ink_channels=("trunk",),
            ink_alpha=0.3,
            ink_color=(10, 12, 26),
            wet=0.12,
        )
        bank = ridge_mask(W, h, ground - 96, 56, 7, 523)
        layer = over(layer, wash(bank, (26, 36, 60), seed=523, blur=2.2, edge=0.16, alpha=0.97, wet=0.22, wet_px=14, fade=0.16))
        glow = Mask(W, h)
        for _ in range(48):
            cx, cy = rng.uniform(0, W), rng.uniform(ground - 420, ground - 120)
            r = rng.uniform(2.4, 4.6)
            glow.ellipse([cx - r, cy - r, cx + r, cy + r])
        fire = gblur(glow.array(), 3.2)
        return over(layer, wash(fire, (242, 228, 138), seed=524, blur=2.4, edge=0.0, mottle=0.0, alpha=0.85))

    for k, (y_off, col) in enumerate([(230, (96, 76, 82)), (158, (116, 88, 74)), (92, (136, 100, 68))]):
        band = ridge_mask(W, h, ground - y_off, 26, 10, 621 + k)
        layer = over(layer, wash(band, col, seed=621 + k, blur=2.2, edge=0.22, alpha=0.96, wet=0.28, wet_px=12, fade=0.20))
    base = ground - 200
    hut(s, 1520, base, 1.25, 6161)
    for _ in range(7):
        palm(s, rng.uniform(0, W), base - rng.uniform(0, 40), 1.0, int(rng.integers(0, 9999)))
    layer = paint(
        layer,
        s,
        [("trunk", (48, 38, 46)), ("leaf", (56, 44, 56)), ("body", (108, 78, 66)), ("roof", (72, 52, 52))],
        seed=624,
        ink_channels=("body", "roof", "trunk"),
        ink_alpha=0.4,
        ink_color=(24, 18, 26),
    )
    return haze(layer, SKY_TINT[6], 0.06)


# --------------------------------------------------------------------------- #
# Near layer
# --------------------------------------------------------------------------- #


def near_for(level: int) -> np.ndarray:
    """A low fringe of plants growing at the front edge of the player's ground.

    This layer is anchored just below the ground line, so anything tall here
    stands right where the player does and hides the action. The plants are kept
    short enough to read as a border rather than a screen.
    """
    h = NEAR_H
    layer = blank(W, h)
    ground = h - 2
    s = Scene(W, h)
    rng = np.random.default_rng(level * 3000 + 13)

    if level == 1:
        blades = s.ch("leaf")
        for _ in range(70):
            grass_tuft(blades, rng.uniform(0, W), ground - rng.uniform(0, 26), 1.0, int(rng.integers(0, 9999)))
        order = [("leaf", (74, 100, 56))]
        ink_c = (34, 46, 28)
    elif level == 2:
        for _ in range(8):
            bamboo_clump(s, rng.uniform(0, W), ground, rng.uniform(90, 130), 0.75, int(rng.integers(0, 9999)), culms=2)
        blades = s.ch("body")
        for _ in range(38):
            grass_tuft(blades, rng.uniform(0, W), ground - rng.uniform(0, 20), 1.1, int(rng.integers(0, 9999)))
        order = [("trunk", (108, 132, 66)), ("leaf", (48, 80, 42)), ("body", (56, 88, 48))]
        ink_c = (24, 40, 22)
    elif level == 3:
        stones = s.ch("body")
        for _ in range(26):
            rock(stones, rng.uniform(0, W), ground - rng.uniform(0, 16), rng.uniform(60, 150), rng.uniform(30, 74), int(rng.integers(0, 9999)))
        dry = s.ch("leaf")
        for _ in range(36):
            grass_tuft(dry, rng.uniform(0, W), ground - rng.uniform(0, 14), 0.9, int(rng.integers(0, 9999)), blades=4)
        order = [("body", (112, 92, 68)), ("leaf", (132, 112, 70))]
        ink_c = (56, 44, 32)
    elif level == 4:
        for _ in range(88):
            rice_stalk(s, rng.uniform(0, W), ground - rng.uniform(0, 22), 0.95, int(rng.integers(0, 9999)))
        order = [("leaf", (108, 122, 48)), ("body", (196, 168, 66))]
        ink_c = (56, 50, 24)
    elif level == 5:
        for _ in range(58):
            reed(s, rng.uniform(0, W), ground - rng.uniform(0, 22), 0.9, int(rng.integers(0, 9999)))
        order = [("leaf", (18, 24, 42)), ("body", (34, 40, 58))]
        ink_c = (8, 10, 22)
    else:
        for _ in range(62):
            rice_stalk(s, rng.uniform(0, W), ground - rng.uniform(0, 22), 0.95, int(rng.integers(0, 9999)))
        order = [("leaf", (58, 46, 52)), ("body", (132, 96, 62))]
        ink_c = (24, 18, 24)

    layer = paint(
        layer,
        s,
        order,
        seed=level * 91,
        ink_channels=tuple(name for name, _ in order),
        ink_alpha=0.4,
        ink_color=ink_c,
        wet=0.22,
        wet_px=6,
    )

    if level == 5:
        glow = Mask(W, h)
        for _ in range(26):
            cx, cy = rng.uniform(0, W), rng.uniform(ground - 240, ground - 40)
            r = rng.uniform(3.0, 5.4)
            glow.ellipse([cx - r, cy - r, cx + r, cy + r])
        fire = gblur(glow.array(), 3.6)
        layer = over(layer, wash(fire, (246, 232, 150), seed=595, blur=2.6, edge=0.0, mottle=0.0, alpha=0.9))
    return layer


# Every scrolling layer ends with a skirt of this depth, so the engine can find
# each layer's ground line without knowing the layer's content height.
SKIRT = 420

# How far the near-layer fringe rises above the ground line. The player is 64px
# tall, so this reads as a border along the front of the ground without becoming
# a screen the player disappears behind.
NEAR_RISE = 58


def build(level: int) -> None:
    print(f"level {level:02d}")
    save(sky_for(level), f"sky_{level:02d}.png", opaque=True)
    # Terrace the ground under each hill line before skirting: the far plane
    # falls off hardest because it is furthest from the light.
    far = ground_plane(far_for(level), FAR_H * 0.55, level * 91 + 1, fall=0.34)
    mid = ground_plane(mid_for(level), MID_H * 0.62, level * 91 + 2, fall=0.26)
    save(add_skirt(far, SKIRT), f"far_{level:02d}.png")
    save(add_skirt(mid, SKIRT), f"mid_{level:02d}.png")
    save(place_fringe(near_for(level), NEAR_RISE, SKIRT), f"near_{level:02d}.png")


def main() -> None:
    levels = [int(a) for a in sys.argv[1:]] or [1, 2, 3, 4, 5, 6]
    for lv in levels:
        build(lv)
    print("done")


if __name__ == "__main__":
    main()
