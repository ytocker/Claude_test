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

Round 2 — at 40px the two sockets must stay distinct holes (≥2px white bridge
+ ≥2px white cranium above), the wing must read as radiating WHITE finger-bones
(no solid dark cape field), a #3A3D47 keyline must rim the white so it never
sits on bright sky, a vertebra spine carries the centerline, and the grin is a
committed white tooth bar — not a smudge.
"""
import math
import pygame

from game.store_skins import SPRITE_W, SPRITE_H, _make_prebuilt_skin, _poly
from game.parrot import _aaellipse


# Pure white is the brightest element; the body is near-black so the value
# split alone carries the read. The keyline sits between bone and sky.
_BONE    = (255, 255, 255)
_BONE_SH = (230, 233, 240)         # cool under-edge (#E6E9F0) for roundness
_BODY    = (21, 22, 28)            # near-black "flesh" + socket interiors (#15161C)
_BODY_D  = (12, 13, 18)
_KEY     = (58, 61, 71)            # keyline rim (#3A3D47) so white reads on day sky


def _key_dot(surf, p, r):
    """Stamp a 1px keyline rim just outside a white bone tip so it never sits
    directly on bright sky — the outline pass adds a near-black edge, this adds
    the cooler #3A3D47 the critique calls for."""
    pygame.draw.circle(surf, _KEY, p, r + 1, 1)


def _finger_wing(angle_deg):
    """Wing as radiating finger-bones (phalanges) fanning from a bone wrist.
    No solid membrane — the dark is only thin negative space BETWEEN the white
    bones, so the wing reads skeletal (not a cape blob) and the flap clatters
    those bones across all 4 poses. Each phalange is keyline-rimmed so it holds
    against the day sky even between the fingers."""
    w = pygame.Surface((52, 52), pygame.SRCALPHA)
    wrist = (24, 30)

    # Splayed phalange tips — a long leading finger fanning down to a short
    # trailing one. Kept as discrete bones with dark gaps, never a filled field.
    tips = [(49, 16), (50, 26), (45, 36), (37, 43), (28, 44)]
    for tip in tips:
        # Keyline underlay (drawn fatter first) so a #3A3D47 rim hugs each bone.
        pygame.draw.line(w, _KEY, wrist, tip, 4)
        _key_dot(w, tip, 2)
    pygame.draw.circle(w, _KEY, wrist, 4)              # wrist keyline

    for i, tip in enumerate(tips):
        col = _BONE if i < 3 else _BONE_SH
        pygame.draw.line(w, col, wrist, tip, 2)        # the bone itself
        pygame.draw.circle(w, _BONE, tip, 2)           # knuckle cap
        # A mid-bone joint pip on the longer fingers for the segmented look.
        if i < 3:
            mid = ((wrist[0] + tip[0]) // 2, (wrist[1] + tip[1]) // 2)
            pygame.draw.circle(w, _BONE_SH, mid, 1)
    pygame.draw.circle(w, _BONE, wrist, 3)             # wrist knob
    pygame.draw.circle(w, _BODY_D, wrist, 1)
    return pygame.transform.rotate(w, angle_deg)


def _vertebra(surf, p0, p1, beads):
    """A short bead column from p0 to p1 — the spine tell. Keyline-rimmed so
    the centerline reads even where it crosses the dark body."""
    for i in range(beads):
        t = i / (beads - 1)
        x = int(p0[0] + (p1[0] - p0[0]) * t)
        y = int(p0[1] + (p1[1] - p0[1]) * t)
        pygame.draw.circle(surf, _KEY, (x, y), 2, 1)
        pygame.draw.circle(surf, _BONE, (x, y), 2)
        pygame.draw.circle(surf, _BONE_SH, (x, y), 2, 1)


def _build_design1(wing_angle_deg):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)

    # Tail + body + head as near-black masses (the value floor the bone sits on).
    # The tail is ribbed with white tail-feather bones so the dark fan never
    # reads as a solid cape — no near-black field wider than ~6px is left bare.
    tail = [(2, 26), (17, 24), (23, 36), (12, 42)]
    _poly(surf, _BODY, tail)
    pygame.draw.polygon(surf, _BODY_D, tail, 1)
    for (a, b) in (((19, 27), (4, 29)), ((20, 31), (5, 34)), ((20, 35), (9, 40))):
        pygame.draw.line(surf, _KEY,  a, b, 3)                  # feather-bone keyline
        pygame.draw.line(surf, _BONE, a, b, 1)                  # white tail-feather bone
    _aaellipse(surf, _BODY_D, (33, 33), 19, 14)
    _aaellipse(surf, _BODY, (32, 32), 18, 13)
    _aaellipse(surf, _BODY_D, (48, 21), 13, 12)
    _aaellipse(surf, _BODY, (47, 20), 12, 11)

    # Spine — vertebra beads from the skull base down toward the ribcage.
    _vertebra(surf, (42, 26), (22, 38), 6)

    # Ribcage — a bold ladder of PAIRED white rib-arcs off a central sternum,
    # keyline-rimmed underneath so the arcs survive on bright sky.
    pygame.draw.line(surf, _KEY,  (38, 24), (24, 40), 4)        # sternum keyline
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
    surf.blit(wing, wing.get_rect(center=(33, 28)).topleft)

    # Leg bones — thin paired bones with knob knees + 3-claw bone feet, each
    # keyline-rimmed so the tips read against the ground.
    for hx, fx in ((28, 27), (34, 35)):
        knee = (hx, 45)
        foot = (fx, 49)
        pygame.draw.line(surf, _KEY,  (hx, 40), knee, 4)        # thigh keyline
        pygame.draw.line(surf, _KEY,  knee, foot, 4)            # shin keyline
        pygame.draw.line(surf, _BONE, (hx, 41), knee, 2)        # thigh
        pygame.draw.circle(surf, _BONE, knee, 2)                # knob knee
        pygame.draw.line(surf, _BONE, knee, foot, 2)            # shin
        for dx in (-2, 0, 2):
            pygame.draw.line(surf, _BONE_SH, foot, (foot[0] + dx, foot[1] + 3), 2)

    # ── Skull — bright white cranium tall enough to seat two DISTINCT sockets
    # with a solid white nasal bridge between and a white crown above them.
    # Keyline first (a hair larger) so the white dome never touches the sky.
    _aaellipse(surf, _KEY,     (47, 19), 11, 10)
    _aaellipse(surf, _BONE,    (47, 19), 10, 9)                 # cranium
    _aaellipse(surf, _BONE_SH, (47, 23), 9, 5)                 # under-edge shade
    _aaellipse(surf, _BONE,    (47, 22), 8, 5)                 # jaw/muzzle front

    # Two big hollow eye sockets — distinct ~4px PURE near-black teardrop holes
    # with a ≥2px white nasal bridge between (x 44↔51 leaves white at x 47-48)
    # and ≥2px white cranium above (sockets sit at y 20, crown top at y ~10).
    for ex in (43, 51):
        # Teardrop: a round top tapering to a point toward the nose centre.
        nose_dir = 1 if ex < 47 else -1
        pts = [(ex - 2, 19), (ex + 2, 19), (ex + 2, 21),
               (ex + nose_dir * 1, 24), (ex - 2, 21)]
        _poly(surf, _BODY_D, pts)
        pygame.draw.circle(surf, _BODY_D, (ex, 20), 2)
        pygame.draw.circle(surf, _KEY,    (ex, 20), 2, 1)      # faint socket rim
    pygame.draw.circle(surf, (255, 255, 255), (52, 18), 1)     # life glint

    # Small triangular nose hollow, centred on the bridge below the sockets.
    _poly(surf, _BODY_D, [(46, 25), (48, 25), (47, 28)])

    # Tooth grin — a committed 2px WHITE tooth bar with two dark notches.
    pygame.draw.line(surf, _BONE, (43, 28), (51, 28), 2)       # tooth bar
    for nx in (46, 49):
        pygame.draw.line(surf, _BODY_D, (nx, 27), (nx, 30), 1) # notch gaps

    # Beak — near-black beak with a crisp white bone outline.
    beak_pts = [(55, 22), (61, 25), (58, 29), (52, 27)]
    _poly(surf, _BODY, beak_pts)
    pygame.draw.polygon(surf, _KEY, beak_pts, 2)
    pygame.draw.polygon(surf, _BONE, beak_pts, 1)

    return surf


build = _make_prebuilt_skin(_build_design1)
