"""
Round-1 concept renderer for BHASMA-YOGINI — the ash-ascetic seed-bead mother
(mukha_citipati_court_ii, sister #2; MUKHA body). Headless Pygame; ELEVATED
pipeline (supersample SS=8 → smoothscale) so the six-arm fan + six palm-skulls +
the knobbly rudraksha swag stay crisp at downscale. Keeps the house grammar:
flat triad fills, hard 1-2px ink keyline (28,22,26), dark-core → flat-fill →
top-left rim-sheen, 1px alpha-grown outline, chibi scary-CUTE; procedural-only.

WHY this sister reads as the ASH-ASCETIC of brood II (charnel-cave register, not
brood I's temple-treasury): the dominant MASS is ash-grey bone smeared with cool
funeral ash, the single saturated accent is saffron (the renunciate's robe), and
the one ornament class is a RUDRAKSHA seed-bead mala. The collision rule vs
asthi_dakini's bone-bead lattice is honoured by SILHOUETTE + TEXTURE, not hue:
each seed is a KNOBBLY, irregular, matte warm-brown nut (puckered/pitted like a
walnut, no two alike, NO smooth pale pip, NO socket-dots), and they string as a
SINGLE FAT U-SWAG across the chest — never a multi-strand net.

WHY the JATA topknot is the gameplay carrier: a lumpy dark matted-dreadlock mass
piled above the crown is a silhouette nothing else in either brood owns. It sits
BEHIND/ABOVE the fused crown so the Citipati 5-skull arc-sweep AND the Mukha
tiara-band still read IN FRONT (never masked). The jata is sculpted/ordered
(reverent ascetic gravitas, the jatamukuta of a yogi), never a messy comic mop.

WHY the alms-staff (khatvanga of seed-bead + ash) IS the pillar: a banded ash
shaft strung with the rudraksha U-swag motif tiles as the repeatable shaft; a
single saffron-lit skull capped by the jata-knot is the gap-edge cap — the
creature's own forms, mirrored on-axis, never top-heavy.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it reuses only colour math + the triad/outline helpers, not runtime
sprite modules.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

# Font lives in the shipped assets dir, five levels up from this sister folder.
FONT_DIR = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "..", "..", "..", "game", "assets"))
FONT_PATH = os.path.join(FONT_DIR, "LiberationSans-Bold.ttf")


# ── PINNED PALETTE (locked brief) ─────────────────────────────────────────────
# Ash-grey bone is the dominant MASS — a cool funeral-ash desaturated bone, NOT
# the rose-bone of Mukha-Devi nor the warm ivory of Citipati. Saffron is the one
# saturated accent (renunciate's robe + third-eye). Seed-brown is the rudraksha
# mala — warm, matte, knobbly, the texture tell vs smooth bone pips.
ASH       = (206, 204, 200)   # ash-grey bone (the dominant fill)
ASH_D     = (150, 148, 146)   # ash dark-core / shade
ASH_DD    = (102, 100, 100)   # deepest ash hollow (sockets, rib gaps)
ASH_SH    = (238, 238, 234)   # ash top-left rim-sheen
SMEAR     = (176, 176, 172)   # cool ash-smear band over the bone (the vibhuti)
SAFF      = (236, 150,  46)   # saffron robe + accent (the one saturated note)
SAFF_BR   = (252, 200, 110)   # hot saffron sheen / inner
SAFF_D    = (176,  98,  26)   # deep saffron shade
SEED      = (132,  86,  52)   # rudraksha seed-brown (knobbly matte mala)
SEED_BR   = (172, 120,  74)   # seed top-light (still MATTE — low spread)
SEED_D    = ( 86,  54,  34)   # seed deep pit / cord-shadow
SEED_DD   = ( 58,  36,  24)   # the pitted walnut grooves (no specular)
INK       = ( 28,  22,  26)   # hard ink keyline
THIRD_EYE = (250, 176,  64)   # saffron-amber third-eye (the brightest focal)
THIRD_BR  = (255, 226, 150)

BG        = ( 92,  90,  92)   # neutral grey review backdrop
PANEL     = ( 72,  70,  74)
DAY_SKY_T = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)   # night biome sky (top)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (240, 238, 238)
LABEL_DIM = (198, 194, 198)


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


# ── a single KNOBBLY rudraksha seed bead (the texture tell vs bone pips) ──────
def seed_bead(surf, cx, cy, r, s, seed=0):
    """ONE rudraksha seed — a matte warm-brown NUT, deliberately NOT a smooth bone
    pip. WHY irregular + pitted: asthi_dakini's bone-bead lattice is smooth pale
    round pips with socket-dots; the collision is broken by SILHOUETTE+TEXTURE.
    Each bead is a slightly lobed blob (a few bulges so the outline is knobbly,
    never a clean circle) with DEEP pit-grooves and NO bright specular — the warm
    light is kept low-spread so the bead reads MATTE like a walnut. `seed` jitters
    the lobes so no two beads look identical (the natural-seed read)."""
    rng = (seed * 2654435761) & 0xFFFFFFFF
    def jit(span):
        nonlocal rng
        rng = (rng * 1103515245 + 12345) & 0x7FFFFFFF
        return (rng / 0x7FFFFFFF - 0.5) * span
    # a lobed/knobbly outline — 7 bumps with jittered radius so it reads irregular
    lobes = 7
    pts = []
    for i in range(lobes):
        a = (i / lobes) * 2 * math.pi
        rr = r * (1.0 + 0.18 * math.cos(a * 2 + seed) + jit(0.16))
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    pygame.draw.polygon(surf, INK, pts)
    pygame.draw.polygon(surf, SEED, pts)
    # deep dark core bottom-right — keeps it round-bodied but MATTE
    pygame.draw.circle(surf, SEED_D,
                       (cx + int(r * 0.22), cy + int(r * 0.24)), int(r * 0.66))
    pygame.draw.circle(surf, SEED, (cx, cy), int(r * 0.74))
    # the pitted walnut grooves — meridian + cross furrows (no two seeds alike)
    for k in range(3):
        a = math.radians(28 + k * 58 + (seed * 23) % 40)
        pygame.draw.line(surf, SEED_DD,
                         (cx - math.cos(a) * r * 0.82, cy - math.sin(a) * r * 0.82),
                         (cx + math.cos(a) * r * 0.82, cy + math.sin(a) * r * 0.82),
                         max(1, int(1.4 * s)))
    # a SMALL, low-spread top-light dot — matte, not a glossy bone glint
    pygame.draw.circle(surf, SEED_BR,
                       (cx - int(r * 0.30), cy - int(r * 0.32)), max(1, int(r * 0.24)))
    pygame.draw.polygon(surf, INK, pts, max(1, int(1.3 * s)))


# ── the rudraksha mala as a single fat U-SWAG (NOT a multi-strand lattice) ────
def seed_swag(surf, cx, cy, span, dip, r, s, n=11):
    """A single hanging U-loop of rudraksha seeds across the chest. WHY one fat
    swag, not a net: asthi_dakini owns the multi-strand smooth-pip LATTICE; this
    is ONE catenary string of knobbly seeds, the silhouette difference doing the
    distinctness work. The cord dips low at centre (gravity) and the centre bead
    is the largest (a guru-bead), so it reads as one mala draped on the body."""
    # the catenary cord the beads thread onto (a real U, low at the middle)
    cord = []
    for i in range(41):
        t = i / 40.0
        x = cx - span + t * span * 2
        y = cy + dip * (1 - (2 * t - 1) ** 2)   # parabolic dip
        cord.append((x, y))
    pygame.draw.lines(surf, SEED_D, False, cord, max(2, int(3.0 * s)))
    pygame.draw.lines(surf, INK, False, cord, max(1, int(1.2 * s)))
    # beads strung evenly along the U; centre bead larger (guru bead)
    for i in range(n):
        t = i / (n - 1)
        x = cx - span + t * span * 2
        y = cy + dip * (1 - (2 * t - 1) ** 2)
        edge = abs(2 * t - 1)
        br = r * (1.0 - 0.18 * edge)
        if i == n // 2:
            br = r * 1.5   # the guru bead at the bottom of the loop
        seed_bead(surf, int(x), int(y), int(br), s, seed=i + 3)


# ── a single ornamental tiara-skull (reused for tiara + pillar) ───────────────
def tiara_skull(surf, cx, cy, r, s, lit=False):
    """Tiny ash-bone skull for the Mukha tiara-BAND across the brow. A domed
    cranium + two dark sockets + a stub jaw, kept LOW on the brow so the face
    still reads under the arm-fan and below the jata mass. `lit` glows the
    centre-skull eyes saffron (the one crown glow allowed)."""
    triad_circle(surf, ASH, (cx, cy), r, ow=max(1, int(1.4 * s)), core=False)
    jaw = [(cx - int(r * 0.5), cy + int(r * 0.5)),
           (cx + int(r * 0.5), cy + int(r * 0.5)),
           (cx + int(r * 0.32), cy + int(r * 0.94)),
           (cx - int(r * 0.32), cy + int(r * 0.94))]
    triad_blob(surf, ASH, jaw, ow=max(1, int(1.1 * s)))
    eye_c = SAFF_BR if lit else INK
    for ex in (cx - int(r * 0.38), cx + int(r * 0.38)):
        pygame.draw.circle(surf, INK, (ex, cy + int(r * 0.02)), max(1, int(r * 0.26)))
        if lit:
            pygame.draw.circle(surf, eye_c, (ex, cy + int(r * 0.02)), max(1, int(r * 0.14)))
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.42)), max(1, int(r * 0.14)))


# ── a single Citipati crown-skull (the OUTER 5-skull arc-sweep) ───────────────
def crown_skull(surf, cx, cy, r, s, lit=False):
    """Tiny ash skull for the Citipati 5-skull arc that owns the OUTER silhouette
    arc. Bigger sockets than the tiara skull so the arc reads countable at 32px.
    The crown is the DIMMEST tier of the value ladder — only the centre skull is
    `lit` (saffron pin), the one crown glow allowed by the brief."""
    triad_circle(surf, ASH, (cx, cy), r, ow=max(1, int(1.6 * s)), core=False)
    jaw = [(cx - int(r * 0.52), cy + int(r * 0.52)),
           (cx + int(r * 0.52), cy + int(r * 0.52)),
           (cx + int(r * 0.34), cy + int(r * 1.0)),
           (cx - int(r * 0.34), cy + int(r * 1.0))]
    triad_blob(surf, ASH, jaw, ow=max(1, int(1.2 * s)))
    eye_c = SAFF_BR if lit else INK
    for ex in (cx - int(r * 0.38), cx + int(r * 0.38)):
        pygame.draw.circle(surf, INK, (ex, cy + int(r * 0.04)), max(1, int(r * 0.24)))
        if lit:
            pygame.draw.circle(surf, eye_c, (ex, cy + int(r * 0.04)), max(1, int(r * 0.13)))
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.42)), max(1, int(r * 0.13)))
    pygame.draw.line(surf, INK, (cx - int(r * 0.34), cy + int(r * 0.70)),
                     (cx + int(r * 0.34), cy + int(r * 0.70)), max(1, int(1.2 * s)))


# ── a tiny palm-skull each open hand cradles (the core motif) ─────────────────
def palm_skull(surf, cx, cy, r, s):
    """A TINY ash skull cradled in one open palm — the MID tier of the value
    ladder (brighter than the crown, dimmer than the third-eye). Domed cranium +
    two dark socket dots; deliberately plain so six of them read as six even
    bone-pips ringing the fan."""
    triad_circle(surf, ASH_SH, (cx, cy), r, ow=max(1, int(1.2 * s)), core=False)
    for ex in (cx - int(r * 0.4), cx + int(r * 0.4)):
        pygame.draw.circle(surf, INK, (ex, cy - int(r * 0.05)), max(1, int(r * 0.26)))
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.3)), max(1, int(r * 0.16)))
    pygame.draw.line(surf, INK, (cx - int(r * 0.4), cy + int(r * 0.55)),
                     (cx + int(r * 0.4), cy + int(r * 0.55)), max(1, int(1.0 * s)))


# ── the six-arm radial fan with OPEN palms cradling tiny skulls ───────────────
def draw_arm_fan(surf, sh_cx, sh_cy, s, hr):
    """Six fat ash-bone arms splay in a wide symmetric STARBURST around the torso
    (the MUKHA KIND tell). Low origin, ~[100,64,28]° off vertical, NONE straight
    up → the crown sky stays open for the jata + fused crown. Each arm ends in an
    OPEN PALM that cradles a tiny skull. Ash-smear bands ring the forearms so the
    arms never read naked. Returns the six hand centres + their open-palm angles."""
    shoulder = (sh_cx, sh_cy)
    arm_len = int(hr * 1.95)
    arm_th = int(12 * s)
    spread = [100, 64, 28]   # degrees off vertical, 3 per side; none vertical
    order = []
    for sgn in (-1, 1):
        for d in spread:
            a = math.radians(-90 + sgn * d)
            order.append((sgn, d, a))
    order.sort(key=lambda o: -o[1])   # lowest arms first, upper splay overlaps clean
    hands = []
    for sgn, d, a in order:
        sh = (shoulder[0] + sgn * int(hr * 0.55), shoulder[1])
        elbow = (sh[0] + math.cos(a) * arm_len * 0.52,
                 sh[1] + math.sin(a) * arm_len * 0.52)
        hand = (sh[0] + math.cos(a) * arm_len,
                sh[1] + math.sin(a) * arm_len)
        for (p, q) in ((sh, elbow), (elbow, hand)):
            dx, dy = q[0] - p[0], q[1] - p[1]
            L = max(1.0, math.hypot(dx, dy))
            nx, ny = -dy / L * arm_th / 2, dx / L * arm_th / 2
            quad = [(p[0] + nx, p[1] + ny), (q[0] + nx, q[1] + ny),
                    (q[0] - nx, q[1] - ny), (p[0] - nx, p[1] - ny)]
            triad_blob(surf, ASH, quad,
                       sheen_pts=[(p[0] + nx, p[1] + ny), (q[0] + nx, q[1] + ny),
                                  (q[0] + nx * 0.3, q[1] + ny * 0.3),
                                  (p[0] + nx * 0.3, p[1] + ny * 0.3)],
                       ow=max(1, int(arm_th * 0.16)))
        triad_circle(surf, ASH, (int(elbow[0]), int(elbow[1])), int(arm_th * 0.55),
                     ow=max(1, int(1.2 * s)), core=False)
        # a saffron + ash-smear forearm cuff so the arm reads dressed, not naked
        cuf = (sh[0] + math.cos(a) * arm_len * 0.78,
               sh[1] + math.sin(a) * arm_len * 0.78)
        pygame.draw.circle(surf, SMEAR, (int(cuf[0]), int(cuf[1])), max(1, int(arm_th * 0.5)))
        pygame.draw.circle(surf, SAFF, (int(cuf[0]), int(cuf[1])), max(1, int(arm_th * 0.28)))
        hands.append((sgn, d, hand, a))
    hands.sort(key=lambda h: (h[0], -h[1]))
    return [(int(h[2][0]), int(h[2][1]), h[3]) for h in hands]


def draw_open_palm(surf, hx, hy, ang, s, r):
    """An OPEN cupped palm at a fan tip — a small ash blob with three short finger
    ticks curling toward the cradled skull, so the hand reads as holding, not a
    fist. Drawn before the palm-skull so the skull sits IN the cup."""
    triad_circle(surf, ASH, (hx, hy), int(r * 0.9), ow=max(1, int(1.2 * s)), core=False)
    for k in range(-1, 2):
        fa = ang - math.pi / 2 + k * 0.5   # fingers fan toward the sky-side of the tip
        ex = hx + math.cos(fa) * r * 1.5
        ey = hy + math.sin(fa) * r * 1.5
        pygame.draw.line(surf, INK, (hx, hy), (ex, ey), max(2, int(3.2 * s)))
        pygame.draw.line(surf, ASH, (hx, hy), (ex, ey), max(1, int(1.8 * s)))


# ── the ash-ascetic seed-bead mother ──────────────────────────────────────────
def draw_bhasma_yogini(surf, cx, cy, s):
    """Pint-sized six-armed ash-mother on a wide lotus base: a chibi ash skull
    framed by a low-origin six-arm fan, each open palm cradling a tiny skull, a
    single fat rudraksha U-swag across the chest, the fused Citipati 5-skull
    arc + Mukha tiara-band on the brow, and a lumpy matted-hair JATA topknot
    piled BEHIND/ABOVE the crown. `s` = unit scale around a ~130-unit figure."""

    head_c = (cx, cy - int(28 * s))
    hr = int(32 * s)
    palm_r = int(9 * s)

    # === SIX-ARM RADIAL FAN (drawn first → behind torso & head) ===============
    hands = draw_arm_fan(surf, head_c[0], head_c[1] + int(hr * 0.82), s, hr)

    # === LOWER BODY — a wide squat 6-petal lotus base (mass low, MUKHA body) ===
    base_y = cy + int(42 * s)
    base = [(cx - int(34 * s), base_y - int(7 * s)),
            (cx - int(24 * s), base_y - int(15 * s)),
            (cx + int(24 * s), base_y - int(15 * s)),
            (cx + int(34 * s), base_y - int(7 * s)),
            (cx + int(27 * s), base_y + int(11 * s)),
            (cx - int(27 * s), base_y + int(11 * s))]
    triad_blob(surf, ASH, base,
               core_pts=[(cx, base_y - int(14 * s)), (cx + int(28 * s), base_y - int(7 * s)),
                         (cx + int(22 * s), base_y + int(9 * s)), (cx, base_y + int(7 * s))],
               ow=max(1, int(1.6 * s)))
    # six lotus-petal grooves, every other one tinted saffron (robe over the base)
    for k in range(-2, 4):
        px = cx + int((k - 0.5) * 11 * s)
        col = SAFF_D if (k % 2 == 0) else ASH_DD
        pygame.draw.line(surf, col, (px, base_y - int(15 * s)),
                         (px, base_y + int(8 * s)), max(1, int(1.6 * s)))
    # an ash-smear seed-glow at the lotus heart — kept deeper than the third-eye
    pygame.draw.circle(surf, SEED_D, (cx, base_y - int(3 * s)), int(5 * s))
    pygame.draw.circle(surf, SEED, (cx - int(1 * s), base_y - int(4 * s)), max(1, int(2 * s)))

    # === TORSO — a SHORT ash rib barrel, smeared with funeral ash =============
    rc_cx, rc_cy = cx, cy + int(12 * s)
    rc_w, rc_h = int(32 * s), int(24 * s)
    cage = [(rc_cx - rc_w // 2, rc_cy - rc_h // 2 + int(2 * s)),
            (rc_cx + rc_w // 2, rc_cy - rc_h // 2),
            (rc_cx + int(rc_w * 0.42), rc_cy + rc_h // 2),
            (rc_cx - int(rc_w * 0.42), rc_cy + rc_h // 2)]
    triad_blob(surf, ASH, cage,
               core_pts=[(rc_cx + int(2 * s), rc_cy - rc_h // 2 + int(3 * s)),
                         (rc_cx + rc_w // 2, rc_cy - rc_h // 2 + int(2 * s)),
                         (rc_cx + int(rc_w * 0.42), rc_cy + rc_h // 2),
                         (rc_cx + int(2 * s), rc_cy + rc_h // 2)],
               sheen_pts=[(rc_cx - rc_w // 2 + int(2 * s), rc_cy - rc_h // 2 + int(3 * s)),
                          (rc_cx - int(4 * s), rc_cy - rc_h // 2 + int(2 * s)),
                          (rc_cx - int(6 * s), rc_cy + int(4 * s)),
                          (rc_cx - rc_w // 2 + int(2 * s), rc_cy + int(2 * s))],
               ow=max(1, int(1.8 * s)))
    # horizontal ash-smear (vibhuti) bands across the ribs — the ascetic tell
    for i in range(3):
        sy = rc_cy - rc_h // 2 + int(6 * s) + i * int(7 * s)
        pygame.draw.line(surf, SMEAR, (rc_cx - int(rc_w * 0.42), sy),
                         (rc_cx + int(rc_w * 0.42), sy), max(2, int(2.6 * s)))
    pygame.draw.line(surf, ASH_DD, (rc_cx, rc_cy - rc_h // 2 + int(5 * s)),
                     (rc_cx, rc_cy + int(3 * s)), max(1, int(2 * s)))

    # === SIX PALM-SKULLS — one cradled in each open hand (the core motif) ======
    # Drawn after torso, before head: they ride at the fan tips so the outer arc
    # is six even bone-pips; each is an OPEN palm cupping a tiny skull.
    for (hx, hy, ang) in hands:
        draw_open_palm(surf, hx, hy, ang, s, palm_r)
        palm_skull(surf, hx, hy - int(palm_r * 0.25), int(palm_r * 0.78), s)

    # === RUDRAKSHA SEED-SWAG — a single fat U across the chest (the ornament) ==
    # WHY routed in FRONT of the torso but BETWEEN the arm origins: it must read
    # as the dressed mala without occluding any palm-skull. One catenary loop of
    # knobbly matte brown seeds — NOT asthi's smooth multi-strand pip lattice.
    # WHY slung WIDE and high off the shoulders with a fat guru-bead: the seed
    # distinctness is the locked CRITICAL tell, so the swag must be unmistakably
    # the secondary read — a generous U that brackets the upper ribs clear of the
    # chin, not a thin necklace buried under the jaw.
    seed_swag(surf, rc_cx, rc_cy - int(rc_h * 0.50), int(rc_w * 0.82),
              int(rc_h * 0.92), int(6.2 * s), s, n=11)

    # === SKULL HEAD — chibi, scary-cute, three-eyed (the framed FACE) =========
    triad_circle(surf, ASH, head_c, hr, ow=max(2, int(2 * s)))
    for sgn in (-1, 1):   # cheek hollows
        pygame.draw.circle(surf, ASH_D,
                           (head_c[0] + sgn * int(hr * 0.66), head_c[1] + int(hr * 0.28)),
                           int(hr * 0.26))
    # two lower sockets — a NOTCH dimmer than the third eye (dark hollow + small
    # deep-saffron pin, no hot core) so the 3-eye triangle points UP to the brow.
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.42)
        ey = head_c[1] + int(hr * 0.16)
        pygame.draw.circle(surf, ASH_DD, (ex, ey), int(hr * 0.30))
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.25))
        pygame.draw.circle(surf, SAFF_D, (ex + sgn * int(1 * s), ey + int(1 * s)),
                           int(hr * 0.12))
    # tri-band forehead lines (the clean ascetic vibhuti tilak) above the brow
    for i in range(3):
        ly = head_c[1] - int(hr * 0.56) + i * int(hr * 0.10)
        ww = hr * (0.42 - i * 0.04)
        pygame.draw.line(surf, SMEAR, (head_c[0] - ww, ly), (head_c[0] + ww, ly),
                         max(1, int(2.0 * s)))
    # THIRD EYE — the single BRIGHTEST pixel (AD hard rule). A fat vertical
    # saffron-amber slit with a hot core, central on the brow.
    tex, tey = head_c[0], head_c[1] - int(hr * 0.32)
    pygame.draw.ellipse(surf, INK, (tex - int(7 * s), tey - int(9 * s), int(14 * s), int(18 * s)))
    pygame.draw.ellipse(surf, SAFF, (tex - int(6 * s), tey - int(8 * s), int(12 * s), int(16 * s)))
    pygame.draw.ellipse(surf, SAFF_BR, (tex - int(4 * s), tey - int(5 * s), int(8 * s), int(10 * s)))
    pygame.draw.circle(surf, THIRD_BR, (tex - int(1 * s), tey - int(2 * s)), max(2, int(3.2 * s)))
    pygame.draw.circle(surf, (255, 255, 255), (tex - int(1 * s), tey - int(2 * s)),
                       max(1, int(1.6 * s)))
    # nose triangle
    pygame.draw.polygon(surf, ASH_DD,
                        [(head_c[0] - int(hr * 0.14), head_c[1] + int(hr * 0.30)),
                         (head_c[0] + int(hr * 0.14), head_c[1] + int(hr * 0.30)),
                         (head_c[0], head_c[1] + int(hr * 0.56))])
    # grinning tooth row + corner fangs (wrathful, not gory)
    my = head_c[1] + int(hr * 0.72)
    pygame.draw.line(surf, INK, (head_c[0] - int(hr * 0.48), my),
                     (head_c[0] + int(hr * 0.48), my), max(1, int(2 * s)))
    for k in range(-3, 4):
        pygame.draw.line(surf, INK, (head_c[0] + int(k * hr * 0.15), my - int(hr * 0.1)),
                         (head_c[0] + int(k * hr * 0.15), my + int(hr * 0.13)), max(1, int(1 * s)))
    for sgn in (-1, 1):
        fx = head_c[0] + sgn * int(hr * 0.40)
        pygame.draw.polygon(surf, ASH_SH,
                            [(fx - int(2 * s), my), (fx + int(2 * s), my),
                             (fx, my + int(hr * 0.22))])

    # === JATA TOPKNOT — matted dreadlocks, BEHIND/ABOVE the crown ==============
    # WHY drawn HERE (after the head, before the crown): the lumpy dark jata mass
    # must sit BEHIND/ABOVE the fused crown so the arc + band read IN FRONT, never
    # masked. Sculpted ORDERED dreadlocks (a jatamukuta), not a messy mop — each
    # lock is a tapering dark coil, fanning up into a piled knot. This dark mass
    # is the gameplay SILHOUETTE CARRIER (nothing else in either brood owns it).
    draw_jata(surf, head_c[0], head_c[1] - int(hr * 0.62), hr, s)

    # === FUSED CROWN: Citipati 5-skull arc-SWEEP + Mukha tiara-BAND ===========
    # Both must read IN FRONT of the jata. The tiara-band seats LOW on the brow;
    # the 5-skull arc sweeps WIDER + higher outside it. Crown is the DIMMEST tier.
    # -- Mukha tiara-BAND across the brow (shallow ~70° arc, 3 low skulls) --
    tiara_r = int(hr * 0.98)
    tiara_skull_r = int(hr * 0.26)
    band_pts = []
    for i in range(9):
        a = math.radians(238 + i * (64 / 8))
        band_pts.append((head_c[0] + math.cos(a) * tiara_r,
                         head_c[1] + math.sin(a) * tiara_r))
    pygame.draw.lines(surf, INK, False, band_pts, int(6 * s))
    pygame.draw.lines(surf, SAFF, False, band_pts, int(3 * s))
    pygame.draw.lines(surf, SAFF_BR, False, band_pts[:5], max(1, int(1.2 * s)))
    for i in range(3):
        a = math.radians(245 + i * (50 / 2))
        sx = head_c[0] + math.cos(a) * tiara_r
        sy = head_c[1] + math.sin(a) * tiara_r
        tiara_skull(surf, int(sx), int(sy), tiara_skull_r, s, lit=False)
    # -- Citipati 5-skull arc-SWEEP, wider + higher, outside the band --
    arc_band_r = int(hr * 1.26)
    skull_cr = hr * 1.52
    skull_r = int(hr * 0.34)
    arc_pts = []
    for i in range(13):
        a = math.radians(212 + i * (116 / 12))
        arc_pts.append((head_c[0] + math.cos(a) * arc_band_r,
                        head_c[1] + math.sin(a) * arc_band_r))
    pygame.draw.lines(surf, INK, False, arc_pts, int(5 * s))
    pygame.draw.lines(surf, SEED, False, arc_pts, int(3 * s))   # seed-brown crown cord
    for i in range(5):
        a = math.radians(218 + i * (104 / 4))
        sx = head_c[0] + math.cos(a) * skull_cr
        sy = head_c[1] + math.sin(a) * skull_cr
        crown_skull(surf, int(sx), int(sy), skull_r, s, lit=(i == 2))


# ── the matted-hair JATA topknot (the 32px silhouette carrier) ────────────────
def draw_jata(surf, cx, cy, hr, s):
    """A lumpy dark matted-hair JATA piled above the head. Sculpted ORDERED
    dreadlocks: a fan of tapering dark coils rising into a piled top knot, bound
    by a saffron tie. WHY a dark near-ink mass with seed-brown grooves: it must
    be the dimmest-but-largest top shape so it reads as a distinct LUMPY mass at
    32px (the carrier) yet never out-values the crown skulls in front of it."""
    HAIR   = (52, 40, 38)     # near-ink matted-hair brown
    HAIR_H = (84, 62, 54)     # the dressed-lock highlight (still dark)
    # the rising fan of dreadlock coils (ordered, symmetric — reverent gravitas)
    n = 11
    for i in range(n):
        t = (i / (n - 1)) - 0.5
        ang = math.radians(-90 + t * 108)      # fan across the top
        reach = hr * (1.34 - 0.28 * abs(t))    # centre locks rise highest
        bx = cx + math.cos(ang) * hr * 0.30
        by = cy + math.sin(ang) * hr * 0.10
        tipx = cx + math.cos(ang) * reach
        tipy = cy + math.sin(ang) * reach - hr * 0.22
        midx = (bx + tipx) / 2 + math.cos(ang + 0.4) * hr * 0.10
        midy = (by + tipy) / 2
        lock = [bx, by, midx, midy, tipx, tipy]
        pygame.draw.lines(surf, INK, False,
                          [(bx, by), (midx, midy), (tipx, tipy)], max(3, int(6.5 * s)))
        pygame.draw.lines(surf, HAIR, False,
                          [(bx, by), (midx, midy), (tipx, tipy)], max(2, int(4.2 * s)))
        # a couple of groove ticks so each coil reads as a matted dreadlock
        pygame.draw.line(surf, HAIR_H, (bx, by - int(1 * s)),
                         (midx, midy - int(1 * s)), max(1, int(1.2 * s)))
    # the piled top-KNOT — a lumpy dark dome bound by a saffron tie (jatamukuta)
    knot_c = (cx, cy - int(hr * 0.92))
    knot = []
    kpts = 13
    rng = 7777
    for i in range(kpts):
        a = (i / kpts) * 2 * math.pi
        rng = (rng * 1103515245 + 12345) & 0x7FFFFFFF
        rr = hr * (0.78 + 0.12 * math.cos(a * 3) + (rng / 0x7FFFFFFF - 0.5) * 0.16)
        knot.append((knot_c[0] + math.cos(a) * rr, knot_c[1] + math.sin(a) * rr * 0.92))
    pygame.draw.polygon(surf, INK, knot)
    pygame.draw.polygon(surf, HAIR, knot)
    # a few coil grooves on the knot surface (ordered, not random scribble)
    for k in range(-2, 3):
        gx = knot_c[0] + int(k * hr * 0.16)
        pygame.draw.line(surf, HAIR_H, (gx, knot_c[1] - int(hr * 0.4)),
                         (gx, knot_c[1] + int(hr * 0.4)), max(1, int(1.4 * s)))
    pygame.draw.polygon(surf, INK, knot, max(1, int(1.4 * s)))
    # the saffron tie binding the knot (the one ascetic colour note up top)
    pygame.draw.line(surf, SAFF, (knot_c[0] - int(hr * 0.5), cy - int(hr * 0.34)),
                     (knot_c[0] + int(hr * 0.5), cy - int(hr * 0.34)), max(2, int(3.2 * s)))
    pygame.draw.line(surf, SAFF_BR, (knot_c[0] - int(hr * 0.4), cy - int(hr * 0.35)),
                     (knot_c[0] + int(hr * 0.1), cy - int(hr * 0.35)), max(1, int(1.4 * s)))


# ── the alms-staff (ash + seed-bead khatvanga) → pillar mirror ────────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The ash-and-seed alms-staff IS the pillar: a banded ash shaft strung with
    the rudraksha U-swag motif = the tileable shaft; a single saffron-lit skull
    capped by a small jata-knot = the gap-edge cap — the sister's own forms,
    mirrored on-axis, never top-heavy. `cap` names the END that faces the GAP."""
    shaft_w = int(13 * s)
    pygame.draw.rect(surf, INK, (cx - int(3 * s), top, int(6 * s), bot - top))

    band_pitch = int(30 * s)
    cap_room = int(40 * s)
    if cap == "bottom":
        b0, b1 = top + int(6 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(6 * s)
    y = b0
    while y <= b1:
        bw = shaft_w
        band = [(cx - bw, y - int(10 * s)),
                (cx + bw, y - int(10 * s)),
                (cx + bw, y + int(10 * s)),
                (cx - bw, y + int(10 * s))]
        triad_blob(surf, ASH, band,
                   core_pts=[(cx, y - int(9 * s)), (cx + bw, y - int(9 * s)),
                             (cx + bw, y + int(9 * s)), (cx, y + int(9 * s))],
                   sheen_pts=[(cx - bw, y - int(9 * s)), (cx - int(bw * 0.3), y - int(9 * s)),
                              (cx - int(bw * 0.3), y + int(2 * s)), (cx - bw, y + int(2 * s))],
                   ow=max(1, int(1.4 * s)))
        # an ash-smear groove across the band (the vibhuti tell on the shaft)
        pygame.draw.line(surf, SMEAR, (cx - bw, y - int(4 * s)),
                         (cx + bw, y - int(4 * s)), max(1, int(2.0 * s)))
        # a single fat seed-swag slung across the band (the mala motif tiled)
        seed_swag(surf, cx, y - int(2 * s), int(bw * 0.92), int(11 * s),
                  int(3.6 * s), s, n=7)
        y += band_pitch

    # === gap-edge cap: a saffron-lit ash skull capped by a small jata-knot =====
    cap_y = (bot - int(22 * s)) if cap == "bottom" else (top + int(22 * s))
    cap_skull_r = int(13 * s)
    # the jata-knot sits on the SKY-side of the cap skull (toward the figure body)
    knot_y = cap_y + (int(cap_skull_r * 1.4) if cap == "top" else -int(cap_skull_r * 1.4))
    kn = []
    rng = 4242
    for i in range(11):
        a = (i / 11) * 2 * math.pi
        rng = (rng * 1103515245 + 12345) & 0x7FFFFFFF
        rr = cap_skull_r * (0.74 + 0.12 * math.cos(a * 3) + (rng / 0x7FFFFFFF - 0.5) * 0.16)
        kn.append((cx + math.cos(a) * rr, knot_y + math.sin(a) * rr * 0.9))
    pygame.draw.polygon(surf, INK, kn)
    pygame.draw.polygon(surf, (52, 40, 38), kn)
    pygame.draw.line(surf, SAFF, (cx - int(cap_skull_r * 0.7), knot_y),
                     (cx + int(cap_skull_r * 0.7), knot_y), max(2, int(2.6 * s)))
    crown_skull(surf, cx, cap_y, cap_skull_r, s, lit=True)
    # a saffron collar where the cap meets the shaft
    collar_y = (cap_y - int(20 * s)) if cap == "bottom" else (cap_y + int(20 * s))
    pygame.draw.rect(surf, INK, (cx - int(10 * s), collar_y - int(3 * s), int(20 * s), int(7 * s)))
    pygame.draw.rect(surf, SAFF, (cx - int(9 * s), collar_y - int(2 * s), int(18 * s), int(5 * s)))
    pygame.draw.rect(surf, SAFF_BR, (cx - int(9 * s), collar_y - int(2 * s), int(18 * s), int(2 * s)))


# ── render pipeline ───────────────────────────────────────────────────────────
SS = 8


def render_creature_chip(boxw, boxh, draw_cx, draw_cy, scale):
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_bhasma_yogini(big, draw_cx * SS, draw_cy * SS, scale * SS)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def font(size):
    return pygame.font.Font(FONT_PATH, size)


def render_hero():
    """Standalone hi-res hero (~1024px tall) — the brood-II hero pipeline."""
    HW, HH = 760, 1024
    surf = pygame.Surface((HW, HH))
    vgrad(surf, (0, 0, HW, HH), (70, 66, 72), (44, 42, 48))
    hero = render_creature_chip(620, 880, 310, 470, 3.0)
    surf.blit(hero, ((HW - 620) // 2, 70))
    f = font(26)
    surf.blit(f.render("BHASMA-YOGINI", True, LABEL), (30, 24))
    fs = font(16)
    surf.blit(fs.render("ash-ascetic seed-bead mother  ·  MUKHA body  ·  SS=8 hero", True, LABEL_DIM),
              (30, 60))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1_hero.png")
    pygame.image.save(surf, out)
    return out


def main():
    W, H = 1010, 860
    font_big = font(30)
    f = font(17)
    f_sm = font(12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("BHASMA-YOGINI", True, LABEL), (24, 13))
    sheet.blit(f_sm.render(
        "ash-ascetic seed-bead mother  ·  MUKHA body · six-arm fan · 6 palm-skulls · rudraksha U-swag · jata topknot · round 1",
        True, LABEL_DIM), (300, 26))

    # === (a) BIG HERO =========================================================
    hero = render_creature_chip(360, 500, 178, 256, 1.62)
    sheet.blit(hero, (14, 84))
    sheet.blit(f.render("Creature — hero", True, LABEL), (110, 588))
    sheet.blit(f_sm.render("Six-arm fan; six OPEN palms each cradle a tiny skull (mid value tier).", True, LABEL_DIM), (14, 612))
    sheet.blit(f_sm.render("Fused crown: Citipati 5-skull arc + Mukha tiara-band IN FRONT of the jata.", True, LABEL_DIM), (14, 628))
    sheet.blit(f_sm.render("Jata topknot = lumpy dark mass behind/above. Saffron-amber third-eye = brightest.", True, LABEL_DIM), (14, 644))
    sheet.blit(f_sm.render("Rudraksha mala = ONE fat knobbly-brown U-swag (NOT a smooth bone lattice).", True, LABEL_DIM), (14, 660))

    # === (b) PILLAR assembled — mirrored ======================================
    pcx = 470
    top_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(top_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="bottom")
    top_seg = grow_outline(pygame.transform.smoothscale(top_big, (150, 250)), INK + (255,), 1)
    sheet.blit(top_seg, (pcx, 84))
    bot_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(bot_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="top")
    bot_seg = grow_outline(pygame.transform.smoothscale(bot_big, (150, 250)), INK + (255,), 1)
    sheet.blit(bot_seg, (pcx, 84 + 250 + 96))
    pygame.draw.rect(sheet, (58, 56, 62), (pcx + 8, 84 + 250, 134, 96))
    sheet.blit(f_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 84 + 250 + 40))
    sheet.blit(f.render("Pillar — alms-staff", True, LABEL), (pcx - 4, 688))
    sheet.blit(f_sm.render("banded ash shaft strung with the rudraksha", True, LABEL_DIM), (pcx - 4, 712))
    sheet.blit(f_sm.render("U-swag = shaft; saffron-lit skull + small", True, LABEL_DIM), (pcx - 4, 728))
    sheet.blit(f_sm.render("jata-knot caps the gap (mirrored top<->bottom)", True, LABEL_DIM), (pcx - 4, 744))

    # === (c) TRUE 32px DAY + NIGHT chips + blackout proof ======================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 84, W - panel_x - 14, 580))
    sheet.blit(f.render("True 32px gameplay chip", True, LABEL), (panel_x + 16, 94))

    def chip32():
        big = pygame.Surface((110 * SS, 110 * SS), pygame.SRCALPHA)
        draw_bhasma_yogini(big, 55 * SS, 58 * SS, (32 / 150.0) * SS)
        small = pygame.transform.smoothscale(big, (110, 110))
        return grow_outline(small, INK + (255,), 1)

    chip = chip32()

    day_y = 124
    vgrad(sheet, (panel_x + 20, day_y, 150, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 20, day_y + 20))
    sheet.blit(f_sm.render("32px on day sky", True, LABEL), (panel_x + 20, day_y + 156))

    night_y = day_y + 184
    vgrad(sheet, (panel_x + 20, night_y, 150, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 20, night_y + 20))
    sheet.blit(f_sm.render("32px on night sky", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    # blackout / silhouette proof — the read at pure-mask scale (jata carrier)
    def blackout():
        big = pygame.Surface((110 * SS, 110 * SS), pygame.SRCALPHA)
        draw_bhasma_yogini(big, 55 * SS, 58 * SS, (32 / 150.0) * SS)
        small = pygame.transform.smoothscale(big, (110, 110))
        mask = pygame.mask.from_surface(small)
        sil = mask.to_surface(setcolor=(20, 18, 22, 255), unsetcolor=(0, 0, 0, 0))
        return sil

    px2 = panel_x + 192
    pygame.draw.rect(sheet, (224, 224, 226), (px2, day_y, 130, 150))
    pygame.draw.rect(sheet, INK, (px2, day_y, 130, 150), 1)
    sheet.blit(blackout(), (px2 + 10, day_y + 20))
    sheet.blit(f_sm.render("blackout", True, LABEL_DIM), (px2 + 2, day_y - 16))
    sheet.blit(f_sm.render("(jata + fan", True, LABEL_DIM), (px2, day_y + 156))
    sheet.blit(f_sm.render(" silhouette)", True, LABEL_DIM), (px2, day_y + 170))

    # 32px pillar gap-cap on both skies
    def pillar_chip32():
        big = pygame.Surface((44 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 22 * SS, 2 * SS, 128 * SS, 0.32 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (44, 130))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    vgrad(sheet, (px2 + 36, night_y, 56, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (px2 + 36, night_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 42, night_y + 10))
    sheet.blit(f_sm.render("pillar 32px", True, LABEL_DIM), (px2 + 32, night_y - 16))

    # palette strip
    sheet.blit(f.render("Pinned palette", True, LABEL), (panel_x + 16, 524))
    swatches = [
        (ASH, "ash-grey bone"), (ASH_D, "ash shade"),
        (SMEAR, "ash-smear"), (SAFF, "saffron robe"),
        (SEED, "seed-brown"), (SEED_DD, "seed pit"),
        (THIRD_EYE, "third-eye"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, 552
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 158
        ry = syp + row * 26
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, ry, 18, 18))
        sheet.blit(f_sm.render(name, True, LABEL), (rx + 26, ry + 3))

    pygame.draw.rect(sheet, PANEL, (14, 810, W - 28, 42))
    sheet.blit(f_sm.render(
        "ELEVATED pipeline: SS=8 supersample -> smoothscale.  STAY: flat fills · hard ink keyline (28,22,26) · "
        "dark-core->fill->top-left sheen triad · 1px grown outline · chibi scary-cute · procedural-only.",
        True, LABEL_DIM), (26, 824))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    hero_path = render_hero()
    print("wrote", hero_path)
    main()
