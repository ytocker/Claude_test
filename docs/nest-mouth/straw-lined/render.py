"""straw-lined: pale straw lining inside the cup, darkening toward the centre.

The mouth interior is never flat black: a warm straw ring hugs the inside of
the rim (brightest at the edge), stepping down to a dark warm centre. The
tips show straw, not black. The empty state's parrot-shaped void sits ON the
lining, reading as the dark absence in a soft lined cup.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import _nestbase as nb
import pygame, math

_BANDS = [           # (t threshold ascending, colour)
    (0.32, (28, 18, 7)),
    (0.55, (70, 48, 20)),
    (0.78, (128, 92, 45)),
    (1.00, (188, 155, 90)),
]


def _lining(surf, cy):
    rx, ry, rw, rh, ecx, ecy, ra, rb = nb.geo(cy)
    for y in range(ry, ry + rh + 1):
        for x in range(rx, rx + rw + 1):
            t = nb.t_ell(x, y, ecx, ecy, ra, rb)
            if t >= 1.0: continue
            for th, col in _BANDS:
                if t <= th:
                    surf.set_at((x, y), col)
                    break


def _ring(surf, cy):
    rx, ry, rw, rh, ecx, ecy, ra, rb = nb.geo(cy)
    pygame.draw.arc(surf, nb._NEST_TWIG_MID,    (rx, ry, rw, rh), math.pi, 2 * math.pi, 2)
    pygame.draw.arc(surf, nb._NEST_TWIG_BRIGHT, (rx, ry, rw, rh), 0, math.pi, 2)


def _ring_restore(surf, cy, snap):
    """Ring band + a sliver of lining at the very edge come back in front."""
    rx, ry, rw, rh, ecx, ecy, ra, rb = nb.geo(cy)
    for y in range(ry, int(ecy) + 1):
        for x in range(rx, rx + rw + 1):
            if nb.t_ell(x, y, ecx, ecy, ra, rb) >= 0.86:
                surf.set_at((x, y), snap.get_at((x, y))[:3])


def draw_slot(surf, cy, alive):
    rx, ry, rw, rh, ecx, ecy, ra, rb = nb.geo(cy)
    pygame.draw.ellipse(surf, (0, 0, 0), (rx, ry, rw, rh))
    _lining(surf, cy)
    _ring(surf, cy)
    nb.sticks_weave01(surf, cy)
    snap = surf.copy()
    if alive:
        surf.blit(nb.BIRD, (nb.CX - nb.BW // 2, cy - nb.BH // 2 + 5))
    else:
        sil, bx, by = nb.make_black_sil(cy)
        surf.blit(sil, (bx, by))
    _ring_restore(surf, cy, snap)
    nb.front_chrome(surf, cy)


if __name__ == '__main__':
    nb.render_pair(draw_slot, 'docs/nest-mouth/straw-lined/pair.png')
