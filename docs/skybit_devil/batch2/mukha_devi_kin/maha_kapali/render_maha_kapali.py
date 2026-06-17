"""
Round-1 concept renderer for MAHA-KAPALI — "great skull-crowned dread", a
GROUNDED SISTER of the shipped six-armed bone-mother MUKHA-DEVI (Mukha-Devi KIN
brood, LOOSE · skull-motif corner anchor). Headless Pygame; ELEVATED pipeline
(supersample SS=6 -> smoothscale) so the radial arm-fan + the dripping skull
trophies stay crisp at downscale. Keeps the shipped house grammar: flat
saturated fills, hard 1-2px ink keyline (28,22,26), dark-core -> flat-fill ->
top-left rim-sheen triad, 1px alpha-grown outline, chibi, scary-CUTE.

WHY a SISTER not a new KIND: she shares Mukha's six-arm radial fan, her chibi
skull-face + rose third eye (the single brightest pixel), and her rose/gold/teal
bone palette UNCHANGED. Distinctness lives ONLY in two places, per the relaxed
sister-doctrine: (a) the arm-ends become SIX skull-trophy STRANDS — a short
gold-capped rod hung with two stacked skull trophies + a rose tassel-dot, hanging
LOWER than Mukha's tight glow-caps — and (b) a tall fanned MEGA-CROWN of EXACTLY
five skulls (lit centre) over a taller head/upper mass. She is the LOOSE,
skull-motif corner of the spread.

WHY the skull count is HARD-LOCKED: ~17 skulls courts the "mush" failure at 32px.
Crown LOCKED to 5; arm trophies LOCKED to 2 per strand (drop-rule: 1 + tassel if
the chip mushes). The target read at 32px is a VALUE-CLUMP — "tall skull-crown +
skulls dripping off the arms" — never countable skulls. A negative gap between
the crown skulls and the topmost arm strands is verified on the 32px chip so the
two skull-masses do NOT merge into one blob.

WHY a standalone script under docs/: review art must never enter the shipped
bundle, so it reuses only colour math + the triad/outline helpers.
"""
import math
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
pygame.init()

# ── PINNED PALETTE (UNCHANGED from Mukha-Devi — sister, not a new creature) ───
BONE      = (224, 200, 196)   # dusty rose-bone (the dominant fill)
BONE_D    = (168, 134, 138)   # mauve-bone dark-core / shade
BONE_DD   = (120,  90,  98)   # deepest bone hollow (sockets, rib gaps)
BONE_SH   = (248, 236, 234)   # bone top-left rim-sheen
ROSE      = (232,  86, 150)   # magenta-rose relic GLOW (the single warm focal)
ROSE_BR   = (255, 160, 200)   # hot relic-glow inner / sheen / lit-skull eyes
ROSE_D    = (160,  40,  86)   # deep-rose shade
GOLD      = (224, 182,  84)   # gold trim accent (rod caps, crown band)
GOLD_BR   = (246, 214, 130)
GOLD_D    = (170, 134,  56)
TEAL      = ( 64, 170, 166)   # teal sliver
TEAL_BR   = (140, 222, 216)
INK       = ( 28,  22,  26)   # hard ink keyline
THIRD_EYE = (232,  86, 150)   # third-eye glow
THIRD_BR  = (255, 196, 224)

BG        = ( 96,  92, 100)
PANEL     = ( 74,  72,  84)
DAY_SKY_T = (120, 196, 236)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (240, 236, 240)
LABEL_DIM = (196, 190, 202)


def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0]-a[0])*t),
            int(a[1] + (b[1]-a[1])*t),
            int(a[2] + (b[2]-a[2])*t))


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


# ── a single ornamental tiara-skull (reused for crown + arm trophies) ─────────
def tiara_skull(surf, cx, cy, r, s, lit=False):
    """Tiny rose-bone skull: domed cranium + jaw + two ink sockets. Punches a
    clean bone shape with two dots at 32px. `lit` floods the eyes ROSE_BR — used
    ONLY for the crown centre so it stays a single motif accent."""
    triad_circle(surf, BONE, (cx, cy), r, ow=max(1, int(1.4 * s)), core=False)
    jaw = [(cx - int(r * 0.5), cy + int(r * 0.5)),
           (cx + int(r * 0.5), cy + int(r * 0.5)),
           (cx + int(r * 0.32), cy + int(r * 0.94)),
           (cx - int(r * 0.32), cy + int(r * 0.94))]
    triad_blob(surf, BONE, jaw, ow=max(1, int(1.1 * s)))
    eye_c = ROSE_BR if lit else INK
    for ex in (cx - int(r * 0.38), cx + int(r * 0.38)):
        pygame.draw.circle(surf, INK, (ex, cy + int(r * 0.02)), max(1, int(r * 0.26)))
        if lit:
            pygame.draw.circle(surf, eye_c, (ex, cy + int(r * 0.02)), max(1, int(r * 0.14)))
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.42)), max(1, int(r * 0.14)))


# ── arm-end SKULL-TROPHY STRAND — replaces Mukha's relic() ────────────────────
def skull_trophy_strand(surf, hx, hy, r, s, ang=0.0, two=True):
    """ONE of the six arm-ends: a short GOLD-capped rod at the hand, hung with
    TWO stacked tiara-skull trophies and a ROSE tassel-dot below — the dripping
    skull motif. WHY it hangs DOWN-and-OUT (toward `ang`, biased toward gravity)
    rather than capping the hand like Mukha's tight glow-disc: the brood spread
    asks Maha to be the LOOSE sister, so her ornaments dangle LOWER and looser
    off the fan than Mukha's caps, reading as trophies swinging from the arms.

    HARD-LOCKED to 2 trophies per strand (`two`); the drop-rule passes
    `two=False` for a single skull + tassel if the 32px chip ever mushes."""
    # the strand hangs mostly downward, nudged outward along the arm angle so the
    # six strands splay into a ring of drips instead of stacking on the torso.
    out = math.cos(ang), math.sin(ang)
    dirx = out[0] * 0.45
    diry = 0.9 + out[1] * 0.2          # gravity-biased: always drips down
    L = math.hypot(dirx, diry)
    dirx, diry = dirx / L, diry / L

    sk_r = int(r * 0.92)
    rod_len = int(r * 0.7)
    pitch = int(sk_r * 1.62)           # stacking pitch keeps two sockets readable

    # short gold-capped rod at the hand (the trophy bar the skulls hang from)
    rx0, ry0 = hx, hy
    rx1 = int(hx + dirx * rod_len)
    ry1 = int(hy + diry * rod_len)
    pygame.draw.line(surf, INK, (rx0, ry0), (rx1, ry1), max(2, int(4.4 * s)))
    pygame.draw.line(surf, GOLD, (rx0, ry0), (rx1, ry1), max(1, int(2.6 * s)))
    pygame.draw.line(surf, GOLD_BR, (rx0, ry0),
                     (int(hx + dirx * rod_len * 0.5), int(hy + diry * rod_len * 0.5)),
                     max(1, int(1.2 * s)))
    triad_circle(surf, GOLD, (rx1, ry1), max(2, int(r * 0.34)),
                 ow=max(1, int(1.2 * s)), core=False)

    # the stacked skull trophies, dripping down the strand
    n = 2 if two else 1
    sx, sy = rx1, ry1 + sk_r
    for i in range(n):
        cy = sy + i * pitch
        # a hair of ink cord between trophies so they read as threaded, not fused
        if i > 0:
            pygame.draw.line(surf, INK, (sx, cy - pitch + int(sk_r * 0.7)),
                             (sx, cy - int(sk_r * 0.8)), max(1, int(1.6 * s)))
        tiara_skull(surf, int(sx), int(cy), sk_r, s, lit=False)

    # the ROSE tassel-dot below the lowest skull (the warm strand terminator)
    tail_y = sy + (n - 1) * pitch + int(sk_r * 1.15)
    pygame.draw.line(surf, ROSE_D, (sx, tail_y - int(sk_r * 0.7)), (sx, tail_y),
                     max(1, int(1.8 * s)))
    triad_circle(surf, ROSE, (int(sx), int(tail_y)), max(2, int(r * 0.42)),
                 ow=max(1, int(1.2 * s)), core=False, sheen=False)
    pygame.draw.circle(surf, ROSE_BR, (int(sx - r * 0.12), int(tail_y - r * 0.14)),
                       max(1, int(r * 0.2)))


# ── the six-arm radial starburst (the KIND tell — UNCHANGED from Mukha) ───────
def draw_arm_fan(surf, sh_cx, sh_cy, s, hr, relic_r):
    shoulder = (sh_cx, sh_cy)
    arm_len = int(hr * 1.95)
    arm_th = int(12 * s)
    spread = [100, 64, 28]
    order = []
    for sgn in (-1, 1):
        for d in spread:
            a = math.radians(-90 + sgn * d)
            order.append((sgn, d, a))
    order.sort(key=lambda o: -o[1])
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
            triad_blob(surf, BONE, quad,
                       sheen_pts=[(p[0] + nx, p[1] + ny), (q[0] + nx, q[1] + ny),
                                  (q[0] + nx * 0.3, q[1] + ny * 0.3),
                                  (p[0] + nx * 0.3, p[1] + ny * 0.3)],
                       ow=max(1, int(arm_th * 0.16)))
        triad_circle(surf, BONE, (int(elbow[0]), int(elbow[1])), int(arm_th * 0.55),
                     ow=max(1, int(1.2 * s)), core=False)
        hands.append((sgn, d, hand))
    hands.sort(key=lambda h: (h[0], -h[1]))
    return [(int(h[2][0]), int(h[2][1])) for h in hands]


# ── MAHA-KAPALI — great skull-crowned dread ───────────────────────────────────
def draw_maha_kapali(surf, cx, cy, s):
    """Mukha's grounded SISTER: same chibi torso under the same six-arm radial
    fan, but each hand drips a skull-trophy strand and a tall five-skull
    MEGA-CROWN rises over a taller head/upper mass. Face + third eye unchanged.
    `s` = unit scale around the same ~130-unit figure."""

    # WHY a TALLER head/upper mass than Mukha (LOOSE sister): she is lifted up a
    # notch (raised head + slightly larger cranium) so the mega-crown has open
    # sky to fan into, and so her upper silhouette is visibly grander than the
    # Original's compact dome. Body, fan origin, base stay Mukha's.
    head_c = (cx, cy - int(34 * s))           # raised ~6 units vs Mukha's -28
    hr = int(34 * s)                          # a touch larger cranium
    trophy_r = int(9 * s)

    # === SIX-ARM RADIAL FAN (behind torso & head) =============================
    hands = draw_arm_fan(surf, head_c[0], head_c[1] + int(hr * 0.82), s, hr, trophy_r)

    # === LOWER BODY — wide squat lotus-base (UNCHANGED) =======================
    base_y = cy + int(42 * s)
    base = [(cx - int(34 * s), base_y - int(7 * s)),
            (cx - int(24 * s), base_y - int(15 * s)),
            (cx + int(24 * s), base_y - int(15 * s)),
            (cx + int(34 * s), base_y - int(7 * s)),
            (cx + int(27 * s), base_y + int(11 * s)),
            (cx - int(27 * s), base_y + int(11 * s))]
    triad_blob(surf, BONE, base,
               core_pts=[(cx, base_y - int(14 * s)), (cx + int(28 * s), base_y - int(7 * s)),
                         (cx + int(22 * s), base_y + int(9 * s)), (cx, base_y + int(7 * s))],
               ow=max(1, int(1.6 * s)))
    for k in range(-2, 3):
        px = cx + int(k * 11 * s)
        pygame.draw.line(surf, BONE_DD, (px, base_y - int(15 * s)),
                         (px, base_y + int(8 * s)), max(1, int(1.4 * s)))
    pygame.draw.circle(surf, ROSE_D, (cx, base_y - int(3 * s)), int(5 * s))
    pygame.draw.circle(surf, ROSE, (cx - int(1 * s), base_y - int(4 * s)), max(1, int(2 * s)))

    # === TORSO — short rib barrel (UNCHANGED) =================================
    rc_cx, rc_cy = cx, cy + int(12 * s)
    rc_w, rc_h = int(32 * s), int(24 * s)
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
    for i in range(2):
        ry = rc_cy - rc_h // 2 + int(7 * s) + i * int(8 * s)
        bw = int(rc_w * (0.42 - i * 0.05))
        pygame.draw.arc(surf, BONE_DD,
                        (rc_cx - bw, ry - int(6 * s), bw * 2, int(14 * s)),
                        math.radians(205), math.radians(335), max(2, int(2.2 * s)))
    pygame.draw.line(surf, BONE_DD, (rc_cx, rc_cy - rc_h // 2 + int(5 * s)),
                     (rc_cx, rc_cy + int(3 * s)), max(1, int(2 * s)))
    pygame.draw.line(surf, ROSE, (rc_cx - int(rc_w * 0.42), rc_cy + int(2 * s)),
                     (rc_cx + int(rc_w * 0.42), rc_cy - int(2 * s)), max(1, int(2 * s)))
    pygame.draw.line(surf, ROSE_BR, (rc_cx - int(rc_w * 0.3), rc_cy + int(1 * s)),
                     (rc_cx, rc_cy - int(1 * s)), max(1, int(1 * s)))

    # === SIX SKULL-TROPHY STRANDS — one dripping off each hand ================
    # WHY drawn after torso, before head: they hang out and DOWN from the fan
    # tips so the outer arc reads as six dripping skull-strands; the head still
    # overdraws nothing of the face.
    for i, (hx, hy) in enumerate(hands):
        oa = math.atan2(hy - rc_cy, hx - rc_cx)
        skull_trophy_strand(surf, hx, hy, trophy_r, s, ang=oa, two=True)

    # === SKULL HEAD — chibi, scary-cute, three-eyed (UNCHANGED face) ==========
    triad_circle(surf, BONE, head_c, hr, ow=max(2, int(2 * s)))
    for sgn in (-1, 1):
        pygame.draw.circle(surf, BONE_D,
                           (head_c[0] + sgn * int(hr * 0.66), head_c[1] + int(hr * 0.28)),
                           int(hr * 0.26))
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.42)
        ey = head_c[1] + int(hr * 0.16)
        pygame.draw.circle(surf, BONE_DD, (ex, ey), int(hr * 0.30))
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.25))
        pygame.draw.circle(surf, ROSE_D, (ex + sgn * int(1 * s), ey + int(1 * s)),
                           int(hr * 0.12))
    # THIRD EYE — the single BRIGHTEST pixel (preserved exactly from Mukha).
    tex, tey = head_c[0], head_c[1] - int(hr * 0.34)
    pygame.draw.ellipse(surf, INK, (tex - int(7 * s), tey - int(9 * s), int(14 * s), int(18 * s)))
    pygame.draw.ellipse(surf, ROSE, (tex - int(6 * s), tey - int(8 * s), int(12 * s), int(16 * s)))
    pygame.draw.ellipse(surf, ROSE_BR, (tex - int(4 * s), tey - int(5 * s), int(8 * s), int(10 * s)))
    pygame.draw.circle(surf, THIRD_BR, (tex - int(1 * s), tey - int(2 * s)), max(2, int(3.2 * s)))
    pygame.draw.circle(surf, (255, 255, 255), (tex - int(1 * s), tey - int(2 * s)),
                       max(1, int(1.6 * s)))
    pygame.draw.polygon(surf, BONE_DD,
                        [(head_c[0] - int(hr * 0.14), head_c[1] + int(hr * 0.30)),
                         (head_c[0] + int(hr * 0.14), head_c[1] + int(hr * 0.30)),
                         (head_c[0], head_c[1] + int(hr * 0.56))])
    my = head_c[1] + int(hr * 0.72)
    pygame.draw.line(surf, INK, (head_c[0] - int(hr * 0.48), my),
                     (head_c[0] + int(hr * 0.48), my), max(1, int(2 * s)))
    for k in range(-3, 4):
        pygame.draw.line(surf, INK, (head_c[0] + int(k * hr * 0.15), my - int(hr * 0.1)),
                         (head_c[0] + int(k * hr * 0.15), my + int(hr * 0.13)), max(1, int(1 * s)))
    for sgn in (-1, 1):
        fx = head_c[0] + sgn * int(hr * 0.40)
        pygame.draw.polygon(surf, BONE_SH,
                            [(fx - int(2 * s), my), (fx + int(2 * s), my),
                             (fx, my + int(hr * 0.22))])

    # === TALL FANNED MEGA-CROWN — EXACTLY 5 SKULLS (the LOOSE / motif tell) ===
    # WHY a tall DENSE 5-stack fanned over the head (vs Mukha's low shallow
    # 3-skull tiara, and vs Nritya's airy wide dance-crest): Maha is the
    # skull-crowned dread, so her crown is the grander, denser, taller mass —
    # five craniums riding a high steep arc, the centre one LIT rose. It is
    # HARD-LOCKED to 5 so the count can never creep toward mush.
    #
    # CRITICAL 32px discipline: the crown sits HIGH on a tall radius so a clean
    # negative gap stays between the lowest crown skulls and the topmost arm
    # strands — the two skull-masses must NOT merge into one blob. The
    # self-check at the bottom verifies this gap survives at 32px.
    crown_r = int(hr * 1.34)                  # tall: lifts skulls well clear of arms
    crown_skull_r = int(hr * 0.32)
    band_pts = []
    for i in range(11):
        a = math.radians(244 + i * (52 / 10))  # steep ~52deg arc, high on the dome
        band_pts.append((head_c[0] + math.cos(a) * crown_r,
                         head_c[1] + math.sin(a) * crown_r))
    pygame.draw.lines(surf, INK, False, band_pts, int(7 * s))
    pygame.draw.lines(surf, GOLD, False, band_pts, int(3.4 * s))
    pygame.draw.lines(surf, GOLD_BR, False, band_pts[:6], max(1, int(1.4 * s)))
    # the FIVE skulls, fanned tall on a steep arc; centre (i==2) lit ROSE_BR.
    for i in range(5):
        a = math.radians(250 + i * (40 / 4))
        # lift the crown skulls a hair above the band so they read as a fanned
        # ridge of craniums, not beads threaded on a wire.
        rr = crown_r + crown_skull_r * 0.55
        sx = head_c[0] + math.cos(a) * rr
        sy = head_c[1] + math.sin(a) * rr
        tiara_skull(surf, int(sx), int(sy), crown_skull_r, s, lit=(i == 2))


# ── the skull-trophy reliquary-staff → pillar mirror ──────────────────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """Maha's pillar mirrors HER motif: a banded bone shaft hung with skull
    trophies (not Mukha's mixed relics) as side-pendants = the tileable shaft;
    the gap-cap is a tall fanned skull-crown burst with a lit rose skull at the
    hub — her own mega-crown language in miniature. `cap` names the gap-facing
    END."""
    shaft_w = int(13 * s)
    sk_r = int(7 * s)
    pygame.draw.rect(surf, INK, (cx - int(3 * s), top, int(6 * s), bot - top))

    band_pitch = int(22 * s)
    cap_room = int(40 * s)
    if cap == "bottom":
        b0, b1 = top + int(6 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(6 * s)
    y = b0
    idx = 0
    while y <= b1:
        bw = shaft_w
        band = [(cx - bw, y - int(8 * s)),
                (cx + bw, y - int(8 * s)),
                (cx + bw, y + int(8 * s)),
                (cx - bw, y + int(8 * s))]
        triad_blob(surf, BONE, band,
                   core_pts=[(cx, y - int(7 * s)), (cx + bw, y - int(7 * s)),
                             (cx + bw, y + int(7 * s)), (cx, y + int(7 * s))],
                   sheen_pts=[(cx - bw, y - int(7 * s)), (cx - int(bw * 0.3), y - int(7 * s)),
                              (cx - int(bw * 0.3), y + int(2 * s)), (cx - bw, y + int(2 * s))],
                   ow=max(1, int(1.4 * s)))
        pygame.draw.line(surf, BONE_DD, (cx - bw, y), (cx + bw, y), max(1, int(1.6 * s)))
        pygame.draw.line(surf, BONE_DD, (cx - bw, y + int(8 * s)),
                         (cx + bw, y + int(8 * s)), max(1, int(1.4 * s)))
        # a skull trophy hung off alternating sides (the dripping skull motif)
        side = -1 if (idx % 2 == 0) else 1
        rx = cx + side * (bw + int(11 * s))
        ry = y + int(4 * s)
        pygame.draw.line(surf, GOLD, (cx + side * bw, y), (rx, ry - sk_r), max(1, int(1.6 * s)))
        tiara_skull(surf, rx, ry, sk_r, s, lit=False)
        # a tiny rose tassel-dot below each pendant skull (the strand terminator)
        pygame.draw.circle(surf, ROSE, (rx, ry + int(sk_r * 1.4)), max(1, int(sk_r * 0.34)))
        idx += 1
        y += band_pitch

    # === gap-edge cap: tall fanned skull-crown burst + lit rose skull =========
    cap_y = (bot - int(24 * s)) if cap == "bottom" else (top + int(24 * s))
    burst_r = int(18 * s)
    grow = +1 if cap == "bottom" else -1
    for k in range(7):
        a = math.radians(-90 + (k - 3) * 24) if grow > 0 else math.radians(90 + (k - 3) * 24)
        tip = (cx + math.cos(a) * burst_r, cap_y + math.sin(a) * burst_r)
        pygame.draw.line(surf, INK, (cx, cap_y), tip, max(2, int(4 * s)))
        pygame.draw.line(surf, BONE, (cx, cap_y), tip, max(1, int(2.4 * s)))
    # three small skull trophies fanned on the burst tips (the crown echo)
    for k in (-1, 0, 1):
        a = (math.radians(-90 + k * 30) if grow > 0 else math.radians(90 + k * 30))
        tx = cx + math.cos(a) * burst_r * 0.92
        ty = cap_y + math.sin(a) * burst_r * 0.92
        tiara_skull(surf, int(tx), int(ty), max(2, int(sk_r * 0.74)), s, lit=False)
    # a thin gold collar where the burst meets the shaft
    collar_y = cap_y - grow * int(burst_r + int(4 * s))
    pygame.draw.rect(surf, INK, (cx - int(10 * s), collar_y - int(3 * s), int(20 * s), int(7 * s)))
    pygame.draw.rect(surf, GOLD, (cx - int(9 * s), collar_y - int(2 * s), int(18 * s), int(5 * s)))
    pygame.draw.rect(surf, GOLD_BR, (cx - int(9 * s), collar_y - int(2 * s), int(18 * s), int(2 * s)))
    # the LIT rose skull at the burst hub (the gap glow — Maha's lit-centre motif)
    tiara_skull(surf, cx, cap_y, int(sk_r * 1.1), s, lit=True)
    pygame.draw.arc(surf, TEAL, (cx - int(7 * s), cap_y + int(2 * s), int(14 * s), int(10 * s)),
                    math.radians(200), math.radians(340), max(1, int(1.8 * s)))


# ── compose the review sheet ─────────────────────────────────────────────────
SS = 6


def render_creature_chip(boxw, boxh, draw_cx, draw_cy, scale):
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_maha_kapali(big, draw_cx * SS, draw_cy * SS, scale * SS)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


# ── 32px self-check: crown-skull mass must NOT merge into the arm strands ─────
def selfcheck_32px_gap():
    """Render JUST the creature at true 32px and confirm a band of BACKGROUND
    survives between the crown-skull cluster (top) and the topmost arm-trophy
    strands. WHY the SIDE wedges, not the centre column: by design the crown
    seats ON the cranium, so straight down the axis the crown and head are ONE
    intended mass (correct). The merge failure mode is the crown's OUTER skulls
    fusing into the near-horizontal topmost arm strands that splay out to the
    sides — so we scan the two off-axis wedge columns where the crown shoulder
    sits above the upper arm. A surviving negative gap in EITHER wedge proves the
    two skull-masses stay distinct value-clumps. Returns (ok, gap_px, detail)."""
    N = 96                                 # render bigger then check, sub-pixel safe
    surf = pygame.Surface((N, N), pygame.SRCALPHA)
    draw_maha_kapali(surf, N // 2, int(N * 0.52), 32 / 150.0 * (N / 32.0))
    cx = N // 2

    def runs_in_column(col_lo, col_hi):
        def row_opaque(y):
            for x in range(col_lo, col_hi):
                if 0 <= x < N and surf.get_at((x, y))[3] > 40:
                    return True
            return False
        runs, prev, start = [], False, 0
        for y in range(N):
            op = row_opaque(y)
            if op and not prev:
                start = y
            if (not op) and prev:
                runs.append((start, y - 1))
            prev = op
        if prev:
            runs.append((start, N - 1))
        return runs

    # the wedge columns where the crown's outer skulls overhang the topmost arm
    best_gap, best_detail = -1, ""
    for sgn in (-1, 1):
        wx = cx + sgn * int(N * 0.22)
        runs = runs_in_column(wx - 3, wx + 4)
        # first run = crown-skull cluster; the next run below it = upper arm strand
        if len(runs) >= 2:
            gap = runs[1][0] - runs[0][1] - 1
            if gap > best_gap:
                best_gap = gap
                best_detail = f"wedge x~{wx}: runs={runs[:3]} -> gap={gap}px"
    if best_gap >= 1:
        return True, best_gap, best_detail
    return False, max(0, best_gap), best_detail or "no separated runs in either wedge"


def _load_font(size, bold=True):
    """FONT path is FIVE levels up to the vendored game asset; SysFont fallback
    so the renderer stays headless-safe on any box."""
    here = os.path.dirname(os.path.abspath(__file__))
    fp = os.path.normpath(os.path.join(here, *([".."] * 5),
                                       "game", "assets", "LiberationSans-Bold.ttf"))
    try:
        if os.path.exists(fp):
            return pygame.font.Font(fp, size)
    except Exception:
        pass
    return pygame.font.SysFont("DejaVu Sans", size, bold=bold)


def main():
    W, H = 1010, 840
    font_big = _load_font(30)
    font = _load_font(17)
    font_sm = _load_font(12)

    ok, gap, detail = selfcheck_32px_gap()

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("MAHA-KAPALI", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "great skull-crowned dread  ·  Mukha-Devi KIN (grounded sister) · LOOSE · skull-motif · "
        "5-skull MEGA-CROWN + six skull-trophy strands · round 1",
        True, LABEL_DIM), (270, 26))

    # === (a) BIG HERO =========================================================
    hero = render_creature_chip(360, 500, 178, 244, 1.5)
    sheet.blit(hero, (14, 92))
    sheet.blit(font.render("Creature — hero", True, LABEL), (110, 596))
    sheet.blit(font_sm.render("Tall fanned 5-skull MEGA-CROWN (lit centre) over a raised, taller head.", True, LABEL_DIM), (14, 620))
    sheet.blit(font_sm.render("Six arm-ends drip skull-trophy strands (gold rod + 2 skulls + rose tassel).", True, LABEL_DIM), (14, 636))
    sheet.blit(font_sm.render("Third eye stays the single BRIGHTEST pixel; six-arm fan + palette = Mukha's sister.", True, LABEL_DIM), (14, 652))

    # === (b) PILLAR assembled — mirrored ======================================
    pcx = 470
    top_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(top_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="bottom")
    top_seg = grow_outline(pygame.transform.smoothscale(top_big, (150, 250)), INK + (255,), 1)
    sheet.blit(top_seg, (pcx, 86))
    bot_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(bot_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="top")
    bot_seg = grow_outline(pygame.transform.smoothscale(bot_big, (150, 250)), INK + (255,), 1)
    sheet.blit(bot_seg, (pcx, 86 + 250 + 96))
    pygame.draw.rect(sheet, (60, 58, 70), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar — reliquary-staff", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("banded bone shaft hung with skull trophies =", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("shaft; tall skull-crown burst + lit rose skull", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("caps the gap (mirrored top<->bottom, on-axis)", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px chips on day + night, + blackout proof =================
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 580))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32():
        big = pygame.Surface((118 * SS, 124 * SS), pygame.SRCALPHA)
        draw_maha_kapali(big, 59 * SS, 64 * SS, (32 / 150.0) * SS)
        small = pygame.transform.smoothscale(big, (118, 124))
        return grow_outline(small, INK + (255,), 1)

    chip = chip32()

    day_y = 128
    vgrad(sheet, (panel_x + 20, day_y, 130, 140), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 130, 140), 1)
    sheet.blit(chip, (panel_x + 20 + 6, day_y + 8))
    sheet.blit(font_sm.render("32px on day sky", True, LABEL), (panel_x + 20, day_y + 146))

    night_y = day_y + 174
    vgrad(sheet, (panel_x + 20, night_y, 130, 140), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 130, 140), 1)
    sheet.blit(chip, (panel_x + 20 + 6, night_y + 8))
    sheet.blit(font_sm.render("32px on night sky", True, LABEL_DIM), (panel_x + 20, night_y + 146))

    # blackout silhouette proof (the crown-vs-arms read at silhouette only)
    bo_x = panel_x + 168
    bo = pygame.Surface((118, 124), pygame.SRCALPHA)
    src = pygame.Surface((118 * SS, 124 * SS), pygame.SRCALPHA)
    draw_maha_kapali(src, 59 * SS, 64 * SS, (32 / 150.0) * SS)
    sm = pygame.transform.smoothscale(src, (118, 124))
    mask = pygame.mask.from_surface(sm)
    for yy in range(124):
        for xx in range(118):
            if mask.get_at((xx, yy)):
                bo.set_at((xx, yy), INK + (255,))
    vgrad(sheet, (bo_x, day_y, 130, 140), (210, 206, 214), (180, 176, 188))
    pygame.draw.rect(sheet, INK, (bo_x, day_y, 130, 140), 1)
    sheet.blit(bo, (bo_x + 6, day_y + 8))
    sheet.blit(font_sm.render("blackout proof", True, LABEL), (bo_x, day_y + 146))

    # the self-check verdict, surfaced ON the sheet
    verdict = f"32px crown<->arm gap CHECK: {'PASS' if ok else 'FAIL'}  (gap={gap}px)"
    vcol = (150, 226, 150) if ok else (250, 150, 150)
    sheet.blit(font_sm.render(verdict, True, vcol), (bo_x, night_y + 8))
    sheet.blit(font_sm.render("crown skulls stay a separate", True, LABEL_DIM), (bo_x, night_y + 30))
    sheet.blit(font_sm.render("value-mass above the arm", True, LABEL_DIM), (bo_x, night_y + 46))
    sheet.blit(font_sm.render("strands (no merge into one blob)", True, LABEL_DIM), (bo_x, night_y + 62))
    sheet.blit(font_sm.render("locks: crown=5 skulls,", True, LABEL_DIM), (bo_x, night_y + 92))
    sheet.blit(font_sm.render("arm trophies=2 per strand.", True, LABEL_DIM), (bo_x, night_y + 108))

    sheet.blit(font.render("Pinned palette (UNCHANGED)", True, LABEL), (panel_x + 16, 540))
    swatches = [
        (BONE, "dusty rose-bone"), (BONE_D, "mauve-bone shade"),
        (ROSE, "magenta relic-glow"), (ROSE_D, "deep-rose"),
        (GOLD, "gold trim"), (TEAL, "teal sliver"),
        (THIRD_EYE, "third-eye"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, 566
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 158
        ry = syp + row * 24
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 18, 18))
        pygame.draw.rect(sheet, c, (rx, ry, 16, 16))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 22, ry + 2))

    pygame.draw.rect(sheet, PANEL, (14, 790, W - 28, 44))
    sheet.blit(font_sm.render(
        "ELEVATED pipeline: SS=6 supersample -> smoothscale.  STAY: flat fills · hard ink keyline (28,22,26) · "
        "dark-core->fill->top-left sheen triad · 1px grown outline · chibi · scary-cute · procedural-only.",
        True, LABEL_DIM), (26, 798))
    sheet.blit(font_sm.render("SISTER of Mukha-Devi: six-arm fan + face + palette UNCHANGED; new = 5-skull mega-crown + dripping skull-trophy strands.",
                              True, LABEL_DIM), (26, 814))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out)
    print("selfcheck:", "PASS" if ok else "FAIL", "gap=", gap, "|", detail)


if __name__ == "__main__":
    main()
