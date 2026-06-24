"""SKELETON costume — design_2 MARIGOLD CALAVERA (scratch exploration only).

A Dia de Muertos sugar-skull macaw. Round 2 reorders the read so it lands
skull-first, colour-second: the skull dome and the front rib-arcs are pushed
to near-white (the brightest mass on the bird), warm ivory survives only as
under-edge shading, and the festive marigold/magenta/cyan paint is seasoning
on a skeleton that already parses at 40px.

The earlier dark shoulder mantle is gone — that was lich vocabulary, not
calavera; the ribcage now reads in the open against the dark flesh. The
ribcage is a bold paired-arc ladder with clean dark rungs between, the crown
is a set of DISCRETE petal-points (dark slivers between) so the silhouette
spikes upward, and the ivory finger-bones fan out to trace each flap pose.

Wrapped via store_skins._make_prebuilt_skin so it composes exactly like the
production calavera redraw, but is NEVER registered in BUILDERS.
"""
from __future__ import annotations
import math
import pygame

from game.store_skins import SPRITE_W, SPRITE_H, _poly, _make_prebuilt_skin
from game.parrot import _aaellipse

# Bone is the brightest base: lit faces go near-white so the eye lands on the
# skull before any colour; warm ivory survives only as the under-edge that
# gives the bone its roundness. Colour is a third tell layered on top.
_CB_BODY   = (34, 24, 38)          # #221826 dark "flesh" — frames the bone
_CB_BODY_D = (24, 16, 28)
_CB_BONE   = (255, 252, 239)       # #FFFCEF near-white — BRIGHTEST lit bone
_CB_BONE_D = (251, 243, 222)       # #FBF3DE warm ivory — under-edge only
_CB_KEY    = (34, 24, 38)          # #221826 keyline on sky-facing bone edges
_CB_SOCK   = (20, 14, 24)          # hollow socket interior
_TH_MARI   = (255, 138, 30)        # #FF8A1E marigold orange — crown/theme
_TH_MARI_D = (214, 104, 12)
_TH_MAG    = (255, 46, 136)        # #FF2E88 calavera magenta — heart/accents
_TH_CYAN   = (22, 200, 216)        # #16C8D8 cyan — socket rings


def _petal(surf, cx, cy, ang, length, color, color_d):
    """A single marigold/magenta petal as a teardrop, pointing along ``ang``.
    Used for the crown points and the bloom/anklet accents — kept >=2px so it
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
    """A small radial flower — marigold bloom for the chin and anklets."""
    for i in range(6):
        a = i * (math.pi / 3.0)
        _petal(surf, cx, cy, a, r, petal_color, petal_d)
    pygame.draw.circle(surf, core_color, (int(cx), int(cy)), max(2, int(r * 0.35)))


def _cal_wing(angle_deg):
    """Wing rendered as ivory finger-bones (phalanges) fanning from a wrist
    knuckle so the flap reads as a clattering skeletal wing in every pose.
    The bones span the full webbing so the skeletal read survives the flap;
    a single petal accent at the wrist is the only calavera tell here, so the
    bone never competes with paint. Drawn upright, then rotated to the pose."""
    w = pygame.Surface((52, 52), pygame.SRCALPHA)
    # Faint dark webbing so the bright finger-bones pop on a bright sky.
    pts = [(24, 26), (47, 13), (51, 30), (34, 45), (17, 41)]
    _poly(w, _CB_BODY, pts)
    pygame.draw.polygon(w, _CB_BODY_D, pts, 1)

    wrist = (24, 28)
    # Finger-bones reach to the wing extremities so the flap clatters.
    tips = ((47, 14), (50, 24), (45, 36), (33, 44))
    for tx, ty in tips:
        pygame.draw.line(w, _CB_BONE_D, wrist, (tx, ty), 3)   # bone underside
        pygame.draw.line(w, _CB_BONE, wrist, (tx, ty), 2)     # lit bone
        pygame.draw.circle(w, _CB_BONE, (tx, ty), 2)          # knuckle knob
        pygame.draw.circle(w, _CB_BONE_D, (tx, ty), 2, 1)
    pygame.draw.circle(w, _CB_BONE, wrist, 3)                 # wrist knuckle
    pygame.draw.circle(w, _CB_BONE_D, wrist, 3, 1)
    # One petal at the wrist — the wing's calavera tell, no bone-eating noise.
    _petal(w, wrist[0] - 1, wrist[1] + 2, math.radians(120), 6, _TH_MARI, _TH_MARI_D)
    return pygame.transform.rotate(w, angle_deg)


def _build_design2(wing_angle_deg):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)

    # Tail — dark fan.
    _poly(surf, _CB_BODY, [(2, 26), (17, 24), (23, 36), (12, 42)])
    pygame.draw.polygon(surf, _CB_BODY_D, [(2, 26), (17, 24), (23, 36), (12, 42)], 1)

    # Body + head silhouette (dark flesh framing the open bone — no mantle).
    _aaellipse(surf, _CB_BODY_D, (33, 33), 19, 14)
    _aaellipse(surf, _CB_BODY, (32, 32), 18, 13)
    _aaellipse(surf, _CB_BODY_D, (48, 22), 13, 12)
    _aaellipse(surf, _CB_BODY, (47, 21), 12, 11)

    # ── SPINE — vertebra column dotted with a few marigold beads.
    spine_pts = [(36, 25), (32, 29), (28, 33), (24, 37)]
    for i in range(len(spine_pts) - 1):
        pygame.draw.line(surf, _CB_BONE, spine_pts[i], spine_pts[i + 1], 2)
    for i, (vx, vy) in enumerate(spine_pts):
        pygame.draw.circle(surf, _CB_BONE, (vx, vy), 2)
        if i % 2 == 1:
            pygame.draw.circle(surf, _TH_MARI, (vx, vy), 1)

    # ── RIBCAGE — a bold paired-arc LADDER. Five ivory rib-arcs with a clean
    # dark #221826 rung between each, plus a vertical sternum line down the
    # centre. No per-rib dots/swirls — those read as noise at 40px.
    cx_rib = 30
    pygame.draw.line(surf, _CB_BODY, (cx_rib, 25), (cx_rib, 39), 3)  # dark gap base
    for j, ry in enumerate(range(26, 40, 3)):                        # 5 rungs
        half = 8 - j                                                 # taper down
        rect = (cx_rib - half, ry - 6, half * 2, 12)
        pygame.draw.arc(surf, _CB_BONE_D, rect,                      # under-edge
                        math.radians(210), math.radians(330), 3)
        pygame.draw.arc(surf, _CB_BONE, rect,                        # bright rib
                        math.radians(210), math.radians(330), 2)
    pygame.draw.line(surf, _CB_BONE, (cx_rib, 25), (cx_rib, 38), 2)  # sternum

    # Wing (over ribs, under skull).
    wing = _cal_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    # ── SKULL — bright near-white dome, the brightest mass on the bird.
    _aaellipse(surf, _CB_BONE_D, (47, 22), 10, 9)       # ivory under-shell
    _aaellipse(surf, _CB_BONE, (47, 20), 10, 8)         # near-white lit dome
    _aaellipse(surf, _CB_BONE_D, (47, 26), 7, 3)        # jaw shadow
    # 1px dark keyline on the sky-facing crown so the dome holds on day biome.
    pygame.draw.arc(surf, _CB_KEY, (37, 11, 20, 20),
                    math.radians(20), math.radians(160), 1)

    # ── FLOWER-CROWN — 6 DISCRETE petal-points fanned across the top, each
    # separated by a dark #221826 sliver so the silhouette spikes upward and
    # reads as a flower-crown, not one magenta blob.
    crx, cry = 47, 12
    petal_cols = ((_TH_MARI, _TH_MARI_D), (_TH_MAG, _TH_MARI_D),
                  (_TH_MARI, _TH_MARI_D), (_TH_MARI, _TH_MARI_D),
                  (_TH_MAG, _TH_MARI_D), (_TH_MARI, _TH_MARI_D))
    n = len(petal_cols)
    for k in range(n):
        a = math.radians(-148 + k * (116.0 / (n - 1)))
        col, cold = petal_cols[k]
        # Dark sliver root first so each point separates cleanly.
        rx = crx + math.cos(a) * 2
        ry = cry + math.sin(a) * 2
        pygame.draw.line(surf, _CB_BODY, (crx, cry), (rx, ry), 3)
        _petal(surf, crx, cry, a, 8, col, cold)
    pygame.draw.circle(surf, _CB_BODY, (crx, cry), 2)   # dark crown hub

    # Eye sockets ringed with the cyan loop — the best-surviving face anchor.
    for ex, ey in ((50, 19), (44, 20)):
        pygame.draw.circle(surf, _CB_SOCK, (ex, ey), 3)
        for p in range(6):
            a = p * (math.pi / 3.0)
            lx = ex + math.cos(a) * 4
            ly = ey + math.sin(a) * 4
            pygame.draw.circle(surf, _TH_CYAN, (int(lx), int(ly)), 1)
        pygame.draw.circle(surf, _TH_CYAN, (ex, ey), 4, 1)

    # Single small magenta heart glyph on the forehead — ~30% smaller and set
    # low so it doesn't merge with the crown's magenta.
    hx, hy = 47, 15
    pygame.draw.circle(surf, _TH_MAG, (hx - 1, hy), 1)
    pygame.draw.circle(surf, _TH_MAG, (hx + 1, hy), 1)
    _poly(surf, _TH_MAG, [(hx - 2, hy), (hx + 2, hy), (hx, hy + 3)])

    # Marigold bloom at the chin/nose.
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
        pygame.draw.line(surf, _CB_BONE_D, (lx0, 44), (lx1, 49), 3)
        pygame.draw.line(surf, _CB_BONE, (lx0, 44), (lx1, 49), 2)
        pygame.draw.circle(surf, _CB_BONE, (lx0, 44), 2)
        _bloom(surf, lx1, 49, 2, _TH_MARI, _TH_MARI_D, _TH_MAG)

    return surf


build = _make_prebuilt_skin(_build_design2)
