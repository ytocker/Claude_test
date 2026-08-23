"""tucked-tips: the oval tips are woven shut; only a central opening stays dark.

The left/right thirds of the mouth become horizontal wicker courses (the cup's
own weave folding over its ends). The black interior survives only as a
central slot the width of the bird. Tips are always woven — in front of the
bird — so no black wedge can appear beside it.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import _nestbase as nb
import pygame, math

SLOT_HW = 8   # half-width (px) of the central dark opening

_ROWS = [nb._NEST_COURSE_TOP, nb._NEST_TWIG_BRIGHT, nb._NEST_TWIG_MID, nb._NEST_COURSE_BOT]


def _tips(surf, cy):
    rx, ry, rw, rh, ecx, ecy, ra, rb = nb.geo(cy)
    for y in range(ry, ry + rh + 1):
        for x in range(rx, rx + rw + 1):
            if abs(x - ecx) <= SLOT_HW: continue
            if nb.t_ell(x, y, ecx, ecy, ra, rb) < 1.02:
                surf.set_at((x, y), _ROWS[(y - ry) % 4])


def _ring(surf, cy):
    rx, ry, rw, rh, ecx, ecy, ra, rb = nb.geo(cy)
    pygame.draw.arc(surf, nb._NEST_TWIG_MID,    (rx, ry, rw, rh), math.pi, 2 * math.pi, 2)
    pygame.draw.arc(surf, nb._NEST_TWIG_BRIGHT, (rx, ry, rw, rh), 0, math.pi, 2)


def draw_slot(surf, cy, alive):
    rx, ry, rw, rh, ecx, ecy, ra, rb = nb.geo(cy)
    pygame.draw.ellipse(surf, (0, 0, 0), (rx, ry, rw, rh))
    _tips(surf, cy)
    _ring(surf, cy)
    nb.sticks_weave01(surf, cy)
    if alive:
        surf.blit(nb.BIRD, (nb.CX - nb.BW // 2, cy - nb.BH // 2 + 5))
    else:
        sil, bx, by = nb.make_black_sil(cy)
        surf.blit(sil, (bx, by))
    # Woven tips + ring fold back in front of the bird.
    _tips(surf, cy)
    _ring(surf, cy)
    nb.front_chrome(surf, cy)


if __name__ == '__main__':
    nb.render_pair(draw_slot, 'docs/nest-mouth/tucked-tips/pair.png')
