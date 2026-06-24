"""DEADMAN'S FLAG — skeleton costume design_4 (scratch exploration).

Concept #4 from docs/store_redesign/costume/skeleton/concepts.md: a
swashbuckling pirate skeleton. Bone is the bright value anchor (#F4EFE0);
the strong themed layer is pirate GEAR — a red bandana with a knot-tail past
the crown, a black eyepatch over one socket, a gold hoop earring, a crossed-
bone Jolly-Roger motif, and a steel cutlass slung diagonally across the back.

Full bone redraw (not a paint overlay): every bone is redrawn so the bird
reads as a skeleton + pirate at 40px. Wrapped with
``store_skins._make_prebuilt_skin`` so the 4 flap poses + outline come for
free. NEVER registered in BUILDERS — exploration only.
"""
import math
import pygame

from game import store_skins
from game.store_skins import SPRITE_W, SPRITE_H, _poly
from game.parrot import _aaellipse


# Bone is the brightest base so the skeleton read never depends on the gear.
_BONE   = (244, 239, 224)        # #F4EFE0 warm white — value anchor
_BONE_D = (196, 188, 166)        # under-edge for roundness
_BONE_DD = (150, 142, 122)       # deepest bone shade / socket inner rim
_RED    = (200, 32, 43)          # #C8202B bandana / cloth (THEME)
_RED_D  = (150, 22, 32)
_RED_H  = (236, 92, 96)          # bandana sheen
_BLACK  = (26, 20, 16)           # #1A1410 body + eyepatch
_BLACK_H = (54, 46, 40)          # faint rim so black reads on day sky
_GOLD   = (232, 178, 58)         # #E8B23A earring + crossguard
_GOLD_H = (255, 224, 140)
_STEEL  = (185, 192, 201)        # #B9C0C9 blade
_STEEL_H = (228, 233, 238)
_STEEL_D = (120, 128, 138)


def _cutlass(surf):
    """Cutlass slung diagonally across the back — butt low past the tail,
    curved blade tip high past the back shoulder into open sky. Drawn FIRST
    (behind the body) so it reads as slung, breaking the silhouette."""
    # Hilt low-left near the tail/hip; blade sweeps up to the right shoulder.
    grip_lo = (10, 44)
    guard   = (18, 36)
    # Steel grip from butt to crossguard.
    pygame.draw.line(surf, _STEEL_D, grip_lo, guard, 5)
    pygame.draw.line(surf, _STEEL, grip_lo, guard, 3)
    pygame.draw.line(surf, _STEEL_H, (grip_lo[0], grip_lo[1] - 1),
                     (guard[0], guard[1] - 1), 1)
    # Pommel knob.
    pygame.draw.circle(surf, _GOLD, grip_lo, 3)
    pygame.draw.circle(surf, _GOLD_H, (grip_lo[0] - 1, grip_lo[1] - 1), 1)

    # Gold crossguard — a short bar across the blade base.
    gx, gy = guard
    pygame.draw.line(surf, _GOLD, (gx - 5, gy + 4), (gx + 5, gy - 4), 4)
    pygame.draw.line(surf, _GOLD_H, (gx - 4, gy + 3), (gx + 4, gy - 3), 1)

    # Curved steel blade — a fat crescent sweeping up past the back shoulder.
    # Built as a filled poly (outer + inner curve) so the cutlass curve reads.
    outer = []
    inner = []
    bx, by = gx + 3, gy - 4          # blade root just past the guard
    tipx, tipy = 40, 6               # tip high into open sky past the shoulder
    for t in (0.0, 0.22, 0.44, 0.66, 0.85, 1.0):
        # Quadratic-ish sweep with a belly bowing toward the back-top.
        mx = bx + (tipx - bx) * t
        my = by + (tipy - by) * t
        bow = math.sin(t * math.pi) * 6.0     # curvature of the cutlass belly
        nx, ny = -(tipy - by), (tipx - bx)
        nl = math.hypot(nx, ny) or 1.0
        nx, ny = nx / nl, ny / nl
        width = 4.0 * (1.0 - t * 0.5)          # tapers toward the point
        cx = mx + nx * bow
        cy = my + ny * bow
        outer.append((cx + nx * width, cy + ny * width))
        inner.append((cx - nx * width, cy - ny * width))
    blade_poly = outer + inner[::-1]
    _poly(surf, _STEEL_D, blade_poly)
    # Bright edge highlight along the cutting (outer) curve.
    pygame.draw.lines(surf, _STEEL, False, outer, 2)
    pygame.draw.lines(surf, _STEEL_H, False, outer[1:-1], 1)
    # Sharp white glint at the very tip.
    pygame.draw.circle(surf, (255, 255, 255), (tipx, tipy), 1)


def _wing(angle_deg):
    """Skeletal pirate wing: radiating finger-bones from a bone wrist, the
    wrist wrapped in a scrap of red bandana cloth so the wing reads pirate."""
    w = pygame.Surface((50, 50), pygame.SRCALPHA)
    wrist = (24, 27)
    # Three radiating phalanges (finger-bones) — 2px min so they survive 40px.
    tips = [(46, 14), (49, 24), (43, 38)]
    for tx, ty in tips:
        pygame.draw.line(w, _BONE_D, (wrist[0], wrist[1] + 1),
                         (tx, ty + 1), 3)
        pygame.draw.line(w, _BONE, wrist, (tx, ty), 2)
        pygame.draw.circle(w, _BONE, (tx, ty), 2)         # knuckle knob
        pygame.draw.circle(w, _BONE_D, (tx, ty), 2, 1)
    # Carpal/wrist knob.
    pygame.draw.circle(w, _BONE, wrist, 3)
    pygame.draw.circle(w, _BONE_D, wrist, 3, 1)
    # Scrap of red bandana cloth wrapped at the wrist (the pirate tell).
    cloth = [(20, 24), (28, 23), (30, 29), (22, 31)]
    _poly(w, _RED, cloth)
    _poly(w, _RED_D, [(20, 24), (22, 31), (24, 27)])
    pygame.draw.line(w, _RED_H, (21, 25), (29, 24), 1)
    # A short cloth tail flicking off the wrist.
    _poly(w, _RED, [(20, 28), (15, 33), (18, 34), (22, 30)])
    return pygame.transform.rotate(w, angle_deg)


def _build_design4(wing_angle_deg):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)

    # 1) Cutlass slung across the back — behind everything.
    _cutlass(surf)

    # 2) Tail — black bone-flesh fan.
    _poly(surf, _BLACK, [(2, 26), (17, 24), (23, 36), (12, 42)])
    _poly(surf, _BLACK_H, [(2, 26), (17, 24), (20, 30)])

    # 3) Body — near-black "flesh" so bright bone reads on top.
    _aaellipse(surf, _BLACK, (33, 33), 19, 14)
    _aaellipse(surf, _BLACK, (32, 32), 18, 13)
    _aaellipse(surf, _BLACK_H, (28, 28), 9, 5)            # faint top sheen

    # 4) Spine — vertebra-bead column from skull base down into the ribcage.
    spine = [(40, 24), (37, 28), (33, 32), (29, 36), (25, 39)]
    for i in range(len(spine) - 1):
        pygame.draw.line(surf, _BONE_D, spine[i], spine[i + 1], 3)
    for vx, vy in spine:
        pygame.draw.circle(surf, _BONE, (vx, vy), 2)

    # 5) Ribcage — bright paired bone arcs sweeping off the spine.
    for off, span in ((-2, 14), (3, 16), (8, 17)):
        rx, ry = 22 + off, 25
        pygame.draw.arc(surf, _BONE_D, (rx, ry + 1, span, 18),
                        math.radians(198), math.radians(342), 3)
        pygame.draw.arc(surf, _BONE, (rx, ry, span, 17),
                        math.radians(198), math.radians(342), 2)

    # 6) Crossed-bone Jolly-Roger motif on the chest, below the sternum.
    def _xbone(ax, ay, bx, by):
        pygame.draw.line(surf, _BONE_D, (ax, ay + 1), (bx, by + 1), 3)
        pygame.draw.line(surf, _BONE, (ax, ay), (bx, by), 2)
        for ex, ey in ((ax, ay), (bx, by)):
            pygame.draw.circle(surf, _BONE, (ex, ey), 2)
    _xbone(24, 38, 32, 44)
    _xbone(24, 44, 32, 38)

    # 7) Wing — skeletal phalanges + bandana-cloth wrist.
    wing = _wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    # 8) Skull dome — bright ivory at the head anchor.
    _aaellipse(surf, _BONE_D, (47, 22), 12, 11)
    _aaellipse(surf, _BONE, (47, 21), 11, 10)
    # Cheekbone / jaw shelf for skull roundness.
    _aaellipse(surf, _BONE_D, (47, 26), 8, 4)

    # 9) Hollow socket (the eye WITHOUT the patch) — deep black hole + rim.
    pygame.draw.circle(surf, _BONE_DD, (44, 20), 4)
    pygame.draw.circle(surf, _BLACK, (44, 20), 3)
    pygame.draw.circle(surf, (8, 6, 5), (44, 20), 2)

    # Nose hollow + bone grin (tooth gaps) so the skull face reads.
    _poly(surf, _BLACK, [(47, 24), (49, 24), (48, 26)])
    pygame.draw.line(surf, _BONE_D, (43, 28), (52, 28), 2)   # grin line
    for gx in (44, 47, 50):
        pygame.draw.line(surf, _BONE_DD, (gx, 27), (gx, 30), 1)

    # 10) Beak — bone-outlined over a black beak.
    beak = [(55, 21), (61, 24), (58, 28), (52, 26)]
    _poly(surf, _BLACK, beak)
    pygame.draw.polygon(surf, _BONE, beak, 2)

    # 11) Gold hoop earring at the jaw.
    pygame.draw.circle(surf, _GOLD, (43, 30), 3, 2)
    pygame.draw.circle(surf, _GOLD_H, (42, 29), 1)

    # 12) Red bandana wrapping the cranium + knot-tail past the crown (tell #1).
    # Wrap band across the top of the skull.
    band = [(36, 17), (58, 17), (57, 11), (38, 11)]
    _poly(surf, _RED, band)
    _poly(surf, _RED_D, [(36, 17), (58, 17), (58, 15), (36, 15)])
    pygame.draw.line(surf, _RED_H, (38, 13), (56, 13), 2)
    # Tiny polka dots on the bandana for the pirate-cloth read.
    for dx in (41, 47, 53):
        pygame.draw.circle(surf, _BONE, (dx, 13), 1)
    # Knot at the back-left of the crown.
    _poly(surf, _RED, [(34, 12), (40, 10), (41, 16), (35, 18)])
    _poly(surf, _RED_D, [(34, 12), (35, 18), (37, 14)])
    # Two knot-tails flicking up/back past the crown — breaks the outline.
    _poly(surf, _RED, [(35, 13), (28, 6), (32, 5), (38, 11)])
    _poly(surf, _RED_D, [(35, 13), (32, 5), (34, 9)])
    _poly(surf, _RED, [(34, 15), (26, 13), (28, 9), (37, 13)])
    pygame.draw.line(surf, _RED_H, (33, 7), (29, 5), 1)

    # 13) Black eyepatch + strap over the OTHER socket (tell, near eye).
    # Strap runs from under the bandana across to the jaw.
    pygame.draw.line(surf, _BLACK, (50, 15), (54, 27), 3)
    pygame.draw.line(surf, _BLACK_H, (50, 15), (54, 27), 1)
    # Patch — a rounded black lens over the near socket.
    _aaellipse(surf, _BLACK, (51, 20), 4, 4)
    _aaellipse(surf, _BLACK_H, (50, 18), 2, 1)              # tiny patch sheen

    # 14) Legs — bone leg-pair; one foot is a peg-leg stub for character.
    # Normal bone leg (front).
    pygame.draw.line(surf, _BONE_D, (35, 45), (36, 50), 3)
    pygame.draw.line(surf, _BONE, (35, 45), (36, 50), 2)
    pygame.draw.circle(surf, _BONE, (35, 45), 2)           # knee knob
    # Three bone claw-toes.
    for tx in (33, 36, 39):
        pygame.draw.line(surf, _BONE, (36, 50), (tx, 53), 1)
    # Peg-leg stub (back leg) — a short tapered bone peg, no foot.
    _poly(surf, _BONE_D, [(27, 44), (31, 44), (30, 52), (28, 52)])
    _poly(surf, _BONE, [(27, 44), (30, 44), (29, 51), (28, 51)])
    pygame.draw.line(surf, _BONE_DD, (28, 46), (28, 50), 1)
    # A red cloth wrap where the peg meets the bone (pirate detail).
    pygame.draw.line(surf, _RED, (27, 45), (31, 45), 2)

    return surf


build = store_skins._make_prebuilt_skin(_build_design4)
