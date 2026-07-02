"""BUG/INSECT redesign — design_4b AZURE MONARCH (Morpho x Monarch cross).

The MONARCH's rounded playing-card wing with its heavy black stained-glass
veins and white margin dots, but recoloured into a deep royal-blue structural
field like a blue morpho — an azure butterfly carved by monarch bones. A
per-frame cyan iridescent shimmer sweeps across each wing face on the flap
beat, the way real morpho scales flash as the angle changes. The read still
rests on raw value contrast (bright blue over deep black), so it holds on both
day and night sky without a glow.

Scratch exploration only — NOT registered in store_skins.BUILDERS. Production
art stays untouched until a winner is picked.
"""
import pygame

from game.parrot import _WING_ANGLES, _add_outline, _aaellipse
from tools.bee_candidates._shared_monarch import (
    _WING_R, _centroid, _inset, _transform, _wing_mask, _new,
    _flap, draw_body, draw_head,
)

# ── palette ──────────────────────────────────────────────────────────────────
ROYAL  = (28, 90, 200)     # #1C5AC8 — deep royal blue, dominant wing field
AZURE  = (55, 140, 245)    # #378CF5 — mid-blue, lighter inner zone near thorax
CYAN   = (80, 210, 255)    # #50D2FF — iridescent shimmer (per-frame additive)
COBALT = (18, 55, 140)     # #12378C — deep cobalt shadow ring (replaces SHADOW)
INK    = (26, 19, 14)      # #1A130E — heavy black veins + margin (as MONARCH)
FLAKE  = (245, 241, 230)   # #F5F1E6 — white margin dots (as MONARCH)


def _draw_wing(surf, side, spread, nx, fi):
    margin = _transform(_WING_R, side, spread, nx)
    fill = _inset(margin, 0.14)                     # thick ~6px black margin

    # Black margin first (the separator that carries the read on any sky), then
    # a deep cobalt rim, then the royal-blue field. Blue must dominate the cells
    # right up to the black bones so nothing near the margin reads grey at 40px.
    pygame.draw.polygon(surf, INK, margin)
    pygame.draw.polygon(surf, COBALT, _inset(fill, 0.06))
    pygame.draw.polygon(surf, ROYAL, fill)

    fcx, fcy = _centroid(fill)
    rx, ry = margin[0]                               # wing root (inner-top)
    root = (rx + (fcx - rx) * 0.42, ry + (fcy - ry) * 0.42)
    core = _new()
    for r, col, a in ((16, ROYAL, 130), (12, AZURE, 160), (7, AZURE, 200)):
        _aaellipse(core, (*col, a), root, r, r * 0.82)
    # Morpho wings flash brightest along the forewing — blush the tip azure.
    tip, lead = fill[2], fill[1]
    mid = ((tip[0] + lead[0]) / 2, (tip[1] + lead[1]) / 2)
    _aaellipse(core, (*AZURE, 190), tip, 7, 6)
    _aaellipse(core, (*AZURE, 215), mid, 4, 4)
    core.blit(_wing_mask(fill), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(core, (0, 0))

    # Heavy black veins radiating from the thorax root — the stained-glass carve
    # kept exactly as the MONARCH so the blue reads as the SAME bug, recoloured.
    for idx in (2, 3, 4, 6, 7):
        pygame.draw.line(surf, INK, root, fill[idx], 2)
    pygame.draw.line(surf, INK, root, fill[1], 1)
    pygame.draw.line(surf, INK, root, fill[8], 1)

    # Per-frame iridescent shimmer: a cyan additive flash on the wing face that
    # slides across the cells with the flap beat, the way structural morpho blue
    # shifts as the wing angle changes through the stroke.
    shim = _new()
    sx = fcx + (fi - 1.5) * 4
    _aaellipse(shim, (*CYAN, 110), (sx, fcy), 18, 14)
    shim.blit(_wing_mask(fill), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(shim, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # White margin flecks — the monarch's signature border dots, unchanged.
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


def _build_frame(wing_angle_deg):
    surf = _new()
    fi = _WING_ANGLES.index(int(round(wing_angle_deg)))
    f = _flap(wing_angle_deg)
    spread = int(f * 9)
    nx = 1.0 - 0.42 * f

    _draw_wing(surf, -1, spread, nx, fi)
    draw_body(surf, spread)
    _draw_wing(surf, +1, spread, nx, fi)
    draw_head(surf, spread, ring_col=AZURE, club_col=CYAN)
    return surf


_state = {"frames": None, "rot": {}}


def build(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    if _state["frames"] is None:
        _state["frames"] = [_add_outline(_build_frame(a)) for a in _WING_ANGLES]
    frame_idx %= 4
    key = (frame_idx, int(round(tilt_deg / 3)) * 3)
    if key not in _state["rot"]:
        _state["rot"][key] = pygame.transform.rotozoom(
            _state["frames"][frame_idx], key[1], 1.0)
    return _state["rot"][key]
