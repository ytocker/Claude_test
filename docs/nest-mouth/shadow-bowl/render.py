"""shadow-bowl: the interior is a radial depth shade, not flat black.

A per-pixel elliptical gradient — near-black centre, warm hollow browns
rising toward the rim — makes the mouth read as a curved bowl catching light
at its edge. Tips show warm dark browns instead of pure black wedges. The
empty state's pure-black bird void pops against the graded bowl.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import _nestbase as nb
import pygame, math

_STOPS = [(0.0, (6, 4, 2)), (0.6, nb._NEST_HOLLOW_COL), (1.0, (95, 65, 30))]


def _shade(t):
    for (t0, c0), (t1, c1) in zip(_STOPS, _STOPS[1:]):
        if t <= t1:
            f = (t - t0) / (t1 - t0)
            return tuple(int(a + (b - a) * f) for a, b in zip(c0, c1))
    return _STOPS[-1][1]


def _bowl(surf, cy):
    rx, ry, rw, rh, ecx, ecy, ra, rb = nb.geo(cy)
    for y in range(ry, ry + rh + 1):
        for x in range(rx, rx + rw + 1):
            t = nb.t_ell(x, y, ecx, ecy, ra, rb)
            if t < 1.0:
                surf.set_at((x, y), _shade(t))


def _ring(surf, cy):
    rx, ry, rw, rh, ecx, ecy, ra, rb = nb.geo(cy)
    pygame.draw.arc(surf, nb._NEST_TWIG_MID,    (rx, ry, rw, rh), math.pi, 2 * math.pi, 2)
    pygame.draw.arc(surf, nb._NEST_TWIG_BRIGHT, (rx, ry, rw, rh), 0, math.pi, 2)


def _ring_restore(surf, cy, snap):
    rx, ry, rw, rh, ecx, ecy, ra, rb = nb.geo(cy)
    for y in range(ry, int(ecy) + 1):
        for x in range(rx, rx + rw + 1):
            if nb.t_ell(x, y, ecx, ecy, ra, rb) >= 0.86:
                surf.set_at((x, y), snap.get_at((x, y))[:3])


def draw_slot(surf, cy, alive):
    rx, ry, rw, rh, ecx, ecy, ra, rb = nb.geo(cy)
    pygame.draw.ellipse(surf, (0, 0, 0), (rx, ry, rw, rh))
    _bowl(surf, cy)
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
    nb.render_pair(draw_slot, 'docs/nest-mouth/shadow-bowl/pair.png')
