"""ROADKILL FRESH-TURNED — zombie parrot candidate (Design 1, scratch).

A *recently* mangled bird: the healthy silhouette is still legible, which is
what sells the fresh-kill horror — it hasn't rotted, it was just torn open.
The read is carried by ONE high-contrast chest wound — white bone bars over a
black cavity with a wet-red pool — one hot glowing eye against a milky dead
ring, a chewed wing edge, and blood bleeding past the belly line. Scratch
explorer only — NOT registered in ``store_skins.BUILDERS``; exposes
``build(frame_idx, tilt_deg) -> Surface``.
"""
from __future__ import annotations

import pygame

from game.parrot import SPRITE_W, SPRITE_H, _aaellipse
from game.store_skins import _make_prebuilt_skin

# Fresh-turned palette — pushed to a necrotic green-gray so the saturated
# wound reds and bone whites carry all the contrast (was a livelier green).
BODY    = (88, 102, 76)
BODY_D  = (26, 34, 24)
BODY_H  = (118, 134, 102)
BELLY   = (128, 144, 110)
GASH_D  = (122, 20, 20)      # clotted rim
GASH_H  = (199, 48, 43)      # wet, fresh center
CAVITY  = (20, 14, 12)       # near-black open interior
BONE    = (233, 228, 208)
EYE_GLOW = (255, 58, 46)
WING     = (74, 88, 62)
WING_D   = (42, 52, 36)
BEAK     = (176, 150, 96)    # desaturated, no longer glossy-live
NEARBLK  = (18, 10, 12)


def _glow_blit(surf, center, color, radius):
    """Additive hot-eye bloom. Concentric fills with scaled RGB (BLEND_RGB_ADD
    ignores alpha) so the pupil looks self-lit against the milky ring."""
    d = radius * 2
    g = pygame.Surface((d, d), pygame.SRCALPHA)
    for f, s in ((1.0, 0.22), (0.6, 0.5), (0.32, 1.0)):
        c = (int(color[0] * s), int(color[1] * s), int(color[2] * s))
        pygame.draw.circle(g, c, (radius, radius), int(radius * f))
    surf.blit(g, (center[0] - radius, center[1] - radius),
              special_flags=pygame.BLEND_RGB_ADD)


def _roadkill_wing(angle_deg):
    """Clean leaf wing with ONE bold triangular bite chewed out of the trailing
    edge in near-black — silhouette-level damage survives the downscale where
    fine saw-tooth texture would vanish. Kept on its own surface so it rotates
    with the flap."""
    w = pygame.Surface((52, 52), pygame.SRCALPHA)
    pts = [(24, 22), (46, 15), (49, 26), (44, 32), (20, 33), (17, 27)]
    pygame.draw.polygon(w, WING, pts)
    pygame.draw.polygon(w, WING_D, [(24, 22), (17, 27), (20, 33), (32, 32)])
    # The single chewed notch: a dark V driven in from the trailing edge.
    pygame.draw.polygon(w, NEARBLK, [(42, 31), (34, 24), (33, 33)])
    pygame.draw.line(w, WING_D, (26, 24), (44, 18), 1)
    return pygame.transform.rotate(w, angle_deg)


def _drip(surf, x, y0, length):
    """A thin teardrop hanging past the belly line — a bulb tip on a narrow
    neck so it reads as fresh blood breaking the silhouette even at 40px."""
    tip = y0 + length
    pygame.draw.polygon(surf, GASH_H,
                        [(x, y0), (x + 2, tip - 2), (x, tip), (x - 2, tip - 2)])


def _build_roadkill(wing_angle_deg):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)

    # Tail — sick-green wedges, darkest at the root.
    for i, c in enumerate([BODY_D, WING_D, BODY, BODY_H]):
        pts = [(2 + i * 3, 26 + i * 2), (14 + i, 24 + i),
               (20 + i, 30 + i * 2), (6 + i * 3, 36 + i * 2)]
        pygame.draw.polygon(surf, c, pts)

    # Body — overlapping ellipses, belly lifted lighter to carry the wound.
    _aaellipse(surf, BODY_D, (34, 35), 19, 14)
    _aaellipse(surf, BODY, (32, 32), 19, 14)
    _aaellipse(surf, BODY_H, (30, 28), 13, 8)
    _aaellipse(surf, BELLY, (28, 38), 12, 6)

    # Split-open back crease — a single dark tear down the far flank, hinting
    # the whole side is peeled. Kept red-free so only the chest wound bleeds.
    pygame.draw.lines(surf, BODY_D, False,
                      [(20, 24), (17, 29), (19, 34), (16, 39), (18, 43)], 2)

    # Near wing — hung low and mangled. Drawn before the wound so nothing
    # occludes the read.
    wing = _roadkill_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 31)).topleft)

    # Chest wound — ONE high-contrast unit riding mid-chest: a clotted rim
    # around a near-black cavity, a wet-red inner pool, crossed by three short
    # thick bone bars. White bone over a black hole is the whole read.
    wx, wy = 30, 34
    gash = [(21, 34), (25, 29), (31, 28), (38, 32), (34, 39), (27, 40), (22, 38)]
    pygame.draw.polygon(surf, GASH_D, gash)
    _aaellipse(surf, CAVITY, (wx, wy), 9, 5)
    _aaellipse(surf, GASH_H, (wx, wy + 1), 5, 2)
    for by, half in ((29, 4), (33, 5), (37, 4)):
        pygame.draw.rect(surf, BONE, (wx - half, by, half * 2, 3))
    pygame.draw.polygon(surf, NEARBLK, gash, 2)

    # Blood drips — bled past the belly outline so the wound reads fresh even
    # at gameplay scale.
    _drip(surf, 27, 42, 6)
    _drip(surf, 32, 43, 5)

    # Head.
    _aaellipse(surf, BODY_D, (48, 23), 12, 11)
    _aaellipse(surf, BODY, (47, 21), 12, 11)
    _aaellipse(surf, BODY_H, (46, 16), 7, 3)

    # Far eye — a normal dead-dark bead, no life left in it.
    pygame.draw.circle(surf, (232, 226, 210), (44, 21), 3)
    pygame.draw.circle(surf, (24, 20, 22), (43, 22), 2)

    # Near eye — oversized milky-white zombie ring holding a hot-red glowing
    # pupil. The additive bloom lands last so it sits over the ring.
    pygame.draw.circle(surf, (222, 216, 200), (50, 19), 5)
    pygame.draw.circle(surf, (150, 148, 132), (50, 19), 5, 1)
    pygame.draw.circle(surf, GASH_D, (50, 19), 2)
    _glow_blit(surf, (50, 19), EYE_GLOW, 5)
    pygame.draw.circle(surf, EYE_GLOW, (50, 19), 1)

    # Beak — dull, and hanging slightly agape.
    beak_pts = [(55, 21), (61, 24), (58, 28), (52, 26)]
    pygame.draw.polygon(surf, BEAK, beak_pts)
    pygame.draw.polygon(surf, NEARBLK, beak_pts, 1)
    pygame.draw.line(surf, NEARBLK, (53, 25), (59, 25), 1)

    # Feet — slack, sickly.
    pygame.draw.line(surf, BODY_D, (28, 45), (26, 49), 2)
    pygame.draw.line(surf, BODY_D, (34, 45), (36, 49), 2)
    return surf


_getter = _make_prebuilt_skin(_build_roadkill)


def build(frame_idx, tilt_deg):
    return _getter(frame_idx, tilt_deg)
