"""Render the round_2 revision sheet for basketball DESIGN 4 (All-Star Dunker).

Matches the round_1 layout (hero clean shot + in-gameplay + 40px day/night truth
swatches) so the art-director compares like-for-like. HERO NEAREST = the near
wing (with the chrome sleeve) faces the viewer in every panel.

Run: SDL_VIDEODRIVER=dummy PYTHONPATH=. python tools/render_basketball_design_4_r2.py
"""
import os, importlib
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.font.init()

from tools.ninja_render import gameplay_panel, hero_panel

FRAME_IDX, TILT = 2, 10.0
DAY = (150, 196, 232)
NIGHT = (16, 18, 30)
LABEL = "DESIGN 4 — THE ALL-STAR DUNKER · ROUND 2"


def _truth(build, bg):
    src = build(FRAME_IDX, TILT)
    bb = src.get_bounding_rect()
    if bb.width and bb.height:
        src = src.subsurface(bb).copy()
    sw, sh = src.get_size()
    sc = 40 / max(sw, sh)
    small = pygame.transform.scale(src, (max(1, int(sw * sc)), max(1, int(sh * sc))))
    swatch = pygame.Surface((64, 64))
    swatch.fill(bg)
    swatch.blit(small, small.get_rect(center=(32, 32)))
    return swatch


def _nearest_up(surf, box):
    sw, sh = surf.get_size()
    sc = max(1, int(box / max(sw, sh)))
    return pygame.transform.scale(surf, (sw * sc, sh * sc))


def main():
    mod = importlib.import_module("tools.basketball_candidates.design_4")
    build = mod.build
    font = pygame.font.SysFont("dejavusans", 15, bold=True)
    sfont = pygame.font.SysFont("dejavusans", 12)

    SHEET_W, SHEET_H = 856, 520
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    sheet.fill((30, 28, 40))
    sheet.blit(font.render(f"BASKETBALL · {LABEL}", True, (236, 236, 244)), (16, 12))

    hero = hero_panel(build, 220, frame_idx=FRAME_IDX, tilt=0.0)
    hero_big = pygame.transform.scale(hero, (300, 300))
    sheet.blit(hero_big, (16, 44))
    sheet.blit(sfont.render("HERO NEAREST (clean shot)", True, (200, 200, 210)), (16, 348))

    gp = gameplay_panel(build, 260, 360, frame_idx=FRAME_IDX, tilt=TILT)
    sheet.blit(gp, (336, 44))
    sheet.blit(sfont.render("IN GAMEPLAY", True, (200, 200, 210)), (336, 408))

    day_up = _nearest_up(_truth(build, DAY), 180)
    night_up = _nearest_up(_truth(build, NIGHT), 180)
    sheet.blit(day_up, (616, 44))
    sheet.blit(sfont.render("40px DAY", True, (200, 200, 210)), (616, 230))
    sheet.blit(night_up, (616, 252))
    sheet.blit(sfont.render("40px NIGHT", True, (200, 200, 210)), (616, 438))

    out = "docs/store_redesign/costume/basketball/design_4/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
