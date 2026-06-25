"""DEADMAN'S FLAG — skeleton costume design_4 (scratch exploration).

Concept #4 from docs/store_redesign/costume/skeleton/concepts.md: a
swashbuckling pirate skeleton. Bone is the bright value anchor (#F4EFE0);
the strong themed layer is pirate GEAR — a red bandana wrapping the cranium
with a short knot-tail flicked UP-and-FORWARD past the crown, a black eyepatch
over one socket, a hollow bone socket for the other, a gold hoop earring, a
dark-on-bone ribcage + crossbones motif, and a thin steel cutlass crossing
OUTSIDE the back silhouette.

Round-2 priorities (art-director ITERATE): the skull is the brightest,
forward-most mass with a 2px dark keyline so it separates from sky AND body;
ONE crisp hollow socket vs. a clearly-different oval eyepatch (two distinct
dark shapes, never one blob); the cutlass is a thin steel diagonal breaking
the outline (no dark back-blob); chunky DARK rib-arcs + an X crossbones laid
ON the bright chest so they survive at 40px.

Full bone redraw (not a paint overlay): wrapped with
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
_KEY    = (40, 30, 24)           # dark keyline around the skull (day-sky anchor)
_RIB    = (96, 80, 64)           # dark-on-bone rib/crossbone arcs (survive at 40px)
_GOLD   = (232, 178, 58)         # #E8B23A earring + crossguard
_GOLD_H = (255, 224, 140)
_STEEL  = (185, 192, 201)        # #B9C0C9 blade
_STEEL_H = (228, 233, 238)
_STEEL_D = (120, 128, 138)


def _cutlass(surf):
    """A thin steel cutlass crossing OUTSIDE the back silhouette — a clear
    recognizable blade (not a back-blob): straight steel diagonal with a gold
    crossguard nub low-near-the-tail and a curved tip that breaks the outline
    high past the back shoulder. Drawn FIRST so the body overlaps its middle,
    selling 'slung across the back'."""
    # Guard sits just behind the hip; tip sweeps up-left into open sky so the
    # cutlass reads as a separate object breaking the silhouette, not a cape.
    guard = (18, 40)
    butt  = (10, 47)               # pommel below/behind the tail
    tip   = (3, 8)                 # curved point high past the back shoulder

    # Short grip from the pommel up to the crossguard.
    pygame.draw.line(surf, _STEEL_D, butt, guard, 4)
    pygame.draw.line(surf, _STEEL, butt, guard, 2)
    pygame.draw.circle(surf, _GOLD, butt, 3)          # pommel knob
    pygame.draw.circle(surf, _GOLD_H, (butt[0] - 1, butt[1] - 1), 1)

    # Gold crossguard nub — a short bar across the blade base.
    gx, gy = guard
    pygame.draw.line(surf, _GOLD, (gx - 4, gy + 4), (gx + 4, gy - 4), 4)
    pygame.draw.line(surf, _GOLD_H, (gx - 3, gy + 3), (gx + 3, gy - 3), 1)

    # Straight steel blade up the back, bending into a curved tip near the top
    # so the silhouette break reads as a cutlass point, not a stick.
    spine = [(gx - 1, gy - 4), (15, 28), (12, 16), (9, 10), tip]
    # Dark steel underline first (gives the thin blade a 3px keyed body).
    pygame.draw.lines(surf, _STEEL_D, False,
                      [(x + 1, y) for x, y in spine], 3)
    pygame.draw.lines(surf, _STEEL, False, spine, 2)
    pygame.draw.lines(surf, _STEEL_H, False, spine[:-1], 1)
    # Curved cutlass tip: a small hook off the point that clearly breaks out.
    pygame.draw.line(surf, _STEEL, tip, (tip[0] + 4, tip[1] - 2), 2)
    pygame.draw.line(surf, _STEEL_D, (tip[0] + 1, tip[1] + 1),
                     (tip[0] + 5, tip[1] - 1), 2)
    pygame.draw.circle(surf, (255, 255, 255), tip, 1)   # tip glint


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

    # 1) Cutlass crossing the back — behind everything so the body overlaps it.
    _cutlass(surf)

    # 2) Tail — black bone-flesh fan (kept SMALL/low so it never out-masses
    #    the forward skull cluster: orientation = head is the biggest mass).
    _poly(surf, _BLACK, [(4, 28), (16, 26), (21, 35), (11, 40)])
    _poly(surf, _BLACK_H, [(4, 28), (16, 26), (18, 31)])

    # 3) Body — near-black "flesh" so bright bone reads on top.
    _aaellipse(surf, _BLACK, (33, 33), 19, 14)
    _aaellipse(surf, _BLACK, (32, 32), 18, 13)
    _aaellipse(surf, _BLACK_H, (28, 28), 9, 5)            # faint top sheen

    # 4) Spine — vertebra-bead column from skull base down into the ribcage.
    spine = [(41, 25), (38, 29), (34, 33), (30, 37), (26, 40)]
    for i in range(len(spine) - 1):
        pygame.draw.line(surf, _BONE_D, spine[i], spine[i + 1], 3)
    for vx, vy in spine:
        pygame.draw.circle(surf, _BONE, (vx, vy), 2)

    # 5) Ribcage — chunky DARK-on-bone arcs. A bright bone field is laid first
    #    so the dark ribs read AS ribs (dark lines on light bone), which is how
    #    arcs survive on a bright body at 40px (white-on-dark vanishes here).
    _aaellipse(surf, _BONE_D, (30, 35), 12, 9)
    _aaellipse(surf, _BONE, (30, 34), 11, 8)
    for off, span in ((-3, 15), (2, 16), (7, 16), (11, 15)):
        rx = 21 + off
        pygame.draw.arc(surf, _RIB, (rx, 28, span, 16),
                        math.radians(200), math.radians(340), 2)

    # 6) Crossed-bone Jolly-Roger motif — a single bold X below the sternum,
    #    dark-on-bone so it survives downscale.
    def _xbone(ax, ay, bx, by):
        pygame.draw.line(surf, _RIB, (ax, ay), (bx, by), 3)
        for ex, ey in ((ax, ay), (bx, by)):
            pygame.draw.circle(surf, _BONE, (ex, ey), 2)
            pygame.draw.circle(surf, _RIB, (ex, ey), 2, 1)
    _xbone(25, 40, 35, 46)
    _xbone(25, 46, 35, 40)

    # 7) Wing — skeletal phalanges + bandana-cloth wrist.
    wing = _wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    # ── HEAD CLUSTER (forward, right side) — the biggest, brightest mass ──────
    # 8) Dark keyline halo behind the skull so the white cranium separates from
    #    BOTH the day sky and the dark body (the day-sky-wash fix).
    _aaellipse(surf, _KEY, (47, 21), 13, 12)

    # 9) Skull dome — bright ivory at the head anchor (brightest value).
    _aaellipse(surf, _BONE_D, (47, 22), 12, 11)
    _aaellipse(surf, _BONE, (47, 21), 11, 10)
    _aaellipse(surf, _BONE_D, (47, 26), 8, 4)            # cheekbone / jaw shelf

    # 10) ONE crisp hollow socket — a clean black circle with a hard 2px rim,
    #     a clearly DIFFERENT shape from the oval eyepatch so the two darks read
    #     as two separate features, never one blob. Forward (beak-side) eye.
    #     Dropped low/forward to (49,22) so it parts company with the eyepatch
    #     band and the socket-hole never fuses into a horizontal dark visor.
    pygame.draw.circle(surf, _BONE_DD, (49, 22), 4)      # rim
    pygame.draw.circle(surf, _BLACK, (49, 22), 3)        # hollow
    pygame.draw.circle(surf, (6, 5, 4), (49, 22), 2)     # deepest

    # 11) Nose hollow + bone grin so the skull face reads.
    _poly(surf, _BLACK, [(52, 24), (54, 24), (53, 26)])
    pygame.draw.line(surf, _RIB, (47, 28), (55, 28), 2)  # grin line
    for gx in (48, 51, 54):
        pygame.draw.line(surf, _RIB, (gx, 27), (gx, 30), 1)

    # 12) Beak — bone-outlined over a LIGHTER fill, trimmed ~2px shorter
    #     (tip 62→60). A 2px _BONE keyline over a _BLACK_H (not pure black) fill
    #     keeps the beak a SEPARATE feature on day sky instead of fusing with the
    #     sockets into one dark mass.
    beak = [(56, 22), (60, 24), (58, 28), (53, 27)]
    _poly(surf, _BLACK_H, beak)
    pygame.draw.polygon(surf, _BONE, beak, 2)

    # 13) Black EYEPATCH over the OTHER (back-side) socket — a small black OVAL
    #     of a clearly different shape than the round hollow, ringed with a thin
    #     bone rim so it stays a SEPARATE dark lens against the dark keyline (not
    #     one mass), plus a 1px strap line. Shrunk to (4,3) and centered (41,19)
    #     so it pulls back off the socket's left edge. Two distinct dark shapes.
    pygame.draw.line(surf, _BLACK, (39, 11), (44, 24), 2)   # strap over crown→jaw
    _aaellipse(surf, _BONE_D, (41, 19), 5, 4)               # bone rim frames patch
    _aaellipse(surf, _BLACK, (41, 19), 4, 3)                # oval patch lens
    _aaellipse(surf, _BLACK_H, (40, 18), 2, 1)              # tiny patch sheen

    # A bright 1px _BONE bridge between the socket and the patch so a light gap
    # ALWAYS parts the two darks at 1× — without it they smear into one band.
    pygame.draw.line(surf, _BONE, (45, 18), (45, 23), 1)
    pygame.draw.line(surf, _BONE, (46, 19), (46, 22), 1)

    # 14) Gold hoop earring at the jaw (clean dot tell) — nudged 1px off the jaw
    #     so the dark keyline doesn't swallow the gold on day sky.
    pygame.draw.circle(surf, _GOLD, (44, 31), 2)
    pygame.draw.circle(surf, _GOLD_H, (43, 30), 1)

    # 15) Red bandana wrapping the CRANIUM ONLY + a short knot-tail trailing
    #     back-and-down. Lowered to hug the BROW (band top 10→12 / 11→13) so it
    #     stops reading as a peaked Santa crown; widened 1px past the back skull
    #     edge so the WRAP reads (a hat never wraps); the knot-tail flattened to
    #     trail back/down instead of a peaked up-forward tip.
    band = [(39, 16), (56, 16), (55, 12), (40, 13)]
    _poly(surf, _RED, band)
    _poly(surf, _RED_D, [(39, 16), (56, 16), (56, 15), (39, 15)])
    pygame.draw.line(surf, _RED_H, (43, 14), (54, 14), 2)
    # Knot at the back-top of the skull (over the crown's back edge).
    _poly(surf, _RED, [(39, 13), (44, 12), (45, 17), (40, 18)])
    _poly(surf, _RED_D, [(39, 13), (40, 18), (42, 15)])
    # Short knot-tails trailing BACK-and-DOWN off the knot (not a peaked
    # up-forward flick) — breaks the outline at the back, reading as cloth ends.
    _poly(surf, _RED, [(40, 14), (33, 12), (32, 16), (40, 18)])
    _poly(surf, _RED_D, [(40, 18), (32, 16), (36, 15)])
    _poly(surf, _RED, [(39, 17), (33, 18), (34, 21), (40, 19)])
    pygame.draw.line(surf, _RED_H, (39, 15), (34, 14), 1)
    # At most one low polka dot near the knot (a single cloth tell, not a row of
    # fur-trim dots over the crown).
    pygame.draw.circle(surf, _BONE, (37, 16), 1)

    # 16) Legs — bone leg-pair; one foot is a peg-leg stub for character. The
    #     clawed foot drops to 2 claws (was 3) so the toes don't merge to a blob
    #     at downscale.
    pygame.draw.line(surf, _BONE_D, (35, 45), (36, 50), 3)
    pygame.draw.line(surf, _BONE, (35, 45), (36, 50), 2)
    pygame.draw.circle(surf, _BONE, (35, 45), 2)           # knee knob
    for tx in (34, 39):
        pygame.draw.line(surf, _BONE, (36, 50), (tx, 53), 2)
    # Peg-leg stub (back leg) — a clean 3px tapered bone peg, no foot, so the leg
    # survives the gameplay downscale.
    pygame.draw.line(surf, _BONE_D, (29, 44), (29, 52), 4)
    pygame.draw.line(surf, _BONE, (29, 44), (29, 51), 3)
    pygame.draw.circle(surf, _BONE, (29, 44), 2)           # peg knee knob
    # A red cloth wrap where the peg meets the bone (pirate detail).
    pygame.draw.line(surf, _RED, (27, 46), (31, 46), 2)

    return surf


build = store_skins._make_prebuilt_skin(_build_design4)
