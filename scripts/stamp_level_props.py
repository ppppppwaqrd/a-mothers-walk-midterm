"""Stamp each level scene's root with its id and chapter title.

Every level scene instances base_level.tscn as its root, so the engine reports
base_level.tscn as the scene path for all of them. The explicit id is what the
background, tileset, music and save system use to tell the levels apart, and the
title is what the chapter page shows.

Titles used to be a text override on a Label node inside the HUD, which is gone
now that the chapter page owns them; this moves any it finds onto the root and
removes the leftover node.

Usage: python scripts/stamp_level_props.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Titles are Thai and the Windows console defaults to cp1252.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

LEVELS = Path(__file__).resolve().parent.parent / "Scenes" / "Levels"

ROOT_NODE = re.compile(r'\[node name="BaseLevel"[^\]]*instance=ExtResource\("1_base"\)\]\n')
OLD_LABEL = re.compile(r'\n\[node name="Label" parent="UserInterface"[^\]]*\]\ntext = "([^"]*)"\n?')
PROPS = re.compile(r'\n(?:level_id|level_title) = "[^"]*"')

# Fallbacks for any level whose title is not already in the scene.
TITLES = {
    1: "ออกจากหมู่บ้าน",
    2: "ป่าไผ่",
    3: "ทางขรุขระ",
    4: "ทุ่งนากลางทาง",
    5: "คูน้ำกลางคืน",
    6: "ส่งกล่องข้าวให้อ้ายทอง",
}


def title_of(text: str, level: int) -> tuple[str, str]:
    """Pull the title out of the old Label override, dropping the "ด่าน N — " prefix."""
    match = OLD_LABEL.search(text)
    if match is None:
        return text, TITLES[level]
    raw = match.group(1).strip()
    _, _, tail = raw.partition("—")
    return text[: match.start()] + text[match.end() :], (tail.strip() or raw)


def main() -> None:
    for level in range(1, 7):
        nn = f"{level:02d}"
        path = LEVELS / f"level_{nn}.tscn"
        text = path.read_text(encoding="utf-8")
        text, title = title_of(text, level)
        text = PROPS.sub("", text)
        match = ROOT_NODE.search(text)
        if match is None:
            print(f"  !! root node not found in level_{nn}.tscn")
            continue
        props = f'level_id = "level_{nn}"\nlevel_title = "{title}"\n'
        text = text[: match.end()] + props + text[match.end() :]
        path.write_text(text, encoding="utf-8")
        print(f"level_{nn}.tscn -> {title}")


if __name__ == "__main__":
    main()
