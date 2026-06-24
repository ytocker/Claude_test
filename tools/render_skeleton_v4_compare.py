"""v4 SKELETON deliverable: ORIGINAL parrot + the 5 x-ray styles, each Pip
mid-flight in a real gameplay scene, side by side.

Scratch/exploration only — imports the candidate builders from
tools/skeleton_candidates/, touches no production art.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from game import parrot
from tools import ninja_render as NR
from tools.skeleton_candidates import (
    v4_design_1, v4_design_2, v4_design_3, v4_design_4, v4_design_5,
)

# Original live macaw as a callable source for the harness.
def _original(frame_idx, tilt):
    return parrot.get_parrot(frame_idx, tilt)

COLUMNS = [
    ("ORIGINAL", "Pip (reference)", _original),
    ("DESIGN 1", "RADIOGRAPH", v4_design_1.build),
    ("DESIGN 2", "BOLD CARTOON", v4_design_2.build),
    ("DESIGN 3", "NEON", v4_design_3.build),
    ("DESIGN 4", "IVORY ANATOMICAL", v4_design_4.build),
    ("DESIGN 5", "ETCHED WOODCUT", v4_design_5.build),
]

PANEL_W, PANEL_H = 200, 356
PAD = 14
TOP = 52
BOT = 40
BG = (32, 34, 46)
N = len(COLUMNS)


def _font(sz, bold=False):
    return pygame.font.SysFont("Arial,DejaVu Sans", sz, bold=bold)


def main():
    cols_w = N * PANEL_W + (N + 1) * PAD
    out = pygame.Surface((cols_w, TOP + PANEL_H + BOT))
    out.fill(BG)
    title = _font(22, bold=True).render(
        "SKELETON v4 — x-ray of the ORIGINAL Pip, full skeleton + dominant beak bone",
        True, (236, 238, 246))
    out.blit(title, (PAD, 16))

    f_tag = _font(13, bold=True)
    f_sub = _font(12)
    for i, (tag, sub, src) in enumerate(COLUMNS):
        x = PAD + i * (PANEL_W + PAD)
        panel = NR.gameplay_panel(src, PANEL_W, PANEL_H)
        out.blit(panel, (x, TOP))
        col = (150, 210, 255) if i else (255, 220, 150)
        out.blit(f_tag.render(tag, True, col), (x, TOP + PANEL_H + 6))
        out.blit(f_sub.render(sub, True, (200, 204, 216)),
                 (x, TOP + PANEL_H + 22))

    dst = "docs/store_redesign/costume/skeleton/v4/final_comparison.png"
    pygame.image.save(out, dst)
    print("SAVED", dst, out.get_size())


if __name__ == "__main__":
    main()
