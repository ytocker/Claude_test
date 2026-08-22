"""short-crib: identical design to classic-seat, crib just shorter.

Only the first three weave courses and shorter sticks — the wall stops
higher, so more of the bird stands proud of the crib.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import _nestbase as nb
import _model3d as m3
import pygame

_COURSES = nb.COURSES[:3]
_STICK_BOTTOM = round(10 * nb._NEST_S)

def _interior(surf, cy):
    rx, ry, rw, rh, ecx, ecy, ra, rb = nb.geo(cy)
    pygame.draw.ellipse(surf, (0, 0, 0), (rx, ry, rw, rh))

def draw_slot(surf, cy, alive):
    m3.draw_crib(surf, cy, alive, _interior, courses=_COURSES,
                 stick_bottom=_STICK_BOTTOM)

if __name__ == '__main__':
    nb.render_pair(draw_slot, 'docs/nest-mouth/short-crib/pair.png')
