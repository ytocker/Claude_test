"""mid-crib-c: crib length between classic-seat and short-crib — 3 courses, sticks to r(12) — a touch taller than short-crib."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import _nestbase as nb
import _model3d as m3
import pygame

_COURSES = nb.COURSES[:3]
_STICK_BOTTOM = round(12 * nb._NEST_S)

def _interior(surf, cy):
    rx, ry, rw, rh, ecx, ecy, ra, rb = nb.geo(cy)
    pygame.draw.ellipse(surf, (0, 0, 0), (rx, ry, rw, rh))

def draw_slot(surf, cy, alive):
    m3.draw_crib(surf, cy, alive, _interior, courses=_COURSES,
                 stick_bottom=_STICK_BOTTOM)

if __name__ == '__main__':
    nb.render_pair(draw_slot, 'docs/nest-mouth/mid-crib-c/pair.png')
