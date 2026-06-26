"""DERPY BEAK PUFFER — design_5. Maximum charm: oversized eyes and a prominent
two-tooth puffer BEAK (a hard fish tell), a swishy little tail + tiny fins, soft
sparse spikes. Led by the goofy beaky face so it reads as a fish character, never
a sun. Scratch only."""
import pygame

from game.parrot import _aaellipse
from tools.pufferfish_candidates._shared import (
    _new, _make_prebuilt_skin, _inflate, _flap, _shade, _eye, _radial_body,
    _tail_fin, _side_fin, _spots, _stub_spikes, BCX, BCY,
)

CORE = (255, 224, 130)
MID  = (230, 178, 78)
EDGE = (194, 135, 30)
BELLY = (246, 230, 180)
SPIKE_D = (176, 116, 26)
SPIKE_T = (248, 206, 110)
SPOT  = (150, 100, 26)
FIN_D = (176, 116, 26)
FIN_L = (236, 186, 90)
DARK  = (58, 42, 18)
TEETH = (255, 243, 214)
BLUSH = (255, 168, 120)

_SPK = [(-2.7, 0.6), (-2.2, 0.8), (-1.6, 0.65), (-1.0, 0.8), (-0.5, 0.6)]


def build_derpy(wing_angle_deg):
    surf = _new()
    inf = _inflate(wing_angle_deg)
    f = _flap(wing_angle_deg)
    r = 14 + int(inf * 2)
    cx, cy = BCX, BCY
    bf = 0.92 + 0.16 * inf
    core, mid, edge = _shade(CORE, bf), _shade(MID, bf), _shade(EDGE, bf)
    fin_d, fin_l = _shade(FIN_D, bf), _shade(FIN_L, bf)

    # Swishy tail (back), sways a little with the flap.
    _tail_fin(surf, cx - r + 1, cy + 2 + int(f * 2), 8, fin_d, fin_l)
    _side_fin(surf, cx - 5, cy - 2, 4, fin_d, fin_l, flip=True)

    # Soft sparse spikes.
    spk = 4 + int(inf * 3)
    _stub_spikes(surf, cx, cy, r, r, spk, _shade(SPIKE_D, bf),
                 _shade(SPIKE_T, bf), _SPK)

    # Body + belly.
    _radial_body(surf, cx, cy, r, r, core, mid, edge)
    _aaellipse(surf, _shade(BELLY, bf), (cx - 1, cy + 5), r - 6, r - 7)
    _spots(surf, cx, cy, r, r, _shade(SPOT, bf), [(-6, 7, 1), (5, 7, 1)])

    # Near pectoral fin.
    _side_fin(surf, cx + r - 4, cy + 6, 5, fin_d, fin_l)

    # ── HERO: oversized eyes + a two-tooth beak ──
    fx, fy = cx + 1, cy - 3
    pygame.draw.circle(surf, BLUSH, (fx - 9, fy + 6), 2)
    pygame.draw.circle(surf, BLUSH, (fx + 9, fy + 6), 2)
    _eye(surf, fx - 6, fy, 5, iris=DARK)        # bigger r5 googly eyes
    _eye(surf, fx + 6, fy, 5, iris=DARK)
    # Beak: a warm-dark lip line with two pale buck-teeth below it.
    pygame.draw.line(surf, (110, 70, 40), (fx - 4, fy + 7), (fx + 4, fy + 7), 2)
    pygame.draw.rect(surf, TEETH, (fx - 3, fy + 7, 2, 3))
    pygame.draw.rect(surf, TEETH, (fx + 1, fy + 7, 2, 3))
    pygame.draw.rect(surf, (200, 170, 120), (fx - 3, fy + 9, 6, 1))
    return surf


build = _make_prebuilt_skin(build_derpy)
