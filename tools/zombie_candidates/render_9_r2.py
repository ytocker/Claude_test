"""Scratch round-2 render for Zombie Design 9 (TRENCH-DEAD WAR PARROT).

Composites the three judgement views the art-director asked for — a mid-flight
gameplay panel, a large hero shot, and a 40px truth-read — onto one sheet so the
helmet-seat / chinstrap / jaw fixes can be verified at real gameplay scale.
Not shipped: exploration output only, saved under ``docs/``.
"""
from __future__ import annotations

import pygame

import tools.ninja_render as nr
import tools.zombie_candidates.design_9 as d

BG = (18, 16, 28)
PAD = 24


def _label(surf, text, x, y, size=20, color=(235, 232, 240)):
    font = pygame.font.SysFont("arial", size, bold=True)
    surf.blit(font.render(text, True, color), (x, y))


def main():
    frame = nr._frame(d.build, nr.FRAME_IDX, nr.TILT)
    gameplay = nr.gameplay_panel(d.build, 220, 392)
    hero = nr.hero_panel(d.build, 320)

    # 40px truth-read — shrink to the smallest on-screen size, then nearest-
    # neighbour back up so the silhouette read is judged with no smoothing.
    tiny = pygame.transform.smoothscale(frame, (40, 40))
    truth = pygame.transform.scale(tiny, (200, 200))

    top = 56
    maxh = max(gameplay.get_height(), hero.get_height(), truth.get_height())
    gy = top + (maxh - gameplay.get_height()) // 2
    hy = top + (maxh - hero.get_height()) // 2
    ty = top + (maxh - truth.get_height()) // 2

    x0 = PAD
    x1 = x0 + gameplay.get_width() + PAD
    x2 = x1 + hero.get_width() + PAD
    total_w = x2 + truth.get_width() + PAD
    total_h = top + maxh + PAD + 24

    sheet = pygame.Surface((total_w, total_h))
    sheet.fill(BG)
    _label(sheet, "D9 SOLDIER — R2", PAD, 16, size=26)

    sheet.blit(gameplay, (x0, gy))
    sheet.blit(hero, (x1, hy))
    sheet.blit(truth, (x2, ty))

    _label(sheet, "gameplay", x0, gy + gameplay.get_height() + 4, size=16,
           color=(180, 176, 190))
    _label(sheet, "hero", x1, hy + hero.get_height() + 4, size=16,
           color=(180, 176, 190))
    _label(sheet, "40px truth-read", x2, ty + truth.get_height() + 4, size=16,
           color=(180, 176, 190))

    out = "docs/store_redesign/costume/zombie/design_9/round_2.png"
    import os
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out)


if __name__ == "__main__":
    main()
