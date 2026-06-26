"""AQUA PUFFER — design_4. Kill the sun with COLOUR: a cute teal/aqua balloon
puffer with a coral-pink belly, a tail fin, and rising bubbles. A cool aqua + an
underwater bubble cue read unmistakably as a fish, never a sun. Scratch only."""
import pygame

from game.parrot import _aaellipse
from tools.pufferfish_candidates._shared import (
    _new, _make_prebuilt_skin, _inflate, _flap, _shade, _eye, _radial_body,
    _tail_fin, _side_fin, _spots, _stub_spikes, _pouty_o, BCX, BCY,
)

CORE = (127, 224, 232)          # light aqua core
MID  = (57, 182, 196)           # aqua body
EDGE = (30, 124, 138)           # deep teal rim
BELLY = (255, 200, 188)         # coral-pink belly (cute contrast)
SPIKE_D = (30, 124, 138)
SPIKE_T = (170, 236, 242)
SPOT  = (30, 110, 124)
FIN_D = (24, 104, 120)
FIN_L = (96, 200, 212)
DARK  = (24, 54, 60)
BUBBLE = (234, 251, 255)

# Soft rounded short spines — upper body PLUS a couple lower on the back flank
# so the bumps wrap the ball (the "spines all over a round body" puffer cue).
_SPK = [(-2.7, 0.7), (-2.2, 0.9), (-1.7, 0.75), (-1.2, 0.95), (-0.7, 0.8),
        (2.7, 0.6), (2.3, 0.7)]


def build_aqua(wing_angle_deg):
    surf = _new()
    inf = _inflate(wing_angle_deg)
    f = _flap(wing_angle_deg)
    r = 14 + int(inf * 2)
    cx, cy = BCX, BCY
    bf = 0.92 + 0.16 * inf
    core, mid, edge = _shade(CORE, bf), _shade(MID, bf), _shade(EDGE, bf)
    fin_d, fin_l = _shade(FIN_D, bf), _shade(FIN_L, bf)

    # Two bubbles drifting up off the back, kept clear of the body silhouette so
    # at least one survives the 40px read — the aquatic tell.
    drift = int(f * 3)
    for dx, dy, br in ((-r - 5, -8, 3), (-r - 8, -16, 2)):
        bx, by = cx + dx, cy + dy - drift
        pygame.draw.circle(surf, BUBBLE, (bx, by), br)
        pygame.draw.circle(surf, (200, 240, 248), (bx, by), br, 1)

    # Tail fin (back) + far pectoral.
    _tail_fin(surf, cx - r + 1, cy + 1, 9, fin_d, fin_l)
    _side_fin(surf, cx - 5, cy - 2, 4, fin_d, fin_l, flip=True)

    # Soft short spines.
    spk = 4 + int(inf * 3)
    _stub_spikes(surf, cx, cy, r, r, spk, _shade(SPIKE_D, bf),
                 _shade(SPIKE_T, bf), _SPK)

    # Aqua ball + coral belly.
    _radial_body(surf, cx, cy, r, r, core, mid, edge)
    _aaellipse(surf, _shade(BELLY, bf), (cx - 1, cy + 4), r - 6, r - 7)
    _spots(surf, cx, cy, r, r, _shade(SPOT, bf),
           [(-6, -2, 1), (2, -5, 1), (6, 2, 1)])

    # Near pectoral fin (front-lower), nudged down with a dark edge so it breaks
    # the silhouette instead of sinking into the coral belly.
    _side_fin(surf, cx + r - 3, cy + 6 + int(inf), 5, fin_d, fin_l)
    pygame.draw.line(surf, fin_d, (cx + r - 3, cy + 6), (cx + r + 2, cy + 7), 1)

    # Big sparkly face.
    fx, fy = cx + 1, cy - 3
    _eye(surf, fx - 6, fy, 4, iris=DARK)
    _eye(surf, fx + 6, fy, 4, iris=DARK)
    _pouty_o(surf, fx, fy + 8, lip=(196, 92, 96))
    return surf


build = _make_prebuilt_skin(build_aqua)
