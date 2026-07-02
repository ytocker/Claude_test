"""MOSQUITO redesign — design_5 PIP THE SKEETER (kawaii/chibi).

The wholesome take: every spiky mosquito feature is rounded off into candy
shapes so it charms instead of bites. A big glossy chibi eye sits in a plump
mint head, the proboscis is a stubby hot-pink drinking straw (never a needle),
the mint body carries two sunny yellow belly bands, and three short springy
legs dangle with tiny rounded feet. It still says "mosquito" at 40px because
the two silhouette tells survive: a forward straw + a low fan of dangling legs.

Legibility is the whole game at thumbnail size, so the body is drawn BRIGHT
(candy mint, not muddy teal) and every blob carries a bright rim UNDER the
factory's dark outline — that dark→bright-mint→mint edge is what keeps the
shape alive on the dark night biome as well as the daytime sky.

Scratch exploration only — NOT registered in animal_skins.BUILDERS. Production
art stays untouched until a winner is picked.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

pygame.init()

from game.parrot import _WING_ANGLES, _add_outline, _aaellipse  # noqa: E402
from game.animal_skins import (  # noqa: E402
    _make_prebuilt_skin, COMPOSITE_W, COMPOSITE_H, BCX, BCY, HCX, HCY, _new,
)

# ── palette (candy pastel — high value so it holds up on night sky) ───────────
OUTLINE = (59, 74, 82)      # #3B4A52 soft charcoal — legs, pupil, straw edge
MINT    = (127, 227, 196)   # #7FE3C4 body base — the actual brief mint
MINT_H  = (200, 251, 232)   # bright top-light so the plump body reads glossy
RIM     = (160, 255, 238)   # #A0FFEE bright rim under the dark outline (night)
STRIPE  = (255, 224, 138)   # #FFE08A sunny belly band
PINK    = (255, 157, 192)   # #FF9DC0 cheek blush + straw
WHITE   = (255, 255, 255)   # sclera + gleams

# Translucent mint wing — kept pale/bright so it never muddies the body.
WING    = (168, 240, 216, 120)
WING_E  = (150, 235, 210, 175)

# ── body anchors (plump chibi; kept near BCX/BCY so collision stays fair) ─────
_AB_C  = (26, 46)           # abdomen centre
_AB_RX, _AB_RY = 13, 11
_TH_C  = (37, 40)           # thorax centre
_TH_R  = 10
_HD_C  = (HCX, HCY)         # head centre → (44, 34)
_HD_R  = 9


def _flap(a):
    # 1 = up-stroke (wings lifted, narrower), 0 = down-stroke (wings wide open).
    return (a + 40) / 90.0


def _wing(f):
    """A soft rounded leaf/oval membrane — deliberately NOT the sharp narrow
    blade of a real mosquito. Wider + taller on the down-stroke, narrowing as
    the stroke lifts so the flap still animates."""
    surf = pygame.Surface((36, 22), pygame.SRCALPHA)
    cx, cy = 18, 11
    ww = 30 - int(f * 8)
    hh = 15 - int(f * 5)
    rect = (cx - ww // 2, cy - hh // 2, ww, hh)
    pygame.draw.ellipse(surf, WING, rect)
    pygame.draw.ellipse(surf, WING_E, rect, 1)
    # A single faint vein keeps it a wing, not a bubble, without going spiky.
    pygame.draw.line(surf, (215, 250, 238, 90),
                     (cx - ww // 2 + 3, cy + 1), (cx + ww // 2 - 3, cy - 1), 1)
    return surf


def _leg(surf, hip, foot, *, bend=2):
    """A short springy leg: a gentle single-bend polyline with a tiny rounded
    charcoal foot. Charcoal so the dangling cluster stays legible against the
    bright belly; three on the visible side is the clearest 'legs' read at 1×
    (six turn to noise on the downsample)."""
    hx, hy = hip
    fx, fy = foot
    mx = (hx + fx) / 2 + bend
    my = (hy + fy) / 2
    pygame.draw.lines(surf, OUTLINE, False,
                      [(hx, hy), (mx, my), (fx, fy)], 2)
    pygame.draw.circle(surf, OUTLINE, (int(fx), int(fy)), 2)


def _band_span(cx, cy, rx, ry, y):
    """Half-width of an ellipse at row y — used to clip the belly bands so they
    sit ON the abdomen instead of overhanging the rounded silhouette."""
    dy = (y - cy) / ry
    if abs(dy) >= 1.0:
        return 0.0
    return rx * (1.0 - dy * dy) ** 0.5


def build_mosquito_cutie(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)

    # 1 · Wings — two soft leaves swept up-and-back, behind the body so the
    #     plump mint mass stays the hero shape.
    far = pygame.transform.rotozoom(_wing(f), 34 + f * 8, 1.0)
    surf.blit(far, far.get_rect(center=(30, 26)))
    near = pygame.transform.rotozoom(_wing(f), 22 + f * 8, 1.0)
    surf.blit(near, near.get_rect(center=(24, 31)))

    # 2 · Bright rims for the whole body mass FIRST, so a bright-mint halo peeks
    #     out under the factory's dark outline at the silhouette edge — this is
    #     the night-legibility insurance. Drawn behind all fills so no bright
    #     seam shows where the blobs overlap.
    _aaellipse(surf, RIM, _AB_C, _AB_RX + 1, _AB_RY + 1)
    _aaellipse(surf, RIM, _TH_C, _TH_R + 1, _TH_R + 1)
    _aaellipse(surf, RIM, _HD_C, _HD_R + 1, _HD_R + 1)

    # 3 · Body fills — plump candy-mint blobs (abdomen + thorax + head) reading
    #     as one soft mass. High-value fill + a crisp top highlight keep it
    #     bright instead of murky.
    acx, acy = _AB_C
    _aaellipse(surf, MINT, _AB_C, _AB_RX, _AB_RY)
    _aaellipse(surf, MINT, _TH_C, _TH_R, _TH_R)
    _aaellipse(surf, MINT, _HD_C, _HD_R, _HD_R)
    _aaellipse(surf, MINT_H, (acx - 4, acy - 5), 6, 3)
    _aaellipse(surf, MINT_H, (_TH_C[0] - 4, _TH_C[1] - 5), 5, 3)
    _aaellipse(surf, MINT_H, (_HD_C[0] - 4, _HD_C[1] - 5), 4, 3)

    # 4 · Belly bands — two clean, distinct sunny bands clipped to the abdomen.
    for by in (42, 49):
        hw = _band_span(acx, acy, _AB_RX - 1, _AB_RY - 1, by)
        if hw > 2:
            pygame.draw.line(surf, STRIPE, (acx - hw, by), (acx + hw, by), 3)

    # 5 · Legs — the #2 tell: three short springy legs dangling below the belly
    #     with tiny rounded feet, in charcoal so they survive over the body.
    _leg(surf, (20, 53), (15, 64), bend=-2)
    _leg(surf, (28, 56), (27, 66), bend=1)
    _leg(surf, (36, 52), (42, 63), bend=2)

    # 6 · Cheek blush — a soft rosy oval below-and-behind the eye; core chibi cue.
    blush = pygame.Surface((13, 9), pygame.SRCALPHA)
    pygame.draw.ellipse(blush, (*PINK, 200), (0, 0, 13, 9))
    surf.blit(blush, blush.get_rect(center=(40, 41)))

    # 7 · THE EYE — one dominant chibi eye: white sclera, big dark pupil, a crisp
    #     offset gleam. Sized so a mint 'cheek' still rings it (it reads as an
    #     eye, not a white disc) and it survives the 40px shrink.
    ex, ey = 46, 33
    pygame.draw.circle(surf, WHITE, (ex, ey), 6)          # sclera
    pygame.draw.circle(surf, OUTLINE, (ex + 1, ey), 4)    # #3B4A52 pupil
    pygame.draw.circle(surf, WHITE, (ex - 2, ey - 2), 2)  # main gleam
    pygame.draw.circle(surf, WHITE, (ex + 2, ey + 2), 1)  # secondary catch

    # 8 · Proboscis — the #1 tell: a stubby but UNMISTAKABLE hot-pink straw
    #     pointing forward-and-down off the head, sticking well past the muzzle
    #     so it stays a distinct silhouette spike at thumbnail size.
    p0 = (49, 39)
    p1 = (61, 43)
    pygame.draw.line(surf, PINK, p0, p1, 4)               # straw
    pygame.draw.circle(surf, PINK, p1, 2)                 # rounded tip
    pygame.draw.line(surf, WHITE, (50, 38), (58, 41), 1)  # glossy gleam
    return surf


build = _make_prebuilt_skin(build_mosquito_cutie)
