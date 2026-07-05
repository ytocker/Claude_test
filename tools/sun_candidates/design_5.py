"""SOLAR DEITY — design_5 (legendary-tier showpiece). A majestic layered sun:
a faceted concentric core, a double corona (long outer ring + short inner ring),
wispy solar-flare licks and a soft glow that pulses with the shine. Scratch
only."""
import math
import pygame

from game.parrot import _aaellipse
from tools.sun_candidates._shared import (
    _new, _make_glow_skin, _flap, _shine, _shade, _spike_ring, _sun_face,
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


def _deity_glow(wing_angle_deg):
    """The radiant bloom, drawn on its own layer so `_make_glow_skin` can blit it
    BEHIND the outlined sun — keeping the soft glow out of the outline pass (no
    dark halo). Pulses brighter/wider on the shine down-stroke."""
    sh = _shine(wing_angle_deg)
    g = _new()
    cx, cy = BCX, BCY
    r = 13 + int(sh * 1)
    pygame.draw.circle(g, (*BLOOM, 40 + int(sh * 30)), (cx, cy), r + 14 + int(sh * 4))
    pygame.draw.circle(g, (*BLOOM, 60 + int(sh * 40)), (cx, cy), r + 7)
    return g


def build_deity(wing_angle_deg):
    surf = _new()
    sh = _shine(wing_angle_deg)
    r = 13 + int(sh * 1)
    cx, cy = BCX, BCY
    bf = 0.90 + 0.20 * sh
    # Corona tips flash toward white on the down-stroke — the premium "ignite".
    rt = _shade(RAY_T, bf)
    if sh > 0.6:
        rt = (255, 248, 210)
    rb = _shade(RAY_B, bf)

    # Double corona: long outer ring + a short inner ring offset half a step.
    long_len = 11 + int(sh * 3)
    _spike_ring(surf, cx, cy, r - 1, long_len, 12, rb, rt, taper=0.42)
    _spike_ring(surf, cx, cy, r - 2, 6, 12, _shade(DGOLD, bf),
                _shade(RAY_T, bf * 0.96), start=math.pi / 12, taper=0.5)
    # Bright wispy flare licks (2px) rotated tangentially for grandeur.
    for i in range(6):
        a = (2 * math.pi) * i / 6 + 0.3
        tip = (cx + math.cos(a + 0.5) * (r + long_len + 3),
               cy + math.sin(a + 0.5) * (r + long_len + 3))
        base = (cx + math.cos(a) * (r + 2), cy + math.sin(a) * (r + 2))
        pygame.draw.line(surf, _shade(FLARE, bf), base, tip, 2)

    # Faceted concentric core: deep gold → gold → white-hot rings.
    _aaellipse(surf, _shade(RIM, bf),  (cx + 1, cy + 1), r, r)
    _aaellipse(surf, _shade(DGOLD, bf), (cx, cy), r - 1, r - 1)
    _aaellipse(surf, _shade(GOLD, bf),  (cx - 1, cy - 1), r - 4, r - 4)
    _aaellipse(surf, _shade(WHOT, bf),  (cx - 2, cy - 2), r - 8, r - 8)
    # White-hot specular that pulses with the shine — the legendary tell.
    pygame.draw.circle(surf, _shade(WHOT, min(1.2, bf * 1.05)),
                       (cx - 3, cy - 3), 2 + int(sh * 1))

    # Serene majestic face: small calm eyes pulled in + a subtle smile.
    _sun_face(surf, cx, cy, eye_dx=5, eye_r=3, iris=(74, 44, 18), mouth="smile")
    return surf


build = _make_glow_skin(build_deity, _deity_glow)
