"""GREASEPAINT GRAVE JESTER — zombie parrot candidate (Design 10, scratch).

A carnival-horror clown that died in costume. The read is carried by three
silhouette-and-block tells that survive the 40px downscale: a torn ruffle
collar that visibly widens the neckline, a stark greasepaint face that reads
as a bright block on any sky, and a too-wide stitched grin. Rot shows where
the makeup has flaked off a corpse, and the eyes are the classic dead-clown
asymmetry — a dead X against a hollow sunken socket. Scratch explorer only —
NOT registered in ``store_skins.BUILDERS``; exposes
``build(frame_idx, tilt_deg) -> Surface``.
"""
from __future__ import annotations

import math

import pygame

from game.parrot import SPRITE_W, SPRITE_H, _aaellipse
from game.store_skins import _make_prebuilt_skin

# Palette — a costume worn too long. The body is pushed to a dusty purple-grey
# so the greasepaint white and faded collar red carry all the contrast.
GREASE   = (237, 230, 222)     # off-white greasepaint
GREASE_D = (205, 197, 188)     # greasepaint in shadow (edge of the mask)
ROT      = (124, 114, 102)     # rotting grey flesh under flaked paint
ROT_D    = (92, 84, 76)        # deeper rot crevice
COLLAR   = (168, 58, 58)       # faded ruff red
COLLAR_D = (120, 36, 36)       # darker scallop tip
BODY     = (78, 74, 82)        # dusty, slightly-purple corpse costume
BODY_D   = (48, 45, 52)
BODY_H   = (104, 100, 110)
BELLY    = (92, 88, 98)
SHADOW   = (35, 32, 38)
DARK     = (26, 22, 22)        # horror near-black (grin, X-eye)
BEAK     = (150, 122, 88)      # dull, no live gloss
WING     = (66, 62, 72)
WING_D   = (42, 39, 47)


def _jester_wing(angle_deg):
    """Leaf wing in dusty costume tones with one torn near-black notch chewed
    from the trailing edge — the damage stays a silhouette event at 40px. Kept
    on its own surface so it rotates with the flap."""
    w = pygame.Surface((52, 52), pygame.SRCALPHA)
    pts = [(24, 22), (46, 15), (49, 26), (44, 32), (20, 33), (17, 27)]
    pygame.draw.polygon(w, WING, pts)
    pygame.draw.polygon(w, WING_D, [(24, 22), (17, 27), (20, 33), (32, 32)])
    pygame.draw.polygon(w, DARK, [(43, 30), (36, 24), (35, 32)])
    pygame.draw.line(w, WING_D, (26, 24), (44, 18), 1)
    return pygame.transform.rotate(w, angle_deg)


def _draw_collar(surf, nx, ny):
    """A torn ruff of overlapping scallop lobes ringing the neck. Spans the
    lower two-thirds of the neck (open toward the head at upper-right) and
    reaches past the body outline so the neckline silhouette visibly widens —
    the primary tell. Each lobe darkens at its outer tip for the scallop read."""
    R = 9                       # lobe seat radius from the neck pivot
    lobe = 5
    for deg in (18, 54, 90, 126, 162, 200, 238):
        a = math.radians(deg)
        lx = nx + R * math.cos(a)
        ly = ny + R * math.sin(a)     # sin is downward in screen space
        pygame.draw.circle(surf, COLLAR, (int(lx), int(ly)), lobe)
        tx = nx + (R + 3) * math.cos(a)
        ty = ny + (R + 3) * math.sin(a)
        pygame.draw.circle(surf, COLLAR_D, (int(tx), int(ty)), 2)
    # A dark shadow crease where the ruff meets the body, so the collar reads as
    # a separate layer rather than a red smear on the chest.
    pygame.draw.arc(surf, SHADOW, pygame.Rect(nx - 9, ny - 5, 18, 20),
                    math.radians(200), math.radians(340), 2)


def _build_jester(wing_angle_deg):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)

    # Tail — dusty wedges, darkest at the root.
    for i, c in enumerate([SHADOW, BODY_D, BODY, BODY_H]):
        pts = [(2 + i * 3, 26 + i * 2), (14 + i, 24 + i),
               (20 + i, 30 + i * 2), (6 + i * 3, 36 + i * 2)]
        pygame.draw.polygon(surf, c, pts)

    # Body — overlapping ellipses in the dusty costume grey.
    _aaellipse(surf, BODY_D, (34, 35), 19, 14)
    _aaellipse(surf, BODY, (32, 32), 19, 14)
    _aaellipse(surf, BODY_H, (30, 29), 13, 8)
    _aaellipse(surf, BELLY, (28, 38), 12, 6)

    # Wing before the collar so the ruff sits proud over the chest.
    wing = _jester_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    # Ruffle collar — drawn over the body at the neck junction.
    _draw_collar(surf, 42, 27)

    # Head base (dusty), then the greasepaint mask over the front of the face.
    _aaellipse(surf, BODY_D, (48, 23), 12, 11)
    _aaellipse(surf, BODY, (47, 21), 12, 11)
    # Greasepaint patch — a bright off-white block that reads on any sky. Two
    # ellipses give a soft shaded rim so the mask has a painted-on edge.
    _aaellipse(surf, GREASE_D, (47, 20), 11, 10)
    _aaellipse(surf, GREASE, (48, 20), 9, 8)

    # Rot peeling — a jagged grey polygon where the greasepaint has FLAKED away
    # over the upper cheek, exposing rotting flesh. A darker crevice inside sells
    # the depth of the "makeup peeling off a corpse".
    flake = [(40, 15), (45, 13), (47, 17), (44, 20), (39, 21), (37, 18)]
    pygame.draw.polygon(surf, ROT, flake)
    pygame.draw.polygon(surf, ROT_D, [(41, 16), (44, 15), (43, 19), (40, 19)])
    pygame.draw.polygon(surf, GREASE_D, flake, 1)   # crusted paint edge

    # Eyes — dead-clown asymmetry.
    # Far eye: a hollow sunken socket, a dark filled pit with one cold pinlight.
    pygame.draw.circle(surf, ROT_D, (44, 21), 4)
    pygame.draw.circle(surf, DARK, (44, 21), 3)
    pygame.draw.circle(surf, (150, 146, 152), (43, 20), 1)   # pinlight
    # Near eye: a dead X of two crossing lines painted over the white face.
    pygame.draw.line(surf, DARK, (48, 16), (53, 22), 2)
    pygame.draw.line(surf, DARK, (53, 16), (48, 22), 2)

    # Beak — dull horn, kept small so the grin can dwarf it.
    beak_pts = [(55, 21), (61, 24), (58, 28), (52, 26)]
    pygame.draw.polygon(surf, BEAK, beak_pts)
    pygame.draw.polygon(surf, DARK, beak_pts, 1)

    # Horror grin — a too-wide stitched smile that extends well past the beak on
    # both sides. Corners hooked up, dipping in the middle; near-black and thick.
    grin = [(41, 25), (46, 29), (52, 30), (58, 28), (63, 23)]
    pygame.draw.lines(surf, DARK, False, grin, 3)
    # A few visible teeth: light greasepaint tabs riding the grin line, with two
    # dark tooth-gap rects cutting between them.
    for tx in (47, 51, 55):
        pygame.draw.rect(surf, GREASE, (tx, 27, 2, 3))
    for gx in (49, 53):
        pygame.draw.rect(surf, DARK, (gx, 27, 1, 3))

    # Feet — slack, dusty.
    pygame.draw.line(surf, BODY_D, (28, 45), (26, 49), 2)
    pygame.draw.line(surf, BODY_D, (34, 45), (36, 49), 2)
    return surf


_getter = _make_prebuilt_skin(_build_jester)


def build(frame_idx, tilt_deg):
    return _getter(frame_idx, tilt_deg)
