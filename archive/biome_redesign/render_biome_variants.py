"""Render docs/biome_redesign/<round>.png — biome candidates × 10 day-stages.

Rows = biome designs, columns = the 10 time-of-day stages. Each cell is a full
360x640 scene (sky + ridges + signature structure + ground + foliage) painted by
the shared scene_engine, then downscaled for the sheet so 10x10 stays viewable.

Run from anywhere::

    python archive/biome_redesign/render_biome_variants.py [round_tag] [rows]

  rows = "A" | "B" | "all" (default all currently-registered biomes)
"""
from __future__ import annotations

import os
import pathlib
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_HERE = pathlib.Path(__file__).parent
_REPO = _HERE.parent.parent
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_HERE))

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H, GROUND_Y

import scene_engine as se
import biome_variants as bv

OUT = _REPO / "docs" / "biome_redesign"
OUT.mkdir(parents=True, exist_ok=True)

# Sheet geometry — native draw, downscaled tiles so a 10x10 grid is viewable.
TILE_SCALE = 0.60
TW, TH = int(W * TILE_SCALE), int(H * TILE_SCALE)
GUT = 168          # left gutter for biome name + note
PAD = 8
HEAD = 30          # top strip for stage column labels
SECTION_H = 30     # full-width group-header band


# Set by main(): when True, tiles show ONLY the biome's sky/background color
# field (no ridges/structures/ground/foliage/atmosphere/stars).
SKY_ONLY = False


def render_cell(biome_id: str, phase: float) -> pygame.Surface:
    surf = pygame.Surface((W, H))
    spec = bv.BIOMES[biome_id]
    if SKY_ONLY:
        se.paint_sky(surf, spec, W, H, phase)
    else:
        se.paint_scene(surf, spec, W, H, GROUND_Y, phase)
    return pygame.transform.smoothscale(surf, (TW, TH))


def _wrap(font, text, maxw):
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if font.size(trial)[0] > maxw and cur:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def make_sheet(rows, title):
    n = len(rows)
    cols = len(bv.STAGES)
    # group section header appears if both groups present
    has_sections = any(r in bv.GROUP_A for r in rows) and any(r in bv.GROUP_B for r in rows)
    n_sections = 2 if has_sections else (1 if rows else 0)

    sheet_w = GUT + PAD + cols * (TW + PAD)
    sheet_h = HEAD + PAD + n * (TH + PAD) + n_sections * SECTION_H
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 18, 22))

    f_head = pygame.font.SysFont("dejavusans", 17, bold=True)
    f_name = pygame.font.SysFont("dejavusans", 14, bold=True)
    f_note = pygame.font.SysFont("dejavusans", 10)
    f_tag = pygame.font.SysFont("dejavusans", 10)
    f_sec = pygame.font.SysFont("dejavusans", 15, bold=True)

    t = f_head.render(title, True, (240, 240, 245))
    sheet.blit(t, (GUT + PAD, 6))

    for c, (label, _ph) in enumerate(bv.STAGES):
        x = GUT + PAD + c * (TW + PAD)
        lbl = f_name.render(label, True, (250, 230, 180))
        sheet.blit(lbl, (x + (TW - lbl.get_width()) // 2, HEAD - 16))

    y = HEAD + PAD
    last_group = None
    for biome_id in rows:
        group = "A — DISTINCT ENVIRONMENTS" if biome_id in bv.GROUP_A else "B — INK / SHAN-SHUI LINEAGE"
        if has_sections and group != last_group:
            band = pygame.Surface((sheet_w, SECTION_H))
            band.fill((34, 34, 42))
            sheet.blit(band, (0, y))
            s = f_sec.render(f"GROUP {group}", True, (255, 220, 140))
            sheet.blit(s, (GUT + PAD, y + 6))
            y += SECTION_H
            last_group = group

        name = bv.BIOME_NAMES[biome_id]
        note = bv.BIOME_NOTES[biome_id]
        nm = f_name.render(name, True, (245, 245, 250))
        sheet.blit(nm, (8, y + 6))
        for li, line in enumerate(_wrap(f_note, note, GUT - 14)):
            ln = f_note.render(line, True, (150, 150, 160))
            sheet.blit(ln, (8, y + 26 + li * 12))

        for c, (label, phase) in enumerate(bv.STAGES):
            x = GUT + PAD + c * (TW + PAD)
            sheet.blit(render_cell(biome_id, phase), (x, y))
            tag = f_tag.render(f"{label}", True, (245, 245, 245))
            bg = pygame.Surface((tag.get_width() + 6, tag.get_height() + 2), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 140))
            sheet.blit(bg, (x + 3, y + 3))
            sheet.blit(tag, (x + 6, y + 4))
        y += TH + PAD

    return sheet


def main():
    global SKY_ONLY
    tag = sys.argv[1] if len(sys.argv) > 1 else "round_0"
    which = sys.argv[2] if len(sys.argv) > 2 else "all"
    # Sky-only mode: triggered by a "sky" token in the round tag or a 3rd arg.
    SKY_ONLY = "sky" in tag.lower() or (len(sys.argv) > 3 and sys.argv[3] == "sky")
    if which == "A":
        rows = bv.GROUP_A
    elif which == "B":
        rows = bv.GROUP_B
    else:
        rows = bv.GROUP_A + bv.GROUP_B
    title = f"BIOME REDESIGN — {tag} — {len(rows)} designs x {len(bv.STAGES)} stages"
    sheet = make_sheet(rows, title)
    out = OUT / f"{tag}.png"
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()}, {len(rows)} rows)")


if __name__ == "__main__":
    main()
