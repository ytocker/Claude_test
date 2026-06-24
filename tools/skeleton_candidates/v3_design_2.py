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
from game.dollar_parrot_ghost import (
    _aaellipse as _aae, SPRITE_W, SPRITE_H, _build_parrot_with_palette)
from tools.skeleton_candidates._v3_bone_base import P_BONE

_BONE    = (255, 255, 255)
_BONE_SH = (214, 219, 230)
_KEY     = (58, 61, 71)
_VOID    = (10, 11, 16)


# ── per-design bone wing palette ─────────────────────────────────────────────
# Copy the shared bone palette, then drop the WHOLE wing membrane to deep void.
# At 40px three bright divider lines averaged to a gray motion-blur fan, so the
# bone read now comes from ONE strut painted by the design's own wing builder
# (`_xray_wing`): leading edge + first divider full white, the other dividers
# void. One crisp white strut flapping reads as bone; three gray ones read blur.
_P = dict(P_BONE)
_P['wing_main']      = (16, 18, 24)
_P['wing_dark']      = (12, 13, 18)      # underside triangle → void
_P['wing_tip']      = (20, 22, 28)
_P['wing_secondary'] = None
_P['wing_highlight'] = None              # leading line painted by _xray_wing
P_BONE_XRAY = _P


def _xray_wing(angle_deg):
    """The base wing membrane (dark) with ONE bright bone strut: a 2px white
    leading edge fused to the first divider, the other two dividers dropped to
    void so they vanish at the downscale instead of blurring to gray. Rotated
    around the same shoulder anchor as the base wing so it flaps in register."""
    w = pygame.Surface((50, 50), pygame.SRCALPHA)
    pygame.draw.polygon(w, (0, 0, 0, 120),
                        [(24, 26), (46, 14), (50, 30), (34, 44), (18, 40)])
    pygame.draw.polygon(w, _P['wing_main'],
                        [(24, 24), (44, 13), (48, 28), (32, 42), (18, 36)])
    pygame.draw.polygon(w, _P['wing_dark'],
                        [(24, 24), (32, 42), (18, 36)])
    pygame.draw.polygon(w, _P['wing_tip'], [(44, 13), (50, 18), (48, 28)])
    # The two trailing dividers go to deep void — black gaps, not gray lines.
    pygame.draw.line(w, _VOID, (28, 30), (44, 25), 2)
    pygame.draw.line(w, _VOID, (30, 34), (46, 32), 2)
    # ONE bone strut: the leading edge and first divider fused into a single
    # crisp white bar with a cool keyline beneath so it can't bleed gray.
    pygame.draw.line(w, _KEY,  (26, 26), (42, 19), 1)
    pygame.draw.line(w, _BONE, (25, 24), (42, 16), 3)
    pygame.draw.circle(w, _BONE, (43, 15), 2)             # wrist knob on the strut
    return pygame.transform.rotate(w, angle_deg)


def _bone_parrot_xray(angle_deg):
    """Rebuild of `_build_parrot_with_palette` (same draw order/proportions) but
    swapping in `_xray_wing` so the single bone strut flaps in register."""
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
    P = P_BONE_XRAY
    for i, c in enumerate(P['tail']):
        pygame.draw.polygon(surf, c, [
            (2 + i * 3, 26 + i * 2), (14 + i, 24 + i),
            (20 + i, 30 + i * 2), (6 + i * 3, 36 + i * 2)])
    pygame.draw.line(surf, P['tail_line'], (4, 27), (18, 31), 1)
    pygame.draw.line(surf, P['tail_line'], (6, 33), (20, 35), 1)
    _aae(surf, P['body_shadow'], (34, 35), 19, 14)
    _aae(surf, P['body_main'],   (32, 32), 19, 14)
    _aae(surf, P['body_chest'],  (30, 29), 13,  8)
    _aae(surf, P['body_belly'],  (28, 38), 12,  6)
    wing = _xray_wing(angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)
    _aae(surf, P['head_shadow'], (48, 23), 12, 11)
    _aae(surf, P['head_main'],   (47, 21), 12, 11)
    _aae(surf, P['head_cheek'],  (44, 24),  4,  3)
    _aae(surf, P['head_crown'],  (46, 16),  7,  3)
    beak_pts = [(55, 21), (61, 24), (58, 28), (52, 26)]
    pygame.draw.polygon(surf, P['beak_main'], beak_pts)
    pygame.draw.polygon(surf, P['beak_dark'], beak_pts, 1)
    pygame.draw.line(surf, P['beak_gloss'], (55, 22), (59, 24), 1)
    pygame.draw.line(surf, P['beak_dark'],  (52, 24), (58, 25), 1)
    pygame.draw.line(surf, P['foot'], (28, 45), (26, 49), 2)
    pygame.draw.line(surf, P['foot'], (34, 45), (36, 49), 2)
    return surf


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

    # ── Ribcage — sternum keel + 4 FAT 3px white ribs over the void wash, with
    #    WIDE black gaps so each rib survives the 40px downscale instead of
    #    averaging to a smear. Roots tight to the spine, feet to the keel, so the
    #    set curves as a CAGE rather than parallel slashes. A 1px _BONE_SH keyline
    #    rims the keel's outer edge so the day torso has a bright silhouette edge.
    pygame.draw.line(surf, _BONE_SH, (40, 46), (31, 60), 1)  # keel rim (day edge)
    _kbone(surf, (39, 46), (30, 60), 3)                      # sternum keel
    rib_spine = ((37, 48), (36, 51), (35, 55), (34, 59))     # roots hug the spine
    rib_keel  = ((30, 50), (29, 54), (29, 58), (30, 62))     # feet meet the keel
    for (sx, sy), (ex, ey) in zip(rib_spine, rib_keel):
        _kbone(surf, (sx, sy), (ex, ey), 3, key_side=-1)

    # ── Wing root — only a shoulder knob + short humerus stub on the spine. The
    #    flapping bone strut now lives in `_xray_wing` (so it rotates in register
    #    across f0–f3); a static finger-fan painted here would re-create the gray
    #    multi-line blur the critique flagged, so it is deliberately omitted.
    shoulder = (37, 47)
    pygame.draw.circle(surf, _BONE, shoulder, 2)             # shoulder knob
    pygame.draw.circle(surf, _KEY,  shoulder, 2, 1)
    _kbone(surf, shoulder, (34, 46), 2)                      # humerus stub to wing

    # ── Tail-feather bones across the ORIGINAL tail fan (x2–23/y44–62) — bumped
    #    to 3px white (one a bright leader) so the original tail still reads
    #    skeletal at 40px day instead of vanishing into the dark fan.
    for (x0, y0), (x1, y1), wpx in (((19, 49), (4, 49), 3),
                                    ((20, 53), (3, 56), 3),
                                    ((18, 56), (6, 61), 3)):
        _kbone(surf, (x0, y0), (x1, y1), wpx)
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
