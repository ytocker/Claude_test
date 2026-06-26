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
EDGE = (118, 138, 74)           # olive rim (lifted/cooled so it holds at night)
BELLY = (244, 246, 236)
SPIKE_D = (96, 112, 48)
SPIKE_T = (180, 196, 120)
SPOT  = (46, 58, 34)
FIN_D = (150, 120, 54)          # warm olive-tan fins
FIN_L = (224, 196, 120)
DARK  = (40, 46, 28)            # dark olive iris (still lets the white win)

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
    _tail_fin(surf, cx - rx + 1, cy, 10, fin_d, fin_l)
    pygame.draw.polygon(surf, fin_d, [(cx - 4, cy - ry + 1), (cx - 11, cy - ry - 4),
                                      (cx - 12, cy - ry + 2)])         # dorsal
    pygame.draw.polygon(surf, fin_d, [(cx - 4, cy + ry - 1), (cx - 11, cy + ry + 4),
                                      (cx - 12, cy + ry - 2)])         # anal

    # Sparse tiny spines (this puffer is barely inflated).
    spk = 4 + int(inf * 2)
    _stub_spikes(surf, cx, cy, rx, ry, spk, _shade(SPIKE_D, bf),
                 _shade(SPIKE_T, bf), _SPK)

    # Oval olive body + a wide white belly (a bright anchor mass at 40px / night).
    _radial_body(surf, cx, cy, rx, ry, core, mid, edge)
    _aaellipse(surf, _shade(BELLY, bf), (cx, cy + 4), rx - 6, ry - 4)
    # Bold fugu spots — kept to the BACK third only so they read as pattern, not
    # blemishes on the face.
    _spots(surf, cx, cy, rx, ry, _shade(SPOT, bf),
           [(-11, -3, 2), (-9, 2, 1), (-6, -5, 2), (-4, 3, 1)])

    # ONE clear near pectoral fin (front-lower), clear of the belly.
    _side_fin(surf, cx + rx - 6, cy + 6, 5, fin_d, fin_l)

    # Forward face: big shiny eyes (brought closer) + a small defined pouty mouth.
    fx, fy = cx + 4, cy - 3
    _eye(surf, fx - 4, fy, 4, iris=DARK)
    _eye(surf, fx + 4, fy, 4, iris=DARK)
    _pouty_o(surf, fx, fy + 7, lip=(70, 58, 36))
    return surf


build = _make_prebuilt_skin(build_fugu)
