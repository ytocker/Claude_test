"""Render a quick sheet of all 5 red-panda back candidates + the original.

Usage:
    PYTHONPATH=. SDL_VIDEODRIVER=dummy python tools/red_panda_candidates/_render_all.py
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import sys
import pygame
pygame.init()

from tools.ninja_render import gameplay_panel, hero_panel
from game.animal_red_panda import get_red_panda

from tools.red_panda_candidates import design_1, design_2, design_3, design_4, design_5

SOURCES = [
    ("ORIGINAL",  get_red_panda),
    ("1 TAPERED",  design_1.build),
    ("2 TAPER-BND", design_2.build),
    ("3 BANDED",   design_3.build),
    ("4 DROOP",    design_4.build),
    ("5 RUMP ANC", design_5.build),
]

PW, PH   = 160, 230    # portrait panel matching game's aspect ratio
HERO_BOX = 120
PAD      = 8
LABEL_H  = 20
STRIP_W  = (PW + PAD) * len(SOURCES) + PAD
STRIP_H  = PAD + HERO_BOX + PAD + PH + LABEL_H + PAD
FONT_SZ  = 14

pygame.font.init()
font = pygame.font.SysFont("monospace", FONT_SZ, bold=True)


def render(label, source, frame_idx, tilt):
    gp = gameplay_panel(source, PW, PH, frame_idx=frame_idx, tilt=tilt)
    hp = hero_panel(source, HERO_BOX, frame_idx=frame_idx)
    col = pygame.Surface((PW, PAD + HERO_BOX + PAD + PH + LABEL_H + PAD), pygame.SRCALPHA)
    col.fill((18, 16, 28))
    col.blit(hp, ((PW - HERO_BOX) // 2, PAD))
    col.blit(gp, (0, PAD + HERO_BOX + PAD))
    txt = font.render(label, True, (255, 240, 200))
    col.blit(txt, ((PW - txt.get_width()) // 2, PAD + HERO_BOX + PAD + PH + 4))
    return col


def build_strip(frame_idx=2, tilt=10.0):
    strip = pygame.Surface((STRIP_W, STRIP_H), pygame.SRCALPHA)
    strip.fill((12, 10, 20))
    for i, (label, src) in enumerate(SOURCES):
        col = render(label, src, frame_idx, tilt)
        strip.blit(col, (PAD + i * (PW + PAD), 0))
    return strip


out_dir = "docs/store_redesign/animal/red_panda"
os.makedirs(out_dir, exist_ok=True)

strip = build_strip(frame_idx=2, tilt=10.0)
out_path = os.path.join(out_dir, "back_r1.png")
pygame.image.save(strip, out_path)
print(f"Saved: {out_path}  ({strip.get_width()}×{strip.get_height()})")

# Also render a 40px truth-read row.
TRUTH_BOX = 40
truth_w   = (TRUTH_BOX + PAD) * len(SOURCES) + PAD
truth     = pygame.Surface((truth_w, TRUTH_BOX + PAD * 2), pygame.SRCALPHA)
truth.fill((12, 10, 20))
for i, (label, src) in enumerate(SOURCES):
    fr = src(2, 10.0)
    small = pygame.transform.scale(fr, (TRUTH_BOX, TRUTH_BOX))
    truth.blit(small, (PAD + i * (TRUTH_BOX + PAD), PAD))
truth_path = os.path.join(out_dir, "back_r1_40px.png")
pygame.image.save(truth, truth_path)
print(f"Saved: {truth_path}")
