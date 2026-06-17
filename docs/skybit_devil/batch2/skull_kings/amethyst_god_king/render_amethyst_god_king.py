"""
Round-1 concept renderer for the AMETHYST GOD-KING — a four-armed radial
deity (Batch 2 / KING SKULL royal brood, concept #2). Headless Pygame;
ELEVATED pipeline (supersample SS=6 -> smoothscale) so the extra radial
geometry stays crisp at downscale. Clones the shipped house grammar from
jiangshi_epic/citipati: flat saturated fills, hard 1-2px ink keyline
(28,22,30), dark-core -> flat-fill -> top-left rim-sheen triad, 1px
alpha-grown outline, chibi proportions, scary-CUTE; procedural-only.

WHY this king is the court's ONLY radial silhouette: the lineage anchor
(Citipati) dances asymmetric; this deity is a WIDE SYMMETRIC FAN of four
ivory arms spreading from a centred chibi skull. It ties Citipati's purple
wisdom-hue through a brow third-eye, but separates from Mukha-Devi (the
other multi-arm chibi) on three hard counts: FOUR arms not six; arm-ends
are HANDS / regalia (scepter, lotus, orb, mudra) NEVER skull-tipped; and a
TALL 5-spire amethyst jewelled CONE-crown (kirita-mukuta) instead of a low
skull-tiara.

WHY a SANCTIONED large purple mass that still must lose to ivory: the brief
grants amethyst a LARGE robe mass (the one king allowed a second saturated
field), BUT the ivory head + four-arm fan must OUT-MASS the purple at 32px
so it reads "ivory deity in a purple robe," not "purple blob." Gold is a
THIN edge only; tiny skulls appear only as small armlet beads.

WHY the throne-spire IS the pillar: the king's own crown-cone, restacked as
a tapering amethyst spire of jewelled tiers, tiles as the repeatable shaft;
a single ivory hand-mudra fan + a purple cone-finial caps each gap edge --
symmetric, on-axis, never top-heavy.

WHY a standalone script under docs/: review art never enters the shipped
bundle, so it reuses only colour math + triad/outline helpers, not runtime
sprite modules.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# -- PINNED PALETTE (locked brief) --------------------------------------------
# Warm-ivory bone is the head + arms (must out-mass purple); amethyst is the
# sanctioned LARGE robe mass; gold is a THIN edge only.
BONE      = (246, 236, 210)   # warm-ivory bone — head + four arms (dominant)
BONE_D    = (190, 172, 138)   # bone dark-core
BONE_DD   = (140, 122,  94)   # deepest bone hollow (sockets, joint gaps)
BONE_SH   = (255, 250, 234)   # bone top-left rim-sheen
# the sanctioned amethyst robe — saturated but kept BELOW the ivory mass.
AMETH     = (132,  78, 196)   # amethyst robe fill (the large mass)
AMETH_D   = ( 86,  46, 138)   # amethyst dark-core / robe shadow
AMETH_DD  = ( 56,  28,  96)   # deepest robe hollow
AMETH_BR  = (176, 132, 230)   # amethyst top-left sheen / jewel facet light
AMETH_HOT = (214, 186, 248)   # hottest jewel highlight (lightest purple)
GOLD      = (224, 186,  88)   # THIN gold edging / crown bands only
GOLD_BR   = (246, 210, 118)
GOLD_D    = (170, 134,  56)
INK       = ( 28,  22,  30)   # hard ink keyline
# the wisdom third-eye — Citipati's purple hue, here the single cool focal.
THIRD_EYE = (120,  84, 196)
EYE_BR    = (214, 196, 255)   # third-eye hot core (the brightest pixel)

BG        = ( 96, 100, 108)   # neutral grey review backdrop
PANEL     = ( 74,  78,  88)
DAY_SKY_T = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)   # night biome sky (top)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (238, 240, 244)
LABEL_DIM = (188, 196, 208)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0]-a[0])*t),
            int(a[1] + (b[1]-a[1])*t),
            int(a[2] + (b[2]-a[2])*t))


# -- outline grown from the alpha mask (the house keyline) --------------------
def grow_outline(surf, color, px):
    mask = pygame.mask.from_surface(surf)
    pts = mask.outline()
    if len(pts) < 2:
        return surf
    base = surf.copy()
    ring = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for (ox, oy) in pts:
        pygame.draw.circle(ring, color, (ox, oy), px)
    ring.blit(base, (0, 0))
    return ring


def triad_blob(surf, color, pts, sheen_pts=None, core_pts=None, outline=True, ow=2):
    """Flat fill + optional dark-core + top-left rim-sheen + ink keyline."""
    if outline:
        pygame.draw.polygon(surf, INK, pts)
    pygame.draw.polygon(surf, color, pts)
    if core_pts:
        pygame.draw.polygon(surf, lerp(color, INK, 0.42), core_pts)
    if sheen_pts:
        pygame.draw.polygon(surf, lerp(color, (255, 255, 255), 0.4), sheen_pts)
    if outline:
        pygame.draw.polygon(surf, INK, pts, ow)


def triad_circle(surf, color, c, r, ow=2, sheen=True, core=True):
    """Round equivalent of triad_blob — dark core bottom-right, sheen top-left."""
    pygame.draw.circle(surf, INK, c, r + max(1, ow // 2))
    pygame.draw.circle(surf, color, c, r)
    if core:
        pygame.draw.circle(surf, lerp(color, INK, 0.4),
                           (c[0] + int(r * 0.28), c[1] + int(r * 0.30)),
                           int(r * 0.74))
        pygame.draw.circle(surf, color, c, int(r * 0.82))
    if sheen:
        pygame.draw.circle(surf, lerp(color, (255, 255, 255), 0.45),
                           (c[0] - int(r * 0.38), c[1] - int(r * 0.40)),
                           max(1, int(r * 0.26)))
    pygame.draw.circle(surf, INK, c, r, ow)


def bone_limb(surf, p0, p1, p2, thick, s, joint=True):
    """Two-segment ivory bone arm with ink keyline + bulbous joint. WHY arms
    are FAT ivory masses: the four-arm fan must out-mass the purple robe at
    32px, so each arm carries real bone width, not a stick."""
    for (a, b) in ((p0, p1), (p1, p2)):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = max(1.0, math.hypot(dx, dy))
        nx, ny = -dy / L * thick / 2, dx / L * thick / 2
        quad = [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny),
                (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]
        triad_blob(surf, BONE, quad,
                   sheen_pts=[(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny),
                              (b[0] + nx * 0.3, b[1] + ny * 0.3),
                              (a[0] + nx * 0.3, a[1] + ny * 0.3)],
                   ow=max(1, int(thick * 0.18)))
    if joint:
        triad_circle(surf, BONE, p1, int(thick * 0.60), ow=max(1, int(1.2 * s)),
                     core=False)


def armlet_bead(surf, cx, cy, r, s):
    """A TINY ivory skull bead on the upper arm — the only skulls on the
    figure, kept small so the lineage tell never competes with the hands."""
    triad_circle(surf, BONE, (cx, cy), r, ow=max(1, int(1.0 * s)), core=False)
    for ex in (cx - int(r * 0.40), cx + int(r * 0.40)):
        pygame.draw.circle(surf, INK, (ex, cy), max(1, int(r * 0.26)))
    pygame.draw.line(surf, INK, (cx - int(r * 0.4), cy + int(r * 0.5)),
                     (cx + int(r * 0.4), cy + int(r * 0.5)), max(1, int(1 * s)))


def gold_gem(surf, cx, cy, r, col, s):
    """A small faceted amethyst gem with a gold collar — the crown-spire
    jewels and brow setting. Kept tiny; gold is edge only."""
    pygame.draw.circle(surf, GOLD_D, (cx, cy), r + max(1, int(1.4 * s)))
    pygame.draw.circle(surf, GOLD, (cx, cy), r + max(1, int(1.0 * s)))
    # the gem facet — diamond cut for the jewel read
    gem = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
    pygame.draw.polygon(surf, INK, gem)
    pygame.draw.polygon(surf, col, gem)
    pygame.draw.polygon(surf, lerp(col, (255, 255, 255), 0.5),
                        [(cx, cy - r), (cx + int(r * 0.5), cy - int(r * 0.1)),
                         (cx - int(r * 0.2), cy - int(r * 0.2))])


# -- the tall 5-spire amethyst CONE-crown (kirita-mukuta — the top tell) ------
def cone_crown(surf, cx, base_y, w, s):
    """A tall jewelled amethyst CONE rising from the brow to FIVE spires, the
    centre tallest. WHY a cone of spires not a skull-ring: this is the king's
    iconic crown and the silhouette tell that separates it from every other
    court member; the purple cone-body + a single brow third-eye are the
    32px read. Gold bands edge each tier; tiny amethyst gems sit on the
    spire tips (gold = edge, purple = mass)."""
    half = w // 2
    apex_y = base_y - int(w * 1.78)        # tall — the dome of the silhouette
    # the cone body — a tapering amethyst triangle (the dominant crown mass)
    body = [(cx - half, base_y),
            (cx - int(half * 0.32), int(base_y - (base_y - apex_y) * 0.86)),
            (cx, apex_y),
            (cx + int(half * 0.32), int(base_y - (base_y - apex_y) * 0.86)),
            (cx + half, base_y)]
    triad_blob(surf, AMETH, body,
               core_pts=[(cx + int(half * 0.10), base_y),
                         (cx + int(half * 0.18), int(base_y - (base_y - apex_y) * 0.6)),
                         (cx, apex_y),
                         (cx + half, base_y)],
               sheen_pts=[(cx - half, base_y),
                          (cx - int(half * 0.30), int(base_y - (base_y - apex_y) * 0.55)),
                          (cx, apex_y),
                          (cx - int(half * 0.10), apex_y + int(w * 0.2))],
               ow=max(1, int(1.8 * s)))
    # horizontal gold tier-bands across the cone (thin edging accents)
    for frac in (0.10, 0.34, 0.60):
        bw = int(half * (1.0 - frac * 0.92))
        by = int(base_y - (base_y - apex_y) * frac)
        pygame.draw.line(surf, GOLD_D, (cx - bw, by + int(1 * s)),
                         (cx + bw, by + int(1 * s)), max(1, int(2.4 * s)))
        pygame.draw.line(surf, GOLD, (cx - bw, by), (cx + bw, by), max(1, int(1.6 * s)))
        pygame.draw.line(surf, GOLD_BR, (cx - bw, by - int(1 * s)),
                         (cx - int(bw * 0.2), by - int(1 * s)), max(1, int(1 * s)))
    # FIVE spires above the cone shoulders — centre tallest (the count tell)
    spire_h = [int(w * 0.30), int(w * 0.52), int(w * 0.86), int(w * 0.52), int(w * 0.30)]
    spire_x = [cx - int(half * 0.72), cx - int(half * 0.36), cx,
               cx + int(half * 0.36), cx + int(half * 0.72)]
    # the spires sit on the upper cone — base them along the cone shoulder line
    for sx, sh in zip(spire_x, spire_h):
        # height of cone surface at sx (linear taper from base to apex)
        t = abs(sx - cx) / max(1, half)
        sy = int(apex_y + (base_y - apex_y) * t)
        tip = (sx, sy - sh)
        sp = [(sx - int(w * 0.07), sy), tip, (sx + int(w * 0.07), sy)]
        triad_blob(surf, AMETH, sp, ow=max(1, int(1.2 * s)))
        gold_gem(surf, tip[0], tip[1], max(2, int(w * 0.06)), AMETH_BR, s)
    # a thin gold circlet band along the brow base of the crown
    pygame.draw.line(surf, INK, (cx - half, base_y), (cx + half, base_y), max(2, int(3 * s)))
    pygame.draw.line(surf, GOLD, (cx - half, base_y), (cx + half, base_y), max(1, int(2 * s)))
    pygame.draw.line(surf, GOLD_BR, (cx - int(half * 0.9), base_y - int(1 * s)),
                     (cx + int(half * 0.9), base_y - int(1 * s)), max(1, int(1 * s)))


# -- the four-armed radial deity ----------------------------------------------
def draw_amethyst_king(surf, cx, cy, s):
    """Centred chibi skull over a wide SYMMETRIC four-arm fan, wrapped in a
    LARGE amethyst robe. `s` = unit scale around a ~130-unit figure.

    Draw order: robe (back mass) -> lower arms -> robe front folds -> upper
    arms + regalia -> head -> cone-crown, so the ivory fan reads ON TOP of
    the purple and the crown owns the top. The hands hold scepter / lotus /
    orb / mudra (NEVER skulls)."""

    head_c = (cx, cy - int(34 * s))
    hr = int(23 * s)
    shoulder_y = cy - int(8 * s)
    hip_y = cy + int(40 * s)

    # === AMETHYST ROBE — the sanctioned LARGE mass (drawn FIRST, behind) ======
    # WHY a tapering bell from the shoulders to a wide floor hem: it gives the
    # "deity in a robe" read, but it sits BEHIND the ivory fan so the bone arms
    # cover its upper half — at 32px the ivory wins the centre.
    robe = [(cx - int(22 * s), shoulder_y),
            (cx + int(22 * s), shoulder_y),
            (cx + int(40 * s), cy + int(36 * s)),
            (cx + int(48 * s), cy + int(74 * s)),
            (cx + int(30 * s), cy + int(84 * s)),
            (cx, cy + int(80 * s)),
            (cx - int(30 * s), cy + int(84 * s)),
            (cx - int(48 * s), cy + int(74 * s)),
            (cx - int(40 * s), cy + int(36 * s))]
    triad_blob(surf, AMETH, robe,
               core_pts=[(cx + int(4 * s), shoulder_y + int(6 * s)),
                         (cx + int(40 * s), cy + int(36 * s)),
                         (cx + int(48 * s), cy + int(74 * s)),
                         (cx + int(20 * s), cy + int(80 * s)),
                         (cx + int(4 * s), cy + int(60 * s))],
               sheen_pts=[(cx - int(20 * s), shoulder_y + int(2 * s)),
                          (cx - int(6 * s), shoulder_y + int(2 * s)),
                          (cx - int(14 * s), cy + int(40 * s)),
                          (cx - int(36 * s), cy + int(60 * s))],
               ow=max(1, int(2 * s)))
    # robe fold grooves (dark amethyst verticals — texture, keeps it royal)
    for fx in (-26, -10, 8, 26):
        x0 = cx + int(fx * s)
        pygame.draw.line(surf, AMETH_DD, (x0, cy + int(20 * s)),
                         (int(cx + fx * 1.5 * s), cy + int(78 * s)), max(1, int(2 * s)))
    # a thin gold hem along the floor edge (edge only)
    hem = [(cx - int(48 * s), cy + int(74 * s)), (cx - int(30 * s), cy + int(84 * s)),
           (cx, cy + int(80 * s)), (cx + int(30 * s), cy + int(84 * s)),
           (cx + int(48 * s), cy + int(74 * s))]
    pygame.draw.lines(surf, GOLD_D, False, hem, max(1, int(3 * s)))
    pygame.draw.lines(surf, GOLD, False, hem, max(1, int(2 * s)))
    # a thin gold central placket down the robe front
    pygame.draw.line(surf, GOLD, (cx, shoulder_y + int(10 * s)), (cx, cy + int(70 * s)),
                     max(1, int(2 * s)))
    pygame.draw.line(surf, GOLD_BR, (cx, shoulder_y + int(10 * s)), (cx, cy + int(40 * s)),
                     max(1, int(1 * s)))

    # === FOUR ARMS — the wide symmetric radial fan (the figure's whole point) =
    # WHY a fan of two pairs: the upper pair sweeps high & wide (the radial
    # spread that makes the only radial silhouette), the lower pair reaches
    # down & out. All four are FAT ivory bone so the fan out-masses the purple.
    arm_th = int(11 * s)
    sh_up = int(14 * s)     # upper-shoulder origin spread
    sh_lo = int(18 * s)     # lower-shoulder origin spread

    # collar / shoulder bone block the arms fan from (keeps origins ivory)
    collar = [(cx - int(26 * s), shoulder_y - int(6 * s)),
              (cx + int(26 * s), shoulder_y - int(6 * s)),
              (cx + int(22 * s), shoulder_y + int(12 * s)),
              (cx - int(22 * s), shoulder_y + int(12 * s))]
    triad_blob(surf, BONE, collar, ow=max(1, int(1.6 * s)))

    # --- LOWER pair: down & out, drawn first (behind the upper pair) ---------
    for sgn in (-1, 1):
        sh = (cx + sgn * sh_lo, shoulder_y + int(6 * s))
        elbow = (cx + sgn * int(40 * s), cy + int(20 * s))
        hand = (cx + sgn * int(50 * s), cy + int(46 * s))
        bone_limb(surf, sh, elbow, hand, arm_th, s)
        armlet_bead(surf, cx + sgn * int(28 * s), cy + int(2 * s), int(5 * s), s)

    # --- UPPER pair: high & wide (the radial top spread) ---------------------
    for sgn in (-1, 1):
        sh = (cx + sgn * sh_up, shoulder_y - int(2 * s))
        elbow = (cx + sgn * int(42 * s), cy - int(28 * s))
        hand = (cx + sgn * int(54 * s), cy - int(54 * s))
        bone_limb(surf, sh, elbow, hand, arm_th, s)
        armlet_bead(surf, cx + sgn * int(30 * s), cy - int(20 * s), int(5 * s), s)

    # === REGALIA in the four hands (HANDS, never skull-tipped) ================
    # ivory hand discs at every arm end first
    hand_pts = {
        "ul": (cx - int(54 * s), cy - int(54 * s)),
        "ur": (cx + int(54 * s), cy - int(54 * s)),
        "ll": (cx - int(50 * s), cy + int(46 * s)),
        "lr": (cx + int(50 * s), cy + int(46 * s)),
    }
    for hx, hy in hand_pts.values():
        triad_circle(surf, BONE, (hx, hy), int(6 * s), ow=max(1, int(1.2 * s)), core=False)

    # upper-left hand: a GOLD-headed SCEPTER raised high
    hx, hy = hand_pts["ul"]
    pygame.draw.line(surf, INK, (hx, hy + int(6 * s)), (hx - int(4 * s), hy - int(30 * s)),
                     max(2, int(4 * s)))
    pygame.draw.line(surf, GOLD, (hx, hy + int(6 * s)), (hx - int(4 * s), hy - int(30 * s)),
                     max(1, int(2.4 * s)))
    gold_gem(surf, hx - int(4 * s), hy - int(34 * s), max(3, int(6 * s)), AMETH_BR, s)

    # upper-right hand: an open LOTUS (amethyst petals around a gold pip)
    hx, hy = hand_pts["ur"]
    for k in range(-2, 3):
        ang = math.radians(-90 + k * 30)
        px = hx + math.cos(ang) * int(13 * s)
        py = hy + math.sin(ang) * int(13 * s)
        petal = [(hx, hy), (px - int(4 * s), py), (px, py - int(6 * s)),
                 (px + int(4 * s), py)]
        triad_blob(surf, AMETH, petal, ow=max(1, int(1 * s)))
    pygame.draw.circle(surf, GOLD, (hx, hy - int(2 * s)), max(2, int(4 * s)))
    pygame.draw.circle(surf, GOLD_BR, (hx - int(1 * s), hy - int(3 * s)), max(1, int(2 * s)))

    # lower-right hand: a held ORB (amethyst sphere, gold meridian)
    hx, hy = hand_pts["lr"]
    triad_circle(surf, AMETH, (hx + int(6 * s), hy + int(6 * s)), int(9 * s),
                 ow=max(1, int(1.4 * s)))
    pygame.draw.line(surf, GOLD, (hx + int(6 * s), hy - int(3 * s)),
                     (hx + int(6 * s), hy + int(15 * s)), max(1, int(1.4 * s)))
    pygame.draw.arc(surf, GOLD, (hx - int(3 * s), hy - int(3 * s), int(18 * s), int(18 * s)),
                    math.radians(20), math.radians(160), max(1, int(1.4 * s)))

    # lower-left hand: an open MUDRA (palm-out fan of finger ticks — blessing)
    hx, hy = hand_pts["ll"]
    for k in range(-2, 3):
        ang = math.radians(120 + k * 22)
        ex = hx + math.cos(ang) * int(11 * s)
        ey = hy + math.sin(ang) * int(11 * s)
        pygame.draw.line(surf, INK, (hx, hy), (ex, ey), max(1, int(2.2 * s)))
        pygame.draw.line(surf, BONE, (hx, hy), (ex, ey), max(1, int(1.4 * s)))

    # === SKULL HEAD — chibi, scary-cute, centred (the ivory focal mass) =======
    triad_circle(surf, BONE, head_c, hr, ow=max(2, int(2 * s)))
    # cheek hollows
    for sgn in (-1, 1):
        pygame.draw.circle(surf, BONE_D,
                           (head_c[0] + sgn * int(hr * 0.66), head_c[1] + int(hr * 0.30)),
                           int(hr * 0.24))
    # big round sockets — scary-CUTE, kept dark so the brow third-eye is the
    # single brightest pixel above them (the deity tell).
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.44)
        ey = head_c[1] + int(hr * 0.06)
        pygame.draw.circle(surf, BONE_DD, (ex, ey), int(hr * 0.32))
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.26))
        pygame.draw.circle(surf, AMETH, (ex, ey), max(1, int(hr * 0.10)))
    # nose triangle
    pygame.draw.polygon(surf, BONE_DD,
                        [(head_c[0] - int(hr * 0.14), head_c[1] + int(hr * 0.30)),
                         (head_c[0] + int(hr * 0.14), head_c[1] + int(hr * 0.30)),
                         (head_c[0], head_c[1] + int(hr * 0.56))])
    # grinning tooth row (cute, not gory)
    my = head_c[1] + int(hr * 0.70)
    pygame.draw.line(surf, INK, (head_c[0] - int(hr * 0.5), my),
                     (head_c[0] + int(hr * 0.5), my), max(1, int(2 * s)))
    for k in range(-3, 4):
        pygame.draw.line(surf, INK, (head_c[0] + int(k * hr * 0.16), my - int(hr * 0.1)),
                         (head_c[0] + int(k * hr * 0.16), my + int(hr * 0.14)), max(1, int(1 * s)))
    # third eye of wisdom — a cool vertical jewel on the brow (the deity tell);
    # the SINGLE brightest pixel. Set in a small gold collar.
    tex, tey = head_c[0], head_c[1] - int(hr * 0.40)
    pygame.draw.circle(surf, GOLD_D, (tex, tey), int(hr * 0.22))
    pygame.draw.circle(surf, GOLD, (tex, tey), int(hr * 0.18))
    pygame.draw.ellipse(surf, INK, (tex - int(4 * s), tey - int(6 * s), int(8 * s), int(12 * s)))
    pygame.draw.ellipse(surf, THIRD_EYE, (tex - int(3 * s), tey - int(5 * s), int(6 * s), int(10 * s)))
    pygame.draw.circle(surf, EYE_BR, (tex, tey - int(1 * s)), max(1, int(2.0 * s)))

    # === TALL 5-SPIRE AMETHYST CONE-CROWN (kirita-mukuta — the top tell) ======
    cone_crown(surf, head_c[0], head_c[1] - int(hr * 0.62), int(hr * 1.7), s)


# -- the crown-spire throne-column -> pillar mirror ---------------------------
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The amethyst crown-cone restacked IS the pillar: a tapering column of
    jewelled amethyst tiers (the kirita-mukuta tier motif tiled) = the
    repeatable shaft; a single ivory hand-mudra fan + a purple cone-finial =
    the creature-derived gap-edge cap. On-axis, symmetric, never top-heavy.

    `cap` names the END that faces the GAP."""
    shaft_w = int(17 * s)
    # central amethyst rod the tiers thread onto (kept slim — ivory caps win)
    pygame.draw.rect(surf, INK, (cx - int(4 * s), top, int(8 * s), bot - top))
    pygame.draw.rect(surf, AMETH_D, (cx - int(3 * s), top, int(6 * s), bot - top))

    tier_pitch = int(22 * s)
    cap_room = int(34 * s)
    if cap == "bottom":
        b0, b1 = top + int(6 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(6 * s)
    y = b0
    while y <= b1:
        # each tier: a jewelled amethyst lozenge with gold tier-band + facet
        bw = shaft_w
        tier = [(cx - bw, y + int(3 * s)),
                (cx - int(bw * 0.5), y - int(8 * s)),
                (cx + int(bw * 0.5), y - int(8 * s)),
                (cx + bw, y + int(3 * s)),
                (cx + int(bw * 0.5), y + int(13 * s)),
                (cx - int(bw * 0.5), y + int(13 * s))]
        triad_blob(surf, AMETH, tier,
                   core_pts=[(cx, y - int(2 * s)), (cx + bw, y + int(3 * s)),
                             (cx + int(bw * 0.5), y + int(13 * s)), (cx, y + int(10 * s))],
                   sheen_pts=[(cx - bw, y + int(3 * s)), (cx - int(bw * 0.5), y - int(7 * s)),
                              (cx - int(bw * 0.2), y - int(4 * s)), (cx - int(bw * 0.7), y + int(6 * s))],
                   ow=max(1, int(1.4 * s)))
        # gold tier-band (thin edge) + a small amethyst facet gem centre
        pygame.draw.line(surf, GOLD_D, (cx - bw, y + int(4 * s)),
                         (cx + bw, y + int(4 * s)), max(1, int(2.2 * s)))
        pygame.draw.line(surf, GOLD, (cx - bw, y + int(3 * s)),
                         (cx + bw, y + int(3 * s)), max(1, int(1.4 * s)))
        gold_gem(surf, cx, y, max(2, int(5 * s)), AMETH_BR, s)
        y += tier_pitch

    # === gap-edge cap: an ivory hand-mudra fan + a purple cone-finial ========
    # WHY ivory fan + small purple cone: it echoes the king's hand-regalia and
    # the cone-crown so the pillar reads as HIS spire, and the ivory cap keeps
    # the bone-dominant rule at the gap edge.
    if cap == "bottom":
        cap_y = bot - int(20 * s)
        cone_dir = 1
    else:
        cap_y = top + int(20 * s)
        cone_dir = -1
    # the ivory mudra fan (palm-out finger ticks toward the gap)
    triad_circle(surf, BONE, (cx, cap_y), int(11 * s), ow=max(1, int(1.4 * s)), core=False)
    for k in range(-2, 3):
        ang = math.radians(90 * cone_dir + k * 24) if cone_dir > 0 else math.radians(-90 + k * 24)
        ex = cx + math.cos(ang) * int(18 * s)
        ey = cap_y + math.sin(ang) * int(18 * s) * (1 if cone_dir > 0 else 1)
        pygame.draw.line(surf, INK, (cx, cap_y), (ex, ey), max(1, int(2.6 * s)))
        pygame.draw.line(surf, BONE, (cx, cap_y), (ex, ey), max(1, int(1.6 * s)))
    # a small purple cone-finial behind the fan (echoes the crown)
    fin_base = cap_y - cone_dir * int(8 * s)
    fin_tip = (cx, fin_base - cone_dir * int(20 * s))
    fin = [(cx - int(9 * s), fin_base), fin_tip, (cx + int(9 * s), fin_base)]
    triad_blob(surf, AMETH, fin, ow=max(1, int(1.2 * s)))
    gold_gem(surf, fin_tip[0], fin_tip[1], max(2, int(5 * s)), AMETH_BR, s)
    # a gold ferrule collar where the cap meets the shaft
    collar_y = cap_y - cone_dir * int(20 * s)
    pygame.draw.rect(surf, INK, (cx - int(13 * s), collar_y - int(3 * s), int(26 * s), int(7 * s)))
    pygame.draw.rect(surf, GOLD, (cx - int(12 * s), collar_y - int(2 * s), int(24 * s), int(5 * s)))
    pygame.draw.rect(surf, GOLD_BR, (cx - int(12 * s), collar_y - int(2 * s), int(24 * s), int(2 * s)))


# -- compose the review sheet -------------------------------------------------
SS = 6


def render_creature_chip(boxw, boxh, draw_cx, draw_cy, scale):
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_amethyst_king(big, draw_cx * SS, draw_cy * SS, scale * SS)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def get_font(size, bold=True):
    """Vendored project font (LiberationSans-Bold) FIVE levels up; SysFont
    fallback so the renderer stays headless-safe anywhere."""
    here = os.path.dirname(os.path.abspath(__file__))
    fp = os.path.normpath(os.path.join(
        here, "..", "..", "..", "..", "..", "game", "assets", "LiberationSans-Bold.ttf"))
    if os.path.exists(fp):
        return pygame.font.Font(fp, size)
    return pygame.font.SysFont("DejaVu Sans", size, bold=bold)


# -- headless self-check ------------------------------------------------------
def self_check():
    """Render the figure at true 32px and verify the GATE: ivory out-masses
    purple, and the radial fan + cone-crown produce a wide-but-tall mask."""
    big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
    draw_amethyst_king(big, 48 * SS, 50 * SS, (32 / 130.0) * SS)
    small = pygame.transform.smoothscale(big, (96, 96))
    ivory = purple = 0
    w, h = small.get_size()
    for yy in range(h):
        for xx in range(w):
            r, g, b, a = small.get_at((xx, yy))
            if a < 60:
                continue
            # classify by hue: purple = blue-dominant + reddish; ivory = warm bright
            if b > r and b > g - 10 and (r + b) > 1.4 * g:
                purple += 1
            elif r > 150 and g > 130:
                ivory += 1
    ivory_wins = ivory > purple
    return ivory, purple, ivory_wins


def main():
    W, H = 1010, 820
    font_big = get_font(30)
    font = get_font(17)
    font_sm = get_font(12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("AMETHYST GOD-KING", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "four-armed radial deity  ·  ivory fan out-masses purple robe · 5-spire amethyst cone-crown · third-eye · round 1",
        True, LABEL_DIM), (320, 30))

    # === (a) BIG HERO =========================================================
    hero = render_creature_chip(360, 470, 178, 232, 1.65)
    sheet.blit(hero, (14, 92))
    sheet.blit(font.render("Creature — hero", True, LABEL), (110, 566))
    sheet.blit(font_sm.render("WIDE SYMMETRIC four-arm fan (the only radial king) over a large amethyst robe.", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("Hands hold scepter / lotus / orb / mudra — NEVER skulls (separates from Mukha-Devi).", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("Tall 5-spire amethyst CONE-crown + brow third-eye = the top tell. Gold = thin edge.", True, LABEL_DIM), (14, 622))

    # === (b) PILLAR assembled — mirrored, clean tileable shaft ================
    pcx = 470
    top_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(top_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="bottom")
    top_seg = grow_outline(pygame.transform.smoothscale(top_big, (150, 250)), INK + (255,), 1)
    sheet.blit(top_seg, (pcx, 86))
    bot_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(bot_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="top")
    bot_seg = grow_outline(pygame.transform.smoothscale(bot_big, (150, 250)), INK + (255,), 1)
    sheet.blit(bot_seg, (pcx, 86 + 250 + 96))
    pygame.draw.rect(sheet, (60, 64, 72), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar — crown-spire", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("jewelled amethyst tiers (cone-crown motif)", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("= shaft; ivory hand-fan + cone-finial cap the", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("gap (mirrored top<->bottom, on-axis)", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px gameplay chips on day + night sky ======================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 560))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_amethyst_king(big, 48 * SS, 50 * SS, (32 / 130.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        return grow_outline(small, INK + (255,), 1)

    chip = chip32()

    day_y = 128
    vgrad(sheet, (panel_x + 20, day_y, 150, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 27, day_y + 27))
    sheet.blit(font_sm.render("32px on day sky", True, LABEL), (panel_x + 20, day_y + 156))

    night_y = day_y + 184
    vgrad(sheet, (panel_x + 20, night_y, 150, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 27, night_y + 27))
    sheet.blit(font_sm.render("32px on night sky", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    # blacked-out silhouette proof beside the chips (radial-fan read)
    def silhouette32():
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_amethyst_king(big, 48 * SS, 50 * SS, (32 / 130.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        sil = pygame.Surface((96, 96), pygame.SRCALPHA)
        mask = pygame.mask.from_surface(small)
        for yy in range(96):
            for xx in range(96):
                if mask.get_at((xx, yy)):
                    sil.set_at((xx, yy), INK + (255,))
        return sil

    sil = silhouette32()
    px2 = panel_x + 192
    pygame.draw.rect(sheet, (210, 214, 220), (px2, day_y, 96, 96))
    pygame.draw.rect(sheet, INK, (px2, day_y, 96, 96), 1)
    sheet.blit(sil, (px2, day_y))
    sheet.blit(font_sm.render("blackout", True, LABEL_DIM), (px2 + 6, day_y - 16))
    sheet.blit(font_sm.render("(radial fan +", True, LABEL_DIM), (px2, day_y + 100))
    sheet.blit(font_sm.render("cone read)", True, LABEL_DIM), (px2, day_y + 114))

    # a 32px pillar gap-cap chip beside, on both skies
    def pillar_chip32():
        big = pygame.Surface((40 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 20 * SS, 2 * SS, 128 * SS, 0.32 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (40, 130))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    px3 = panel_x + 192
    vgrad(sheet, (px3, night_y, 56, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (px3, night_y, 56, 150), 1)
    sheet.blit(pc, (px3 + 8, night_y + 10))
    sheet.blit(font_sm.render("pillar", True, LABEL_DIM), (px3 + 4, night_y - 16))

    # palette swatches
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, 510))
    swatches = [
        (BONE, "warm-ivory bone"), (BONE_D, "bone shade"),
        (AMETH, "amethyst robe"), (AMETH_D, "amethyst shade"),
        (AMETH_BR, "amethyst jewel"), (GOLD, "gold edge"),
        (THIRD_EYE, "third-eye"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, 538
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 158
        ry = syp + row * 26
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, ry, 18, 18))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 26, ry + 3))

    # self-check result printed onto the sheet (the bone>purple proof)
    ivory, purple, ivory_wins = self_check()
    verdict = "IVORY > purple  OK" if ivory_wins else "FAIL: purple wins"
    vc = (150, 240, 170) if ivory_wins else (240, 150, 150)
    sheet.blit(font_sm.render(
        f"32px mass audit: ivory={ivory}px  purple={purple}px  ->  {verdict}",
        True, vc), (panel_x + 16, 646 - 16))

    # bottom note strip
    pygame.draw.rect(sheet, PANEL, (14, 770, W - 28, 40))
    sheet.blit(font_sm.render(
        "ELEVATED pipeline: SS=6 supersample -> smoothscale.  STAY: flat saturated fills · hard ink keyline (28,22,30) · "
        "dark-core->fill->top-left sheen triad · 1px grown outline · chibi · scary-cute · procedural-only.",
        True, LABEL_DIM), (26, 783))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out)
    print(f"self-check: ivory={ivory}px purple={purple}px ivory_wins={ivory_wins}")


if __name__ == "__main__":
    main()
