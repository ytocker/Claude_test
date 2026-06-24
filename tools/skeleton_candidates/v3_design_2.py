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


def _paint(surf, wing_angle_deg):
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

    # ── Full vertebral column — dense beads skull-base → tail root, one chain.
    spine = [(42, 45), (38, 47), (34, 49), (30, 51), (26, 52),
             (22, 53), (19, 54)]
    pygame.draw.lines(surf, _KEY, False, spine, 4)
    pygame.draw.lines(surf, _BONE, False, spine, 1)
    for vx, vy in spine:
        pygame.draw.circle(surf, _KEY,  (vx, vy), 2)
        pygame.draw.circle(surf, _BONE, (vx, vy), 1)

    # ── Full ribcage — sternum + five paired ribs wrapping chest→belly, with
    #    dark gaps between (this density is the X-RAY identity). Ribs spring off
    #    the spine and curve down/forward to the sternum.
    pygame.draw.line(surf, _KEY,  (39, 46), (29, 62), 4)     # sternum keel
    pygame.draw.line(surf, _BONE, (39, 46), (29, 62), 2)
    for i, ty in enumerate((48, 51, 54, 57, 60)):
        sx = 37 - i * 2                                      # rib root on spine
        ex = 30 - i                                          # rib foot on keel
        rib = [(sx, ty - 1), (sx - 5, ty + 2), (ex, ty + 5)]
        pygame.draw.lines(surf, _KEY,  False, rib, 3)
        pygame.draw.lines(surf, _BONE, False, rib, 1)

    # ── Wing phalanges — a finger-bone fan off the wrist. The base wing already
    #    carries flapping bone dividers; these add the hand bones at the wrist so
    #    the wing reads skeletal at the leading edge across the flap range.
    wrist = (31, 47)
    pygame.draw.circle(surf, _BONE, wrist, 2)
    pygame.draw.circle(surf, _KEY,  wrist, 2, 1)
    for tip in ((45, 42), (48, 48), (43, 55)):
        pygame.draw.line(surf, _KEY,  wrist, tip, 3)
        pygame.draw.line(surf, _BONE, wrist, tip, 1)
        pygame.draw.circle(surf, _BONE, tip, 1)

    # ── Tail-feather bones fanning across the ORIGINAL tail fan (x2–23/y44–62).
    for (x0, y0), (x1, y1) in (((19, 49), (4, 49)), ((20, 53), (3, 56)),
                               ((18, 56), (6, 61))):
        pygame.draw.line(surf, _KEY,  (x0, y0), (x1, y1), 3)
        pygame.draw.line(surf, _BONE, (x0, y0), (x1, y1), 1)
        pygame.draw.circle(surf, _BONE, (x1, y1), 1)

    # ── Legs — full bones: knob knees + 2-claw bone feet on the original lines.
    for kx, fx in ((28, 26), (34, 36)):
        pygame.draw.line(surf, _KEY,  (kx, 62), (kx, 68), 3)   # shin bone
        pygame.draw.line(surf, _BONE, (kx, 62), (kx, 68), 1)
        pygame.draw.circle(surf, _BONE, (kx, 62), 2)           # knob knee
        pygame.draw.circle(surf, _KEY,  (kx, 62), 2, 1)
        for dx in (-2, 0, 2):                                  # 3 bone claws
            pygame.draw.line(surf, _BONE, (fx, 69), (fx + dx, 72), 1)


build = store_skins._make_skin(_paint, base_fn=_bone_parrot_xray)
