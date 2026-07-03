"""ROADKILL FRESH-TURNED — zombie parrot candidate (Design 1, scratch).

A *recently* mangled bird: the healthy silhouette is still legible, which is
what sells the fresh-kill horror — it hasn't rotted, it was just torn open.
The read is carried by a wet chest gash with exposed ribs, one hot glowing
eye against a milky dead ring, a torn bruise-toned wing hung low, and a
couple of blood drips. Scratch explorer only — NOT registered in
``store_skins.BUILDERS``; exposes ``build(frame_idx, tilt_deg) -> Surface``.
"""
from __future__ import annotations

import pygame

from game.parrot import SPRITE_W, SPRITE_H, _aaellipse
from game.store_skins import _make_prebuilt_skin

# Fresh-turned palette — a sick green-gray body (alive enough to still be a
# parrot) so the saturated wound reds and bone whites do all the shouting.
BODY    = (110, 138, 94)
BODY_D  = (36, 48, 33)
BODY_H  = (140, 166, 118)
BELLY   = (156, 176, 132)
GASH_D  = (122, 20, 20)      # clotted rim
GASH_H  = (199, 48, 43)      # wet, fresh center
BONE    = (233, 228, 208)
EYE_GLOW = (255, 58, 46)
BRUISE   = (96, 62, 84)      # torn-flesh purple on the ragged wing
BRUISE_D = (60, 38, 54)
WING     = (92, 116, 78)
WING_D   = (54, 72, 46)
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
    """Trailing edge is a 3-notch saw-tooth in a bruise tone — the flesh got
    ripped, not moulted. Kept as its own surface so it rotates with the flap."""
    w = pygame.Surface((52, 52), pygame.SRCALPHA)
    # Leading body of the wing, then a downward saw of three ragged teeth.
    pts = [
        (24, 23), (46, 15), (49, 26),
        (45, 33), (42, 27), (38, 34), (34, 28), (30, 35), (26, 29),
        (20, 33), (17, 27),
    ]
    pygame.draw.polygon(w, WING, pts)
    # Underside shadow keeps the torn edge from reading flat.
    pygame.draw.polygon(w, WING_D, [(24, 23), (17, 27), (20, 33), (30, 35)])
    # Bruise smear staining the ripped teeth.
    pygame.draw.polygon(w, BRUISE, [(45, 33), (42, 27), (38, 34),
                                    (34, 28), (30, 35), (26, 29), (24, 31)])
    pygame.draw.polygon(w, BRUISE_D, [(38, 34), (34, 28), (30, 35), (32, 33)])
    pygame.draw.line(w, WING_D, (26, 24), (44, 18), 1)
    return pygame.transform.rotate(w, angle_deg)


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

    # Split-open back seam — a dark jagged tear down the far side, hinting the
    # whole flank is peeled. Sits behind the wing so it reads as depth.
    seam = [(20, 24), (17, 29), (19, 34), (16, 39), (18, 43)]
    pygame.draw.lines(surf, BODY_D, False, seam, 2)
    pygame.draw.lines(surf, GASH_D, False,
                      [(19, 27), (18, 31), (17, 37)], 1)

    # Chest gash — almond/lens wound low on the belly, wet center inset in the
    # clotted rim, hard near-black outline so it punches at gameplay scale.
    gash = [(22, 39), (28, 35), (35, 38), (31, 43), (25, 43)]
    inner = [(25, 39), (29, 37), (32, 39), (29, 42), (26, 42)]
    pygame.draw.polygon(surf, GASH_D, gash)
    pygame.draw.polygon(surf, GASH_H, inner)
    pygame.draw.polygon(surf, NEARBLK, gash, 2)

    # Exposed ribs — three bone segments fanning out of the top of the gash,
    # arced to ride the belly curve.
    ribs = [
        [(24, 37), (23, 34), (25, 32)],
        [(28, 35), (28, 32), (30, 30)],
        [(32, 37), (34, 34), (35, 32)],
    ]
    for r in ribs:
        pygame.draw.lines(surf, BONE, False, r, 2)

    # Blood drips — fresh ooze hanging off the lower lip of the wound.
    _aaellipse(surf, GASH_D, (27, 45), 2, 3)
    _aaellipse(surf, GASH_H, (27, 44), 1, 1)
    _aaellipse(surf, GASH_D, (31, 46), 1, 2)

    # Wing — hung low (dropped y) so one side droops, mangled.
    wing = _roadkill_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 31)).topleft)

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
