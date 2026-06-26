"""KAWAII SUN — design_4. A soft pastel chibi sun: rounded bobble rays, huge
sparkly eyes, a tiny smile and big round blush. Maximum charm. Scratch only."""
import pygame

from game.parrot import _aaellipse
import math

from tools.sun_candidates._shared import (
    _new, _make_prebuilt_skin, _shine, _shade, _radial_body, _stub_ring,
    _spike_ring, _sun_face, BCX, BCY,
)

CORE = (255, 241, 194)
MID  = (255, 221, 102)
EDGE = (228, 176, 70)
RAY_B = (255, 192, 77)
RAY_T = (255, 240, 190)
SPARK = (255, 251, 234)


def build_kawaii(wing_angle_deg):
    surf = _new()
    sh = _shine(wing_angle_deg)
    r = 13 + int(sh * 1)
    cx, cy = BCX, BCY
    bf = 0.94 + 0.12 * sh
    core, mid, edge = _shade(CORE, bf), _shade(MID, bf), _shade(EDGE, bf)
    rb, rt = _shade(RAY_B, bf), _shade(RAY_T, bf)

    # Pointed triangular rays interleaved BETWEEN the round bobbles so the
    # silhouette spikes like a sun (not an even-petal marigold). Sharp tips first
    # (under), longer than the bobbles, offset half a step.
    _spike_ring(surf, cx, cy, r - 2, 9 + int(sh * 2), 8, rb, rt,
                start=math.pi / 8, taper=0.5)
    # Soft rounded bobbles pulled IN to the disc (one radiant body, not orbiting
    # dots).
    _stub_ring(surf, cx, cy, r - 3, 5 + int(sh * 1), 8, rb, rt)

    # Plump pastel disc.
    _radial_body(surf, cx, cy, r, core, mid, edge)

    # Big-eyed adorable face with round blush + a tiny smile (nudged down 1px).
    _sun_face(surf, cx, cy + 1, eye_dx=6, eye_r=5, iris=(96, 56, 24),
              mouth="tiny", blush=(255, 158, 176))

    # Two sparkle stars off the corona (4-point glints).
    for sxp, syp in ((cx + r + 5, cy - 8), (cx - r - 4, cy + 6)):
        pygame.draw.line(surf, SPARK, (sxp - 2, syp), (sxp + 2, syp), 1)
        pygame.draw.line(surf, SPARK, (sxp, syp - 2), (sxp, syp + 2), 1)
        pygame.draw.circle(surf, SPARK, (sxp, syp), 1)
    return surf


build = _make_prebuilt_skin(build_kawaii)
