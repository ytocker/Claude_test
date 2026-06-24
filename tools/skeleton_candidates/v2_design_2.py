"""v2_design_2 — PIRATE-MACAW: the DEADMAN'S FLAG pirate on correct anatomy.

Keeps the v1 pirate gear — red bandana wrapping the cranium, a black eyepatch
over the socket, a gold hoop earring, and a steel cutlass slung across the back
breaking the silhouette — but rebuilt on the ``_v2_anatomy`` parrot skeleton so
the hooked bone beak and the long bony tail now read as a macaw. Bone is the
bright value anchor; the gear is the theme layer. Scratch only.

This module hosts FIVE distinct pirate takes (``build_v1``..``build_v5``) for
the round sheet — same locked anatomy, genuinely different gear reads — plus
``build`` aliased to the lead candidate so the harness has a default:

  v1 CORSAIR    brow bandana + back cutlass + chest X (the canonical refine)
  v2 CAPTAIN    black tricorn hat w/ bone crossbones cockade, no bandana
  v3 BALDRIC    bandana + dark baldric strap w/ crossbones plaque, sabre
  v4 FLAGBEARER bandana + ragged Jolly-Roger pennant on a mast-bone behind
  v5 BUCCANEER  bandana w/ red feather plume + boarding hook + cutlass

Every take keeps the macaw read: the HOOKED BONE BEAK stays bare (gear wraps
the CRANIUM only), the long bony tail stays visible, and the two eye-darks
(round bone socket vs. black oval eyepatch) keep a bright bone bridge between
them so they never fuse into one visor.
"""
import math
import pygame

from game.store_skins import _make_prebuilt_skin, _poly
from tools.skeleton_candidates import _v2_anatomy as A


# Warm-ivory bone so the gear colours sit naturally on it.
P = A.Pal(
    bone=(244, 239, 224), bone_sh=(196, 188, 166), bone_deep=(150, 142, 122),
    body=(26, 20, 16), body_deep=(14, 10, 8), keyline=(40, 30, 24),
    socket=(8, 6, 5), glint=(255, 250, 235), rib=(96, 80, 64),
)

_RED, _RED_D, _RED_H = (200, 32, 43), (150, 22, 32), (236, 92, 96)
_BLACK, _BLACK_H = (26, 20, 16), (78, 66, 58)
# Bone-deep rim laid OUTSIDE the black felt so the tricorn silhouette survives
# against night pillars/dark body where pure black would vanish.
_HAT_RIM = (150, 142, 122)
_GOLD, _GOLD_H = (232, 178, 58), (255, 224, 140)
_STEEL, _STEEL_D, _STEEL_H = (185, 192, 201), (120, 128, 138), (228, 233, 238)


# ── shared gear pieces ────────────────────────────────────────────────────────
def _cutlass(surf, angle_deg, P):
    """Steel blade slung across the back, drawn behind the bones; gold crossguard
    low by the hip, curved tip breaking the outline high past the shoulder. A
    thin steel diagonal — never a back-blob."""
    guard, butt, tip = (18, 40), (10, 47), (3, 8)
    pygame.draw.line(surf, _STEEL_D, butt, guard, 4)
    pygame.draw.line(surf, _STEEL, butt, guard, 2)
    pygame.draw.circle(surf, _GOLD, butt, 3)            # pommel knob
    pygame.draw.circle(surf, _GOLD_H, (butt[0] - 1, butt[1] - 1), 1)
    gx, gy = guard
    pygame.draw.line(surf, _GOLD, (gx - 4, gy + 4), (gx + 4, gy - 4), 4)   # guard
    blade = [(gx - 1, gy - 4), (15, 28), (12, 16), (9, 10), tip]
    pygame.draw.lines(surf, _STEEL_D, False, [(x + 1, y) for x, y in blade], 3)
    pygame.draw.lines(surf, _STEEL, False, blade, 2)
    # Highlight runs the FULL blade incl. the tip so it reads as a sharpened
    # edge of light, not a stray bone with a dull point.
    pygame.draw.lines(surf, _STEEL_H, False, blade, 1)
    # Sharpened upswept point — curved tip kicked up 1px so it reads as a blade.
    pygame.draw.line(surf, _STEEL, tip, (tip[0] + 5, tip[1] - 4), 2)
    pygame.draw.line(surf, _STEEL_H, tip, (tip[0] + 5, tip[1] - 4), 1)
    pygame.draw.circle(surf, (255, 255, 255), (tip[0] + 5, tip[1] - 4), 1)


def _eyepatch(surf, P):
    """Black oval eyepatch over the BACK socket + a bright bone bridge so it
    reads as a distinct dark from the round bone socket (never one visor).
    The anatomy's own socket lives forward at ~(45,16); this patch sits back at
    ~(40,15) with a 1px bone gap kept between them."""
    pygame.draw.line(surf, _BLACK, (37, 9), (42, 19), 2)        # strap crown→jaw
    A._aaellipse(surf, P.bone_sh, (40, 15), 5, 4)              # bone rim frame
    A._aaellipse(surf, _BLACK, (40, 15), 4, 3)                 # oval lens
    A._aaellipse(surf, _BLACK_H, (39, 14), 2, 1)              # faint sheen
    # Bright bone bridge parting the patch from the round socket at (45,16).
    pygame.draw.line(surf, P.bone, (44, 13), (44, 18), 1)
    pygame.draw.line(surf, P.bone, (43, 14), (43, 17), 1)


def _earring(surf, P):
    """Gold hoop at the jaw-TIP front (~48,27) where the dark body sits behind it
    so the gold hoop reads as a distinct shape instead of dissolving into the
    bone jaw at 40px."""
    pygame.draw.circle(surf, _GOLD, (48, 27), 2)
    pygame.draw.circle(surf, _GOLD, (48, 27), 2, 1)
    pygame.draw.circle(surf, _GOLD_H, (47, 26), 1)


def _bandana(surf, P, plume=False):
    """Red bandana wrapping the CRANIUM ONLY (brow-hugging) with a knot + tails
    trailing back, leaving the hooked beak fully bare. Optional red feather
    plume rising off the knot for the buccaneer take."""
    band = [(37, 12), (54, 11), (54, 8), (38, 9)]             # brow wrap
    _poly(surf, _RED, band)
    pygame.draw.line(surf, _RED_H, (41, 10), (52, 10), 2)     # sheen
    _poly(surf, _RED_D, [(37, 12), (54, 11), (54, 12), (37, 13)])  # under-shade
    # Knot over the back crown edge + two tails trailing back/down (break out).
    _poly(surf, _RED, [(37, 9), (42, 8), (43, 13), (38, 14)])      # knot
    _poly(surf, _RED, [(38, 10), (30, 8), (29, 12), (38, 14)])     # upper tail
    _poly(surf, _RED_D, [(38, 14), (29, 12), (33, 11)])
    _poly(surf, _RED, [(38, 13), (31, 15), (32, 18), (38, 15)])    # lower tail
    pygame.draw.circle(surf, P.bone, (35, 12), 1)                  # one cloth dot
    if plume:
        pygame.draw.line(surf, _RED_D, (40, 8), (35, 1), 3)       # plume quill
        pygame.draw.line(surf, _RED, (40, 8), (36, 1), 2)
        for fx, fy in ((34, 2), (37, 0), (33, 5)):               # feather barbs
            pygame.draw.line(surf, _RED_H, (37, 4), (fx, fy), 1)


def _crossbones_x(surf, P, cx=31, cy=40):
    """A bold X crossbones on the chest — the Jolly-Roger tell. Laid on a small
    dark cartouche disc so the BRIGHT bone X reads cleanly against it (bone-on-
    dark survives where dark-on-tangle vanishes); bone end-knobs cap each arm.
    Sat low-forward on the belly clear of the wing wrist so the two never share
    pixels."""
    A._aaellipse(surf, P.body_deep, (cx, cy), 8, 7)       # dark cartouche disc
    pygame.draw.circle(surf, P.keyline, (cx, cy), 8, 1)   # rim
    arms = (((cx - 5, cy - 3), (cx + 5, cy + 3)),
            ((cx - 5, cy + 3), (cx + 5, cy - 3)))
    for (ax, ay), (bx, by) in arms:
        pygame.draw.line(surf, P.keyline, (ax, ay), (bx, by), 4)   # dark rim
        pygame.draw.line(surf, P.bone, (ax, ay), (bx, by), 2)      # bright core
        for ex, ey in ((ax, ay), (bx, by)):
            pygame.draw.circle(surf, P.bone, (ex, ey), 2)
            pygame.draw.circle(surf, P.keyline, (ex, ey), 2, 1)


# ── v1 CORSAIR — the canonical refine (bandana + back cutlass + chest X) ───────
def _v1_pre(surf, angle_deg, P):
    _cutlass(surf, angle_deg, P)


def _v1_post(surf, angle_deg, P):
    _eyepatch(surf, P)
    _earring(surf, P)
    _bandana(surf, P)
    _crossbones_x(surf, P)


# ── v2 CAPTAIN — black tricorn hat (no bandana), bone crossbones cockade ───────
def _v2_pre(surf, angle_deg, P):
    _cutlass(surf, angle_deg, P)


def _captain_chest_x(surf, P, cx=31, cy=40):
    """The bone crossbones laid DIRECTLY on the ribcage as the single brightest
    mass — no dark cartouche disc. A 1px keyline halo hugs each bone so the
    bone-on-rib X stays legible without a competing dark plate stealing focus
    from the hat front."""
    arms = (((cx - 5, cy - 3), (cx + 5, cy + 3)),
            ((cx - 5, cy + 3), (cx + 5, cy - 3)))
    for (ax, ay), (bx, by) in arms:
        pygame.draw.line(surf, P.keyline, (ax, ay), (bx, by), 4)   # tight halo
        pygame.draw.line(surf, P.bone, (ax, ay), (bx, by), 2)      # bright core
        for ex, ey in ((ax, ay), (bx, by)):
            pygame.draw.circle(surf, P.keyline, (ex, ey), 2, 1)
            pygame.draw.circle(surf, P.bone, (ex, ey), 1)


def _v2_hat(surf, P):
    """Three-cornered captain's hat sitting on the cranium crown, NOT over the
    beak. A dark felt brim sweeping up at front and back corners, a bone-white
    crossbones cockade pinned at the front — the captain's-hat alt to a wrap.

    The black felt is RIMMED with a bone-deep stroke laid OUTSIDE it so the
    tricorn silhouette survives on night where pure black fuses with the dark
    pillars/body."""
    brim = [(31, 9), (38, 4), (49, 2), (56, 6), (52, 9), (40, 10)]
    front_peak = [(54, 6), (58, 1), (57, 7)]
    back_peak = [(33, 9), (28, 4), (31, 10)]
    # Bone-deep rim OUTSIDE the black, drawn first so the felt overpaints its
    # interior and only the outer edge survives as a night-legible silhouette.
    pygame.draw.polygon(surf, _HAT_RIM, brim, 3)
    pygame.draw.polygon(surf, _HAT_RIM, front_peak, 2)
    pygame.draw.polygon(surf, _HAT_RIM, back_peak, 2)
    _poly(surf, _BLACK, brim)
    _poly(surf, _BLACK, front_peak)                              # front peak
    _poly(surf, _BLACK, back_peak)                               # back peak
    # Widened top sheen (lightened felt) so the crown catches a little light.
    _poly(surf, _BLACK_H, [(38, 4), (49, 2), (49, 5), (39, 7)])
    # Bone crossbones cockade pinned at the front of the brim.
    for (ax, ay), (bx, by) in (((44, 4), (49, 8)), ((44, 8), (49, 4))):
        pygame.draw.line(surf, P.bone, (ax, ay), (bx, by), 2)
    pygame.draw.circle(surf, P.bone, (46, 6), 2)
    pygame.draw.circle(surf, P.keyline, (46, 6), 2, 1)
    # One bright glint dot at the hat front so the eye locks the cockade focal.
    pygame.draw.circle(surf, P.glint, (45, 5), 1)


def _v2_post(surf, angle_deg, P):
    _eyepatch(surf, P)
    _earring(surf, P)
    _v2_hat(surf, P)
    _captain_chest_x(surf, P)


# ── v3 BALDRIC — bandana + dark baldric strap w/ crossbones plaque, sabre ──────
def _v3_pre(surf, angle_deg, P):
    _cutlass(surf, angle_deg, P)


def _v3_baldric(surf, P):
    """A dark leather baldric strap crossing the chest shoulder-to-hip with a
    round bone-and-gold crossbones plaque where it meets the sternum — a
    sturdier 'kit' read than a lone painted X."""
    strap = [(40, 23), (44, 26), (24, 47), (20, 44)]
    _poly(surf, _BLACK, strap)
    pygame.draw.line(surf, _BLACK_H, (40, 24), (22, 45), 1)
    # Round gold-rim plaque mid-strap.
    px, py = 32, 35
    pygame.draw.circle(surf, _GOLD, (px, py), 5)
    pygame.draw.circle(surf, _BLACK, (px, py), 4)
    for (ax, ay), (bx, by) in (((px - 3, py - 3), (px + 3, py + 3)),
                               ((px - 3, py + 3), (px + 3, py - 3))):
        pygame.draw.line(surf, P.bone, (ax, ay), (bx, by), 2)
    pygame.draw.circle(surf, P.bone, (px, py), 1)


def _v3_post(surf, angle_deg, P):
    _v3_baldric(surf, P)
    _eyepatch(surf, P)
    _earring(surf, P)
    _bandana(surf, P)


# ── v4 FLAGBEARER — bandana + ragged Jolly-Roger pennant on a mast-bone ────────
def _v4_pre(surf, angle_deg, P):
    """A bone mast rising behind the back shoulder flying a small ragged black
    pennant with a bone skull-and-bones — drawn behind the bird so the body
    overlaps the mast foot. Cutlass kept low so the two don't collide."""
    # Mast bone.
    A._bone_line(surf, P, (16, 40), (10, 6), 3)
    # Ragged black pennant streaming back off the mast top.
    flag = [(10, 7), (1, 9), (3, 13), (0, 17), (4, 19), (1, 22), (10, 21)]
    _poly(surf, _BLACK, flag)
    pygame.draw.line(surf, _BLACK_H, (10, 8), (10, 20), 1)
    # Bone skull + crossed bones on the flag.
    A._aaellipse(surf, P.bone, (6, 13), 3, 3)
    pygame.draw.circle(surf, _BLACK, (5, 13), 1)
    pygame.draw.circle(surf, _BLACK, (7, 13), 1)
    for (ax, ay), (bx, by) in (((3, 16), (9, 19)), ((3, 19), (9, 16))):
        pygame.draw.line(surf, P.bone, (ax, ay), (bx, by), 1)
    # Low cutlass tucked under the body (short, doesn't reach the flag).
    pygame.draw.line(surf, _STEEL_D, (8, 47), (20, 41), 4)
    pygame.draw.line(surf, _STEEL, (8, 47), (20, 41), 2)
    pygame.draw.circle(surf, _GOLD, (8, 47), 3)


def _v4_post(surf, angle_deg, P):
    _eyepatch(surf, P)
    _earring(surf, P)
    _bandana(surf, P)
    _crossbones_x(surf, P)


# ── v5 BUCCANEER — bandana w/ red feather plume + boarding hook + cutlass ──────
def _v5_pre(surf, angle_deg, P):
    _cutlass(surf, angle_deg, P)


def _v5_hook(surf, P):
    """A curved steel boarding hook replacing one foot — the buccaneer 'hook
    hand/foot' tell — and a gold cuff where it meets the leg bone."""
    pygame.draw.circle(surf, _GOLD, (34, 47), 2)                 # cuff
    hook = [(34, 49), (37, 52), (35, 55), (31, 54)]
    pygame.draw.lines(surf, _STEEL_D, False, [(x + 1, y) for x, y in hook], 3)
    pygame.draw.lines(surf, _STEEL, False, hook, 2)
    pygame.draw.circle(surf, _STEEL_H, (31, 54), 1)


def _v5_post(surf, angle_deg, P):
    _eyepatch(surf, P)
    _earring(surf, P)
    _bandana(surf, P, plume=True)
    _v5_hook(surf, P)
    _crossbones_x(surf, P)


# ── builders ──────────────────────────────────────────────────────────────────
def _mk(pre, post):
    def _b(wing_angle_deg):
        return A.build_skeleton(wing_angle_deg, P, pre=pre, post=post,
                                draw_socket=True)
    return _make_prebuilt_skin(_b)


build_v1 = _mk(_v1_pre, _v1_post)     # CORSAIR
build_v2 = _mk(_v2_pre, _v2_post)     # CAPTAIN
build_v3 = _mk(_v3_pre, _v3_post)     # BALDRIC
build_v4 = _mk(_v4_pre, _v4_post)     # FLAGBEARER
build_v5 = _mk(_v5_pre, _v5_post)     # BUCCANEER

build = build_v2                      # CAPTAIN — art-director's lead take
