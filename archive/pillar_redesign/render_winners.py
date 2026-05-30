"""Render the user-curated WINNERS sheet — every favourite picked across
rounds 4 / 5 / 7 / 8 / 10 of the pagoda-pillar exploration on a single
comparison image.

The user's pick list (verbatim mapping to candidate functions):
  Round 4 — seed variation               v5  → candidate_stupa_canopy (round-4 snapshot)
  Round 5 — 5 iconic real-world pagodas  v4  → candidate_wat_arun
  Round 5 — 5 iconic real-world pagodas  v5  → candidate_songyue
  Round 7 — Hōryū-ji + Fogong polish     d1  → candidate_horyuji
  Round 7 — Hōryū-ji + Fogong polish     d2  → candidate_fogong
  Round 8 — 2 keepers + 10 East-Asian    d2  → candidate_toji
  Round 8 — 2 keepers + 10 East-Asian    d3  → candidate_daigoji
  Round 8 — 2 keepers + 10 East-Asian    d4  → candidate_yakushiji
  Round 8 — 2 keepers + 10 East-Asian    d8  → candidate_baoen
  Round 10 — 5 wooden tower candidates   d3  → candidate_muroji
  Round 10 — 5 wooden tower candidates   d6  → candidate_palsangjeon

Round 4's `candidate_stupa_canopy` was dropped from the live source in
round 5, so we import it from a frozen snapshot of the round-4 source
(`pillar_pagoda_variants_r4.py`, restored from commit fd3bcb0). Every
other winner is imported from the current `pillar_pagoda_variants`
module so they reflect their final round-7/8/10 polish.

Output:
  docs/pillar_redesign/_comparison_winners.png
  11 winners × 5 phases (day / sunrise / sunset / dusk / night),
  full-size 360×640 tiles, labelled.

Run from anywhere:
    python archive/pillar_redesign/render_winners.py
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
import pillar_pagoda_variants_r4 as pgv_r4


PHASES = [
    ("day",     0.020),
    ("sunrise", 0.906),
    ("sunset",  0.363),
    ("dusk",    0.513),
    ("night",   0.644),
]

# Each entry: (display label, source-module, candidate function name,
# round tag for the row blurb). Order is the order the user listed them.
WINNERS = [
    ("Round 4 v5 — Stupa + Prayer-Flag Canopy (Tibetan)",
     pgv_r4, "candidate_stupa_canopy", "R4"),
    ("Round 5 v4 — Wat Arun (Thai Khmer prang)",
     pgv,    "candidate_wat_arun",     "R5"),
    ("Round 5 v5 — Songyue Sandstone (12-sided Wei brick, warm tan)",
     pgv,    "candidate_songyue_sandstone", "R5+R14"),
    ("Round 7 d1 — Hōryū-ji (Japanese 5-storey tō, baseline)",
     pgv,    "candidate_horyuji",      "R7"),
    ("Round 7 d2 — Fogong / Yingxian (Liao wooden, baseline)",
     pgv,    "candidate_fogong",       "R7"),
    ("Round 8 d2 — Tō-ji (tallest Japanese wooden, dark cypress)",
     pgv,    "candidate_toji",         "R8"),
    ("Round 8 d3 — Daigo-ji (vermillion lacquer + gold sōrin)",
     pgv,    "candidate_daigoji",      "R8"),
    ("Round 8 d4 — Yakushi-ji (mokoshi pent-roof, bronze suien)",
     pgv,    "candidate_yakushiji",    "R8"),
    ("Round 8 d8 — Bao'en Porcelain Tower (Nanjing white porcelain)",
     pgv,    "candidate_baoen",        "R8"),
    ("Round 10 d3 — Murō-ji (smallest 5-storey, thatched cypress-bark)",
     pgv,    "candidate_muroji",       "R10"),
    ("Round 10 d6 — Palsangjeon / Beopjusa (only Korean wooden pagoda)",
     pgv,    "candidate_palsangjeon",  "R10"),
]

# Ground accents: reuse the curated palette from the round-10 harness so
# the rows that already have a site-specific tint keep it, and unstyled
# rows fall through to the default biome ground.
ROW_GROUND_ACCENT = {
    "daigoji":      (148, 80, 50),    # red-clay foreground.
    "wat_arun":     (180, 120, 140),  # Thai temple-grounds rose-clay.
    "songyue_sandstone": (192, 148, 110),  # warm sandy Wei dust to pair with the lighter brick.
    "songyue":      (162, 96, 72),    # Henan terracotta dust (original baseline, kept for reference).
    "toji":         (96, 76, 60),     # Heian cedar-litter forest.
    "yakushiji":    (140, 116, 78),   # Nara warm bronze-stone court.
    "baoen":        (208, 196, 178),  # Nanjing cool porcelain-white path.
    # Round-10 ground accents (already curated).
    "muroji":       (52, 78, 50),     # deep forest moss.
    "palsangjeon":  (118, 130, 138),  # cool Joseon courtyard.
    # The Tibetan stupa winner doesn't have a published accent — give it
    # one in keeping with the Boudhanath / Gyantse high-altitude palette.
    "stupa_canopy": (172, 152, 124),  # high-plateau dust.
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


def render_tile(source_module, candidate_name: str, row_key: str,
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

    fn = getattr(source_module, candidate_name)
    fn(surf, top2, bot2, palette, seed + 401)
    fn(surf, top_rect, bot_rect, palette, seed)
    return surf


def make_winners_sheet() -> pygame.Surface:
    tw, th = W, H
    label_h = 30
    row_label_w = 280
    pad = 10
    sheet_w = row_label_w + pad + len(PHASES) * (tw + pad)
    sheet_h = label_h + pad + len(WINNERS) * (th + pad)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((20, 20, 24))

    font_small = pygame.font.SysFont(None, 22)
    font_head = pygame.font.SysFont(None, 28)

    title = font_head.render(
        "WINNERS — every pick across rounds 4 / 5 / 7 / 8 / 10  ·  "
        "day → sunrise → sunset → dusk → night",
        True, (240, 240, 240))
    sheet.blit(title, (row_label_w + pad, 6))

    for c, (pname, _) in enumerate(PHASES):
        x = row_label_w + pad + c * (tw + pad)
        lbl = font_head.render(pname.upper(), True, (240, 240, 240))
        sheet.blit(lbl, (x + tw // 2 - lbl.get_width() // 2, label_h - 22))

    for r, (label, module, fn_name, tag) in enumerate(WINNERS):
        y = label_h + pad + r * (th + pad)
        idx_lbl = font_head.render(f"#{r + 1}", True, (255, 220, 130))
        sheet.blit(idx_lbl, (8, y + 6))
        tag_lbl = font_small.render(tag, True, (200, 200, 110))
        sheet.blit(tag_lbl, (8, y + 32))

        # Wrap the label to fit the row-label column.
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

        # Derive a row-key for the ground-accent lookup from the function name.
        row_key = fn_name.replace("candidate_", "")
        for c, (pname, pval) in enumerate(PHASES):
            random.seed(CANONICAL_SEED * 100 + int(pval * 1000))
            # Clear the live module's pillar cache so each row actually
            # rebuilds rather than reusing whatever sat in cache. The
            # round-4 snapshot has its own cache if any.
            if hasattr(pgv, "_PILLAR_CACHE"):
                pgv._PILLAR_CACHE.clear()
            if hasattr(pgv_r4, "_PILLAR_CACHE"):
                pgv_r4._PILLAR_CACHE.clear()
            tile = render_tile(module, fn_name, row_key, pval, CANONICAL_SEED)
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
    sheet = make_winners_sheet()
    out = OUT / "_comparison_winners.png"
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
