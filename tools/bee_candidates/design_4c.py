"""BUG/INSECT redesign — design_4c RED ADMIRAL (Vanessa atalanta).

The dark, dramatic counterweight to the MONARCH: jet-black wings almost
edge to edge, cut once by a single bold scarlet diagonal slash across the
forewing and hemmed by a thin orange-red trim along the hindwing trailing
edge, with a tight cluster of white flecks at the forewing apex. The read
is built on raw value contrast — near-black wings with one high-chroma red
mark — so it stays legible on bright day sky AND night sky. Black must
dominate; this is NOT an orange butterfly.

Scratch exploration only — NOT registered in store_skins.BUILDERS. Production
art stays untouched until a winner is picked.
"""
import math

import pygame

from tools.bee_candidates._shared_monarch import (
    _WING_R, _centroid, _inset, _transform, _wing_mask, _new, _flap,
    _aaellipse, draw_body, draw_head, make_build,
    COMPOSITE_W, COMPOSITE_H, BCX, BCY,
)

# ── palette ──────────────────────────────────────────────────────────────────
OBSIDIAN = (14, 11, 20)    # dominant jet-black wing field
NIGHT_RIM = (44, 48, 68)   # cool blue-grey edge so the black shape reads at night
SCARLET  = (215, 28, 28)   # bold diagonal band — the hero mark
EMBER    = (190, 70, 18)   # thin rust-red hindwing trailing hem
FLAKE    = (245, 241, 230)  # white spots at forewing apex
INK      = (26, 19, 14)    # veins/margin/body
DIM_RED  = (100, 15, 15)   # faint vein lines inside the red band only


def _lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def _draw_wing(surf, side, spread, nx):
    margin = _transform(_WING_R, side, spread, nx)
    fill = _inset(margin, 0.14)

    # Black IS the wing — one flat obsidian field carries the whole silhouette,
    # so the single scarlet slash reads as the only chroma on either sky.
    pygame.draw.polygon(surf, OBSIDIAN, margin)
    # A 1px cool-dark rim gives the jet-black shape an edge against night-sky
    # navy without lifting the value enough to change the day read.
    pygame.draw.polygon(surf, NIGHT_RIM, margin, 1)

    # Scarlet oblique band — a true diagonal BAR floating inside the black field,
    # not an edge colouring. Both endpoints are pulled well inward so black margin
    # survives OUTBOARD of the red on every side: the low end sits in the inner
    # forewing near the fore/hind boundary, the high end near (but short of) the
    # apex, leaving a black costal line above and a black outer margin beyond.
    fc = _centroid(margin)
    e1 = _lerp(_lerp(fc, margin[0], 0.35), margin[9], 0.12)
    e2 = _lerp(margin[2], fc, 0.40)
    vx, vy = e2[0] - e1[0], e2[1] - e1[1]
    seg = math.hypot(vx, vy) or 1.0
    px, py = -vy / seg, vx / seg
    hw = 4.2
    band = [
        (e1[0] + px * hw, e1[1] + py * hw),
        (e2[0] + px * hw, e2[1] + py * hw),
        (e2[0] - px * hw, e2[1] - py * hw),
        (e1[0] - px * hw, e1[1] - py * hw),
    ]
    pygame.draw.polygon(surf, SCARLET, band)

    # Faint interior veins live ONLY inside the scarlet band — texture on the red
    # that never shows against the black field. Two thin DIM_RED strokes run the
    # band's long axis at slight cross-band offsets.
    for t in (0.35, 0.65):
        a = _lerp(band[3], band[0], t)
        b = _lerp(band[2], band[1], t)
        pygame.draw.line(surf, DIM_RED, a, b, 1)

    # Hindwing trailing hem: a thin rust strip along the bottom edge from the
    # notch-side outer (fill[6]) around the lobe to the inner bottom (fill[9]),
    # kept to 2px so it hems rather than co-leads with the scarlet.
    trim = [fill[6], fill[7], fill[8], fill[9]]
    pygame.draw.lines(surf, EMBER, False, trim, 2)

    # White apex cluster — the admiral's signature flecks, a tight scatter in the
    # black apex zone OUTBOARD of the scarlet (around fill[2]/fill[3]).
    ap2, ap3 = fill[2], fill[3]
    apex_spots = (
        (ap2[0], ap2[1]),
        (ap2[0] - 2, ap2[1] + 3),
        ((ap2[0] + ap3[0]) / 2, (ap2[1] + ap3[1]) / 2),
        (ap3[0] - 1, ap3[1] - 2),
    )
    for sx, sy in apex_spots:
        pygame.draw.circle(surf, FLAKE, (int(sx), int(sy)), 1)


_draw_wing_wrapper = lambda surf, side, spread, nx: _draw_wing(surf, side, spread, nx)

# ring_col=INK keeps the head a single dark node with one FLAKE accent, so the
# scarlet forewing slash stays the sole red focal point.
build = make_build(_draw_wing_wrapper, ink=INK, flake=FLAKE,
                   ring_col=INK, club_col=EMBER)
