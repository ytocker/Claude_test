"""len-4: crib length step between classic-seat (D1) and short-crib (D2).
Bottom band forced BRIGHT so every length ends on the same bottom panel."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import _nestbase as nb
import _model3d as m3
import pygame

_OFFS = [2, 6, 10]
_COLS = [nb._NEST_TWIG_BRIGHT, nb._NEST_TWIG_MID, nb._NEST_TWIG_BRIGHT]
_STICKS = 12

_COURSES = [(o, c, nb.COURSES[i][2], nb.COURSES[i][3], nb.COURSES[i][4])
            for i, (o, c) in enumerate(zip(_OFFS, _COLS))]

def _interior(surf, cy):
    rx, ry, rw, rh, ecx, ecy, ra, rb = nb.geo(cy)
    pygame.draw.ellipse(surf, (0, 0, 0), (rx, ry, rw, rh))

def draw_slot(surf, cy, alive):
    m3.draw_crib(surf, cy, alive, _interior, courses=_COURSES,
                 stick_bottom=_STICKS)

if __name__ == '__main__':
    nb.render_pair(draw_slot, 'docs/nest-mouth/len-4/pair.png')
