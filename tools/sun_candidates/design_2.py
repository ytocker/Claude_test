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

    # Soft outer glow halo (translucent) so it reads as emitting light.
    glow = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
    pygame.draw.circle(glow, (*GLOW, 60), (cx, cy), r + 13 + int(sh * 3))
    pygame.draw.circle(glow, (*GLOW, 70), (cx, cy), r + 8)
    surf.blit(glow, (0, 0))

    # Curved flame corona: a long outer ring + a short inner ring, same sweep.
    sweep = 0.55 + sh * 0.2
    _flame_ring(surf, cx, cy, r - 1, 11 + int(sh * 3), 11, fb, ft, sweep=sweep)
    _flame_ring(surf, cx, cy, r - 2, 6, 11, _shade(FLAME_B, bf * 0.9),
                _shade(FLAME_T, bf * 0.95), sweep=sweep * 0.8,
                start=0.28)

    # Molten disc with a hot inner core.
    _radial_body(surf, cx, cy, r, mid, mid, edge)
    _aaellipse(surf, _shade((255, 150, 40), bf), (cx - 1, cy), r - 5, r - 5)
    _aaellipse(surf, core, (cx - 2, cy - 2), r - 8, r - 8)

    # Fierce face: angled brows + a confident grin.
    _sun_face(surf, cx, cy, eye_dx=6, eye_r=4, iris=(70, 26, 12),
              mouth="grin", brow=(120, 36, 14))
    return surf


build = _make_prebuilt_skin(build_blaze)
