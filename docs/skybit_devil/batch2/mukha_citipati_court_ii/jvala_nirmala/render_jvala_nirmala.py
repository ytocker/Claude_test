"""
Round-1 concept renderer for JVALA-NIRMALA — sister #3 of the SECOND bone-deity
brood (mukha_citipati_court_ii), the charnel-ascetic / mountain-cave register.
She is the COOL WISDOM-FLAME DANCER: a Citipati cocked-hip dancing skeleton fused
with the Mukha six-arm radial fan + six palm-skulls, sheathed in a FULL-BODY
cobalt wisdom-flame MANTLE. Headless Pygame; ELEVATED pipeline (SS=8 supersample
-> smoothscale) so the dense draped flame stays crisp at downscale. House
grammar: flat saturated fills, hard ink keyline (28,22,26), dark-core -> flat-fill
-> top-left rim-sheen triad, 1px alpha-grown outline, chibi scary-cute;
procedural-only (no gradients/PNGs).

WHY she must NOT read as "a blue vajra_rakta": three taken sisters already own
the FLAME-as-HEAD-RING / closed-HALO grammar (vajra_rakta's flame-ring,
ratna_padmini's flame-halo, the Citipati reference's own ember-ring). The whole
job here is distinctness in PLACEMENT + SHAPE, not hue. So the cobalt flame is a
FULL-BODY DRAPED MANTLE — a sheeting SHAWL of overlapping tongues wrapping the
shoulders, both arm-fans, and the kicked-out knee — a filled blue dancing-flame
MASS, never a thin radiating spike-ring behind the head. There is deliberately
NO head-ring and NO closed halo. The mantle tongues route BEHIND the six arms so
all six palm-skulls stay legible.

WHY the crown is value-laddered against the mantle: the triple cobalt flame-crest
sits BEHIND the skull arc and is the SAME cold family as the mantle, so the
5-skull arc is forced OPAQUE PALE-BONE reading clearly IN FRONT of the crest
(value gap), and the Mukha tiara-BAND crosses the brow under it. The white-blue
third-eye is the single brightest pixel and OUT-GLOWS the crown-centre skull by a
wide value gap so the two near-white points never tie.

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

# ── PINNED PALETTE (locked brief) ─────────────────────────────────────────────
# Pale-BONE is the figure mass; deep saturated COBALT is a FILLED flame field
# (not a thin glow rim); ice-white is the focal/highlight. NO warm note anywhere.
BONE      = (232, 234, 224)   # pale-bone (the figure mass — cool-neutral, no warmth)
BONE_D    = (168, 174, 172)   # bone dark-core / shade
BONE_DD   = (104, 112, 118)   # deepest bone hollow (sockets, rib gaps)
BONE_SH   = (250, 252, 248)   # bone top-left rim-sheen
# the cobalt mantle is a filled MASS with a clear value ladder so sheeting tongues
# overlap legibly: deep field -> mid cobalt -> bright ice-edge tips.
COBALT_DD = ( 16,  30,  96)   # deepest cobalt (mantle under-shadow / overlaps)
COBALT_D  = ( 28,  58, 168)   # deep saturated cobalt field (the dominant mantle mass)
COBALT    = ( 52, 104, 220)   # mid cobalt flame body
COBALT_BR = (110, 176, 248)   # bright cobalt tongue
ICE       = (190, 224, 255)   # ice-white tongue tip / cool edge sheen
ICE_HOT   = (236, 248, 255)   # hottest cool flame core (lightest blue-white)
INK       = ( 28,  22,  26)   # hard ink keyline
# the third-eye is the single brightest element — a near-white-blue that must
# OUT-glow the crown-centre skull (which is held to pale-bone, never ICE_HOT).
EYE_GLOW  = (214, 238, 255)   # third-eye outer glow ring
EYE_CORE  = (255, 255, 255)   # third-eye brightest pixel (the one true white)
EYE_RING  = ( 70, 138, 236)   # third-eye cobalt iris (frames the white core)

BG        = ( 90,  94, 104)   # neutral grey review backdrop
PANEL     = ( 70,  74,  86)
DAY_SKY_T = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)   # night biome sky (top)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (240, 240, 244)
LABEL_DIM = (192, 198, 210)


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


def bone_limb(surf, p0, p1, p2, thick, s, joint=True):
    """Two-segment pale-bone limb with ink keyline + bulbous joint (Citipati)."""
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


# ── ONE draped cobalt flame tongue — the SHEETING shawl unit ──────────────────
def flame_tongue(surf, base0, base1, tipp, s, lit=0.0, sway=0.55):
    """A single overlapping draped flame tongue (a leaf-shaped lobe with one kink
    so it curls like cloth/flame, not a straight spike). WHY a value ladder per
    tongue: when dozens of these overlap into a SHEET (the shawl), the deep-cobalt
    body keeps the mass dense and opaque (body never reads naked through gaps),
    while a bright ice tip rides on top so the overlap reads as drapery folds, not
    a flat blob. `lit` 0..1 pushes the whole tongue cooler/brighter for the
    leading edge of the mantle. `sway` curls the kink sideways like a flame curl."""
    bx = (base0[0] + base1[0]) * 0.5
    by = (base0[1] + base1[1]) * 0.5
    # kink point partway up, swayed off-axis so the tongue curls (drapery read)
    perp = (-(tipp[1] - by), (tipp[0] - bx))
    pl = max(1.0, math.hypot(*perp))
    kx = bx + (tipp[0] - bx) * 0.56 + perp[0] / pl * (tipp_len(base0, base1) * sway)
    ky = by + (tipp[1] - by) * 0.56 + perp[1] / pl * (tipp_len(base0, base1) * sway)
    tongue = [base0, (kx, ky), tipp, base1]
    body = lerp(COBALT_D, COBALT, lit)
    pygame.draw.polygon(surf, INK, tongue)
    pygame.draw.polygon(surf, body, tongue)
    # darker overlap shadow on the trailing (base1) side so folds layer
    shade = [base1, (kx, ky), tipp,
             ((base1[0] + kx) * 0.5, (base1[1] + ky) * 0.5)]
    pygame.draw.polygon(surf, lerp(COBALT_DD, COBALT_D, lit), shade)
    # bright leaf-spine + ice tip riding the upper half
    mid0 = (base0[0] + (kx - base0[0]) * 0.5, base0[1] + (ky - base0[1]) * 0.5)
    bright = lerp(COBALT, COBALT_BR, lit)
    pygame.draw.polygon(surf, bright, [mid0, (kx, ky), tipp])
    pygame.draw.polygon(surf, lerp(COBALT_BR, ICE, lit),
                        [(kx, ky), tipp,
                         ((kx + tipp[0]) * 0.5, (ky + tipp[1]) * 0.5)])
    pygame.draw.line(surf, ICE, (kx, ky), tipp, max(1, int(1.6 * s)))
    pygame.draw.polygon(surf, INK, tongue, max(1, int(1.1 * s)))


def tipp_len(base0, base1):
    return max(1.0, math.hypot(base1[0] - base0[0], base1[1] - base0[1]))


def mantle_drape(surf, anchor, ang, length, width, s, n=4, lit=0.0, sway=0.5):
    """A cluster of overlapping draped tongues fanning from `anchor` toward `ang`
    — one panel of the full-body sheeting shawl. WHY many short overlapping
    tongues instead of a few long spikes: overlap = drapery, and density means the
    body never reads naked through gaps (the core distinctness rule). Each panel
    is built tip-near-to-far so closer tongues overlap farther ones."""
    tongues = []
    for i in range(n):
        f = (i - (n - 1) / 2.0) / max(1, (n - 1))   # -0.5..0.5 across the fan
        a = ang + f * 0.9
        L = length * (0.78 + 0.30 * (1 - abs(f)))    # centre tongues longest
        bx = anchor[0] + math.cos(a) * width * f * 1.3
        by = anchor[1] + math.sin(a) * width * f * 1.3
        # tongue base width
        pa = a + math.pi / 2
        bw = width * 0.5
        b0 = (bx + math.cos(pa) * bw, by + math.sin(pa) * bw)
        b1 = (bx - math.cos(pa) * bw, by - math.sin(pa) * bw)
        tip = (bx + math.cos(a) * L, by + math.sin(a) * L)
        tongues.append((abs(f), b0, b1, tip))
    # draw outermost (high |f|) first so centre tongues overlap on top
    tongues.sort(key=lambda t: -t[0])
    for k, (af, b0, b1, tip) in enumerate(tongues):
        flame_tongue(surf, b0, b1, tip, s, lit=lit + (1 - af) * 0.25, sway=sway)


# ── a single ornamental crown-skull (reused for the arc + the pillar cap) ─────
def crown_skull(surf, cx, cy, r, s, lit=False):
    """Tiny pale-bone skull — domed cranium, two dark sockets, a stub jaw. The arc
    skulls are OPAQUE bone so they read clearly IN FRONT of the cobalt crest
    behind them (value separation). `lit` swaps the centre skull's eye-pins to a
    cool ice pin — but kept BELOW the third-eye so the value gap holds."""
    triad_circle(surf, BONE, (cx, cy), r, ow=max(1, int(1.6 * s)), core=False)
    jaw = [(cx - int(r * 0.52), cy + int(r * 0.52)),
           (cx + int(r * 0.52), cy + int(r * 0.52)),
           (cx + int(r * 0.34), cy + int(r * 1.0)),
           (cx - int(r * 0.34), cy + int(r * 1.0))]
    triad_blob(surf, BONE, jaw, ow=max(1, int(1.2 * s)))
    eye_c = COBALT_BR if lit else INK
    for ex in (cx - int(r * 0.38), cx + int(r * 0.38)):
        pygame.draw.circle(surf, INK, (ex, cy + int(r * 0.04)), max(1, int(r * 0.24)))
        if lit:
            pygame.draw.circle(surf, eye_c, (ex, cy + int(r * 0.04)), max(1, int(r * 0.13)))
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.42)), max(1, int(r * 0.13)))
    pygame.draw.line(surf, INK,
                     (cx - int(r * 0.34), cy + int(r * 0.70)),
                     (cx + int(r * 0.34), cy + int(r * 0.70)),
                     max(1, int(1.2 * s)))


# ── a tiny cradled palm-skull (the core Mukha motif) ──────────────────────────
def palm_skull(surf, cx, cy, r, s):
    """A tiny pale-bone skull cradled in an open palm — six of these ride the
    fan-tips and MUST stay legible (mantle routes behind them). A clean bone dome
    + two dark sockets reads at 32px."""
    triad_circle(surf, BONE, (cx, cy), r, ow=max(1, int(1.2 * s)), core=False)
    for ex in (cx - int(r * 0.4), cx + int(r * 0.4)):
        pygame.draw.circle(surf, INK, (ex, cy - int(r * 0.05)), max(1, int(r * 0.3)))
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.3)), max(1, int(r * 0.16)))
    # stub jaw notch
    pygame.draw.line(surf, INK, (cx - int(r * 0.4), cy + int(r * 0.6)),
                     (cx + int(r * 0.4), cy + int(r * 0.6)), max(1, int(1 * s)))


def open_palm(surf, hx, hy, ang, r, s):
    """An open bone palm cradling a skull — a small cup of finger ticks fanning up
    around the cradled palm-skull. Drawn so the skull nests in the cup."""
    # palm pad
    triad_circle(surf, BONE, (hx, hy), int(r * 0.7), ow=max(1, int(1.2 * s)), core=False)
    # finger ticks fanning outward (the cradle)
    for k in range(-2, 3):
        fa = ang + k * 0.34
        ex = hx + math.cos(fa) * r * 1.25
        ey = hy + math.sin(fa) * r * 1.25
        pygame.draw.line(surf, INK, (hx, hy), (ex, ey), max(1, int(2.0 * s)))
        pygame.draw.line(surf, BONE, (hx, hy), (ex, ey), max(1, int(1.2 * s)))


# ── the six-arm radial fan (Mukha KIND, grafted onto the Citipati torso) ──────
def draw_arm_fan(surf, sh_cx, sh_cy, s, hr):
    """Six fat bone arms splay in a wide symmetric STARBURST from a LOW shoulder
    origin (Mukha radial fan). No arm aims straight up — the crown sky stays open.
    Spread ~[100,64,28] deg off vertical, three per side. Returns the six hand
    centres + their outward angles for palm + cradled-skull placement."""
    arm_len = int(hr * 1.95)
    arm_th = int(12 * s)
    spread = [100, 64, 28]
    order = []
    for sgn in (-1, 1):
        for d in spread:
            a = math.radians(-90 + sgn * d)
            order.append((sgn, d, a))
    order.sort(key=lambda o: -o[1])   # lowest arms first so upper splay overlaps
    hands = []
    for sgn, d, a in order:
        sh = (sh_cx + sgn * int(hr * 0.55), sh_cy)
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
        hands.append((int(hand[0]), int(hand[1]), a))
    return hands


# ── the cool wisdom-flame dancer ──────────────────────────────────────────────
def draw_jvala(surf, cx, cy, s):
    """Citipati cocked-hip dancing skeleton (tall rib-barrel torso, one knee
    kicked out) wearing the Mukha six-arm fan + six cradled palm-skulls, all
    sheathed in a FULL-BODY cobalt wisdom-flame MANTLE (sheeting shawl). Fused
    crown: triple cobalt flame-crest behind an opaque 5-skull arc + Mukha
    tiara-band across the brow. White-blue third-eye out-glows the crown centre.
    `s` = unit scale around a ~140-unit figure."""

    head_c = (cx, cy - int(30 * s))
    hr = int(23 * s)
    hip_y = cy + int(24 * s)
    hip_cx = cx + int(7 * s)
    rc_cx, rc_cy = cx, cy - int(2 * s)
    rc_w, rc_h = int(34 * s), int(40 * s)
    sh_line_y = rc_cy - rc_h // 2 + int(6 * s)

    # === (1) BACK MANTLE PANELS (drawn FIRST → the shawl behind the whole body) =
    # WHY a full-body field, not a head-ring: a broad cobalt mantle MASS spreads
    # behind shoulders, down both flanks, and out under the kicked-out knee — the
    # silhouette-carrying blue dancing-flame figure. Tongues sheet densely so no
    # sky shows through onto the body. This is the anti-halo placement.
    back_anchor = (cx, rc_cy + int(2 * s))
    # broad rear fan filling behind the torso (the shawl back)
    mantle_drape(surf, (cx, rc_cy + int(8 * s)), math.radians(-90),
                 int(64 * s), int(56 * s), s, n=7, lit=0.0, sway=0.42)
    # two shoulder shawl wings sweeping up-and-out behind the arms
    mantle_drape(surf, (rc_cx - int(20 * s), sh_line_y), math.radians(-150),
                 int(54 * s), int(40 * s), s, n=5, lit=0.05, sway=0.55)
    mantle_drape(surf, (rc_cx + int(20 * s), sh_line_y), math.radians(-30),
                 int(54 * s), int(40 * s), s, n=5, lit=0.05, sway=-0.55)
    # lower flank drapes pooling down past the hips (mantle wraps the knee)
    mantle_drape(surf, (hip_cx - int(20 * s), hip_y + int(6 * s)), math.radians(140),
                 int(50 * s), int(34 * s), s, n=5, lit=0.0, sway=0.5)
    mantle_drape(surf, (hip_cx + int(26 * s), hip_y + int(2 * s)), math.radians(46),
                 int(52 * s), int(36 * s), s, n=5, lit=0.0, sway=-0.5)

    # === (2) SIX-ARM RADIAL FAN (bone arms over the back mantle) ===============
    hands = draw_arm_fan(surf, head_c[0], head_c[1] + int(hr * 0.92), s, hr)

    # === (3) LEGS — cocked-hip dance, one knee kicked OUT (Citipati) ===========
    leg_th = int(14 * s)
    hipL = (hip_cx - int(13 * s), hip_y)
    kneeL = (hip_cx - int(20 * s), hip_y + int(26 * s))
    footL = (hip_cx - int(22 * s), hip_y + int(52 * s))
    bone_limb(surf, hipL, kneeL, footL, leg_th, s)
    hipR = (hip_cx + int(11 * s), hip_y)
    kneeR = (hip_cx + int(30 * s), hip_y + int(8 * s))
    footR = (hip_cx + int(20 * s), hip_y + int(34 * s))
    bone_limb(surf, hipR, kneeR, footR, leg_th, s)
    for (fx, fy), sgn in ((footL, -1), (footR, +1)):
        foot = [(fx - int(4 * s), fy - int(2 * s)), (fx + sgn * int(16 * s), fy + int(2 * s)),
                (fx + sgn * int(15 * s), fy + int(10 * s)), (fx - int(5 * s), fy + int(8 * s))]
        triad_blob(surf, BONE, foot, ow=max(1, int(1.4 * s)))

    # === (3b) KNEE MANTLE WRAP — sheeting tongues over the kicked-out knee =====
    # WHY explicitly on the knee: the brief wants the mantle wrapping shoulders/
    # arms/KNEE; a cobalt drape licking up over the thrust knee proves it is a
    # garment on the body, not a backdrop ring.
    mantle_drape(surf, (kneeR[0] + int(4 * s), kneeR[1]), math.radians(-18),
                 int(26 * s), int(22 * s), s, n=4, lit=0.30, sway=-0.5)

    # === (4) PELVIS + RIBCAGE torso (Citipati rib bands → pillar motif) ========
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

    spine_top_y = cy - int(14 * s)
    spine = [(hip_cx, hip_y - int(2 * s)),
             (cx + int(2 * s), cy + int(6 * s)),
             (cx - int(1 * s), spine_top_y)]
    pygame.draw.lines(surf, INK, False, spine, int(8 * s))
    pygame.draw.lines(surf, BONE, False, spine, int(5 * s))

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
    for i in range(4):
        ry = rc_cy - rc_h // 2 + int(8 * s) + i * int(8 * s)
        bw = int(rc_w * (0.46 - i * 0.05))
        pygame.draw.arc(surf, BONE_DD,
                        (rc_cx - bw, ry - int(7 * s), bw * 2, int(16 * s)),
                        math.radians(205), math.radians(335), max(2, int(2.4 * s)))
    pygame.draw.line(surf, BONE_DD, (rc_cx, rc_cy - rc_h // 2 + int(6 * s)),
                     (rc_cx, rc_cy + int(6 * s)), max(1, int(2 * s)))

    # === (4b) FRONT MANTLE COLLAR — sheeting tongues draped over the shoulders ==
    # WHY a FRONT drape too: a shawl wraps over the shoulders, not only behind. A
    # band of dense cobalt tongues laps over the collarbones and down the chest
    # sides so the cobalt clearly OVERLAYS the body (a worn garment), and the
    # density means the torso never reads naked. WHY aimed DOWNWARD (>90deg, into
    # the chest) and anchored a touch lower: the collar must NEVER lick up onto the
    # brow and bury the third-eye — it pools down over the sternum.
    mantle_drape(surf, (rc_cx - int(16 * s), sh_line_y + int(8 * s)), math.radians(128),
                 int(30 * s), int(26 * s), s, n=5, lit=0.45, sway=0.4)
    mantle_drape(surf, (rc_cx + int(16 * s), sh_line_y + int(8 * s)), math.radians(52),
                 int(30 * s), int(26 * s), s, n=5, lit=0.45, sway=-0.4)
    # a short cobalt cowl tongue-row pooling down the upper chest (the collar)
    mantle_drape(surf, (rc_cx, sh_line_y + int(10 * s)), math.radians(90),
                 int(22 * s), int(34 * s), s, n=6, lit=0.55, sway=0.3)

    # === (5) SIX OPEN PALMS each cradling a TINY SKULL =========================
    # WHY drawn AFTER the front mantle, over the bone arms: the palm-skulls are the
    # core motif and must stay frontmost & legible; the mantle was routed behind
    # the arms so nothing occludes the six skulls.
    palm_r = int(8 * s)
    for hx, hy, a in hands:
        open_palm(surf, hx, hy, a, palm_r, s)
        # the cradled skull sits just outward of the palm, in the finger cup
        skx = hx + int(math.cos(a) * palm_r * 0.7)
        sky = hy + int(math.sin(a) * palm_r * 0.7)
        palm_skull(surf, skx, sky, int(palm_r * 0.78), s)

    # === (6) SKULL HEAD — chibi scary-cute, white-blue third eye ===============
    triad_circle(surf, BONE, head_c, hr, ow=max(2, int(2 * s)))
    for sgn in (-1, 1):
        pygame.draw.circle(surf, BONE_D,
                           (head_c[0] + sgn * int(hr * 0.66), head_c[1] + int(hr * 0.28)),
                           int(hr * 0.26))
    # two big sockets — cool deep cobalt pins, kept DIM so the third-eye out-glows
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.44)
        ey = head_c[1] + int(hr * 0.04)
        pygame.draw.circle(surf, BONE_DD, (ex, ey), int(hr * 0.34))
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.28))
        pygame.draw.circle(surf, COBALT_D, (ex + sgn * int(1 * s), ey + int(1 * s)),
                           int(hr * 0.13))
    # nose triangle
    pygame.draw.polygon(surf, BONE_DD,
                        [(head_c[0] - int(hr * 0.14), head_c[1] + int(hr * 0.26)),
                         (head_c[0] + int(hr * 0.14), head_c[1] + int(hr * 0.26)),
                         (head_c[0], head_c[1] + int(hr * 0.52))])
    my = head_c[1] + int(hr * 0.68)
    pygame.draw.line(surf, INK, (head_c[0] - int(hr * 0.5), my),
                     (head_c[0] + int(hr * 0.5), my), max(1, int(2 * s)))
    for k in range(-3, 4):
        pygame.draw.line(surf, INK, (head_c[0] + int(k * hr * 0.16), my - int(hr * 0.1)),
                         (head_c[0] + int(k * hr * 0.16), my + int(hr * 0.14)), max(1, int(1 * s)))

    # === (7) FUSED CROWN — triple cobalt flame-crest BEHIND, opaque 5-skull arc =
    #         + Mukha tiara-BAND across the brow, all IN FRONT of the crest =======
    # WHY the crest is drawn first and the arc + band over it: same-cobalt tongues
    # would otherwise erase the bone arc. Three upright cobalt flame-crests rise
    # from BEHIND the head (a small, contained crest — NOT a ring around the head)
    # and the OPAQUE pale-bone 5-skull arc + tiara band read clearly in front,
    # value-separated.
    crest_cy = head_c[1] - int(hr * 0.5)
    for cx_off, lift, scl in ((-int(hr * 0.62), 0.86, 0.8),
                              (0.0, 1.0, 1.0),
                              (int(hr * 0.62), 0.86, 0.8)):
        a = math.radians(-90)
        base_y = crest_cy
        anchor = (head_c[0] + cx_off, base_y)
        mantle_drape(surf, anchor, a, int(hr * 1.5 * lift * scl + hr * 0.6),
                     int(hr * 0.7 * scl), s, n=3, lit=0.15, sway=0.35 * (1 if cx_off >= 0 else -1))

    # Mukha tiara BAND across the brow (a shallow arc seated low on the head)
    band_r = int(hr * 1.04)
    band_pts = []
    for i in range(11):
        a = math.radians(218 + i * (104 / 10))
        band_pts.append((head_c[0] + math.cos(a) * band_r,
                         head_c[1] + math.sin(a) * band_r))
    pygame.draw.lines(surf, INK, False, band_pts, int(7 * s))
    pygame.draw.lines(surf, BONE, False, band_pts, int(4 * s))
    pygame.draw.lines(surf, BONE_SH, False, band_pts[:6], max(1, int(1.4 * s)))

    # FIVE opaque pale-bone crown skulls fanned across the top arc, IN FRONT of
    # the cobalt crest — the value separation is the whole job here.
    skull_cr = hr * 1.52
    skull_r = int(hr * 0.40)
    for i in range(5):
        a = math.radians(216 + i * (108 / 4))
        sx = head_c[0] + math.cos(a) * skull_cr
        sy = head_c[1] + math.sin(a) * skull_cr
        crown_skull(surf, int(sx), int(sy), skull_r, s, lit=(i == 2))

    # === (8) THIRD EYE — drawn LAST so NOTHING (mantle/crest/band) can occlude ==
    # the single BRIGHTEST element. WHY glow-ring -> cobalt iris -> pure-white core,
    # and bigger than the crown-centre skull's eye-pins: it must win the value
    # ladder by a WIDE gap (the two near-white-blue points never tie), seated on
    # the brow between the band apex and the sockets.
    tex, tey = head_c[0], head_c[1] - int(hr * 0.40)
    pygame.draw.circle(surf, INK, (tex, tey), max(2, int(hr * 0.40)))
    pygame.draw.circle(surf, EYE_RING, (tex, tey), max(2, int(hr * 0.36)))
    pygame.draw.circle(surf, EYE_GLOW, (tex, tey), max(2, int(hr * 0.25)))
    pygame.draw.circle(surf, EYE_CORE, (tex, tey), max(1, int(hr * 0.14)))


# ── the spine-staff → pillar mirror, built from HER own forms ─────────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The dancer's spine-staff IS the pillar: stacked vertebra beads (her torso
    rib-band motif) = the tileable shaft, each bead flanked by a small SHEETING
    cobalt-flame drape (her mantle grammar) so the column reads as her own; the
    gap-edge cap is a single opaque crown-skull seated in front of a triple cobalt
    flame-crest (her crown in miniature). On-axis, symmetric, not top-heavy.

    `cap` names the END that faces the GAP."""
    shaft_w = int(14 * s)
    pygame.draw.rect(surf, INK, (cx - int(3 * s), top, int(6 * s), bot - top))

    bead_pitch = int(22 * s)
    cap_room = int(34 * s)
    if cap == "bottom":
        b0, b1 = top + int(8 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(8 * s)
    y = b0
    idx = 0
    while y <= b1:
        # mantle drapes flanking each bead (drawn first → behind the bone bead)
        for sgn in (-1, 1):
            mantle_drape(surf, (cx + sgn * int(shaft_w * 0.8), y + int(2 * s)),
                         math.radians(0 if sgn > 0 else 180),
                         int(20 * s), int(16 * s), s, n=3, lit=0.1,
                         sway=0.45 * sgn)
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
        pygame.draw.line(surf, BONE_DD, (cx - int(bw * 0.5), y - int(5 * s)),
                         (cx + int(bw * 0.5), y - int(5 * s)), max(1, int(1.2 * s)))
        idx += 1
        y += bead_pitch

    # gap-edge cap: triple cobalt crest behind a single opaque crown-skull
    cap_y = (bot - int(20 * s)) if cap == "bottom" else (top + int(20 * s))
    grow = +1 if cap == "bottom" else -1
    crest_dir = math.radians(90) if grow > 0 else math.radians(-90)
    for off, scl in ((-int(12 * s), 0.8), (0, 1.0), (int(12 * s), 0.8)):
        mantle_drape(surf, (cx + off, cap_y), crest_dir,
                     int(26 * s * scl + 8 * s), int(11 * s * scl), s, n=3, lit=0.15,
                     sway=0.4 * (1 if off >= 0 else -1))
    crown_skull(surf, cx, cap_y, int(13 * s), s, lit=True)


# ── compose the review sheet ─────────────────────────────────────────────────
SS = 8


def render_creature_chip(boxw, boxh, draw_cx, draw_cy, scale, ss=SS):
    big = pygame.Surface((boxw * ss, boxh * ss), pygame.SRCALPHA)
    draw_jvala(big, draw_cx * ss, draw_cy * ss, scale * ss)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def render_hero_hires():
    """Standalone hi-res hero ≈1024px tall on a dark cool panel."""
    HW, HH = 820, 1024
    surf = pygame.Surface((HW, HH))
    vgrad(surf, (0, 0, HW, HH), (24, 28, 52), (40, 38, 70))
    hero = render_creature_chip(HW, HH, HW // 2 // 1, 540, 4.0)
    surf.blit(hero, (0, 0))
    font_sm = pygame.font.SysFont("DejaVu Sans", 18)
    surf.blit(font_sm.render(
        "JVALA-NIRMALA  ·  cool wisdom-flame dancer  ·  hi-res hero (SS=8)",
        True, LABEL), (24, 24))
    return surf


def blackout(surf):
    """Silhouette proof — fill every non-transparent pixel solid black."""
    out = surf.copy()
    arr = pygame.surfarray.pixels_alpha(out)
    rgb = pygame.surfarray.pixels3d(out)
    mask = arr > 24
    rgb[mask] = (12, 12, 14)
    del arr, rgb
    return out


def main():
    here = os.path.dirname(os.path.abspath(__file__))

    # ── hi-res standalone hero ────────────────────────────────────────────────
    hero_hi = render_hero_hires()
    hero_path = os.path.join(here, "round_1_hero.png")
    pygame.image.save(hero_hi, hero_path)

    # ── the standard review sheet ─────────────────────────────────────────────
    W, H = 1040, 860
    font_big = pygame.font.SysFont("DejaVu Sans", 30, bold=True)
    font = pygame.font.SysFont("DejaVu Sans", 17, bold=True)
    font_sm = pygame.font.SysFont("DejaVu Sans", 12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("JVALA-NIRMALA", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "cool wisdom-flame dancer  ·  CITIPATI body + Mukha 6-arm fan · FULL-BODY cobalt SHEETING mantle (NOT a ring) · 6 palm-skulls · round 1",
        True, LABEL_DIM), (300, 26))

    # === (a) BIG HERO =========================================================
    hero = render_creature_chip(370, 500, 185, 268, 1.95)
    sheet.blit(hero, (14, 86))
    sheet.blit(font.render("Creature — hero", True, LABEL), (120, 596))
    sheet.blit(font_sm.render("FULL-BODY cobalt mantle DRAPES over shoulders/arms/knee (a sheeting shawl,", True, LABEL_DIM), (14, 620))
    sheet.blit(font_sm.render("NOT a head-ring/halo). 6-arm fan + 6 cradled palm-skulls in FRONT of mantle.", True, LABEL_DIM), (14, 636))
    sheet.blit(font_sm.render("Crown: cobalt flame-crest BEHIND an opaque 5-skull arc + tiara band. White-", True, LABEL_DIM), (14, 652))
    sheet.blit(font_sm.render("blue third-eye out-glows crown-centre by a wide value gap.", True, LABEL_DIM), (14, 668))

    # === (b) PILLAR assembled — mirrored, from HER own forms ==================
    pcx = 408
    top_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(top_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="bottom")
    top_seg = grow_outline(pygame.transform.smoothscale(top_big, (150, 250)), INK + (255,), 1)
    sheet.blit(top_seg, (pcx, 86))
    bot_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(bot_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="top")
    bot_seg = grow_outline(pygame.transform.smoothscale(bot_big, (150, 250)), INK + (255,), 1)
    sheet.blit(bot_seg, (pcx, 86 + 250 + 96))
    pygame.draw.rect(sheet, (58, 62, 74), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar — spine-staff", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("vertebra beads + cobalt-flame drapes = shaft;", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("crown-skull + flame-crest caps each gap edge", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("(mirrored top<->bottom, on-axis, her own forms)", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) blackout / silhouette proof ======================================
    sil_box = render_creature_chip(150, 250, 75, 132, 0.95)
    sil = blackout(sil_box)
    sbx = 568
    pygame.draw.rect(sheet, (150, 156, 168), (sbx - 4, 86 - 4, 158, 258))
    sheet.blit(sil, (sbx, 86))
    sheet.blit(font.render("Silhouette", True, LABEL), (sbx, 350))
    sheet.blit(font_sm.render("mantle MASS reads as a", True, LABEL_DIM), (sbx, 374))
    sheet.blit(font_sm.render("filled blue figure — not a", True, LABEL_DIM), (sbx, 390))
    sheet.blit(font_sm.render("thin spiky rim/ring.", True, LABEL_DIM), (sbx, 406))

    # === (d) TRUE 32px gameplay chips on day + night sky ======================
    panel_x = 736
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 600))
    sheet.blit(font.render("True 32px chip", True, LABEL), (panel_x + 16, 96))

    def chip32():
        big = pygame.Surface((120 * SS, 120 * SS), pygame.SRCALPHA)
        draw_jvala(big, 60 * SS, 64 * SS, (32 / 150.0) * SS)
        small = pygame.transform.smoothscale(big, (120, 120))
        return grow_outline(small, INK + (255,), 1)

    chip = chip32()
    day_y = 128
    vgrad(sheet, (panel_x + 20, day_y, 130, 130), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 130, 130), 1)
    sheet.blit(chip, (panel_x + 20 + 5, day_y + 5))
    sheet.blit(font_sm.render("32px DAY", True, LABEL), (panel_x + 20, day_y + 134))

    night_y = day_y + 168
    vgrad(sheet, (panel_x + 20, night_y, 130, 130), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 130, 130), 1)
    sheet.blit(chip, (panel_x + 20 + 5, night_y + 5))
    sheet.blit(font_sm.render("32px NIGHT", True, LABEL_DIM), (panel_x + 20, night_y + 134))

    def pillar_chip32():
        big = pygame.Surface((44 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 22 * SS, 2 * SS, 128 * SS, 0.32 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (44, 130))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    px2 = panel_x + 162
    vgrad(sheet, (px2, day_y, 56, 130), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (px2, day_y, 56, 130), 1)
    sheet.blit(pc, (px2 + 6, day_y + 2))
    vgrad(sheet, (px2, night_y, 56, 130), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (px2, night_y, 56, 130), 1)
    sheet.blit(pc, (px2 + 6, night_y + 2))
    sheet.blit(font_sm.render("pillar", True, LABEL_DIM), (px2 + 6, day_y - 16))

    # palette strip
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, 480))
    swatches = [
        (BONE, "pale-bone"), (BONE_DD, "bone hollow"),
        (COBALT_D, "deep cobalt"), (COBALT, "cobalt body"),
        (COBALT_BR, "cobalt tongue"), (ICE, "ice-edge"),
        (EYE_CORE, "third-eye core"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, 508
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 142
        ry = syp + row * 26
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, ry, 18, 18))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 24, ry + 3))

    pygame.draw.rect(sheet, PANEL, (14, 700, W - 28, 44))
    sheet.blit(font_sm.render(
        "DISTINCTNESS: cobalt FLAME lives as a FULL-BODY DRAPED MANTLE (sheeting shawl over shoulders/arms/knee), NOT a head-ring/halo (vs vajra_rakta ring,", True, LABEL_DIM), (26, 708))
    sheet.blit(font_sm.render(
        "ratna_padmini halo, Citipati ember-ring).  STAY: flat fills · ink keyline (28,22,26) · dark-core->fill->sheen triad · 1px grown outline · chibi scary-cute · procedural.",
        True, LABEL_DIM), (26, 724))

    pygame.draw.rect(sheet, PANEL, (14, 756, W - 28, 28))
    sheet.blit(font_sm.render(
        "ELEVATED pipeline: SS=8 supersample -> smoothscale.  Standalone hi-res hero exported separately: round_1_hero.png (~1024px).",
        True, LABEL_DIM), (26, 762))

    out = os.path.join(here, "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out)
    print("wrote", hero_path)


if __name__ == "__main__":
    main()
