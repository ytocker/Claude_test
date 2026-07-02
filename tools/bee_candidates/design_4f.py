"""BUG/INSECT redesign — design_4f PURPLE EMPEROR (Apatura iris).

The regal showpiece.  The MONARCH's rounded playing-card wing and heavy black
stained-glass frame, refilled with a deep royal-purple iridescent field.  Like
the real Apatura iris, the structural colour flashes as the wing angle shifts,
so a violet/blue shimmer wheel sweeps the wing face across the four flap frames.
A cream-white diagonal band cuts across the forewing and a small orange eyespot
sits on the hindwing lobe — the emperor's signature markings.  Purple dominates
the cells right up to the black bones so the read stays premium and unmistakably
royal on both day and night sky without a glow.

Scratch exploration only — NOT registered in store_skins.BUILDERS. Production
art stays untouched until a winner is picked.
"""
import pygame

from game.parrot import _WING_ANGLES, _add_outline
from tools.bee_candidates._shared_monarch import (
    _WING_R, _centroid, _inset, _transform, _wing_mask, _new,
    _flap, _aaellipse, draw_body, draw_head,
    COMPOSITE_W, COMPOSITE_H, BCX, BCY, _INK, _FLAKE,
)

# ── palette ──────────────────────────────────────────────────────────────────
PURPLE = (90, 38, 168)       # #5A26A8 — deep royal purple, dominant field
VIOLET = (130, 60, 210)      # #823CD2 — mid-purple lighter zone near thorax
DEEP   = (44, 18, 88)        # #2C1258 — near-black violet shadow at outer cells
SHIMMER_COLS = [             # violet↔indigo wheel only — no magenta, so the flash
    (150, 95, 235),          # violet          reads as a highlight sweep on a
    (95, 120, 240),          # indigo-blue     purple wing, never a pink recolor
    (120, 80, 225),          # blue-violet
    (110, 150, 245),         # periwinkle
]
WHITE_BAND = (240, 232, 210)  # #F0E8D2 — cream-white diagonal band (signature)
ORANGE_EYE = (220, 70, 15)    # #DC460F — hindwing eyespot outer ring
INK   = _INK                  # heavy black veins + margin (as MONARCH)
FLAKE = _FLAKE                # white margin dots (as MONARCH)


def _draw_wing(surf, side, spread, nx, fi):
    margin = _transform(_WING_R, side, spread, nx)
    fill = _inset(margin, 0.14)                     # thick ~6px black margin

    # Black margin first (the separator that carries the read on any sky), then
    # a deep-shadow value ring under the field: the outer cells go near-black
    # violet and only the inner field is mid-purple, so the wing reads dark and
    # rich at the rim — the value depth that makes purple read "royal" not "candy".
    pygame.draw.polygon(surf, INK, margin)
    pygame.draw.polygon(surf, DEEP, fill)
    pygame.draw.polygon(surf, PURPLE, _inset(fill, 0.18))

    fcx, fcy = _centroid(fill)
    rx, ry = margin[0]                               # wing root (inner-top)
    root = (rx + (fcx - rx) * 0.42, ry + (fcy - ry) * 0.42)

    # Warm-toward-thorax gradient: the inner wing lightens to violet, the way the
    # emperor's colour deepens from the body out to the rim.
    grad = _new()
    for r, col, a in ((16, PURPLE, 140), (11, VIOLET, 170), (6, VIOLET, 215)):
        _aaellipse(grad, (*col, a), root, r, r * 0.82)
    grad.blit(_wing_mask(fill), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(grad, (0, 0))

    # Per-frame structural shimmer: an additive violet/blue flash that slides
    # across the wing face with the flap beat, the way Apatura iris flips colour
    # as the wing angle passes through the stroke.
    shim = _new()
    scx = fcx + (fi - 1.5) * 5
    _aaellipse(shim, (*SHIMMER_COLS[fi % 4], 40), (scx, fcy), 14, 11)
    shim.blit(_wing_mask(fill), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(shim, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # Cream-white diagonal slash across the forewing — the emperor's signature
    # marking, but a narrow STRIPE, not a bisecting divider: both anchors are
    # pulled inboard of the rim so royal purple sits outboard AND inboard of the
    # cream and the slash only crosses about a third of the wing.
    WIDTH_BAND = 5
    a0 = ((fill[4][0] + fill[5][0]) / 2, (fill[4][1] + fill[5][1]) / 2)
    a1 = ((fill[2][0] + fill[3][0]) / 2, (fill[2][1] + fill[3][1]) / 2)
    a0 = (a0[0] + (fcx - a0[0]) * 0.16, a0[1] + (fcy - a0[1]) * 0.16)
    a1 = (a1[0] + (fcx - a1[0]) * 0.16, a1[1] + (fcy - a1[1]) * 0.16)
    dx, dy = a1[0] - a0[0], a1[1] - a0[1]
    dlen = max(1.0, (dx * dx + dy * dy) ** 0.5)
    px, py = -dy / dlen * (WIDTH_BAND / 2), dx / dlen * (WIDTH_BAND / 2)
    band = _new()
    pygame.draw.polygon(band, WHITE_BAND, [
        (a0[0] + px, a0[1] + py), (a1[0] + px, a1[1] + py),
        (a1[0] - px, a1[1] - py), (a0[0] - px, a0[1] - py),
    ])
    band.blit(_wing_mask(fill), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(band, (0, 0))

    # Heavy black veins radiating from the thorax root — the stained-glass carve
    # kept as the MONARCH so the purple reads as the SAME bug, recoloured. The two
    # veins that pass over the cream slash (to the forewing shoulder/outer, 3 & 4)
    # are drawn thin so they don't read as scratches across the light stripe.
    for idx in (2, 6, 7):
        pygame.draw.line(surf, INK, root, fill[idx], 2)
    for idx in (1, 3, 4, 8):
        pygame.draw.line(surf, INK, root, fill[idx], 1)

    # Orange eyespot on the hindwing lobe — a bright ringed dot with a purple
    # pupil and a single flake catch, the emperor's warm accent against the cool
    # field.
    ex = (fill[7][0] + fill[8][0]) / 2
    ey = (fill[7][1] + fill[8][1]) / 2
    pygame.draw.circle(surf, ORANGE_EYE, (int(ex), int(ey)), 4)
    pygame.draw.circle(surf, PURPLE, (int(ex), int(ey)), 2)
    pygame.draw.circle(surf, FLAKE, (int(ex), int(ey)), 1)

    # White margin flecks — the monarch's signature border dots, unchanged.
    outer = margin[1:9]
    for i in range(len(outer) - 1):
        a0, a1 = outer[i], outer[i + 1]
        ox = a0[0] + (fcx - a0[0]) * 0.14
        oy = a0[1] + (fcy - a0[1]) * 0.14
        pygame.draw.circle(surf, FLAKE, (int(ox), int(oy)), 1)
        for t in (0.0, 0.5):
            ex2 = a0[0] + (a1[0] - a0[0]) * t
            ey2 = a0[1] + (a1[1] - a0[1]) * t
            ix = ex2 + (fcx - ex2) * 0.30
            iy = ey2 + (fcy - ey2) * 0.30
            pygame.draw.circle(surf, FLAKE, (int(ix), int(iy)), 1)


_state = {"frames": None, "rot": {}}


def _build_frame(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    spread = int(f * 9)
    nx = 1.0 - 0.42 * f
    try:
        fi = list(_WING_ANGLES).index(int(round(wing_angle_deg)))
    except ValueError:
        fi = 0
    _draw_wing(surf, -1, spread, nx, fi)
    draw_body(surf, spread)
    _draw_wing(surf, +1, spread, nx, fi)
    draw_head(surf, spread, ring_col=VIOLET, club_col=(160, 90, 255))
    return surf


def build(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    if _state["frames"] is None:
        _state["frames"] = [_add_outline(_build_frame(a)) for a in _WING_ANGLES]
    frame_idx %= 4
    key = (frame_idx, int(round(tilt_deg / 3)) * 3)
    if key not in _state["rot"]:
        _state["rot"][key] = pygame.transform.rotozoom(
            _state["frames"][frame_idx], key[1], 1.0)
    return _state["rot"][key]
