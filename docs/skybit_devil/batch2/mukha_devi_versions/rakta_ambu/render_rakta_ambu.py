"""
Round-1 concept renderer for RAKTA-AMBU — coral-tree dendritic bone-canopy
(Mukha-Devi brood spin-off, concept #4). Headless Pygame; ELEVATED pipeline
(supersample SS=6 -> smoothscale) so the forked canopy + tip relics + tiny
encrusted skulls stay crisp at downscale. Keeps the shipped house grammar:
flat saturated fills, hard 1-2px ink keyline (28,22,26), dark-core -> flat-fill
-> top-left rim-sheen triad, 1px alpha-grown outline, chibi, scary-CUTE;
procedural-only.

WHY this is the forked-tree-canopy KIND (the ONLY ORGANIC silhouette in the
brood): Rakta-Ambu goes MID-TALL -> MONUMENTAL by spreading WIDE, not tall.
EIGHT bone arms leave a low shoulder line and immediately FORK — each splits
into two, and those two split again — into a knobbly spreading coral
tree-crown. So her blackout is NOT discrete radiating limbs (that is Mukha's
open starburst) but one organic branching CANOPY: a dendritic blob whose
outer edge is lumpy with coral-polyp cups. Recursion is hard-capped at TWO
fork levels so at 32px the OUTER canopy silhouette carries the read, never
interior tracery turning to noise.

WHY briny-indigo bone with a small coral-pink HEART, not white: the cross-set
pin bans Yurei cyan and Mukha hot magenta. The bone mass is pushed clearly
toward briny INDIGO-blue (dominant), and the single warm focal is a DULL
SALMON-CORAL heart-glow — a small warm core in a cold body, so it reads
unmistakably as a deep-reef thing, never a bright magenta deity.

WHY the coral-reef bone-trunk IS the pillar: a knobbly branching bone-trunk
rooted at the bottom (the root system roots it -> no taper risk) hung with
coral-polyp cups and conch relics as the tileable shaft; the gap-cap is a
small forked coral-frond crown with a glowing coral heart at the fork — the
creature's own dendritic language, on-axis.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it reuses only colour math + the triad/outline helpers, not runtime
sprite modules.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# -- PINNED PALETTE (locked brief) --------------------------------------------
# Briny INDIGO-blue is the dominant bone mass (anti-Yurei: darker, never cyan).
# The single warm focal is a DULL SALMON-CORAL heart (anti-Mukha: never hot
# magenta) -- a small warm core, indigo dominant.
BONE      = ( 54,  86, 140)   # briny indigo-blue bone (the dominant fill)
BONE_D    = ( 36,  58,  98)   # deep-indigo dark-core / shade
BONE_DD   = ( 22,  38,  70)   # deepest indigo hollow (sockets, fork grooves)
BONE_SH   = (118, 152, 202)   # cool indigo top-left rim-sheen
CORAL     = (214, 118, 110)   # dull salmon-coral HEART glow (small warm focal)
CORAL_BR  = (244, 168, 156)   # lit coral inner / sheen
CORAL_D   = (150,  72,  72)   # deep coral shade
CONCH     = (220, 196, 170)   # pale conch-relic bone (a warm-neutral relic note)
CONCH_BR  = (244, 230, 210)
CONCH_D   = (158, 132, 108)
SKULL     = (206, 214, 232)   # tiny encrusted skull (pale cold bone, reads dead-on-indigo)
SKULL_D   = (132, 146, 178)
INK       = ( 28,  22,  26)   # hard ink keyline
HEART     = (214, 118, 110)   # heart-glow (same coral so it reads as her warm core)
HEART_BR  = (250, 196, 178)

BG        = ( 96,  92, 100)   # neutral grey review backdrop
PANEL     = ( 74,  72,  84)
DAY_SKY_T = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)   # night biome sky (top)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (240, 236, 240)
LABEL_DIM = (196, 190, 202)


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
    """Round equivalent of triad_blob -- dark core bottom-right, sheen top-left."""
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


def tapered_limb(surf, p, q, w0, w1, color, ow):
    """A knobbly bone branch segment that TAPERS from w0 (base) to w1 (tip).
    WHY tapered, not parallel-sided: a coral branch thins as it forks, so the
    canopy edge reads organic/dendritic instead of a bundle of even sticks."""
    dx, dy = q[0] - p[0], q[1] - p[1]
    L = max(1.0, math.hypot(dx, dy))
    nx, ny = -dy / L, dx / L
    quad = [(p[0] + nx * w0 / 2, p[1] + ny * w0 / 2),
            (q[0] + nx * w1 / 2, q[1] + ny * w1 / 2),
            (q[0] - nx * w1 / 2, q[1] - ny * w1 / 2),
            (p[0] - nx * w0 / 2, p[1] - ny * w0 / 2)]
    # top-left edge catches the sheen
    sheen = [(p[0] + nx * w0 / 2, p[1] + ny * w0 / 2),
             (q[0] + nx * w1 / 2, q[1] + ny * w1 / 2),
             (q[0] + nx * w1 * 0.18, q[1] + ny * w1 * 0.18),
             (p[0] + nx * w0 * 0.18, p[1] + ny * w0 * 0.18)]
    triad_blob(surf, color, quad, sheen_pts=sheen, ow=ow)


# -- a tiny encrusted skull (the surviving arm-end-skull DNA) ------------------
def tiny_skull(surf, cx, cy, r, s, lit=False):
    """Tiny pale skull ENCRUSTED into a lower fork -- death-as-growth. WHY pale
    cold bone (not indigo): it must punch a clean dead-white dot with two
    sockets against the dark indigo canopy at 32px, so the 'skulls in the
    branches' tell survives the shrink."""
    triad_circle(surf, SKULL, (cx, cy), r, ow=max(1, int(1.2 * s)), core=False)
    jaw = [(cx - int(r * 0.5), cy + int(r * 0.45)),
           (cx + int(r * 0.5), cy + int(r * 0.45)),
           (cx + int(r * 0.30), cy + int(r * 0.92)),
           (cx - int(r * 0.30), cy + int(r * 0.92))]
    triad_blob(surf, SKULL, jaw, ow=max(1, int(1.0 * s)))
    for ex in (cx - int(r * 0.36), cx + int(r * 0.36)):
        pygame.draw.circle(surf, INK, (ex, cy), max(1, int(r * 0.26)))
        if lit:
            pygame.draw.circle(surf, CORAL_BR, (ex, cy), max(1, int(r * 0.12)))
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.40)), max(1, int(r * 0.12)))


# -- the tip ornaments: coral-polyp cups + conch relics ------------------------
def polyp_cup(surf, cx, cy, r, s, ang):
    """A coral-POLYP cup at a canopy tip -- a knobbly indigo cup cradling a small
    dull-coral heart. WHY a cup w/ a coral dot: the brief's tip ornament; the
    coral heart is a tiny warm note so the canopy edge twinkles warm-on-cold
    without ever becoming a magenta fringe."""
    triad_circle(surf, BONE, (cx, cy), int(r * 1.0), ow=max(1, int(1.3 * s)), core=False)
    # the open cup mouth (a dark crescent so it reads as a polyp cup, not a knob)
    pygame.draw.arc(surf, BONE_DD,
                    (cx - int(r * 0.78), cy - int(r * 0.86), int(r * 1.56), int(r * 1.5)),
                    math.radians(200), math.radians(340), max(2, int(2.0 * s)))
    # three tiny coral tentacle-nubs around the rim
    for k in (-1, 0, 1):
        a = math.radians(-90 + k * 34)
        tx = cx + math.cos(a) * r * 0.7
        ty = cy + math.sin(a) * r * 0.7 - int(r * 0.1)
        pygame.draw.circle(surf, INK, (int(tx), int(ty)), max(1, int(r * 0.22)))
        pygame.draw.circle(surf, CORAL, (int(tx), int(ty)), max(1, int(r * 0.16)))
    # the coral heart in the cup
    pygame.draw.circle(surf, CORAL, (cx, cy - int(r * 0.06)), max(1, int(r * 0.36)))
    pygame.draw.circle(surf, CORAL_BR, (cx - int(r * 0.12), cy - int(r * 0.2)),
                       max(1, int(r * 0.18)))


def conch_relic(surf, cx, cy, r, s):
    """A spiralled conch relic at a canopy tip (a held relic, the surviving
    arm-end-ornament DNA). WHY pale conch-bone + a coral aperture: a warm-neutral
    relic mass that reads as a distinct ornament chunk vs the polyp cups, with a
    small coral mouth tying it to the heart palette."""
    body = [(cx - int(r * 0.9), cy + int(r * 0.2)),
            (cx - int(r * 0.3), cy - int(r * 0.95)),
            (cx + int(r * 0.5), cy - int(r * 0.6)),
            (cx + int(r * 0.95), cy + int(r * 0.35)),
            (cx + int(r * 0.3), cy + int(r * 0.95)),
            (cx - int(r * 0.55), cy + int(r * 0.75))]
    triad_blob(surf, CONCH, body,
               core_pts=[(cx, cy - int(r * 0.2)), (cx + int(r * 0.7), cy + int(r * 0.1)),
                         (cx + int(r * 0.2), cy + int(r * 0.7)), (cx - int(r * 0.1), cy + int(r * 0.2))],
               sheen_pts=[(cx - int(r * 0.3), cy - int(r * 0.85)),
                          (cx + int(r * 0.2), cy - int(r * 0.5)),
                          (cx - int(r * 0.1), cy - int(r * 0.1)),
                          (cx - int(r * 0.6), cy - int(r * 0.1))],
               ow=max(1, int(1.3 * s)))
    # spiral whorl grooves
    pygame.draw.arc(surf, CONCH_D, (cx - int(r * 0.55), cy - int(r * 0.5),
                    int(r * 1.0), int(r * 1.0)), math.radians(20), math.radians(300), max(1, int(1.6 * s)))
    # coral aperture mouth at the lip
    pygame.draw.circle(surf, CORAL, (cx + int(r * 0.45), cy + int(r * 0.45)), max(1, int(r * 0.26)))
    pygame.draw.circle(surf, CORAL_BR, (cx + int(r * 0.4), cy + int(r * 0.38)), max(1, int(r * 0.12)))


# -- the FORKED dendritic canopy (the KIND tell) -------------------------------
def draw_canopy(surf, ox, oy, s, span, levels=2):
    """EIGHT arms leave a low shoulder line and FORK into a spreading coral
    tree-crown. WHY a hard-capped binary fractal: each of 8 base arms splits
    into 2, and (level 2) each of those splits again -> a knobbly branching
    canopy whose OUTER edge is lumpy with polyp cups, NOT discrete radiating
    spokes. Recursion is capped at TWO levels (the 32px rule) so the silhouette
    stays a readable organic blob, never interior noise. Returns lists of tip
    centres (with type) and lower-fork centres for skull encrusting."""
    tips = []        # (x, y, type, ang) -- canopy edge ornaments
    lower_forks = [] # (x, y) -- where to encrust tiny skulls (death-as-growth)

    # eight base arms span a wide low arc -- WIDE, not tall (monumental-by-width)
    base_w = int(20 * s)
    base_count = 8
    # arms aim across the upper hemisphere but lean OUTWARD (spreading canopy),
    # the outermost near-horizontal so the blackout is wider than tall.
    spread_deg = [-150, -120, -96, -74, -106, -84, -60, -30]
    # symmetric, ordered so lowest/outermost draw first (upper overlaps cleanly)
    angles = [-150, -116, -84, -52, -128, -100, -64, -30]
    angles = sorted(angles, key=lambda a: -abs(a - (-90)))

    def grow(px, py, ang, length, width, depth):
        # the branch segment to its fork
        ex = px + math.cos(math.radians(ang)) * length
        ey = py + math.sin(math.radians(ang)) * length
        tip_w = width * 0.62
        tapered_limb(surf, (px, py), (ex, ey), width, tip_w, BONE,
                     ow=max(1, int(width * 0.14)))
        # a knobbly node at the fork joint
        triad_circle(surf, BONE, (int(ex), int(ey)), int(tip_w * 0.62),
                     ow=max(1, int(1.1 * s)), core=False)
        if depth >= levels:
            # a leaf TIP: ornament alternates polyp-cup / conch relic
            tips.append((int(ex), int(ey), depth % 1, ang, tip_w))
            return
        # record the LOWER forks (depth-1 joints in the bottom half) for skulls
        if ang > -90 - 46 and ang < -90 + 46 and depth == 1:
            pass  # central upper forks stay clean
        if depth == 1:
            lower_forks.append((int(ex), int(ey)))
        # FORK INTO TWO -- the dendritic split
        split = 34 - depth * 6
        # branches lean outward from vertical so the crown SPREADS
        outward = 1 if ang <= -90 else -1
        for d in (-split, split):
            child_ang = ang + d + outward * 8
            grow(ex, ey, child_ang, length * 0.74, tip_w, depth + 1)

    arm_len = span * 0.5
    for a in angles:
        sx = ox + (1 if a > -90 else -1) * int(6 * s)
        grow(sx, oy, a, arm_len, base_w, 1)

    return tips, lower_forks


# -- the coral-tree bone-canopy creature ---------------------------------------
def draw_rakta_ambu(surf, cx, cy, s):
    """Coral-reef death-mother: a chibi indigo-bone skull-trunk crowned by a
    WIDE forked dendritic canopy that spreads sideways (monumental-by-width).
    Tips bear polyp cups + conch relics; tiny pale skulls are encrusted into
    the lower forks; a low skull-crown + a dull-coral heart keep the FACE and
    warm focal reading inside the cold canopy. `s` = unit scale (~150-unit fig)."""

    head_c = (cx, cy - int(14 * s))
    hr = int(28 * s)

    # === FORKED CANOPY (drawn first -> branches sit BEHIND the head) ==========
    # WHY origin at a LOW shoulder line + a WIDE span: the canopy must SPREAD,
    # bracketing the head sideways, leaving open sky directly above the crown so
    # the skull-tiara reads -- and so the blackout is wider than tall.
    canopy_span = int(150 * s)
    tips, lower_forks = draw_canopy(surf, head_c[0], head_c[1] + int(hr * 0.55),
                                    s, canopy_span, levels=2)

    # === TIP ORNAMENTS -- polyp cups + conch relics around the canopy edge ====
    # WHY alternating by horizontal position (not draw order): a regular cup /
    # conch rhythm reads along the lumpy edge so it is clearly "ornamented
    # canopy," and the warm coral dots twinkle along the rim without a fringe.
    tips_sorted = sorted(tips, key=lambda t: t[0])
    orn_r = int(7 * s)
    for i, (tx, ty, _, ang, tw) in enumerate(tips_sorted):
        if i % 3 == 1:
            conch_relic(surf, tx, ty - int(orn_r * 0.2), orn_r, s)
        else:
            polyp_cup(surf, tx, ty, orn_r, s, ang)

    # === LOWER BODY -- a wide squat reef-foot (mass low, spreading) ===========
    base_y = cy + int(40 * s)
    base = [(cx - int(38 * s), base_y - int(6 * s)),
            (cx - int(26 * s), base_y - int(16 * s)),
            (cx + int(26 * s), base_y - int(16 * s)),
            (cx + int(38 * s), base_y - int(6 * s)),
            (cx + int(30 * s), base_y + int(12 * s)),
            (cx - int(30 * s), base_y + int(12 * s))]
    triad_blob(surf, BONE, base,
               core_pts=[(cx, base_y - int(14 * s)), (cx + int(32 * s), base_y - int(6 * s)),
                         (cx + int(24 * s), base_y + int(10 * s)), (cx, base_y + int(7 * s))],
               ow=max(1, int(1.6 * s)))
    # knobbly reef-foot bumps (organic, not petals)
    for k in range(-3, 4):
        px = cx + int(k * 10 * s)
        pygame.draw.circle(surf, BONE_DD, (px, base_y + int(11 * s)), max(1, int(3 * s)))
        pygame.draw.circle(surf, BONE, (px - int(1 * s), base_y + int(10 * s)), max(1, int(2 * s)))

    # === TORSO -- a short coral-rib trunk (squat; head + canopy hold mass) ====
    rc_cx, rc_cy = cx, cy + int(14 * s)
    rc_w, rc_h = int(30 * s), int(26 * s)
    cage = [(rc_cx - rc_w // 2, rc_cy - rc_h // 2 + int(2 * s)),
            (rc_cx + rc_w // 2, rc_cy - rc_h // 2),
            (rc_cx + int(rc_w * 0.42), rc_cy + rc_h // 2),
            (rc_cx - int(rc_w * 0.42), rc_cy + rc_h // 2)]
    triad_blob(surf, BONE, cage,
               core_pts=[(rc_cx + int(2 * s), rc_cy - rc_h // 2 + int(3 * s)),
                         (rc_cx + rc_w // 2, rc_cy - rc_h // 2 + int(2 * s)),
                         (rc_cx + int(rc_w * 0.42), rc_cy + rc_h // 2),
                         (rc_cx + int(2 * s), rc_cy + rc_h // 2)],
               sheen_pts=[(rc_cx - rc_w // 2 + int(2 * s), rc_cy - rc_h // 2 + int(3 * s)),
                          (rc_cx - int(4 * s), rc_cy - rc_h // 2 + int(2 * s)),
                          (rc_cx - int(6 * s), rc_cy + int(4 * s)),
                          (rc_cx - rc_w // 2 + int(2 * s), rc_cy + int(2 * s))],
               ow=max(1, int(1.8 * s)))
    # coral-rib bands (knobbly, reef-textured)
    for i in range(2):
        ry = rc_cy - rc_h // 2 + int(8 * s) + i * int(9 * s)
        bw = int(rc_w * (0.42 - i * 0.05))
        pygame.draw.arc(surf, BONE_DD,
                        (rc_cx - bw, ry - int(6 * s), bw * 2, int(14 * s)),
                        math.radians(205), math.radians(335), max(2, int(2.2 * s)))
    pygame.draw.line(surf, BONE_DD, (rc_cx, rc_cy - rc_h // 2 + int(6 * s)),
                     (rc_cx, rc_cy + int(4 * s)), max(1, int(2 * s)))

    # === CORAL HEART -- the single warm focal, set in the chest =============
    # WHY a dull-coral heart-glow on the sternum, kept WARMER+SMALLER than any
    # canopy dot: indigo dominant, this is the small warm core that says "living
    # reef" -- a dull salmon-coral, demonstrably NOT Mukha hot magenta.
    hxy = (rc_cx, rc_cy - int(1 * s))
    pygame.draw.circle(surf, INK, hxy, int(7 * s))
    pygame.draw.circle(surf, CORAL_D, hxy, int(6 * s))
    pygame.draw.circle(surf, CORAL, hxy, int(4 * s))
    pygame.draw.circle(surf, CORAL_BR, (hxy[0] - int(1 * s), hxy[1] - int(1 * s)), max(1, int(2 * s)))

    # === TINY ENCRUSTED SKULLS in the LOWER forks (death-as-growth) ==========
    # WHY in the LOWER forks specifically (per the brief): the bottom of the
    # canopy near the shoulders, so the pale skulls read as growth-encrusted
    # joints framing the head, not scattered over the crown.
    fl = sorted(lower_forks, key=lambda f: f[0])
    skull_r = int(5.2 * s)
    lit_idx = len(fl) // 2
    for i, (fx, fy) in enumerate(fl):
        tiny_skull(surf, fx, fy + int(2 * s), skull_r, s, lit=(i == lit_idx))

    # === SKULL HEAD -- chibi, scary-cute, coral-eyed (the framed FACE) ========
    triad_circle(surf, BONE, head_c, hr, ow=max(2, int(2 * s)))
    for sgn in (-1, 1):   # cheek hollows
        pygame.draw.circle(surf, BONE_D,
                           (head_c[0] + sgn * int(hr * 0.66), head_c[1] + int(hr * 0.30)),
                           int(hr * 0.24))
    # two big sockets -- dark hollows with small deep-coral pins (scary-CUTE),
    # kept a notch dimmer than the chest heart so the heart stays warm focal.
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.40)
        ey = head_c[1] + int(hr * 0.06)
        pygame.draw.circle(surf, BONE_DD, (ex, ey), int(hr * 0.32))
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.26))
        pygame.draw.circle(surf, CORAL, (ex + sgn * int(1 * s), ey + int(1 * s)),
                           int(hr * 0.13))
        pygame.draw.circle(surf, CORAL_BR, (ex, ey - int(1 * s)), max(1, int(hr * 0.06)))
    # nose triangle
    pygame.draw.polygon(surf, BONE_DD,
                        [(head_c[0] - int(hr * 0.13), head_c[1] + int(hr * 0.34)),
                         (head_c[0] + int(hr * 0.13), head_c[1] + int(hr * 0.34)),
                         (head_c[0], head_c[1] + int(hr * 0.58))])
    # grinning tooth row (cute, not gory)
    my = head_c[1] + int(hr * 0.74)
    pygame.draw.line(surf, INK, (head_c[0] - int(hr * 0.46), my),
                     (head_c[0] + int(hr * 0.46), my), max(1, int(2 * s)))
    for k in range(-3, 4):
        pygame.draw.line(surf, INK, (head_c[0] + int(k * hr * 0.14), my - int(hr * 0.1)),
                         (head_c[0] + int(k * hr * 0.14), my + int(hr * 0.12)), max(1, int(1 * s)))

    # === LOW SKULL-CROWN / coral-tiara (the preserved crown DNA) ==============
    # WHY a shallow band of THREE tiny skulls seated in the open sky above the
    # crown: keeps Mukha's skull-tiara DNA, lower/fewer, and the central one is
    # the lit-coral focal echoing the chest heart so the warm read stays paired.
    tiara_r = int(hr * 0.98)
    band_pts = []
    for i in range(9):
        a = math.radians(238 + i * (64 / 8))
        band_pts.append((head_c[0] + math.cos(a) * tiara_r,
                         head_c[1] + math.sin(a) * tiara_r))
    pygame.draw.lines(surf, INK, False, band_pts, int(5 * s))
    pygame.draw.lines(surf, CORAL, False, band_pts, int(2 * s))
    for i in range(3):
        a = math.radians(244 + i * (52 / 2))
        sx = head_c[0] + math.cos(a) * tiara_r
        sy = head_c[1] + math.sin(a) * tiara_r
        tiny_skull(surf, int(sx), int(sy), int(hr * 0.26), s, lit=(i == 1))


# -- the coral-reef bone-trunk -> pillar mirror --------------------------------
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The coral-reef bone-TRUNK is the pillar: a knobbly branching bone-trunk
    hung with coral-polyp cups + conch relics = the tileable shaft; the gap-cap
    is a small FORKED coral-frond crown with a glowing coral heart at the fork --
    the creature's own dendritic language, on-axis. Bottom-rooted (the root
    system roots it, so there is no taper risk).

    `cap` names the END that faces the GAP."""
    trunk_w = int(15 * s)
    relic_r = int(6 * s)
    pygame.draw.rect(surf, INK, (cx - int(3 * s), top, int(6 * s), bot - top))

    band_pitch = int(24 * s)
    cap_room = int(38 * s)
    root_room = int(20 * s)
    if cap == "bottom":
        b0, b1 = top + int(6 * s), bot - cap_room
        root_y = bot
    else:
        b0, b1 = top + cap_room, bot - int(6 * s)
        root_y = top

    # === knobbly branching bone-trunk + relic side-branches ===================
    y = b0
    idx = 0
    while y <= b1:
        bw = trunk_w + int(math.sin(idx * 1.3) * 2 * s)  # knobbly width wobble
        band = [(cx - bw, y - int(9 * s)),
                (cx + bw, y - int(9 * s)),
                (cx + bw, y + int(9 * s)),
                (cx - bw, y + int(9 * s))]
        triad_blob(surf, BONE, band,
                   core_pts=[(cx, y - int(8 * s)), (cx + bw, y - int(8 * s)),
                             (cx + bw, y + int(8 * s)), (cx, y + int(8 * s))],
                   sheen_pts=[(cx - bw, y - int(8 * s)), (cx - int(bw * 0.3), y - int(8 * s)),
                              (cx - int(bw * 0.3), y + int(2 * s)), (cx - bw, y + int(2 * s))],
                   ow=max(1, int(1.4 * s)))
        # a forked node groove (so the shaft reads coral-knobbly, not a column)
        pygame.draw.arc(surf, BONE_DD, (cx - bw, y - int(8 * s), bw * 2, int(16 * s)),
                        math.radians(200), math.radians(340), max(1, int(1.6 * s)))
        # a relic side-branch off alternating sides (cup / conch alternation)
        side = -1 if (idx % 2 == 0) else 1
        bx = cx + side * (bw + int(2 * s))
        rx = cx + side * (bw + int(11 * s))
        ry = y - int(3 * s)
        tapered_limb(surf, (bx, y), (rx, ry), int(5 * s), int(3 * s), BONE, ow=max(1, int(1.0 * s)))
        if idx % 2 == 0:
            polyp_cup(surf, rx, ry, relic_r, s, math.radians(-90))
        else:
            conch_relic(surf, rx, ry, relic_r, s)
        # tiny encrusted skull on a lower-third joint
        if (idx % 3 == 2):
            tiny_skull(surf, cx, y + int(7 * s), int(4 * s), s, lit=False)
        idx += 1
        y += band_pitch

    # === bottom root flare (the trunk roots it) ==============================
    rgrow = +1 if cap == "bottom" else -1
    ry0 = root_y - rgrow * int(2 * s)
    for d in (-1, 0, 1):
        rxt = cx + d * int(16 * s)
        ryt = ry0 + rgrow * int(16 * s)
        tapered_limb(surf, (cx, ry0), (rxt, ryt), int(8 * s), int(3 * s), BONE,
                     ow=max(1, int(1.2 * s)))

    # === gap-edge cap: forked coral-frond crown + glowing coral heart ========
    cap_y = (bot - int(22 * s)) if cap == "bottom" else (top + int(22 * s))
    grow = +1 if cap == "bottom" else -1   # the fronds fork toward the gap
    # a small two-level fork-burst mirroring the canopy in miniature
    fr = int(15 * s)
    for k in (-1, 1):
        base_a = math.radians(-90 + k * 18) if grow > 0 else math.radians(90 + k * 18)
        jx = cx + math.cos(base_a) * fr * 0.6
        jy = cap_y + math.sin(base_a) * fr * 0.6
        tapered_limb(surf, (cx, cap_y), (jx, jy), int(7 * s), int(4 * s), BONE,
                     ow=max(1, int(1.2 * s)))
        for d in (-22, 22):
            ca = base_a + math.radians(d)
            tx = jx + math.cos(ca) * fr * 0.6
            ty = jy + math.sin(ca) * fr * 0.6
            tapered_limb(surf, (jx, jy), (tx, ty), int(4 * s), int(2 * s), BONE,
                         ow=max(1, int(1.0 * s)))
            polyp_cup(surf, int(tx), int(ty), int(4 * s), s, ca)
    # a thin coral collar where the fronds meet the trunk
    collar_y = cap_y - grow * int(fr + int(3 * s))
    pygame.draw.rect(surf, INK, (cx - int(10 * s), collar_y - int(3 * s), int(20 * s), int(7 * s)))
    pygame.draw.rect(surf, CORAL_D, (cx - int(9 * s), collar_y - int(2 * s), int(18 * s), int(5 * s)))
    pygame.draw.rect(surf, CORAL, (cx - int(9 * s), collar_y - int(2 * s), int(18 * s), int(2 * s)))
    # the glowing coral HEART at the fork hub (the gap glow)
    triad_circle(surf, BONE, (cx, cap_y), int(7 * s), ow=max(1, int(1.4 * s)), core=False)
    pygame.draw.circle(surf, CORAL_D, (cx, cap_y), int(5 * s))
    pygame.draw.circle(surf, CORAL, (cx, cap_y), int(3 * s))
    pygame.draw.circle(surf, CORAL_BR, (cx - int(1 * s), cap_y - int(1 * s)), max(1, int(1.6 * s)))


# -- compose the review sheet --------------------------------------------------
SS = 6


def font_at(size):
    path = "/home/user/skybit/game/assets/LiberationSans-Bold.ttf"
    return pygame.font.Font(path, size)


def render_creature_chip(boxw, boxh, draw_cx, draw_cy, scale):
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_rakta_ambu(big, draw_cx * SS, draw_cy * SS, scale * SS)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def silhouette_of(boxw, boxh, draw_cx, draw_cy, scale):
    """A blacked-out silhouette proof: render, then recolour every opaque pixel
    to ink so we can judge the canopy READ as a solid organic branching blob."""
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_rakta_ambu(big, draw_cx * SS, draw_cy * SS, scale * SS)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    sil = pygame.Surface((boxw, boxh), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(small, 40)
    for yy in range(boxh):
        for xx in range(boxw):
            if mask.get_at((xx, yy)):
                sil.set_at((xx, yy), (18, 14, 18, 255))
    return sil


def main():
    W, H = 1040, 840
    font_big = font_at(30)
    font = font_at(17)
    font_sm = font_at(12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("RAKTA-AMBU", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "coral-tree dendritic bone-canopy  ·  KIND: forked tree-canopy · mid-tall -> MONUMENTAL via WIDTH · briny-indigo + coral HEART · round 1",
        True, LABEL_DIM), (250, 26))

    # === (1) EPIC HERO ========================================================
    hero = render_creature_chip(380, 470, 190, 230, 1.55)
    sheet.blit(hero, (14, 84))
    sheet.blit(font.render("Creature — EPIC hero", True, LABEL), (120, 558))
    sheet.blit(font_sm.render("EIGHT arms FORK twice into a WIDE spreading coral tree-crown (cap 2 fork levels).", True, LABEL_DIM), (14, 584))
    sheet.blit(font_sm.render("Tips = polyp cups + conch relics; TINY pale skulls encrusted into the LOWER forks.", True, LABEL_DIM), (14, 600))
    sheet.blit(font_sm.render("Indigo bone dominant; dull-coral chest HEART = the small warm focal (anti-magenta).", True, LABEL_DIM), (14, 616))
    sheet.blit(font_sm.render("Low 3-skull coral-crown in open sky over the head (preserved tiara DNA).", True, LABEL_DIM), (14, 632))

    # === (2) PILLAR -- bottom-rooted, mirrored top<->bottom ===================
    pcx = 470
    top_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(top_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="bottom")
    top_seg = grow_outline(pygame.transform.smoothscale(top_big, (150, 250)), INK + (255,), 1)
    sheet.blit(top_seg, (pcx, 80))
    bot_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(bot_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="top")
    bot_seg = grow_outline(pygame.transform.smoothscale(bot_big, (150, 250)), INK + (255,), 1)
    sheet.blit(bot_seg, (pcx, 80 + 250 + 92))
    pygame.draw.rect(sheet, (60, 58, 70), (pcx + 8, 80 + 250, 134, 92))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 80 + 250 + 38))
    sheet.blit(font.render("Pillar — coral-reef trunk", True, LABEL), (pcx - 4, 680))
    sheet.blit(font_sm.render("knobbly branching bone-trunk hung with", True, LABEL_DIM), (pcx - 4, 704))
    sheet.blit(font_sm.render("cup/conch relics = shaft; root-flare bottom-", True, LABEL_DIM), (pcx - 4, 720))
    sheet.blit(font_sm.render("roots it; forked coral-frond + heart caps gap", True, LABEL_DIM), (pcx - 4, 736))

    # === (3) TRUE 32px chips on day + night sky ===============================
    panel_x = 662
    pygame.draw.rect(sheet, PANEL, (panel_x, 80, W - panel_x - 14, 300))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 14, 88))

    def chip32():
        big = pygame.Surface((118 * SS, 118 * SS), pygame.SRCALPHA)
        draw_rakta_ambu(big, 59 * SS, 64 * SS, (32 / 150.0) * SS)
        small = pygame.transform.smoothscale(big, (118, 118))
        return grow_outline(small, INK + (255,), 1)

    chip = chip32()
    day_y = 116
    vgrad(sheet, (panel_x + 16, day_y, 150, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 16, day_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 16 + 16, day_y + 16))
    sheet.blit(font_sm.render("32px DAY", True, LABEL), (panel_x + 16, day_y + 154))

    px2 = panel_x + 180
    vgrad(sheet, (px2, day_y, 150, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (px2, day_y, 150, 150), 1)
    sheet.blit(chip, (px2 + 16, day_y + 16))
    sheet.blit(font_sm.render("32px NIGHT", True, LABEL_DIM), (px2, day_y + 154))

    # 32px pillar chips on both skies
    def pillar_chip32():
        big = pygame.Surface((52 * SS, 150 * SS), pygame.SRCALPHA)
        draw_pillar(big, 26 * SS, 2 * SS, 148 * SS, 0.32 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (52, 150))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    pcy = day_y + 178
    vgrad(sheet, (panel_x + 16, pcy, 60, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 16, pcy, 60, 150), 1)
    sheet.blit(pc, (panel_x + 16 + 4, pcy))
    vgrad(sheet, (panel_x + 86, pcy, 60, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 86, pcy, 60, 150), 1)
    sheet.blit(pc, (panel_x + 86 + 4, pcy))
    sheet.blit(font_sm.render("32px pillar (day / night)", True, LABEL_DIM), (panel_x + 16, pcy + 152))

    # === (4) BLACKED-OUT SILHOUETTE PROOF =====================================
    sil_panel_y = 392
    pygame.draw.rect(sheet, (150, 150, 158), (panel_x, sil_panel_y, W - panel_x - 14, 196))
    sheet.blit(font.render("Blackout silhouette proof", True, (40, 38, 44)), (panel_x + 14, sil_panel_y + 6))
    sil_big = silhouette_of(150, 160, 75, 92, (150 / 150.0))
    sheet.blit(sil_big, (panel_x + 16, sil_panel_y + 28))
    sil_sm = silhouette_of(64, 64, 32, 34, (32 / 150.0))
    sheet.blit(pygame.transform.scale(sil_sm, (96, 96)), (panel_x + 196, sil_panel_y + 30))
    sheet.blit(font_sm.render("hero", True, (40, 38, 44)), (panel_x + 60, sil_panel_y + 172))
    sheet.blit(font_sm.render("32px (x3)", True, (40, 38, 44)), (panel_x + 210, sil_panel_y + 128))

    # === (5) PALETTE STRIP ====================================================
    pal_y = 600
    pygame.draw.rect(sheet, PANEL, (14, pal_y, W - 28, 60))
    sheet.blit(font.render("Pinned palette", True, LABEL), (24, pal_y + 6))
    swatches = [
        (BONE, "briny-indigo bone"), (BONE_D, "indigo shade"),
        (BONE_DD, "indigo hollow"), (CORAL, "coral HEART"),
        (CORAL_D, "deep coral"), (CONCH, "conch relic"),
        (SKULL, "encrusted skull"), (INK, "ink keyline"),
    ]
    sxp, syp = 24, pal_y + 30
    for i, (c, name) in enumerate(swatches):
        rx = sxp + i * 126
        pygame.draw.rect(sheet, INK, (rx - 1, syp - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, syp, 18, 18))
        sheet.blit(font_sm.render(name, True, LABEL), (rx, syp + 22))

    # footer
    pygame.draw.rect(sheet, PANEL, (14, H - 56, W - 28, 42))
    sheet.blit(font_sm.render(
        "ELEVATED pipeline: SS=6 supersample -> smoothscale.  STAY: flat triad fills · hard ink keyline (28,22,26) · "
        "dark-core->fill->top-left sheen · 1px grown outline · chibi · scary-cute · procedural-only.",
        True, LABEL_DIM), (26, H - 44))
    sheet.blit(font_sm.render(
        "Silhouette tell: an ORGANIC knobbly BRANCHING canopy (forked, spreading) — not discrete radiating limbs (anti-Mukha starburst).",
        True, LABEL_DIM), (26, H - 28))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
