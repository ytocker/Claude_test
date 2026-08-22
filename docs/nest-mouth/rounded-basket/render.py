"""rounded-basket: wall courses bow parallel to the lip — a rounder basket.

Correct occlusion + reshaped front wall: every course's sag is doubled so the
bands follow the bowl curvature instead of running nearly straight, making
the crib read as a rounded basket under the bird.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import _nestbase as nb
import _model3d as m3

_COURSES = [(off, col, x1, x2, sag + 2) for (off, col, x1, x2, sag) in nb.COURSES]

def _interior(surf, cy):
    rx, ry, rw, rh, ecx, ecy, ra, rb = nb.geo(cy)
    import pygame
    pygame.draw.ellipse(surf, nb._NEST_HOLLOW_COL, (rx, ry, rw, rh))

def draw_slot(surf, cy, alive):
    m3.draw_crib(surf, cy, alive, _interior, courses=_COURSES)

if __name__ == '__main__':
    nb.render_pair(draw_slot, 'docs/nest-mouth/rounded-basket/pair.png')
