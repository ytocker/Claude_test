"""DISCO · Design 5 — MIRRORBALL (legendary showpiece candidate).

Pip becomes a walking disco ball: the scarlet macaw shows through, but the head
is wrapped in a faceted mirror-ball helmet and the chest carries a vest cut from
the *same* chrome, so head + torso read as one continuous mirror-ball material.
Bold spotlight wedges throw up-and-forward off the crown and a light-streak
trails the tail.

Two design bets make the ball survive the 40px downscale: facet tiles are big
(5px) with near-black grout so their edges keep reading, and two curved
great-circle seams cross the dome — the universal disco-ball shorthand that
sells "sphere" at any size, even when the tile grid itself dithers.

The facet glints are re-rolled per wing frame (seeded on the wing angle so the
result is stable + cacheable); across the 4-frame flap loop that reads as a
full-time rotating mirror-ball shimmer — the baked-in spectacle the legendary
tier is meant to earn.

Scratch exploration builder — exposes ``build`` for the render harness; NOT
registered in ``store_skins.BUILDERS``.
"""
import math
import random

import pygame

from game.parrot import _build_frame, BIRD_BEAK, BIRD_BEAK_D
from game.store_skins import _make_skin, _spark, HX, HY, CROWN_Y


# One neutral silver drives both the helmet and the vest so they read as the
# same chrome. Kept near-grey (r≈g≈b) on purpose — the R1 palette skewed blue
# and collapsed the vest into "gingham". Colour lives ONLY in sparse 2px glints.
_SILVER_RIM  = (140, 146, 156)     # dark rim so the dome reads spherical
_SILVER_BASE = (198, 203, 209)     # helmet/vest base under the tiles
_TILE_HI     = (236, 238, 240)     # top-lit facet
_TILE_MID    = (206, 210, 214)     # mid facet
_TILE_LO     = (168, 174, 182)     # shaded lower facet (rounds the sphere)
_GROUT       = (20, 20, 20)        # near-black gap so facet edges survive downscale
_SEAM        = (66, 70, 80)        # great-circle groove line
_CYAN        = (63, 224, 255)
_MAGENTA     = (255, 63, 184)
_HOTWHITE    = (255, 246, 201)
_BEAM        = (255, 252, 220)     # opaque spotlight-wedge core

# Wing beat nudges the beams so the spotlight rakes as the ball spins rather
# than reading as a static decal.
_BEAM_SWEEP = 0.04

# Glints on the ball rotate between the three club colours; the tiles stay
# silver so cyan/magenta never becomes a field colour.
_GLINTS = (_CYAN, _MAGENTA, _HOTWHITE)


def _tile_grid(surf, cx, cy, clip_fn, rng, *, glint_rate, span, grout_bg):
    """Lay a big-facet mirror-tile grid centred on (cx, cy), keeping only tiles
    ``clip_fn`` accepts. Tiles are 5px with a 1px near-black grout gap so the
    facet edges keep reading after the 64→40px downscale; they shade top→bottom
    so the plane reads curved, and a share catch a coloured glint. ``grout_bg``
    stamps a black backing per tile where the surface below isn't already dark
    (the vest sits on the body, the helmet on its own dark dome)."""
    tile, step = 5, 6
    for gx in range(-span, span + 1):
        for gy in range(-span, span + 1):
            ccx = cx + gx * step
            ccy = cy + gy * step
            if not clip_fn(ccx, ccy):
                continue
            if grout_bg:
                pygame.draw.rect(surf, _GROUT, (ccx - 3, ccy - 3, step, step))
            frac = (gy + span) / (2 * span)
            base = _TILE_HI if frac < 0.34 else _TILE_MID if frac < 0.7 else _TILE_LO
            pygame.draw.rect(surf, base, (ccx - 2, ccy - 2, tile, tile))
            if rng.random() < glint_rate:
                gc = _GLINTS[rng.randrange(3)]
                pygame.draw.rect(surf, gc, (ccx - 1, ccy - 1, 2, 2))


def _paint_mirrorball(surf, wing_angle_deg):
    # Seed on the frame's wing angle so glints are deterministic per frame yet
    # differ across the 4-frame loop → a rotating-facet shimmer for free.
    rng = random.Random(int(wing_angle_deg) * 131 + 7)

    # ── LIGHT-STREAK TRAIL off the tail (drawn first, behind the bird) ────────
    # A straight horizontal line of shrinking dots trailing the tail tip reads
    # as motion/light, not scattered damage pips. Cyan + white only.
    streak = [(14, 55, 2, _CYAN), (10, 55, 1, _HOTWHITE),
              (6, 55, 1, _CYAN), (3, 55, 1, _HOTWHITE)]
    for i, (sx, sy, r, col) in enumerate(streak):
        if i == 0 and rng.random() < 0.5:
            _spark(surf, sx, sy, 2, _HOTWHITE)
        else:
            pygame.draw.circle(surf, col, (sx, sy), r)

    # ── SPOTLIGHT WEDGES off the crown (opaque so they survive downscale) ─────
    # 3 thin solid triangles fanning UP-AND-FORWARD off the top of the ball,
    # like beams thrown upward. Drawn before the dome so their feet tuck under
    # the silver. A small wing-driven sweep keeps them alive.
    sweep = wing_angle_deg * _BEAM_SWEEP
    top = (HX, HY - 12)
    wedges = [((-3.5, -22), 2.2), ((0.5, -25), 2.6), ((5.0, -20), 2.2)]
    for (dx, dy), half in wedges:
        tip = (top[0] + dx + sweep, top[1] + dy)
        pygame.draw.polygon(surf, _BEAM, [
            (top[0] - half, top[1]), (top[0] + half, top[1]), tip])
    # Hot core down the centre beam so at least one stays crisp at 40px.
    pygame.draw.polygon(surf, _HOTWHITE, [
        (top[0] - 1, top[1]), (top[0] + 1, top[1]),
        (top[0] + 0.5 + sweep, top[1] - 25)])

    # ── MIRROR-TILE VEST down the chest (same chrome as the helmet) ───────────
    # Clip to the front of the body ellipse and the chest column so the tiles
    # hug Pip's breast; grout backing makes the facet edges read on the body.
    def _vest_clip(x, y):
        ex = (x - 32) / 19.0
        ey = (y - 52) / 14.0
        return ex * ex + ey * ey <= 0.92 and 29 <= x <= 47 and 42 <= y <= 61

    _tile_grid(surf, 38, 51, _vest_clip, rng, glint_rate=0.18, span=3, grout_bg=True)

    # ── MIRROR-BALL HELMET on the head ───────────────────────────────────────
    hcx, hcy = HX, HY - 2
    pygame.draw.circle(surf, _SILVER_RIM, (hcx, hcy), 13)
    pygame.draw.circle(surf, _GROUT, (hcx, hcy), 12)   # grout shows through gaps

    # Beak opening: skip any tile whose centre lands over the beak so it pokes
    # through cleanly on the front-right of the dome.
    def _dome_clip(x, y):
        if (x - hcx) ** 2 + (y - hcy) ** 2 > 12 * 12:
            return False
        return ((x - 56) / 6.0) ** 2 + ((y - 44) / 4.0) ** 2 > 1.0

    _tile_grid(surf, hcx, hcy, _dome_clip, rng, glint_rate=0.30, span=2, grout_bg=False)

    # Two curved great-circle seams — the disco-ball shorthand that instantly
    # sells "ball" even when the tile grid mushes. One near-horizontal latitude
    # bulging down the front, one near-vertical longitude bulging forward.
    pygame.draw.arc(surf, _SEAM, (hcx - 11, hcy - 6, 22, 13), math.pi, 2 * math.pi, 2)
    pygame.draw.arc(surf, _SEAM, (hcx - 7, hcy - 11, 12, 22), -math.pi / 2, math.pi / 2, 2)

    # Spherical read: an enlarged bright top-left crescent + a hot core the tile
    # grid alone can't guarantee.
    pygame.draw.circle(surf, _TILE_HI, (hcx - 4, hcy - 6), 4)
    pygame.draw.circle(surf, _HOTWHITE, (hcx - 5, hcy - 7), 2)
    pygame.draw.circle(surf, (255, 255, 255), (hcx - 6, hcy - 8), 1)

    # Peek eye so Pip still reads through the helmet — a dark facet with a
    # cyan-lit pupil pip.
    pygame.draw.circle(surf, (40, 46, 60), (hcx + 3, hcy), 2)
    pygame.draw.circle(surf, _CYAN, (hcx + 3, hcy - 1), 1)

    # Redraw the beak on top so it clears the silver dome.
    beak_pts = [(55, 41), (61, 44), (58, 48), (52, 46)]
    pygame.draw.polygon(surf, BIRD_BEAK, beak_pts)
    pygame.draw.polygon(surf, BIRD_BEAK_D, beak_pts, 1)
    pygame.draw.line(surf, BIRD_BEAK_D, (52, 44), (58, 45), 1)


build = _make_skin(_paint_mirrorball, base_fn=_build_frame)
