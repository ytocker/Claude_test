"""GREASEPAINT GRAVE JESTER — zombie parrot candidate (Design 10, scratch).

A carnival-horror clown that died in costume. The read is carried by three
silhouette-and-block tells that survive the 40px downscale: a torn ruffle
collar of big scalloped lobes that break the body outline and visibly widen
the neckline, a stark greasepaint face reduced to exactly two dark marks (a
bold up-hooked grin crescent and the dead-clown eye asymmetry), and a faded
grey-purple costume body that never crushes to "crow" on a bright sky. Scratch
explorer only — NOT registered in ``store_skins.BUILDERS``; exposes
``build(frame_idx, tilt_deg) -> Surface``.
"""
from __future__ import annotations

import math

import pygame

from game.parrot import SPRITE_W, SPRITE_H, _aaellipse
from game.store_skins import _make_prebuilt_skin

# Palette — a costume worn too long. The body is a faded grey-purple that keeps
# its value up on a bright day sky (never a crow silhouette); the greasepaint
# white, the faded collar red, and TWO near-black facial marks carry the read.
GREASE   = (237, 230, 222)     # off-white greasepaint
GREASE_D = (205, 197, 188)     # greasepaint in shadow (edge of the mask)
ROT      = (124, 114, 102)     # rotting grey flesh under flaked paint
ROT_D    = (92, 84, 76)        # deeper rot crevice / sunken socket rim
COLLAR   = (176, 62, 62)       # faded ruff red
COLLAR_D = (120, 36, 36)       # darker scallop tip (outer crescent)
COLLAR_H = (208, 104, 96)      # lighter-red highlight — overlapping-fabric read
BODY     = (100, 90, 114)      # faded grey-purple costume — value kept up
BODY_D   = (70, 62, 84)
BODY_H   = (128, 118, 146)
BELLY    = (114, 106, 132)
SHADOW   = (54, 48, 64)        # a soft purple shadow — deliberately NOT near-black
DARK     = (26, 22, 22)        # horror near-black — ONLY the grin + eyes use this
BEAK     = (150, 122, 88)      # dull, no live gloss
BEAK_D   = (96, 76, 52)        # beak edge — kept off the reserved near-black
WING     = (88, 80, 104)
WING_D   = (60, 54, 76)
WING_VD  = (40, 36, 52)        # torn-notch shadow — a deep purple, not true black


def _jester_wing(angle_deg):
    """Leaf wing in dusty costume tones with one torn notch chewed from the
    trailing edge — the damage stays a silhouette event at 40px. The notch
    stays a deep purple so the reserved near-black belongs to the face alone."""
    w = pygame.Surface((52, 52), pygame.SRCALPHA)
    pts = [(24, 22), (46, 15), (49, 26), (44, 32), (20, 33), (17, 27)]
    pygame.draw.polygon(w, WING, pts)
    pygame.draw.polygon(w, WING_D, [(24, 22), (17, 27), (20, 33), (32, 32)])
    pygame.draw.polygon(w, WING_VD, [(43, 30), (36, 24), (35, 32)])
    pygame.draw.line(w, WING_D, (26, 24), (44, 18), 1)
    return pygame.transform.rotate(w, angle_deg)


def _draw_collar(surf):
    """A torn ruff of BIG overlapping scallop lobes ringing the throat and
    upper chest. The lobes are seated so their outer tips clear the body edge
    on the right and bottom — the neckline visibly widens and the silhouette
    bumps at the neck, which is this concept's hero break. Drawn back-to-front
    (left→right) so the frontmost lobes overlap. Each lobe: a darker scallop
    tip pushed outward, the main red body, then a lighter-red highlight pulled
    toward the neck so overlapping ruff fabric reads instead of a flat smear."""
    neck = (46.0, 29.0)
    # Ordered back (chest-left) to front (throat-right) so the near lobes win.
    lobes = [(38, 39), (42, 41), (47, 40), (52, 36), (53, 30)]
    nx, ny = neck
    for lx, ly in lobes:
        dx, dy = lx - nx, ly - ny
        d = math.hypot(dx, dy) or 1.0
        ox, oy = dx / d, dy / d
        # Outer dark crescent pushed further out — this is the tip that breaks
        # and bumps the body outline.
        pygame.draw.circle(surf, COLLAR_D,
                           (round(lx + ox * 2), round(ly + oy * 2)), 5)
        pygame.draw.circle(surf, COLLAR, (round(lx), round(ly)), 5)
        pygame.draw.circle(surf, COLLAR_H,
                           (round(lx - ox * 2), round(ly - oy * 2)), 2)
    # A soft crease along the collar's upper edge so the ruff reads as a layer
    # tucked under the chin rather than paint on the chest.
    pygame.draw.lines(surf, SHADOW, False,
                      [(40, 31), (46, 33), (52, 31), (56, 28)], 1)


def _build_jester(wing_angle_deg):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)

    # Tail — faded wedges, darkest at the root.
    for i, c in enumerate([SHADOW, BODY_D, BODY, BODY_H]):
        pts = [(2 + i * 3, 26 + i * 2), (14 + i, 24 + i),
               (20 + i, 30 + i * 2), (6 + i * 3, 36 + i * 2)]
        pygame.draw.polygon(surf, c, pts)

    # Body — overlapping ellipses in the faded grey-purple costume.
    _aaellipse(surf, BODY_D, (34, 35), 19, 14)
    _aaellipse(surf, BODY, (32, 32), 19, 14)
    _aaellipse(surf, BODY_H, (30, 29), 13, 8)
    _aaellipse(surf, BELLY, (28, 38), 12, 6)

    # Wing before the collar so the ruff sits proud over the chest.
    wing = _jester_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    # Ruffle collar — before the head so the ruff tucks behind the chin and its
    # outer scallops break the body silhouette below/right of the head.
    _draw_collar(surf)

    # Head base (faded), then the greasepaint mask over the front of the face.
    _aaellipse(surf, BODY_D, (48, 23), 12, 11)
    _aaellipse(surf, BODY, (47, 21), 12, 11)
    # Greasepaint patch — a bright off-white block that reads on any sky.
    _aaellipse(surf, GREASE_D, (47, 20), 11, 10)
    _aaellipse(surf, GREASE, (48, 20), 9, 8)

    # Peeling paint as a SILHOUETTE notch — a rot-coloured bite taken out of the
    # lower-left edge of the greasepaint patch, so the white block's outline is
    # chewed rather than the face carrying an interior speckle.
    pygame.draw.polygon(surf, ROT, [(38, 24), (43, 26), (41, 29), (36, 28)])

    # Eyes — dead-clown asymmetry, EXAGGERATED so the two shapes never merge.
    # Far eye: a solid sunken socket, a dark filled hollow with a rot rim and no
    # competing pinlight.
    pygame.draw.circle(surf, ROT_D, (43, 19), 4)
    pygame.draw.circle(surf, DARK, (43, 19), 3)
    # Near eye: an oversized clown X, thick and clearly diagonal, riding onto
    # the white face. Nudged clear of the socket so both read distinctly.
    pygame.draw.line(surf, DARK, (48, 14), (54, 21), 3)
    pygame.draw.line(surf, DARK, (54, 14), (48, 21), 3)

    # Beak — dull horn, kept small so the grin dwarfs it. Edge stays off the
    # reserved near-black.
    beak_pts = [(55, 22), (61, 25), (58, 28), (53, 26)]
    pygame.draw.polygon(surf, BEAK, beak_pts)
    pygame.draw.polygon(surf, BEAK_D, beak_pts, 1)

    # Horror grin — one bold, near-black, UP-HOOKED crescent set CLEARLY BELOW
    # the eyes, its corners hooking up past both sides of the beak. This is the
    # single widest dark mark on the sprite.
    grin = [(40, 25), (46, 29), (52, 30), (58, 29), (63, 25),
            (59, 31), (52, 34), (45, 31)]
    pygame.draw.polygon(surf, DARK, grin)
    # Three bold triangular teeth — greasepaint tabs riding the crescent (real
    # tabs, not 1–2px rects that vanish at scale).
    for tri in ([(45, 30), (48, 30), (46, 33)],
                [(49, 30), (52, 30), (50, 33)],
                [(53, 29), (56, 29), (54, 32)]):
        pygame.draw.polygon(surf, GREASE, tri)

    # Feet — slack, faded.
    pygame.draw.line(surf, BODY_D, (28, 45), (26, 49), 2)
    pygame.draw.line(surf, BODY_D, (34, 45), (36, 49), 2)
    return surf


_getter = _make_prebuilt_skin(_build_jester)


def build(frame_idx, tilt_deg):
    return _getter(frame_idx, tilt_deg)
