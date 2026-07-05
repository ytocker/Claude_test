"""BLAZING SUN — design_2. A fierce, radiant sun: curved flame-tongue rays
sweeping one way around a white-hot core, with a determined face. Scratch only."""
import pygame

from game.parrot import _aaellipse
from tools.sun_candidates._shared import (
    _new, _make_prebuilt_skin, _shine, _shade, _radial_body, _flame_ring,
    _spike_ring, _sun_face, BCX, BCY,
)

CORE = (255, 246, 216)          # white-hot
MID  = (255, 176, 46)
EDGE = (196, 58, 18)            # deep red rim
FLAME_B = (255, 106, 30)        # deep flame
FLAME_T = (255, 200, 90)        # bright flame
GLOW = (255, 150, 60)


def build_blaze(wing_angle_deg):
    surf = _new()
    sh = _shine(wing_angle_deg)
    r = 13 + int(sh * 1)
    cx, cy = BCX, BCY
    bf = 0.90 + 0.20 * sh
    core, mid, edge = _shade(CORE, bf), _shade(MID, bf), _shade(EDGE, bf)
    fb, ft = _shade(FLAME_B, bf), _shade(FLAME_T, bf)

    # Full, round flame corona — a dense even ring of curved tongues (a sun, not
    # a pinwheel or a triangle): mostly RADIAL with just a hint of lean, plus a
    # short inner ring for depth. The fierceness lives in the curve + hot palette
    # + the face, NOT in a few dominant spikes.
    sweep = 0.22 + sh * 0.06
    _flame_ring(surf, cx, cy, r - 1, 12 + int(sh * 4), 14, fb, ft, sweep=sweep)
    _flame_ring(surf, cx, cy, r - 2, 7, 14, _shade(FLAME_B, bf * 0.9),
                _shade(FLAME_T, bf * 0.95), sweep=sweep, start=0.22)

    # Molten disc with a hot inner core.
    _radial_body(surf, cx, cy, r, mid, mid, edge)
    _aaellipse(surf, _shade((255, 150, 40), bf), (cx - 1, cy), r - 5, r - 5)
    _aaellipse(surf, core, (cx - 2, cy - 2), r - 8, r - 8)

    # Fierce face: thick dark angled brows + a confident grin, legible small.
    _sun_face(surf, cx, cy, eye_dx=5, eye_r=3, iris=(50, 18, 8),
              mouth="grin", brow=(96, 24, 10))
    # Thicken the brows so the scowl survives 40px.
    pygame.draw.line(surf, (96, 24, 10), (cx - 9, cy - 5), (cx - 2, cy - 2), 2)
    pygame.draw.line(surf, (96, 24, 10), (cx + 2, cy - 2), (cx + 9, cy - 5), 2)
    return surf


build = _make_prebuilt_skin(build_blaze)
