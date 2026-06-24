"""SKELETON redesign candidate — design_1: BONEWHITE.

Scratch exploration only (never registered in store_skins.BUILDERS). The fix
for the muted ivory-on-navy original is a value split, not a recolour: crank
the bone to pure WHITE, drop the flesh to near-black, and wrap a dark keyline
so the white survives even the brightest day sky. The skeleton read is the
whole costume — skull + socketed eyes, a bold paired rib ladder, a vertebra
spine, a finger-bone wing that clatters across the 4 flap poses, and bone legs.

Built like the live _build_skeleton_redraw: a full body redraw per wing angle,
wrapped by store_skins._make_prebuilt_skin so it picks up the _WING_ANGLES
flap poses, the outline pass, and the rotation cache for free.
"""
import math
import pygame

from game.store_skins import SPRITE_W, SPRITE_H, _make_prebuilt_skin, _poly
from game.parrot import _aaellipse


# Pure white is the brightest element; the body is near-black so the value
# split alone carries the read. The keyline sits between bone and sky.
_BONE    = (255, 255, 255)
_BONE_SH = (230, 233, 240)         # cool under-edge for roundness
_BODY    = (21, 22, 28)            # near-black "flesh" + socket interiors
_BODY_D  = (12, 13, 18)
_KEY     = (58, 61, 71)            # dark rim so white bone reads on day sky


def _finger_wing(angle_deg):
    """Wing as radiating finger-bones (phalanges) fanning from a bone wrist —
    near-black membrane behind so the white phalanges stay the read, with a
    keyline edge. Rotated with the flap so it reads as a clattering wing."""
    w = pygame.Surface((50, 50), pygame.SRCALPHA)
    membrane = [(24, 26), (47, 13), (50, 30), (34, 45), (18, 40)]
    _poly(w, _BODY, membrane)
    pygame.draw.polygon(w, _KEY, membrane, 1)

    wrist = (25, 28)
    # Splayed phalange tips — long leading finger down to a short trailing one.
    tips = [(47, 14), (49, 23), (46, 33), (38, 42), (28, 43)]
    for i, tip in enumerate(tips):
        col = _BONE if i < 3 else _BONE_SH
        pygame.draw.line(w, col, wrist, tip, 2)
        pygame.draw.circle(w, _BONE, tip, 2)            # knuckle cap
        # A mid-bone joint pip on the longer fingers for the segmented look.
        if i < 3:
            mid = ((wrist[0] + tip[0]) // 2, (wrist[1] + tip[1]) // 2)
            pygame.draw.circle(w, _BONE_SH, mid, 1)
    pygame.draw.circle(w, _BONE, wrist, 3)              # wrist knob
    pygame.draw.circle(w, _BODY_D, wrist, 1)
    return pygame.transform.rotate(w, angle_deg)


def _vertebra(surf, p0, p1, beads):
    """A short bead column from p0 to p1 — the spine tell."""
    for i in range(beads):
        t = i / (beads - 1)
        x = int(p0[0] + (p1[0] - p0[0]) * t)
        y = int(p0[1] + (p1[1] - p0[1]) * t)
        pygame.draw.circle(surf, _BONE, (x, y), 2)
        pygame.draw.circle(surf, _BONE_SH, (x, y), 2, 1)


def _build_design1(wing_angle_deg):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)

    # Tail + body + head as near-black masses (the value floor the bone sits on).
    _poly(surf, _BODY, [(2, 26), (17, 24), (23, 36), (12, 42)])
    pygame.draw.polygon(surf, _BODY_D, [(2, 26), (17, 24), (23, 36), (12, 42)], 1)
    _aaellipse(surf, _BODY_D, (33, 33), 19, 14)
    _aaellipse(surf, _BODY, (32, 32), 18, 13)
    _aaellipse(surf, _BODY_D, (48, 22), 12, 11)
    _aaellipse(surf, _BODY, (47, 21), 11, 10)

    # Spine — vertebra beads from the skull base down toward the ribcage.
    _vertebra(surf, (42, 27), (22, 38), 6)

    # Ribcage — a bold ladder of PAIRED white rib-arcs off a central sternum.
    pygame.draw.line(surf, _BONE, (38, 25), (24, 39), 2)        # sternum
    for i, ty in enumerate((26, 30, 34, 38)):
        sx = 38 - i * 3
        # Each rung is a pair of arcs sweeping out either side of the sternum.
        pygame.draw.arc(surf, _BONE, (sx - 12, ty - 5, 13, 12),
                        math.radians(20), math.radians(150), 2)
        pygame.draw.arc(surf, _BONE_SH, (sx - 1, ty - 5, 13, 12),
                        math.radians(30), math.radians(160), 2)

    # Wing — radiating finger-bones over the chest, centred + rotated by flap.
    wing = _finger_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    # Leg bones — thin paired bones with knob knees + 3-claw bone feet.
    for hx, fx in ((28, 27), (34, 35)):
        knee = (hx, 45)
        foot = (fx, 49)
        pygame.draw.line(surf, _BONE, (hx, 41), knee, 2)        # thigh
        pygame.draw.circle(surf, _BONE, knee, 2)                # knob knee
        pygame.draw.line(surf, _BONE, knee, foot, 2)            # shin
        for dx in (-2, 0, 2):
            pygame.draw.line(surf, _BONE_SH, foot, (foot[0] + dx, foot[1] + 3), 2)

    # Skull — bright white cranium with hollow sockets, nose hole, tooth grin.
    _aaellipse(surf, _BONE, (47, 20), 10, 9)                    # cranium
    _aaellipse(surf, _BONE, (47, 26), 7, 4)                     # jaw/muzzle
    # Two big hollow eye sockets (pure near-black holes) with a faint rim.
    for ex in (44, 50):
        pygame.draw.circle(surf, _BODY_D, (ex, 19), 3)
        pygame.draw.circle(surf, _KEY, (ex, 19), 3, 1)
    pygame.draw.circle(surf, (255, 255, 255), (51, 18), 1)     # life glint
    # Small triangular nose hollow.
    _poly(surf, _BODY_D, [(46, 23), (48, 23), (47, 26)])
    # Blocky tooth grin — vertical bone teeth with dark gaps.
    for gx in (43, 46, 49):
        pygame.draw.line(surf, _BODY_D, (gx, 27), (gx, 30), 1)
        pygame.draw.line(surf, _BONE_SH, (gx + 1, 27), (gx + 1, 30), 1)

    # Beak — near-black beak with a crisp white bone outline.
    beak_pts = [(55, 21), (61, 24), (58, 28), (52, 26)]
    _poly(surf, _BODY, beak_pts)
    pygame.draw.polygon(surf, _BONE, beak_pts, 2)

    return surf


build = _make_prebuilt_skin(_build_design1)
