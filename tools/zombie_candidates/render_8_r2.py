"""Round-2 review render for zombie candidate 8 (BARNACLE DROWNED WRETCH).

Scratch harness: composites a gameplay panel, a large hero shot, and a 40px
"truth read" (down to 40px then nearest-neighbour back up 5x) so the coarse
silhouette read is judged the same way it survives on-screen. Exploration only.
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import tools.ninja_render as nr
import tools.zombie_candidates.design_8 as d

pygame.init()

OUT = "docs/store_redesign/costume/zombie/design_8/round_2.png"


def _truth_read(box: int) -> pygame.Surface:
    """Hero frame crushed to 40px then blown back up 5x with no smoothing, to
    expose whether the lure/eye/contour cues survive the shrink."""
    frame = nr._frame(d.build, nr.FRAME_IDX, nr.TILT)
    bb = frame.get_bounding_rect()
    if bb.width and bb.height:
        frame = frame.subsurface(bb).copy()
    tiny = pygame.transform.smoothscale(frame, (40, 40))
    big = pygame.transform.scale(tiny, (box, box))       # nearest-neighbour
    panel = pygame.Surface((box, box), pygame.SRCALPHA)
    pygame.draw.rect(panel, (30, 34, 44), panel.get_rect(), border_radius=12)
    panel.blit(big, big.get_rect(center=(box // 2, box // 2)))
    return panel


def main():
    gameplay = nr.gameplay_panel(d.build, 220, 392)
    hero = nr.hero_panel(d.build, 320)
    truth = _truth_read(200)

    pad = 24
    label_h = 44
    panels = [gameplay, hero, truth]
    total_w = sum(p.get_width() for p in panels) + pad * (len(panels) + 1)
    total_h = label_h + max(p.get_height() for p in panels) + pad

    sheet = pygame.Surface((total_w, total_h))
    sheet.fill((18, 16, 28))

    font = pygame.font.SysFont("dejavusans", 22, bold=True)
    small = pygame.font.SysFont("dejavusans", 15)
    sheet.blit(font.render("D8 DROWNED — R2", True, (226, 232, 238)), (pad, 12))

    captions = ["gameplay mid-flight", "hero shot", "40px truth read"]
    x = pad
    for p, cap in zip(panels, captions):
        y = label_h
        sheet.blit(p, (x, y))
        sheet.blit(small.render(cap, True, (150, 160, 172)),
                   (x, y + p.get_height() + 2))
        x += p.get_width() + pad

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(sheet, OUT)
    print("wrote", OUT, sheet.get_size())


if __name__ == "__main__":
    main()
