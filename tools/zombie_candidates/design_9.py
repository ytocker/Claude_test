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
HELM     = (75, 81, 87)       # steel — darkened so it separates from the drab body against a bright sky
HELM_D   = (40, 44, 48)       # helmet underside shadow
HELM_H   = (128, 134, 140)    # rivet / mid glint
HELM_G   = (220, 225, 230)    # near-white metallic sheen on the crown
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

    # Dog tag — ONE larger, brighter plate on a short glint chain across the
    # neck. A single bold tag survives at 40px where two small plates dissolve
    # into speckle noise.
    pygame.draw.line(surf, (192, 188, 174), (28, 28), (37, 31), 1)
    pygame.draw.rect(surf, (198, 192, 176), (31, 33, 6, 4), border_radius=1)
    pygame.draw.line(surf, (120, 116, 104), (32, 35), (35, 35), 1)
    pygame.draw.line(surf, (232, 228, 214), (32, 33), (34, 33), 1)

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

    # Slack jaw — the mandible has come unhinged and hangs open, leaving a
    # dark wedge of open mouth between the upper beak and the dropped lower
    # jaw. Drawn first so both beak and jaw seat over the shadow.
    pygame.draw.polygon(surf, (14, 12, 10), [(52, 25), (61, 26), (59, 31), (52, 29)])

    # Upper beak — normal shape, desaturated to a dead horn.
    beak_pts = [(55, 21), (61, 24), (60, 26), (52, 24)]
    pygame.draw.polygon(surf, BEAK, beak_pts)
    pygame.draw.polygon(surf, NEARBLK, beak_pts, 1)

    # Dropped lower mandible — one clean exposed-bone shape hung well below the
    # beak, a single crack line instead of a hatch cluster.
    jaw = [(52, 30), (60, 31), (58, 36), (53, 36), (50, 33)]
    pygame.draw.polygon(surf, BONE, jaw)
    pygame.draw.polygon(surf, (150, 142, 118), jaw, 1)
    pygame.draw.line(surf, (120, 114, 92), (55, 31), (55, 35), 1)

    # Milky undead eye — the near eye is a blank cataract with a dim off-center
    # pupil. The far eye sits deep in the brim shadow.
    pygame.draw.circle(surf, HELM_D, (44, 21), 3)
    pygame.draw.circle(surf, (60, 56, 50), (44, 22), 1)
    pygame.draw.circle(surf, (200, 196, 184), (50, 19), 4)
    pygame.draw.circle(surf, (150, 148, 138), (50, 19), 4, 1)
    pygame.draw.circle(surf, (70, 68, 62), (51, 20), 2)

    # ── Steel helmet — the hero tell (no other zombie wears a hat). A shallow
    # Brodie-style shell CLAMPED onto the skull: a wide flat brim whose dark
    # underside overlaps the crown, capped by a short dome. The read at 40px is
    # brim-plus-shallow-dome widening the head — never a floating mushroom.
    #
    # Brim underside (dark) first — wide + flat, dipping over the skull crown so
    # a dark band shows beneath the front lip and the helmet reads as SEATED.
    brim = pygame.Rect(0, 0, 32, 6)
    brim.center = (48, 15)
    pygame.draw.ellipse(surf, HELM_D, brim)
    # Brim top face — lifted 2px so the dark underside band stays visible below.
    brim_top = pygame.Rect(0, 0, 32, 5)
    brim_top.center = (48, 13)
    pygame.draw.ellipse(surf, HELM, brim_top)
    # Dome — a SHORT shell (wider than tall) seated low on the crown so it tucks
    # into the brim with no air gap.
    dome = pygame.Rect(0, 0, 28, 14)
    dome.center = (48, 11)
    pygame.draw.ellipse(surf, HELM, dome)
    # Dark seam where the dome tucks under the brim at the back and sides.
    pygame.draw.arc(surf, HELM_D, dome.inflate(-2, 0), 3.34, 6.09, 2)
    # Metallic sheen — a near-white glint keeps the shell reading as a separate
    # hard object above the drab army-green body.
    pygame.draw.arc(surf, HELM_G, dome.inflate(-8, -3), 0.7, 2.1, 2)
    pygame.draw.line(surf, HELM_G, (43, 8), (52, 7), 1)
    # Battle dent — a dark notch driven into the crown.
    pygame.draw.polygon(surf, HELM_D, [(53, 6), (57, 8), (53, 10), (51, 8)])
    # Rivet on the brim.
    pygame.draw.circle(surf, RIVET, (36, 14), 2)
    pygame.draw.circle(surf, HELM_D, (36, 14), 2, 1)
    # Chinstrap — a single dark strap from the brim edge down past the jaw
    # hinge. Cheapest, clearest cue that locks "military helmet" at a glance.
    pygame.draw.line(surf, NEARBLK, (51, 16), (53, 28), 2)

    # Feet — slack.
    pygame.draw.line(surf, BODY_D, (28, 45), (26, 49), 2)
    pygame.draw.line(surf, BODY_D, (34, 45), (36, 49), 2)
    return surf


_getter = _make_prebuilt_skin(_build_war)


def build(frame_idx, tilt_deg):
    return _getter(frame_idx, tilt_deg)
