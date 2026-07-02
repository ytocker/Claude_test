"""BUZZ THE HOUSEFLY (Design 2) — scratch candidate for the ANIMALS fly skin.

The "fly everyone draws": a round grey dumpling body under two ENORMOUS glossy
compound eyes that eat most of an oversized head, framed by stubby clear wings.
The eyes are the whole sell — big white catch-lights + a soft pupil read as
charming and unmistakably fly at 30px. Wholesome, not gross: the mouth is a soft
round sponge (labellum), never a needle. Scratch only — not registered in
BUILDERS; wrapped by the shared prebuilt getter so tools/ninja_render can drive
it exactly like a production skin.
"""
import math

import pygame

from game.animal_skins import (
    _make_prebuilt_skin, _new, _flap, _rot_blit, BCX, BCY, HCX, HCY, CROWN_Y,
)
from game.parrot import _aaellipse


# ── palette ──────────────────────────────────────────────────────────────────
_BODY_LT   = (154, 152, 150)        # #9A9896 warm-neutral top of the barrel
_BODY_DK   = (110, 108, 106)        # #6E6C6A bottom of the vertical ramp
_BODY_SHD  = (86, 84, 82)           # cast shadow / rim under the belly
_BAND      = (78, 76, 74)           # darker abdominal bands
_BRISTLE   = (74, 72, 70)           # #4A4846 fuzzy thorax fringe
_EYE       = (178, 74, 58)          # #B24A3A warm red-brown compound dome
_EYE_D     = (134, 52, 40)          # eye rim / lower shading
_EYE_FACET = (202, 100, 82)         # lighter facet stipple
_EYE_PUPIL = (86, 32, 26)           # soft pupil hint
_CATCH     = (255, 255, 255)        # glossy catch-light
_SPONGE    = (199, 154, 110)        # #C79A6E labellum pad
_SPONGE_D  = (168, 124, 84)
_LEG       = (66, 64, 62)
_SMILE     = (128, 100, 92)         # warm-grey warmth crease below the eyes
_WING_FILL = (237, 239, 242)        # #EDEFF2 clear-wing membrane
_WING_VEIN = (176, 182, 194)


def _lerp(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def _vgrad_ellipse(surf, cx, cy, rx, ry, top, bot):
    """Vertical top→bottom colour ramp clipped to an ellipse — sells the round
    barrel body reading as a lit dumpling rather than a flat disc."""
    for yy in range(-ry, ry + 1):
        frac = 1.0 - (yy / ry) ** 2
        if frac <= 0:
            continue
        half = rx * math.sqrt(frac)
        col = _lerp(top, bot, (yy + ry) / (2 * ry))
        pygame.draw.line(surf, col, (cx - half, cy + yy), (cx + half, cy + yy))


def _fly_wing(f, sgn):
    """A wide rounded clear wing (NOT a narrow mosquito blade). `f` (0=down,
    1=up) rotates + gently stretches it so the flap reads as a soft buzz.
    `sgn` splays the far vs. near wing to different rest angles."""
    w = pygame.Surface((46, 30), pygame.SRCALPHA)
    # Broad teardrop membrane: fat rounded oval, slightly translucent.
    pygame.draw.ellipse(w, (*_WING_FILL, 150), (4, 5, 40, 22))
    pygame.draw.ellipse(w, (255, 255, 255, 70), (10, 8, 24, 12))     # sheen
    pygame.draw.ellipse(w, (*_WING_VEIN, 170), (4, 5, 40, 22), 1)    # edge
    pygame.draw.line(w, (*_WING_VEIN, 150), (12, 14), (41, 11), 1)   # veins
    pygame.draw.line(w, (*_WING_VEIN, 120), (12, 20), (39, 20), 1)
    ang = sgn * (16 + f * 30)                # up-swept on the up-stroke
    stretch = 1.0 + f * 0.12
    if stretch != 1.0:
        w = pygame.transform.smoothscale(
            w, (46, max(1, int(30 * stretch))))
    return pygame.transform.rotozoom(w, ang, 1.0)


def build_buzz_housefly(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)                # 0 wings down, 1 wings up

    # ── far wing sweeps up-back behind the body for span/depth ──
    _rot_blit(surf, _fly_wing(f, +1), (30, 22))

    # ── chunky grey barrel body (vertical grey ramp) ──
    _aaellipse(surf, _BODY_SHD, (BCX + 1, BCY + 3), 13, 12)          # rim shade
    _vgrad_ellipse(surf, BCX, BCY + 1, 12, 11, _BODY_LT, _BODY_DK)
    # Two subtle darker abdominal bands across the lower body.
    for by in (BCY + 4, BCY + 8):
        pygame.draw.arc(surf, _BAND, (BCX - 11, by - 6, 22, 12),
                        math.radians(200), math.radians(340), 2)
    # Top-left specular so the barrel reads glossy-round.
    _aaellipse(surf, (176, 174, 172), (BCX - 4, BCY - 5), 5, 3)

    # Thin dangling legs (fly-read grounding, kept subtle behind the body).
    for lx, bend in ((BCX - 3, -3), (BCX + 2, 0), (BCX + 7, 3)):
        pygame.draw.lines(surf, _LEG, False,
                          [(lx, BCY + 9), (lx + bend, BCY + 15),
                           (lx + bend + 3, BCY + 18)], 1)

    # ── fuzzy thorax bristle fringe (hairy-fly tell) ──
    for i in range(6):
        bx = 24 + i * 3
        pygame.draw.line(surf, _BRISTLE, (bx, 33), (bx - 1, 29), 1)

    # ── oversized head behind the eyes so the face is one big mass ──
    _aaellipse(surf, _BODY_DK, (HCX, HCY + 3), 12, 9)
    _vgrad_ellipse(surf, HCX, HCY + 2, 11, 8, _BODY_LT, _BODY_DK)

    # ═══ HERO: two ENORMOUS glossy compound eyes ═══
    for ex in (37, 51):
        # Warm red-brown compound dome.
        _aaellipse(surf, _EYE_D, (ex + 1, 32), 9, 9)
        _aaellipse(surf, _EYE, (ex, 31), 8, 8)
        # Faint facet stipple — a few lighter dots read as compound eye.
        for fx, fy in ((ex - 3, 33), (ex + 2, 34), (ex + 3, 29), (ex - 1, 30)):
            pygame.draw.circle(surf, _EYE_FACET, (fx, fy), 1)
        # Soft pupil hint at centre keeps the huge eye feeling alive.
        pygame.draw.circle(surf, _EYE_PUPIL, (ex, 31), 2)
        # BIG catch-light upper-left + a soft secondary lower-right = gloss.
        _aaellipse(surf, _CATCH, (ex - 3, 28), 3, 2)
        pygame.draw.circle(surf, (255, 255, 255), (ex + 3, 34), 1)
        # Rim the dome for a crisp read against the grey head.
        pygame.draw.circle(surf, _EYE_D, (ex, 31), 8, 1)

    # Tiny warmth crease below each eye.
    for ex in (37, 51):
        pygame.draw.arc(surf, _SMILE, (ex - 3, 38, 6, 5),
                        math.radians(200), math.radians(340), 1)

    # ── spongy labellum (soft round mouth pad — NOT a needle) ──
    _aaellipse(surf, _SPONGE_D, (46, 46), 3, 3)
    _aaellipse(surf, _SPONGE, (46, 45), 3, 2)
    pygame.draw.line(surf, _SPONGE_D, (44, 45), (48, 45), 1)

    # ── near wing over the abdomen, translucent so the body shows through ──
    _rot_blit(surf, _fly_wing(f, -1), (25, 33))

    return surf


build = _make_prebuilt_skin(build_buzz_housefly)
