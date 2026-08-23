"""wide-mouth: a taller opening — the window onto the bird is bigger.

The rim oval grows from 34x10 to 38x14, so the lip sits lower and more of
the bird's body is visible through the opening.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import _nestbase as nb
import _model3d as m3
import pygame

_RIM = (nb.CX - 19, -6, 38, 14)

def _interior(surf, cy):
    rx, ry_off, rw, rh = _RIM
    pygame.draw.ellipse(surf, (0, 0, 0), (rx, cy + ry_off, rw, rh))

def draw_slot(surf, cy, alive):
    m3.draw_crib(surf, cy, alive, _interior, rim=_RIM)

if __name__ == '__main__':
    nb.render_pair(draw_slot, 'docs/nest-mouth/wide-mouth/pair.png')
