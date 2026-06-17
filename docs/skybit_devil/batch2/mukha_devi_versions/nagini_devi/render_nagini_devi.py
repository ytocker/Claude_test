"""
Round-1 concept renderer for NAGINI-DEVI — the serpent-hood-ring bone-naga-queen
(Mukha-Devi brood, concept #2). Headless Pygame; ELEVATED pipeline (supersample
SS=5-6 -> smoothscale) so the ring of reared hood-lobes + tiny in-jaw skulls stay
crisp at downscale. Keeps the shipped house grammar: flat saturated fills, hard
1-2px ink keyline (28,22,26), dark-core -> flat-fill -> top-left rim-sheen triad,
1px alpha-grown outline, chibi/scary-CUTE; procedural-only.

WHY this is the arms-as-snakes hood-RING KIND (the deliberate ANTITHESIS of
Mukha-Devi's straight radial spokes): six arms do NOT splay as clean rays — each
ends in a FAT reared cobra-HOOD, and the six hoods crowd around the skull as a
LUMPY LATERAL RING of bulbous blobs. The blackout read is a head ringed by
S-curved hood-lobes with clear negative gaps between them, never a starburst.
The DNA of the brood survives intact: six arms + a skull-crown tiara + arm-end
ornaments carrying TINY SKULLS (here the skulls sit in alternating hood-jaws).

WHY duller, greener-bronze, NOT teal-grown-up: the cross-set pin demands this
split from Nagaraja's bright emerald (72,196,142) AND from Mukha-Devi's clean
teal (64,170,166). So the verdigris-teal is desaturated and the AGED-BRONZE is
the DOMINANT mass — it must read as a tarnished bronze naga-queen, not "Mukha's
teal grown up." Teal is the cool patina shading; bronze owns the silhouette.

WHY the caduceus twin-snake staff IS the pillar: two bone-snakes wind up a
central bronze rod and rear into facing hoods at the cap — the creature's own
serpent language, bottom-rooted, tiling as the repeatable shaft.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it reuses only colour math + the triad/outline helpers, not runtime
sprite modules.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# ── PINNED PALETTE (locked brief) ─────────────────────────────────────────────
# Aged-bronze is the DOMINANT mass; verdigris-teal is the cool patina shading.
# Both are deliberately DULLER + GREENER-BRONZE than the siblings so this reads
# as a tarnished naga-queen, not Nagaraja emerald and not Mukha teal.
BONE      = (220, 206, 184)   # warm bone-core (skull, snake bellies)
BONE_D    = (158, 142, 116)   # bone dark-core / shade
BONE_DD   = (104,  90,  70)   # deepest bone hollow (sockets, jaw gaps)
BONE_SH   = (244, 236, 218)   # bone top-left rim-sheen
BRONZE    = (150, 110,  62)   # aged-bronze — the DOMINANT accent mass
BRONZE_BR = (196, 152,  92)   # bronze top-left sheen
BRONZE_D  = ( 98,  70,  40)   # deep-bronze shade / core
TEAL      = ( 78, 150, 128)   # verdigris-teal — DULL + green-leaning patina
TEAL_BR   = (128, 192, 168)   # teal patina sheen
TEAL_D    = ( 46,  96,  82)   # deep verdigris shade
EYE       = ( 96, 210, 168)   # cool serpent-eye glow (verdigris, the focal hue)
EYE_BR    = (188, 246, 214)   # hot eye core
INK       = ( 28,  22,  26)   # hard ink keyline

BG        = ( 92,  96,  88)   # neutral green-grey review backdrop
PANEL     = ( 70,  76,  68)
DAY_SKY_T = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)   # night biome sky (top)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (240, 240, 234)
LABEL_DIM = (196, 200, 188)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0]-a[0])*t),
            int(a[1] + (b[1]-a[1])*t),
            int(a[2] + (b[2]-a[2])*t))


# ── outline grown from the alpha mask (the house keyline) ────────────────────
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


def thick_path(surf, color, pts, w, ow):
    """A fat tapering-free polyline rendered as a filled ribbon with ink keyline
    — used for the S-curved snake arms so each arm is a single chunky bone limb,
    not a thin line that smears at 32px."""
    if len(pts) < 2:
        return
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        if i == 0:
            dx, dy = pts[1][0] - x, pts[1][1] - y
        elif i == len(pts) - 1:
            dx, dy = x - pts[-2][0], y - pts[-2][1]
        else:
            dx, dy = pts[i + 1][0] - pts[i - 1][0], pts[i + 1][1] - pts[i - 1][1]
        L = max(1.0, math.hypot(dx, dy))
        nx, ny = -dy / L * w / 2, dx / L * w / 2
        left.append((x + nx, y + ny))
        right.append((x - nx, y - ny))
    poly = left + right[::-1]
    pygame.draw.polygon(surf, INK, poly)
    pygame.draw.polygon(surf, color, poly)
    # a thin top-left belly sheen along the leading edge (the inner half-ribbon)
    inner = [(0.62 * lp[0] + 0.38 * pts[k][0], 0.62 * lp[1] + 0.38 * pts[k][1])
             for k, lp in enumerate(left)]
    pygame.draw.polygon(surf, lerp(color, (255, 255, 255), 0.3), left + inner[::-1])
    pygame.draw.polygon(surf, INK, poly, ow)


# ── ONE reared cobra-hood (the arm-end ornament — replaces Mukha's hands) ─────
def cobra_hood(surf, cx, cy, r, s, ang, with_skull, lit=False):
    """A FAT reared cobra-hood: a bulbous flared bronze hood-flap with a small
    bone snake-head at its centre, a bronze hood-RING + skull-boss, and (on
    alternating hoods) a TINY SKULL set in the open jaw. WHY fat + bulbous: the
    silhouette tell is a RING OF DISCRETE LOBES — each hood must blackout as one
    chunky blob with a clear gap to its neighbour, the antithesis of a spoke.
    `ang` orients the hood so it rears OUTWARD from the skull. The brood's
    arm-end-ornament-with-tiny-skull DNA lives here."""
    ca, sa = math.cos(ang), math.sin(ang)
    # perpendicular axis for the lateral hood-flare
    px, py = -sa, ca

    # the flared HOOD-FLAP — a wide rounded shield (the bulbous lobe)
    flap = []
    for t in (-1.0, -0.62, 0.0, 0.62, 1.0):
        # widen at the shoulders, round the top
        wide = r * (1.55 - abs(t) * 0.35)
        reach = r * (1.0 + (1.0 - abs(t)) * 0.45)
        flap.append((cx + px * wide * t + ca * reach,
                     cy + py * wide * t + sa * reach))
    # base of the flap nearer the arm
    flap.append((cx + px * r * 0.6 - ca * r * 0.2,
                 cy + py * r * 0.6 - sa * r * 0.2))
    flap.append((cx - px * r * 0.6 - ca * r * 0.2,
                 cy - py * r * 0.6 - sa * r * 0.2))
    triad_blob(surf, BRONZE, flap,
               core_pts=[(cx + ca * r * 0.7, cy + sa * r * 0.7),
                         (cx + px * r * 0.9 + ca * r * 0.3, cy + py * r * 0.9 + sa * r * 0.3),
                         (cx + px * r * 0.5 + ca * r * 1.2, cy + py * r * 0.5 + sa * r * 1.2),
                         (cx - px * r * 0.2 + ca * r * 1.1, cy - py * r * 0.2 + sa * r * 1.1)],
               ow=max(1, int(1.6 * s)))
    # verdigris patina pooling at the hood crown (the cool shading note)
    crown = (cx + ca * r * 1.15, cy + sa * r * 1.15)
    pygame.draw.circle(surf, TEAL_D, (int(crown[0]), int(crown[1])), int(r * 0.5))
    pygame.draw.circle(surf, TEAL, (int(crown[0] - ca * r * 0.1), int(crown[1] - sa * r * 0.1)),
                       int(r * 0.34))

    # bronze hood-RING with a skull-boss at the hood throat (DNA: ring + skull)
    ring_c = (cx + ca * r * 0.42, cy + sa * r * 0.42)
    triad_circle(surf, BRONZE, (int(ring_c[0]), int(ring_c[1])), int(r * 0.46),
                 ow=max(1, int(1.4 * s)), core=False, sheen=False)
    triad_circle(surf, BRONZE_D, (int(ring_c[0]), int(ring_c[1])), int(r * 0.28),
                 ow=max(1, int(1 * s)), core=False, sheen=False)
    # the small bone snake-head poking through the ring (the "hand" replacement)
    snake_c = (cx + ca * r * 0.7, cy + sa * r * 0.7)
    triad_circle(surf, BONE, (int(snake_c[0]), int(snake_c[1])), int(r * 0.42),
                 ow=max(1, int(1.4 * s)), core=False)
    # snub snout
    snout = [(snake_c[0] + ca * r * 0.7, snake_c[1] + sa * r * 0.7),
             (snake_c[0] + px * r * 0.3 + ca * r * 0.3, snake_c[1] + py * r * 0.3 + sa * r * 0.3),
             (snake_c[0] - px * r * 0.3 + ca * r * 0.3, snake_c[1] - py * r * 0.3 + sa * r * 0.3)]
    triad_blob(surf, BONE, snout, ow=max(1, int(1 * s)))

    if with_skull:
        # a TINY SKULL set in the open jaw (alternating hoods only) — the brood's
        # arm-end-skull DNA. Sits just inside the snout so it reads as "in jaw."
        sk = (snake_c[0] + ca * r * 0.5, snake_c[1] + sa * r * 0.5)
        skr = int(r * 0.3)
        triad_circle(surf, BONE_SH, (int(sk[0]), int(sk[1])), skr,
                     ow=max(1, int(1 * s)), core=False, sheen=False)
        for off in (-0.34, 0.34):
            pygame.draw.circle(surf, INK,
                               (int(sk[0] + px * skr * off), int(sk[1] + py * skr * off)),
                               max(1, int(skr * 0.3)))
    else:
        # serpent eyes (verdigris) on the snake-head when no skull rides the jaw
        for off in (-0.42, 0.42):
            ex = snake_c[0] + px * r * 0.22 * (off / 0.42) - ca * r * 0.05
            ey = snake_c[1] + py * r * 0.22 * (off / 0.42) - sa * r * 0.05
            pygame.draw.circle(surf, INK, (int(ex), int(ey)), max(1, int(r * 0.12)))
            ec = EYE_BR if lit else EYE
            pygame.draw.circle(surf, ec, (int(ex), int(ey)), max(1, int(r * 0.07)))


# ── a single ornamental tiara-skull (the preserved skull-crown DNA) ───────────
def tiara_skull(surf, cx, cy, r, s, lit=False):
    """Tiny bone skull for the skull-crown tiara — the brood's preserved
    skull-crown DNA. A domed cranium + jaw with two dark sockets; centre skull
    lit verdigris so the crown carries a cool focal note distinct from siblings."""
    triad_circle(surf, BONE, (cx, cy), r, ow=max(1, int(1.4 * s)), core=False)
    jaw = [(cx - int(r * 0.5), cy + int(r * 0.5)),
           (cx + int(r * 0.5), cy + int(r * 0.5)),
           (cx + int(r * 0.32), cy + int(r * 0.94)),
           (cx - int(r * 0.32), cy + int(r * 0.94))]
    triad_blob(surf, BONE, jaw, ow=max(1, int(1.1 * s)))
    eye_c = EYE_BR if lit else INK
    for ex in (cx - int(r * 0.38), cx + int(r * 0.38)):
        pygame.draw.circle(surf, INK, (ex, cy + int(r * 0.02)), max(1, int(r * 0.26)))
        if lit:
            pygame.draw.circle(surf, eye_c, (ex, cy + int(r * 0.02)), max(1, int(r * 0.14)))
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.42)), max(1, int(r * 0.14)))


# ── the six-arm SERPENT hood-ring (the KIND tell) ─────────────────────────────
def draw_hood_ring(surf, sh_cx, sh_cy, s, hr, hood_r):
    """Six bone-snake arms wind out from a low shoulder line and each REARS into
    a fat cobra-hood, the six hoods crowding around the skull as a lumpy lateral
    RING. WHY S-curved arms but FAT discrete hoods: the writhing arms give the
    organic naga read, but the SILHOUETTE must survive at 32px as a ring of
    separate bulbous lobes with negative GAPS between — so the hoods are fat and
    the ring angles are spaced to keep a clear gap between adjacent hoods. The
    ring deliberately reaches AROUND and slightly OVER the head (not capped by a
    straight spoke), the antithesis of Mukha's open radial fan. Returns the six
    (hood-centre, outward-angle) for skull placement, with which hoods carry a
    jaw-skull (alternating)."""
    shoulder = (sh_cx, sh_cy)
    arm_len = int(hr * 1.7)
    arm_th = int(11 * s)
    # six hoods spaced AROUND the head: two low, two mid-lateral, two upper —
    # angles chosen so adjacent hoods leave a clear negative gap (not even spokes).
    ring_deg = [-150, -108, -54, 54, 108, 150]  # measured from +x, screen space
    hoods = []
    for k, d in enumerate(ring_deg):
        a = math.radians(d)
        sgn = -1 if d < 0 else 1
        sh = (shoulder[0] + sgn * int(hr * 0.5), shoulder[1] + int(hr * 0.1))
        # an S-curve: bow the arm outward then curl the hood up/around
        ex = sh[0] + math.cos(a) * arm_len * 0.95
        ey = sh[1] + math.sin(a) * arm_len * 0.95
        mid1 = (sh[0] + math.cos(a) * arm_len * 0.38 - sgn * hr * 0.18,
                sh[1] + math.sin(a) * arm_len * 0.38 + hr * 0.12)
        mid2 = (sh[0] + math.cos(a) * arm_len * 0.72 + sgn * hr * 0.16,
                sh[1] + math.sin(a) * arm_len * 0.72 - hr * 0.05)
        hood_c = (ex, ey)
        thick_path(surf, BONE, [sh, mid1, mid2, hood_c], arm_th, max(1, int(arm_th * 0.16)))
        # bone scale-segment dots along the arm (cute serpent texture)
        for t in (0.4, 0.62, 0.82):
            sx = sh[0] + (hood_c[0] - sh[0]) * t
            sy = sh[1] + (hood_c[1] - sh[1]) * t
            pygame.draw.circle(surf, BONE_DD, (int(sx), int(sy)), max(1, int(arm_th * 0.18)))
        # the hood rears OUTWARD along the arm direction
        hoods.append((hood_c, a, k % 2 == 0))
    # draw hoods AFTER all arms so the bulbous lobes sit on top, clean ring read
    return hoods, hood_r


# ── the bone-naga-queen ───────────────────────────────────────────────────────
def draw_nagini_devi(surf, cx, cy, s):
    """Mid-proportioned naga death-queen: a chibi three-eyed skull ringed by six
    reared cobra-hoods on bone-snake arms, crowned with a skull-tiara, rooted on
    a coiled-serpent base. `s` = unit scale around a ~140-unit figure."""

    # WHY a big chibi head: like the brood Original, at 32px the ring of hoods
    # will crowd the skull, so the FACE must be the dominant mass to win the read.
    head_c = (cx, cy - int(20 * s))
    hr = int(30 * s)
    hood_r = int(13 * s)

    # === SIX SERPENT-ARM HOODS (arms drawn behind; hoods drawn after) =========
    hoods, hr_hood = draw_hood_ring(surf, head_c[0], head_c[1] + int(hr * 0.9), s, hr, hood_r)

    # === LOWER BODY — a coiled-serpent base (keeps mass low, roots the figure) =
    base_y = cy + int(46 * s)
    # a fat coil loop reading as the naga's lower body
    coil = [(cx - int(36 * s), base_y - int(6 * s)),
            (cx - int(30 * s), base_y - int(18 * s)),
            (cx + int(30 * s), base_y - int(18 * s)),
            (cx + int(36 * s), base_y - int(6 * s)),
            (cx + int(28 * s), base_y + int(12 * s)),
            (cx - int(28 * s), base_y + int(12 * s))]
    triad_blob(surf, BRONZE, coil,
               core_pts=[(cx, base_y - int(16 * s)), (cx + int(30 * s), base_y - int(6 * s)),
                         (cx + int(22 * s), base_y + int(10 * s)), (cx, base_y + int(8 * s))],
               sheen_pts=[(cx - int(30 * s), base_y - int(16 * s)), (cx - int(6 * s), base_y - int(17 * s)),
                          (cx - int(10 * s), base_y - int(2 * s)), (cx - int(30 * s), base_y - int(4 * s))],
               ow=max(1, int(1.6 * s)))
    # coil scale-bands (verdigris grooves so the base reads as a snake body)
    for k in range(-2, 3):
        px = cx + int(k * 12 * s)
        pygame.draw.line(surf, TEAL_D, (px, base_y - int(18 * s)),
                         (px, base_y + int(10 * s)), max(1, int(1.6 * s)))
    # a verdigris belly-stone at the coil heart — kept DEEPER than the third eye
    # so it stays a SECONDARY focal (Mukha's belly-gem note, learned from AD).
    pygame.draw.circle(surf, TEAL_D, (cx, base_y - int(3 * s)), int(5 * s))
    pygame.draw.circle(surf, TEAL, (cx - int(1 * s), base_y - int(4 * s)), max(1, int(2 * s)))

    # === TORSO — a short bronze rib barrel (squat, head + base hold the mass) ==
    rc_cx, rc_cy = cx, cy + int(14 * s)
    rc_w, rc_h = int(32 * s), int(24 * s)
    cage = [(rc_cx - rc_w // 2, rc_cy - rc_h // 2 + int(2 * s)),
            (rc_cx + rc_w // 2, rc_cy - rc_h // 2),
            (rc_cx + int(rc_w * 0.42), rc_cy + rc_h // 2),
            (rc_cx - int(rc_w * 0.42), rc_cy + rc_h // 2)]
    triad_blob(surf, BRONZE, cage,
               core_pts=[(rc_cx + int(2 * s), rc_cy - rc_h // 2 + int(3 * s)),
                         (rc_cx + rc_w // 2, rc_cy - rc_h // 2 + int(2 * s)),
                         (rc_cx + int(rc_w * 0.42), rc_cy + rc_h // 2),
                         (rc_cx + int(2 * s), rc_cy + rc_h // 2)],
               sheen_pts=[(rc_cx - rc_w // 2 + int(2 * s), rc_cy - rc_h // 2 + int(3 * s)),
                          (rc_cx - int(4 * s), rc_cy - rc_h // 2 + int(2 * s)),
                          (rc_cx - int(6 * s), rc_cy + int(4 * s)),
                          (rc_cx - rc_w // 2 + int(2 * s), rc_cy + int(2 * s))],
               ow=max(1, int(1.8 * s)))
    # bone rib bands over the bronze (bone-core showing through tarnish)
    for i in range(2):
        ry = rc_cy - rc_h // 2 + int(7 * s) + i * int(8 * s)
        bw = int(rc_w * (0.42 - i * 0.05))
        pygame.draw.arc(surf, BONE,
                        (rc_cx - bw, ry - int(6 * s), bw * 2, int(14 * s)),
                        math.radians(205), math.radians(335), max(2, int(2.2 * s)))
    pygame.draw.line(surf, BRONZE_D, (rc_cx, rc_cy - rc_h // 2 + int(5 * s)),
                     (rc_cx, rc_cy + int(3 * s)), max(1, int(2 * s)))
    # a thin verdigris sash (linear accent, never a mass)
    pygame.draw.line(surf, TEAL, (rc_cx - int(rc_w * 0.42), rc_cy + int(2 * s)),
                     (rc_cx + int(rc_w * 0.42), rc_cy - int(2 * s)), max(1, int(2 * s)))

    # === SIX COBRA-HOODS — the ring of bulbous lobes (drawn over torso) ========
    # WHY after torso, before head: hoods crowd around and slightly over the
    # skull so the RING reads, but the big head still overdraws the inner edges.
    for (hood_c, a, with_skull) in hoods:
        cobra_hood(surf, int(hood_c[0]), int(hood_c[1]), hr_hood, s, a,
                   with_skull, lit=False)

    # === SKULL HEAD — chibi, scary-cute, three-eyed (the framed FACE) =========
    triad_circle(surf, BONE, head_c, hr, ow=max(2, int(2 * s)))
    for sgn in (-1, 1):   # cheek hollows
        pygame.draw.circle(surf, BONE_D,
                           (head_c[0] + sgn * int(hr * 0.66), head_c[1] + int(hr * 0.28)),
                           int(hr * 0.26))
    # two big lower sockets — scary-CUTE, a NOTCH DIMMER than the third eye
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.42)
        ey = head_c[1] + int(hr * 0.16)
        pygame.draw.circle(surf, BONE_DD, (ex, ey), int(hr * 0.30))
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.25))
        pygame.draw.circle(surf, TEAL_D, (ex + sgn * int(1 * s), ey + int(1 * s)),
                           int(hr * 0.12))
    # THIRD EYE — the single BRIGHTEST pixel: a vertical verdigris slit with a
    # hot mint-green core, central on the brow. WHY verdigris not magenta: this
    # is the owned focal hue that splits Nagini from Mukha's rose third-eye.
    tex, tey = head_c[0], head_c[1] - int(hr * 0.34)
    pygame.draw.ellipse(surf, INK, (tex - int(7 * s), tey - int(9 * s), int(14 * s), int(18 * s)))
    pygame.draw.ellipse(surf, EYE, (tex - int(6 * s), tey - int(8 * s), int(12 * s), int(16 * s)))
    pygame.draw.ellipse(surf, EYE_BR, (tex - int(4 * s), tey - int(5 * s), int(8 * s), int(10 * s)))
    pygame.draw.circle(surf, EYE_BR, (tex - int(1 * s), tey - int(2 * s)), max(2, int(3.2 * s)))
    pygame.draw.circle(surf, (255, 255, 255), (tex - int(1 * s), tey - int(2 * s)),
                       max(1, int(1.6 * s)))
    # nose triangle
    pygame.draw.polygon(surf, BONE_DD,
                        [(head_c[0] - int(hr * 0.14), head_c[1] + int(hr * 0.30)),
                         (head_c[0] + int(hr * 0.14), head_c[1] + int(hr * 0.30)),
                         (head_c[0], head_c[1] + int(hr * 0.56))])
    # grinning tooth row (cute, not gory)
    my = head_c[1] + int(hr * 0.72)
    pygame.draw.line(surf, INK, (head_c[0] - int(hr * 0.48), my),
                     (head_c[0] + int(hr * 0.48), my), max(1, int(2 * s)))
    for k in range(-3, 4):
        pygame.draw.line(surf, INK, (head_c[0] + int(k * hr * 0.15), my - int(hr * 0.1)),
                         (head_c[0] + int(k * hr * 0.15), my + int(hr * 0.13)), max(1, int(1 * s)))
    # two small fangs at the corners (wrathful + serpent tell)
    for sgn in (-1, 1):
        fx = head_c[0] + sgn * int(hr * 0.40)
        pygame.draw.polygon(surf, BONE_SH,
                            [(fx - int(2 * s), my), (fx + int(2 * s), my),
                             (fx, my + int(hr * 0.26))])

    # === SKULL-CROWN TIARA (preserved DNA — small bronze band + 3 skulls) =====
    # WHY a SHALLOW arc seated low on the brow in the gap between the upper hoods:
    # the two topmost hoods rear out to the sides, leaving a clean wedge above the
    # crown for the skull-tiara to read against sky.
    tiara_r = int(hr * 0.98)
    tsk_r = int(hr * 0.30)
    band_pts = []
    for i in range(9):
        a = math.radians(238 + i * (64 / 8))
        band_pts.append((head_c[0] + math.cos(a) * tiara_r,
                         head_c[1] + math.sin(a) * tiara_r))
    pygame.draw.lines(surf, INK, False, band_pts, int(6 * s))
    pygame.draw.lines(surf, BRONZE, False, band_pts, int(3 * s))
    pygame.draw.lines(surf, BRONZE_BR, False, band_pts[:5], max(1, int(1.2 * s)))
    for i in range(3):
        a = math.radians(244 + i * (52 / 2))
        sx = head_c[0] + math.cos(a) * tiara_r
        sy = head_c[1] + math.sin(a) * tiara_r
        tiara_skull(surf, int(sx), int(sy), tsk_r, s, lit=(i == 1))


# ── the caduceus twin-snake staff → pillar mirror ─────────────────────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The caduceus twin-snake staff IS the pillar: two bone-snakes wind up a
    central bronze rod and rear into facing cobra-hoods at the cap — the
    creature's own serpent language, bottom-rooted, symmetric on-axis.

    `cap` names the END that faces the GAP."""
    rod_w = int(6 * s)
    # central bronze rod the snakes wind around
    pygame.draw.rect(surf, INK, (cx - rod_w // 2 - int(1 * s), top, rod_w + int(2 * s), bot - top))
    pygame.draw.rect(surf, BRONZE, (cx - rod_w // 2, top, rod_w, bot - top))
    pygame.draw.rect(surf, BRONZE_BR, (cx - rod_w // 2, top, max(1, int(2 * s)), bot - top))

    cap_room = int(40 * s)
    if cap == "bottom":
        b0, b1 = top + int(6 * s), bot - cap_room
        cap_y = bot - int(22 * s)
        grow = +1
    else:
        b0, b1 = top + cap_room, bot - int(6 * s)
        cap_y = top + int(22 * s)
        grow = -1

    # === twin bone-snakes spiralling the rod (the tileable shaft) =============
    snake_w = int(7 * s)
    amp = int(13 * s)
    period = int(34 * s)
    for phase in (0.0, math.pi):   # the two crossing snakes
        pts = []
        y = b0
        while y <= b1:
            x = cx + math.sin((y - b0) / period * 2 * math.pi + phase) * amp
            pts.append((x, y))
            y += int(3 * s)
        thick_path(surf, BONE, pts, snake_w, max(1, int(1.2 * s)))
        # verdigris scale-dashes where the snake crosses the centre rod
        for k in range(len(pts)):
            if abs(pts[k][0] - cx) < int(2 * s):
                pygame.draw.circle(surf, TEAL_D, (int(pts[k][0]), int(pts[k][1])),
                                   max(1, int(1.6 * s)))

    # === gap-edge cap: two facing cobra-hoods rearing toward the gap ==========
    # WHY twin facing hoods at the gap: it mirrors the creature's hood language
    # and the symmetric pair stays on-axis, never wider than the snake span.
    hood_cap_r = int(9 * s)
    for sgn in (-1, 1):
        hc = (cx + sgn * int(11 * s), cap_y + grow * int(2 * s))
        # the hood rears toward the gap and flares outward to its side
        ang = math.atan2(grow, sgn * 0.6)
        cobra_hood(surf, int(hc[0]), int(hc[1]), hood_cap_r, s, ang, with_skull=False, lit=True)
    # a small bronze collar where the snakes meet the cap
    collar_y = cap_y - grow * int(20 * s)
    pygame.draw.rect(surf, INK, (cx - int(10 * s), collar_y - int(3 * s), int(20 * s), int(7 * s)))
    pygame.draw.rect(surf, BRONZE, (cx - int(9 * s), collar_y - int(2 * s), int(18 * s), int(5 * s)))
    pygame.draw.rect(surf, BRONZE_BR, (cx - int(9 * s), collar_y - int(2 * s), int(18 * s), int(2 * s)))
    # a verdigris focal stone between the facing hoods (the gap glow)
    pygame.draw.circle(surf, INK, (cx, cap_y), int(4 * s))
    pygame.draw.circle(surf, EYE, (cx, cap_y), int(3 * s))
    pygame.draw.circle(surf, EYE_BR, (cx - int(1 * s), cap_y - int(1 * s)), max(1, int(1.6 * s)))


# ── compose the review sheet ─────────────────────────────────────────────────
SS = 6


def grow1(surf):
    return grow_outline(surf, INK + (255,), 1)


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def main():
    W, H = 1010, 820
    font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "..", "..", "..", "..", "..", "game", "assets",
                            "LiberationSans-Bold.ttf")
    font_dir = os.path.normpath(font_dir)
    if os.path.exists(font_dir):
        font_big = pygame.font.Font(font_dir, 28)
        font = pygame.font.Font(font_dir, 16)
        font_sm = pygame.font.Font(font_dir, 12)
    else:  # headless fallback so the script never hard-fails on a missing font
        font_big = pygame.font.SysFont("DejaVu Sans", 28, bold=True)
        font = pygame.font.SysFont("DejaVu Sans", 16, bold=True)
        font_sm = pygame.font.SysFont("DejaVu Sans", 12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("NAGINI-DEVI", True, LABEL), (24, 14))
    sheet.blit(font_sm.render(
        "serpent hood-ring bone-naga-queen  ·  KIND: arms-as-snakes hood-RING · mid · aged-bronze (dom) + verdigris-teal · 6 cobra-hoods · round 1",
        True, LABEL_DIM), (250, 26))

    # === (a) EPIC HERO ========================================================
    big = pygame.Surface((360 * SS, 470 * SS), pygame.SRCALPHA)
    draw_nagini_devi(big, 178 * SS, 232 * SS, 1.5 * SS)
    hero = grow1(pygame.transform.smoothscale(big, (360, 470)))
    sheet.blit(hero, (14, 92))
    sheet.blit(font.render("Creature — EPIC hero", True, LABEL), (96, 566))
    sheet.blit(font_sm.render("Big chibi head RINGED by six reared cobra-hoods (S-curved snake-arms, not spokes).", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("Tiny skulls in ALTERNATING hood-jaws; bronze hood-rings + skull-bosses (brood DNA).", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("Verdigris third-eye = brightest pixel; bronze = dominant mass; skull-crown tiara on top.", True, LABEL_DIM), (14, 622))

    # === (b) PILLAR — caduceus twin-snake staff, mirrored, bottom-rooted ======
    pcx = 470
    top_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(top_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="bottom")
    top_seg = grow1(pygame.transform.smoothscale(top_big, (150, 250)))
    sheet.blit(top_seg, (pcx, 86))
    bot_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(bot_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="top")
    bot_seg = grow1(pygame.transform.smoothscale(bot_big, (150, 250)))
    sheet.blit(bot_seg, (pcx, 86 + 250 + 96))
    pygame.draw.rect(sheet, (58, 64, 56), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar — caduceus staff", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("twin bone-snakes spiral a bronze rod =", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("shaft; twin facing cobra-hoods + verdigris", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("stone cap the gap (mirrored, bottom-rooted)", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px gameplay chips on day + night sky ======================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 560))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32():
        b = pygame.Surface((110 * SS, 110 * SS), pygame.SRCALPHA)
        draw_nagini_devi(b, 55 * SS, 56 * SS, (32 / 150.0) * SS)
        return grow1(pygame.transform.smoothscale(b, (110, 110)))

    chip = chip32()

    day_y = 128
    vgrad(sheet, (panel_x + 20, day_y, 150, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 20, day_y + 20))
    sheet.blit(font_sm.render("32px on day sky", True, LABEL), (panel_x + 20, day_y + 156))

    night_y = day_y + 184
    vgrad(sheet, (panel_x + 20, night_y, 150, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 20, night_y + 20))
    sheet.blit(font_sm.render("32px on night sky", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    def pillar_chip32():
        b = pygame.Surface((44 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(b, 22 * SS, 2 * SS, 128 * SS, 0.32 * SS, cap="bottom")
        return grow1(pygame.transform.smoothscale(b, (44, 130)))

    pc = pillar_chip32()
    px2 = panel_x + 192
    vgrad(sheet, (px2, day_y, 56, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (px2, day_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 6, day_y + 10))
    vgrad(sheet, (px2, night_y, 56, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (px2, night_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 6, night_y + 10))
    sheet.blit(font_sm.render("pillar", True, LABEL_DIM), (px2 + 4, day_y - 16))
    sheet.blit(font_sm.render("gap-cap", True, LABEL_DIM), (px2 - 2, night_y - 16))

    # === (d) BLACKED-OUT SILHOUETTE PROOF =====================================
    sil_y = 432
    sheet.blit(font.render("Silhouette proof", True, LABEL), (panel_x + 16, sil_y - 8))
    big_sil = pygame.Surface((150 * SS, 170 * SS), pygame.SRCALPHA)
    draw_nagini_devi(big_sil, 75 * SS, 86 * SS, 0.5 * SS)
    sil = pygame.transform.smoothscale(big_sil, (150, 170))
    # flatten every non-transparent pixel to solid ink — the blackout read
    mask = pygame.mask.from_surface(sil)
    blk = mask.to_surface(setcolor=INK + (255,), unsetcolor=(0, 0, 0, 0))
    pygame.draw.rect(sheet, (180, 184, 176), (panel_x + 16, sil_y + 14, 150, 170))
    pygame.draw.rect(sheet, INK, (panel_x + 16, sil_y + 14, 150, 170), 1)
    sheet.blit(blk, (panel_x + 16, sil_y + 14))
    sheet.blit(font_sm.render("ring of hood-lobes,", True, LABEL_DIM), (panel_x + 174, sil_y + 40))
    sheet.blit(font_sm.render("NOT a radial fan", True, LABEL_DIM), (panel_x + 174, sil_y + 56))

    # === (e) PALETTE STRIP ====================================================
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, sil_y + 196))
    swatches = [
        (BRONZE, "aged-bronze (dom)"), (BRONZE_D, "deep-bronze"),
        (TEAL, "verdigris-teal"), (TEAL_D, "deep verdigris"),
        (BONE, "bone-core"), (EYE, "serpent-eye glow"),
        (BONE_DD, "bone hollow"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, sil_y + 222
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 158
        ry = syp + row * 24
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 18, 18))
        pygame.draw.rect(sheet, c, (rx, ry, 16, 16))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 24, ry + 2))

    pygame.draw.rect(sheet, PANEL, (14, 770, W - 28, 40))
    sheet.blit(font_sm.render(
        "ELEVATED pipeline: SS=6 supersample -> smoothscale.  STAY: flat fills · hard ink keyline (28,22,26) · "
        "dark-core->fill->top-left sheen triad · 1px grown outline · chibi · scary-cute · procedural-only.",
        True, LABEL_DIM), (26, 783))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
