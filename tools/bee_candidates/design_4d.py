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
TAWNY = (228, 108, 42)     # #E46C2A — warm salmon-tawny, dominant wing field
PEACH = (245, 150, 80)     # #F59650 — warm forewing inner highlight
CREAM = (235, 218, 180)    # #EBDAB4 — pale central hindwing zone
INK   = (26, 19, 14)       # #1A130E — veins, margin, apex patch, body
FLAKE = (245, 241, 230)    # #F5F1E6 — white spots inside the black apex patch
BUFF  = (200, 175, 140)    # #C8AF8C — faint streaks across the hindwing zone


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

    # Pale cream hindwing zone — the lower half of the wing washes to buff-cream,
    # painted onto its own surface and MIN-clipped to the wing so it never bleeds
    # past the black margin.
    cream = _new()
    zone = [fill[5], fill[6], fill[7], fill[8], fill[9], (fcx, fcy)]
    pygame.draw.polygon(cream, (*CREAM, 180), zone)
    cream.blit(_wing_mask(fill), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(cream, (0, 0))

    # Faint buff streaks fanning across the cream zone — the hindwing texture.
    inner_root = ((root[0] + fcx) / 2, (root[1] + fcy) / 2)
    for idx in (6, 7, 8):
        pygame.draw.line(surf, BUFF, inner_root, fill[idx], 1)

    # Black apex patch — the Painted Lady's signature. A dark wedge over the
    # forewing outer corner (leading rise → apex → outer shoulder → trailing).
    apex = [fill[1], fill[2], fill[3], fill[4]]
    pygame.draw.polygon(surf, INK, apex)

    # White spots scattered inside the black apex patch.
    acx = sum(p[0] for p in apex) / 4
    acy = sum(p[1] for p in apex) / 4
    for sp in (fill[2], fill[3],
               ((fill[1][0] + fill[2][0]) / 2, (fill[1][1] + fill[2][1]) / 2),
               ((fill[2][0] + fill[3][0]) / 2, (fill[2][1] + fill[3][1]) / 2),
               (acx, acy)):
        px = sp[0] + (acx - sp[0]) * 0.34
        py = sp[1] + (acy - sp[1]) * 0.34
        pygame.draw.circle(surf, FLAKE, (int(px), int(py)), 1)

    # Heavy black veins radiating from the thorax root — the same stained-glass
    # carve as the MONARCH so it reads as the SAME bug, re-liveried. The ribs
    # inside the apex patch simply vanish into the black, which is correct.
    for idx in (2, 3, 4, 6, 7):
        pygame.draw.line(surf, INK, root, fill[idx], 2)
    pygame.draw.line(surf, INK, root, fill[1], 1)
    pygame.draw.line(surf, INK, root, fill[8], 1)

    # White margin flecks — kept off the black apex edge (which carries its own
    # spots) and run along the non-apex forewing edge + hindwing rim only.
    outer = margin[4:9]
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
