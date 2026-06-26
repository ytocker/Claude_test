"""SOLAR DEITY — design_5 (legendary-tier showpiece). A majestic layered sun:
a faceted concentric core, a double corona (long outer ring + short inner ring),
wispy solar-flare licks and a soft glow that pulses with the shine. Scratch
only."""
import math
import pygame

from game.parrot import _aaellipse
from tools.sun_candidates._shared import (
    _new, _make_prebuilt_skin, _shine, _shade, _spike_ring, _sun_face,
    BCX, BCY,
)

WHOT = (255, 244, 200)          # white-hot core
GOLD = (255, 210, 62)
DGOLD = (240, 160, 40)
RIM  = (181, 112, 26)
RAY_B = (236, 158, 40)
RAY_T = (255, 240, 170)
FLARE = (255, 185, 74)
BLOOM = (255, 233, 160)


def build_deity(wing_angle_deg):
    surf = _new()
    sh = _shine(wing_angle_deg)
    r = 13 + int(sh * 1)
    cx, cy = BCX, BCY
    bf = 0.90 + 0.20 * sh
    rb, rt = _shade(RAY_B, bf), _shade(RAY_T, bf)

    # Soft radiant bloom.
    glow = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
    pygame.draw.circle(glow, (*BLOOM, 55), (cx, cy), r + 14 + int(sh * 4))
    pygame.draw.circle(glow, (*BLOOM, 70), (cx, cy), r + 7)
    surf.blit(glow, (0, 0))

    # Double corona: long outer ring + a short inner ring offset half a step.
    long_len = 11 + int(sh * 3)
    _spike_ring(surf, cx, cy, r - 1, long_len, 12, rb, rt, taper=0.42)
    _spike_ring(surf, cx, cy, r - 2, 6, 12, _shade(DGOLD, bf),
                _shade(RAY_T, bf * 0.96), start=math.pi / 12, taper=0.5)
    # A few wispy flare licks rotated tangentially for grandeur.
    for i in range(6):
        a = (2 * math.pi) * i / 6 + 0.3
        tip = (cx + math.cos(a + 0.5) * (r + long_len + 2),
               cy + math.sin(a + 0.5) * (r + long_len + 2))
        base = (cx + math.cos(a) * (r + 2), cy + math.sin(a) * (r + 2))
        pygame.draw.line(surf, _shade(FLARE, bf), base, tip, 1)

    # Faceted concentric core: deep gold → gold → white-hot rings.
    _aaellipse(surf, _shade(RIM, bf),  (cx + 1, cy + 1), r, r)
    _aaellipse(surf, _shade(DGOLD, bf), (cx, cy), r - 1, r - 1)
    _aaellipse(surf, _shade(GOLD, bf),  (cx - 1, cy - 1), r - 4, r - 4)
    _aaellipse(surf, _shade(WHOT, bf),  (cx - 2, cy - 2), r - 8, r - 8)
    pygame.draw.circle(surf, _shade(WHOT, bf * 1.05), (cx - 3, cy - 3), 2)

    # Serene majestic face: calm eyes + a subtle smile.
    _sun_face(surf, cx, cy, eye_dx=6, eye_r=4, iris=(120, 70, 24),
              mouth="smile")
    return surf


build = _make_prebuilt_skin(build_deity)
