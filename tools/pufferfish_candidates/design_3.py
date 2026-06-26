"""FUGU TORPEDO — design_3. The realistic fix: a less-inflated, slightly OVAL
body (longer front-to-back than tall) with full fish fins (tail + dorsal + anal
+ pectoral), sparse tiny spines, classic olive fugu colouring and bold spots.
The non-circular silhouette alone defeats the sun read. Scratch only."""
import math
import pygame

from game.parrot import _aaellipse
from tools.pufferfish_candidates._shared import (
    _new, _make_prebuilt_skin, _inflate, _shade, _eye, _radial_body,
    _tail_fin, _side_fin, _spots, _stub_spikes, _pouty_o, BCX, BCY,
)

CORE = (201, 210, 154)          # pale olive flank
MID  = (143, 162, 78)           # olive back
EDGE = (96, 112, 48)            # deep olive rim
BELLY = (244, 246, 236)
SPIKE_D = (96, 112, 48)
SPIKE_T = (180, 196, 120)
SPOT  = (46, 58, 34)
FIN_D = (150, 120, 54)          # warm olive-tan fins
FIN_L = (224, 196, 120)
DARK  = (32, 40, 24)

# Sparse, tiny spines on the upper back only.
_SPK = [(-2.6, 0.5), (-2.1, 0.6), (-1.6, 0.55), (-1.1, 0.5)]


def build_fugu(wing_angle_deg):
    surf = _new()
    inf = _inflate(wing_angle_deg)
    rx = 16 + int(inf * 2)          # OVAL: wider than tall
    ry = 12 + int(inf * 1)
    cx, cy = BCX, BCY
    bf = 0.94 + 0.12 * inf
    core, mid, edge = _shade(CORE, bf), _shade(MID, bf), _shade(EDGE, bf)
    fin_d, fin_l = _shade(FIN_D, bf), _shade(FIN_L, bf)

    # Tail fin (back), dorsal (top-back), anal (bottom-back) — full fish set.
    _tail_fin(surf, cx - rx + 1, cy, 9, fin_d, fin_l)
    pygame.draw.polygon(surf, fin_d, [(cx - 4, cy - ry + 1), (cx - 11, cy - ry - 4),
                                      (cx - 12, cy - ry + 2)])         # dorsal
    pygame.draw.polygon(surf, fin_d, [(cx - 4, cy + ry - 1), (cx - 11, cy + ry + 4),
                                      (cx - 12, cy + ry - 2)])         # anal
    _side_fin(surf, cx - 7, cy - 1, 4, fin_d, fin_l, flip=True)        # far pectoral

    # Sparse tiny spines (this puffer is barely inflated).
    spk = 4 + int(inf * 2)
    _stub_spikes(surf, cx, cy, rx, ry, spk, _shade(SPIKE_D, bf),
                 _shade(SPIKE_T, bf), _SPK)

    # Oval olive body + white belly.
    _radial_body(surf, cx, cy, rx, ry, core, mid, edge)
    _aaellipse(surf, _shade(BELLY, bf), (cx, cy + 4), rx - 7, ry - 5)
    # Bold fugu spots across the back.
    _spots(surf, cx, cy, rx, ry, _shade(SPOT, bf),
           [(-8, -4, 2), (-2, -6, 1), (4, -4, 2), (9, -1, 1), (-5, 1, 1)])

    # Near pectoral fin (front-lower).
    _side_fin(surf, cx + rx - 6, cy + 5, 5, fin_d, fin_l)

    # Forward face: eyes + a small beaky mouth (fugu has a beak, not a big O).
    fx, fy = cx + 4, cy - 3
    _eye(surf, fx - 5, fy, 4, iris=DARK)
    _eye(surf, fx + 4, fy, 4, iris=DARK)
    pygame.draw.line(surf, (60, 50, 30), (fx - 2, fy + 7), (fx + 4, fy + 7), 2)
    pygame.draw.line(surf, (90, 76, 48), (fx, fy + 6), (fx, fy + 9), 1)
    return surf


build = _make_prebuilt_skin(build_fugu)
