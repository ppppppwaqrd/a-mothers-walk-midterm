"""Paint watercolour ground tilesheets so the terrain matches the painted skies.

Row 0 holds surface tiles (soil capped with vegetation under an ink contour) and
row 1 holds the plain soil body, four interchangeable variants of each. Every
tile comes from a torus-periodic field, so tiles butt against each other in any
arrangement without a seam.

Output: Assets/Generated/Tiles/tiles_level_0N.png (896x448, 14x7 cells of 64px)

Usage: python scripts/build_storybook_tiles.py [level ...]
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "Assets" / "Generated" / "Tiles"

TILE = 64
COLS, ROWS = 14, 7

# A single 64px tile repeated across a whole level reads as a grid, because the
# eye locks onto its speck pattern. Four variants of each tile, scattered by
# retop_tilemaps.py, break that up. They live at (3..6, 0) and (3..6, 1).
VARIANTS = 4
FIRST_COL = 3

# Per level: soil body, its shadow, vegetation, vegetation shadow, ink, and the
# lighter mineral flecks. "turf" is how deep the vegetation band bites into the
# cell and "stones" how gravelly the soil is, so a rocky ridge and a paddy bank
# come out of the same painter looking like different ground.
THEMES = {
    1: {
        "soil": (150, 112, 76),
        "soil_deep": (108, 78, 52),
        "veg": (104, 132, 76),
        "veg_deep": (62, 88, 50),
        "ink": (58, 44, 32),
        "grit": (172, 142, 106),
        "turf": 20.0,
        "stones": 7,
    },
    2: {
        "soil": (120, 98, 70),
        "soil_deep": (84, 66, 46),
        "veg": (86, 116, 66),
        "veg_deep": (50, 76, 44),
        "ink": (40, 48, 32),
        "grit": (142, 120, 88),
        "turf": 22.0,
        "stones": 6,
    },
    3: {
        "soil": (116, 104, 94),
        "soil_deep": (78, 70, 64),
        "veg": (134, 120, 88),
        "veg_deep": (90, 78, 54),
        "ink": (56, 52, 46),
        "grit": (148, 136, 124),
        "turf": 12.0,
        "stones": 13,
    },
    4: {
        "soil": (156, 118, 76),
        "soil_deep": (114, 82, 52),
        "veg": (136, 148, 80),
        "veg_deep": (92, 106, 54),
        "ink": (60, 48, 30),
        "grit": (178, 148, 106),
        "turf": 19.0,
        "stones": 7,
    },
    5: {
        "soil": (68, 66, 82),
        "soil_deep": (42, 40, 54),
        "veg": (48, 66, 68),
        "veg_deep": (28, 42, 46),
        "ink": (18, 20, 28),
        "grit": (92, 90, 104),
        "turf": 18.0,
        "stones": 9,
    },
    6: {
        "soil": (124, 90, 68),
        "soil_deep": (88, 62, 46),
        "veg": (146, 116, 70),
        "veg_deep": (98, 74, 46),
        "ink": (44, 32, 26),
        "grit": (152, 116, 88),
        "turf": 17.0,
        "stones": 8,
    },
}


def noise_torus(size: int, cells: int, seed: int, octaves: int = 4) -> np.ndarray:
    """Smooth noise in [0,1] that wraps on both axes."""
    total = np.zeros((size, size))
    amp_sum = 0.0
    for o in range(octaves):
        c = max(2, cells * 2**o)
        amp = 0.5**o
        rng = np.random.default_rng(seed + o * 911)
        vals = rng.random((c, c))
        t = np.linspace(0, c, size, endpoint=False)
        idx = np.floor(t).astype(int) % c
        frac = t - np.floor(t)
        frac = frac * frac * (3 - 2 * frac)
        iy, ix = idx[:, None], idx[None, :]
        fy, fx = frac[:, None], frac[None, :]
        v00 = vals[iy, ix]
        v01 = vals[iy, (ix + 1) % c]
        v10 = vals[(iy + 1) % c, ix]
        v11 = vals[(iy + 1) % c, (ix + 1) % c]
        top = v00 * (1 - fx) + v01 * fx
        bot = v10 * (1 - fx) + v11 * fx
        total += amp * (top * (1 - fy) + bot * fy)
        amp_sum += amp
    return total / amp_sum


def noise_ring(size: int, cells: int, seed: int, octaves: int = 3) -> np.ndarray:
    """1D noise in [0,1] wrapping across `size`."""
    total = np.zeros(size)
    amp_sum = 0.0
    for o in range(octaves):
        c = max(2, cells * 2**o)
        amp = 0.5**o
        rng = np.random.default_rng(seed + o * 337)
        vals = rng.random(c)
        t = np.linspace(0, c, size, endpoint=False)
        i = np.floor(t).astype(int) % c
        f = t - np.floor(t)
        f = f * f * (3 - 2 * f)
        total += amp * (vals[i] * (1 - f) + vals[(i + 1) % c] * f)
        amp_sum += amp
    return total / amp_sum


class WrapMask:
    """64x64 draw target that repeats shapes across all four edges."""

    def __init__(self, size: int = TILE):
        self.size = size
        self.img = Image.new("L", (size, size), 0)
        self.draw = ImageDraw.Draw(self.img)

    def _offsets(self):
        s = self.size
        return [(dx, dy) for dx in (-s, 0, s) for dy in (-s, 0, s)]

    def ellipse(self, cx: float, cy: float, rx: float, ry: float) -> None:
        for dx, dy in self._offsets():
            self.draw.ellipse([cx - rx + dx, cy - ry + dy, cx + rx + dx, cy + ry + dy], fill=255)

    def line(self, pts, width: int = 2) -> None:
        for dx, dy in self._offsets():
            self.draw.line([(x + dx, y + dy) for x, y in pts], fill=255, width=width, joint="curve")

    def blade(self, x: float, base_y: float, height: float, lean: float) -> None:
        """A tapered leaf: wide at the root, a single hair at the tip."""
        steps = 5
        for i in range(steps):
            t0, t1 = i / steps, (i + 1) / steps
            w = max(1, int(round(3.4 * (1.0 - t0))))
            self.line(
                [
                    (x + lean * t0 * t0, base_y - height * t0),
                    (x + lean * t1 * t1, base_y - height * t1),
                ],
                width=w,
            )

    def array(self) -> np.ndarray:
        return np.asarray(self.img, dtype=np.float64) / 255.0


def blur_torus(arr: np.ndarray, sigma: float) -> np.ndarray:
    return ndimage.gaussian_filter(arr, sigma, mode="wrap")


def granulate(size: int, cells: int, seed: int) -> np.ndarray:
    """Pigment settling: blotches in [0,1] with dark rims, as wet paint dries."""
    field = noise_torus(size, cells, seed, octaves=3)
    # Edge darkening is where the field changes fastest, i.e. its gradient.
    gy, gx = np.gradient(np.pad(field, 1, mode="wrap"))
    edge = np.hypot(gy, gx)[1:-1, 1:-1]
    edge /= max(edge.max(), 1e-6)
    pool = np.clip((field - 0.45) * 2.2, 0.0, 1.0) ** 1.4
    return np.clip(0.62 * pool + 0.38 * edge**0.7, 0.0, 1.0)


def soil_tile(theme: dict, seed: int) -> np.ndarray:
    """Opaque RGBA soil that tiles in both directions.

    Built like a wet-on-wet wash: a flat ground colour, two blotch layers of
    different grain, then stones drawn on top with their own ink rim. Nothing
    varies over the height of the cell, because the soil repeats downward and
    any vertical gradient would band at every tile join.
    """
    base = np.array(theme["soil"], dtype=np.float64) / 255.0
    deep = np.array(theme["soil_deep"], dtype=np.float64) / 255.0
    grit = np.array(theme["grit"], dtype=np.float64) / 255.0
    ink = np.array(theme["ink"], dtype=np.float64) / 255.0

    # Only high-frequency detail: the same 64px tile repeats across the whole
    # level, so any large-scale feature turns into a visible grid.
    broad = granulate(TILE, 6, seed + 51)
    fine = granulate(TILE, 13, seed + 77)
    rgb = base[None, None, :] + (deep - base)[None, None, :] * (0.72 * broad)[:, :, None]
    # A second pass of lighter pigment keeps the wash from reading as one flat
    # ramp between two colours.
    lift = np.clip((fine - 0.55) * 1.8, 0.0, 1.0)
    rgb += (grit - base)[None, None, :] * (0.26 * lift)[:, :, None]

    # Stones read from their own shading, not from an outline: a pale crown and
    # a cast shadow just under it. Ringing every pebble in ink turns the soil
    # into a field of little circles.
    stones = WrapMask()
    rng = np.random.default_rng(seed + 7)
    for _ in range(int(theme["stones"])):
        cx, cy = rng.uniform(0, TILE), rng.uniform(0, TILE)
        r = rng.uniform(2.0, 4.4)
        stones.ellipse(cx, cy, r, r * rng.uniform(0.5, 0.85))
    stone_m = stones.array()
    body = blur_torus(stone_m, 0.9)
    cast = np.clip(np.roll(stone_m, 2, axis=0) - stone_m, 0.0, 1.0)
    cast = blur_torus(cast, 0.9) * 0.42
    rgb = rgb * (1 - cast[:, :, None]) + deep[None, None, :] * cast[:, :, None]
    rgb = rgb * (1 - 0.34 * body[:, :, None]) + grit[None, None, :] * 0.34 * body[:, :, None]
    crown = np.clip(np.roll(stone_m, 1, axis=0) * stone_m - blur_torus(stone_m, 1.6), 0.0, 1.0)
    rgb += crown[:, :, None] * 0.10

    # Dry-brush drags: the tooth of the paper catching pigment.
    drag = noise_torus(TILE, 30, seed + 83, octaves=1)
    rgb *= (1.0 + 0.10 * (drag - 0.5) * 2.0)[:, :, None]
    paper = 1.0 + 0.07 * (noise_torus(TILE, 21, seed + 91, octaves=2) - 0.5) * 2.0
    rgb *= paper[:, :, None]
    return np.dstack([np.clip(rgb, 0, 1), np.ones((TILE, TILE))])


def surface_tile(soil: np.ndarray, theme: dict, seed: int) -> np.ndarray:
    """Soil capped with vegetation and contoured with an ink line along the top.

    The tile stays fully opaque and the turf reaches row 0. The collision box is
    the whole cell, so any transparent margin at the top would leave the player
    standing on empty air; the organic look comes from the wavy grass/soil
    boundary and the root fringe below it instead of from a ragged silhouette.
    """
    veg = np.array(theme["veg"], dtype=np.float64) / 255.0
    veg_deep = np.array(theme["veg_deep"], dtype=np.float64) / 255.0
    ink = np.array(theme["ink"], dtype=np.float64) / 255.0
    yy = np.arange(TILE)[:, None]
    rng = np.random.default_rng(seed + 5)

    turf = float(theme["turf"])
    # Big lazy clumps, not an even hem: three humps across the cell.
    turf_bottom = turf * (0.70 + 0.55 * noise_ring(TILE, 3, seed + 23))
    mat = np.clip((turf_bottom[None, :] - yy) / 2.4 + 0.5, 0.0, 1.0)

    # Leaf tips drooping out of the mat, so the turf meets the soil as a fringe
    # rather than a cut line.
    tufts = WrapMask()
    for _ in range(24):
        bx = rng.uniform(0, TILE)
        base_y = float(turf_bottom[int(bx) % TILE]) + rng.uniform(2.0, 6.5)
        tufts.blade(bx, base_y, rng.uniform(3.0, 7.0), rng.uniform(-3.0, 3.0))
    fringe = np.clip(blur_torus(tufts.array(), 0.6) * 1.3, 0.0, 1.0)

    out = soil.copy()
    soil_shadow = np.clip(1.0 - np.abs(yy - turf_bottom[None, :] - 4.0) / 12.0, 0.0, 1.0)
    out[:, :, :3] *= (1.0 - 0.30 * soil_shadow)[:, :, None]

    veg_mask = np.clip(mat + fringe, 0.0, 1.0)
    # Sun on the crowns, shade at the roots.
    lit = np.clip(np.broadcast_to(yy, (TILE, TILE)) / (turf + 6.0), 0.0, 1.0) ** 0.75
    veg_rgb = veg[None, None, :] * (1 - lit[:, :, None]) + veg_deep[None, None, :] * lit[:, :, None]
    veg_rgb *= (1.0 - 0.24 * granulate(TILE, 9, seed + 61))[:, :, None]
    # Blades are vertical, so their tone varies column by column, in clumps
    # rather than as an even comb, and it fades out toward the roots.
    clump = noise_ring(TILE, 7, seed + 71, octaves=2)[None, :]
    hair = noise_ring(TILE, 26, seed + 73, octaves=1)[None, :]
    depth = np.clip(1.0 - yy / max(turf, 1.0), 0.0, 1.0)
    veg_rgb *= (1.0 + (0.15 * (clump - 0.5) + 0.07 * (hair - 0.5)) * 2.0 * depth)[:, :, None]
    # Darker leaves woven through the band give it depth without new geometry.
    dark = WrapMask()
    for _ in range(14):
        bx = rng.uniform(0, TILE)
        dark.blade(bx, float(turf_bottom[int(bx) % TILE]), rng.uniform(5.0, turf * 0.9), rng.uniform(-3.0, 3.0))
    shade = blur_torus(dark.array(), 0.7) * 0.34
    veg_rgb = veg_rgb * (1 - shade[:, :, None]) + veg_deep[None, None, :] * shade[:, :, None]
    out[:, :, :3] = out[:, :, :3] * (1 - veg_mask[:, :, None]) + veg_rgb * veg_mask[:, :, None]

    # Ink contour hugging the top of the ground mass, weight varying like a brush.
    weight = 1.7 + 1.2 * noise_ring(TILE, 5, seed + 11)
    contour = np.clip((weight[None, :] - yy) / 1.3 + 0.5, 0.0, 1.0)
    ink_a = contour * (0.40 + 0.32 * noise_ring(TILE, 8, seed + 13))[None, :]
    out[:, :, :3] = out[:, :, :3] * (1 - ink_a[:, :, None]) + ink[None, None, :] * ink_a[:, :, None]

    out[:, :, 3] = 1.0
    return out


def build(level: int) -> None:
    theme = THEMES[level]
    sheet = np.zeros((ROWS * TILE, COLS * TILE, 4))
    for v in range(VARIANTS):
        seed = level * 1301 + v * 197
        soil = soil_tile(theme, seed)
        surface = surface_tile(soil, theme, seed)
        col = FIRST_COL + v
        sheet[0:TILE, col * TILE : (col + 1) * TILE, :] = surface
        sheet[TILE : 2 * TILE, col * TILE : (col + 1) * TILE, :] = soil

    arr = np.clip(sheet, 0, 1)
    img = Image.fromarray((arr * 255.0).round().astype(np.uint8), "RGBA")
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"tiles_level_{level:02d}.png"
    img.save(path, optimize=True)
    print(f"  tiles_level_{level:02d}.png  {img.size[0]}x{img.size[1]}  {path.stat().st_size / 1024:.0f} KB")


def main() -> None:
    levels = [int(a) for a in sys.argv[1:]] or sorted(THEMES)
    for lv in levels:
        build(lv)
    print("done")


if __name__ == "__main__":
    main()
