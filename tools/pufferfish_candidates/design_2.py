"""BALLOON SPINES — design_2 (REBUILT after a RE-ROLL: R1 still read as a sun).

The fix kills the radial halo: spines sit on the TOP/BACK arc only with a CLEAN
belly, the studs are short + dark-socketed (tips never the brightest pixel), the
palette is de-golded to tan puffer-skin, the body is an EGG (not a circle), and a
big dark forked tail breaks the outline asymmetrically. Scratch only."""
import pygame

from game.parrot import _aaellipse
from tools.pufferfish_candidates._shared import (
    _new, _make_prebuilt_skin, _inflate, _shade, _eye, _radial_body,
    _tail_fin, _side_fin, _spots, _stub_spikes, _spike_field, _pouty_o,
    BCX, BCY,
)

# De-golded tan puffer skin so colour stops reading "sun".
CORE = (208, 198, 158)          # pale tan
MID  = (170, 156, 112)          # tan body
EDGE = (120, 106, 70)           # dark tan rim
BELLY = (241, 235, 214)         # cream belly
SPIKE_D = (92, 80, 50)          # dark socket (clearly darker than EDGE)
SPIKE_T = (150, 136, 96)        # DIM tip — never brighter than the body core
SPOT  = (88, 74, 46)
FIN_D = (104, 90, 56)           # dark fin (the tail must not be gold)
FIN_L = (168, 150, 102)
DARK  = (46, 38, 22)
BLUSH = (228, 150, 120)

# The SPIKY puffer: studs wrap nearly the whole body (top + sides + belly +
# back), with only the front face kept clear. Short + irregular + a dominant
# tail keep it bumpy-blowfish, not a radial sun.
_SPK = _spike_field(18, base=0.6, var=0.5, gap=(-0.7, 0.4), seed=2)


def build_balloon(wing_angle_deg):
    surf = _new()
    inf = _inflate(wing_angle_deg)
    rx = 15 + int(inf * 2)
    ry = 13 + int(inf * 1)          # EGG: wider than tall
    cx, cy = BCX, BCY
    bf = 0.92 + 0.16 * inf
    core, mid, edge = _shade(CORE, bf), _shade(MID, bf), _shade(EDGE, bf)

    # Big dark forked tail at the back — the loud anti-sun signal.
    _tail_fin(surf, cx - rx + 2, cy + 3, 11, _shade(FIN_D, bf), _shade(FIN_L, bf))
    _side_fin(surf, cx - 6, cy - 3, 4, _shade(FIN_D, bf), _shade(FIN_L, bf),
              flip=True)

    # Short dark-socketed studs on the top/back arc only (roots tuck behind body).
    spk = 4 + int(inf * 2)
    _stub_spikes(surf, cx, cy, rx, ry, spk, _shade(SPIKE_D, bf),
                 _shade(SPIKE_T, bf), _SPK)

    # Egg body + a couple of low-frequency edge bumps so the outline is lumpy
    # (puffer skin), not a clean solar ring.
    _radial_body(surf, cx, cy, rx, ry, core, mid, edge)
    for bx, by, br in ((-rx + 3, -4, 4), (-2, ry - 4, 4), (rx - 5, 2, 3)):
        _aaellipse(surf, mid, (cx + bx, cy + by), br, br)
    # Clean cream belly (NO spikes here — the strongest "not a sun" signal).
    _aaellipse(surf, _shade(BELLY, bf), (cx - 1, cy + 4), rx - 6, ry - 5)
    _spots(surf, cx, cy, rx, ry, _shade(SPOT, bf),
           [(-9, -3, 1), (-5, -6, 1), (-2, 2, 1)])

    # Near pectoral fin (front-lower).
    _side_fin(surf, cx + rx - 5, cy + 6, 5, _shade(FIN_D, bf), _shade(FIN_L, bf))

    # Big friendly face, front-loaded.
    fx, fy = cx + 2, cy - 3
    pygame.draw.circle(surf, BLUSH, (fx - 8, fy + 5), 2)
    pygame.draw.circle(surf, BLUSH, (fx + 8, fy + 5), 2)
    _eye(surf, fx - 5, fy, 4, iris=DARK)
    _eye(surf, fx + 5, fy, 4, iris=DARK)
    _pouty_o(surf, fx, fy + 7)
    return surf


build = _make_prebuilt_skin(build_balloon)
