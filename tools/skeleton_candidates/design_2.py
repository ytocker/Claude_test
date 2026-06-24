"""SKELETON costume — design_2 MARIGOLD CALAVERA (scratch exploration only).

A Dia de Muertos sugar-skull macaw: warm-ivory bone is the brightest base,
painted LOUD with marigold/magenta/cyan calavera decoration and crowned by an
arc of petals rising past the skull. The colour sits ON the bone, so the
skeleton read (skull + sockets + ribcage + spine + limb bones) survives even
when the paint flattens at 40px — the festive layer is the third tell, never
the load-bearing one.

Wrapped via store_skins._make_prebuilt_skin so it composes exactly like the
production calavera redraw, but is NEVER registered in BUILDERS.
"""
from __future__ import annotations
import math
import pygame

from game.store_skins import SPRITE_W, SPRITE_H, _poly, _make_prebuilt_skin
from game.parrot import _aaellipse

# Warm ivory is the brightest element; everything painted reads as decoration
# layered over it, so dropping the colour still leaves a legible skeleton.
_CB_BODY   = (34, 24, 38)          # #221826 dark "flesh" — frames the bone
_CB_BODY_D = (24, 16, 28)
_CB_BONE   = (251, 243, 222)       # #FBF3DE warm ivory — brightest base
_CB_BONE_D = (210, 198, 168)       # under-edge for bone roundness
_CB_SOCK   = (20, 14, 24)          # hollow socket interior
_TH_MARI   = (255, 138, 30)        # #FF8A1E marigold orange — crown/theme
_TH_MARI_D = (214, 104, 12)
_TH_MAG    = (255, 46, 136)        # #FF2E88 calavera magenta — heart/accents
_TH_CYAN   = (22, 200, 216)        # #16C8D8 cyan — socket rings/swirls


def _petal(surf, cx, cy, ang, length, color, color_d):
    """A single marigold/magenta petal as a teardrop, pointing along ``ang``.
    Used for the crown arc and the bloom/anklet accents — kept >=2px so it
    never dissolves at downscale."""
    tx = cx + math.cos(ang) * length
    ty = cy + math.sin(ang) * length
    px = -math.sin(ang)
    py = math.cos(ang)
    wid = max(2, length * 0.42)
    base_l = (cx + px * wid * 0.5, cy + py * wid * 0.5)
    base_r = (cx - px * wid * 0.5, cy - py * wid * 0.5)
    mid_l = (cx + math.cos(ang) * length * 0.55 + px * wid,
             cy + math.sin(ang) * length * 0.55 + py * wid)
    mid_r = (cx + math.cos(ang) * length * 0.55 - px * wid,
             cy + math.sin(ang) * length * 0.55 - py * wid)
    _poly(surf, color, [base_l, mid_l, (tx, ty), mid_r, base_r])
    pygame.draw.line(surf, color_d, base_l, (tx, ty), 1)


def _bloom(surf, cx, cy, r, petal_color, petal_d, core_color):
    """A small radial flower — marigold bloom for nose/chin and anklets."""
    for i in range(6):
        a = i * (math.pi / 3.0)
        _petal(surf, cx, cy, a, r, petal_color, petal_d)
    pygame.draw.circle(surf, core_color, (int(cx), int(cy)), max(2, int(r * 0.35)))


def _cal_wing(angle_deg):
    """Wing rendered as ivory finger-bones (phalanges) fanning from a wrist
    knuckle, tipped with tiny petal accents so the flap reads as a painted
    calavera wing. Drawn upright, then rotated to the flap pose."""
    w = pygame.Surface((52, 52), pygame.SRCALPHA)
    # Dark webbing behind the bones so ivory pops on bright sky.
    pts = [(24, 26), (47, 13), (51, 30), (34, 45), (17, 41)]
    _poly(w, _CB_BODY, pts)
    pygame.draw.polygon(w, _CB_BODY_D, pts, 1)

    wrist = (25, 28)
    # Three radiating finger-bones with knuckle knobs.
    tips = ((47, 16), (50, 27), (40, 42))
    for tx, ty in tips:
        pygame.draw.line(w, _CB_BONE, wrist, (tx, ty), 2)
        pygame.draw.circle(w, _CB_BONE, (tx, ty), 2)
        pygame.draw.circle(w, _CB_BONE_D, (tx, ty), 2, 1)
    pygame.draw.circle(w, _CB_BONE, wrist, 3)          # wrist knuckle
    pygame.draw.circle(w, _CB_BONE_D, wrist, 3, 1)
    # Petal accents at the wrist — the calavera tell on the wing.
    _petal(w, wrist[0] - 1, wrist[1] + 1, math.radians(150), 6, _TH_MARI, _TH_MARI_D)
    _petal(w, wrist[0] - 2, wrist[1] + 4, math.radians(110), 5, _TH_MAG, _TH_MARI_D)
    return pygame.transform.rotate(w, angle_deg)


def _build_design2(wing_angle_deg):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)

    # Tail — dark fan.
    _poly(surf, _CB_BODY, [(2, 26), (17, 24), (23, 36), (12, 42)])
    pygame.draw.polygon(surf, _CB_BODY_D, [(2, 26), (17, 24), (23, 36), (12, 42)], 1)

    # Body + head silhouette (dark flesh framing the bone).
    _aaellipse(surf, _CB_BODY_D, (33, 33), 19, 14)
    _aaellipse(surf, _CB_BODY, (32, 32), 18, 13)
    _aaellipse(surf, _CB_BODY_D, (48, 22), 13, 12)
    _aaellipse(surf, _CB_BODY, (47, 21), 12, 11)

    # ── SPINE — vertebra column dotted with marigold beads.
    spine_pts = [(36, 25), (32, 29), (28, 33), (24, 37)]
    for i in range(len(spine_pts) - 1):
        pygame.draw.line(surf, _CB_BONE, spine_pts[i], spine_pts[i + 1], 2)
    for i, (vx, vy) in enumerate(spine_pts):
        pygame.draw.circle(surf, _CB_BONE, (vx, vy), 2)
        if i % 2 == 1:
            pygame.draw.circle(surf, _TH_MARI, (vx, vy), 1)

    # ── RIBCAGE — chunky ivory arcs; alternate ribs carry cyan dot+swirl.
    for j, off in enumerate((-5, 0, 5)):
        rect = (24 + off, 24, 13, 16)
        pygame.draw.arc(surf, _CB_BONE, rect,
                        math.radians(200), math.radians(340), 2)
        if j % 2 == 0:                              # cyan accent on alt ribs
            ax = 30 + off
            pygame.draw.circle(surf, _TH_CYAN, (ax, 35), 2)
            pygame.draw.arc(surf, _TH_CYAN, (ax - 2, 33, 6, 6),
                            math.radians(0), math.radians(180), 2)

    # Wing (over ribs, under skull).
    wing = _cal_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    # ── SKULL — bright ivory dome, the brightest mass on the bird.
    _aaellipse(surf, _CB_BONE, (47, 21), 10, 9)
    _aaellipse(surf, _CB_BONE_D, (47, 26), 7, 3)        # jaw shadow

    # Flower-crown — arc of marigold + magenta petals rising past the crown.
    # This broken-upward bloom is the hero 40px tell.
    cx, cy = 47, 12
    for k in range(7):
        a = math.radians(-160 + k * (140.0 / 6.0))    # fan across the top
        col, cold = (_TH_MARI, _TH_MARI_D) if k % 2 == 0 else (_TH_MAG, _TH_MARI_D)
        _petal(surf, cx, cy, a, 7, col, cold)
    pygame.draw.circle(surf, _TH_MARI, (cx, cy), 2)

    # Eye sockets ringed with cyan petal-loops.
    for ex, ey in ((50, 19), (44, 20)):
        pygame.draw.circle(surf, _CB_SOCK, (ex, ey), 3)
        for p in range(6):
            a = p * (math.pi / 3.0)
            lx = ex + math.cos(a) * 4
            ly = ey + math.sin(a) * 4
            pygame.draw.circle(surf, _TH_CYAN, (int(lx), int(ly)), 1)
        pygame.draw.circle(surf, _TH_CYAN, (ex, ey), 4, 1)

    # Magenta heart/flower glyph on the forehead.
    hx, hy = 47, 14
    pygame.draw.circle(surf, _TH_MAG, (hx - 1, hy), 2)
    pygame.draw.circle(surf, _TH_MAG, (hx + 1, hy), 2)
    _poly(surf, _TH_MAG, [(hx - 2, hy + 1), (hx + 2, hy + 1), (hx, hy + 4)])

    # Marigold bloom at the nose/chin.
    _bloom(surf, 47, 24, 3, _TH_MARI, _TH_MARI_D, _TH_MAG)

    # Wide toothy grin with painted colour gaps.
    gy0, gy1 = 27, 30
    pygame.draw.line(surf, _CB_BONE, (43, gy0), (51, gy0), 2)
    grin_cols = (_TH_MARI, _CB_BONE_D, _TH_MAG, _CB_BONE_D, _TH_CYAN)
    for i, gx in enumerate(range(43, 52, 2)):
        pygame.draw.line(surf, grin_cols[i % len(grin_cols)], (gx, gy0), (gx, gy1), 1)

    # Beak — ivory bone outline over a dark beak.
    beak_pts = [(56, 21), (62, 24), (59, 28), (53, 26)]
    _poly(surf, _CB_BODY, beak_pts)
    pygame.draw.polygon(surf, _CB_BONE, beak_pts, 2)

    # ── LEG BONES — ivory pair, each with a single marigold anklet bloom.
    for lx0, lx1 in ((28, 27), (34, 35)):
        pygame.draw.line(surf, _CB_BONE, (lx0, 44), (lx1, 49), 2)
        pygame.draw.circle(surf, _CB_BONE, (lx0, 44), 2)
        _bloom(surf, lx1, 49, 2, _TH_MARI, _TH_MARI_D, _TH_MAG)

    return surf


build = _make_prebuilt_skin(_build_design2)
