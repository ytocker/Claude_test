"""BALLOON SPINES — design_2. The iconic spiky blowfish: the whole ball studded
with short blunt cone spines on a STAGGERED scattered grid (never a clean radial
fan), plus a small tail nub so it reads fish, not sun. Scratch only."""
import math
import pygame

from game.parrot import _aaellipse
from tools.pufferfish_candidates._shared import (
    _new, _make_prebuilt_skin, _inflate, _shade, _eye, _radial_body,
    _tail_fin, _side_fin, _spots, _stub_spikes, _pouty_o, BCX, BCY,
)

CORE = (236, 196, 110)
MID  = (217, 162, 74)
EDGE = (166, 112, 30)
BELLY = (243, 226, 180)
SPIKE_D = (150, 96, 22)
SPIKE_T = (250, 224, 150)
SPOT  = (124, 84, 26)
FIN_D = (150, 96, 22)
FIN_L = (210, 160, 80)
DARK  = (44, 30, 12)
BLUSH = (255, 170, 120)

# ~18 spines on a jittered ring set (two staggered rings, varied lengths) — the
# scatter is what kills the radial-sun pattern. Fixed list → stable frames.
_RING = []
for _k in range(11):
    _a = (-math.pi) + (2 * math.pi) * _k / 11
    _RING.append((_a, 0.75 + 0.5 * ((_k * 7) % 5) / 4.0))
for _k in range(7):
    _a = (-math.pi) + (2 * math.pi) * (_k + 0.5) / 7
    _RING.append((_a, 0.55 + 0.4 * ((_k * 3) % 4) / 3.0))


def build_balloon(wing_angle_deg):
    surf = _new()
    inf = _inflate(wing_angle_deg)
    r = 14 + int(inf * 2)
    cx, cy = BCX, BCY
    bf = 0.92 + 0.16 * inf
    core, mid, edge = _shade(CORE, bf), _shade(MID, bf), _shade(EDGE, bf)

    # Small fan tail low at the back.
    _tail_fin(surf, cx - r + 1, cy + 5, 7, _shade(FIN_D, bf), _shade(FIN_L, bf))
    # Tiny pectoral nub.
    _side_fin(surf, cx + r - 3, cy + 6, 4, _shade(FIN_D, bf), _shade(FIN_L, bf))

    # All-over short studs (staggered) BEHIND the body so roots tuck under.
    spk = 5 + int(inf * 4)
    _stub_spikes(surf, cx, cy, r, r, spk, _shade(SPIKE_D, bf),
                 _shade(SPIKE_T, bf), _RING)

    # Ball + belly.
    _radial_body(surf, cx, cy, r, r, core, mid, edge)
    _aaellipse(surf, _shade(BELLY, bf), (cx - 1, cy + 4), r - 6, r - 7)
    # Dark dots scattered between studs (extra blowfish texture).
    _spots(surf, cx, cy, r, r, _shade(SPOT, bf),
           [(-5, -3, 1), (3, -5, 1), (7, 1, 1), (-7, 3, 1), (1, 6, 1)])

    # Big friendly face.
    fx, fy = cx + 1, cy - 3
    pygame.draw.circle(surf, BLUSH, (fx - 8, fy + 5), 2)
    pygame.draw.circle(surf, BLUSH, (fx + 8, fy + 5), 2)
    _eye(surf, fx - 6, fy, 4, iris=DARK)
    _eye(surf, fx + 6, fy, 4, iris=DARK)
    _pouty_o(surf, fx, fy + 8)
    return surf


build = _make_prebuilt_skin(build_balloon)
