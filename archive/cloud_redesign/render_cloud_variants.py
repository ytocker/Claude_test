"""Render `docs/cloud_redesign/round_1.png`.

Composes one full game scene per cell (sky + V14 backdrop + ground)
and scatters 5–6 instances of the row's cloud variant across it so each
variant is judged in situ, never as a bare swatch.

Grid: 5 rows (one variant each) × 5 columns (DAY / GOLDEN / SUNSET /
DUSK / NIGHT). Each tile is 360×640 — the live game canvas.

Run from anywhere:
    python archive/cloud_redesign/render_cloud_variants.py
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
sys.path.insert(0, str(_REPO / "archive" / "mountain_redesign"))
sys.path.insert(0, str(_HERE))

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H, GROUND_Y
from game import biome as _biome
from game.draw import (
    get_sky_surface_biome,
    draw_ground,
)
import mountain_variants_alive as mv
import cloud_variants as cv


KEEPER_V14 = 14

# Phases — locked to the round brief.
PHASES = [
    ("DAY",     0.02),
    ("GOLDEN",  0.23),
    ("SUNSET",  0.36),
    ("DUSK",    0.51),
    ("NIGHT",   0.64),
]

# Cloud placement scattered across the canvas so each cell reads as a
# real sky, not a single demo blob. Different x/y/scale per slot lets
# the AD see the variant working at a range of sizes.
CLOUD_SLOTS = (
    # (x, y, scale)
    (60,  90, 0.90),
    (220, 130, 1.05),
    (140, 200, 0.80),
    (290, 250, 0.70),
    (40,  290, 0.85),
    (200, 340, 0.95),
)

# Per-row scroll for the V14 backdrop — late-game bucket so the ridge
# silhouette is visually rich behind every variant.
ROW_SCROLL = 1800.0

OUT = _REPO / "docs" / "cloud_redesign"
OUT.mkdir(parents=True, exist_ok=True)


def _scene_backdrop(phase: float, scroll: float) -> pygame.Surface:
    """Sky + V14 backdrop + ground. Clouds painted by caller on top."""
    palette = _biome.palette_for_phase(phase)
    surf = pygame.Surface((W, H))
    bucket = _biome.phase_bucket(phase)
    sky = get_sky_surface_biome(W, H, GROUND_Y, palette, bucket)
    sky.set_alpha(None)
    surf.blit(sky, (0, 0))
    mv.set_phase(phase)
    mv.VARIANTS[KEEPER_V14](surf, scroll, GROUND_Y, W,
                            palette['mtn_far'], palette['mtn_near'])
    draw_ground(surf, GROUND_Y, W, H, scroll,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    return surf


def render_cell(variant_id: int, phase: float) -> pygame.Surface:
    surf = _scene_backdrop(phase, ROW_SCROLL)
    palette = _biome.palette_for_phase(phase)
    draw_fn = cv.VARIANTS[variant_id]
    for i, (cx, cy, sc) in enumerate(CLOUD_SLOTS):
        # Subtle vertical bob keeps the demo from looking flat-tiled.
        bob = math.sin(i * 0.9) * 2
        draw_fn(surf, cx, cy + bob, palette, scale=sc)
    return surf


def make_sheet() -> pygame.Surface:
    tw, th = W, H
    label_h = 32
    row_label_w = 240
    pad = 10
    sheet_w = row_label_w + pad + len(PHASES) * (tw + pad)
    sheet_h = label_h + pad + len(cv.VARIANTS) * (th + pad)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 18, 22))

    font_small = pygame.font.SysFont(None, 18)
    font_mid = pygame.font.SysFont(None, 22)
    font_head = pygame.font.SysFont(None, 28)

    title = font_head.render(
        "CLOUD REDESIGN — ROUND 1 · 5 variants × 5 phases",
        True, (240, 240, 240))
    sheet.blit(title, (row_label_w + pad, 6))

    # Phase column headers.
    for c, (plabel, _p) in enumerate(PHASES):
        x = row_label_w + pad + c * (tw + pad)
        lbl = font_mid.render(plabel, True, (250, 230, 180))
        sheet.blit(lbl, (x + 8, label_h - 22))

    variant_ids = sorted(cv.VARIANTS.keys())
    for r, vid in enumerate(variant_ids):
        y = label_h + pad + r * (th + pad)
        name = cv.VARIANT_NAMES[vid]
        src = cv.VARIANT_SOURCES[vid]

        # Row index + variant name.
        idx_lbl = font_head.render(f"#{vid}", True, (255, 220, 130))
        sheet.blit(idx_lbl, (8, y + 6))

        # Wrap variant name into row-label column.
        words = name.split()
        line, ly = "", y + 40
        for word in words:
            test = (line + " " + word).strip()
            if font_mid.size(test)[0] > row_label_w - 16 and line:
                sheet.blit(font_mid.render(line, True, (235, 235, 235)),
                           (8, ly))
                ly += 20
                line = word
            else:
                line = test
        if line:
            sheet.blit(font_mid.render(line, True, (235, 235, 235)),
                       (8, ly))
            ly += 24

        # Research URL (wrapped, smaller, dim).
        url_line = ""
        for word in src.split():
            test = (url_line + " " + word).strip()
            if font_small.size(test)[0] > row_label_w - 16 and url_line:
                sheet.blit(
                    font_small.render(url_line, True, (170, 180, 200)),
                    (8, ly))
                ly += 16
                url_line = word
            else:
                url_line = test
        if url_line:
            sheet.blit(font_small.render(url_line, True, (170, 180, 200)),
                       (8, ly))

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
    out = OUT / "round_1.png"
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
