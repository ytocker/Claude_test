"""
Round-1 concept renderer for VYAGHRA-CHARMA — the tiger-pelt charnel adept
(brood mukha_citipati_court_ii, sister #1). A FUSED Mukha-Devi + Citipati
bone-deity in the charnel-ascetic / mountain-cave register: a CITIPATI dancing
rib-barrel torso wearing a Mukha SIX-ARM radial fan, each open palm cradling a
tiny skull, under a fused above-head crown (Citipati 5-skull arc-SWEEP + Mukha
tiara-BAND across the brow). Headless Pygame; ELEVATED pipeline (SS=8
supersample -> smoothscale) so the striped pelt + six palm-skulls stay crisp at
downscale. House grammar: flat saturated fills, hard 1-2px ink keyline
(28,22,26), dark-core -> flat-fill -> top-left rim-sheen triad, 1px alpha-grown
outline, chibi scary-CUTE (cuteness in PROPORTION only — the ornament is a
reverent ascetic's tiger-pelt, never flippant); procedural-only.

WHY the TIGER-PELT ornament set is the fresh class (vyaghra-charma, the tiger
skin a meditating yogin sits on and a wrathful destroyer wears as a loincloth):
a striped tawny/black tiger-HIDE sash slung diagonally across the rib barrel,
hung with claw-paw danglers and a flicking tail, clasped by a tiger-FACE buckle.
No beads, no silk-brocade, no garland, no flame-ring — a hide. The 32px CARRIER
is the bold tawny/black diagonal STRIPE-SASH band; the claw-paws + face-buckle
are hero-only detail that may mush at gameplay scale.

WHY a green-gold third-eye on a warm mass: it is the one COOL focal pixel on an
otherwise tawny-gold + black-stripe + cream-bone field — the brightest pixel in
the value ladder (third-eye brightest -> six palm-skulls mid -> crown dimmest).
Glow lives ONLY on the third-eye and the crown-centre skull (drawn value/inlay,
never a bloom).

WHY the tiger-EARS FLANK the centre crown skull: the fused superstructure must
NEVER cap/replace the arc — the paired tawny ears spring from BEHIND, sitting to
either SIDE of the centre skull, so the full 5-skull arc-sweep and the tiara
band still read in FRONT of the ear crest.

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

# FONT path: five dirs up from this sister dir -> game/assets/
_HERE = os.path.dirname(os.path.abspath(__file__))
_ASSETS = os.path.normpath(os.path.join(_HERE, "..", "..", "..", "..", "..", "game", "assets"))


def _load_font(size, bold=False):
    """Prefer the vendored game font; fall back to a system sans so the review
    renders even if the asset tree moved. Review art only — never shipped."""
    for name in ("Baloo2-Bold.ttf", "Baloo2-SemiBold.ttf", "Baloo2-Medium.ttf"):
        p = os.path.join(_ASSETS, name)
        if os.path.exists(p):
            try:
                return pygame.font.Font(p, size)
            except Exception:
                pass
    return pygame.font.SysFont("DejaVu Sans", size, bold=bold)


# ── PINNED PALETTE (locked brief) ─────────────────────────────────────────────
# Cream BONE is the dominant deity MASS; tawny-gold + black-stripe are the pelt
# ornament; green-gold third-eye is the single COOL focal. Tawny is warm so the
# brood reads "charnel-ascetic in a tiger hide," not treasury-gold.
BONE      = (238, 228, 204)   # cream bone (the dominant deity fill)
BONE_D    = (186, 172, 142)   # bone dark-core / shade
BONE_DD   = (134, 120,  92)   # deepest bone hollow (sockets, rib gaps)
BONE_SH   = (252, 246, 228)   # bone top-left rim-sheen
TAWNY     = (214, 150,  54)   # tawny-gold tiger hide (the pelt field)
TAWNY_BR  = (244, 196, 104)   # hot tawny sheen / fur tips
TAWNY_D   = (158, 102,  30)   # deep tawny shade
STRIPE    = ( 40,  30,  24)   # black tiger stripe (near-ink, warm-black)
STRIPE_BR = ( 70,  54,  42)   # stripe edge so it isn't pure ink
EARTH     = (110,  72,  40)   # claw / buckle brown midtone
EARTH_D   = ( 70,  44,  24)
THIRD_EYE = ( 96, 196, 120)   # green-gold third-eye GLOW (the cool focal)
THIRD_BR  = (190, 246, 196)   # hot green-white inner of the third-eye
THIRD_GLD = (210, 232, 120)   # green-gold rim where the cool meets the warm mass
INK       = ( 28,  22,  26)   # hard ink keyline

BG        = ( 92,  88,  82)   # neutral warm-grey review backdrop
PANEL     = ( 72,  68,  64)
DAY_SKY_T = (120, 196, 236)   # day biome sky (top)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)   # night biome sky (top)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (240, 236, 230)
LABEL_DIM = (198, 192, 184)


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


# ── a single ornamental crown-skull (the fused arc + the pillar cap) ──────────
def crown_skull(surf, cx, cy, r, s, lit=False):
    """Tiny cream skull — domed cranium, two dark sockets, a stub jaw. WHY small
    high-contrast sockets: each crown skull must punch a clean bone shape with
    two dark dots at 32px so the dome stays the dominant value. `lit` swaps the
    eye-pins to the green-gold focal for the crown-CENTRE skull (the only crown
    glow in the value ladder)."""
    triad_circle(surf, BONE, (cx, cy), r, ow=max(1, int(1.6 * s)), core=False)
    jaw = [(cx - int(r * 0.52), cy + int(r * 0.52)),
           (cx + int(r * 0.52), cy + int(r * 0.52)),
           (cx + int(r * 0.34), cy + int(r * 1.0)),
           (cx - int(r * 0.34), cy + int(r * 1.0))]
    triad_blob(surf, BONE, jaw, ow=max(1, int(1.2 * s)))
    for ex in (cx - int(r * 0.38), cx + int(r * 0.38)):
        pygame.draw.circle(surf, INK, (ex, cy + int(r * 0.04)), max(1, int(r * 0.24)))
        if lit:
            pygame.draw.circle(surf, THIRD_EYE, (ex, cy + int(r * 0.04)), max(1, int(r * 0.13)))
            pygame.draw.circle(surf, THIRD_BR, (ex, cy + int(r * 0.02)), max(1, int(r * 0.06)))
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.42)), max(1, int(r * 0.13)))
    pygame.draw.line(surf, INK,
                     (cx - int(r * 0.34), cy + int(r * 0.70)),
                     (cx + int(r * 0.34), cy + int(r * 0.70)),
                     max(1, int(1.2 * s)))


# ── a tiny palm-skull cradled in an open hand (the core motif) ────────────────
def palm_skull(surf, hx, hy, r, s):
    """An open palm cradling a TINY skull — the locked core motif on all sisters.
    WHY a shallow bone cup with five short finger-ticks under a small cream skull:
    at hero scale you read the cupped hand; at 32px the six of them read as six
    even mid-value bone dots ringing the figure (the value ladder's middle rung,
    brighter than the crown, dimmer than the third-eye)."""
    # open palm cup — a shallow bone bowl beneath the skull
    cup = [(hx - int(r * 1.15), hy + int(r * 0.10)),
           (hx - int(r * 0.55), hy + int(r * 0.78)),
           (hx + int(r * 0.55), hy + int(r * 0.78)),
           (hx + int(r * 1.15), hy + int(r * 0.10)),
           (hx + int(r * 0.80), hy + int(r * 0.30)),
           (hx - int(r * 0.80), hy + int(r * 0.30))]
    triad_blob(surf, BONE, cup, ow=max(1, int(1.2 * s)))
    # five short finger-ticks splaying up around the skull (the open hand)
    for k in range(-2, 3):
        a = math.radians(-90 + k * 26)
        fx = hx + math.cos(a) * r * 1.05
        fy = hy + math.sin(a) * r * 1.05 + int(r * 0.05)
        pygame.draw.line(surf, INK, (hx + k * int(r * 0.2), hy + int(r * 0.05)),
                         (fx, fy), max(2, int(2.6 * s)))
        pygame.draw.line(surf, BONE, (hx + k * int(r * 0.2), hy + int(r * 0.05)),
                         (fx, fy), max(1, int(1.4 * s)))
    # the cradled skull — small cream dome with two dark sockets
    sk_y = hy - int(r * 0.30)
    triad_circle(surf, BONE, (hx, sk_y), int(r * 0.62), ow=max(1, int(1.2 * s)), core=False)
    for ex in (hx - int(r * 0.26), hx + int(r * 0.26)):
        pygame.draw.circle(surf, INK, (ex, sk_y + int(r * 0.04)), max(1, int(r * 0.15)))
    pygame.draw.circle(surf, BONE_DD, (hx, sk_y + int(r * 0.24)), max(1, int(r * 0.08)))
    # tiny jaw stub
    jaw = [(hx - int(r * 0.34), sk_y + int(r * 0.40)),
           (hx + int(r * 0.34), sk_y + int(r * 0.40)),
           (hx + int(r * 0.22), sk_y + int(r * 0.66)),
           (hx - int(r * 0.22), sk_y + int(r * 0.66))]
    triad_blob(surf, BONE, jaw, ow=max(1, int(1.0 * s)))


# ── the six-arm radial fan (the Mukha KIND tell) ──────────────────────────────
def draw_arm_fan(surf, sh_cx, sh_cy, s, hr):
    """Six fat bone arms splay in a wide symmetric STARBURST around the torso —
    the Mukha radial silhouette. Low origin, spread ~[100,64,28]deg off vertical
    (NONE straight up, so the crown sky stays open and the fused crown reads).
    Drawn behind the torso so the pelt sash and palm-skulls route in front.
    Returns the six hand centres for palm-skull placement."""
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


# ── the tiger pelt ornament set ───────────────────────────────────────────────
def _stripe_band(surf, p0, p1, width, s, n=5):
    """Tiger black stripes hashed ACROSS a sash run from p0->p1. WHY transverse
    ticks (not a fill): the diagonal tawny field hung with crisp black bars IS
    the brood read and the 32px carrier; they must be the highest-contrast detail
    on the pelt so the stripe-sash survives downscale."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = max(1.0, math.hypot(dx, dy))
    ux, uy = dx / L, dy / L          # along-sash
    nx, ny = -uy, ux                 # across-sash
    for i in range(n):
        t = (i + 0.6) / (n + 0.2)
        cx = p0[0] + dx * t
        cy = p0[1] + dy * t
        # a tapered stripe — wider on the outer edge for tiger taper
        w = width * (0.92 - 0.05 * math.sin(i * 1.3))
        a = (cx + nx * w * 0.5, cy + ny * w * 0.5)
        b = (cx - nx * w * 0.5, cy - ny * w * 0.5)
        # slight along-sash skew so stripes read as fur bands, not a ladder
        skew = ux * width * 0.16, uy * width * 0.16
        bar = [(a[0] - skew[0], a[1] - skew[1]), (a[0] + skew[0], a[1] + skew[1]),
               (b[0] + skew[0], b[1] + skew[1]), (b[0] - skew[0], b[1] - skew[1])]
        pygame.draw.polygon(surf, STRIPE, bar)
        pygame.draw.polygon(surf, STRIPE_BR, bar, max(1, int(1.0 * s)))


def tiger_face_buckle(surf, cx, cy, r, s):
    """The tiger-FACE buckle clasping the sash at the shoulder — a tawny round
    cat face with black brow-stripes, two green-tinged eyes and a snarl. Hero-only
    hero detail; mushes to a tawny disc at 32px (intended)."""
    triad_circle(surf, TAWNY, (cx, cy), r, ow=max(1, int(1.6 * s)), core=False)
    # cheek ruff lobes
    for sgn in (-1, 1):
        ruff = [(cx + sgn * int(r * 0.7), cy - int(r * 0.2)),
                (cx + sgn * int(r * 1.15), cy + int(r * 0.1)),
                (cx + sgn * int(r * 1.0), cy + int(r * 0.55)),
                (cx + sgn * int(r * 0.5), cy + int(r * 0.45))]
        triad_blob(surf, TAWNY, ruff, ow=max(1, int(1.2 * s)))
    triad_circle(surf, TAWNY, (cx, cy), int(r * 0.92), ow=max(1, int(1.0 * s)), core=False)
    # brow / forehead stripes (the tiger '王' read in miniature)
    for k in (-1, 0, 1):
        pygame.draw.line(surf, STRIPE, (cx + k * int(r * 0.22), cy - int(r * 0.78)),
                         (cx + k * int(r * 0.16), cy - int(r * 0.30)), max(2, int(2.4 * s)))
    for sgn in (-1, 1):
        pygame.draw.line(surf, STRIPE, (cx + sgn * int(r * 0.55), cy - int(r * 0.45)),
                         (cx + sgn * int(r * 0.9), cy - int(r * 0.25)), max(2, int(2.2 * s)))
        pygame.draw.line(surf, STRIPE, (cx + sgn * int(r * 0.55), cy + int(r * 0.0)),
                         (cx + sgn * int(r * 0.95), cy + int(r * 0.05)), max(2, int(2.2 * s)))
    # eyes — cream sclera with a green-gold glint (cool echo of the third-eye)
    for sgn in (-1, 1):
        ex = cx + sgn * int(r * 0.36)
        ey = cy - int(r * 0.05)
        pygame.draw.circle(surf, INK, (ex, ey), max(1, int(r * 0.22)))
        pygame.draw.circle(surf, THIRD_GLD, (ex, ey), max(1, int(r * 0.15)))
        pygame.draw.circle(surf, INK, (ex, ey), max(1, int(r * 0.07)))
    # muzzle + snarl
    pygame.draw.polygon(surf, BONE, [(cx - int(r * 0.18), cy + int(r * 0.18)),
                                     (cx + int(r * 0.18), cy + int(r * 0.18)),
                                     (cx, cy + int(r * 0.42))])
    pygame.draw.circle(surf, STRIPE, (cx, cy + int(r * 0.24)), max(1, int(r * 0.1)))
    pygame.draw.line(surf, INK, (cx, cy + int(r * 0.34)), (cx, cy + int(r * 0.52)),
                     max(1, int(1.6 * s)))
    for sgn in (-1, 1):
        # a small fang
        pygame.draw.polygon(surf, BONE_SH,
                            [(cx + sgn * int(r * 0.12), cy + int(r * 0.5)),
                             (cx + sgn * int(r * 0.22), cy + int(r * 0.5)),
                             (cx + sgn * int(r * 0.15), cy + int(r * 0.72))])


def claw_paw(surf, cx, cy, r, s):
    """A tiger claw-paw dangler — a tawny pad with three black claw-hooks. Hero
    detail hung off the pelt's lower edge; reads as a small tawny pip at 32px."""
    triad_circle(surf, TAWNY, (cx, cy), r, ow=max(1, int(1.2 * s)), core=False)
    pygame.draw.circle(surf, TAWNY_D, (cx, cy + int(r * 0.2)), int(r * 0.5))
    for k in (-1, 0, 1):
        bx = cx + k * int(r * 0.55)
        triad_circle(surf, TAWNY, (bx, cy + int(r * 0.62)), max(1, int(r * 0.34)),
                     ow=max(1, int(1.0 * s)), core=False, sheen=False)
        # the claw hook
        pygame.draw.line(surf, STRIPE, (bx, cy + int(r * 0.9)),
                         (bx - int(r * 0.18), cy + int(r * 1.35)), max(2, int(2.2 * s)))


# ── the fused tiger-pelt charnel adept ────────────────────────────────────────
def draw_vyaghra(surf, cx, cy, s):
    """A chibi Citipati dancing rib-barrel torso (cocked hip, one knee kicked
    out) wearing a Mukha six-arm radial fan, each open palm cradling a tiny
    skull, slung with a striped tiger-pelt sash (claw-paws + tail + tiger-face
    buckle), under a fused above-head crown (5-skull arc + tiara band) flanked by
    a paired tiger-EAR crest, and lit by a single green-gold third-eye.
    `s` = unit scale around a ~130-unit figure."""

    head_c = (cx, cy - int(28 * s))
    hr = int(26 * s)
    hip_y = cy + int(30 * s)
    hip_cx = cx + int(7 * s)          # hips cocked to the figure's right (the dance)

    # === SIX-ARM RADIAL FAN (drawn FIRST -> behind torso, head, pelt) =========
    hands = draw_arm_fan(surf, head_c[0], head_c[1] + int(hr * 0.92), s, hr)

    # === TIGER TAIL — a striped tawny tail flicking out behind the hip ========
    # WHY drawn early (behind the body): the tail is pelt mass that must route
    # BEHIND so it never occludes a palm-skull; it curls out low for the dance.
    tail_pts = [(hip_cx + int(2 * s), hip_y + int(2 * s)),
                (hip_cx + int(26 * s), hip_y + int(6 * s)),
                (hip_cx + int(46 * s), hip_y - int(2 * s)),
                (hip_cx + int(56 * s), hip_y - int(22 * s))]
    pygame.draw.lines(surf, INK, False, tail_pts, int(11 * s))
    pygame.draw.lines(surf, TAWNY, False, tail_pts, int(7 * s))
    # tail black rings
    for i, t in enumerate((0.32, 0.55, 0.78)):
        ti = int((len(tail_pts) - 1) * t)
        p = tail_pts[min(ti, len(tail_pts) - 2)]
        pygame.draw.circle(surf, STRIPE, (int(p[0]), int(p[1])), max(2, int(2.6 * s)))
    # tail tuft tip (black)
    triad_circle(surf, STRIPE, (hip_cx + int(56 * s), hip_y - int(22 * s)),
                 int(5 * s), ow=max(1, int(1.0 * s)), core=False, sheen=False)

    # === LEGS — wide cocked-hip dance: one knee kicked OUT (Citipati motion) ===
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

    # === PELVIS + RIBCAGE torso (Citipati rib barrel) =========================
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

    spine = [(hip_cx, hip_y - int(2 * s)),
             (cx + int(2 * s), cy + int(6 * s)),
             (cx - int(1 * s), cy - int(14 * s))]
    pygame.draw.lines(surf, INK, False, spine, int(8 * s))
    pygame.draw.lines(surf, BONE, False, spine, int(5 * s))

    rc_cx, rc_cy = cx, cy - int(2 * s)
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
    for i in range(4):
        ry = rc_cy - rc_h // 2 + int(8 * s) + i * int(8 * s)
        bw = int(rc_w * (0.46 - i * 0.05))
        pygame.draw.arc(surf, BONE_DD,
                        (rc_cx - bw, ry - int(7 * s), bw * 2, int(16 * s)),
                        math.radians(205), math.radians(335), max(2, int(2.4 * s)))
    pygame.draw.line(surf, BONE_DD, (rc_cx, rc_cy - rc_h // 2 + int(6 * s)),
                     (rc_cx, rc_cy + int(6 * s)), max(1, int(2 * s)))

    # === TIGER-PELT SASH — the diagonal stripe-band (the 32px CARRIER) ========
    # WHY a bold diagonal tawny band crossing the rib barrel shoulder-to-hip,
    # hashed with black stripes: this is the brood ornament class AND the gameplay
    # silhouette. Routed in FRONT of the body but it stays a SASH (a diagonal
    # ribbon, not a block) so the six palm-skulls ring it untouched.
    sash_top = (rc_cx - int(20 * s), rc_cy - int(18 * s))   # over the left shoulder
    sash_hip = (hip_cx + int(20 * s), hip_y + int(8 * s))   # down to the right hip
    # the tawny hide band (a tapered diagonal quad)
    def _perp(p0, p1, half):
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        L = max(1.0, math.hypot(dx, dy))
        return (-dy / L * half, dx / L * half)
    half0 = int(13 * s)
    half1 = int(10 * s)
    n0 = _perp(sash_top, sash_hip, half0)
    n1 = _perp(sash_top, sash_hip, half1)
    sash = [(sash_top[0] + n0[0], sash_top[1] + n0[1]),
            (sash_hip[0] + n1[0], sash_hip[1] + n1[1]),
            (sash_hip[0] - n1[0], sash_hip[1] - n1[1]),
            (sash_top[0] - n0[0], sash_top[1] - n0[1])]
    triad_blob(surf, TAWNY, sash,
               sheen_pts=[(sash_top[0] + n0[0], sash_top[1] + n0[1]),
                          (sash_hip[0] + n1[0] * 0.6, sash_hip[1] + n1[1] * 0.6),
                          (sash_hip[0] + n1[0] * 0.2, sash_hip[1] + n1[1] * 0.2),
                          (sash_top[0] + n0[0] * 0.3, sash_top[1] + n0[1] * 0.3)],
               ow=max(1, int(1.8 * s)))
    # black tiger stripes hashed across the band — the carrier detail
    _stripe_band(surf, sash_top, sash_hip, int(24 * s), s, n=6)
    # a scalloped fur edge on the lower run of the sash (hide, not cloth)
    dxh = sash_hip[0] - sash_top[0]
    dyh = sash_hip[1] - sash_top[1]
    for i in range(6):
        t = (i + 0.5) / 6
        bx = sash_top[0] + dxh * t - n1[0]
        by = sash_top[1] + dyh * t - n1[1]
        pygame.draw.circle(surf, TAWNY_BR, (int(bx), int(by)), max(1, int(2.0 * s)))

    # === the TAIL flutter / pelt fringe + CLAW-PAW danglers (hero detail) =====
    # claw-paws hung off the lower hip edge of the sash
    claw_paw(surf, hip_cx + int(14 * s), hip_y + int(20 * s), int(7 * s), s)
    claw_paw(surf, hip_cx - int(8 * s), hip_y + int(24 * s), int(6 * s), s)

    # === SIX PALM-SKULLS — one cradled in each open hand (the core motif) =====
    # WHY drawn after torso + sash, before head: they ride out at the fan hands so
    # the outer arc is six even cradled-skull masses (the value-ladder mid rung),
    # and the pelt sash sits BEHIND/BETWEEN them, never occluding any.
    palm_r = int(11 * s)
    for (hx, hy) in hands:
        palm_skull(surf, hx, hy, palm_r, s)

    # === the TIGER-FACE BUCKLE clasping the sash at the shoulder (hero) ========
    tiger_face_buckle(surf, sash_top[0] - int(2 * s), sash_top[1] + int(2 * s),
                      int(11 * s), s)

    # === SKULL HEAD — chibi, scary-cute, with the cool green-gold third eye ====
    triad_circle(surf, BONE, head_c, hr, ow=max(2, int(2 * s)))
    for sgn in (-1, 1):   # cheek hollows
        pygame.draw.circle(surf, BONE_D,
                           (head_c[0] + sgn * int(hr * 0.66), head_c[1] + int(hr * 0.28)),
                           int(hr * 0.26))
    # two big lower sockets — scary-CUTE, kept a NOTCH dimmer than the third eye
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.44)
        ey = head_c[1] + int(hr * 0.12)
        pygame.draw.circle(surf, BONE_DD, (ex, ey), int(hr * 0.32))
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.26))
        pygame.draw.circle(surf, EARTH_D, (ex + sgn * int(1 * s), ey + int(1 * s)),
                           int(hr * 0.10))
    # THIRD EYE of wisdom — the single BRIGHTEST pixel: a cool green-gold slit on
    # the brow with a hot green-white core, ringed green-gold where it meets the
    # warm mass. The only cool pin on the tawny field; out-glows the crown.
    tex, tey = head_c[0], head_c[1] - int(hr * 0.40)
    pygame.draw.ellipse(surf, INK, (tex - int(7 * s), tey - int(9 * s), int(14 * s), int(18 * s)))
    pygame.draw.ellipse(surf, THIRD_GLD, (tex - int(6 * s), tey - int(8 * s), int(12 * s), int(16 * s)))
    pygame.draw.ellipse(surf, THIRD_EYE, (tex - int(4 * s), tey - int(6 * s), int(8 * s), int(12 * s)))
    pygame.draw.circle(surf, THIRD_BR, (tex, tey - int(1 * s)), max(2, int(3.0 * s)))
    pygame.draw.circle(surf, (244, 255, 248), (tex, tey - int(2 * s)), max(1, int(1.5 * s)))
    # nose triangle
    pygame.draw.polygon(surf, BONE_DD,
                        [(head_c[0] - int(hr * 0.14), head_c[1] + int(hr * 0.26)),
                         (head_c[0] + int(hr * 0.14), head_c[1] + int(hr * 0.26)),
                         (head_c[0], head_c[1] + int(hr * 0.54))])
    # grinning tooth row (cute, not gory)
    my = head_c[1] + int(hr * 0.70)
    pygame.draw.line(surf, INK, (head_c[0] - int(hr * 0.5), my),
                     (head_c[0] + int(hr * 0.5), my), max(1, int(2 * s)))
    for k in range(-3, 4):
        pygame.draw.line(surf, INK, (head_c[0] + int(k * hr * 0.16), my - int(hr * 0.1)),
                         (head_c[0] + int(k * hr * 0.16), my + int(hr * 0.14)), max(1, int(1 * s)))

    # === FUSED ABOVE-HEAD CROWN: 5-skull arc-SWEEP + tiara BAND, flanked by =====
    # === a paired TIGER-EAR crest (ears FLANK the centre skull, never cap) =====
    # WHY ears drawn FIRST (behind), the arc + band drawn AFTER (in front): the
    # locked rule is the superstructure springs from BEHIND and never replaces the
    # arc. The two tawny ears sit to either SIDE of where the centre skull lands,
    # so the full 5-skull sweep + tiara band read clearly IN FRONT of them.
    arc_r  = int(hr * 1.55)          # skull centres ride outside the head
    skull_r = int(hr * 0.40)
    centre_a = math.radians(270)     # straight up = the centre skull seat

    # --- paired tiger-EAR crest (BEHIND the arc), FLANKING the centre skull ---
    # WHY pinned tight to the centre seat (~18deg to each side): the ears must
    # read as flanking the CENTRE skull specifically — two upright tawny tiger
    # ears poking up just to its left and right, between it and its neighbours —
    # NOT a wide crest behind the outer skulls. They spring from behind, so the
    # centre skull (drawn last) still sits in front of them, arc unbroken.
    centre_seat = (head_c[0] + math.cos(centre_a) * arc_r,
                   head_c[1] + math.sin(centre_a) * arc_r)
    for sgn in (-1, 1):
        # base hugs the centre skull's shoulder; the ear rises up-and-out
        bx = centre_seat[0] + sgn * int(skull_r * 0.95)
        by = centre_seat[1] - int(skull_r * 0.15)
        tipx = bx + sgn * int(skull_r * 0.85)
        tipy = by - int(skull_r * 1.55)
        ear = [(bx - sgn * int(skull_r * 0.30), by + int(skull_r * 0.30)),
               (bx + sgn * int(skull_r * 0.10), by - int(skull_r * 0.30)),
               (tipx, tipy),
               (bx + sgn * int(skull_r * 0.95), by + int(skull_r * 0.10))]
        triad_blob(surf, TAWNY, ear, ow=max(1, int(1.6 * s)))
        # inner-ear bone hollow so it reads as an ear, not a horn
        innr = [(bx + sgn * int(skull_r * 0.04), by - int(skull_r * 0.02)),
                ((bx + tipx) / 2 + sgn * int(skull_r * 0.10), (by + tipy) / 2),
                (bx + sgn * int(skull_r * 0.55), by - int(skull_r * 0.02))]
        pygame.draw.polygon(surf, BONE_SH, [(int(p[0]), int(p[1])) for p in innr])
        # a black tiger tick up the ear back
        pygame.draw.line(surf, STRIPE,
                         (int(bx + sgn * int(skull_r * 0.7)), int(by)),
                         (int(tipx - sgn * int(skull_r * 0.1)), int((by + tipy) / 2)),
                         max(2, int(2.0 * s)))

    # --- the tiara BAND across the brow (drawn over the head, under the arc) ---
    band_r = int(hr * 1.12)
    band_pts = []
    for i in range(13):
        a = math.radians(208 + i * (124 / 12))
        band_pts.append((head_c[0] + math.cos(a) * band_r,
                         head_c[1] + math.sin(a) * band_r))
    pygame.draw.lines(surf, INK, False, band_pts, int(7 * s))
    pygame.draw.lines(surf, TAWNY, False, band_pts, int(4 * s))
    pygame.draw.lines(surf, TAWNY_BR, False, band_pts[:7], max(1, int(1.4 * s)))
    # tiny black stripe ticks on the band so it reads as tiger-hide, not gold
    for i in range(1, 12, 2):
        pygame.draw.circle(surf, STRIPE, (int(band_pts[i][0]), int(band_pts[i][1])),
                           max(1, int(1.6 * s)))

    # --- the 5-skull arc-SWEEP (drawn LAST -> frontmost over ears + band) ----
    for i in range(5):
        a = math.radians(216 + i * (108 / 4))
        sx = head_c[0] + math.cos(a) * arc_r
        sy = head_c[1] + math.sin(a) * arc_r
        crown_skull(surf, int(sx), int(sy), skull_r, s, lit=(i == 2))


# ── the tiger-pelt khatvanga spine-staff → pillar mirror ──────────────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The pillar is built from the sister's OWN forms: a stacked column of
    vertebra beads (the rib-band torso motif) WRAPPED in a striped tiger-hide
    sleeve = the tileable shaft; a single crown-skull seated between a paired
    tiger-EAR crest = the creature-derived gap-edge cap (the same ears-flank-skull
    crown read, on-axis, never top-heavy). `cap` names the END that faces the GAP."""
    shaft_w = int(15 * s)
    pygame.draw.rect(surf, INK, (cx - int(3 * s), top, int(6 * s), bot - top))

    bead_pitch = int(20 * s)
    cap_room = int(34 * s)
    if cap == "bottom":
        b0, b1 = top + int(6 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(6 * s)
    y = b0
    idx = 0
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
        # a tiger-hide stripe sleeve cinched around each vertebra (alternating
        # side) so the shaft reads as the SAME striped pelt the creature wears
        side = -1 if (idx % 2 == 0) else 1
        sx0 = cx + side * int(bw * 0.2)
        wrap = [(sx0 - int(bw * 0.9), y - int(3 * s)),
                (sx0 + int(bw * 0.9), y - int(5 * s)),
                (sx0 + int(bw * 0.8), y + int(7 * s)),
                (sx0 - int(bw * 0.8), y + int(9 * s))]
        triad_blob(surf, TAWNY, wrap, ow=max(1, int(1.2 * s)))
        for k in (-1, 0, 1):
            pygame.draw.line(surf, STRIPE, (sx0 + k * int(bw * 0.5), y - int(4 * s)),
                             (sx0 + k * int(bw * 0.5), y + int(8 * s)), max(2, int(2.2 * s)))
        idx += 1
        y += bead_pitch

    # === gap-edge cap: a crown-skull flanked by a paired tiger-EAR crest ======
    cap_y = (bot - int(20 * s)) if cap == "bottom" else (top + int(20 * s))
    cap_skull_r = int(14 * s)
    # ears flank the skull (behind), so the cap echoes the creature's crown read
    for sgn in (-1, 1):
        ebx = cx + sgn * int(cap_skull_r * 1.05)
        eby = cap_y - int(cap_skull_r * 0.9)
        ear = [(ebx - sgn * int(cap_skull_r * 0.2), eby + int(cap_skull_r * 0.5)),
               (ebx + sgn * int(cap_skull_r * 0.5), eby - int(cap_skull_r * 0.2)),
               (ebx + sgn * int(cap_skull_r * 0.9), eby + int(cap_skull_r * 0.4)),
               (ebx + sgn * int(cap_skull_r * 0.4), eby + int(cap_skull_r * 0.7))]
        triad_blob(surf, TAWNY, ear, ow=max(1, int(1.2 * s)))
        pygame.draw.line(surf, STRIPE, (ebx + sgn * int(cap_skull_r * 0.2), eby + int(cap_skull_r * 0.3)),
                         (ebx + sgn * int(cap_skull_r * 0.6), eby), max(2, int(2.0 * s)))
    crown_skull(surf, cx, cap_y, cap_skull_r, s, lit=True)
    # a tiger-hide collar (tawny + stripe) where the cap meets the shaft
    collar_y = (cap_y - int(20 * s)) if cap == "bottom" else (cap_y + int(20 * s))
    pygame.draw.rect(surf, INK, (cx - int(12 * s), collar_y - int(4 * s), int(24 * s), int(9 * s)))
    pygame.draw.rect(surf, TAWNY, (cx - int(11 * s), collar_y - int(3 * s), int(22 * s), int(7 * s)))
    for k in range(-2, 3):
        pygame.draw.line(surf, STRIPE, (cx + k * int(5 * s), collar_y - int(3 * s)),
                         (cx + k * int(5 * s), collar_y + int(4 * s)), max(2, int(2.0 * s)))


# ── compose the review sheet ─────────────────────────────────────────────────
SS = 8


def render_creature_chip(boxw, boxh, draw_cx, draw_cy, scale):
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_vyaghra(big, draw_cx * SS, draw_cy * SS, scale * SS)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def export_hero():
    """Standalone hi-res hero (~1024px tall) on a charnel-cave panel.
    SS=8 supersample so the pelt stripes + six palm-skulls + fused crown stay
    crisp. Review art only — saved beside this script, never shipped."""
    HW, HH = 880, 1040
    panel = pygame.Surface((HW, HH))
    vgrad(panel, (0, 0, HW, HH), (58, 52, 50), (36, 32, 34))   # cave gloom
    # the figure spans ~130 units; place it centred with headroom for the crown
    big = pygame.Surface((HW * SS, HH * SS), pygame.SRCALPHA)
    draw_vyaghra(big, (HW // 2) * SS, int(HH * 0.56) * SS, 6.0 * SS)
    small = pygame.transform.smoothscale(big, (HW, HH))
    small = grow_outline(small, INK + (255,), 2)
    panel.blit(small, (0, 0))
    font = _load_font(30)
    font_sm = _load_font(19)
    panel.blit(font.render("VYAGHRA-CHARMA", True, LABEL), (28, 24))
    panel.blit(font_sm.render("tiger-pelt charnel adept  ·  hi-res hero (SS=8)", True, LABEL_DIM), (28, 64))
    out = os.path.join(_HERE, "round_1_hero.png")
    pygame.image.save(panel, out)
    print("wrote", out)


def main():
    W, H = 1180, 880
    font_big = _load_font(32)
    font = _load_font(18)
    font_sm = _load_font(13)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 58))
    sheet.blit(font_big.render("VYAGHRA-CHARMA", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "tiger-pelt charnel adept (sister #1, court II)  ·  CITIPATI body · 6-arm fan + 6 palm-skulls · "
        "fused 5-skull arc + tiara band, tiger-ears FLANK centre skull · stripe-sash = 32px carrier · round 1",
        True, LABEL_DIM), (300, 22))

    # === (a) BIG HERO =========================================================
    hero = render_creature_chip(390, 560, 195, 320, 2.7)
    sheet.blit(hero, (14, 84))
    sheet.blit(font.render("Creature — hero", True, LABEL), (120, 650))
    sheet.blit(font_sm.render("CITIPATI cocked-hip dance under a six-arm fan; each open palm cradles a tiny skull.", True, LABEL_DIM), (14, 676))
    sheet.blit(font_sm.render("Tiger-pelt sash (stripes + claw-paws + tail + tiger-face buckle). Green-gold 3rd eye =", True, LABEL_DIM), (14, 692))
    sheet.blit(font_sm.render("brightest. Fused crown: 5-skull arc + tiara band; tiger-EARS FLANK the centre skull.", True, LABEL_DIM), (14, 708))

    # === (b) PILLAR assembled — mirrored, sister's own forms ==================
    pcx = 430
    top_big = pygame.Surface((150 * SS, 270 * SS), pygame.SRCALPHA)
    draw_pillar(top_big, 75 * SS, 4 * SS, 266 * SS, 1.0 * SS, cap="bottom")
    top_seg = grow_outline(pygame.transform.smoothscale(top_big, (150, 270)), INK + (255,), 1)
    sheet.blit(top_seg, (pcx, 80))
    bot_big = pygame.Surface((150 * SS, 270 * SS), pygame.SRCALPHA)
    draw_pillar(bot_big, 75 * SS, 4 * SS, 266 * SS, 1.0 * SS, cap="top")
    bot_seg = grow_outline(pygame.transform.smoothscale(bot_big, (150, 270)), INK + (255,), 1)
    sheet.blit(bot_seg, (pcx, 80 + 270 + 100))
    pygame.draw.rect(sheet, (58, 54, 50), (pcx + 8, 80 + 270, 134, 100))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 80 + 270 + 42))
    sheet.blit(font.render("Pillar — pelt-wrapped spine", True, LABEL), (pcx - 4, 730))
    sheet.blit(font_sm.render("vertebra beads in a striped tiger-hide sleeve =", True, LABEL_DIM), (pcx - 4, 756))
    sheet.blit(font_sm.render("shaft; crown-skull flanked by tiger-ears caps the", True, LABEL_DIM), (pcx - 4, 772))
    sheet.blit(font_sm.render("gap (mirrored top<->bottom, on-axis, not top-heavy)", True, LABEL_DIM), (pcx - 4, 788))

    # === (c) TRUE 32px DAY + NIGHT chips + blackout proof =====================
    panel_x = 632
    pygame.draw.rect(sheet, PANEL, (panel_x, 80, W - panel_x - 14, 720))
    sheet.blit(font.render("True 32px gameplay-scale", True, LABEL), (panel_x + 16, 90))

    def chip32():
        big = pygame.Surface((110 * SS, 110 * SS), pygame.SRCALPHA)
        draw_vyaghra(big, 55 * SS, 58 * SS, (32 / 150.0) * SS)
        small = pygame.transform.smoothscale(big, (110, 110))
        return grow_outline(small, INK + (255,), 1)

    chip = chip32()

    day_y = 124
    vgrad(sheet, (panel_x + 20, day_y, 150, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 20, day_y + 20))
    sheet.blit(font_sm.render("32px on day sky", True, LABEL), (panel_x + 20, day_y + 156))

    night_y = day_y + 184
    vgrad(sheet, (panel_x + 20, night_y, 150, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 20, night_y + 20))
    sheet.blit(font_sm.render("32px on night sky", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    # 32px pillar gap-cap chip beside, both skies
    def pillar_chip32():
        big = pygame.Surface((44 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 22 * SS, 2 * SS, 128 * SS, 0.32 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (44, 130))
        return grow_outline(small, INK + (255,), 1)

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

    # === (d) BLACKOUT / SILHOUETTE proof ======================================
    blk_x = panel_x + 264
    sheet.blit(font_sm.render("silhouette", True, LABEL_DIM), (blk_x + 4, day_y - 16))
    # hero-scale mask filled solid to prove the read (sash + arms + crown)
    sil_big = pygame.Surface((130 * SS, 150 * SS), pygame.SRCALPHA)
    draw_vyaghra(sil_big, 65 * SS, 78 * SS, (120 / 150.0) * SS)
    sil = pygame.transform.smoothscale(sil_big, (130, 150))
    mask = pygame.mask.from_surface(sil)
    sil_surf = mask.to_surface(setcolor=(18, 16, 18, 255), unsetcolor=(0, 0, 0, 0))
    pygame.draw.rect(sheet, (200, 198, 196), (blk_x, day_y, 130, 150))
    pygame.draw.rect(sheet, INK, (blk_x, day_y, 130, 150), 1)
    sheet.blit(sil_surf, (blk_x, day_y))
    # 32px silhouette beside it (the carrier read)
    sil32_big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
    draw_vyaghra(sil32_big, 48 * SS, 50 * SS, (32 / 150.0) * SS)
    sil32 = pygame.transform.smoothscale(sil32_big, (96, 96))
    m32 = pygame.mask.from_surface(sil32)
    sil32_surf = m32.to_surface(setcolor=(18, 16, 18, 255), unsetcolor=(0, 0, 0, 0))
    pygame.draw.rect(sheet, (200, 198, 196), (blk_x, night_y, 96, 96))
    pygame.draw.rect(sheet, INK, (blk_x, night_y, 96, 96), 1)
    sheet.blit(sil32_surf, (blk_x, night_y))
    sheet.blit(font_sm.render("32px sil", True, LABEL_DIM), (blk_x, night_y + 100))

    # === palette strip ========================================================
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, 500))
    swatches = [
        (BONE, "cream bone (mass)"), (BONE_D, "bone shade"),
        (TAWNY, "tawny-gold pelt"), (TAWNY_BR, "tawny sheen"),
        (STRIPE, "black stripe"), (EARTH, "claw/buckle"),
        (THIRD_EYE, "green-gold 3rd-eye"), (THIRD_GLD, "green-gold rim"),
        (INK, "ink keyline"), (BONE_DD, "deep hollow"),
    ]
    sxp, syp = panel_x + 16, 528
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 250
        ry = syp + row * 28
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, ry, 18, 18))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 26, ry + 3))

    # bottom note strip
    pygame.draw.rect(sheet, PANEL, (14, 828, W - 28, 42))
    sheet.blit(font_sm.render(
        "ELEVATED pipeline: SS=8 supersample -> smoothscale.  Value ladder: green-gold 3rd-eye brightest -> 6 palm-skulls "
        "mid -> crown dimmest. Glow ONLY on 3rd-eye + crown-centre skull.  STAY: flat fills · ink keyline (28,22,26) · "
        "triad · 1px grown outline · chibi scary-cute · procedural-only.",
        True, LABEL_DIM), (26, 842))

    out = os.path.join(_HERE, "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    export_hero()
    main()
