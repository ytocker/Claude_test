"""Render the round-2 sheet for basketball DESIGN 5 — THE COACH (sideline).

HERO panel (NEAREST upscale of the bounding content so the costume detail is
crisp), a gameplay panel (Pip mid-flight in a real biome scene), and the 40px
NEAREST truth read on a day-bright AND a night-dark swatch so the at-size read
is honest — exactly the deliverable shape the loop expects.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from tools.ninja_render import gameplay_panel
from tools.basketball_candidates.design_5 import build

OUT = "docs/store_redesign/costume/basketball/design_5/round_2.png"

PAD = 18
HERO = 300
# Kept proportioned so the 0.78*H crop the harness takes stays inside the
# 360-wide canvas (crop_w = 0.78*640 * GP_W/GP_H must be <= 360).
GP_W, GP_H = 255, 360
TRUTH = 40
TRUTH_UP = 160          # NEAREST upscale of the 40px read so the truth is visible
DAY = (150, 196, 232)
NIGHT = (18, 16, 30)
LABEL = (236, 238, 244)
SHEET_BG = (32, 30, 40)


def _hero_nearest(box, bg=(22, 20, 32)):
    """Product shot upscaled with NEAREST so every drawn pixel stays crisp —
    the honest 'what did I actually draw' read the smoothscale hero blurs."""
    panel = pygame.Surface((box, box), pygame.SRCALPHA)
    pygame.draw.rect(panel, bg, panel.get_rect(), border_radius=14)
    frame = build(2, 0.0)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy() if bb.width else frame
    sw, sh = frame.get_size()
    scale = int((box * 0.82) / max(sw, sh))
    scale = max(1, scale)
    frame = pygame.transform.scale(frame, (sw * scale, sh * scale))
    panel.blit(frame, frame.get_rect(center=(box // 2, box // 2)))
    return panel


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

    hero = _hero_nearest(HERO)
    gp = gameplay_panel(build, GP_W, GP_H)
    t_day = _truth_swatch(DAY)
    t_night = _truth_swatch(NIGHT)

    col_w = max(HERO, TRUTH_UP * 2 + PAD)
    width = PAD * 3 + col_w + GP_W
    height = PAD * 4 + 28 + HERO + 28 + TRUTH_UP + 24
    sheet = pygame.Surface((width, height))
    sheet.fill(SHEET_BG)

    title = font.render(
        "BASKETBALL  DESIGN 5 — THE COACH  (sideline)   ·   ROUND 2", True, LABEL)
    sheet.blit(title, (PAD, PAD - 4))

    y0 = PAD + 24
    sheet.blit(hero, (PAD, y0))
    sheet.blit(small.render("HERO (NEAREST)", True, LABEL), (PAD, y0 - 2))

    gx = PAD * 2 + col_w
    sheet.blit(gp, (gx, y0))
    sheet.blit(small.render("GAMEPLAY — Pip mid-flight", True, LABEL), (gx, y0 - 2))

    ty = y0 + HERO + 26
    sheet.blit(small.render("40px TRUTH READ (NEAREST)", True, LABEL), (PAD, ty - 18))
    sheet.blit(t_day, (PAD, ty))
    sheet.blit(small.render("40px day", True, LABEL), (PAD, ty + TRUTH_UP + 2))
    sheet.blit(t_night, (PAD + TRUTH_UP + PAD, ty))
    sheet.blit(small.render("40px night", True, LABEL),
               (PAD + TRUTH_UP + PAD, ty + TRUTH_UP + 2))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(sheet, OUT)
    print("wrote", OUT, sheet.get_size())


if __name__ == "__main__":
    main()
