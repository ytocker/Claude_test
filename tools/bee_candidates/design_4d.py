"""BUG/INSECT redesign — design_4d PAINTED LADY (Vanessa cardui).

The world's most widespread butterfly, carved from the MONARCH's rounded
playing-card wing and stained-glass bones but painted in its own multi-zone
livery: a warm salmon-tawny field, a pale cream hindwing zone streaked with
buff, and — the species' signature — a heavy black apex patch on the forewing
corner peppered with white spots.  More complex and multi-zone than the flat
orange MONARCH, yet still built on raw value contrast (dark bones + bright
field) so the read holds on both day and night sky without a glow.

Scratch exploration only — NOT registered in store_skins.BUILDERS. Production
art stays untouched until a winner is picked.
"""
import pygame

from game.parrot import _aaellipse
from tools.bee_candidates._shared_monarch import (
    _WING_R, _centroid, _inset, _transform, _wing_mask, _new,
    _flap, draw_body, draw_head, make_build,
    COMPOSITE_W, COMPOSITE_H, BCX, BCY,
)

# ── palette ──────────────────────────────────────────────────────────────────
TAWNY = (240, 140, 88)     # #F08C58 — pale salmon field; peachier than MONARCH orange
PEACH = (247, 176, 136)    # #F7B088 — warm forewing inner highlight
CREAM = (240, 226, 192)    # #F0E2C0 — pale central hindwing zone
INK   = (26, 19, 14)       # #1A130E — veins, margin, apex patch, body
FLAKE = (245, 241, 230)    # #F5F1E6 — white spots inside the black apex patch


def _draw_wing(surf, side, spread, nx):
    margin = _transform(_WING_R, side, spread, nx)
    fill = _inset(margin, 0.14)                      # thick ~6px black margin

    # Black margin first (the separator that carries the read on any sky), then
    # the salmon field covering every cell right up to the bones.
    pygame.draw.polygon(surf, INK, margin)
    pygame.draw.polygon(surf, TAWNY, fill)

    fcx, fcy = _centroid(fill)
    rx, ry = margin[0]                               # wing root (inner-top)
    root = (rx + (fcx - rx) * 0.42, ry + (fcy - ry) * 0.42)

    # Warm core: the wing runs peachier near the thorax root and cools to tawny
    # at the edges — a painted-lady body-glow rather than a hard gradient ring.
    core = _new()
    for r, col, a in ((16, TAWNY, 140), (11, PEACH, 170), (6, PEACH, 210)):
        _aaellipse(core, (*col, a), root, r, r * 0.82)
    core.blit(_wing_mask(fill), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(core, (0, 0))

    # Pale cream hindwing zone — a distinct pale patch sitting INSIDE the central
    # hindwing (not on the rim), framed by salmon below and outboard. Anchored on
    # the three lower-hindwing points but pulled hard toward the centroid so the
    # orange field rings it. Painted at full alpha for a clean read, then
    # MIN-clipped to the wing so it never bleeds past the black margin.
    def _pull(p, frac):
        return (p[0] + (fcx - p[0]) * frac, p[1] + (fcy - p[1]) * frac)
    cream = _new()
    # A rounded pale lobe: an outer arc sitting inside the margin (orange still
    # frames it below + outboard) rising to a single inner point near the
    # centroid — enough area to read as its own zone rather than a sliver.
    zone = [_pull(fill[6], 0.26), _pull(fill[7], 0.24),
            _pull(fill[8], 0.26), _pull(fill[9], 0.32),
            _pull(fill[7], 0.58)]
    pygame.draw.polygon(cream, (*CREAM, 255), zone)
    cream.blit(_wing_mask(fill), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(cream, (0, 0))

    # Black apex patch — the Painted Lady's signature. A dark wedge over the
    # forewing outer corner (leading rise → apex → outer shoulder → trailing).
    apex = [fill[1], fill[2], fill[3], fill[4]]
    pygame.draw.polygon(surf, INK, apex)

    # White spots scattered inside the black apex patch — a visible cluster spaced
    # along the apex diagonal (apex tip → outer shoulder), pulled only lightly to
    # centre so they stay spread across the patch instead of clumping.
    acx = sum(p[0] for p in apex) / 4
    acy = sum(p[1] for p in apex) / 4

    def _mix(a, b, t):
        return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
    for sp in (_mix(fill[2], fill[3], 0.15),
               _mix(fill[2], fill[3], 0.55),
               _mix(fill[1], fill[2], 0.55),
               _mix(fill[2], fill[3], 0.85),
               _mix(fill[3], fill[4], 0.35)):
        px = sp[0] + (acx - sp[0]) * 0.12
        py = sp[1] + (acy - sp[1]) * 0.12
        pygame.draw.circle(surf, FLAKE, (int(px), int(py)), 1)

    # Heavy black veins radiating from the thorax root — the same stained-glass
    # carve as the MONARCH so it reads as the SAME bug, re-liveried. The ribs
    # inside the apex patch simply vanish into the black, which is correct.
    for idx in (2, 3, 4, 6, 7):
        pygame.draw.line(surf, INK, root, fill[idx], 2)
    pygame.draw.line(surf, INK, root, fill[1], 1)
    pygame.draw.line(surf, INK, root, fill[8], 1)

    # White margin flecks — confined to the forewing edge only. Kept entirely off
    # the hindwing rim so nothing specks into the pale cream zone below.
    outer = margin[1:6]
    for i in range(len(outer) - 1):
        a0, a1 = outer[i], outer[i + 1]
        ox = a0[0] + (fcx - a0[0]) * 0.14
        oy = a0[1] + (fcy - a0[1]) * 0.14
        pygame.draw.circle(surf, FLAKE, (int(ox), int(oy)), 1)
        for t in (0.0, 0.5):
            ex = a0[0] + (a1[0] - a0[0]) * t
            ey = a0[1] + (a1[1] - a0[1]) * t
            ix = ex + (fcx - ex) * 0.30
            iy = ey + (fcy - ey) * 0.30
            pygame.draw.circle(surf, FLAKE, (int(ix), int(iy)), 1)


build = make_build(
    lambda surf, side, spread, nx: _draw_wing(surf, side, spread, nx),
    ink=INK, flake=FLAKE, ring_col=TAWNY, club_col=PEACH,
)
