"""hollow-flat: the mouth interior is the flat warm hollow colour, no black.

Layers, back to front: back rim (MID arc) -> interior hollow -> parrot ->
front rim + lower weave. Empty state is simply the same crib with nothing in
it — the hollow shows in full.
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import _nestbase as nb
import pygame


def _mouth(surf, cy):
    rx, ry, rw, rh, ecx, ecy, ra, rb = nb.geo(cy)
    pygame.draw.ellipse(surf, nb._NEST_HOLLOW_COL, (rx, ry, rw, rh))
    pygame.draw.arc(surf, nb._NEST_TWIG_MID,    (rx, ry, rw, rh), math.pi, 2 * math.pi, 2)
    pygame.draw.arc(surf, nb._NEST_TWIG_BRIGHT, (rx, ry, rw, rh), 0, math.pi, 2)


def draw_slot(surf, cy, alive):
    _mouth(surf, cy)
    nb.sticks_weave01(surf, cy)
    if alive:
        surf.blit(nb.BIRD, (nb.CX - nb.BW // 2, cy - nb.BH // 2 + 5))
    nb.front_chrome(surf, cy)


if __name__ == '__main__':
    nb.render_pair(draw_slot, 'docs/nest-mouth/hollow-flat/pair.png')
