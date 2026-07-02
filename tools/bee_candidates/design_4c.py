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
import pygame

from tools.bee_candidates._shared_monarch import (
    _WING_R, _centroid, _inset, _transform, _wing_mask, _new, _flap,
    _aaellipse, draw_body, draw_head, make_build,
    COMPOSITE_W, COMPOSITE_H, BCX, BCY,
)

# ── palette ──────────────────────────────────────────────────────────────────
OBSIDIAN = (14, 11, 20)    # dominant jet-black wing field
SCARLET  = (215, 28, 28)   # bold diagonal band — the hero mark
EMBER    = (210, 80, 20)   # thin orange-red hindwing trailing trim
FLAKE    = (245, 241, 230)  # white spots at forewing apex
INK      = (26, 19, 14)    # veins/margin/body
DIM_RED  = (100, 15, 15)   # faint vein lines inside the red band only


def _draw_wing(surf, side, spread, nx):
    margin = _transform(_WING_R, side, spread, nx)
    fill = _inset(margin, 0.14)

    # Black IS the wing — one flat obsidian field carries the whole silhouette,
    # so the single scarlet slash reads as the only chroma on either sky.
    pygame.draw.polygon(surf, OBSIDIAN, margin)

    # Scarlet diagonal band: an inner-mid → outer-forewing slash. Built from the
    # notch (fill[5]) up to the apex zone (fill[2]/fill[3]) as a ~9px-wide strip
    # so it stays a decisive bar, not a thin line, at 40px.
    inner_lo, inner_hi = fill[5], fill[4]
    outer_lo, outer_hi = fill[3], fill[2]
    band = [
        (inner_lo[0], inner_lo[1]),
        (outer_lo[0], outer_lo[1]),
        (outer_hi[0], outer_hi[1]),
        (inner_hi[0], inner_hi[1]),
    ]
    pygame.draw.polygon(surf, SCARLET, band)

    # Faint interior veins live ONLY inside the scarlet band — texture on the red
    # that never shows against the black field. Two thin DIM_RED strokes span the
    # band's long axis at slight offsets.
    for t in (0.38, 0.62):
        a = (inner_lo[0] + (inner_hi[0] - inner_lo[0]) * t,
             inner_lo[1] + (inner_hi[1] - inner_lo[1]) * t)
        b = (outer_lo[0] + (outer_hi[0] - outer_lo[0]) * t,
             outer_lo[1] + (outer_hi[1] - outer_lo[1]) * t)
        pygame.draw.line(surf, DIM_RED, a, b, 1)

    # Hindwing trailing trim: a thin ember strip hugging the bottom edge from the
    # notch-side outer (fill[6]) around the lobe to the inner bottom (fill[9]).
    trim = [fill[6], fill[7], fill[8], fill[9]]
    pygame.draw.lines(surf, EMBER, False, trim, 3)

    # White apex spots — the admiral's signature flecks, a tight scatter near the
    # forewing tip (around fill[2]/fill[3]).
    ap2, ap3 = fill[2], fill[3]
    apex_spots = (
        (ap2[0], ap2[1]),
        (ap2[0] - 2, ap2[1] + 3),
        ((ap2[0] + ap3[0]) / 2, (ap2[1] + ap3[1]) / 2),
        (ap3[0] - 1, ap3[1] - 2),
    )
    for sx, sy in apex_spots:
        pygame.draw.circle(surf, FLAKE, (int(sx), int(sy)), 1)

    # Sparse white margin dots only where black meets the red band on the
    # forewing outer edge (fill[1]..fill[4]) — one per segment, kept sparse so
    # the read stays BLACK-with-a-red-slash, never a lacy rim.
    fcx, fcy = _centroid(fill)
    edge = [margin[1], margin[2], margin[3], margin[4]]
    for a0 in edge:
        ox = a0[0] + (fcx - a0[0]) * 0.14
        oy = a0[1] + (fcy - a0[1]) * 0.14
        pygame.draw.circle(surf, FLAKE, (int(ox), int(oy)), 1)


_draw_wing_wrapper = lambda surf, side, spread, nx: _draw_wing(surf, side, spread, nx)

build = make_build(_draw_wing_wrapper, ink=INK, flake=FLAKE,
                   ring_col=SCARLET, club_col=EMBER)
