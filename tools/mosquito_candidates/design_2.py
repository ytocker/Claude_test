"""MOSQUITO redesign — design_2 AMBER RELIC (legendary showpiece).

A mosquito preserved in glowing amber: the MEDIUM is the star. A layered
additive golden halo suspends a dark sepia fossil silhouette, dotted with
frozen bubble specks and a single gem-face streak. The insect itself reads
low-contrast (it's preserved, not alive) so the warm glow does the selling —
while the proboscis + curled legs stay sharp enough to survive the 40px
gameplay shrink against pale day sky.

Scratch exploration only — NOT registered in animal_skins.BUILDERS / catalog.
Production art stays untouched until a winner is picked.
"""
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

pygame.init()

from game.parrot import _WING_ANGLES, _add_outline, _aaellipse  # noqa: E402,F401
from game.animal_skins import (  # noqa: E402
    _make_prebuilt_skin, COMPOSITE_W, COMPOSITE_H, BCX, BCY, HCX, HCY, _new,
)

# ── palette ──────────────────────────────────────────────────────────────────
FOSSIL = (58, 30, 8)      # dark sepia — the preserved silhouette
SEPIA  = (138, 75, 18)    # mid-sepia — abdomen banding / warm shade
AMBER  = (232, 162, 44)   # amber core — glow field, low-contrast eye
HONEY  = (255, 216, 115)  # honey highlight — rim light / gem streak
GLINT  = (255, 243, 201)  # bubble / spark whites


def _rot_blit(surf, s, anchor):
    surf.blit(s, s.get_rect(center=anchor).topleft)


def _ghost_wing(angle_deg, sgn):
    """A translucent 'ghost' forewing — a thin amber-tinted ellipse with two
    faint veins. Kept near-horizontal: a fossil wing is frozen, so the flap is
    only a slight tilt off level rather than a live buzz."""
    w = pygame.Surface((40, 20), pygame.SRCALPHA)
    _aaellipse(w, (*AMBER, 78), (20, 10), 18, 7)
    _aaellipse(w, (*HONEY, 55), (14, 9), 9, 4)
    pygame.draw.ellipse(w, (*HONEY, 90), (2, 3, 36, 14), 1)
    for vy in (8, 12):
        pygame.draw.line(w, (*SEPIA, 70), (6, vy), (34, 10), 1)
    out = pygame.transform.rotate(w, angle_deg)
    if sgn < 0:
        out = pygame.transform.flip(out, True, False)
    return out


def build_mosquito_amber(wing_angle_deg):
    surf = _new()
    f = (wing_angle_deg + 40) / 90.0        # 0 down-stroke … 1 up-stroke
    # Frozen wings barely move — a shallow oscillation around level.
    tilt = (f - 0.5) * 10

    # ── 1 · amber glow field (behind everything) ─────────────────────────────
    # Layered concentric ellipses, HONEY-bright core → AMBER → transparent,
    # composited additively so the overlaps bloom into a gem-like halo.
    glow = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    for r, col, a in (
        (23, AMBER, 26), (20, AMBER, 34), (16, AMBER, 46),
        (12, HONEY, 40), (8, HONEY, 58), (5, GLINT, 70),
    ):
        _aaellipse(glow, (*col, a), (BCX, BCY - 2), r, int(r * 1.28))
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # ── 2 · gem-face streak highlight (a raking light on the amber facet) ─────
    streak = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    pygame.draw.line(streak, (*GLINT, 120), (21, 30), (44, 21), 2)
    pygame.draw.line(streak, (*HONEY, 70), (20, 35), (40, 27), 1)
    surf.blit(streak, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # ── 3 · frozen bubble specks trapped in the resin ────────────────────────
    for bx, by, br in ((39, 29, 2), (27, 41, 3), (37, 53, 2), (24, 32, 1)):
        pygame.draw.circle(surf, (*GLINT, 210), (bx, by), br)
        if br > 1:                          # crescent shade → tiny sphere read
            pygame.draw.circle(surf, (*AMBER, 150), (bx + 1, by + 1), br - 1)
            pygame.draw.circle(surf, (*GLINT, 230), (bx - 1, by - 1), 1)

    # ── 4 · far ghost wing (behind the body) ─────────────────────────────────
    _rot_blit(surf, _ghost_wing(18 + tilt, +1), (BCX + 12, BCY - 8))

    # ── 5 · thorax (dark fossil hump with a honey rim-light) ─────────────────
    _aaellipse(surf, FOSSIL, (BCX + 4, BCY - 5), 8, 7)
    pygame.draw.arc(surf, HONEY, (BCX - 4, BCY - 14, 18, 16),
                    math.radians(35), math.radians(140), 2)

    # ── 6 · abdomen (tapering dark tail, sepia banding) ──────────────────────
    abdomen = [
        (BCX + 2, BCY - 3), (BCX + 6, BCY + 1),
        (BCX - 2, BCY + 16), (BCX - 8, BCY + 22), (BCX - 10, BCY + 19),
        (BCX - 4, BCY + 8), (BCX - 2, BCY - 1),
    ]
    pygame.draw.polygon(surf, FOSSIL, abdomen)
    # Segment bands warm the underside without lifting the low-contrast read.
    for t, (bx, by) in enumerate(((BCX - 1, BCY + 6), (BCX - 4, BCY + 12),
                                  (BCX - 7, BCY + 18))):
        pygame.draw.line(surf, SEPIA, (bx + 3, by - 2), (bx - 3, by + 2), 2)
    # Dorsal honey rim continuing down the abdomen top edge.
    pygame.draw.line(surf, (*HONEY, 200),
                     (BCX + 3, BCY - 2), (BCX - 8, BCY + 19), 1)

    # ── 7 · legs (six curled, frozen filaments) ──────────────────────────────
    # Three near legs (bent knees) + three faint far legs for the tangled,
    # suspended look. Dark FOSSIL, slightly irregular — they froze mid-drift.
    for (x0, y0), (kx, ky), (x1, y1), wdt in (
        ((38, 46), (44, 51), (46, 59), 2),   # front
        ((32, 48), (33, 55), (31, 62), 2),   # mid
        ((26, 46), (20, 51), (16, 59), 2),   # rear
    ):
        pygame.draw.lines(surf, FOSSIL, False, [(x0, y0), (kx, ky), (x1, y1)],
                          wdt)
        pygame.draw.circle(surf, FOSSIL, (x1, y1), 1)
    for (x0, y0), (kx, ky), (x1, y1) in (
        ((40, 44), (48, 47), (52, 53)),      # far front
        ((34, 45), (40, 43), (46, 41)),      # far raised
        ((28, 45), (22, 43), (17, 45)),      # far rear
    ):
        pygame.draw.lines(surf, (*SEPIA, 140), False,
                          [(x0, y0), (kx, ky), (x1, y1)], 1)

    # ── 8 · near ghost wing (over the body — the frozen span) ────────────────
    _rot_blit(surf, _ghost_wing(-8 - tilt, -1), (BCX - 4, BCY - 6))

    # ── 9 · head + low-contrast amber eye ────────────────────────────────────
    _aaellipse(surf, FOSSIL, (HCX, HCY), 7, 7)
    pygame.draw.arc(surf, HONEY, (HCX - 7, HCY - 8, 14, 12),
                    math.radians(30), math.radians(150), 2)
    # Compound eye: amber-on-fossil, low contrast (preserved, not alive).
    _aaellipse(surf, AMBER, (HCX + 1, HCY - 1), 5, 5)
    _aaellipse(surf, SEPIA, (HCX + 1, HCY - 1), 5, 5)
    for gx in range(-2, 4, 2):              # faint faceted stipple
        for gy in range(-2, 4, 2):
            pygame.draw.circle(surf, FOSSIL, (HCX + 1 + gx, HCY - 1 + gy), 1)
    pygame.draw.circle(surf, HONEY, (HCX - 1, HCY - 3), 1)   # single frozen glint

    # ── 10 · proboscis (dark needle + honey dorsal highlight) ────────────────
    # Two tiny palp stubs at the base, then the long needle striking forward.
    for py in (HCY + 1, HCY + 3):
        pygame.draw.line(surf, FOSSIL, (HCX + 4, py), (HCX + 10, py + 2), 2)
    pygame.draw.line(surf, FOSSIL, (HCX, HCY + 2), (63, HCY), 3)
    pygame.draw.line(surf, HONEY, (HCX + 1, HCY + 1), (62, HCY - 1), 1)

    return surf


build = _make_prebuilt_skin(build_mosquito_amber)
