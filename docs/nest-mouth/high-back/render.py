"""high-back: the nest's far wall rises behind the bird; the opening is a slit.

A woven back wall fills the mouth's upper curve (plus a 2-row crown above the
oval), so the visible interior is only a short front slit. The tips vanish
where the wall bands converge. The bird sits IN FRONT of the far wall and
behind the front rim — a true 3D sandwich.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import _nestbase as nb
import pygame, math

WALL_ROWS = 4    # wall thickness measured down from the oval's top edge
CROWN = 2        # extra rows rising above the oval silhouette

_WALL = [nb._NEST_TWIG_MID, nb._NEST_TWIG_BRIGHT, nb._NEST_TWIG_MID, nb._NEST_TWIG_DARK]


def _y_top(px, ecx, ecy, ra, rb):
    nx = (px - ecx) / ra
    if abs(nx) > 1.0: return None
    return ecy - rb * math.sqrt(1.0 - nx * nx)


def _wall(surf, cy):
    rx, ry, rw, rh, ecx, ecy, ra, rb = nb.geo(cy)
    for x in range(rx, rx + rw + 1):
        yt = _y_top(x, ecx, ecy, ra, rb)
        if yt is None: continue
        yt = int(yt)
        for i in range(-CROWN, WALL_ROWS):
            y = yt + i
            col = _WALL[i % 4] if i >= 0 else nb._NEST_TWIG_DARK
            surf.set_at((x, y), col)


def _front_rim(surf, cy):
    rx, ry, rw, rh, ecx, ecy, ra, rb = nb.geo(cy)
    pygame.draw.arc(surf, nb._NEST_TWIG_BRIGHT, (rx, ry, rw, rh), 0, math.pi, 2)


def draw_slot(surf, cy, alive):
    rx, ry, rw, rh, ecx, ecy, ra, rb = nb.geo(cy)
    pygame.draw.ellipse(surf, (0, 0, 0), (rx, ry, rw, rh))
    _wall(surf, cy)
    _front_rim(surf, cy)
    nb.sticks_weave01(surf, cy)
    snap = surf.copy()
    if alive:
        surf.blit(nb.BIRD, (nb.CX - nb.BW // 2, cy - nb.BH // 2 + 5))
    else:
        sil, bx, by = nb.make_black_sil(cy)
        surf.blit(sil, (bx, by))
        # The void is inside the cup — the far wall stays visible above it.
        for x in range(rx, rx + rw + 1):
            yt = _y_top(x, ecx, ecy, ra, rb)
            if yt is None: continue
            yt = int(yt)
            for i in range(-CROWN, WALL_ROWS):
                surf.set_at((x, yt + i), snap.get_at((x, yt + i))[:3])
    nb.front_chrome(surf, cy)


if __name__ == '__main__':
    nb.render_pair(draw_slot, 'docs/nest-mouth/high-back/pair.png')
