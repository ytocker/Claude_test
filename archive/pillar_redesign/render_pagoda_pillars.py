"""Render the round-5 day/night comparison sheet for pagoda pillars.

User feedback after round 4 was that the five candidates blurred into
near-identical Chinese towers. Round 5 rebuilds them from real iconic
pagodas; only the day → night palette sweep is requested this round.

Output:

  _comparison_dayNight_v2.png   5 candidates × 5 phases at one shared
                                seed per row — verifies every candidate
                                retints through DAY → SUNRISE → SUNSET
                                → DUSK → NIGHT while keeping each
                                pagoda's identity (cedar/gold/white-eye/
                                pastel-porcelain/terracotta-brick) read
                                instantly.

The old `_comparison_dayNight.png` is preserved in git history; this
round writes a `_v2` file so the round-4 sheet is still side-by-side
diffable.

Each tile is a full 360x640 game-style scene: biome sky + drifting
clouds, the locked-keeper V4 shan-shui mountains, ground texture, and
the pillar pair at the standard PIPE_W=58, gap_y≈285, gap_h≈170 spawn
position.

Run from anywhere:
    python archive/pillar_redesign/render_pagoda_pillars.py
"""
from __future__ import annotations

import math
import os
import pathlib
import random
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

from game.config import W, H, GROUND_Y, PIPE_W
from game import biome as _biome
from game.draw import (
    get_sky_surface_biome,
    draw_cloud,
    draw_ground,
)
import mountain_variants_r2 as mv
import pillar_pagoda_variants as pgv


PHASES = [
    ("day",     0.020),
    ("sunrise", 0.906),
    ("sunset",  0.363),
    ("dusk",    0.513),
    ("night",   0.644),
]
KEEPER_V4 = 4
# Canonical seed for the day/night row — chosen so each candidate's per-seed
# variation (tier count, mosaic distribution, hti ring count, etc.) fires at
# a representative density.
CANONICAL_SEED = 13

OUT = _REPO / "docs" / "pillar_redesign"
OUT.mkdir(parents=True, exist_ok=True)


def _scene_backdrop(phase: float) -> pygame.Surface:
    """Sky + clouds + keeper-V4 mountains + ground, no pillars yet."""
    palette = _biome.palette_for_phase(phase)
    surf = pygame.Surface((W, H))

    bucket = int(phase * _biome.PHASE_BUCKETS) % _biome.PHASE_BUCKETS
    sky = get_sky_surface_biome(W, H, GROUND_Y, palette, bucket)
    sky.set_alpha(None)
    surf.blit(sky, (0, 0))

    scroll = 120.0
    for i, (bx, by, sc, variant) in enumerate((
            (40, 95, 0.9, 0), (200, 150, 1.0, 2),
            (90, 230, 0.8, 3), (270, 70, 0.7, 1))):
        ox = ((bx - scroll * (0.04 + 0.02 * i)) % (W + 160)) - 80
        draw_cloud(surf, ox, by + math.sin(0.45 + i) * 3, sc, variant=variant)

    mv.set_phase(phase)
    mv.VARIANTS[KEEPER_V4](surf, scroll, GROUND_Y, W,
                           palette['mtn_far'], palette['mtn_near'])

    draw_ground(surf, GROUND_Y, W, H, scroll,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    return surf


def render_tile(candidate_key: str, phase: float, seed: int) -> pygame.Surface:
    surf = _scene_backdrop(phase)
    palette = _biome.palette_for_phase(phase)

    # Standard spawn geometry — matches what the live game spawns at.
    gap_y = 285
    gap_h = 170
    px = W - 90
    top_rect = pygame.Rect(px, 0, PIPE_W, gap_y - gap_h // 2)
    bot_rect = pygame.Rect(px, gap_y + gap_h // 2, PIPE_W,
                           GROUND_Y - (gap_y + gap_h // 2))

    # A second pillar farther back so the row reads as a real corridor.
    px2 = W - 250
    # Use a distinct seed offset for the rear pillar so it doesn't look like
    # a duplicate of the foreground one.
    top2 = pygame.Rect(px2, 0, PIPE_W, max(1, top_rect.height - 40))
    bot2 = pygame.Rect(px2, top2.height + gap_h + 10, PIPE_W,
                       GROUND_Y - (top2.height + gap_h + 10))

    pgv.CANDIDATES[candidate_key](surf, top2, bot2, palette, seed + 401)
    pgv.CANDIDATES[candidate_key](surf, top_rect, bot_rect, palette, seed)
    return surf


def make_day_night_sheet() -> pygame.Surface:
    """Rows = 5 candidates, Cols = 5 phases. Same seed per row to isolate
    the palette change."""
    rows = list(pgv.CANDIDATES.keys())
    cols = PHASES
    tw, th = W, H
    label_h = 30
    row_label_w = 220
    pad = 10
    sheet_w = row_label_w + pad + len(cols) * (tw + pad)
    sheet_h = label_h + pad + len(rows) * (th + pad)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((20, 20, 24))

    font_small = pygame.font.SysFont(None, 22)
    font_head = pygame.font.SysFont(None, 28)

    title = font_head.render(
        "Round 5 pagodas — day → sunrise → sunset → dusk → night",
        True, (240, 240, 240))
    sheet.blit(title, (row_label_w + pad, 6))

    for c, (pname, _) in enumerate(cols):
        x = row_label_w + pad + c * (tw + pad)
        lbl = font_head.render(pname.upper(), True, (240, 240, 240))
        sheet.blit(lbl, (x + tw // 2 - lbl.get_width() // 2, label_h - 22))

    for r, key in enumerate(rows):
        y = label_h + pad + r * (th + pad)
        name_lbl = font_head.render(f"#{r + 1}", True, (255, 220, 130))
        sheet.blit(name_lbl, (8, y + 6))
        blurb = pgv.CANDIDATE_BLURBS[key]
        words = (key + " — " + blurb).split()
        line, ly = "", y + 36
        for word in words:
            test = (line + " " + word).strip()
            if font_small.size(test)[0] > row_label_w - 12 and line:
                sheet.blit(font_small.render(line, True, (215, 215, 215)),
                           (8, ly))
                ly += 20
                line = word
            else:
                line = test
        if line:
            sheet.blit(font_small.render(line, True, (215, 215, 215)),
                       (8, ly))

        for c, (pname, pval) in enumerate(cols):
            random.seed(CANONICAL_SEED * 100 + int(pval * 1000))
            tile = render_tile(key, pval, CANONICAL_SEED)
            x = row_label_w + pad + c * (tw + pad)
            sheet.blit(tile, (x, y))
            tag = font_small.render(f"{key} · {pname}", True, (250, 250, 250))
            bg = pygame.Surface((tag.get_width() + 8, tag.get_height() + 4),
                                pygame.SRCALPHA)
            bg.fill((0, 0, 0, 120))
            sheet.blit(bg, (x + 4, y + 4))
            sheet.blit(tag, (x + 8, y + 6))

    return sheet


def main() -> None:
    dn_sheet = make_day_night_sheet()
    dn_path = OUT / "_comparison_dayNight_v2.png"
    pygame.image.save(dn_sheet, dn_path)
    print(f"wrote {dn_path}  "
          f"({dn_sheet.get_width()}x{dn_sheet.get_height()})")


if __name__ == "__main__":
    main()
