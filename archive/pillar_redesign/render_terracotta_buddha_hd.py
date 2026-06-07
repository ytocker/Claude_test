"""Terracotta + Buddha HD pillar exploration sheet — round 1.

10 rows x 5 biome phases (day -> golden -> sunset -> dusk -> night).
Same layout convention as the round-1-3 harness but the candidate
module is the new HD pipeline. One canonical seed per cell so each row
is honestly a different candidate not a different RNG roll.

Output:
  docs/pillar_redesign/terracotta_buddha_hd_round_1.png

Run from anywhere:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python archive/pillar_redesign/render_terracotta_buddha_hd.py
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
import pillar_terracotta_buddha_hd as hd


# Same phase set as the failed-attempt sheet so AD can flip between the
# two side-by-side at matching cells.
PHASES = [
    ("day",     0.020),
    ("golden",  0.230),
    ("sunset",  0.363),
    ("dusk",    0.513),
    ("night",   0.644),
]

# (row label, candidate function name, short tag, accent ground band).
VARIANTS = [
    ("Terracotta General (高级军吏俑) - officer, fish-tail crown",
     "candidate_warrior_general", "WARRIOR", (164, 116, 80)),
    ("Standing Archer (立射俑) - torso lean, bow-arm extended",
     "candidate_warrior_standing_archer", "WARRIOR", (164, 116, 80)),
    ("Kneeling Crossbowman (跪射俑) - museum-icon crouch",
     "candidate_warrior_kneeling_archer", "WARRIOR", (164, 116, 80)),
    ("Cavalryman + Saddled Horse (骑兵俑 + 鞍马)",
     "candidate_warrior_cavalry", "WARRIOR", (164, 116, 80)),
    ("Charioteer (御手俑) - arms forward gripping reins",
     "candidate_warrior_charioteer", "WARRIOR", (164, 116, 80)),
    ("Leshan Giant Buddha (乐山大佛) - cliff sandstone seated",
     "candidate_buddha_leshan", "BUDDHA", (180, 132, 88)),
    ("Tian Tan Buddha (天坛大佛) - bronze abhaya mudra + halo",
     "candidate_buddha_tian_tan", "BUDDHA", (96, 86, 70)),
    ("Standing Maitreya / Budai (彌勒) - laughing, lotus throne",
     "candidate_buddha_maitreya", "BUDDHA", (118, 94, 56)),
    ("Cliff-Niche Reclining (涅槃·龕) - sandstone cliff + carved niche",
     "candidate_buddha_niche_reclining", "BUDDHA", (148, 116, 70)),
    ("Guanyin / Avalokiteśvara (觀音) - porcelain, vase + willow",
     "candidate_buddha_guanyin", "BUDDHA", (124, 130, 138)),
]

VARIANT_URLS = [
    "smithsonianmag.com/.../clay-commander-180985747",
    "travelchinaguide.com/.../standing-archers.htm",
    "travelchinaguide.com/.../kneeling-archers.htm",
    "travelchinaguide.com/.../cavalrymen.htm",
    "travelchinaguide.com/.../chariots.htm",
    "en.wikipedia.org/wiki/Leshan_Giant_Buddha",
    "en.wikipedia.org/wiki/Tian_Tan_Buddha",
    "en.wikipedia.org/wiki/Budai",
    "en.wikipedia.org/wiki/Yungang_Grottoes",
    "en.wikipedia.org/wiki/Dehua_porcelain + Guanyin",
]

KEEPER_V4 = 4
CANONICAL_SEED = 13

OUT = _REPO / "docs" / "pillar_redesign"
OUT.mkdir(parents=True, exist_ok=True)


def _apply_ground_accent(surf, accent):
    overlay = pygame.Surface((W, 7), pygame.SRCALPHA)
    overlay.fill((*accent, 110))
    surf.blit(overlay, (0, GROUND_Y))
    for x in range(0, W, 9):
        r = (x * 7 + accent[0] & 0xFF) % 5
        col = (max(0, accent[0] - 30), max(0, accent[1] - 30),
               max(0, accent[2] - 30))
        surf.set_at((x + r, GROUND_Y + 2), col)
        surf.set_at((x + r + 4, GROUND_Y + 5), col)


def _scene_backdrop(phase: float) -> pygame.Surface:
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
        draw_cloud(surf, ox, by + math.sin(0.45 + i) * 3, sc,
                   variant=variant)

    mv.set_phase(phase)
    mv.VARIANTS[KEEPER_V4](surf, scroll, GROUND_Y, W,
                           palette['mtn_far'], palette['mtn_near'])

    draw_ground(surf, GROUND_Y, W, H, scroll,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    return surf


def render_tile(candidate_name: str, accent_band: tuple,
                phase: float, seed: int) -> pygame.Surface:
    surf = _scene_backdrop(phase)
    palette = _biome.palette_for_phase(phase)

    _apply_ground_accent(surf, accent_band)

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

    fn = getattr(hd, candidate_name)
    fn(surf, top2, bot2, palette, seed + 401)
    fn(surf, top_rect, bot_rect, palette, seed)
    return surf


def make_sheet() -> pygame.Surface:
    tw, th = W, H
    label_h = 32
    row_label_w = 320
    pad = 10
    sheet_w = row_label_w + pad + len(PHASES) * (tw + pad)
    sheet_h = label_h + pad + len(VARIANTS) * (th + pad)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((20, 20, 24))

    font_small = pygame.font.SysFont(None, 20)
    font_mid = pygame.font.SysFont(None, 22)
    font_head = pygame.font.SysFont(None, 28)

    title = font_head.render(
        "TERRACOTTA + BUDDHA HD  -  R1 .  "
        "10 candidates x day -> golden -> sunset -> dusk -> night",
        True, (240, 240, 240))
    sheet.blit(title, (row_label_w + pad, 6))

    for c, (pname, _) in enumerate(PHASES):
        x = row_label_w + pad + c * (tw + pad)
        lbl = font_head.render(pname.upper(), True, (240, 240, 240))
        sheet.blit(lbl, (x + tw // 2 - lbl.get_width() // 2,
                         label_h - 24))

    for r, (label, fn_name, tag, accent) in enumerate(VARIANTS):
        y = label_h + pad + r * (th + pad)
        idx_lbl = font_head.render(f"#{r + 1}", True, (255, 220, 130))
        sheet.blit(idx_lbl, (8, y + 6))
        tag_col = (210, 170, 110) if tag == "WARRIOR" else (170, 200, 230)
        tag_lbl = font_mid.render(tag, True, tag_col)
        sheet.blit(tag_lbl, (8, y + 32))

        words = label.split()
        line, ly = "", y + 58
        for word in words:
            test = (line + " " + word).strip()
            if font_small.size(test)[0] > row_label_w - 16 and line:
                sheet.blit(font_small.render(line, True, (220, 220, 220)),
                           (8, ly))
                ly += 18
                line = word
            else:
                line = test
        if line:
            sheet.blit(font_small.render(line, True, (220, 220, 220)),
                       (8, ly))
            ly += 18

        url_lbl = font_small.render(VARIANT_URLS[r], True, (140, 170, 200))
        sheet.blit(url_lbl, (8, ly + 4))

        for c, (pname, pval) in enumerate(PHASES):
            random.seed(CANONICAL_SEED * 100 + int(pval * 1000))
            if hasattr(hd, "_PILLAR_CACHE"):
                hd._PILLAR_CACHE.clear()
            tile = render_tile(fn_name, accent, pval, CANONICAL_SEED)
            x = row_label_w + pad + c * (tw + pad)
            sheet.blit(tile, (x, y))
            row_key = fn_name.replace("candidate_", "")
            tagtxt = font_small.render(f"{row_key} . {pname}",
                                       True, (250, 250, 250))
            bg = pygame.Surface(
                (tagtxt.get_width() + 8, tagtxt.get_height() + 4),
                pygame.SRCALPHA)
            bg.fill((0, 0, 0, 130))
            sheet.blit(bg, (x + 4, y + 4))
            sheet.blit(tagtxt, (x + 8, y + 6))

    return sheet


def main() -> None:
    sheet = make_sheet()
    out = OUT / "terracotta_buddha_hd_round_1.png"
    pygame.image.save(sheet, out)
    print(f"wrote {out}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
