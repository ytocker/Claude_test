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


def _taper_bar(surf, col, a, b, wa, wb):
    """A chevron tiger bar: fat where it meets the leading edge (a), tapering
    thin toward the notch (b) — the classic swallowtail stripe shape a straight
    constant-width line can't give."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    d = (dx * dx + dy * dy) ** 0.5 or 1.0
    px, py = -dy / d, dx / d
    ha, hb = wa / 2.0, wb / 2.0
    pygame.draw.polygon(surf, col, [
        (a[0] + px * ha, a[1] + py * ha),
        (a[0] - px * ha, a[1] - py * ha),
        (b[0] - px * hb, b[1] - py * hb),
        (b[0] + px * hb, b[1] + py * hb),
    ])


def _draw_wing(surf, side, spread, nx):
    margin = _transform(_WING_R, side, spread, nx)
    fill = _inset(margin, 0.08)                     # thin ~3-4px black margin so
                                                    # yellow dominates the field

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

    # Two separate black-line systems keep the two wings reading as distinct
    # zones instead of merging into one black field: the FOREWING carries only
    # tiger bars (below), the HINDWING only thin radiating veins. Veins stay 1px
    # so the hindwing reads yellow-forward, not caged.
    for idx in (6, 7):
        pygame.draw.line(surf, INK, root, fill[idx], 1)
    pygame.draw.line(surf, INK, root, fill[1], 1)   # midribs — thin, safe anywhere
    pygame.draw.line(surf, INK, root, fill[8], 1)

    # Tiger stripes — three thick black bars across the FOREWING, each running
    # roughly perpendicular to the leading edge and tapering toward the trailing
    # side (the swallowtail chevron read). They overlay the yellow field and
    # veins, spaced from the wing root out toward the apex.
    # Leading anchors span the whole leading edge (rise→apex→shoulder) so the
    # three bars stay spread and parallel instead of converging into one black
    # blob near the apex; inner anchors sweep from the root toward the notch for
    # the chevron. The wide top span guarantees the yellow gaps stay at least as
    # wide as each bar.
    lead0, shoulder = fill[1], fill[3]
    tail = fill[5]                                    # fore/hind notch (inner end)
    for t in (0.20, 0.50, 0.80):
        lx = lead0[0] + (shoulder[0] - lead0[0]) * t
        ly = lead0[1] + (shoulder[1] - lead0[1]) * t
        ix = root[0] + (tail[0] - root[0]) * t
        iy = root[1] + (tail[1] - root[1]) * t
        _taper_bar(surf, INK, (lx, ly), (ix, iy), 3.2, 1.8)

    # Blue lunules on the hindwing margin — a row of small SOLID blue scale-dots
    # just inboard of the dark margin between the outer hindwing and the tail.
    # Solid blue reads unmistakably blue; an alpha wash over the sulfur field
    # only mudded to gray-green (yellow+blue), so the shimmer is inked as opaque
    # crescents instead, which is also how the real bug carries its blue scales.
    shim = _new()
    for j in (6, 7, 8):
        mp = fill[j]
        bx = mp[0] + (fcx - mp[0]) * 0.16
        by = mp[1] + (fcy - mp[1]) * 0.16
        _aaellipse(shim, (*BLUE, 255), (bx, by), 2.2, 2.0)
    shim.blit(_wing_mask(fill), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(shim, (0, 0))

    # Eyespot on the hindwing bottom (fill[8]) — the orange-and-blue signature
    # spot near the tail, with a tiny catch-light.
    spot = fill[8]
    pygame.draw.circle(surf, ORANGE, (int(spot[0]), int(spot[1])), 4)
    pygame.draw.circle(surf, EYE_C, (int(spot[0]), int(spot[1])), 2)
    pygame.draw.circle(surf, FLAKE, (int(spot[0]), int(spot[1] - 1)), 1)

    # White margin flecks — a crisp double-row dotted rim, as the MONARCH.
    outer = margin[1:9]
    for i in range(len(outer) - 1):
        # Skip the flecks over the hindwing lobe (outer 5-6) so the crisp white
        # rim doesn't wash the blue shimmer zone back toward white.
        if i in (5, 6):
            continue
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
