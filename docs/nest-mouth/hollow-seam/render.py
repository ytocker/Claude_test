"""hollow-seam: flat hollow + crisp 1px pixel-art depth cues.

Same 3-layer sandwich; the interior is the flat hollow colour with two
restrained contact cues: a 1px dark seam hugging the inside of the back rim
(its cast shadow) and a 1px lighter catch just inside the front lip.
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import _nestbase as nb
import pygame

_SEAM  = (28, 18, 8)
_CATCH = (86, 60, 27)


def _mouth(surf, cy):
    rx, ry, rw, rh, ecx, ecy, ra, rb = nb.geo(cy)
    pygame.draw.ellipse(surf, nb._NEST_HOLLOW_COL, (rx, ry, rw, rh))
    # Contact cues track the oval curvature 2px inside each rim.
    for x in range(rx + 2, rx + rw - 1):
        nx = (x - ecx) / ra
        if abs(nx) >= 0.98: continue
        dy = rb * math.sqrt(1.0 - nx * nx)
        surf.set_at((x, int(ecy - dy) + 2), _SEAM)
        surf.set_at((x, int(ecy + dy) - 2), _CATCH)
    pygame.draw.arc(surf, nb._NEST_TWIG_MID,    (rx, ry, rw, rh), math.pi, 2 * math.pi, 2)
    pygame.draw.arc(surf, nb._NEST_TWIG_BRIGHT, (rx, ry, rw, rh), 0, math.pi, 2)


def draw_slot(surf, cy, alive):
    _mouth(surf, cy)
    nb.sticks_weave01(surf, cy)
    if alive:
        surf.blit(nb.BIRD, (nb.CX - nb.BW // 2, cy - nb.BH // 2 + 5))
    nb.front_chrome(surf, cy)


if __name__ == '__main__':
    nb.render_pair(draw_slot, 'docs/nest-mouth/hollow-seam/pair.png')
