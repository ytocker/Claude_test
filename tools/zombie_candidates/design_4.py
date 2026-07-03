"""Zombie parrot candidate — DESIGN 4: LAB SPECIMEN #7.

A reanimated experiment: cracked-open skull with an exposed pink brain under
a cyan glass dome, a Frankenstein neck-bolt that arcs a spark on the down-flap,
a sutured chest seam stapled shut, radioactive ooze weeping from the seam, and
a stamped specimen tag on the leg. Reads as "science did this" at 40px because
the tells are big high-contrast blocks (pink brain vs. green skin, hot cyan
spark, toxic-chartreuse ooze) rather than fine detail.

Scratch exploration only — this is NOT registered in store_skins.BUILDERS.
Exposes ``build(frame_idx, tilt_deg) -> Surface`` via the prebuilt-skin getter.
"""
from __future__ import annotations

import pygame

from game.parrot import SPRITE_W, SPRITE_H, _aaellipse
from game.store_skins import _make_prebuilt_skin

# Embalmed corpse palette + the lab accents that carry the read.
BODY     = (126, 155, 134)          # embalmed gray-green
BODY_D   = (96, 122, 105)           # shaded green
BODY_H   = (156, 182, 162)          # lit green
BELLY    = (172, 194, 174)          # pale underside
SEAM     = (30, 39, 35)             # near-black outline / seam ink
BRAIN    = (235, 120, 150)          # exposed brain pink — saturated hero tell
BRAIN_D  = (198, 96, 124)           # brain shadow
FISSURE  = (150, 66, 90)            # central fissure cleft
OOZE     = (198, 245, 58)           # toxic yellow-green fluid
OOZE_D   = (150, 196, 40)           # ooze shadow
BOLT     = (174, 184, 190)          # galvanized bolt / stitch crimp
BOLT_D   = (120, 130, 138)          # bolt shadow
BOLT_H   = (210, 218, 220)          # bone-white bolt highlight
DOME_RIM = (170, 245, 255)          # cyan glass-dome crescent
SPARK    = (79, 227, 255)           # electric arc
BEAK     = (150, 150, 138)          # dead horn
TAG      = (222, 224, 210)          # specimen-tag band

# The down-flap pose is the "power surge": the bolt arcs a spark and the
# lowest ooze drip stretches. Keyed on wing angle so the getter animates it.
_SURGE_ANGLE = 40


def _ls_wing(angle_deg):
    w = pygame.Surface((50, 50), pygame.SRCALPHA)
    pts = [(24, 24), (44, 13), (48, 28), (32, 42), (18, 36)]
    pygame.draw.polygon(w, BODY, pts)
    pygame.draw.polygon(w, BODY_D, [(24, 24), (32, 42), (18, 36)])
    # A stapled tear across the flight feathers — the wing was operated on too.
    pygame.draw.line(w, SEAM, (28, 22), (44, 16), 1)
    for tx, ty in ((30, 21), (34, 19), (38, 18), (42, 16)):
        pygame.draw.line(w, BOLT, (tx - 1, ty - 1), (tx + 1, ty + 2), 1)
    pygame.draw.line(w, BODY_H, (26, 26), (30, 40), 1)
    return pygame.transform.rotate(w, angle_deg)


def _build_lab_specimen(wing_angle_deg):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    surge = wing_angle_deg >= _SURGE_ANGLE

    # Tail — corpse-green wedges fanning off the rump.
    for i, c in enumerate([BODY_D, BODY, BODY_H, BELLY]):
        pts = [(2 + i * 3, 26 + i * 2), (14 + i, 24 + i),
               (20 + i, 30 + i * 2), (6 + i * 3, 36 + i * 2)]
        pygame.draw.polygon(surf, c, pts)

    # Body.
    _aaellipse(surf, BODY_D, (34, 35), 19, 14)
    _aaellipse(surf, BODY, (32, 32), 19, 14)
    _aaellipse(surf, BODY_H, (30, 29), 13, 8)
    _aaellipse(surf, BELLY, (28, 38), 12, 6)

    # ── Sutured chest seam — a clinical incision closed with three bold
    # cross-stitches, spaced so each stays a discrete stitch at 40px.
    pygame.draw.line(surf, SEAM, (30, 29), (30, 44), 1)         # incision line
    for sy in (32, 37, 42):
        pygame.draw.line(surf, SEAM, (26, sy - 2), (34, sy + 2), 2)  # cross-stitch
        pygame.draw.line(surf, BOLT, (29, sy), (31, sy), 1)          # thread crimp

    # ── Toxic seep — radioactive ooze weeping out the bottom of the seam.
    glow = pygame.Surface((26, 30), pygame.SRCALPHA)
    pygame.draw.ellipse(glow, (*OOZE, 55), (2, 4, 22, 24))
    pygame.draw.ellipse(glow, (*OOZE, 90), (7, 8, 12, 16))
    surf.blit(glow, (17, 32))
    for dx, dy, dr in ((30, 43, 2), (29, 46, 2), (32, 45, 1)):
        pygame.draw.circle(surf, OOZE_D, (dx, dy + 1), dr)
        pygame.draw.circle(surf, OOZE, (dx, dy), dr)
    # Lowest drip elongates and drools on the power-surge (down) flap.
    tip_y = 52 if surge else 49
    pygame.draw.line(surf, OOZE_D, (30, 47), (30, tip_y), 2)
    pygame.draw.circle(surf, OOZE, (30, tip_y), 2)
    pygame.draw.circle(surf, (230, 255, 150), (29, tip_y - 1), 1)

    # Feet.
    pygame.draw.line(surf, BODY_D, (28, 45), (26, 49), 2)
    pygame.draw.line(surf, BODY_D, (34, 45), (36, 49), 2)

    # ── Specimen tag — stamped band on the leg with a segmented "7".
    pygame.draw.rect(surf, TAG, (24, 45, 6, 4))
    pygame.draw.rect(surf, BOLT_D, (24, 45, 6, 4), 1)
    pygame.draw.line(surf, SEAM, (25, 46), (28, 46), 1)          # 7 — top bar
    pygame.draw.line(surf, SEAM, (28, 46), (26, 48), 1)          # 7 — leg

    # Wing.
    wing = _ls_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    # Head.
    _aaellipse(surf, BODY_D, (48, 23), 12, 11)
    _aaellipse(surf, BODY, (47, 21), 12, 11)
    _aaellipse(surf, BODY_H, (46, 16), 7, 3)

    # ── Cracked-open skull — the exposed brain is THE hero tell: two big pink
    # lobes sitting proud of the skull line, joined into one two-bump shape and
    # split by a single central fissure so it reads as "brain" at 40px.
    pygame.draw.arc(surf, SEAM, (38, 6, 18, 16), 0.15, 3.0, 2)   # dark skull opening
    _aaellipse(surf, BRAIN_D, (44, 14), 5, 4)                    # left lobe shade
    _aaellipse(surf, BRAIN_D, (49, 14), 5, 4)                    # right lobe shade
    _aaellipse(surf, BRAIN, (44, 13), 5, 4)                      # left lobe
    _aaellipse(surf, BRAIN, (49, 13), 5, 4)                      # right lobe
    pygame.draw.line(surf, FISSURE, (46, 9), (46, 17), 1)        # central fissure cleft
    # One bold cyan crescent hugging the bumps = the glass specimen dome.
    pygame.draw.arc(surf, DOME_RIM, (38, 5, 18, 15), 0.15, 3.0, 2)

    # ── Neck bolt — a crisp horizontal electrode cylinder breaking the neck
    # silhouette: a flat-gray shaft with two end-caps, jutting out past the body.
    pygame.draw.rect(surf, BOLT_D, (32, 28, 12, 5))             # cylinder body
    pygame.draw.rect(surf, BOLT,   (33, 28, 10, 4))
    pygame.draw.rect(surf, BOLT_D, (31, 27, 3, 6))             # outer end-cap
    pygame.draw.rect(surf, BOLT,   (41, 27, 3, 6))             # inner end-cap
    pygame.draw.line(surf, BOLT_H, (33, 28), (43, 28), 1)     # bone-white top glint
    pygame.draw.rect(surf, SEAM,   (31, 27, 13, 6), 1)        # full dark outline

    # ── Spark — jagged electric arc anchored on the bolt cap, on the surge flap.
    if surge:
        arc = [(38, 28), (41, 22), (39, 16)]
        pygame.draw.lines(surf, (200, 250, 255), False, arc, 3)
        pygame.draw.lines(surf, SPARK, False, arc, 1)
        pygame.draw.circle(surf, (220, 250, 255), (39, 16), 1)

    # Sunken undead eyes — one milky wide, one small.
    pygame.draw.circle(surf, (208, 214, 202), (50, 19), 4)
    pygame.draw.circle(surf, SEAM, (50, 20), 2)
    pygame.draw.circle(surf, (204, 210, 198), (44, 21), 2)
    pygame.draw.circle(surf, SEAM, (44, 21), 1)
    pygame.draw.circle(surf, (255, 255, 255), (49, 18), 1)

    # Beak — dead horn with a dark outline.
    beak_pts = [(55, 21), (61, 24), (58, 28), (52, 26)]
    pygame.draw.polygon(surf, BEAK, beak_pts)
    pygame.draw.polygon(surf, SEAM, beak_pts, 1)
    # Stitched-shut grimace under the beak.
    pygame.draw.line(surf, SEAM, (52, 30), (58, 29), 1)
    for gx in (53, 55, 57):
        pygame.draw.line(surf, SEAM, (gx, 28), (gx, 31), 1)

    return surf


build = _make_prebuilt_skin(_build_lab_specimen)
