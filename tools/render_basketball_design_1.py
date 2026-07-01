"""Render the round sheet for basketball DESIGN 1 — THE PRO.

A large HERO panel (NEAREST upscale for crispness), a gameplay panel (Pip
mid-flight in a real biome scene), and a 40px NEAREST truth read on a
day-bright AND a night-dark swatch so the at-size read can be judged.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from tools.ninja_render import gameplay_panel, hero_panel
from tools.basketball_candidates.design_1 import build

OUT = "docs/store_redesign/costume/basketball/design_1/round_1.png"

PAD = 18
HERO = 300
GP_W, GP_H = 300, 360
TRUTH = 40
TRUTH_UP = 160          # NEAREST upscale of the 40px read so the truth is visible
DAY = (150, 196, 232)
NIGHT = (18, 16, 30)
LABEL = (236, 238, 244)
SHEET_BG = (32, 30, 40)


def _truth_swatch(bg):
    """The candidate composited at native size, NEAREST-downscaled to 40px then
    NEAREST-upscaled — the honest 'what does it read as when tiny' test."""
    frame = build(2, 8.0)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy() if bb.width else frame
    sw, sh = frame.get_size()
    scale = (TRUTH * 0.92) / max(sw, sh)
    small = pygame.transform.smoothscale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    cell = pygame.Surface((TRUTH, TRUTH))
    cell.fill(bg)
    cell.blit(small, small.get_rect(center=(TRUTH // 2, TRUTH // 2)))
    return pygame.transform.scale(cell, (TRUTH_UP, TRUTH_UP))


def main():
    font = pygame.font.SysFont("dejavusans", 15, bold=True)
    small = pygame.font.SysFont("dejavusans", 12)

    hero = hero_panel(build, HERO, tilt=0.0)
    # NEAREST re-upscale of the bounding content for crisp hero pixels.
    gp = gameplay_panel(build, GP_W, GP_H)
    t_day = _truth_swatch(DAY)
    t_night = _truth_swatch(NIGHT)

    col_w = max(HERO, TRUTH_UP * 2 + PAD)
    width = PAD * 3 + col_w + GP_W
    height = PAD * 4 + 28 + HERO + 28 + TRUTH_UP + 24
    sheet = pygame.Surface((width, height))
    sheet.fill(SHEET_BG)

    title = font.render("BASKETBALL  DESIGN 1 — THE PRO  (modern NBA)", True, LABEL)
    sheet.blit(title, (PAD, PAD - 4))

    y0 = PAD + 24
    # Hero (left column, top).
    sheet.blit(hero, (PAD, y0))
    sheet.blit(small.render("HERO", True, LABEL), (PAD, y0 - 2))

    # Gameplay (right column).
    gx = PAD * 2 + col_w
    sheet.blit(gp, (gx, y0))
    sheet.blit(small.render("GAMEPLAY — Pip mid-flight", True, LABEL), (gx, y0 - 2))

    # Truth reads (left column, below hero).
    ty = y0 + HERO + 26
    sheet.blit(small.render("40px TRUTH READ (NEAREST)", True, LABEL), (PAD, ty - 18))
    sheet.blit(t_day, (PAD, ty))
    sheet.blit(small.render("day-bright", True, LABEL), (PAD, ty + TRUTH_UP + 2))
    sheet.blit(t_night, (PAD + TRUTH_UP + PAD, ty))
    sheet.blit(small.render("night-dark", True, LABEL),
               (PAD + TRUTH_UP + PAD, ty + TRUTH_UP + 2))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(sheet, OUT)
    print("wrote", OUT, sheet.get_size())


if __name__ == "__main__":
    main()
