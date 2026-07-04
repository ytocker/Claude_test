"""Round-2 review render for zombie Design 10 (Greasepaint Grave Jester).

Composites the three judging views side by side: a mid-flight gameplay panel,
a large hero shot, and a 40px "truth read" (downscaled then nearest-neighbour
blown back up) so the reviewer sees exactly what survives the in-game scale.
Scratch harness — writes only under docs/, touches no production art.
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import tools.ninja_render as nr
import tools.zombie_candidates.design_10 as d

pygame.init()

OUT = "docs/store_redesign/costume/zombie/design_10/round_2.png"


def _truth_read(frame, box=200):
    """Downscale the hero frame to 40px then blow it back up nearest-neighbour
    so the reviewer judges what actually survives the in-game downscale."""
    bb = frame.get_bounding_rect()
    src = frame.subsurface(bb).copy() if bb.width and bb.height else frame
    small = pygame.transform.smoothscale(src, (40, 40))
    return pygame.transform.scale(small, (box, box))


def main():
    frame = nr._frame(d.build, nr.FRAME_IDX, nr.TILT)

    gp = nr.gameplay_panel(d.build, 220, 392)
    hero = nr.hero_panel(d.build, 320)
    truth = _truth_read(frame, 200)

    pad = 20
    label_h = 40
    panels = [gp, hero, truth]
    total_w = sum(p.get_width() for p in panels) + pad * (len(panels) + 1)
    total_h = label_h + max(p.get_height() for p in panels) + pad * 2

    sheet = pygame.Surface((total_w, total_h))
    sheet.fill((18, 16, 28))

    font = pygame.font.SysFont("dejavusans", 22, bold=True)
    sheet.blit(font.render("D10 CLOWN — R2", True, (232, 228, 240)), (pad, 10))

    sub = pygame.font.SysFont("dejavusans", 14)
    captions = ["gameplay", "hero", "40px truth read"]
    x = pad
    y = label_h + pad
    for p, cap in zip(panels, captions):
        sheet.blit(p, (x, y))
        sheet.blit(sub.render(cap, True, (170, 166, 182)),
                   (x, y + p.get_height() + 2))
        x += p.get_width() + pad

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(sheet, OUT)
    print("wrote", OUT, sheet.get_size())


if __name__ == "__main__":
    main()
