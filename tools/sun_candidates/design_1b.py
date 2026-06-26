"""CLASSIC SUNFACE — design_1. The iconic smiling sun: the puffer star-burst
made symmetric and friendly. Full even halo of alternating long/short rays + a
cheerful cartoon face. Scratch only."""
from game.parrot import _aaellipse
from tools.sun_candidates._shared import (
    _new, _make_prebuilt_skin, _shine, _shade, _radial_body, _ray_ring_alt,
    _sun_face, BCX, BCY,
)

CORE = (255, 232, 154)
MID  = (255, 210, 62)
EDGE = (200, 146, 36)
RAY_B = (224, 150, 44)
RAY_T = (255, 240, 176)


def build_sun(wing_angle_deg):
    surf = _new()
    sh = _shine(wing_angle_deg)
    r = 13 + int(sh * 1)
    cx, cy = BCX, BCY
    bf = 0.92 + 0.16 * sh
    core, mid, edge = _shade(CORE, bf), _shade(MID, bf), _shade(EDGE, bf)
    rb, rt = _shade(RAY_B, bf), _shade(RAY_T, bf)

    # Full even corona — alternating long/short triangular rays (flare on shine).
    long_len = 9 + int(sh * 3)
    _ray_ring_alt(surf, cx, cy, r - 1, long_len, long_len - 4, 10, rb, rt,
                  taper=0.5)

    # Golden disc + a warm core highlight.
    _radial_body(surf, cx, cy, r, core, mid, edge)
    _aaellipse(surf, _shade(CORE, bf * 1.06), (cx - 1, cy - 1), r - 7, r - 7)

    # Cheerful sun-face — calm small eyes pulled in, recentred up, and design 4's
    # gentle 'tiny' smile (the wider grin read as a creepy open mouth).
    _sun_face(surf, cx, cy - 1, eye_dx=5, eye_r=3, iris=(70, 40, 16),
              mouth="grin", blush=(255, 150, 120))
    return surf


build = _make_prebuilt_skin(build_sun)
