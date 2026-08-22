"""hollow-seat: correct occlusion + warm hollow interior instead of black.

The opening reads as a shadowed cup interior (darkest under the back rim,
warming toward the lip) rather than a void.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import _nestbase as nb
import _model3d as m3

_DEEP = (26, 17, 7)
_WARM = (64, 44, 19)

def _interior(surf, cy):
    rx, ry, rw, rh, ecx, ecy, ra, rb = nb.geo(cy)
    for y in range(ry, ry + rh + 1):
        f = (y - ry) / max(1, rh)
        col = tuple(int(a + (b - a) * f) for a, b in zip(_DEEP, _WARM))
        for x in range(rx, rx + rw + 1):
            if nb.t_ell(x, y, ecx, ecy, ra, rb) <= 1.0:
                surf.set_at((x, y), col)

def draw_slot(surf, cy, alive):
    m3.draw_crib(surf, cy, alive, _interior)

if __name__ == '__main__':
    nb.render_pair(draw_slot, 'docs/nest-mouth/hollow-seat/pair.png')
