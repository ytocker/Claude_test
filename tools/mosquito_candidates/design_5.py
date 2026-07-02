"""MOSQUITO redesign — design_5 PIP THE SKEETER (kawaii/chibi).

The wholesome take: every spiky mosquito feature is rounded off into candy
shapes so it charms instead of bites. One ENORMOUS glossy cartoon eye owns the
whole head, the proboscis is a stubby rounded drinking straw (never a needle),
the mint body is plump with two friendly yellow belly bands, and the six legs
are short and springy with tiny rounded feet. It still says "mosquito" at 40px
because the two silhouette tells survive: a forward straw + a low fan of
dangling legs. Pastel mint keeps it reading as a bug, not a bird.

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

# ── palette ──────────────────────────────────────────────────────────────────
OUTLINE = (59, 74, 82)      # #3B4A52 soft charcoal — friendly, not black
MINT    = (127, 227, 196)   # #7FE3C4 mint body
STRIPE  = (255, 224, 138)   # #FFE08A friendly yellow belly band
PINK    = (255, 157, 192)   # #FF9DC0 rosy cheek
WHITE   = (255, 255, 255)   # eye gleam

# Volume shades derived from the mint so the round body isn't flat.
MINT_D  = (92, 196, 166)    # underside shadow
MINT_H  = (182, 246, 222)   # top rim-light
EYE_DK  = (26, 34, 52)      # near-black navy pupil — reads warm, not harsh
WING    = (127, 227, 196, 110)   # pale translucent mint wing membrane
WING_E  = (150, 235, 210, 165)   # slightly firmer wing edge


def _flap(a):
    # 1 = up-stroke (wings lifted, narrower), 0 = down-stroke (wings wide open).
    return (a + 40) / 90.0


def _wing(f):
    """A soft rounded leaf/oval membrane — deliberately NOT the sharp narrow
    blade of a real mosquito. Wider + taller on the down-stroke, narrowed toward
    edge-on as the stroke lifts, so the flap still animates."""
    surf = pygame.Surface((36, 22), pygame.SRCALPHA)
    cx, cy = 18, 11
    ww = 30 - int(f * 8)
    hh = 15 - int(f * 5)
    rect = (cx - ww // 2, cy - hh // 2, ww, hh)
    pygame.draw.ellipse(surf, WING, rect)
    pygame.draw.ellipse(surf, WING_E, rect, 1)
    # A single faint vein keeps it a wing, not a bubble, without going spiky.
    pygame.draw.line(surf, (200, 248, 232, 90),
                     (cx - ww // 2 + 3, cy + 1), (cx + ww // 2 - 3, cy - 1), 1)
    return surf


def _leg(surf, hip, foot, width, *, bend=2):
    """A short springy leg: a gentle single-bend polyline with a tiny rounded
    foot pad. Kept bouncy/curved (never a straight stiff spider line) so the rig
    stays chibi while the dangling six-line cluster still tells 'mosquito'."""
    hx, hy = hip
    fx, fy = foot
    mx = (hx + fx) / 2 + bend
    my = (hy + fy) / 2
    pygame.draw.lines(surf, OUTLINE, False,
                      [(hx, hy), (mx, my), (fx, fy)], width)
    pygame.draw.circle(surf, OUTLINE, (int(fx), int(fy)), 2)


def _band_span(cx, cy, rx, ry, y):
    """Half-width of an ellipse at row y — used to clip the belly bands so they
    sit ON the abdomen instead of overhanging the rounded silhouette."""
    dy = (y - cy) / ry
    if abs(dy) >= 1.0:
        return 0.0
    return rx * (1.0 - dy * dy) ** 0.5


# Abdomen / thorax anchors (rounded, chubby — friendlier than a scary skeeter).
_AB_C = (28, 51)
_AB_RX, _AB_RY = 13, 9
_TH_C = (37, 41)


def build_mosquito_cutie(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)

    # 1 · Wings — two soft leaves swept up-and-back over the abdomen, behind the
    #     body so the plump mint mass stays the hero shape.
    far = pygame.transform.rotozoom(_wing(f), 34 + f * 8, 1.0)
    surf.blit(far, far.get_rect(center=(34, 28)))
    near = pygame.transform.rotozoom(_wing(f), 22 + f * 8, 1.0)
    surf.blit(near, near.get_rect(center=(27, 33)))

    # 2 · Far legs behind the body — thin, so the near set reads in front.
    for hip, foot in (((38, 47), (44, 57)), ((30, 49), (29, 59)),
                      ((22, 47), (15, 55))):
        _leg(surf, hip, foot, 1, bend=-1)

    # 3 · Abdomen — a plump ROUNDED mint oval (no pointed tail) with two chunky
    #     friendly yellow bands clipped to its width.
    acx, acy = _AB_C
    _aaellipse(surf, MINT_D, (acx + 1, acy + 2), _AB_RX, _AB_RY)
    _aaellipse(surf, MINT, (acx, acy), _AB_RX, _AB_RY)
    _aaellipse(surf, MINT_H, (acx - 3, acy - 4), 6, 3)
    for by in (50, 55):
        hw = _band_span(acx, acy, _AB_RX - 1, _AB_RY, by)
        if hw > 2:
            pygame.draw.line(surf, STRIPE, (acx - hw, by), (acx + hw, by), 3)

    # 4 · Thorax — a rounder, chubbier hump than a real mosquito, seating the
    #     head. Overlaps the abdomen so the body reads as one soft blob.
    tcx, tcy = _TH_C
    _aaellipse(surf, MINT_D, (tcx + 1, tcy + 1), 12, 11)
    _aaellipse(surf, MINT, (tcx, tcy), 12, 11)
    _aaellipse(surf, MINT_H, (tcx - 3, tcy - 4), 6, 4)

    # 5 · Near legs in front of the body — the dangling six-line tell, springy.
    for hip, foot in (((40, 46), (47, 56)), ((33, 48), (33, 58)),
                      ((24, 46), (18, 56))):
        _leg(surf, hip, foot, 2, bend=2)

    # 6 · Head — a small mint nub behind the eye so there's a mint 'cheek' collar
    #     around the giant eye; mostly the eye takes this whole zone.
    _aaellipse(surf, MINT, (HCX, HCY + 2), 9, 9)

    # 7 · Cheek blush — a soft rosy oval just below-and-behind the eye.
    blush = pygame.Surface((14, 10), pygame.SRCALPHA)
    pygame.draw.ellipse(blush, (*PINK, 200), (0, 0, 14, 10))
    surf.blit(blush, blush.get_rect(center=(40, 41)))

    # 8 · THE EYE — one ENORMOUS glossy cartoon eye owning the head. Dark navy
    #     pupil, a big upper-left gleam + a small secondary catch = classic
    #     chibi wet-eye read that survives the 40px shrink.
    ex, ey = 46, 32
    pygame.draw.circle(surf, OUTLINE, (ex, ey), 12)
    pygame.draw.circle(surf, EYE_DK, (ex, ey), 11)
    pygame.draw.circle(surf, WHITE, (ex - 3, ey - 3), 5)
    pygame.draw.circle(surf, WHITE, (ex + 4, ey + 3), 2)

    # 9 · Proboscis — a CUTE rounded drinking straw, not a needle: a stubby
    #     mint tube with a soft charcoal border and a rounded cap tip.
    p0 = (46, 36)
    p1 = (58, 35)
    pygame.draw.line(surf, OUTLINE, p0, p1, 5)       # border
    pygame.draw.line(surf, MINT, p0, p1, 3)          # straw fill
    pygame.draw.circle(surf, MINT, (59, 35), 3)      # rounded cap
    pygame.draw.circle(surf, OUTLINE, (59, 35), 3, 1)
    # A tiny gleam so the straw looks glossy/soft.
    pygame.draw.line(surf, MINT_H, (48, 34), (55, 34), 1)
    return surf


build = _make_prebuilt_skin(build_mosquito_cutie)
