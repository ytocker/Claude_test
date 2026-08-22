"""hollow-shade: hollow with a vertical depth gradient — dark under the back
rim, warming toward the front lip.

Same 3-layer sandwich as hollow-flat; only the interior shading differs: the
far inside wall (just under the back rim) sits in the rim's shadow, and the
interior brightens as it curves toward the lit front lip.
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import _nestbase as nb
import pygame

_DEEP = (32, 21, 9)
_LIT  = (78, 54, 24)


def _mouth(surf, cy):
    rx, ry, rw, rh, ecx, ecy, ra, rb = nb.geo(cy)
    for y in range(ry, ry + rh + 1):
        f = (y - ry) / max(1, rh)
        col = tuple(int(a + (b - a) * f) for a, b in zip(_DEEP, _LIT))
        for x in range(rx, rx + rw + 1):
            if nb.t_ell(x, y, ecx, ecy, ra, rb) <= 1.0:
                surf.set_at((x, y), col)
    pygame.draw.arc(surf, nb._NEST_TWIG_MID,    (rx, ry, rw, rh), math.pi, 2 * math.pi, 2)
    pygame.draw.arc(surf, nb._NEST_TWIG_BRIGHT, (rx, ry, rw, rh), 0, math.pi, 2)


def draw_slot(surf, cy, alive):
    _mouth(surf, cy)
    nb.sticks_weave01(surf, cy)
    if alive:
        surf.blit(nb.BIRD, (nb.CX - nb.BW // 2, cy - nb.BH // 2 + 5))
    nb.front_chrome(surf, cy)


if __name__ == '__main__':
    nb.render_pair(draw_slot, 'docs/nest-mouth/hollow-shade/pair.png')
