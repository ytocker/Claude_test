"""BUG/INSECT redesign — design_4e TIGER SWALLOWTAIL (Papilio glaucus).

The MONARCH's rounded playing-card wing and heavy black stained-glass bones,
recut as a tiger swallowtail: a bright sulfur-yellow field carved by the same
radiating black veins AND overlaid with three bold black tiger stripes across
the forewing, the pattern a player reads as "yellow-and-black tiger butterfly"
before anything else. A blue shimmer washes the hindwing lobe and a small
orange+blue eyespot sits on the hindwing bottom — the vivid tropical showpiece
counterpart to the warm orange MONARCH. The read still rests on raw value
contrast (bright yellow over deep black), so it holds on day and night sky.

Scratch exploration only — NOT registered in store_skins.BUILDERS. Production
art stays untouched until a winner is picked.
"""
import pygame

from tools.bee_candidates._shared_monarch import (
    _WING_R, _centroid, _inset, _transform, _wing_mask, _new,
    _aaellipse, make_build,
)

# ── palette ──────────────────────────────────────────────────────────────────
SULFUR = (252, 218, 18)    # #FCDA12 — bright sulfur yellow, dominant field
LEMON  = (255, 240, 100)   # #FFF064 — warm highlight near the thorax
INK    = (26, 19, 14)      # #1A130E — heavy black veins + margin + tiger stripes
BLUE   = (60, 100, 220)    # #3C64DC — hindwing shimmer wash (additive)
ORANGE = (230, 75, 15)     # #E64B0F — eyespot outer ring
EYE_C  = (50, 80, 200)     # #3250C8 — eyespot inner blue pupil
FLAKE  = (245, 241, 230)   # #F5F1E6 — white margin dots


def _draw_wing(surf, side, spread, nx):
    margin = _transform(_WING_R, side, spread, nx)
    fill = _inset(margin, 0.14)                     # thick ~6px black margin

    # Black margin first (the separator that carries the read on any sky), then
    # the yellow field right up to the bones so nothing near the margin reads
    # dull at 40px.
    pygame.draw.polygon(surf, INK, margin)
    pygame.draw.polygon(surf, SULFUR, fill)

    fcx, fcy = _centroid(fill)
    rx, ry = margin[0]                               # wing root (inner-top)
    root = (rx + (fcx - rx) * 0.42, ry + (fcy - ry) * 0.42)

    # Warm gradient core at the thorax root — a lemon glow the tiger stripes
    # ride over, so the field feels lit from the body outward.
    core = _new()
    for r, col, a in ((16, SULFUR, 140), (10, LEMON, 180), (5, LEMON, 220)):
        _aaellipse(core, (*col, a), root, r, r * 0.82)
    core.blit(_wing_mask(fill), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(core, (0, 0))

    # Heavy black veins radiating from the thorax root — the stained-glass carve
    # kept exactly as the MONARCH so the yellow reads as the SAME bug, recut.
    for idx in (2, 3, 4, 6, 7):
        pygame.draw.line(surf, INK, root, fill[idx], 2)
    pygame.draw.line(surf, INK, root, fill[1], 1)
    pygame.draw.line(surf, INK, root, fill[8], 1)

    # Tiger stripes — three thick black bars across the FOREWING, each running
    # roughly perpendicular to the leading edge and tapering toward the trailing
    # side (the swallowtail chevron read). They overlay the yellow field and
    # veins, spaced from the wing root out toward the apex.
    lead0, apex = fill[1], fill[2]                    # forewing leading edge span
    tail = fill[5]                                    # fore/hind notch (inner end)
    for t in (0.34, 0.55, 0.76):
        # Anchor on the leading edge, sweep in toward the notch for the chevron.
        lx = lead0[0] + (apex[0] - lead0[0]) * t
        ly = lead0[1] + (apex[1] - lead0[1]) * t
        ix = root[0] + (tail[0] - root[0]) * t
        iy = root[1] + (tail[1] - root[1]) * t
        pygame.draw.line(surf, INK, (lx, ly), (ix, iy), 3)

    # Blue shimmer on the hindwing lobe — an additive wash centred on fill[7],
    # the way tiger swallowtail hindwings carry a dusting of blue scales.
    shim = _new()
    lobe = fill[7]
    _aaellipse(shim, (*BLUE, 90), lobe, 18, 14)
    shim.blit(_wing_mask(fill), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(shim, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # Eyespot on the hindwing bottom (fill[8]) — the orange-and-blue signature
    # spot near the tail, with a tiny catch-light.
    spot = fill[8]
    pygame.draw.circle(surf, ORANGE, (int(spot[0]), int(spot[1])), 4)
    pygame.draw.circle(surf, EYE_C, (int(spot[0]), int(spot[1])), 2)
    pygame.draw.circle(surf, FLAKE, (int(spot[0]), int(spot[1] - 1)), 1)

    # White margin flecks — a crisp double-row dotted rim, as the MONARCH.
    outer = margin[1:9]
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
    ring_col=SULFUR, club_col=LEMON,
)
