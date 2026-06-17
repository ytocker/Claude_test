"""
Round-1 concept renderer for ASHA-MUKTI — the lotus bloom-mandorla bone-saint
(Mukha-Devi spin-off brood, concept #1). Headless Pygame; ELEVATED pipeline
(supersample SS=6 → smoothscale) so the eight slender arms + lotus-pod relics
stay crisp at downscale. Keeps the citipati house grammar: flat triad
(dark-core → flat-fill → top-left rim-sheen), hard ink keyline (28,22,26),
1px alpha-grown outline, chibi proportions, scary-CUTE; procedural-only.

WHY this is the closed tall-ALMOND mandorla KIND (the CHIBI/small pole of the
brood): eight thin bone arms sprout from a LOW shoulder line and curve up and
INWARD to MEET at a single teardrop point ABOVE the crown. The blackout must
read as one unmistakable vertical pointed ALMOND (a sacred mandorla / vesica
aureole around the saint) — never the wide OPEN sideways starburst of mother
Mukha, never a circle or open fan. Where Mukha's six fat arms splay OUT, Asha's
eight thin arms close IN: the closed point is the whole identity tell, so the
hands ride the rim of the almond, NOT off in a peripheral ring.

WHY warm butter-saffron → lotus-peach bloom (NOT pink): the cross-set pin bans
echoing mother Mukha's magenta-rose, and Stupika's hard metallic gilt. So the
accent is a SOFT WARM-GOLD that blooms into PEACH — a lotus opening, a saint's
calm aureole-glow. Demonstrably NOT rose: zero magenta in the ramp, the hottest
note is a pale peach, never a pink. The bone is a WARM ivory core, not white.

WHY lotus-pod relics with skulls only in the TWO LOWEST hands: the arm-ends are
lotus seed-pods; the arc-tips that build the almond point stay CLEAN glow-caps
so the silhouette point reads pure, and the death-DNA (tiny skulls among the
arm-end ornaments) is carried by the two LOWEST pods where there is room for a
socketed skull without muddying the point.

WHY the lotus-stalk reliquary IS the pillar: a bottom-rooted bone stalk hung
with lotus-pod pendants tiles as the repeatable shaft; the cap blooms into a
lotus flower with a saffron seed-glow at the gap — the creature's own closed-
bloom language continued on-axis.

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
# Warm IVORY bone-core is the dominant mass — clearly WARM, never the cold white
# Mukha was barred from. The single accent is a SOFT saffron→peach bloom; there
# is deliberately ZERO magenta in the ramp (anti-mother-Mukha rose) and the gold
# is soft-warm, not Stupika's hard metallic gilt.
BONE      = (236, 222, 196)   # warm ivory bone (the dominant fill)
BONE_D    = (188, 166, 138)   # warm-tan bone dark-core / shade
BONE_DD   = (138, 116,  92)   # deepest warm bone hollow (sockets, gaps)
BONE_SH   = (252, 244, 224)   # bone top-left rim-sheen
SAFF      = (238, 190,  86)   # butter-saffron — the warm-gold bloom base
SAFF_D    = (180, 134,  54)   # deep saffron shade
PEACH     = (248, 196, 150)   # lotus-peach — the soft bloom highlight (NOT pink)
PEACH_BR  = (255, 226, 196)   # palest peach bloom inner / sheen
GLOW_CORE = (255, 244, 214)   # hottest pixel — warm white-gold seed-glow core
INK       = ( 28,  22,  26)   # hard ink keyline
THIRD_EYE = (238, 190,  86)   # third-eye glow (saffron, the saint's calm focus)

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


def thick_curve(surf, color, p0, p1, p2, width, steps=16, sheen=False):
    """Draw a quadratic-bezier arm as a chain of fat dots → a smooth tapering
    bone limb. WHY a dot-chain not a polyline: round caps overlap into a clean
    continuous curve with no mitre gaps, and the hard ink keyline is grown
    after, so the slender arms stay one solid stroke at downscale."""
    pts = []
    for i in range(steps + 1):
        t = i / steps
        x = (1-t)**2 * p0[0] + 2*(1-t)*t * p1[0] + t*t * p2[0]
        y = (1-t)**2 * p0[1] + 2*(1-t)*t * p1[1] + t*t * p2[1]
        pts.append((x, y))
    # ink keyline pass (fatter), then the warm-bone fill pass
    for col, w in ((INK, width + max(2, width // 3)), (color, width)):
        for i in range(len(pts) - 1):
            a, b = pts[i], pts[i + 1]
            pygame.draw.line(surf, col, a, b, int(w))
            pygame.draw.circle(surf, col, (int(b[0]), int(b[1])), int(w // 2))
    if sheen:
        # a thin top-left sheen ribbon along the inner half of the curve
        sh = lerp(color, (255, 255, 255), 0.4)
        for i in range(len(pts) // 2):
            a = pts[i]
            pygame.draw.circle(surf, sh, (int(a[0]), int(a[1])), max(1, int(width * 0.22)))
    return pts


# ── a single lotus-pod relic (arm-end ornament) ───────────────────────────────
def lotus_pod(surf, cx, cy, r, s, ang, skull=False, glow=True):
    """An arm-end lotus seed-pod relic. WHY a pod, not a weapon: Asha is a calm
    bloom-saint, not a wrathful armoury — the relics are lotus pods that bloom a
    soft saffron seed-glow. The TWO LOWEST pods cradle a tiny socketed skull
    (the death-DNA among the ornaments); the arc-tip pods stay CLEAN glow-caps
    so the almond point reads pure. `ang` orients the pod outward off the rim."""
    # the pod body — a small warm-bone teardrop
    tip = (cx + math.cos(ang) * r * 1.15, cy + math.sin(ang) * r * 1.15)
    lobe = [(cx + math.cos(ang - 2.1) * r, cy + math.sin(ang - 2.1) * r),
            (cx + math.cos(ang + 2.1) * r, cy + math.sin(ang + 2.1) * r),
            tip]
    triad_blob(surf, BONE, lobe, ow=max(1, int(1.3 * s)))
    triad_circle(surf, BONE, (cx, cy), int(r * 0.92), ow=max(1, int(1.3 * s)), core=False)
    if skull:
        # a tiny socketed skull seated in the pod — the arm-end death tell
        sr = int(r * 0.62)
        triad_circle(surf, BONE_SH, (cx, cy - int(r * 0.06)), sr,
                     ow=max(1, int(1.1 * s)), core=False, sheen=False)
        for ex in (cx - int(sr * 0.42), cx + int(sr * 0.42)):
            pygame.draw.circle(surf, INK, (ex, cy - int(r * 0.02)), max(1, int(sr * 0.30)))
        pygame.draw.circle(surf, INK, (cx, cy + int(sr * 0.34)), max(1, int(sr * 0.18)))
        # tiny jaw line
        pygame.draw.line(surf, INK, (cx - int(sr * 0.5), cy + int(sr * 0.5)),
                         (cx + int(sr * 0.5), cy + int(sr * 0.5)), max(1, int(s)))
    elif glow:
        # a clean saffron→peach seed-glow cap (the calm bloom)
        pygame.draw.circle(surf, SAFF_D, (cx, cy), max(1, int(r * 0.52)))
        pygame.draw.circle(surf, SAFF, (cx, cy), max(1, int(r * 0.42)))
        pygame.draw.circle(surf, PEACH, (cx - int(r * 0.12), cy - int(r * 0.14)),
                           max(1, int(r * 0.26)))
        pygame.draw.circle(surf, PEACH_BR, (cx - int(r * 0.16), cy - int(r * 0.18)),
                           max(1, int(r * 0.12)))


# ── a single ornamental tiara-skull (reused for tiara + pillar relics) ────────
def tiara_skull(surf, cx, cy, r, s, lit=False):
    """Tiny warm-bone skull for the skull-crown — the preserved DNA. WHY a domed
    cranium with two dark sockets: it must punch a clean bone shape with two
    sockets at 32px. Centre skull lit saffron so the crown reads warm-gold."""
    triad_circle(surf, BONE, (cx, cy), r, ow=max(1, int(1.4 * s)), core=False)
    jaw = [(cx - int(r * 0.5), cy + int(r * 0.5)),
           (cx + int(r * 0.5), cy + int(r * 0.5)),
           (cx + int(r * 0.32), cy + int(r * 0.94)),
           (cx - int(r * 0.32), cy + int(r * 0.94))]
    triad_blob(surf, BONE, jaw, ow=max(1, int(1.1 * s)))
    eye_c = PEACH_BR if lit else INK
    for ex in (cx - int(r * 0.38), cx + int(r * 0.38)):
        pygame.draw.circle(surf, INK, (ex, cy + int(r * 0.02)), max(1, int(r * 0.26)))
        if lit:
            pygame.draw.circle(surf, eye_c, (ex, cy + int(r * 0.02)), max(1, int(r * 0.14)))
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.42)), max(1, int(r * 0.14)))


# ── the eight-arm closed almond (the KIND tell) ───────────────────────────────
def draw_arm_almond(surf, sh_cx, sh_cy, head_cy, s, reach):
    """Eight thin bone arms sprout from a LOW shoulder line and curve up and IN
    to MEET at a single teardrop point ABOVE the crown — the closed tall-almond
    mandorla, the ONLY closed-point silhouette in the brood.

    WHY eight thin (vs Mukha's six fat): more + thinner arms describe a smooth
    almond RIM; the pairs are placed so their bezier control points pull every
    arm toward a shared apex high above the head, so the outer envelope is one
    pointed vertical almond. The LOWEST pair hangs nearly straight down to close
    the BOTTOM point of the almond too, so the blackout is pointed at BOTH ends
    (a true vesica/mandorla), not an open fan.

    Returns (hand centres, apex point) — hands ride the almond RIM for relics."""
    shoulder_y = sh_cy
    apex = (sh_cx, head_cy - int(reach * 0.98))          # the teardrop point ABOVE crown
    bottom = (sh_cx, shoulder_y + int(reach * 0.70))     # the lower point of the almond
    arm_th = int(6.5 * s)
    hands = []
    # Every arm is ONE bone curve from the shoulder, OUT to a rim hand, then ON
    # to a shared point — so the eight outer edges trace a single pointed almond.
    # `t` ∈ (0,1) = how high the hand rides the rim; widest rim hand near t≈0.5.
    # `frac` = how much of the rim's vertical span this arm covers between the
    # bottom point and the apex, so the bone edges nest into one convex lens.
    rim_t = [0.86, 0.60, 0.34, 0.12]
    # half-width of the almond at its widest (the rim belly)
    belly = reach * 0.62
    for sgn in (-1, 1):
        for t in rim_t:
            sh = (sh_cx + sgn * int(reach * 0.14), shoulder_y)
            # vertical position of this hand on the rim: lerp bottom→apex
            ry = bottom[1] + (apex[1] - bottom[1]) * t
            # almond half-width at height t follows a lens profile (0 at both ends)
            w = belly * math.sin(math.pi * t) ** 0.7
            hand = (sh_cx + sgn * w, ry)
            # leg 1: shoulder bows OUT to the rim hand
            c1 = (sh[0] + sgn * w * 1.15, (sh[1] + ry) * 0.5 + reach * 0.04)
            thick_curve(surf, BONE, sh, c1, hand, arm_th, sheen=(sgn < 0))
            # leg 2: the rim hand sweeps ON toward the shared point (up or down).
            # upper arms reach the APEX; lower arms reach the BOTTOM point — both
            # close the lens so the blackout is pointed at BOTH ends.
            target = apex if t >= 0.5 else bottom
            c2 = (sh_cx + sgn * w * 0.42, (ry + target[1]) * 0.5)
            thick_curve(surf, BONE, hand, c2, target, max(2, int(arm_th * 0.82)))
            hands.append((sgn, t, hand))
    # the apex knuckle where the top arms meet — a small clean bone bead (point)
    triad_circle(surf, BONE, apex, max(2, int(arm_th * 0.78)),
                 ow=max(1, int(1.2 * s)), core=False, sheen=False)
    triad_circle(surf, BONE, bottom, max(2, int(arm_th * 0.72)),
                 ow=max(1, int(1.2 * s)), core=False, sheen=False)
    return hands, apex


# ── the lotus bloom-mandorla bone-saint ───────────────────────────────────────
def draw_asha_mukti(surf, cx, cy, s):
    """A tiny-idol bone-saint: a small chibi torso under a big calm chibi skull,
    haloed by eight slender arms that close into a pointed almond mandorla above
    the crown. Warm saffron→peach bloom-glow, a skull-crown, lotus-pod relics.
    `s` = unit scale around a ~130-unit figure."""

    # WHY a BIG calm head over a SHORT torso, tiny overall: this is the CHIBI /
    # tiny-idol pole of the brood. A large serene skull + squat body = a little
    # devotional figurine, demonstrably smaller-feeling than mother Mukha.
    head_c = (cx, cy - int(20 * s))
    hr = int(28 * s)
    reach = int(78 * s)
    pod_r = int(8 * s)

    # === EIGHT-ARM CLOSED ALMOND (drawn first → arms sit BEHIND torso & head) =
    # WHY behind: the almond is the AUREOLE the saint sits inside, so the limbs
    # frame the body from behind and meet in the point above the crown.
    sh_y = head_c[1] + int(hr * 1.05)
    hands, apex = draw_arm_almond(surf, head_c[0], sh_y, head_c[1], s, reach)

    # === LOWER BODY — a small lotus-seat base (keeps the idol footed, not leggy)
    base_y = cy + int(40 * s)
    base = [(cx - int(28 * s), base_y - int(6 * s)),
            (cx - int(19 * s), base_y - int(13 * s)),
            (cx + int(19 * s), base_y - int(13 * s)),
            (cx + int(28 * s), base_y - int(6 * s)),
            (cx + int(21 * s), base_y + int(9 * s)),
            (cx - int(21 * s), base_y + int(9 * s))]
    triad_blob(surf, BONE, base,
               core_pts=[(cx, base_y - int(12 * s)), (cx + int(23 * s), base_y - int(6 * s)),
                         (cx + int(17 * s), base_y + int(7 * s)), (cx, base_y + int(6 * s))],
               ow=max(1, int(1.6 * s)))
    # lotus-petal seat grooves
    for k in range(-2, 3):
        px = cx + int(k * 9 * s)
        pygame.draw.line(surf, BONE_DD, (px, base_y - int(13 * s)),
                         (px, base_y + int(7 * s)), max(1, int(1.3 * s)))

    # === TORSO — a SHORT rib barrel (squat, so the head + almond hold the mass)
    rc_cx, rc_cy = cx, cy + int(12 * s)
    rc_w, rc_h = int(28 * s), int(22 * s)
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
        ry = rc_cy - rc_h // 2 + int(7 * s) + i * int(7 * s)
        bw = int(rc_w * (0.42 - i * 0.05))
        pygame.draw.arc(surf, BONE_DD,
                        (rc_cx - bw, ry - int(6 * s), bw * 2, int(13 * s)),
                        math.radians(205), math.radians(335), max(2, int(2.0 * s)))
    pygame.draw.line(surf, BONE_DD, (rc_cx, rc_cy - rc_h // 2 + int(5 * s)),
                     (rc_cx, rc_cy + int(3 * s)), max(1, int(1.8 * s)))

    # === LOTUS-POD RELICS — one at each arm-end (skulls in the TWO LOWEST) =====
    # WHY skulls only in the two lowest: the arc-tip pods that build the almond
    # point stay CLEAN glow-caps so the silhouette point reads pure; the death
    # DNA rides the two lowest hands where a socketed skull has room.
    lowest_t = min(h[1] for h in hands)
    for sgn, t, hand in hands:
        oa = math.atan2(hand[1] - rc_cy, hand[0] - rc_cx)
        is_lowest = abs(t - lowest_t) < 1e-3
        lotus_pod(surf, int(hand[0]), int(hand[1]), pod_r, s, oa,
                  skull=is_lowest, glow=not is_lowest)

    # === SKULL HEAD — chibi, scary-CUTE, SERENE three-eyed (the calm saint) ====
    triad_circle(surf, BONE, head_c, hr, ow=max(2, int(2 * s)))
    for sgn in (-1, 1):   # gentle cheek hollows
        pygame.draw.circle(surf, BONE_D,
                           (head_c[0] + sgn * int(hr * 0.64), head_c[1] + int(hr * 0.28)),
                           int(hr * 0.24))
    # two calm lower sockets — gentle, kept a NOTCH DIMMER than the third eye
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.42)
        ey = head_c[1] + int(hr * 0.16)
        pygame.draw.circle(surf, BONE_DD, (ex, ey), int(hr * 0.30))
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.25))
        pygame.draw.circle(surf, SAFF_D, (ex + sgn * int(1 * s), ey + int(1 * s)),
                           int(hr * 0.11))
    # THIRD EYE — the single BRIGHTEST pixel: a calm saffron-bloom dot on the brow.
    tex, tey = head_c[0], head_c[1] - int(hr * 0.34)
    pygame.draw.ellipse(surf, INK, (tex - int(6 * s), tey - int(8 * s), int(12 * s), int(16 * s)))
    pygame.draw.ellipse(surf, SAFF, (tex - int(5 * s), tey - int(7 * s), int(10 * s), int(14 * s)))
    pygame.draw.ellipse(surf, PEACH, (tex - int(3 * s), tey - int(4 * s), int(7 * s), int(9 * s)))
    pygame.draw.circle(surf, GLOW_CORE, (tex - int(1 * s), tey - int(2 * s)), max(2, int(3.0 * s)))
    pygame.draw.circle(surf, (255, 255, 255), (tex - int(1 * s), tey - int(2 * s)),
                       max(1, int(1.4 * s)))
    # nose triangle
    pygame.draw.polygon(surf, BONE_DD,
                        [(head_c[0] - int(hr * 0.13), head_c[1] + int(hr * 0.30)),
                         (head_c[0] + int(hr * 0.13), head_c[1] + int(hr * 0.30)),
                         (head_c[0], head_c[1] + int(hr * 0.54))])
    # a small SERENE closed-mouth tooth row (calm saint, not a wrathful grin)
    my = head_c[1] + int(hr * 0.70)
    pygame.draw.line(surf, INK, (head_c[0] - int(hr * 0.40), my),
                     (head_c[0] + int(hr * 0.40), my), max(1, int(2 * s)))
    for k in range(-2, 3):
        pygame.draw.line(surf, INK, (head_c[0] + int(k * hr * 0.16), my - int(hr * 0.07)),
                         (head_c[0] + int(k * hr * 0.16), my + int(hr * 0.07)), max(1, int(s)))

    # === SKULL-CROWN / TIARA (preserved DNA) — a low warm-bone 3-skull band ====
    # WHY low + only three: it must sit ON the brow under the almond apex so the
    # crown reads against the open sky inside the almond's upper point.
    tiara_r = int(hr * 0.94)
    tiara_skull_r = int(hr * 0.28)
    band_pts = []
    for i in range(9):
        a = math.radians(238 + i * (64 / 8))
        band_pts.append((head_c[0] + math.cos(a) * tiara_r,
                         head_c[1] + math.sin(a) * tiara_r))
    pygame.draw.lines(surf, INK, False, band_pts, int(5 * s))
    pygame.draw.lines(surf, SAFF, False, band_pts, int(3 * s))
    pygame.draw.lines(surf, PEACH, False, band_pts[:5], max(1, int(1.2 * s)))
    for i in range(3):
        a = math.radians(244 + i * (52 / 2))
        sx = head_c[0] + math.cos(a) * tiara_r
        sy = head_c[1] + math.sin(a) * tiara_r
        tiara_skull(surf, int(sx), int(sy), tiara_skull_r, s, lit=(i == 1))


# ── the lotus-stalk reliquary → pillar mirror ─────────────────────────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The lotus-stalk reliquary IS the pillar: a bottom-rooted bone stalk hung
    with lotus-pod pendants tiles as the repeatable shaft; the cap blooms into a
    closed lotus flower with a saffron seed-glow at the gap — the saint's own
    closed-bloom language, on-axis. `cap` names the END that faces the GAP."""
    shaft_w = int(7 * s)
    pod_r = int(6 * s)
    pygame.draw.rect(surf, INK, (cx - int(3 * s), top, int(6 * s), bot - top))

    band_pitch = int(24 * s)
    cap_room = int(36 * s)
    if cap == "bottom":
        b0, b1 = top + int(6 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(6 * s)
    # a slender ridged bone stalk (the tileable shaft)
    stalk = [(cx - shaft_w, b0), (cx + shaft_w, b0),
             (cx + shaft_w, b1), (cx - shaft_w, b1)]
    triad_blob(surf, BONE, stalk,
               core_pts=[(cx, b0), (cx + shaft_w, b0), (cx + shaft_w, b1), (cx, b1)],
               sheen_pts=[(cx - shaft_w, b0), (cx - int(shaft_w * 0.3), b0),
                          (cx - int(shaft_w * 0.3), b1), (cx - shaft_w, b1)],
               ow=max(1, int(1.4 * s)))
    y = b0 + int(12 * s)
    idx = 0
    while y <= b1 - int(8 * s):
        # a stalk node groove + a lotus-pod pendant on alternating sides
        pygame.draw.line(surf, BONE_DD, (cx - shaft_w, y), (cx + shaft_w, y), max(1, int(1.4 * s)))
        side = -1 if (idx % 2 == 0) else 1
        rx = cx + side * (shaft_w + int(9 * s))
        ry = y + int(3 * s)
        pygame.draw.line(surf, SAFF, (cx + side * shaft_w, y), (rx, ry), max(1, int(1.4 * s)))
        # every 3rd pendant cradles a tiny skull (the death DNA on the shaft too)
        lotus_pod(surf, rx, ry, pod_r, s, math.radians(0 if side > 0 else 180),
                  skull=(idx % 3 == 1), glow=(idx % 3 != 1))
        idx += 1
        y += band_pitch

    # === gap-edge cap: a closed lotus bloom + saffron seed-glow ===============
    # WHY a closed-petal lotus with a lit seed: it mirrors the saint's closed
    # almond bloom in miniature and glows toward the gap, on-axis and never wider
    # than the pod span (not top-heavy).
    cap_y = (bot - int(22 * s)) if cap == "bottom" else (top + int(22 * s))
    grow = +1 if cap == "bottom" else -1
    bloom_r = int(16 * s)
    # closed lotus petals — slender pointed bone leaves converging up toward gap
    for k in range(7):
        a = math.radians(-90 + (k - 3) * 19) if grow > 0 else math.radians(90 + (k - 3) * 19)
        tip = (cx + math.cos(a) * bloom_r, cap_y + math.sin(a) * bloom_r)
        base_l = (cx + math.cos(a - 0.12) * bloom_r * 0.28, cap_y + math.sin(a - 0.12) * bloom_r * 0.28)
        base_r = (cx + math.cos(a + 0.12) * bloom_r * 0.28, cap_y + math.sin(a + 0.12) * bloom_r * 0.28)
        triad_blob(surf, BONE, [base_l, tip, base_r], ow=max(1, int(1.1 * s)))
    # a thin saffron collar where the bloom meets the stalk
    collar_y = cap_y - grow * int(bloom_r + int(2 * s))
    pygame.draw.rect(surf, INK, (cx - int(9 * s), collar_y - int(3 * s), int(18 * s), int(7 * s)))
    pygame.draw.rect(surf, SAFF, (cx - int(8 * s), collar_y - int(2 * s), int(16 * s), int(5 * s)))
    pygame.draw.rect(surf, PEACH, (cx - int(8 * s), collar_y - int(2 * s), int(16 * s), int(2 * s)))
    # the glowing saffron seed at the bloom heart (the gap glow)
    triad_circle(surf, BONE, (cx, cap_y), int(6 * s), ow=max(1, int(1.3 * s)), core=False)
    pygame.draw.circle(surf, SAFF, (cx, cap_y), int(4 * s))
    pygame.draw.circle(surf, PEACH, (cx, cap_y), max(1, int(2.4 * s)))
    pygame.draw.circle(surf, GLOW_CORE, (cx - int(s), cap_y - int(s)), max(1, int(1.4 * s)))


# ── compose the review sheet ─────────────────────────────────────────────────
SS = 6


def font_at(size):
    return pygame.font.Font(
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "..", "..", "..", "..", "..", "game", "assets",
                     "LiberationSans-Bold.ttf"), size)


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def main():
    W, H = 1010, 820
    font_big = font_at(30)
    font = font_at(17)
    font_sm = font_at(12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("ASHA-MUKTI", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "lotus bloom-mandorla bone-saint  ·  KIND: closed tall-almond · CHIBI tiny-idol · warm saffron->peach bloom (NOT pink) · round 1",
        True, LABEL_DIM), (250, 26))

    # === (a) BIG HERO =========================================================
    hero = pygame.Surface((360 * SS, 480 * SS), pygame.SRCALPHA)
    draw_asha_mukti(hero, 180 * SS, 250 * SS, 1.55 * SS)
    hero = grow_outline(pygame.transform.smoothscale(hero, (360, 480)), INK + (255,), 1)
    sheet.blit(hero, (14, 82))
    sheet.blit(font.render("Creature - hero", True, LABEL), (110, 562))
    sheet.blit(font_sm.render("EIGHT slender arms close to a teardrop point ABOVE the crown = a vertical almond.", True, LABEL_DIM), (14, 588))
    sheet.blit(font_sm.render("Saffron third-eye = the single brightest pixel; calm serene chibi saint, tiny-idol scale.", True, LABEL_DIM), (14, 604))
    sheet.blit(font_sm.render("Arm-ends = lotus-pod relics; tiny skulls in the TWO LOWEST pods, arc-tips clean glow-caps.", True, LABEL_DIM), (14, 620))

    # === (b) PILLAR assembled — mirrored, bottom-rooted lotus-stalk ===========
    pcx = 470
    top_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(top_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="bottom")
    top_seg = grow_outline(pygame.transform.smoothscale(top_big, (150, 250)), INK + (255,), 1)
    sheet.blit(top_seg, (pcx, 82))
    bot_big = pygame.Surface((150 * SS, 250 * SS), pygame.SRCALPHA)
    draw_pillar(bot_big, 75 * SS, 4 * SS, 246 * SS, 1.0 * SS, cap="top")
    bot_seg = grow_outline(pygame.transform.smoothscale(bot_big, (150, 250)), INK + (255,), 1)
    sheet.blit(bot_seg, (pcx, 82 + 250 + 96))
    pygame.draw.rect(sheet, (60, 58, 70), (pcx + 8, 82 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 82 + 250 + 40))
    sheet.blit(font.render("Pillar - lotus-stalk reliquary", True, LABEL), (pcx - 4, 686))
    sheet.blit(font_sm.render("bottom-rooted bone stalk hung with lotus-pod", True, LABEL_DIM), (pcx - 4, 710))
    sheet.blit(font_sm.render("pendants = shaft; a closed lotus bloom +", True, LABEL_DIM), (pcx - 4, 726))
    sheet.blit(font_sm.render("saffron seed-glow caps the gap (mirrored)", True, LABEL_DIM), (pcx - 4, 742))

    # === (c) right panel: TRUE 32px chips + blackout proof + palette ==========
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 82, W - panel_x - 14, 564))
    sheet.blit(font.render("True 32px chip + blackout proof", True, LABEL), (panel_x + 16, 90))

    def chip32():
        big = pygame.Surface((110 * SS, 110 * SS), pygame.SRCALPHA)
        draw_asha_mukti(big, 55 * SS, 60 * SS, (32 / 130.0) * SS)
        small = pygame.transform.smoothscale(big, (110, 110))
        return grow_outline(small, INK + (255,), 1)

    chip = chip32()

    day_y = 120
    vgrad(sheet, (panel_x + 18, day_y, 96, 130), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 18, day_y, 96, 130), 1)
    sheet.blit(chip, (panel_x + 18 - 7, day_y + 10))
    sheet.blit(font_sm.render("32px DAY", True, LABEL), (panel_x + 18, day_y + 134))

    vgrad(sheet, (panel_x + 124, day_y, 96, 130), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 124, day_y, 96, 130), 1)
    sheet.blit(chip, (panel_x + 124 - 7, day_y + 10))
    sheet.blit(font_sm.render("32px NIGHT", True, LABEL_DIM), (panel_x + 124, day_y + 134))

    # === blackout silhouette proof — the almond must read pure ================
    blk_big = pygame.Surface((360 * SS, 480 * SS), pygame.SRCALPHA)
    draw_asha_mukti(blk_big, 180 * SS, 250 * SS, 1.55 * SS)
    blk = pygame.transform.smoothscale(blk_big, (150, 200))
    # flatten every opaque pixel to solid ink → the silhouette proof
    mask = pygame.mask.from_surface(blk)
    sil_mask_surf = mask.to_surface(setcolor=INK + (255,), unsetcolor=(0, 0, 0, 0))
    proof_x, proof_y = panel_x + 18, day_y + 158
    pygame.draw.rect(sheet, (210, 210, 216), (proof_x, proof_y, 150, 200))
    pygame.draw.rect(sheet, INK, (proof_x, proof_y, 150, 200), 1)
    sheet.blit(sil_mask_surf, (proof_x, proof_y))
    sheet.blit(font_sm.render("BLACKOUT: vertical pointed ALMOND", True, LABEL), (proof_x, proof_y + 202))

    # pillar 32px chip (day) beside the proof
    def pillar_chip32(captype):
        big = pygame.Surface((40 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 20 * SS, 2 * SS, 128 * SS, 0.30 * SS, cap=captype)
        small = pygame.transform.smoothscale(big, (40, 130))
        return grow_outline(small, INK + (255,), 1)

    px2 = panel_x + 178
    vgrad(sheet, (px2, proof_y, 44, 200), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (px2, proof_y, 44, 200), 1)
    sheet.blit(pillar_chip32("bottom"), (px2 + 2, proof_y + 8))
    sheet.blit(font_sm.render("pillar", True, LABEL_DIM), (px2 + 2, proof_y - 16))

    # === palette strip ========================================================
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, day_y + 374))
    swatches = [
        (BONE, "warm ivory bone"), (BONE_D, "warm-tan shade"),
        (SAFF, "butter-saffron"), (PEACH, "lotus-peach bloom"),
        (PEACH_BR, "pale peach sheen"), (GLOW_CORE, "warm seed-glow"),
        (THIRD_EYE, "third-eye saffron"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, day_y + 400
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 160
        ry = syp + row * 26
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, ry, 18, 18))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 26, ry + 3))

    pygame.draw.rect(sheet, PANEL, (14, 770, W - 28, 40))
    sheet.blit(font_sm.render(
        "ELEVATED pipeline: SS=6 supersample -> smoothscale.  STAY: flat triad (dark-core->fill->top-left sheen) · "
        "hard ink keyline (28,22,26) · 1px grown outline · CHIBI tiny-idol · scary-cute · procedural-only.",
        True, LABEL_DIM), (26, 783))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
