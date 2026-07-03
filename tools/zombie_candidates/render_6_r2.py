"""Round-2 review sheet for zombie design 6 (fungal / cordyceps host body).

Scratch harness: a gameplay crop, a large hero shot, and a 40px truth-read
(shrunk then blown up nearest-neighbour) side by side, so the silhouette break
and the gill hierarchy can be judged at both product and thumbnail scale.
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import tools.ninja_render as nr
import tools.zombie_candidates.design_6 as d

pygame.init()

BG = (18, 16, 28)
PAD = 20
LABEL_H = 40


def _truth_read(frame: pygame.Surface, small: int = 40, box: int = 200) -> pygame.Surface:
    """Shrink the hero frame to ``small`` px, then blow it back up nearest-
    neighbour so the thumbnail-scale silhouette is legible at review size."""
    tiny = pygame.transform.scale(frame, (small, small))
    panel = pygame.Surface((box, box), pygame.SRCALPHA)
    pygame.draw.rect(panel, (30, 28, 42), panel.get_rect(), border_radius=14)
    big = pygame.transform.scale(tiny, (box, box))
    panel.blit(big, (0, 0))
    return panel


def main():
    frame = nr._frame(d.build, nr.FRAME_IDX, nr.TILT)
    gp = nr.gameplay_panel(d.build, 220, 392)
    hero = nr.hero_panel(d.build, 320)
    truth = _truth_read(frame)

    panels = [gp, hero, truth]
    total_w = PAD + sum(p.get_width() + PAD for p in panels)
    total_h = LABEL_H + max(p.get_height() for p in panels) + PAD

    sheet = pygame.Surface((total_w, total_h))
    sheet.fill(BG)

    font = pygame.font.SysFont("dejavusans", 22, bold=True)
    label = font.render("D6 FUNGAL — R2", True, (230, 235, 225))
    sheet.blit(label, (PAD, (LABEL_H - label.get_height()) // 2))

    small = pygame.font.SysFont("dejavusans", 13)
    captions = ["gameplay (mid-flight)", "hero", "40px truth-read"]
    x = PAD
    for p, cap in zip(panels, captions):
        y = LABEL_H + (total_h - LABEL_H - PAD - p.get_height()) // 2
        sheet.blit(p, (x, y))
        ctext = small.render(cap, True, (170, 175, 165))
        sheet.blit(ctext, (x, LABEL_H + max(p.get_height() for p in panels) + 2))
        x += p.get_width() + PAD

    out = "docs/store_redesign/costume/zombie/design_6/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    main()
