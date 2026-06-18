"""
Round-1 concept renderer for ASTHI-DAKINI — the bone-jewel sky-dancer
(mukha_citipati_court brood, sister #1). Headless Pygame; ELEVATED pipeline
(SS=8 supersample → smoothscale) so the dense multi-strand bead-lattice survives
the downscale. Keeps the shipped house grammar: flat saturated fills, hard 1-2px
ink keyline (28,22,26), dark-core → flat-fill → top-left rim-sheen triad, 1px
alpha-grown outline, chibi proportions, scary-CUTE; procedural-only.

WHY this sister is the bead-jewel dancer: she fuses the CITIPATI body (tall
rib-barrel dancing torso, cocked hip, flamenco-flourish) with the MUKHA six-arm
radial fan — every one of the six open palms cradles a tiny skull. Her non-naked
density is multi-strand bone-BEAD jewelry: a 3-row choker, a long swag necklace,
beaded armlets/bracelets/anklets, wheel earrings, and a bold beaded girdle. A
bead-lattice wraps every surface.

WHY the palette is pushed DARKER (~120,134,162) cool moonlit bone: the #1
tonal-collapse risk is low-chroma beads on low-chroma bone reading as a grey
smear ("naked in disguise"). The fix the AD pinned: darken the bone field so the
bead lattice reads LIGHT-on-dark, and CARRY the texture with WARM gold spacer-pips
between the cool bone beads — value AND hue separation, colourblind-safe — so the
contrast is never only cyan-on-blue.

WHY the fused crown shows BOTH languages: a plain skull-arc alone reads as the
Citipati reference, so the crown seats the Mukha tiara-BAND across the brow AND
sweeps the wide airy 6-skull arc above it. Crown skulls are a notch warmer/darker
than the body so they hold against open sky.

Value ladder (AD hard rule): cyan third-eye slit = single brightest pixel → the
six palm-skulls = mid → crown skulls = dimmest. Glow ONLY on the third-eye + the
crown-centre skull.

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

# WHY the vendored font over SysFont: review sheets must read identically on the
# headless CI box where no system fonts are guaranteed; the shipped Liberation
# face is always present, five dirs up from the sister folder in game/assets/.
_FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "..", "..", "..", "..", "..",
                          "game", "assets", "LiberationSans-Bold.ttf")
_FONT_PATH = os.path.abspath(_FONT_PATH)


def font(sz):
    if os.path.exists(_FONT_PATH):
        return pygame.font.Font(_FONT_PATH, sz)
    return pygame.font.SysFont("DejaVu Sans", sz, bold=True)


# ── PINNED PALETTE (locked brief) ─────────────────────────────────────────────
# Cool moonlit bone pushed DARKER so the bead lattice + gold spacer-pips read
# LIGHT-on-dark. Beads (BEAD/BEAD_BR) and warm gold pips (GOLD/GOLD_BR) sit a full
# value step above the bone field — value + hue separation, never cyan-on-blue.
BONE      = (120, 134, 162)   # cool moonlit bone, DARKENED (the dominant field)
BONE_D    = ( 84,  96, 122)   # bone dark-core / shade
BONE_DD   = ( 54,  64,  86)   # deepest bone hollow (sockets, rib gaps)
BONE_SH   = (176, 190, 214)   # bone top-left rim-sheen
BEAD      = (196, 208, 226)   # pale bone bead — reads light on the dark bone
BEAD_BR   = (228, 238, 250)   # bead top sheen / hottest bone bead
CYAN      = ( 86, 214, 226)   # icy-cyan — third-eye + sparse jewel cabochons
CYAN_BR   = (188, 248, 252)   # hot cyan inner
CYAN_D    = ( 40, 132, 150)
GOLD      = (220, 178,  86)   # WARM gold spacer-pips (the hue/value separator)
GOLD_BR   = (248, 214, 124)
GOLD_D    = (168, 124,  52)
INK       = ( 28,  22,  26)   # hard ink keyline
# crown skulls a notch WARMER + DARKER than the cool body so they hold their own
# shape against open sky (don't melt into a day sky or vanish on night).
CROWN_BONE   = (150, 142, 130)
CROWN_BONE_D = (104,  96,  86)
CROWN_SH     = (196, 188, 174)
THIRD_EYE = CYAN              # cyan third-eye slit = the single brightest focal

BG        = ( 92,  96, 108)   # neutral grey review backdrop
PANEL     = ( 70,  74,  86)
DAY_SKY_T = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)   # night biome sky (top)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (238, 240, 246)
LABEL_DIM = (190, 198, 212)


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


# ── bone-bead strand — the brood's non-naked density device ───────────────────
def bead_strand(surf, pts, bead_r, s, gold_every=3, pip_r_frac=0.42, light=True):
    """A strand of pale bone beads threaded along a polyline, with WARM gold
    spacer-pips every `gold_every` beads. WHY: the whole tonal-collapse fix lives
    here — pale beads read LIGHT on the dark bone field, and the periodic gold pip
    injects a warm hue so the strand never collapses to cyan-on-blue. Beads are
    spaced evenly by arc length so the lattice stays regular at downscale."""
    if len(pts) < 2:
        return
    # accumulate arc length and walk it, dropping a bead every 2*bead_r
    segs = []
    total = 0.0
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        d = math.hypot(b[0] - a[0], b[1] - a[1])
        segs.append((a, b, d))
        total += d
    pitch = max(1.0, bead_r * 1.85)
    n = max(1, int(total / pitch))
    idx = 0
    for k in range(n + 1):
        target = k * pitch
        # find the segment containing this arc position
        acc = 0.0
        bx, by = pts[0]
        for (a, b, d) in segs:
            if acc + d >= target or (a, b, d) is segs[-1]:
                t = (target - acc) / max(1e-6, d)
                t = max(0.0, min(1.0, t))
                bx = a[0] + (b[0] - a[0]) * t
                by = a[1] + (b[1] - a[1]) * t
                break
            acc += d
        if idx % gold_every == 0:
            # warm gold spacer-pip (smaller, the hue separator)
            triad_circle(surf, GOLD, (int(bx), int(by)), max(1, int(bead_r * (0.6 + pip_r_frac))),
                         ow=max(1, int(1.0 * s)), core=False)
            pygame.draw.circle(surf, GOLD_BR, (int(bx - bead_r * 0.2), int(by - bead_r * 0.2)),
                               max(1, int(bead_r * 0.22)))
        else:
            col = BEAD if light else BONE
            triad_circle(surf, col, (int(bx), int(by)), max(1, int(bead_r)),
                         ow=max(1, int(1.0 * s)), core=False)
            pygame.draw.circle(surf, BEAD_BR, (int(bx - bead_r * 0.28), int(by - bead_r * 0.30)),
                               max(1, int(bead_r * 0.30)))
        idx += 1


def bead_arc(surf, cx, cy, r, a0, a1, bead_r, s, gold_every=3, light=True):
    """Convenience wrapper — a bead strand laid along a circular arc."""
    steps = max(2, int(abs(a1 - a0) / 0.18))
    pts = [(cx + math.cos(a0 + (a1 - a0) * i / steps) * r,
            cy + math.sin(a0 + (a1 - a0) * i / steps) * r) for i in range(steps + 1)]
    bead_strand(surf, pts, bead_r, s, gold_every=gold_every, light=light)


# ── a single ornamental crown-skull (cloned from Citipati; crown-warm tint) ────
def crown_skull(surf, cx, cy, r, s, lit=False):
    """Tiny warm-bone skull — domed cranium, two dark sockets, a stub jaw. WHY a
    notch warmer/darker than the body (CROWN_BONE): the cool body palette would
    let cool crown skulls vanish against the day sky, so the crown carries its own
    slightly warm value. `lit` swaps the centre skull's eyes + a soft cyan halo on
    — the ONLY crown glow allowed (value-ladder dimmest tier otherwise)."""
    # no glow bloom — the only cyan glow on the figure is the faceted brow third-eye
    # gem (the weird blue auras are gone); `lit` only tints the centre skull's eyes.
    triad_circle(surf, CROWN_BONE, (cx, cy), r, ow=max(1, int(1.6 * s)), core=False)
    jaw = [(cx - int(r * 0.52), cy + int(r * 0.52)),
           (cx + int(r * 0.52), cy + int(r * 0.52)),
           (cx + int(r * 0.34), cy + int(r * 1.0)),
           (cx - int(r * 0.34), cy + int(r * 1.0))]
    triad_blob(surf, CROWN_BONE, jaw, ow=max(1, int(1.2 * s)))
    eye_c = CYAN_BR if lit else INK
    for ex in (cx - int(r * 0.38), cx + int(r * 0.38)):
        pygame.draw.circle(surf, INK, (ex, cy + int(r * 0.04)), max(1, int(r * 0.24)))
        if lit:
            pygame.draw.circle(surf, eye_c, (ex, cy + int(r * 0.04)), max(1, int(r * 0.13)))
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.42)), max(1, int(r * 0.13)))
    pygame.draw.line(surf, INK,
                     (cx - int(r * 0.34), cy + int(r * 0.70)),
                     (cx + int(r * 0.34), cy + int(r * 0.70)),
                     max(1, int(1.2 * s)))


# ── a tiny skull cradled in an open palm (the brood MOTIF) ────────────────────
def palm_skull(surf, cx, cy, r, s):
    """An open BONE palm cradling a TINY skull. WHY both pieces: the brood motif
    is six open palms EACH holding a skull, sitting at the fan tips. The palm is a
    shallow bone cup; the skull rides in it, sized to the MID value tier (brighter
    than the crown skulls, dimmer than the third-eye)."""
    # open palm cup — a shallow bone bowl with finger-ticks fanning up
    cup = [(cx - int(r * 1.05), cy + int(r * 0.30)),
           (cx - int(r * 0.70), cy + int(r * 0.78)),
           (cx + int(r * 0.70), cy + int(r * 0.78)),
           (cx + int(r * 1.05), cy + int(r * 0.30)),
           (cx + int(r * 0.75), cy + int(r * 0.10)),
           (cx - int(r * 0.75), cy + int(r * 0.10))]
    triad_blob(surf, BONE, cup, ow=max(1, int(1.2 * s)))
    for k in range(-2, 3):
        fx = cx + int(k * r * 0.40)
        pygame.draw.line(surf, INK, (fx, cy + int(r * 0.20)),
                         (fx + int(k * r * 0.10), cy - int(r * 0.20)), max(1, int(2.0 * s)))
        pygame.draw.line(surf, BONE_SH, (fx, cy + int(r * 0.18)),
                         (fx + int(k * r * 0.10), cy - int(r * 0.16)), max(1, int(1.0 * s)))
    # the cradled tiny skull (MID value — pale bone dome, sits above the crown tier)
    sk = (cx, cy - int(r * 0.32))
    triad_circle(surf, BEAD, sk, int(r * 0.62), ow=max(1, int(1.4 * s)), core=False)
    for ex in (sk[0] - int(r * 0.26), sk[0] + int(r * 0.26)):
        pygame.draw.circle(surf, INK, (ex, sk[1] + int(r * 0.02)), max(1, int(r * 0.16)))
    pygame.draw.circle(surf, INK, (sk[0], sk[1] + int(r * 0.24)), max(1, int(r * 0.09)))
    jaw = [(sk[0] - int(r * 0.30), sk[1] + int(r * 0.40)),
           (sk[0] + int(r * 0.30), sk[1] + int(r * 0.40)),
           (sk[0] + int(r * 0.20), sk[1] + int(r * 0.66)),
           (sk[0] - int(r * 0.20), sk[1] + int(r * 0.66))]
    triad_blob(surf, BEAD, jaw, ow=max(1, int(1.0 * s)))


# ── the Mukha-Devi six-arm radial fan (cloned; bead-armlet wrapped) ───────────
def draw_arm_fan(surf, sh_cx, sh_cy, s, hr, arm_th_frac=0.16):
    """Six fat bone arms splay in a wide symmetric STARBURST around the torso —
    the ONLY radial silhouette in the brood. Low-origin, ~[100,64,28]° off the
    vertical, NONE straight up → the crown sky stays open. WHY beaded armlets:
    this sister wraps every surface, so each arm carries a bone-bead bracelet at
    the wrist + an armlet near the shoulder. Returns the six hand centres + their
    outward angles for palm-skull placement."""
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
                       ow=max(1, int(arm_th * arm_th_frac)))
        triad_circle(surf, BONE, (int(elbow[0]), int(elbow[1])), int(arm_th * 0.55),
                     ow=max(1, int(1.2 * s)), core=False)
        # beaded armlet (near the elbow) + bracelet (at the wrist) wrapping the arm
        for frac, br in ((0.62, 0.55), (0.92, 0.62)):
            wx = sh[0] + (hand[0] - sh[0]) * frac
            wy = sh[1] + (hand[1] - sh[1]) * frac
            perp = a + math.pi / 2
            band_r = arm_th * 0.80
            p0 = (wx + math.cos(perp) * band_r, wy + math.sin(perp) * band_r)
            p1 = (wx - math.cos(perp) * band_r, wy - math.sin(perp) * band_r)
            bead_strand(surf, [p0, p1], arm_th * br * 0.42, s, gold_every=2)
        hands.append((sgn, d, hand, a))
    hands.sort(key=lambda h: (h[0], -h[1]))
    return [(int(h[2][0]), int(h[2][1]), h[3]) for h in hands]


# ── a FACETED cyan cut-stone GEM — asthi's contained jewel (current-design focal) ──
def cyan_gem(surf, c, r, s, focal=False):
    """A CUT cyan jewel built from FLAT FACET PLANES, not a glossy sphere — a facet
    ROSETTE: a flat angular TABLE polygon at the crown, ringed by angled crown facets
    that radiate from the table edge out to the bezel, each a FILLED polygon in a
    stepped cyan value so adjacent planes meet at SHARP corners. Hard glints are tiny
    white TRIANGLES pinned at facet corners. `focal` is the brow third-eye: it alone
    gets the white hot core + 3 glints and shows ONLY its octagonal faceted stone (no
    circular background)."""
    cx, cy = int(c[0]), int(c[1])
    # the focal brow gem shows only its faceted stone (no circular background); a
    # non-focal palm gem keeps an ink seat to read against bone.
    if not focal:
        pygame.draw.circle(surf, INK, (cx, cy), r + max(1, int(1.4 * s)))

    # the crown girdle outline — a faceted POLYGON (octagonal), NOT a circle: the
    # straight-edged girdle kills the round-lens read at the silhouette.
    def gpt(ang_deg, rad):
        a = math.radians(ang_deg)
        return (cx + math.cos(a) * rad, cy + math.sin(a) * rad)
    n_crown = 8
    girdle = [gpt(-90 + i * (360 / n_crown), r) for i in range(n_crown)]
    pygame.draw.polygon(surf, CYAN_D, girdle)

    # the flat TABLE face — a smaller angular polygon offset UP toward the crown.
    table_r = r * 0.46
    tcx, tcy = cx, cy - int(r * 0.10)
    table = [(tcx + math.cos(math.radians(-90 + i * (360 / n_crown))) * table_r,
              tcy + math.sin(math.radians(-90 + i * (360 / n_crown))) * table_r)
             for i in range(n_crown)]

    # the CROWN FACETS — one filled trapezoid bridging each girdle edge to the table
    # edge, light-direction value steps so neighbours never share a tone.
    for i in range(n_crown):
        g0, g1 = girdle[i], girdle[(i + 1) % n_crown]
        t0, t1 = table[i], table[(i + 1) % n_crown]
        mx = (g0[0] + g1[0]) * 0.5 - cx
        my = (g0[1] + g1[1]) * 0.5 - cy
        facing = -(mx * 0.7 + my * 0.7) / max(1.0, r)
        if facing > 0.35:
            fc = CYAN_BR
        elif facing > -0.15:
            fc = CYAN
        else:
            fc = lerp(CYAN, CYAN_D, 0.6)
        pygame.draw.polygon(surf, fc, [g0, g1, t1, t0])
        pygame.draw.polygon(surf, INK, [g0, g1, t1, t0], max(1, int(0.9 * s)))

    # the flat table plane on top — lighter than every crown facet so the eye lands
    # on the table, like a real cut stone.
    pygame.draw.polygon(surf, lerp(CYAN, CYAN_BR, 0.55), table)
    pygame.draw.polygon(surf, INK, table, max(1, int(0.9 * s)))
    pygame.draw.line(surf, CYAN_BR, table[0], table[n_crown // 2], max(1, int(0.8 * s)))

    # HARD specular glints — tiny white TRIANGLES pinned at facet corners.
    def glint(px, py, sz):
        pygame.draw.polygon(surf, (255, 255, 255),
                            [(px, py - sz), (px + sz, py + sz * 0.5),
                             (px - sz, py + sz * 0.5)])

    g = max(1, int(r * 0.16))
    glint(table[6][0], table[6][1], g)
    if focal:
        # the white HOT CORE — the single brightest pixel of the whole sprite.
        pygame.draw.polygon(surf, CYAN_BR,
                            [(tcx, tcy - int(r * 0.22)), (tcx + int(r * 0.20), tcy),
                             (tcx, tcy + int(r * 0.20)), (tcx - int(r * 0.20), tcy)])
        pygame.draw.circle(surf, (240, 255, 255), (tcx, tcy), max(2, int(r * 0.15)))
        pygame.draw.circle(surf, (255, 255, 255), (tcx - int(r * 0.04), tcy - int(r * 0.04)),
                           max(1, int(r * 0.08)))
        glint(girdle[1][0], girdle[1][1], max(1, int(r * 0.12)))
        glint(table[3][0], table[3][1], max(1, int(r * 0.11)))


# ── the bone-jewel sky-dancer ─────────────────────────────────────────────────
def draw_asthi_dakini(surf, cx, cy, s):
    """Cocked-hip dancing chibi skeleton (CITIPATI body) under a six-arm radial
    fan (MUKHA). Each of the six open palms cradles a tiny skull. A fused crown
    (Mukha tiara-band across the brow + wide airy 6-skull arc) tops the head, and
    a multi-strand bone-bead jewelry SET (3-row choker, swag necklace, armlets/
    bracelets/anklets, wheel earrings, beaded girdle) wraps every surface.
    `s` = unit scale around a ~130-unit figure."""

    head_c = (cx, cy - int(34 * s))
    hr = int(26 * s)
    hip_y = cy + int(24 * s)
    hip_cx = cx + int(7 * s)

    # === SIX-ARM RADIAL FAN (drawn first → behind torso & head) ===============
    hands = draw_arm_fan(surf, head_c[0], head_c[1] + int(hr * 0.92), s, hr)

    # === LEGS — cocked-hip dance, one knee kicked OUT (Citipati body) =========
    def bone_limb(p0, p1, p2, thick, joint=True):
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
            triad_circle(surf, BONE, p1, int(thick * 0.62), ow=max(1, int(1.2 * s)),
                         core=False)

    leg_th = int(14 * s)
    hipL = (hip_cx - int(13 * s), hip_y)
    kneeL = (hip_cx - int(20 * s), hip_y + int(26 * s))
    footL = (hip_cx - int(22 * s), hip_y + int(52 * s))
    bone_limb(hipL, kneeL, footL, leg_th)
    hipR = (hip_cx + int(11 * s), hip_y)
    kneeR = (hip_cx + int(30 * s), hip_y + int(8 * s))
    footR = (hip_cx + int(20 * s), hip_y + int(34 * s))
    bone_limb(hipR, kneeR, footR, leg_th)
    for (fx, fy), sgn in ((footL, -1), (footR, +1)):
        foot = [(fx - int(4 * s), fy - int(2 * s)), (fx + sgn * int(16 * s), fy + int(2 * s)),
                (fx + sgn * int(15 * s), fy + int(10 * s)), (fx - int(5 * s), fy + int(8 * s))]
        triad_blob(surf, BONE, foot, ow=max(1, int(1.4 * s)))
    # beaded ANKLETS — a bead band just above each foot (jewelry set, ankle tier)
    for (kx, ky), (fx, fy) in ((kneeL, footL), (kneeR, footR)):
        ax = fx + (kx - fx) * 0.32
        ay = fy + (ky - fy) * 0.32
        ang = math.atan2(ky - fy, kx - fx) + math.pi / 2
        ar = leg_th * 0.85
        bead_strand(surf, [(ax + math.cos(ang) * ar, ay + math.sin(ang) * ar),
                           (ax - math.cos(ang) * ar, ay - math.sin(ang) * ar)],
                    leg_th * 0.30, s, gold_every=2)

    # === PELVIS + RIBCAGE (Citipati torso) ====================================
    pelvis = [(hip_cx - int(17 * s), hip_y - int(4 * s)),
              (hip_cx + int(17 * s), hip_y - int(6 * s)),
              (hip_cx + int(14 * s), hip_y + int(10 * s)),
              (hip_cx, hip_y + int(13 * s)),
              (hip_cx - int(15 * s), hip_y + int(9 * s))]
    triad_blob(surf, BONE, pelvis,
               core_pts=[(hip_cx - int(6 * s), hip_y + int(2 * s)),
                         (hip_cx + int(14 * s), hip_y - int(2 * s)),
                         (hip_cx + int(13 * s), hip_y + int(9 * s)),
                         (hip_cx, hip_y + int(12 * s))],
               ow=max(1, int(1.6 * s)))
    pygame.draw.circle(surf, BONE_DD, (hip_cx, hip_y + int(2 * s)), int(4 * s))

    spine_top_y = cy - int(16 * s)
    spine = [(hip_cx, hip_y - int(2 * s)),
             (cx + int(2 * s), cy + int(6 * s)),
             (cx - int(1 * s), spine_top_y)]
    pygame.draw.lines(surf, INK, False, spine, int(8 * s))
    pygame.draw.lines(surf, BONE, False, spine, int(5 * s))

    rc_cx, rc_cy = cx, cy - int(4 * s)
    rc_w, rc_h = int(34 * s), int(40 * s)
    cage = [(rc_cx - rc_w // 2, rc_cy - rc_h // 2 + int(2 * s)),
            (rc_cx + rc_w // 2, rc_cy - rc_h // 2),
            (rc_cx + int(rc_w * 0.40), rc_cy + rc_h // 2),
            (rc_cx - int(rc_w * 0.40), rc_cy + rc_h // 2)]
    triad_blob(surf, BONE, cage,
               core_pts=[(rc_cx + int(2 * s), rc_cy - rc_h // 2 + int(3 * s)),
                         (rc_cx + rc_w // 2, rc_cy - rc_h // 2 + int(2 * s)),
                         (rc_cx + int(rc_w * 0.40), rc_cy + rc_h // 2),
                         (rc_cx + int(2 * s), rc_cy + rc_h // 2)],
               sheen_pts=[(rc_cx - rc_w // 2 + int(2 * s), rc_cy - rc_h // 2 + int(3 * s)),
                          (rc_cx - int(4 * s), rc_cy - rc_h // 2 + int(2 * s)),
                          (rc_cx - int(6 * s), rc_cy + int(6 * s)),
                          (rc_cx - rc_w // 2 + int(2 * s), rc_cy + int(4 * s))],
               ow=max(1, int(1.8 * s)))
    # 4 rib-band arcs (the Citipati torso motif)
    for i in range(4):
        ry = rc_cy - rc_h // 2 + int(8 * s) + i * int(8 * s)
        bw = int(rc_w * (0.46 - i * 0.05))
        pygame.draw.arc(surf, BONE_DD,
                        (rc_cx - bw, ry - int(7 * s), bw * 2, int(16 * s)),
                        math.radians(205), math.radians(335), max(2, int(2.4 * s)))
    pygame.draw.line(surf, BONE_DD, (rc_cx, rc_cy - rc_h // 2 + int(6 * s)),
                     (rc_cx, rc_cy + int(6 * s)), max(1, int(2 * s)))

    # === ARMS of the DANCE (flamenco flourish) wrapped in bead bracelets ======
    # WHY a flourish PAIR on top of the six-arm fan: the Citipati dance read needs
    # an asymmetric raised pair; the radial fan frames behind, this pair gestures.
    arm_th = int(8 * s)
    shoulderL = (rc_cx - int(16 * s), rc_cy - rc_h // 2 + int(6 * s))
    shoulderR = (rc_cx + int(16 * s), rc_cy - rc_h // 2 + int(5 * s))
    elbowL = (rc_cx - int(30 * s), rc_cy - int(18 * s))
    handL = (rc_cx - int(26 * s), rc_cy - int(40 * s))
    bone_limb(shoulderL, elbowL, handL, arm_th)
    elbowR = (rc_cx + int(30 * s), rc_cy - int(2 * s))
    handR = (rc_cx + int(40 * s), rc_cy + int(14 * s))
    bone_limb(shoulderR, elbowR, handR, arm_th)
    for (hx, hy), sgn, up in ((handL, -1, True), (handR, +1, False)):
        triad_circle(surf, BONE, (hx, hy), int(5 * s), ow=max(1, int(1.2 * s)), core=False)
        for k in range(-1, 3):
            ang = math.radians(-90 + k * 26) if up else math.radians(40 + k * 26)
            ex = hx + math.cos(ang) * int(9 * s)
            ey = hy + math.sin(ang) * int(9 * s)
            pygame.draw.line(surf, INK, (hx, hy), (ex, ey), max(1, int(1.6 * s)))
            pygame.draw.line(surf, BONE, (hx, hy), (ex, ey), max(1, int(1 * s)))

    # === SIX PALM-SKULLS — one cradled in every fan hand (the brood MOTIF) ====
    for (hx, hy, a) in hands:
        palm_skull(surf, hx, hy, int(11 * s), s)

    # === BEADED GIRDLE — the 32px-CARRYING element (bold rows across the hips) =
    # WHY this is the silhouette element: a wide bold double-row bead-girdle slung
    # across the pelvis collapses to two clean light bands at 32px, the single
    # heaviest ornament read that holds when the fine lattice mushes.
    g_y0 = hip_y - int(2 * s)
    for row, (yy, br) in enumerate(((g_y0, 0.0), (g_y0 + int(7 * s), 0.0))):
        bead_arc(surf, hip_cx, hip_y - int(20 * s), int(40 * s) + row * int(4 * s),
                 math.radians(58), math.radians(122), int(4.6 * s), s, gold_every=3)
    # girdle pendant tassel — a short bead drop at the centre front
    bead_strand(surf, [(hip_cx, g_y0 + int(8 * s)), (hip_cx, g_y0 + int(22 * s))],
                int(3.4 * s), s, gold_every=2)

    # === 3-ROW CHOKER + long SWAG NECKLACE (bold rows, the second 32px read) ==
    neck_y = rc_cy - rc_h // 2 - int(1 * s)
    for r_i in range(3):
        cy_row = neck_y + r_i * int(5 * s)
        bead_arc(surf, rc_cx, cy_row - int(4 * s), int(18 * s) + r_i * int(2 * s),
                 math.radians(35), math.radians(145), int(3.2 * s), s, gold_every=3)
    # long swag necklace dipping onto the ribcage (a deep U)
    swag = [(rc_cx - int(15 * s), neck_y + int(10 * s)),
            (rc_cx - int(8 * s), rc_cy + int(8 * s)),
            (rc_cx, rc_cy + int(13 * s)),
            (rc_cx + int(8 * s), rc_cy + int(8 * s)),
            (rc_cx + int(15 * s), neck_y + int(10 * s))]
    bead_strand(surf, swag, int(3.6 * s), s, gold_every=3)
    # a single cyan cabochon pendant at the swag's lowest point (sparse jewel)
    triad_circle(surf, CYAN, (rc_cx, rc_cy + int(15 * s)), int(4 * s),
                 ow=max(1, int(1.2 * s)), core=False)
    pygame.draw.circle(surf, CYAN_BR, (rc_cx - int(1 * s), rc_cy + int(14 * s)), max(1, int(1.6 * s)))

    # === SKULL HEAD — chibi, scary-cute, cyan third-eye (single brightest) ====
    triad_circle(surf, BONE, head_c, hr, ow=max(2, int(2 * s)))
    for sgn in (-1, 1):
        pygame.draw.circle(surf, BONE_D,
                           (head_c[0] + sgn * int(hr * 0.66), head_c[1] + int(hr * 0.28)),
                           int(hr * 0.26))
    # big round sockets — scary-cute, kept dim (no hot core) so the third-eye wins
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.44)
        ey = head_c[1] + int(hr * 0.10)
        pygame.draw.circle(surf, BONE_DD, (ex, ey), int(hr * 0.32))
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.26))
        pygame.draw.circle(surf, CYAN_D, (ex + sgn * int(1 * s), ey + int(1 * s)), int(hr * 0.10))
    # THIRD EYE — the contained faceted cyan cut-gem (current design). The weird
    # additive blue aura is gone; the gem alone is the single brightest pixel.
    tex, tey = head_c[0], head_c[1] - int(hr * 0.36)
    cyan_gem(surf, (tex, tey), int(hr * 0.40), s, focal=True)
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

    # === WHEEL EARRINGS — beaded ring discs hung at each temple (jewelry set) ==
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 1.04)
        ey = head_c[1] + int(hr * 0.10)
        triad_circle(surf, GOLD, (ex, ey), int(hr * 0.30), ow=max(1, int(1.4 * s)), core=False)
        triad_circle(surf, BONE_DD, (ex, ey), int(hr * 0.16), ow=max(1, int(1.0 * s)),
                     core=False, sheen=False)
        # bead rim ticks around the wheel
        for t in range(8):
            a = math.radians(t * 45)
            bx = ex + math.cos(a) * int(hr * 0.30)
            by = ey + math.sin(a) * int(hr * 0.30)
            pygame.draw.circle(surf, BEAD_BR, (int(bx), int(by)), max(1, int(1.4 * s)))

    # === FUSED CROWN — Mukha tiara-BAND on the brow + wide airy 6-skull ARC ====
    # WHY both languages: a plain arc reads as the Citipati reference, so the
    # tiara-band (a beaded gold band seated ACROSS the brow) is drawn first, then
    # the wide 6-skull arc sweeps above it in open sky. Crown skulls = warm-bone,
    # the dimmest value tier; only the centre skull glows.

    # -- tiara-band across the brow (Mukha language) --
    tiara_r = int(hr * 0.98)
    band_pts = []
    for i in range(11):
        a = math.radians(212 + i * (116 / 10))
        band_pts.append((head_c[0] + math.cos(a) * tiara_r,
                         head_c[1] + math.sin(a) * tiara_r))
    pygame.draw.lines(surf, INK, False, band_pts, int(6 * s))
    pygame.draw.lines(surf, GOLD, False, band_pts, int(4 * s))
    pygame.draw.lines(surf, GOLD_BR, False, band_pts[:6], max(1, int(1.4 * s)))
    # a bead-row riding on the band (carry the brood's bead texture into the crown)
    bead_arc(surf, head_c[0], head_c[1], int(hr * 0.98), math.radians(214),
             math.radians(326), int(2.6 * s), s, gold_every=3)
    # three cyan brow-cabochons set into the band (sparse jewel — not focal-bright)
    for i in range(3):
        a = math.radians(232 + i * 38)
        bx = head_c[0] + math.cos(a) * int(hr * 0.98)
        by = head_c[1] + math.sin(a) * int(hr * 0.98)
        triad_circle(surf, CYAN_D, (int(bx), int(by)), max(1, int(2.4 * s)),
                     ow=max(1, int(1.0 * s)), core=False, sheen=False)

    # -- wide airy 6-skull arc sweeping ABOVE the band (Citipati language) --
    arc_r = int(hr * 1.66)
    skull_r = int(hr * 0.36)
    # thin gold arc-wire the skulls perch on (kept linear)
    wire_pts = []
    for i in range(13):
        a = math.radians(216 + i * (108 / 12))
        wire_pts.append((head_c[0] + math.cos(a) * arc_r,
                         head_c[1] + math.sin(a) * arc_r))
    pygame.draw.lines(surf, INK, False, wire_pts, int(4 * s))
    pygame.draw.lines(surf, GOLD_D, False, wire_pts, int(2 * s))
    # WHY exactly ONE lit skull (centre of the 6): the locked rule restricts crown
    # glow to the crown-CENTRE skull only; the rest stay the dimmest value tier.
    for i in range(6):
        a = math.radians(220 + i * (100 / 5))
        sx = head_c[0] + math.cos(a) * arc_r
        sy = head_c[1] + math.sin(a) * arc_r
        crown_skull(surf, int(sx), int(sy), skull_r, s, lit=(i == 2))


# ── the bone-bead reliquary-staff → pillar mirror (sister's own forms) ────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The pillar is built from this sister's OWN forms: a stacked column of
    vertebra beads strung on a central rod (the Citipati torso rib-band motif),
    EVERY tier wrapped in a bone-bead collar (her jewelry set), and a gap-edge cap
    of one warm crown-skull seated on a beaded tiara-band ring (her fused-crown
    language in miniature). On-axis, symmetric, never top-heavy.

    `cap` names the END that faces the GAP."""
    shaft_w = int(15 * s)
    pygame.draw.rect(surf, INK, (cx - int(3 * s), top, int(6 * s), bot - top))

    bead_pitch = int(20 * s)
    cap_room = int(34 * s)
    if cap == "bottom":
        b0, b1 = top + int(6 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(6 * s)
    y = b0
    while y <= b1:
        bw = shaft_w
        bead = [(cx - bw, y + int(2 * s)),
                (cx - int(bw * 0.5), y - int(7 * s)),
                (cx + int(bw * 0.5), y - int(7 * s)),
                (cx + bw, y + int(2 * s)),
                (cx + int(bw * 0.5), y + int(11 * s)),
                (cx - int(bw * 0.5), y + int(11 * s))]
        triad_blob(surf, BONE, bead,
                   core_pts=[(cx, y - int(1 * s)), (cx + bw, y + int(2 * s)),
                             (cx + int(bw * 0.5), y + int(11 * s)), (cx, y + int(9 * s))],
                   sheen_pts=[(cx - bw, y + int(2 * s)), (cx - int(bw * 0.5), y - int(6 * s)),
                              (cx - int(bw * 0.2), y - int(4 * s)), (cx - int(bw * 0.7), y + int(5 * s))],
                   ow=max(1, int(1.4 * s)))
        pygame.draw.circle(surf, BONE_DD, (cx, y + int(2 * s)), int(4 * s))
        pygame.draw.circle(surf, INK, (cx, y + int(2 * s)), int(4 * s), max(1, int(1 * s)))
        # bone-bead collar wrapping each vertebra tier (her jewelry set on the shaft)
        bead_strand(surf, [(cx - bw - int(3 * s), y + int(2 * s)),
                           (cx + bw + int(3 * s), y + int(2 * s))],
                    int(3.0 * s), s, gold_every=3)
        y += bead_pitch

    # === gap-edge cap: warm crown-skull on a beaded tiara-band ring ===========
    cap_y = (bot - int(20 * s)) if cap == "bottom" else (top + int(20 * s))
    cap_skull_r = int(14 * s)
    # beaded tiara-band ring behind the cap skull (fused-crown language, miniature)
    bead_arc(surf, cx, cap_y, int(cap_skull_r * 1.35), math.radians(180), math.radians(360),
             int(3.0 * s), s, gold_every=3)
    crown_skull(surf, cx, cap_y, cap_skull_r, s, lit=True)
    # gold ferrule collar where the cap meets the shaft
    collar_y = (cap_y - int(20 * s)) if cap == "bottom" else (cap_y + int(20 * s))
    pygame.draw.rect(surf, INK, (cx - int(11 * s), collar_y - int(3 * s), int(22 * s), int(7 * s)))
    pygame.draw.rect(surf, GOLD, (cx - int(10 * s), collar_y - int(2 * s), int(20 * s), int(5 * s)))
    pygame.draw.rect(surf, GOLD_BR, (cx - int(10 * s), collar_y - int(2 * s), int(20 * s), int(2 * s)))


# ── compose the review sheet ─────────────────────────────────────────────────
SS = 8


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def render_creature_chip(boxw, boxh, draw_cx, draw_cy, scale, ss=SS):
    big = pygame.Surface((boxw * ss, boxh * ss), pygame.SRCALPHA)
    draw_asthi_dakini(big, draw_cx * ss, draw_cy * ss, scale * ss)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


def export_hero():
    """Standalone hi-res hero PNG (~1024px tall) so the dense bead-work survives.
    Rendered at SS=8 on a large canvas then smoothscaled into the export box."""
    boxw, boxh = 760, 1024
    hero = render_creature_chip(boxw, boxh, 380, 540, 3.7, ss=SS)
    canvas = pygame.Surface((boxw, boxh))
    vgrad(canvas, (0, 0, boxw, boxh), (74, 84, 104), (40, 46, 64))
    canvas.blit(hero, (0, 0))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_7_hero.png")
    pygame.image.save(canvas, out)
    return out


def blackout(surf):
    """Flatten any non-transparent pixel to solid ink — the silhouette proof."""
    out = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(surf)
    sil = mask.to_surface(setcolor=INK + (255,), unsetcolor=(0, 0, 0, 0))
    out.blit(sil, (0, 0))
    return out


def main():
    W, H = 1180, 900
    font_big = font(30)
    f = font(16)
    f_sm = font(12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("#1 — ASTHI-DAKINI", True, LABEL), (24, 13))
    sheet.blit(f_sm.render(
        "bone-jewel sky-dancer  ·  CITIPATI body + MUKHA 6-arm fan · 6 palm-skulls · fused crown · DARK cool bone + gold pips · round 1",
        True, LABEL_DIM), (270, 28))

    # === (a) BIG HERO =========================================================
    hero = render_creature_chip(380, 540, 188, 296, 2.05)
    sheet.blit(hero, (14, 92))
    sheet.blit(f.render("Creature — hero", True, LABEL), (120, 636))
    sheet.blit(f_sm.render("Cocked-hip DANCE under a six-arm radial fan; each of the 6 open palms cradles", True, LABEL_DIM), (14, 660))
    sheet.blit(f_sm.render("a tiny skull. Fused crown = Mukha tiara-band on the brow + wide airy 6-skull arc.", True, LABEL_DIM), (14, 676))
    sheet.blit(f_sm.render("Bead-lattice over every surface; gold spacer-pips carry the texture (not cyan-on-blue).", True, LABEL_DIM), (14, 692))
    sheet.blit(f_sm.render("Value ladder: cyan third-eye brightest > palm-skulls mid > crown skulls dimmest.", True, LABEL_DIM), (14, 708))

    # === (b) PILLAR assembled — mirrored, tileable shaft ======================
    pcx = 444
    top_big = pygame.Surface((150 * SS, 280 * SS), pygame.SRCALPHA)
    draw_pillar(top_big, 75 * SS, 4 * SS, 276 * SS, 1.0 * SS, cap="bottom")
    top_seg = grow_outline(pygame.transform.smoothscale(top_big, (150, 280)), INK + (255,), 1)
    sheet.blit(top_seg, (pcx, 86))
    bot_big = pygame.Surface((150 * SS, 280 * SS), pygame.SRCALPHA)
    draw_pillar(bot_big, 75 * SS, 4 * SS, 276 * SS, 1.0 * SS, cap="top")
    bot_seg = grow_outline(pygame.transform.smoothscale(bot_big, (150, 280)), INK + (255,), 1)
    sheet.blit(bot_seg, (pcx, 86 + 280 + 96))
    pygame.draw.rect(sheet, (58, 62, 74), (pcx + 8, 86 + 280, 134, 96))
    sheet.blit(f_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 280 + 40))
    sheet.blit(f.render("Pillar — bead-reliquary staff", True, LABEL), (pcx - 4, 766))
    sheet.blit(f_sm.render("vertebra beads + bone-bead collars = shaft;", True, LABEL_DIM), (pcx - 4, 790))
    sheet.blit(f_sm.render("crown-skull on a beaded tiara-ring caps the gap", True, LABEL_DIM), (pcx - 4, 806))

    # === (c) TRUE 32px DAY + NIGHT chips + blackout proof ======================
    panel_x = 632
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 700))
    sheet.blit(f.render("True 32px gameplay chip + silhouette", True, LABEL), (panel_x + 16, 96))

    def chip32():
        big = pygame.Surface((120 * SS, 120 * SS), pygame.SRCALPHA)
        draw_asthi_dakini(big, 60 * SS, 64 * SS, (32 / 150.0) * SS)
        small = pygame.transform.smoothscale(big, (120, 120))
        return grow_outline(small, INK + (255,), 1)

    chip = chip32()

    day_y = 128
    vgrad(sheet, (panel_x + 20, day_y, 150, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 15, day_y + 15))
    sheet.blit(f_sm.render("32px DAY sky", True, LABEL), (panel_x + 20, day_y + 156))

    night_y = day_y + 184
    vgrad(sheet, (panel_x + 20, night_y, 150, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 15, night_y + 15))
    sheet.blit(f_sm.render("32px NIGHT sky", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    # blackout / silhouette proof beside the 32px chips
    bo = blackout(chip)
    bx = panel_x + 192
    pygame.draw.rect(sheet, (208, 214, 224), (bx, day_y, 150, 150))
    pygame.draw.rect(sheet, INK, (bx, day_y, 150, 150), 1)
    sheet.blit(bo, (bx + 15, day_y + 15))
    sheet.blit(f_sm.render("silhouette proof", True, LABEL), (bx, day_y + 156))
    # a larger blackout of the hero so the fan + crown read as one shape
    bo_big = blackout(render_creature_chip(150, 200, 75, 110, 0.82))
    pygame.draw.rect(sheet, (208, 214, 224), (bx, night_y, 150, 200))
    pygame.draw.rect(sheet, INK, (bx, night_y, 150, 200), 1)
    sheet.blit(bo_big, (bx, night_y))
    sheet.blit(f_sm.render("hero silhouette", True, LABEL_DIM), (bx, night_y + 204))

    # a 32px pillar gap-cap chip on both skies
    def pillar_chip32():
        big = pygame.Surface((44 * SS, 140 * SS), pygame.SRCALPHA)
        draw_pillar(big, 22 * SS, 2 * SS, 138 * SS, 0.32 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (44, 140))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    px2 = panel_x + 364
    vgrad(sheet, (px2, day_y, 56, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (px2, day_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 6, day_y + 6))
    vgrad(sheet, (px2, night_y, 56, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (px2, night_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 6, night_y + 6))
    sheet.blit(f_sm.render("pillar", True, LABEL_DIM), (px2 + 4, day_y - 16))
    sheet.blit(f_sm.render("gap-cap", True, LABEL_DIM), (px2 - 2, night_y - 16))

    # palette strip
    sheet.blit(f.render("Pinned palette", True, LABEL), (panel_x + 16, day_y + 380))
    swatches = [
        (BONE, "cool bone (DARK)"), (BONE_D, "bone shade"),
        (BEAD, "bone bead (light)"), (BEAD_BR, "bead sheen"),
        (GOLD, "gold spacer-pip"), (GOLD_BR, "gold sheen"),
        (CYAN, "icy-cyan focal"), (CROWN_BONE, "crown-warm bone"),
        (THIRD_EYE, "third-eye"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, day_y + 408
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 184
        ry = syp + row * 26
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, ry, 18, 18))
        sheet.blit(f_sm.render(name, True, LABEL), (rx + 26, ry + 3))

    # bottom note strip
    pygame.draw.rect(sheet, PANEL, (14, 836, W - 28, 48))
    sheet.blit(f_sm.render(
        "ELEVATED pipeline: SS=8 supersample -> smoothscale; standalone hi-res hero export (round_7_hero.png).",
        True, LABEL_DIM), (26, 846))
    sheet.blit(f_sm.render(
        "STAY: flat fills · hard ink keyline (28,22,26) · dark-core->fill->top-left sheen triad · 1px grown outline · chibi scary-cute · procedural-only.",
        True, LABEL_DIM), (26, 864))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_7.png")
    pygame.image.save(sheet, out)
    hero_out = export_hero()
    print("wrote", out)
    print("wrote", hero_out)


if __name__ == "__main__":
    main()
