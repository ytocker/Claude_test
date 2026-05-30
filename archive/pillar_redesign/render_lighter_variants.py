"""Render the round-14 LIGHTER-COLOR variants sheet for Songyue and
Tō-ji — the two darkest pagodas from the round-13 winners set.

User feedback after round 13: Songyue's deep terracotta brick and Tō-ji's
dark cypress sit far heavier than the rest of the eleven winners. This
sheet drops 4 lighter palette variants per pagoda alongside the baseline
so the user can pick favorites for the next round.

Row order (10 rows × 5 phases):
  1. Songyue baseline (deep terracotta brick — round-13 winner)
  2. Songyue cream      (sun-bleached Northern-Wei)
  3. Songyue sandstone  (Yungang warm tan)
  4. Songyue blush      (washed-out terracotta)
  5. Songyue rose       (light pink + cool grey mortar)
  6. Tō-ji baseline (dark cypress — round-13 winner)
  7. Tō-ji cedar gold      (warm honey cedar)
  8. Tō-ji light pine      (pale blond pine)
  9. Tō-ji weathered white (cool whitewashed wood)
 10. Tō-ji teak           (medium warm teak / oak)

Output:
  docs/pillar_redesign/_lighter_variants.png

The main winners sheet (_comparison_winners.png) stays untouched.

Run from anywhere:
    python archive/pillar_redesign/render_lighter_variants.py
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

# Each entry: (display label, candidate function name, round tag).
# Order: songyue baseline → 4 songyue variants → toji baseline →
# 4 toji variants. Baselines first per pagoda so the eye anchors to
# the original tone before scanning the lighter family.
VARIANTS = [
    ("Songyue — BASELINE (deep terracotta brick, R13 winner)",
     "candidate_songyue",           "R13"),
    ("Songyue cream — sun-bleached Northern-Wei bone-cream brick",
     "candidate_songyue_cream",     "R14"),
    ("Songyue sandstone — Yungang warm tan with faint pink hint",
     "candidate_songyue_sandstone", "R14"),
    ("Songyue blush — washed-out terracotta, ~30% lighter",
     "candidate_songyue_blush",     "R14"),
    ("Songyue rose — light pink brick + cool grey mortar",
     "candidate_songyue_rose",      "R14"),
    ("Tō-ji — BASELINE (dark cypress wood, R13 winner)",
     "candidate_toji",              "R13"),
    ("Tō-ji cedar gold — warm honey cedar body",
     "candidate_toji_cedar_gold",   "R14"),
    ("Tō-ji light pine — pale neutral blond pine",
     "candidate_toji_light_pine",   "R14"),
    ("Tō-ji weathered white — cool whitewashed old-wood",
     "candidate_toji_weathered_white", "R14"),
    ("Tō-ji teak — medium warm teak / oak",
     "candidate_toji_teak",         "R14"),
]

# Ground accents reused verbatim from render_winners.py so each Songyue
# row sits on the Henan terracotta-dust band and each Tō-ji row sits on
# the Heian cedar-litter band — keeps the comparison honest. The lighter
# variants share their parent's accent so palette comparisons aren't
# contaminated by a different ground band.
ROW_GROUND_ACCENT = {
    "songyue":               (162, 96, 72),
    "songyue_cream":         (162, 96, 72),
    "songyue_sandstone":     (162, 96, 72),
    "songyue_blush":         (162, 96, 72),
    "songyue_rose":          (162, 96, 72),
    "toji":                  (96, 76, 60),
    "toji_cedar_gold":       (96, 76, 60),
    "toji_light_pine":       (96, 76, 60),
    "toji_weathered_white":  (96, 76, 60),
    "toji_teak":             (96, 76, 60),
}

KEEPER_V4 = 4
CANONICAL_SEED = 13

OUT = _REPO / "docs" / "pillar_redesign"
OUT.mkdir(parents=True, exist_ok=True)


def _apply_ground_accent(surf, row_key):
    accent = ROW_GROUND_ACCENT.get(row_key)
    if accent is None:
        return
    overlay = pygame.Surface((W, 7), pygame.SRCALPHA)
    overlay.fill((*accent, 110))
    surf.blit(overlay, (0, GROUND_Y))
    for x in range(0, W, 9):
        r = (x * 7 + row_key.__hash__() & 0xFF) % 5
        col = (max(0, accent[0] - 30), max(0, accent[1] - 30),
               max(0, accent[2] - 30))
        surf.set_at((x + r, GROUND_Y + 2), col)
        surf.set_at((x + r + 4, GROUND_Y + 5), col)


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


def render_tile(candidate_name: str, row_key: str,
                phase: float, seed: int) -> pygame.Surface:
    surf = _scene_backdrop(phase)
    palette = _biome.palette_for_phase(phase)

    _apply_ground_accent(surf, row_key)

    gap_y = 280
    gap_h = 170
    px = W - 90
    top_rect = pygame.Rect(px, 0, PIPE_W, gap_y - gap_h // 2)
    bot_rect = pygame.Rect(px, gap_y + gap_h // 2, PIPE_W,
                           GROUND_Y - (gap_y + gap_h // 2))

    px2 = W - 250
    top2 = pygame.Rect(px2, 0, PIPE_W, max(1, top_rect.height - 40))
    bot2 = pygame.Rect(px2, top2.height + gap_h + 10, PIPE_W,
                       GROUND_Y - (top2.height + gap_h + 10))

    fn = getattr(pgv, candidate_name)
    fn(surf, top2, bot2, palette, seed + 401)
    fn(surf, top_rect, bot_rect, palette, seed)
    return surf


def make_variants_sheet() -> pygame.Surface:
    tw, th = W, H
    label_h = 30
    row_label_w = 300
    pad = 10
    sheet_w = row_label_w + pad + len(PHASES) * (tw + pad)
    sheet_h = label_h + pad + len(VARIANTS) * (th + pad)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((20, 20, 24))

    font_small = pygame.font.SysFont(None, 22)
    font_head = pygame.font.SysFont(None, 28)

    title = font_head.render(
        "ROUND 14 — Songyue + Tō-ji LIGHTER variants  ·  "
        "day → sunrise → sunset → dusk → night",
        True, (240, 240, 240))
    sheet.blit(title, (row_label_w + pad, 6))

    for c, (pname, _) in enumerate(PHASES):
        x = row_label_w + pad + c * (tw + pad)
        lbl = font_head.render(pname.upper(), True, (240, 240, 240))
        sheet.blit(lbl, (x + tw // 2 - lbl.get_width() // 2, label_h - 22))

    for r, (label, fn_name, tag) in enumerate(VARIANTS):
        y = label_h + pad + r * (th + pad)
        idx_lbl = font_head.render(f"#{r + 1}", True, (255, 220, 130))
        sheet.blit(idx_lbl, (8, y + 6))
        tag_lbl = font_small.render(tag, True, (200, 200, 110))
        sheet.blit(tag_lbl, (8, y + 32))

        words = label.split()
        line, ly = "", y + 56
        for word in words:
            test = (line + " " + word).strip()
            if font_small.size(test)[0] > row_label_w - 16 and line:
                sheet.blit(font_small.render(line, True, (215, 215, 215)),
                           (8, ly))
                ly += 20
                line = word
            else:
                line = test
        if line:
            sheet.blit(font_small.render(line, True, (215, 215, 215)),
                       (8, ly))

        row_key = fn_name.replace("candidate_", "")
        for c, (pname, pval) in enumerate(PHASES):
            random.seed(CANONICAL_SEED * 100 + int(pval * 1000))
            # Each variant uses its own _cached_draw key so wiping the
            # cache per row keeps the sheet honest if helper state leaks.
            if hasattr(pgv, "_PILLAR_CACHE"):
                pgv._PILLAR_CACHE.clear()
            tile = render_tile(fn_name, row_key, pval, CANONICAL_SEED)
            x = row_label_w + pad + c * (tw + pad)
            sheet.blit(tile, (x, y))
            tagtxt = font_small.render(f"{row_key} · {pname}",
                                       True, (250, 250, 250))
            bg = pygame.Surface(
                (tagtxt.get_width() + 8, tagtxt.get_height() + 4),
                pygame.SRCALPHA)
            bg.fill((0, 0, 0, 120))
            sheet.blit(bg, (x + 4, y + 4))
            sheet.blit(tagtxt, (x + 8, y + 6))

    return sheet


def main() -> None:
    sheet = make_variants_sheet()
    out = OUT / "_lighter_variants.png"
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
