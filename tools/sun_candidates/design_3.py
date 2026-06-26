"""SYNTHWAVE SUN — design_3. An 80s vaporwave sunset: a magenta→orange→yellow
banded gradient disc crossed by dark horizontal slit bands, rays only off the
upper half (a rising sun). The graphic-design sun. Scratch only."""
import pygame

from game.parrot import _aaellipse
from game.draw import lerp_color
from tools.sun_candidates._shared import (
    _new, _make_prebuilt_skin, _shine, _shade, _spike_ring, _eye, BCX, BCY,
)

TOP  = (255, 61, 174)           # magenta (top)
MID  = (255, 122, 61)           # orange
BOT  = (255, 210, 62)           # yellow (bottom)
SLIT = (42, 18, 51)             # dark slit shadow
RAY_B = (255, 90, 140)
RAY_T = (255, 224, 120)
GLOW = (255, 120, 180)


def _grad_disc(surf, cx, cy, r, stops):
    """A vertical multi-stop gradient clipped to a circle (built straight into an
    SRCALPHA layer so it needs no display)."""
    d = r * 2
    grad = pygame.Surface((d, d), pygame.SRCALPHA)
    for i in range(d):
        t = i / max(1, d - 1)
        if t < 0.5:
            c = lerp_color(stops[0], stops[1], t * 2)
        else:
            c = lerp_color(stops[1], stops[2], (t - 0.5) * 2)
        pygame.draw.line(grad, c, (0, i), (d - 1, i))
    mask = pygame.Surface((d, d), pygame.SRCALPHA)
    _aaellipse(mask, (255, 255, 255, 255), (r, r), r - 1, r - 1)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(grad, (cx - r, cy - r))


def build_retro(wing_angle_deg):
    surf = _new()
    sh = _shine(wing_angle_deg)
    r = 13 + int(sh * 1)
    cx, cy = BCX, BCY
    bf = 0.94 + 0.12 * sh
    rb, rt = _shade(RAY_B, bf), _shade(RAY_T, bf)

    # Soft glow.
    glow = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
    pygame.draw.circle(glow, (*GLOW, 55), (cx, cy), r + 10 + int(sh * 3))
    surf.blit(glow, (0, 0))

    # Upper-HALF corona only (rising sun): rays fanned across the top ~200°.
    n = 9
    import math
    for i in range(n):
        a = math.pi + 0.15 + (math.pi - 0.3) * i / (n - 1)   # top arc
        _spike_ring(surf, cx, cy, r - 1, 9 + int(sh * 3), 1, rb, rt,
                    start=a, taper=0.5)

    # Gradient disc.
    _grad_disc(surf, cx, cy, r, (_shade(TOP, bf), _shade(MID, bf), _shade(BOT, bf)))

    # Horizontal retro slit bands across the lower half (thicker toward the base).
    for k, yy in enumerate((cy + 2, cy + 5, cy + 8, cy + 11)):
        half = int((r ** 2 - (yy - cy) ** 2) ** 0.5) if abs(yy - cy) < r else 0
        if half > 1:
            pygame.draw.line(surf, SLIT, (cx - half + 1, yy),
                             (cx + half - 1, yy), 1 + (k >= 2))

    # Minimal calm face on the upper disc.
    _eye(surf, cx - 5, cy - 2, 3, iris=(60, 24, 60))
    _eye(surf, cx + 5, cy - 2, 3, iris=(60, 24, 60))
    return surf


build = _make_prebuilt_skin(build_retro)
