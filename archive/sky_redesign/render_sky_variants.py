"""Render docs/sky_redesign/round_N.png — ranked sky finalists × 5 phases.

Layout: one row per ranked sky variant × 5 phase columns (day / sunrise /
sunset / dusk / night — the project's canonical review phases). Each cell
builds a full 360×640 tile = candidate sky painted onto the band, THEN the
existing world (clouds + mountains + ground) composited on top, so each sky
is judged in real in-game context rather than bare.

Run from anywhere::

    python archive/sky_redesign/render_sky_variants.py
"""
from __future__ import annotations

import math
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
from game import biome as _biome
from game.draw import draw_mountains, draw_cloud, draw_ground

import sky_variants as sv

OUT = _REPO / "docs" / "sky_redesign"
OUT.mkdir(parents=True, exist_ok=True)


# Canonical project review phases (exact labels/values are the convention).
PHASES = [
    ("day", 0.02),
    ("sunrise", 0.906),
    ("sunset", 0.363),
    ("dusk", 0.513),
    ("night", 0.644),
]

# Shared scroll so every cell composites the same world layout — only the
# sky and palette change across the grid, which is what's under review.
SCROLL = 760.0


def render_cell(variant_id: int, phase: float) -> pygame.Surface:
    palette = _biome.palette_for_phase(phase)
    surf = pygame.Surface((W, H))

    # The candidate paints the FULL opaque sky band itself.
    sv.VARIANTS[variant_id](surf, W, H, GROUND_Y, palette, phase)

    # Composite the existing world on top so the sky reads in context. The
    # cloud scatter mirrors tools/biome_snapshots.py so the judgement holds
    # against real frames.
    cloud_phase = 1.5
    for i, (bx, by, sc, variant) in enumerate((
            (20, 90, 0.9, 0), (180, 140, 1.1, 2),
            (60, 220, 0.8, 3), (230, 60, 0.7, 1),
            (320, 180, 0.9, 4))):
        ox = ((bx - SCROLL * (0.04 + 0.02 * i)) % (W + 160)) - 80
        draw_cloud(surf, ox, by + math.sin(cloud_phase * 0.3 + i) * 3,
                   sc, variant=variant)

    draw_mountains(surf, SCROLL, GROUND_Y, W,
                   palette['mtn_far'], palette['mtn_near'])
    draw_ground(surf, GROUND_Y, W, H, SCROLL,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    return surf


def make_sheet() -> pygame.Surface:
    rows = sv.ROUND3_ORDER  # 2 finalists, ranked: winner #1 then fallback #4
    n_rows = len(rows)
    tw, th = W, H
    label_h = 34
    row_label_w = 250
    pad = 10
    sheet_w = row_label_w + pad + len(PHASES) * (tw + pad)
    sheet_h = label_h + pad + n_rows * (th + pad)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 18, 22))

    font_small = pygame.font.SysFont(None, 18)
    font_mid = pygame.font.SysFont(None, 22)
    font_head = pygame.font.SysFont(None, 28)

    title = font_head.render(
        "SKY REDESIGN — ROUND 3 — FINAL · winner #1 + fallback #4 × 5 phases",
        True, (240, 240, 240))
    sheet.blit(title, (row_label_w + pad, 7))

    for c, (plabel, _p) in enumerate(PHASES):
        x = row_label_w + pad + c * (tw + pad)
        lbl = font_mid.render(plabel, True, (250, 230, 180))
        sheet.blit(lbl, (x + 8, label_h - 22))

    for r, vid in enumerate(rows):
        y = label_h + pad + r * (th + pad)
        name = sv.VARIANT_NAMES[vid]
        note = sv.VARIANT_NOTES[vid]

        idx_lbl = font_head.render(f"#{vid}", True, (255, 220, 130))
        sheet.blit(idx_lbl, (8, y + 6))

        # Wrap the name.
        ly = y + 40
        line = ""
        for word in name.split():
            test = (line + " " + word).strip()
            if font_mid.size(test)[0] > row_label_w - 16 and line:
                sheet.blit(font_mid.render(line, True, (235, 235, 235)), (8, ly))
                ly += 20
                line = word
            else:
                line = test
        if line:
            sheet.blit(font_mid.render(line, True, (235, 235, 235)), (8, ly))
            ly += 26

        # Wrap the note.
        nline = ""
        for word in note.split():
            test = (nline + " " + word).strip()
            if font_small.size(test)[0] > row_label_w - 16 and nline:
                sheet.blit(font_small.render(nline, True, (170, 180, 200)), (8, ly))
                ly += 16
                nline = word
            else:
                nline = test
        if nline:
            sheet.blit(font_small.render(nline, True, (170, 180, 200)), (8, ly))

        for c, (plabel, phase) in enumerate(PHASES):
            x = row_label_w + pad + c * (tw + pad)
            tile = render_cell(vid, phase)
            sheet.blit(tile, (x, y))
            tagtxt = font_small.render(
                f"{plabel} · phase {phase:.2f}", True, (250, 250, 250))
            bg = pygame.Surface(
                (tagtxt.get_width() + 8, tagtxt.get_height() + 4),
                pygame.SRCALPHA)
            bg.fill((0, 0, 0, 150))
            sheet.blit(bg, (x + 4, y + 4))
            sheet.blit(tagtxt, (x + 8, y + 6))

    return sheet


def main() -> None:
    sheet = make_sheet()
    out = OUT / "round_3.png"
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
