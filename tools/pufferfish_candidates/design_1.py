"""FINNED PUFFER — design_1. The literal fix: keep the golden inflated ball but
make it unmistakably a fish with a fan TAIL fin, pectoral side fins, and short
SCATTERED stub spikes (not a radial sun-halo). Scratch only."""
import pygame

from game.parrot import _aaellipse
from tools.pufferfish_candidates._shared import (
    _new, _make_prebuilt_skin, _inflate, _shade, _eye, _radial_body,
    _tail_fin, _side_fin, _spots, _stub_spikes, _spike_field, _pouty_o,
    BCX, BCY,
)

CORE = (255, 226, 132)
MID  = (232, 194, 78)
EDGE = (200, 146, 46)
BELLY = (246, 230, 176)
SPIKE_D = (182, 120, 28)
SPIKE_T = (248, 206, 110)
SPOT  = (160, 104, 26)
FIN_D = (44, 122, 140)          # teal fins so they read OFF the gold body
FIN_L = (111, 183, 201)
DARK  = (52, 36, 14)
BLUSH = (255, 168, 120)

# Stubs wrapping most of the body (top + sides + lower-back) with a clear gap
# over the front face — short + uneven so they read as bumpy puffer skin.
_SPK = _spike_field(14, base=0.55, var=0.45, gap=(-0.7, 0.5), seed=1)


def build_finned(wing_angle_deg):
    surf = _new()
    inf = _inflate(wing_angle_deg)
    r = 14 + int(inf * 2)
    cx, cy = BCX, BCY
    bf = 0.92 + 0.16 * inf
    core, mid, edge = _shade(CORE, bf), _shade(MID, bf), _shade(EDGE, bf)
    fin_d, fin_l = _shade(FIN_D, bf), _shade(FIN_L, bf)

    # BIG forked tail fin at the BACK-left — the loudest anti-sun signal, so it
    # must win the silhouette (drawn first so the body overlaps its root).
    _tail_fin(surf, cx - r + 2, cy + 1, 12, fin_d, fin_l)

    # Short blunt stubs wrapping the body (anti-sun: short + irregular + face gap).
    spk = 5 + int(inf * 2)
    _stub_spikes(surf, cx, cy, r, r - 2, spk, _shade(SPIKE_D, bf),
                 _shade(SPIKE_T, bf), _SPK)

    # Gold body as a gentle horizontal OVAL (rx>ry) — reads as an inflated fish
    # belly, not a celestial disc.
    _radial_body(surf, cx, cy, r, r - 2, core, mid, edge)
    _aaellipse(surf, _shade(BELLY, bf), (cx - 1, cy + 3), r - 6, r - 7)
    _spots(surf, cx, cy, r, r, _shade(SPOT, bf),
           [(-6, 5, 1), (0, 7, 1), (6, 4, 1)])

    # ONE clear near pectoral fin (front-lower) with a rib, flicks with the puff.
    _side_fin(surf, cx + r - 3, cy + 5 + int(inf), 6, fin_d, fin_l)
    pygame.draw.line(surf, fin_d, (cx + r - 3, cy + 5), (cx + r + 2, cy + 6), 1)

    # Forward face: two eyes + blush + pouty O.
    fx, fy = cx + 1, cy - 3
    pygame.draw.circle(surf, BLUSH, (fx - 8, fy + 5), 2)
    pygame.draw.circle(surf, BLUSH, (fx + 8, fy + 5), 2)
    _eye(surf, fx - 6, fy, 4, iris=DARK)
    _eye(surf, fx + 6, fy, 4, iris=DARK)
    _pouty_o(surf, fx, fy + 8)
    return surf


build = _make_prebuilt_skin(build_finned)
