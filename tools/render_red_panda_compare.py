"""Final comparison figure: ORIGINAL production red panda + 5 full redesigns.

Each column: pip mid-flight in a real gameplay scene (day), labeled.
Saves to docs/store_redesign/animal/red_panda/final_comparison.png.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.font.init()

from tools.ninja_render import gameplay_panel, hero_panel
from game.animal_red_panda import get_red_panda

from tools.red_panda_candidates import design_1, design_2, design_3, design_4, design_5

SOURCES = [
    ("ORIGINAL",         get_red_panda),
    ("1 EMBER\nSCOUT",   design_1.build),
    ("2 DUSK\nBANDIT",   design_2.build),
    ("3 AUTUMN\nMONK",   design_3.build),
    ("4 MAPLE\nSPRITE",  design_4.build),
    ("5 CINDER\nGUARDIAN", design_5.build),
]

PW, PH   = 180, 260
HERO_BOX = 130
PAD      = 12
LABEL_H  = 36
BG       = (14, 12, 22)

TOTAL_W = PAD + len(SOURCES) * (PW + PAD)
TOTAL_H = PAD + HERO_BOX + PAD + PH + PAD + LABEL_H

font_lg = pygame.font.SysFont("dejavusans", 13, bold=True)


def _label(surf, text, rect_x, rect_w, y, color=(240, 230, 210)):
    lines = text.split("\n")
    total_h = sum(font_lg.get_height() for _ in lines)
    cy = y + (LABEL_H - total_h) // 2
    for line in lines:
        txt = font_lg.render(line, True, (8, 6, 16))
        surf.blit(txt, (rect_x + (rect_w - txt.get_width()) // 2 + 1, cy + 1))
        txt = font_lg.render(line, True, color)
        surf.blit(txt, (rect_x + (rect_w - txt.get_width()) // 2, cy))
        cy += font_lg.get_height()


canvas = pygame.Surface((TOTAL_W, TOTAL_H))
canvas.fill(BG)

pygame.draw.line(canvas, (40, 36, 56), (0, PAD + HERO_BOX + PAD + PH + PAD - 2),
                 (TOTAL_W, PAD + HERO_BOX + PAD + PH + PAD - 2), 1)

for i, (label, src) in enumerate(SOURCES):
    x = PAD + i * (PW + PAD)
    hero = hero_panel(src, HERO_BOX, frame_idx=2, tilt=0.0, bg=(26, 22, 38))
    gplay = gameplay_panel(src, PW, PH, frame_idx=2, tilt=10.0)
    canvas.blit(hero, (x + (PW - HERO_BOX) // 2, PAD))
    canvas.blit(gplay, (x, PAD + HERO_BOX + PAD))
    _label(canvas, label, x, PW, PAD + HERO_BOX + PAD + PH + PAD)
    if i > 0:
        pygame.draw.line(canvas, (40, 36, 56),
                         (x - PAD // 2, PAD), (x - PAD // 2, TOTAL_H - PAD), 1)

out = "docs/store_redesign/animal/red_panda/final_comparison.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"Saved {out}  ({canvas.get_width()}x{canvas.get_height()})")
