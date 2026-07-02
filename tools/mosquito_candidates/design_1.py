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
BLUE    = (60, 110, 215)        # #3C6ED7 cool blue — coolest oil-slick stop
TEAL    = (94, 200, 229)        # #5EC8E5 iridescent teal sheen
VIOLET  = (142, 63, 214)        # #8E3FD6 wing shimmer (pushed to the root now)
# Eye kept muted so the cool wing stays the brightest thing in the silhouette.
EYE_MAG = (146, 53, 84)         # muted compound-eye magenta
EYE_HI  = (232, 138, 174)       # magenta rim light
RIMLIGHT = (120, 150, 210)      # cool thorax rim highlight
LEG_HI  = (78, 100, 165)        # steel near-leg so 1px legs survive the night


def _mosq_wing(f, near):
    """A single narrow iridescent blade, root at the RIGHT (thorax) end, tip at
    the LEFT. Three oil-slick stops run the full visible length — violet tip →
    cool blue mid → teal root — so the blade never flattens into one magenta
    streak and its cool/green end reads apart from the warm compound eye. A
    specular streak slides with the flap phase, and a vertical squash thins the
    blade toward the top of the up-stroke so it reads as a lifted shape."""
    L, H = 32, 8
    surf = pygame.Surface((L, H + 4), pygame.SRCALPHA)
    base_a = 168 if near else 88
    a = max(48, int(base_a - f * 40))
    cx, cy = L / 2.0, (H + 4) / 2.0
    rx = L / 2.0 - 1
    ry = max(1.5, (H * (1.0 - 0.45 * f)) / 2.0)
    for x in range(L):
        t = x / (L - 1)                     # 0 tip(violet) → 1 root(teal)
        if t < 0.5:                         # violet tip → cool blue mid
            u = t / 0.5
            col = tuple(int(VIOLET[i] + (BLUE[i] - VIOLET[i]) * u) for i in range(3))
        else:                               # cool blue mid → teal root
            u = (t - 0.5) / 0.5
            col = tuple(int(BLUE[i] + (TEAL[i] - BLUE[i]) * u) for i in range(3))
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
        pygame.draw.line(surf, (230, 248, 255, min(220, a + 80)),
                         (sx, cy - dy * 0.55), (sx + 5, cy + dy * 0.35), 1)
    # Cool-blue rim so the blade edge survives the outline pass without warming
    # back toward the eye's magenta.
    pygame.draw.ellipse(surf, (*BLUE, min(195, a + 30)),
                        (1, int(cy - ry), L - 2, int(ry * 2)), 1)
    return surf


def _leg(surf, p0, knee, p1, core, rim=None, w=1):
    """Hair-thin jointed leg. Near legs stay a single 1px line so the six of
    them splay wide without fattening into a blob; when a rim colour is given a
    faint underlay keeps a near-black core alive against the dark night biome."""
    pts = [p0, knee, p1]
    if rim is not None:
        pygame.draw.lines(surf, rim, False, pts, w + 1)
    pygame.draw.lines(surf, core, False, pts, w)


def build_mosquito_midnight(wing_angle_deg):
    surf = _new()
    # _WING_ANGLES runs 50→-40, so f: 1.0 (wing high/back) … 0.0 (low/forward).
    f = _flap(wing_angle_deg)

    # ── far legs (behind the body, dimmer + offset so all 6 legs read) ──
    #   front pair forward-down, mid pair straight down, hind pair kicking up.
    for p0, knee, p1 in (
        ((37, 47), (47, 53), (55, 57)),     # front · forward-down, splayed out
        ((34, 48), (37, 56), (39, 64)),     # mid   · straight down
        ((30, 47), (20, 45), (3, 37)),      # hind  · long up-kick past abdomen
    ):
        _leg(surf, p0, knee, p1, BODY_D)

    # ── far wing (a dim, smaller hint of the second wing, tucked behind) ──
    fw = _mosq_wing(f, near=False)
    fax = 27 + int((1.0 - f) * 5)
    fay = 22 + int((1.0 - f) * 8)
    _rot_blit(surf, pygame.transform.rotozoom(fw, -8 + f * 58, 0.78), (fax, fay))

    # ── abdomen: a long banded spike trailing down-and-back to a sharp point —
    #   the pointed rear that separates a mosquito from a fly. Kept slim and
    #   given a steel underside rim so it reads as its own shape past the legs ──
    for i, (x, y, ex, ey) in enumerate((
        (29, 45, 6, 6), (25, 49, 5, 5), (20, 53, 5, 4),
        (16, 57, 4, 4), (11, 60, 3, 3),
    )):
        _aaellipse(surf, BODY if i % 2 == 0 else MID, (x, y), ex, ey)
    pygame.draw.polygon(surf, BODY_D, [(11, 58), (11, 63), (3, 64)])  # sharp tip
    pygame.draw.lines(surf, MID, False,                               # underside rim
                      [(28, 48), (20, 54), (12, 59), (4, 63)], 1)
    for x, y in ((26, 47), (20, 51), (15, 55)):                       # banding seams
        pygame.draw.line(surf, BODY_D, (x + 2, y - 3), (x - 2, y + 3), 1)

    # ── thorax: compact arched indigo hump with a cool top rim-light, notched
    #   off the abdomen so the two masses don't fuse into one blob ──
    _aaellipse(surf, BODY_D, (BCX + 1, BCY - 3), 8, 7)
    _aaellipse(surf, BODY, (BCX, BCY - 4), 7, 6)
    pygame.draw.line(surf, BODY_D, (BCX - 4, BCY + 2), (BCX - 8, BCY + 5), 1)
    _aaellipse(surf, RIMLIGHT, (BCX - 3, BCY - 9), 4, 2)

    # ── near legs (over the body; steel rim keeps them alive at night) ──
    for p0, knee, p1 in (
        ((36, 48), (45, 55), (53, 60)),     # front · forward-down, splayed out
        ((33, 49), (33, 57), (32, 65)),     # mid   · straight down
        ((30, 48), (18, 45), (4, 38)),      # hind  · long up-kick past abdomen
    ):
        _leg(surf, p0, knee, p1, LEG_HI, w=1)

    # ── near wing: a single narrow blade hinged off the thorax top with just a
    #   sky gap; its anchor + tilt travel across the flap so the cycle reads.
    #   High/back on the up-stroke (f→1), low/forward on the down-stroke (f→0).
    #   A short dark stalk bridges blade root to thorax so the wing reads as
    #   hinged, not a detached shard floating in the gap ──
    nw = _mosq_wing(f, near=True)
    nax = 29 + int((1.0 - f) * 6)
    nay = 23 + int((1.0 - f) * 9)
    pygame.draw.line(surf, BODY, (31, 36), (nax, nay + 3), 3)   # hinge stalk
    _rot_blit(surf, pygame.transform.rotate(nw, -16 + f * 66), (nax, nay))

    # ── head + the single magenta compound eye, kept muted so it never
    #   out-shouts the cool wing or the proboscis. One catchlight only ──
    _aaellipse(surf, BODY_D, (HCX - 2, HCY + 2), 5, 5)
    pygame.draw.circle(surf, BODY, (HCX, HCY), 7)
    pygame.draw.circle(surf, EYE_MAG, (HCX, HCY), 6)
    pygame.draw.circle(surf, (128, 40, 70), (HCX, HCY), 6, 1)
    # A single upper-forward catchlight (toward the needle) — no facet cluster,
    # so the eye stays one quiet mass instead of a second sparkle field.
    pygame.draw.circle(surf, (236, 196, 214), (HCX + 2, HCY - 3), 2)

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
