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
BRAIN    = (229, 138, 160)          # exposed brain pink
BRAIN_D  = (206, 112, 136)          # brain-fold shadow
FISSURE  = (155, 78, 99)            # central fissure
OOZE     = (198, 245, 58)           # toxic yellow-green fluid
OOZE_D   = (150, 196, 40)           # ooze shadow
BOLT     = (174, 184, 190)          # galvanized bolt / staples / dome
BOLT_D   = (120, 130, 138)          # bolt shadow
DOME     = (150, 235, 255)          # glass dome tint
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

    # ── Sutured chest seam — clinical vertical incision, stapled shut.
    pygame.draw.line(surf, SEAM, (30, 29), (30, 43), 1)
    for sy in range(30, 44, 3):
        pygame.draw.line(surf, SEAM, (27, sy), (33, sy), 1)      # staple bed
        pygame.draw.line(surf, BOLT, (28, sy), (32, sy), 1)      # metal crimp

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

    # ── Cracked-open skull — the exposed brain, kept inside the head outline.
    # A dark opening rim first so the pink lobes read as sitting IN the skull.
    pygame.draw.arc(surf, SEAM, (39, 6, 16, 16), 0.2, 2.9, 2)
    _aaellipse(surf, BRAIN, (44, 14), 4, 3)                      # left lobe
    _aaellipse(surf, BRAIN, (50, 14), 4, 3)                      # right lobe
    _aaellipse(surf, BRAIN_D, (44, 15), 4, 2)                    # lobe shade
    _aaellipse(surf, BRAIN_D, (50, 15), 4, 2)
    _aaellipse(surf, BRAIN, (44, 13), 3, 2)                      # lobe crown
    _aaellipse(surf, BRAIN, (50, 13), 3, 2)
    for fy in (12, 14, 16):                                      # fold texture
        pygame.draw.line(surf, BRAIN_D, (42, fy), (45, fy - 1), 1)
        pygame.draw.line(surf, BRAIN_D, (49, fy), (52, fy - 1), 1)
    pygame.draw.line(surf, FISSURE, (47, 11), (47, 18), 1)      # central fissure
    # Cyan glass dome arcing over the specimen brain.
    pygame.draw.arc(surf, DOME, (39, 5, 16, 15), 0.15, 3.0, 1)
    pygame.draw.line(surf, DOME, (52, 11), (53, 14), 1)

    # ── Neck bolt — galvanized electrode jutting from the neck side.
    pygame.draw.rect(surf, BOLT_D, (37, 29, 7, 5))
    pygame.draw.rect(surf, BOLT, (37, 29, 6, 4))
    pygame.draw.circle(surf, BOLT, (37, 31), 3)
    pygame.draw.circle(surf, BOLT_D, (37, 31), 3, 1)
    pygame.draw.line(surf, BOLT_D, (40, 30), (43, 32), 1)

    # ── Spark — jagged electric arc from bolt cap to skull, on the surge flap.
    if surge:
        arc = [(37, 28), (40, 22), (37, 17), (42, 12)]
        pygame.draw.lines(surf, (200, 250, 255), False, arc, 3)
        pygame.draw.lines(surf, SPARK, False, arc, 1)
        pygame.draw.circle(surf, (220, 250, 255), (42, 12), 1)

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
