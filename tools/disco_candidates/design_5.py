"""DISCO · Design 5 — MIRRORBALL (legendary showpiece candidate).

Pip becomes a walking disco ball: the scarlet macaw shows through, but the
head is wrapped in a faceted mirror-ball helmet, the chest carries a matching
mirror-tile vest, spotlight rays fan off the wing, and a sparkle trail drifts
off the tail onto a little chrome pedestal.

The facet glints are re-rolled per wing frame (seeded on the wing angle so the
result is stable + cacheable) — across the 4-frame flap loop that reads as a
full-time rotating mirror-ball shimmer, which is the baked-in spectacle the
legendary tier is meant to earn.

Scratch exploration builder — exposes ``build`` for the render harness; NOT
registered in ``store_skins.BUILDERS``.
"""
import math
import random

import pygame

from game.parrot import _build_frame, BIRD_BEAK, BIRD_BEAK_D
from game.store_skins import _make_skin, _spark, HX, HY, CROWN_Y


# Mirror-ball palette (from the concept sheet): a cool silver body lit by three
# saturated facet glints so every tile can catch a shifting cyan / magenta /
# hot-white spark without muddying to grey at 40px.
_SILVER_RIM  = (150, 160, 180)     # dark rim so the dome reads spherical
_SILVER_BASE = (200, 210, 220)     # helmet/vest base under the tiles
_TILE_HI     = (232, 236, 245)     # top-lit facet
_TILE_MID    = (214, 220, 232)     # mid facet
_TILE_LO     = (176, 187, 205)     # shaded lower facet (rounds the sphere)
_CYAN        = (63, 224, 255)
_MAGENTA     = (255, 63, 184)
_HOTWHITE    = (255, 246, 201)
_RAY         = (255, 252, 220)     # spotlight-beam yellow-white
_CHROME_HI   = (226, 232, 242)
_CHROME_LO   = (120, 132, 152)

# Wing beat drives a small ray sweep so the beams feel like light raking a
# spinning ball rather than a static decal.
_RAY_SWEEP = 0.05

_GLINTS = (_CYAN, _MAGENTA, _HOTWHITE)


def _tile_grid(surf, cx, cy, clip_fn, rng, *, glint_rate):
    """Lay a 4×3px mirror-tile grid (1px grout gaps) centred on (cx, cy),
    keeping only tiles ``clip_fn(tx, ty)`` accepts. Tiles shade top→bottom so
    the plane reads curved, and a share of them catch a coloured glint so the
    surface sparkles instead of reading as flat silver."""
    step_x, step_y = 5, 4          # 4px tile + 1px grout
    span = 4                       # ~4 tiles each way from centre
    for gx in range(-span, span + 1):
        for gy in range(-span, span + 1):
            tx = cx + gx * step_x - 2
            ty = cy + gy * step_y - 1
            if not clip_fn(tx + 2, ty + 1):
                continue
            # Vertical position picks the facet value; the top catches light,
            # the belly of the sphere falls into shadow.
            frac = (gy + span) / (2 * span)
            base = _TILE_HI if frac < 0.34 else _TILE_MID if frac < 0.7 else _TILE_LO
            pygame.draw.rect(surf, base, (tx, ty, 4, 3))
            if rng.random() < glint_rate:
                gc = _GLINTS[rng.randrange(3)]
                pygame.draw.rect(surf, gc, (tx + rng.randrange(2), ty + rng.randrange(2), 2, 2))


def _paint_mirrorball(surf, wing_angle_deg):
    # Seed on the frame's wing angle so glints are deterministic per frame yet
    # differ across the 4-frame loop → a rotating-facet shimmer for free.
    rng = random.Random(int(wing_angle_deg) * 131 + 7)

    # ── SPARKLE TRAIL (drawn first so it sits behind the bird) ───────────────
    # Light dots drifting off the tail into open sky; a couple twinkle per frame
    # via the seed so the stream feels alive.
    trail = [(24, 61), (20, 66), (16, 62), (13, 70), (22, 74),
             (10, 66), (18, 79), (14, 76)]
    for i, (sx, sy) in enumerate(trail):
        col = _GLINTS[i % 3]
        if rng.random() < 0.4:
            _spark(surf, sx, sy, 2, _HOTWHITE)
        else:
            pygame.draw.circle(surf, col, (sx, sy), 1 + (i % 2))

    # ── SPOTLIGHT RAYS off the wing (soft alpha beams on a scratch layer) ─────
    off = int(wing_angle_deg * _RAY_SWEEP)
    beams = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    wing_hub = (44, HY + 6)        # upper-back wing edge
    ray_tips = [(64, HY - 12 + off), (62, HY + 2 + off), (58, HY + 16 - off),
                (40, HY - 18 + off), (26, HY - 12 - off)]
    for tx, ty in ray_tips:
        pygame.draw.line(beams, (*_RAY, 150), wing_hub, (tx, ty), 1)
    # A brighter core spoke so at least one beam survives the downscale.
    pygame.draw.line(beams, (*_HOTWHITE, 190), wing_hub, ray_tips[0], 1)
    surf.blit(beams, (0, 0))

    # ── MIRROR-TILE VEST down the chest ──────────────────────────────────────
    # Clip to the front of the body ellipse (centre (32,52), rx19 ry14) and to
    # the chest column so the tiles hug Pip's breast, not the whole belly.
    def _vest_clip(x, y):
        ex = (x - 32) / 19.0
        ey = (y - 52) / 14.0
        return ex * ex + ey * ey <= 0.92 and 29 <= x <= 47 and 42 <= y <= 61

    _tile_grid(surf, 38, 51, _vest_clip, rng, glint_rate=0.28)

    # ── MIRROR-BALL HELMET on the head ───────────────────────────────────────
    hcx, hcy = HX, HY - 2
    pygame.draw.circle(surf, _SILVER_RIM, (hcx, hcy), 13)
    pygame.draw.circle(surf, _SILVER_BASE, (hcx, hcy), 12)

    # Beak opening: skip any tile whose centre lands over the beak so it pokes
    # through cleanly on the front-right of the dome.
    def _dome_clip(x, y):
        if (x - hcx) ** 2 + (y - hcy) ** 2 > 12 * 12:
            return False
        return ((x - 56) / 6.0) ** 2 + ((y - 44) / 4.0) ** 2 > 1.0

    _tile_grid(surf, hcx, hcy, _dome_clip, rng, glint_rate=0.34)

    # Spherical read: a bright top-left crescent and a soft lower shade the tile
    # grid alone can't guarantee.
    pygame.draw.circle(surf, _TILE_HI, (hcx - 4, hcy - 6), 3)
    pygame.draw.circle(surf, _HOTWHITE, (hcx - 5, hcy - 7), 1)

    # Peek eye so Pip still reads through the helmet — a dark facet with a
    # cyan-lit pupil pip.
    pygame.draw.circle(surf, (40, 46, 60), (hcx + 3, hcy), 2)
    pygame.draw.circle(surf, _CYAN, (hcx + 3, hcy - 1), 1)

    # Redraw the beak on top so it clears the silver dome.
    beak_pts = [(55, 41), (61, 44), (58, 48), (52, 46)]
    pygame.draw.polygon(surf, BIRD_BEAK, beak_pts)
    pygame.draw.polygon(surf, BIRD_BEAK_D, beak_pts, 1)
    pygame.draw.line(surf, BIRD_BEAK_D, (52, 44), (58, 45), 1)

    # ── CHROME PEDESTAL under the feet ───────────────────────────────────────
    # A stubby mount + capsule so the mirror ball reads as if on its stand.
    pygame.draw.line(surf, _CHROME_LO, (32, 74), (32, 77), 2)
    pygame.draw.rect(surf, _CHROME_LO, (28, 77, 9, 4), border_radius=2)
    pygame.draw.rect(surf, _CHROME_HI, (28, 77, 9, 2), border_radius=2)
    pygame.draw.line(surf, _SILVER_BASE, (29, 79), (35, 79), 1)


build = _make_skin(_paint_mirrorball, base_fn=_build_frame)
