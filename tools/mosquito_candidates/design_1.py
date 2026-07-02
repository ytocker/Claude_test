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
    """A single narrow iridescent blade, root at the RIGHT (thorax) end, tip at
    the LEFT. Teal (root) → violet (tip) gradient, a specular streak that slides
    with the flap phase, and a vertical squash so the blade thins toward the top
    of the up-stroke. Kept narrow so it reads as its own lifted shape, not a
    shiny back."""
    L, H = 32, 8
    surf = pygame.Surface((L, H + 4), pygame.SRCALPHA)
    base_a = 158 if near else 84
    a = max(46, int(base_a - f * 40))
    cx, cy = L / 2.0, (H + 4) / 2.0
    rx = L / 2.0 - 1
    ry = max(1.5, (H * (1.0 - 0.45 * f)) / 2.0)
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
        pygame.draw.line(surf, (230, 248, 255, min(215, a + 80)),
                         (sx, cy - dy * 0.55), (sx + 5, cy + dy * 0.35), 1)
    # Faint violet rim so the blade edge survives the outline pass.
    pygame.draw.ellipse(surf, (*VIOLET, min(185, a + 30)),
                        (1, int(cy - ry), L - 2, int(ry * 2)), 1)
    return surf


def _leg(surf, p0, knee, p1, core, rim=None):
    """Hair-thin jointed leg. When a rim colour is given, a 2px steel underlay
    keeps the near-black core from vanishing against the dark night biome."""
    pts = [p0, knee, p1]
    if rim is not None:
        pygame.draw.lines(surf, rim, False, pts, 2)
    pygame.draw.lines(surf, core, False, pts, 1)


def build_mosquito_midnight(wing_angle_deg):
    surf = _new()
    # _WING_ANGLES runs 50→-40, so f: 1.0 (wing high/back) … 0.0 (low/forward).
    f = _flap(wing_angle_deg)

    # ── far legs (behind the body, dimmer + offset so all 6 legs read) ──
    #   front pair forward-down, mid pair straight down, hind pair kicking up.
    for p0, knee, p1 in (
        ((37, 47), (46, 52), (53, 55)),     # front · forward-down
        ((34, 48), (37, 54), (39, 61)),     # mid   · straight down
        ((30, 47), (24, 48), (16, 41)),     # hind  · kicks up-and-back
    ):
        _leg(surf, p0, knee, p1, BODY_D)

    # ── far wing (a dim, smaller hint of the second wing, tucked behind) ──
    fw = _mosq_wing(f, near=False)
    fax = 24 + int((1.0 - f) * 5)
    fay = 20 + int((1.0 - f) * 9)
    _rot_blit(surf, pygame.transform.rotozoom(fw, -8 + f * 58, 0.78), (fax, fay))

    # ── abdomen: a long banded spike trailing down-and-back to a sharp point —
    #   the pointed rear that separates a mosquito from a fly. Kept slim and
    #   given a steel underside rim so it reads as its own shape past the legs ──
    for i, (x, y, ex, ey) in enumerate((
        (29, 45, 6, 6), (25, 48, 5, 5), (21, 51, 5, 4),
        (17, 54, 4, 4), (13, 56, 3, 3),
    )):
        _aaellipse(surf, BODY if i % 2 == 0 else MID, (x, y), ex, ey)
    pygame.draw.polygon(surf, BODY_D, [(13, 54), (13, 59), (6, 60)])  # sharp tip
    pygame.draw.lines(surf, MID, False,                               # underside rim
                      [(28, 48), (20, 53), (13, 57), (7, 59)], 1)
    for x, y in ((26, 47), (21, 50), (16, 53)):                       # banding seams
        pygame.draw.line(surf, BODY_D, (x + 2, y - 3), (x - 2, y + 3), 1)

    # ── thorax: compact arched indigo hump with a cool top rim-light, notched
    #   off the abdomen so the two masses don't fuse into one blob ──
    _aaellipse(surf, BODY_D, (BCX + 1, BCY - 3), 8, 7)
    _aaellipse(surf, BODY, (BCX, BCY - 4), 7, 6)
    pygame.draw.line(surf, BODY_D, (BCX - 4, BCY + 2), (BCX - 8, BCY + 5), 1)
    _aaellipse(surf, RIMLIGHT, (BCX - 3, BCY - 9), 4, 2)

    # ── near legs (over the body; steel rim keeps them alive at night) ──
    for p0, knee, p1 in (
        ((36, 48), (44, 54), (50, 58)),     # front · forward-down
        ((33, 49), (34, 56), (34, 63)),     # mid   · straight down
        ((30, 48), (24, 46), (17, 42)),     # hind  · kicks up-and-back
    ):
        _leg(surf, p0, knee, p1, BODY, rim=MID)

    # ── near wing: a single narrow blade lifted up-and-back off the thorax with
    #   a sky gap; its anchor + tilt travel across the flap so the cycle reads.
    #   High/back on the up-stroke (f→1), low/forward on the down-stroke (f→0) ──
    nw = _mosq_wing(f, near=True)
    nax = 25 + int((1.0 - f) * 6)
    nay = 19 + int((1.0 - f) * 10)
    _rot_blit(surf, pygame.transform.rotate(nw, -16 + f * 66), (nax, nay))

    # ── head + the single magenta compound eye (dialled back ~25%) ──
    _aaellipse(surf, BODY_D, (HCX - 2, HCY + 2), 5, 5)
    pygame.draw.circle(surf, BODY, (HCX, HCY), 7)
    pygame.draw.circle(surf, EYE_MAG, (HCX, HCY), 6)
    pygame.draw.circle(surf, (150, 44, 78), (HCX, HCY), 6, 1)
    for dx, dy in ((-2, -2), (2, -2), (3, 1), (-1, 3), (1, 2)):
        pygame.draw.circle(surf, EYE_HI, (HCX + dx, HCY + dy), 1)
    # Catchlight kept in the upper-forward quadrant (toward the needle).
    pygame.draw.circle(surf, (255, 240, 250), (HCX + 2, HCY - 3), 2)

    # ── feathery antennae rising up-forward off the crown ──
    for ax in (HCX, HCX + 4):
        tipx, tipy = ax + 4, HCY - 12
        pygame.draw.line(surf, MID, (ax, HCY - 5), (tipx, tipy), 1)
        for t in (0.35, 0.65):              # plumose barbs
            bx = int(ax + (tipx - ax) * t)
            by = int((HCY - 5) + (tipy - (HCY - 5)) * t)
            pygame.draw.line(surf, MID, (bx, by), (bx - 2, by - 1), 1)

    # ── HERO: the long hair-thin proboscis needle — the longest single element
    #   in the silhouette — dead-horizontal from below the eye to the far edge ──
    NY = HCY + 4
    pygame.draw.polygon(surf, BODY, [(40, NY - 1), (40, NY + 2), (60, NY)])
    pygame.draw.line(surf, TEAL, (42, NY - 1), (59, NY - 1), 1)   # pale top ridge
    # Two short forked palps flanking the base.
    pygame.draw.line(surf, MID, (41, NY), (45, NY - 3), 1)
    pygame.draw.line(surf, MID, (41, NY), (45, NY + 3), 1)
    return surf


build = _make_prebuilt_skin(build_mosquito_midnight)
