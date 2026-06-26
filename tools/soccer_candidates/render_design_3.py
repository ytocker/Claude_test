"""Headless review sheet for DESIGN 3 — THE NÚMERO 10 (soccer).

Composites the candidate the same way the deliverable will: a large HERO shot
(NEAREST upscale so the laced collar / crest / "10" detail is judged crisp), an
in-gameplay panel, and the 40px NEAREST "truth read" on both a day-bright and a
night-dark swatch — the read that has to say "retro footballer".
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from tools.ninja_render import gameplay_panel, hero_panel
from tools.soccer_candidates.design_3 import build

OUT = "docs/store_redesign/costume/soccer/design_3/round_1.png"

FRAME_IDX, TILT = 2, 10.0
DAY = (150, 196, 232)
NIGHT = (16, 18, 30)


def _truth(bg):
    """40px NEAREST downscale of the bird on a flat swatch — the truth read."""
    src = build(FRAME_IDX, TILT)
    bb = src.get_bounding_rect()
    if bb.width and bb.height:
        src = src.subsurface(bb).copy()
    sw, sh = src.get_size()
    sc = 40 / max(sw, sh)
    small = pygame.transform.smoothscale(
        src, (max(1, int(sw * sc)), max(1, int(sh * sc))))
    swatch = pygame.Surface((64, 64))
    swatch.fill(bg)
    swatch.blit(small, small.get_rect(center=(32, 32)))
    return swatch


def _nearest_up(surf, box):
    sw, sh = surf.get_size()
    sc = int(box / max(sw, sh))
    return pygame.transform.scale(surf, (sw * sc, sh * sc))


def _label(sheet, font, text, x, y):
    sheet.blit(font.render(text, True, (236, 236, 244)), (x, y))


def main():
    pygame.font.init()
    font = pygame.font.SysFont("dejavusans", 15, bold=True)
    small_font = pygame.font.SysFont("dejavusans", 12)

    SHEET_W, SHEET_H = 856, 520
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    sheet.fill((30, 28, 40))
    _label(sheet, font, "SOCCER · DESIGN 3 — THE NUMERO 10  (retro legend, laced collar)", 16, 12)

    # HERO — large NEAREST upscale of the hero_panel (clean product shot).
    hero = hero_panel(build, 220, frame_idx=FRAME_IDX, tilt=0.0)
    hero = pygame.transform.scale(hero, (300, 300))
    sheet.blit(hero, (16, 44))
    _label(sheet, small_font, "HERO (clean shot)", 16, 348)

    # Gameplay panel.
    gp = gameplay_panel(build, 260, 360, frame_idx=FRAME_IDX, tilt=TILT)
    sheet.blit(gp, (336, 44))
    _label(sheet, small_font, "IN GAMEPLAY", 336, 408)

    # 40px truth reads, NEAREST-upscaled so pixels are honest.
    day = _nearest_up(_truth(DAY), 180)
    night = _nearest_up(_truth(NIGHT), 180)
    sheet.blit(day, (656, 44))
    _label(sheet, small_font, "40px DAY", 656, 230)
    sheet.blit(night, (656, 252))
    _label(sheet, small_font, "40px NIGHT", 656, 438)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(sheet, OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
