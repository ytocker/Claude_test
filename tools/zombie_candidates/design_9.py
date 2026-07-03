"""TRENCH-DEAD WAR PARROT — zombie parrot candidate (Design 9, scratch).

A soldier that fell in the trenches and got back up. The read is carried by
HARD manufactured gear against organic rot: a dented steel helmet whose dome
reshapes the head silhouette (the hero tell — no other zombie has a hat), a
clean punched bullet-hole void in the chest, and a pair of dog tags glinting
on a chain. Field-drab army-green body under it all. Scratch explorer only —
NOT registered in ``store_skins.BUILDERS``; exposes
``build(frame_idx, tilt_deg) -> Surface``.
"""
from __future__ import annotations

import pygame

from game.parrot import SPRITE_W, SPRITE_H, _aaellipse
from game.store_skins import _make_prebuilt_skin

# Field-drab palette — the body is pushed to a pallid army-green so the cold
# steel helmet and the near-black wound void both read as "not organic".
BODY     = (107, 115, 80)     # pallid army-green (field drab)
BODY_D   = (58, 62, 42)       # rot shadow
BODY_H   = (138, 146, 108)
BELLY    = (150, 156, 118)
HELM     = (90, 96, 102)      # steel
HELM_D   = (50, 54, 58)       # helmet underside shadow
HELM_H   = (128, 134, 140)    # top glint / rivet
RIVET    = (130, 136, 140)
WOUND    = (20, 18, 14)       # punched void
WOUND_R  = (50, 46, 40)       # scorched dark ring
BONE     = (203, 195, 166)    # exposed jaw + dog tags
TAG      = (180, 174, 158)
CHAIN    = (150, 146, 132)
BEAK     = (150, 150, 92)     # desaturated horn, no gloss
WING     = (86, 94, 64)
WING_D   = (52, 58, 40)
NEARBLK  = (24, 22, 18)


def _war_wing(angle_deg):
    """Drab leaf wing with a dark ragged inner shadow. Kept on its own surface
    so it rotates with the flap and never occludes the chest gear."""
    w = pygame.Surface((52, 52), pygame.SRCALPHA)
    pts = [(24, 22), (46, 15), (49, 26), (44, 32), (20, 33), (17, 27)]
    pygame.draw.polygon(w, WING, pts)
    pygame.draw.polygon(w, WING_D, [(24, 22), (17, 27), (20, 33), (32, 32)])
    pygame.draw.line(w, WING_D, (26, 24), (44, 18), 2)
    pygame.draw.line(w, (162, 168, 130), (25, 25), (43, 17), 1)
    return pygame.transform.rotate(w, angle_deg)


def _build_war(wing_angle_deg):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)

    # Tail — drab wedges, darkest at the root.
    for i, c in enumerate([BODY_D, WING_D, BODY, BODY_H]):
        pts = [(2 + i * 3, 26 + i * 2), (14 + i, 24 + i),
               (20 + i, 30 + i * 2), (6 + i * 3, 36 + i * 2)]
        pygame.draw.polygon(surf, c, pts)

    # Body — overlapping ellipses, belly lifted so the wound punches high-
    # contrast against pale flesh.
    _aaellipse(surf, BODY_D, (34, 35), 19, 14)
    _aaellipse(surf, BODY, (32, 32), 19, 14)
    _aaellipse(surf, BODY_H, (30, 28), 13, 8)
    _aaellipse(surf, BELLY, (28, 38), 12, 6)

    # Near wing — drawn before the chest gear so nothing occludes the read.
    wing = _war_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 30)).topleft)

    # Dog tags — a thin chain looping across the upper chest with two small
    # metal plates hanging low. The metallic accent sells the soldier theme.
    pygame.draw.line(surf, CHAIN, (26, 26), (33, 25), 1)
    pygame.draw.line(surf, CHAIN, (33, 25), (33, 39), 1)
    for tx, ty in ((31, 39), (35, 41)):
        pygame.draw.rect(surf, TAG, (tx, ty, 3, 5), border_radius=1)
        pygame.draw.line(surf, NEARBLK, (tx + 1, ty + 2), (tx + 2, ty + 2), 1)

    # Bullet wound — one clean punched void mid-chest: a near-black hole inside
    # a slightly larger scorched ring. High contrast against the pale flank.
    wx, wy = 29, 33
    _aaellipse(surf, WOUND_R, (wx, wy), 7, 6)
    pygame.draw.circle(surf, WOUND, (wx, wy), 5)
    pygame.draw.circle(surf, (12, 10, 8), (wx, wy - 1), 2)

    # Head — sits under the helmet dome.
    _aaellipse(surf, BODY_D, (48, 23), 12, 11)
    _aaellipse(surf, BODY, (47, 21), 12, 11)
    _aaellipse(surf, BODY_H, (46, 17), 7, 3)

    # Rotting lower jaw — an exposed bone polygon dropped slack below the beak,
    # as if the mandible has come unhinged.
    jaw = [(52, 27), (60, 28), (58, 33), (53, 33), (50, 30)]
    pygame.draw.polygon(surf, BONE, jaw)
    pygame.draw.polygon(surf, (150, 142, 118), jaw, 1)
    for jx in (54, 56, 58):
        pygame.draw.line(surf, (120, 114, 92), (jx, 28), (jx, 32), 1)

    # Upper beak — normal shape, desaturated to a dead horn.
    beak_pts = [(55, 21), (61, 24), (58, 27), (52, 25)]
    pygame.draw.polygon(surf, BEAK, beak_pts)
    pygame.draw.polygon(surf, NEARBLK, beak_pts, 1)

    # Milky undead eye — the near eye is a blank cataract with a dim off-center
    # pupil. The far eye sits deep in the brim shadow.
    pygame.draw.circle(surf, HELM_D, (44, 21), 3)
    pygame.draw.circle(surf, (60, 56, 50), (44, 22), 1)
    pygame.draw.circle(surf, (200, 196, 184), (50, 19), 4)
    pygame.draw.circle(surf, (150, 148, 138), (50, 19), 4, 1)
    pygame.draw.circle(surf, (70, 68, 62), (51, 20), 2)

    # ── Steel helmet — the hero tell. Drawn OVER the head, deliberately LARGER
    # than the skull so the dome + brim reshape the silhouette. Brim first so
    # the dome overlaps its back edge.
    brim = pygame.Rect(0, 0, 34, 6)
    brim.center = (48, 13)
    pygame.draw.ellipse(surf, HELM_D, brim)
    pygame.draw.ellipse(surf, HELM, brim.inflate(0, -2))
    # Dome — a wide filled ellipse capping the crown, taller than the head.
    dome = pygame.Rect(0, 0, 30, 20)
    dome.center = (48, 9)
    pygame.draw.ellipse(surf, HELM, dome)
    # Underside shadow band where the dome meets the head, and a top glint.
    pygame.draw.arc(surf, HELM_D, dome.inflate(-2, -2), 3.34, 6.09, 2)
    pygame.draw.arc(surf, HELM_H, dome.inflate(-6, -6), 0.5, 2.2, 2)
    # Battle dent — a dark notch driven into the crown.
    pygame.draw.polygon(surf, HELM_D, [(52, 3), (56, 5), (52, 7), (50, 5)])
    # Rivet on the brim.
    pygame.draw.circle(surf, RIVET, (37, 13), 2)
    pygame.draw.circle(surf, HELM_D, (37, 13), 2, 1)

    # Feet — slack.
    pygame.draw.line(surf, BODY_D, (28, 45), (26, 49), 2)
    pygame.draw.line(surf, BODY_D, (34, 45), (36, 49), 2)
    return surf


_getter = _make_prebuilt_skin(_build_war)


def build(frame_idx, tilt_deg):
    return _getter(frame_idx, tilt_deg)
