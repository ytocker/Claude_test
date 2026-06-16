"""
Calaca Comelona — the gluttonous Day-of-the-Dead street-food VENDOR whose
open ribcage is a literal pantry stuffed with food (BATCH 2 / mariachi-lineage
warm-skeleton family, lead facet: EXPOSED ANATOMY).

Procedural Pygame, house style: chibi proportions, flat saturated fills + hard
1-2px ink keylines, form via the dark-core -> flat-fill -> top-left rim-sheen
TRIAD (never soft gradient), silhouette POP via a 1px outline grown from the
alpha mask, supersample (SS=4) -> smoothscale.

Red-split pin honoured: chile-red `(214,86,44)` is a SMALL accent ONLY (hatband
+ one chile lobe), pushed oranger to stay off Zapateada's pink-rose. The HERO
body mass is masa-gold/corn-tan `(228,186,96)` (food + tamale) with warm-bone
ribcage. Lead read is EXPOSED ANATOMY: the barrel ribcage spreads OPEN like
cupboard doors framing an interior cluster of exactly 3 fat food lobes.

Sheet shows the creature AND its prop->pillar mirror (market-pole ristra +
round comal cap) at large + 32px scales, plus a pure-black silhouette panel and
the pinned palette swatches.

Run headless:  SDL_VIDEODRIVER=dummy python render_comelona.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

pygame.init()

# -- PINNED PALETTE (locked brief, exact hexes) -------------------------------
MASA_GOLD   = (228, 186,  96)   # masa-gold tamale/pan -- HERO body/food mass
OCHRE_HAT   = (214, 156,  72)   # pumpkin-ochre straw vendor hat
BONE        = (236, 222, 194)   # warm-bone ribcage
BONE_SHADE  = (174, 148, 106)   # tan-bone shade
CHILE       = (214,  86,  44)   # chile-red ACCENT ONLY (hatband + one chile)
CILANTRO    = (120, 170,  80)   # cilantro-green garnish, tiny
INK         = ( 30,  22,  20)   # keyline ink
SHEEN       = (250, 240, 218)   # top-left rim sheen

# Derived working tones, all kept inside the pinned families (triad cores/sheens).
BONE_CORE   = (150, 126,  90)   # dark-core under bone (deeper than tan shade)
GOLD_CORE   = (162, 122,  52)   # dark-core under masa-gold
GOLD_SHEEN  = (246, 218, 142)   # masa-gold top-left sheen
OCHRE_CORE  = (152, 104,  44)   # dark-core under straw hat
OCHRE_SHEEN = (244, 198, 124)   # straw-hat top-left sheen
CHILE_CORE  = (132,  46,  24)   # dark-core under chile-red
CHILE_SHEEN = (236, 138,  92)   # chile-red top-left sheen
CILANTRO_D  = ( 80, 120,  52)   # cilantro garnish shade
# Pan-dulce concha gets a warm pinkish tint that still lives in the gold family
# so the red read stays demoted -- it must not compete with the chile accent.
PAN_PINK    = (224, 152, 118)   # pan-dulce concha shell glaze
PAN_PINK_D  = (164,  98,  74)
PAN_PINK_S  = (244, 196, 168)

SS = 4   # supersample factor


# -- geometry / triad helpers (house grammar) ---------------------------------

def _ell(surf, color, cx, cy, rx, ry):
    pygame.draw.ellipse(surf, color,
                        (int(cx - rx), int(cy - ry), int(rx * 2), int(ry * 2)))


def triad_ellipse(surf, cx, cy, rx, ry, core, fill, sheen, outline=INK):
    """dark-core -> flat-fill -> top-left rim-sheen on an ellipse mass, with a
    hard ink keyline. Reads as form without any soft gradient."""
    if outline is not None:
        _ell(surf, outline, cx, cy, rx + SS, ry + SS)
    _ell(surf, core, cx, cy, rx, ry)
    _ell(surf, fill, cx, cy, rx - SS * 0.7, ry - SS * 0.7)
    _ell(surf, sheen, cx - rx * 0.34, cy - ry * 0.36, rx * 0.5, ry * 0.42)


def triad_poly(surf, pts, core, fill, sheen, outline=INK, sheen_pts=None):
    """Triad on an arbitrary polygon: ink keyline, core fill, inset fill, then an
    optional top-left sheen sliver."""
    if outline is not None:
        pygame.draw.polygon(surf, outline, pts)
        pygame.draw.polygon(surf, outline, pts, SS * 2)
    pygame.draw.polygon(surf, core, pts)
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    inset = [(p[0] + (cx - p[0]) * 0.16, p[1] + (cy - p[1]) * 0.16) for p in pts]
    pygame.draw.polygon(surf, fill, inset)
    if sheen_pts:
        pygame.draw.polygon(surf, sheen, sheen_pts)


def grow_outline(surf, color=INK, thickness=1):
    """1px (post-scale) outline grown from the alpha mask -- the silhouette POP.
    Run at supersample scale so it survives smoothscale."""
    mask = pygame.mask.from_surface(surf)
    outline_pts = mask.outline()
    if len(outline_pts) > 2:
        pygame.draw.lines(surf, color, True, outline_pts, max(1, thickness * SS))


# -- the creature -------------------------------------------------------------

def draw_comelona(target_size):
    """Squat bottom-heavy pear vendor calaca: small skull under a flat straw
    vendor hat with a chile clenched cigar-style in the grin; a wide barrel
    RIBCAGE spread OPEN like cupboard doors framing an interior cluster of 3 fat
    food lobes (pan dulce, one chile, a round tamale); thin pelvis + bowed bone
    legs; one bony hand thrust forward offering a fat tamale. The open-belly-
    with-food-inside read is the signature -- gluttony through bared bone."""
    S = target_size * SS
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = S * 0.5

    # Layout anchors (fractions of S). Bottom-heavy: small high skull, wide low
    # ribcage belly, short legs -- the pear silhouette.
    hat_y   = S * 0.205
    head_y  = S * 0.275
    belly_y = S * 0.575   # centre of the open ribcage pantry (dominant mass)
    hip_y   = S * 0.745

    # ---- BONE LEGS: short, bowed femurs (drawn first, pelvis overlaps hips) ---
    def bone_limb(p0, p1, p2, w):
        for a, b in ((p0, p1), (p1, p2)):
            pygame.draw.line(surf, INK, a, b, int(w + SS * 1.6))
        for a, b in ((p0, p1), (p1, p2)):
            pygame.draw.line(surf, BONE_SHADE, a, b, int(w))
            pygame.draw.line(surf, BONE, a, b, int(w * 0.5))
        for p in (p0, p1, p2):
            triad_ellipse(surf, p[0], p[1], w * 0.62, w * 0.62,
                          BONE_CORE, BONE, SHEEN)

    legw = S * 0.062
    # Bowed femur legs splayed slightly so the squat base is wide -- a planted,
    # heavy vendor stance, not a dancer's kick.
    bone_limb((cx - S * 0.085, hip_y),
              (cx - S * 0.155, S * 0.85),
              (cx - S * 0.115, S * 0.95), legw)
    bone_limb((cx + S * 0.085, hip_y),
              (cx + S * 0.155, S * 0.85),
              (cx + S * 0.115, S * 0.95), legw)
    # Flat bone feet, toes outward.
    for fx in (cx - S * 0.115, cx + S * 0.115):
        triad_ellipse(surf, fx + S * 0.02, S * 0.955, S * 0.072, S * 0.038,
                      BONE_CORE, BONE, SHEEN)

    # ---- THIN PELVIS (the narrow waist of the pear, under the wide belly) -----
    pelvis = [
        (cx - S * 0.115, hip_y - S * 0.05),
        (cx + S * 0.115, hip_y - S * 0.05),
        (cx + S * 0.085, hip_y + S * 0.045),
        (cx,             hip_y + S * 0.02),
        (cx - S * 0.085, hip_y + S * 0.045),
    ]
    triad_poly(surf, pelvis, BONE_CORE, BONE, SHEEN)
    # Pelvic eye-holes (iliac fossae) -- bone read.
    for sx in (-1, 1):
        _ell(surf, INK, cx + sx * S * 0.058, hip_y - S * 0.005,
             S * 0.026, S * 0.034)

    # ---- OPEN RIBCAGE PANTRY (the dominant mass + signature read) -------------
    # Back wall: warm-bone barrel that the cage doors swing off, with the spine
    # visible up the back. Drawn before the food cluster so food sits INSIDE.
    back = [
        (cx - S * 0.225, belly_y - S * 0.135),
        (cx + S * 0.225, belly_y - S * 0.135),
        (cx + S * 0.205, belly_y + S * 0.165),
        (cx,             belly_y + S * 0.205),
        (cx - S * 0.205, belly_y + S * 0.165),
    ]
    triad_poly(surf, back, BONE_CORE, BONE_SHADE, BONE,
               sheen_pts=[(cx - S * 0.205, belly_y - S * 0.11),
                          (cx - S * 0.06,  belly_y - S * 0.12),
                          (cx - S * 0.10,  belly_y + S * 0.10),
                          (cx - S * 0.18,  belly_y + S * 0.09)])
    # Spine ticks up the centre-back, peeking between the food lobes' gaps.
    for i in range(5):
        sy = belly_y - S * 0.10 + i * S * 0.06
        _ell(surf, BONE_SHADE, cx, sy, S * 0.022, S * 0.018)
        _ell(surf, INK, cx, sy, S * 0.022, S * 0.018)

    # INTERIOR FOOD CLUSTER -- exactly 3 FAT lobes (brief cap: 4th garnish
    # dropped to avoid 32px noise). Gold/bone hero mass; chile is the ONE small
    # red. Each lobe gets the hard triad so the pantry reads busy but legible.
    # Lobe 1: round tamale (masa-gold husk-wrapped) -- lower-centre, biggest.
    triad_ellipse(surf, cx + S * 0.01, belly_y + S * 0.055,
                  S * 0.115, S * 0.10, GOLD_CORE, MASA_GOLD, GOLD_SHEEN)
    # Husk-tie ink ticks so the tamale reads as wrapped, not a plain blob.
    for k in (-1, 0, 1):
        pygame.draw.line(surf, BONE_SHADE,
                         (cx + S * 0.01 + k * S * 0.03, belly_y - S * 0.03),
                         (cx + S * 0.01 + k * S * 0.045, belly_y + S * 0.15),
                         max(1, int(SS * 0.8)))
    # Lobe 2: pan dulce concha (upper-left) -- warm pink glaze in the gold family
    # with a cross-hatch shell, so it's clearly bread, not a second chile.
    pcx, pcy = cx - S * 0.10, belly_y - S * 0.045
    triad_ellipse(surf, pcx, pcy, S * 0.082, S * 0.078,
                  PAN_PINK_D, PAN_PINK, PAN_PINK_S)
    for k in (-1, 0, 1):
        pygame.draw.line(surf, PAN_PINK_D,
                         (pcx - S * 0.05, pcy + k * S * 0.026),
                         (pcx + S * 0.05, pcy + k * S * 0.026), max(1, int(SS)))
        pygame.draw.line(surf, PAN_PINK_D,
                         (pcx + k * S * 0.026, pcy - S * 0.05),
                         (pcx + k * S * 0.026, pcy + S * 0.05), max(1, int(SS)))
    # Lobe 3: ONE chile (upper-right) -- the SMALL red accent, oranger so it
    # stays off Zapateada's pink-rose. A curved pod with a green cilantro stem
    # cap to anchor it as produce, not the body's hue.
    chx, chy = cx + S * 0.115, belly_y - S * 0.055
    chile_pod = [
        (chx - S * 0.018, chy - S * 0.07),
        (chx + S * 0.045, chy - S * 0.04),
        (chx + S * 0.06,  chy + S * 0.035),
        (chx + S * 0.02,  chy + S * 0.085),
        (chx - S * 0.03,  chy + S * 0.05),
        (chx - S * 0.045, chy - S * 0.01),
    ]
    triad_poly(surf, chile_pod, CHILE_CORE, CHILE, CHILE_SHEEN)
    pygame.draw.line(surf, CILANTRO_D,
                     (chx - S * 0.018, chy - S * 0.07),
                     (chx - S * 0.035, chy - S * 0.105), max(2, int(SS * 1.4)))
    pygame.draw.line(surf, CILANTRO,
                     (chx - S * 0.018, chy - S * 0.07),
                     (chx - S * 0.035, chy - S * 0.105), max(1, int(SS * 0.7)))

    # CAGE DOORS: the ribs spread OPEN like cupboard doors, in front of the food
    # cluster so they FRAME it. Two stacks of curved rib bands per side, hinged
    # at the spine and swinging outward -- the "open cupboard" tell. Hard triad
    # on every rib: dark-core trough, flat bone face, top-left sheen lip.
    def rib(side, i, n):
        t = i / (n - 1)
        ry0 = belly_y - S * 0.115 + t * S * 0.26
        # Outward swing: lower ribs reach wider, like flung-open doors.
        reach = S * (0.10 + 0.13 * (0.4 + 0.6 * t))
        hinge_x = cx + side * S * 0.028
        tip_x = cx + side * reach
        curve = S * 0.05 * (1.0 - abs(t - 0.5) * 1.2)
        # Rib as a fat curved bone bar: trough core, bone face, sheen lip.
        thick = S * 0.030
        pts = [
            (hinge_x, ry0 - thick),
            (cx + side * reach * 0.55, ry0 - thick - curve),
            (tip_x, ry0 - thick * 0.4 - curve * 0.4),
            (tip_x, ry0 + thick * 0.6 - curve * 0.4),
            (cx + side * reach * 0.55, ry0 + thick - curve),
            (hinge_x, ry0 + thick),
        ]
        triad_poly(surf, pts, BONE_CORE, BONE, SHEEN)
        # Bright sheen lip along the TOP edge of each rib so curvature reads in
        # flat banding (brief: curvature in flat banding, never gradient).
        pygame.draw.line(surf, SHEEN,
                         (hinge_x, ry0 - thick * 0.5),
                         (cx + side * reach * 0.6, ry0 - thick * 0.5 - curve),
                         max(1, int(SS * 0.9)))

    for side in (-1, 1):
        for i in range(4):
            rib(side, i, 4)
    # Hinge spine seam: a dark ink valley up the centre where the doors meet, so
    # the "two doors swung open" read is unmistakable in silhouette.
    pygame.draw.line(surf, INK,
                     (cx, belly_y - S * 0.135),
                     (cx, belly_y + S * 0.19), max(2, int(SS * 1.6)))

    # ---- SKULL head (small, grinning, chile clenched cigar-style) ------------
    triad_ellipse(surf, cx, head_y, S * 0.128, S * 0.135,
                  BONE_CORE, BONE, SHEEN)
    triad_ellipse(surf, cx, head_y + S * 0.085, S * 0.095, S * 0.058,
                  BONE_CORE, BONE, SHEEN)
    # Eye sockets -- DotD style with a tiny ochre marigold petal ring.
    for ex in (cx - S * 0.05, cx + S * 0.05):
        triad_ellipse(surf, ex, head_y - S * 0.008, S * 0.032, S * 0.036,
                      (40, 28, 24), (56, 40, 32), (92, 68, 52), outline=None)
        for k in range(8):
            a = k * math.tau / 8
            px = ex + math.cos(a) * S * 0.042
            py = (head_y - S * 0.008) + math.sin(a) * S * 0.048
            pygame.draw.circle(surf, OCHRE_HAT, (int(px), int(py)),
                               max(1, int(SS * 1.0)))
        pygame.draw.circle(surf, INK, (int(ex), int(head_y - S * 0.008)),
                           int(S * 0.015))
    # Nose triangle.
    pygame.draw.polygon(surf, (40, 28, 24), [
        (cx, head_y + S * 0.02),
        (cx - S * 0.015, head_y + S * 0.05),
        (cx + S * 0.015, head_y + S * 0.05),
    ])
    # Big toothy grin (vendor cheer).
    sm_y = head_y + S * 0.078
    pygame.draw.arc(surf, INK,
                    (cx - S * 0.07, sm_y - S * 0.038, S * 0.14, S * 0.076),
                    math.pi * 1.05, math.pi * 1.95, max(1, int(SS * 1.6)))
    for k in range(-3, 4):
        tx = cx + k * S * 0.019
        pygame.draw.line(surf, INK, (tx, sm_y - S * 0.012),
                         (tx, sm_y + S * 0.013), max(1, int(SS)))
    # Chile clenched like a CIGAR in the corner of the jaw (the gluttony tell,
    # the second small chile-red accent on the face). Green stem flicks up.
    cgx, cgy = cx + S * 0.075, sm_y + S * 0.004
    cigar = [
        (cgx, cgy - S * 0.014),
        (cgx + S * 0.10, cgy - S * 0.028),
        (cgx + S * 0.11, cgy - S * 0.006),
        (cgx + S * 0.01, cgy + S * 0.014),
    ]
    triad_poly(surf, cigar, CHILE_CORE, CHILE, CHILE_SHEEN)
    pygame.draw.line(surf, CILANTRO,
                     (cgx + S * 0.105, cgy - S * 0.017),
                     (cgx + S * 0.13, cgy - S * 0.04), max(1, int(SS * 0.9)))

    # ---- FLAT STRAW VENDOR HAT (pumpkin-ochre, wide low brim + chile band) ----
    _ell(surf, INK, cx, hat_y + S * 0.012, S * 0.255, S * 0.072)
    triad_ellipse(surf, cx, hat_y, S * 0.25, S * 0.066,
                  OCHRE_CORE, OCHRE_HAT, OCHRE_SHEEN)
    # Woven straw radial ticks so the brim reads as straw, not felt.
    for k in range(-5, 6):
        bx = cx + k * S * 0.04
        pygame.draw.line(surf, OCHRE_CORE,
                         (bx, hat_y - S * 0.02), (bx, hat_y + S * 0.02),
                         max(1, int(SS * 0.7)))
    # Low rounded crown.
    crown = [
        (cx - S * 0.095, hat_y - S * 0.008),
        (cx - S * 0.075, hat_y - S * 0.062),
        (cx - S * 0.04,  hat_y - S * 0.082),
        (cx + S * 0.04,  hat_y - S * 0.082),
        (cx + S * 0.075, hat_y - S * 0.062),
        (cx + S * 0.095, hat_y - S * 0.008),
    ]
    triad_poly(surf, crown, OCHRE_CORE, OCHRE_HAT, OCHRE_SHEEN,
               sheen_pts=[(cx - S * 0.08, hat_y - S * 0.012),
                          (cx - S * 0.045, hat_y - S * 0.072),
                          (cx - S * 0.01, hat_y - S * 0.078),
                          (cx - S * 0.035, hat_y - S * 0.012)])
    # Chile-red HATBAND -- the one designated red accent on the hat.
    pygame.draw.line(surf, CHILE,
                     (cx - S * 0.082, hat_y - S * 0.014),
                     (cx + S * 0.082, hat_y - S * 0.014), max(2, int(SS * 2.0)))
    pygame.draw.line(surf, CHILE_SHEEN,
                     (cx - S * 0.082, hat_y - S * 0.02),
                     (cx + S * 0.04, hat_y - S * 0.02), max(1, int(SS * 0.7)))

    # ---- OFFERED-TAMALE HAND thrust forward (vendor read + asymmetry tell) ----
    # One bony arm reaches out player-right holding a fat masa-gold tamale up to
    # the viewer -- the "vendor offering food" gesture that breaks symmetry.
    sh_x, sh_y = cx + S * 0.205, belly_y - S * 0.05
    el_x, el_y = cx + S * 0.31, belly_y + S * 0.01
    hd_x, hd_y = cx + S * 0.37, belly_y + S * 0.075
    for a, b in (((sh_x, sh_y), (el_x, el_y)), ((el_x, el_y), (hd_x, hd_y))):
        pygame.draw.line(surf, INK, a, b, int(S * 0.05 + SS * 1.6))
        pygame.draw.line(surf, BONE_SHADE, a, b, int(S * 0.05))
        pygame.draw.line(surf, BONE, a, b, int(S * 0.025))
    triad_ellipse(surf, el_x, el_y, S * 0.034, S * 0.034, BONE_CORE, BONE, SHEEN)
    triad_ellipse(surf, sh_x, sh_y, S * 0.04, S * 0.04, BONE_CORE, BONE, SHEEN)
    # Offered tamale on the palm.
    triad_ellipse(surf, hd_x + S * 0.02, hd_y - S * 0.01,
                  S * 0.078, S * 0.068, GOLD_CORE, MASA_GOLD, GOLD_SHEEN)
    for k in (-1, 0, 1):
        pygame.draw.line(surf, BONE_SHADE,
                         (hd_x + S * 0.02 + k * S * 0.022, hd_y - S * 0.07),
                         (hd_x + S * 0.02 + k * S * 0.03, hd_y + S * 0.04),
                         max(1, int(SS * 0.8)))
    # A few bony fingers cupping the tamale underneath.
    for f in range(3):
        fx = hd_x - S * 0.02 + f * S * 0.026
        pygame.draw.line(surf, INK, (fx, hd_y + S * 0.02),
                         (fx + S * 0.01, hd_y + S * 0.06), max(1, int(SS)))
        pygame.draw.line(surf, BONE, (fx, hd_y + S * 0.02),
                         (fx + S * 0.01, hd_y + S * 0.06), max(1, int(SS * 0.5)))

    grow_outline(surf, INK, 1)
    return pygame.transform.smoothscale(surf, (target_size, target_size))


# -- the prop -> pillar mirror (market-pole ristra + comal cap) ---------------

def draw_pillar(width, height, top_cap=True):
    """Market-stall vendor pole: a wooden pole strung with a ristra of dried
    chiles = repeatable shaft (chile banding); a round comal griddle topped with
    a stacked-tamale dome = detachable gap-edge cap. Mirror is clean -- the
    round comal sits on-axis and symmetric (the creature is the bottom-heavy
    one; the prop is balanced), so the cap never goes top-heavy."""
    W = width * SS
    H = height * SS
    cx = W * 0.5
    surf = pygame.Surface((W, H), pygame.SRCALPHA)

    # Wooden pole shaft (warm tan-bone wood lane, so it reads as a market post).
    pole_w = W * 0.26
    pole = pygame.Rect(int(cx - pole_w / 2), 0, int(pole_w), int(H))
    pygame.draw.rect(surf, BONE_CORE, pole)
    pygame.draw.rect(surf, BONE_SHADE, pole.inflate(-int(SS * 3), 0))
    pygame.draw.rect(surf, BONE,
                     (int(cx - pole_w / 2 + SS * 2), 0,
                      int(pole_w * 0.26), int(H)))

    # RISTRA of dried chiles strung down BOTH sides of the pole = repeatable
    # shaft banding. Chile-red here is the prop's signature produce, paired with
    # masa-gold corn ears so the gold-led palette still leads the prop too.
    band = max(1, int(height / 7))
    for i in range(band + 1):
        by = int(H * i / band)
        for side in (-1, 1):
            chx = cx + side * pole_w * 0.62
            chile = [
                (chx, by - SS * 5),
                (chx + side * SS * 5, by - SS * 1),
                (chx + side * SS * 6, by + SS * 5),
                (chx + side * SS * 2, by + SS * 9),
                (chx - side * SS * 1, by + SS * 4),
            ]
            triad_poly(surf, chile, CHILE_CORE, CHILE, CHILE_SHEEN)
        # Masa-gold corn ear hung centre between chile pairs (gold leads).
        if i % 2 == 0:
            triad_ellipse(surf, cx, by + SS * 4, SS * 3.4, SS * 6,
                          GOLD_CORE, MASA_GOLD, GOLD_SHEEN)

    # Gap-edge cap: round comal griddle (on-axis, symmetric) with a stacked-
    # tamale dome rising off it. Sized ~shaft +35% so the mirror stays balanced.
    if top_cap:
        comal_r = pole_w * 0.95   # ~shaft width +35% per radius
        cyp = H - comal_r - W * 0.04
        # Dark iron comal disc.
        triad_ellipse(surf, cx, cyp, comal_r, comal_r * 0.42,
                      (40, 32, 28), (70, 58, 50), (120, 104, 90))
        # Stacked-tamale dome (masa-gold) sitting on the comal -- gold hero mass.
        triad_ellipse(surf, cx, cyp - comal_r * 0.32,
                      comal_r * 0.66, comal_r * 0.6,
                      GOLD_CORE, MASA_GOLD, GOLD_SHEEN)
        triad_ellipse(surf, cx, cyp - comal_r * 0.72,
                      comal_r * 0.44, comal_r * 0.42,
                      GOLD_CORE, MASA_GOLD, GOLD_SHEEN)
        # Husk ties on the dome.
        for k in (-1, 0, 1):
            pygame.draw.line(surf, BONE_SHADE,
                             (cx + k * comal_r * 0.22, cyp - comal_r * 0.95),
                             (cx + k * comal_r * 0.28, cyp - comal_r * 0.05),
                             max(1, int(SS * 0.9)))
        # A single chile-red garnish on the dome top (accent, on-axis).
        triad_ellipse(surf, cx, cyp - comal_r * 1.0,
                      comal_r * 0.14, comal_r * 0.22,
                      CHILE_CORE, CHILE, CHILE_SHEEN)

    grow_outline(surf, INK, 1)
    return pygame.transform.smoothscale(surf, (width, height))


# -- pure-black silhouette read (accessibility / outline test) ----------------

def draw_silhouette(target_size):
    """Flatten the creature to a pure-black mask -- proves the lead read survives
    in outline alone: bottom-heavy pear + open-cupboard ribcage gap + offered
    tamale hand asymmetry."""
    rgba = draw_comelona(target_size)
    sil = pygame.Surface((target_size, target_size), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(rgba)
    surf = mask.to_surface(setcolor=(18, 16, 18, 255), unsetcolor=(0, 0, 0, 0))
    sil.blit(surf, (0, 0))
    return sil


# -- sheet composition --------------------------------------------------------

def build_sheet():
    W, H = 1000, 720
    sheet = pygame.Surface((W, H))
    sheet.fill((46, 40, 50))   # warm-dark neutral review backdrop

    font = pygame.font.SysFont("arial", 18, bold=True)
    small = pygame.font.SysFont("arial", 13)

    def label(txt, x, y, col=(245, 238, 226)):
        sheet.blit(font.render(txt, True, col), (x, y))

    def caption(txt, x, y, col=(208, 200, 210)):
        sheet.blit(small.render(txt, True, col), (x, y))

    label("CALACA COMELONA — gluttonous Day-of-the-Dead street-food vendor  ·  round 1",
          18, 12, (250, 214, 130))
    caption("LEAD: EXPOSED ANATOMY — open ribcage-pantry stuffed with 3 food lobes "
            "· gold-led body, chile-red accent only", 18, 36)

    # Large creature.
    big = draw_comelona(300)
    sheet.blit(big, (24, 60))
    caption("creature · large (300px)", 24, 362)

    # Mid-scale legibility ramp.
    mid = draw_comelona(150)
    sheet.blit(mid, (350, 60))
    caption("creature · 150px", 350, 214)

    # 32px creature + 4x zoom.
    tiny = draw_comelona(32)
    sheet.blit(tiny, (350, 244))
    caption("32px", 350, 280)
    zoom = pygame.transform.scale(tiny, (128, 128))
    sheet.blit(zoom, (392, 244))
    caption("32px @4x", 392, 376)

    # Pure-black silhouette read.
    sil_big = draw_silhouette(150)
    sheet.blit(sil_big, (24, 408))
    caption("silhouette · 150px", 24, 560)
    sil_tiny = draw_silhouette(32)
    sil_zoom = pygame.transform.scale(sil_tiny, (128, 128))
    sheet.blit(sil_zoom, (188, 408))
    caption("silhouette 32px @4x", 188, 540)
    caption("read: bottom-heavy vendor, open belly", 188, 556)

    # Warm OCHRE-DAY-SKY verification — confirm the open-cage gap + food cluster
    # stay legible on a desert biome, not only on the dark review mat.
    tiny_w = draw_comelona(32)
    panel_x = 350
    sky_top, sky_bot = (236, 196, 120), (210, 158, 92)
    for yy in range(128):
        t = yy / 128.0
        col = tuple(int(sky_top[i] + (sky_bot[i] - sky_top[i]) * t) for i in range(3))
        pygame.draw.line(sheet, col, (panel_x, 408 + yy), (panel_x + 128, 408 + yy))
    pygame.draw.rect(sheet, (24, 20, 26), (panel_x, 408, 128, 128), 2)
    sheet.blit(pygame.transform.scale(tiny_w, (128, 128)), (panel_x, 408))
    caption("32px @4x on ochre day sky", panel_x, 540)
    caption("cage gap + food cluster legible", panel_x, 556)

    # Prop -> pillar mirror (market-pole ristra + comal cap).
    px = 580
    py = 60
    cap_h = 92
    shaft_h = 150
    big_w = 64
    bot_cap = draw_pillar(big_w, cap_h, top_cap=True)
    bot_shaft = draw_pillar(big_w, shaft_h, top_cap=False)
    top_cap = pygame.transform.flip(bot_cap, False, True)
    top_shaft = pygame.transform.flip(bot_shaft, False, True)

    gap = 64
    sheet.blit(top_shaft, (px, py))
    sheet.blit(top_cap, (px, py + shaft_h))
    gap_y = py + shaft_h + cap_h
    sheet.blit(bot_cap, (px, gap_y + gap))
    sheet.blit(bot_shaft, (px, gap_y + gap + cap_h))
    caption("prop->pillar mirror", px - 4, py + shaft_h * 2 + cap_h * 2 + gap + 6)
    caption("market pole + ristra · comal cap", px - 4, py + shaft_h * 2 + cap_h * 2 + gap + 22)

    # 32px pillar cap (judge the gap-edge read small).
    tcap = draw_pillar(28, 42, top_cap=True)
    sheet.blit(tcap, (px + 130, py + 20))
    czoom = pygame.transform.scale(tcap, (112, 168))
    sheet.blit(czoom, (px + 172, py + 20))
    caption("cap 28px / @4x", px + 130, py + 196)
    caption("comal cap ~shaft +35%", px + 130, py + 212)

    # Palette swatch strip.
    sw_y = H - 52
    swatches = [
        ("masa-gold", MASA_GOLD), ("ochre-hat", OCHRE_HAT), ("bone", BONE),
        ("tan-bone", BONE_SHADE), ("chile-red", CHILE), ("cilantro", CILANTRO),
        ("ink", INK), ("sheen", SHEEN),
    ]
    for i, (nm, col) in enumerate(swatches):
        sx = 430 + i * 70
        pygame.draw.rect(sheet, col, (sx, sw_y, 58, 28))
        pygame.draw.rect(sheet, (20, 18, 22), (sx, sw_y, 58, 28), 2)
        caption(nm, sx + 1, sw_y + 30)

    return sheet


if __name__ == "__main__":
    out = build_sheet()
    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(out, dst)
    print("wrote", dst)
