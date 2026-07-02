"""MOSQUITO · DESIGN 1 — MIDNIGHT WHINE (scratch candidate).

Dark, elegant, definitive mosquito: the realistic-but-premium baseline of the
MOSQUITO exploration. The silhouette lives or dies on the long forward
proboscis needle + the single oversized magenta compound eye, so both are
pushed harder than feels comfortable at 64px — they resolve at 40px in motion.

Exploration only: this exposes ``build`` for the tools/ninja_render.py harness
and is NEVER registered in animal_skins.BUILDERS or the store catalog.
"""
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

pygame.init()

from game.parrot import _add_outline, _aaellipse  # noqa: E402,F401
from game.animal_skins import (  # noqa: E402
    _make_prebuilt_skin, COMPOSITE_W, COMPOSITE_H, BCX, BCY, HCX, HCY,
    _new, _rot_blit, _flap,
)

# ── palette ──────────────────────────────────────────────────────────────────
BODY    = (18, 19, 43)          # #12132B near-black indigo
BODY_D  = (10, 11, 26)          # deepen for banding shadow / legs
MID     = (43, 58, 122)         # #2B3A7A mid-indigo steel band
TEAL    = (94, 200, 229)        # #5EC8E5 iridescent teal sheen
VIOLET  = (142, 63, 214)        # #8E3FD6 wing shimmer
EYE_MAG = (192, 70, 111)        # #C0466F compound-eye magenta
EYE_HI  = (255, 150, 190)       # magenta rim light
RIMLIGHT = (120, 150, 210)      # cool thorax rim highlight


def _mosq_wing(f, near):
    """A single long narrow iridescent blade, root at the RIGHT (thorax) end,
    tip at the LEFT. Teal (root) → violet (tip) smooth gradient, a specular
    streak whose position slides with the flap phase, and a vertical squash so
    the blade reads as a thin slit when the wings clap up (f→1)."""
    L, H = 34, 12
    surf = pygame.Surface((L, H + 4), pygame.SRCALPHA)
    base_a = 132 if near else 100
    a = max(46, int(base_a - f * 46))
    cx, cy = L / 2.0, (H + 4) / 2.0
    rx = L / 2.0 - 1
    ry = max(1.6, (H * (1.0 - 0.5 * f)) / 2.0)
    for x in range(L):
        t = x / (L - 1)                     # 0 tip(violet) → 1 root(teal)
        col = tuple(int(VIOLET[i] + (TEAL[i] - VIOLET[i]) * t) for i in range(3))
        norm = (x - cx) / rx
        if norm * norm >= 1.0:
            continue
        dy = ry * math.sqrt(1.0 - norm * norm)
        pygame.draw.line(surf, (*col, a), (x, cy - dy), (x, cy + dy))
    # Specular streak shifts frame-to-frame so the sheen visibly travels.
    sx = int(6 + f * (L - 14))
    norm = (sx - cx) / rx
    if norm * norm < 0.9:
        dy = ry * math.sqrt(1.0 - norm * norm)
        pygame.draw.line(surf, (230, 248, 255, min(210, a + 80)),
                         (sx, cy - dy * 0.55), (sx + 5, cy + dy * 0.35), 1)
    # Faint violet rim so the blade edge survives the outline pass.
    pygame.draw.ellipse(surf, (*VIOLET, min(180, a + 30)),
                        (1, int(cy - ry), L - 2, int(ry * 2)), 1)
    return surf


def _leg(surf, p0, knee, p1, col, width=1):
    pygame.draw.lines(surf, col, False, [p0, knee, p1], width)


def build_mosquito_midnight(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)               # 0 = wings down/spread, 1 = up/clap

    # ── far legs (behind the body, dimmer + offset so 6 legs read) ──
    for p0, knee, p1 in (
        ((37, 47), (41, 53), (44, 60)),
        ((33, 49), (32, 55), (31, 62)),
        ((27, 47), (24, 54), (21, 61)),
    ):
        _leg(surf, p0, knee, p1, BODY_D, 1)

    # ── far wing (behind, dimmer, swept a touch higher) ──
    fw = _mosq_wing(f, near=False)
    _rot_blit(surf, pygame.transform.rotate(fw, -12 + f * 40), (23, BCY - 15))

    # ── abdomen: tapered, pointed, banded indigo/steel back-left of thorax ──
    for i, (x, y, ex, ey) in enumerate((
        (26, BCY - 1, 7, 7), (21, BCY, 6, 6), (16, BCY + 2, 5, 5),
        (12, BCY + 3, 4, 4), (8, BCY + 4, 3, 3), (5, BCY + 5, 2, 2),
    )):
        _aaellipse(surf, BODY if i % 2 == 0 else MID, (x, y), ex, ey)
    # Segment seams read the banding even after the downscale.
    for x, y in ((23, BCY), (18, BCY + 1), (14, BCY + 3)):
        pygame.draw.line(surf, BODY_D, (x, y - 4), (x, y + 4), 1)

    # ── thorax: arched round indigo hump with a cool top rim-light ──
    _aaellipse(surf, BODY_D, (BCX + 1, BCY - 3), 10, 9)
    _aaellipse(surf, BODY, (BCX, BCY - 4), 9, 8)
    _aaellipse(surf, RIMLIGHT, (BCX - 3, BCY - 9), 4, 2)

    # ── near legs (over the body, full-strength indigo) ──
    for p0, knee, p1 in (
        ((36, 46), (40, 52), (42, 58)),
        ((32, 48), (31, 54), (30, 60)),
        ((26, 46), (23, 52), (20, 58)),
    ):
        _leg(surf, p0, knee, p1, BODY, 1)

    # ── near wing (the bright hero blade, resting up over the back) ──
    nw = _mosq_wing(f, near=True)
    _rot_blit(surf, pygame.transform.rotate(nw, -22 + f * 44), (22, BCY - 10))

    # ── head + the single oversized magenta compound eye ──
    _aaellipse(surf, BODY_D, (HCX - 2, HCY + 2), 6, 6)
    pygame.draw.circle(surf, BODY, (HCX, HCY), 9)
    pygame.draw.circle(surf, EYE_MAG, (HCX, HCY), 8)
    pygame.draw.circle(surf, (150, 44, 78), (HCX, HCY), 8, 1)
    # Faceted compound-eye stipple + a tiny bright catchlight.
    for dx, dy in ((-3, -3), (2, -4), (4, 1), (-2, 3), (1, 2)):
        pygame.draw.circle(surf, EYE_HI, (HCX + dx, HCY + dy), 1)
    pygame.draw.circle(surf, (255, 240, 250), (HCX - 3, HCY - 3), 2)

    # ── feathery antennae rising forward off the crown ──
    for sgn, ax in ((-1, HCX - 2), (1, HCX + 3)):
        tipx, tipy = ax + sgn * 1 + 6, HCY - 12
        pygame.draw.line(surf, MID, (ax, HCY - 6), (tipx, tipy), 1)

    # ── HERO: long tapered proboscis needle + flanking palps ──
    # Tapered so it reads as a needle, not a bar: wedge poly + a bright core.
    pygame.draw.polygon(surf, BODY, [
        (HCX, HCY + 4), (HCX, HCY), (63, HCY - 1), (63, HCY),
    ])
    pygame.draw.line(surf, MID, (HCX + 2, HCY + 1), (62, HCY - 1), 1)
    # Two short palps flanking the base.
    pygame.draw.line(surf, BODY_D, (HCX + 3, HCY + 3), (HCX + 10, HCY + 6), 1)
    pygame.draw.line(surf, BODY_D, (HCX + 3, HCY + 2), (HCX + 10, HCY - 1), 1)
    return surf


build = _make_prebuilt_skin(build_mosquito_midnight)
