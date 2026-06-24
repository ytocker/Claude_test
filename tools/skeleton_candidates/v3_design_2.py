"""v3_design_2 · X-RAY — a faithful skeleton of the ORIGINAL Pip macaw, full.

Same faithful base as the CLEAN take (`_bone_parrot` = the recoloured original
parrot, so silhouette + ORIGINAL beak + ORIGINAL tail location are exact), but the
paint shows the FULL anatomy "through" the dark flesh: a white cranium + hollow
socket, a complete vertebral column, a full ribcage (every rib), wing phalanges
fanning along the wing, leg bones with knees + claw feet, and tail-feather bones
across the original tail fan. Denser than CLEAN — must still pass the 40px read,
white bone staying the brightest element.

WHY the wing uses a per-design palette copy: the base wing FLAPS across 4 frames,
so a statically-painted wing-bone drifts off the rotating wing. Re-toning the
wing's OWN feather-divider lines (`wing_highlight`/`wing_dark`) to bone makes the
base wing draw its bone-lines and rotate them correctly with the flap — the
painted phalanges then only have to read at the wrist, not carry the whole wing.

Paint is in COMPOSITE space (original sprite coords + PARROT_DY=20). Scratch only
— never registered in BUILDERS.
"""
import math
import pygame

from game import store_skins
from game.parrot import _aaellipse
from game.dollar_parrot_ghost import _build_parrot_with_palette
from tools.skeleton_candidates._v3_bone_base import P_BONE

_BONE    = (255, 255, 255)
_BONE_SH = (214, 219, 230)
_KEY     = (58, 61, 71)
_VOID    = (10, 11, 16)


# ── per-design bone wing palette ─────────────────────────────────────────────
# Copy the shared bone palette, then re-tone the wing so the base wing's own
# internal lines render as BONE and flap correctly. The divider lines become
# bright bone (wing_highlight carries one crisp top line; wing_dark carries the
# rib-like dividers), and a deep void underside keeps dark gaps between them so
# the wing doesn't smear to a white blob at 40px.
_P = dict(P_BONE)
_P['wing_main']      = (22, 24, 30)
_P['wing_dark']      = (228, 232, 240)   # divider lines → bone
_P['wing_tip']      = (30, 33, 41)
_P['wing_secondary'] = (10, 11, 16)      # dark void wedge between bones
_P['wing_highlight'] = (255, 255, 255)   # crisp leading bone line
P_BONE_XRAY = _P


def _bone_parrot_xray(angle_deg):
    return _build_parrot_with_palette(angle_deg, P_BONE_XRAY, draw_lenses=False)


def _kbone(surf, p0, p1, w=2, *, key_side=1):
    """One bone stroke: a w-px white CORE with a 1px _KEY keyline on ONE side.
    White core ≥ key so the bone wins the 40px downscale instead of averaging
    to mid-gray. key_side offsets the keyline perpendicular to the bone by 1px."""
    x0, y0 = p0
    x1, y1 = p1
    dx, dy = x1 - x0, y1 - y0
    d = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / d * key_side, dx / d * key_side               # unit normal
    pygame.draw.line(surf, _KEY, (x0 + nx, y0 + ny), (x1 + nx, y1 + ny), 1)
    pygame.draw.line(surf, _BONE, p0, p1, w)


def _paint(surf, wing_angle_deg):
    # ── VOID wash — paint the ribcage footprint near-black FIRST so the spaces
    #    between ribs read as true void, not mid-gray flesh. White-on-black is
    #    the only contrast that survives the 40px downscale.
    void_torso = [(38, 45), (40, 53), (33, 64), (24, 64), (20, 56), (24, 47)]
    pygame.draw.polygon(surf, _VOID, void_torso)

    # ── Skull — white cranium + a clean HOLLOW eye-socket (head centre 47,41).
    #    Cranium first as a keyed white dome, then carve the socket as a dark
    #    ring so it reads as a socket, not a painted dot.
    _aaellipse(surf, _KEY,     (47, 39), 12, 11)
    _aaellipse(surf, _BONE,    (47, 39), 11, 10)
    _aaellipse(surf, _BONE_SH, (45, 43), 7, 4)
    # Cranial suture hint across the crown.
    pygame.draw.line(surf, _KEY, (40, 33), (52, 32), 1)
    # Hollow eye-socket: bright bone rim, deep void centre.
    pygame.draw.circle(surf, _BONE, (50, 40), 5)
    pygame.draw.circle(surf, _KEY,  (50, 40), 5, 1)
    pygame.draw.circle(surf, _VOID, (50, 40), 3)
    pygame.draw.circle(surf, (60, 64, 76), (51, 39), 1)      # socket depth glint
    # Nostril + a mandible line so the ORIGINAL beak reads skeletal.
    pygame.draw.circle(surf, _VOID, (54, 43), 1)             # nostril
    pygame.draw.line(surf, _KEY, (52, 46), (59, 47), 1)      # mandible seam
    pygame.draw.line(surf, _BONE_SH, (52, 45), (58, 46), 1)  # upper-bill ridge

    # ── Vertebral column — beads skull-base → tail root, LIFTED to horizontal so
    #    Pip reads as a flyer, not a standing dinosaur (was drooping to y54).
    spine = [(42, 45), (38, 46), (34, 47), (30, 48), (26, 49),
             (22, 50), (19, 51)]
    for vx, vy in spine:
        _kbone(surf, (vx, vy), (vx, vy), 2)                  # white core beads
    for i in range(len(spine) - 1):                          # 2px white linkage
        pygame.draw.line(surf, _BONE, spine[i], spine[i + 1], 2)

    # ── Ribcage — sternum keel + ~4 STRONG ribs at 2px white each over the void
    #    wash, so the gaps stay black and every rib resolves discretely at 40px.
    #    Clearly denser than the CLEAN sibling, but never a filled paddle.
    _kbone(surf, (39, 46), (30, 60), 2)                      # sternum keel
    for ty in (50, 53, 56, 60):
        sx, sy = 36 - (ty - 50) // 2, ty - 4                 # rib root near spine
        ex, ey = 30 - (ty - 50) // 3, ty                     # rib foot on keel
        _kbone(surf, (sx, sy), (ex, ey), 2, key_side=-1)

    # ── Wing bones — anchor the floating phalanges with a bright HUMERUS from a
    #    shoulder knob on the spine out to the wrist, THEN fan the finger sticks
    #    off the wrist. Connected bones read as a wing, not 3 motion-blur lines.
    shoulder = (37, 47)
    wrist = (31, 47)
    pygame.draw.circle(surf, _BONE, shoulder, 2)             # shoulder knob
    pygame.draw.circle(surf, _KEY,  shoulder, 2, 1)
    _kbone(surf, shoulder, wrist, 2)                         # humerus
    pygame.draw.circle(surf, _BONE, wrist, 2)
    pygame.draw.circle(surf, _KEY,  wrist, 2, 1)
    for tip in ((45, 42), (48, 48), (43, 55)):
        _kbone(surf, wrist, tip, 2)
        pygame.draw.circle(surf, _BONE, tip, 1)

    # ── Tail-feather bones fanning across the ORIGINAL tail fan (x2–23/y44–62).
    for (x0, y0), (x1, y1) in (((19, 49), (4, 49)), ((20, 53), (3, 56)),
                               ((18, 56), (6, 61))):
        _kbone(surf, (x0, y0), (x1, y1), 2)
        pygame.draw.circle(surf, _BONE, (x1, y1), 1)

    # ── Legs — TUCKED up + forward under the body (a flyer's posture), not the
    #    straight-down vertical shins that read as a standing biped. Femur back
    #    from the hip to a raised knee, short shin forward to a clawed foot.
    for hip, knee, foot in (((30, 56), (28, 60), (30, 66)),
                            ((34, 57), (35, 61), (38, 66))):
        _kbone(surf, hip, knee, 2)                           # femur
        _kbone(surf, knee, foot, 2)                          # shin, angled fwd
        pygame.draw.circle(surf, _BONE, knee, 2)             # knob knee
        pygame.draw.circle(surf, _KEY,  knee, 2, 1)
        fx, fy = foot
        for dx in (-2, 0, 2):                                # 3 bone claws
            pygame.draw.line(surf, _BONE, foot, (fx + dx, fy + 3), 1)


build = store_skins._make_skin(_paint, base_fn=_bone_parrot_xray)
