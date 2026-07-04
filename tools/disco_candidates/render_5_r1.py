"""Round-1 review sheet for DISCO Design 5 — MIRRORBALL.

Renders the candidate over the real gameplay biome (the deliverable read) plus
a clean hero shot and a 4x zoom of every flap frame so the facet shimmer + the
40px silhouette read can both be judged. Preview only — writes under docs/, not
into the shipped bundle.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from tools.ninja_render import gameplay_panel, hero_panel
from tools.disco_candidates.design_5 import build

OUT = "docs/store_redesign/costume/disco/design_5/round_1.png"

BG = (18, 16, 26)
PANEL = 300                 # hero shot (square)
GPW, GPH = 210, 300         # gameplay crop is portrait (~0.72 aspect)
GAP = 16
COLS_W = PANEL + GPW * 2 + GAP * 4
SHEET_W = COLS_W
SHEET_H = 70 + PANEL + GAP + 300 + 40


def _checker(box, cell=8):
    s = pygame.Surface((box, box))
    a, b = (54, 54, 62), (40, 40, 48)
    for y in range(0, box, cell):
        for x in range(0, box, cell):
            s.fill(a if ((x // cell + y // cell) % 2 == 0) else b, (x, y, cell, cell))
    return s


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    sheet.fill(BG)

    title = pygame.font.SysFont("Arial", 30, bold=True)
    small = pygame.font.SysFont("Arial", 16)
    sheet.blit(title.render("D5 MIRRORBALL — R1", True, (240, 244, 252)), (GAP, 20))

    y0 = 70
    # Top row: hero product shot + two live gameplay reads.
    x_hero = GAP
    x_g1 = GAP * 2 + PANEL
    x_g2 = GAP * 3 + PANEL + GPW
    sheet.blit(hero_panel(build, PANEL, tilt=6.0), (x_hero, y0))
    sheet.blit(gameplay_panel(build, GPW, GPH), (x_g1, y0))
    sheet.blit(gameplay_panel(build, GPW, GPH, frame_idx=0, tilt=-18.0), (x_g2, y0))
    for x, lbl in ((x_hero, "HERO"), (x_g1, "GAMEPLAY (glide)"),
                   (x_g2, "GAMEPLAY (climb)")):
        sheet.blit(small.render(lbl, True, (180, 186, 200)), (x + 4, y0 + PANEL - 22))

    # Bottom row: 4x zoom of every flap frame on a checker so facet shimmer +
    # the poke-through beak/eye can be inspected, and a 1:1 40px read at right.
    y1 = y0 + PANEL + GAP
    zbox = 300
    checker = _checker(zbox)
    slot_w = (COLS_W - GAP) // 4
    for f in range(4):
        frame = build(f, 0.0)
        bb = frame.get_bounding_rect()
        crop = frame.subsurface(bb).copy() if bb.width else frame
        scale = int(min((slot_w - 24) / crop.get_width(),
                        (zbox - 40) / crop.get_height()))
        scale = max(3, scale)
        big = pygame.transform.scale(
            crop, (crop.get_width() * scale, crop.get_height() * scale))
        tile = checker.copy()
        tile = pygame.transform.scale(checker, (slot_w, zbox))
        tile.blit(big, big.get_rect(center=(slot_w // 2, zbox // 2 - 8)))
        # Actual-size 40px read in the corner so nothing hides behind the zoom.
        small_read = pygame.transform.smoothscale(crop, (40, int(40 * crop.get_height() / crop.get_width())))
        tile.blit(small_read, (slot_w - 48, zbox - 60))
        tile.blit(small.render(f"frame {f}", True, (210, 214, 224)), (8, zbox - 22))
        sheet.blit(tile, (GAP + f * slot_w, y1))

    pygame.image.save(sheet, OUT)
    print("wrote", OUT, sheet.get_size())


if __name__ == "__main__":
    main()
