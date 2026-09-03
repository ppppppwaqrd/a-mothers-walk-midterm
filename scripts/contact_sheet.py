"""Tile the captured screens into one image for review.

Usage: python scripts/contact_sheet.py [name ...]      (default: every capture)
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

# The project path contains Thai and the Windows console defaults to cp1252.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SHOTS = Path(__file__).resolve().parent / "_shots"
CELL = (560, 315)
COLS = 2


def main() -> None:
    names = sys.argv[1:]
    paths = [SHOTS / f"{n}.png" for n in names] if names else sorted(SHOTS.glob("*.png"))
    paths = [p for p in paths if p.exists() and p.name != "sheet.png"]
    if not paths:
        print("no captures found; run scripts/capture.ps1 first")
        return
    rows = (len(paths) + COLS - 1) // COLS
    sheet = Image.new("RGB", (CELL[0] * COLS, CELL[1] * rows), (22, 20, 18))
    for i, path in enumerate(paths):
        frame = Image.open(path).convert("RGB").resize(CELL, Image.LANCZOS)
        sheet.paste(frame, ((i % COLS) * CELL[0], (i // COLS) * CELL[1]))
    out = SHOTS / "sheet.png"
    sheet.save(out)
    print(f"{out}  {sheet.width}x{sheet.height}  ({len(paths)} screens)")
    for path in paths:
        print(f"  {path.stem}")


if __name__ == "__main__":
    main()
