"""
Round-1 concept renderer for RATNA-PADMINI — the jewel-lotus throne mother
(mukha_citipati_court brood, sister #5; the gentlest, the brood's PREMIUM /
high-end anchor). Headless Pygame; HIGH-RES pipeline (supersample SS=8 →
smoothscale) so the highest small-element count in the brood stays crisp at
downscale. Keeps the shipped house grammar: flat saturated fills, hard 1-2px
ink keyline (28,22,26), dark-core → flat-fill → top-left rim-sheen triad, 1px
alpha-grown outline, chibi proportions, scary-CUTE; procedural-only (no
gradients/PNGs).

WHY this sister is the premium CONTRAST piece: turquoise + lavish gold + coral
read as jewel-and-treasure against the wrathful sisters' bone-and-fire. The
look must be RICH by drawn jewel-edge value (gold rims, cabochon highlights,
inlay facets), NOT by bloom — glow is confined to the turquoise third-eye + the
crown-centre skull only, per the value ladder.

WHY she is the ONLY sister with a FULL enclosing flame-halo (prabhamandala): the
locked 32px element. With the highest small-element count in the brood (jewel
inlay + tassels + beadwork + per-petal gems + a tiered throne), the two-scale
rule is policed hardest here — the closed halo RING is the one element that
carries the gameplay silhouette; every fiddly inlay/tassel/per-petal gem is
HERO-ONLY and is dropped at true 32px. The body is MUKHA's squat chibi
rib-barrel over a wide 6-petal lotus base; she fuses the Citipati 5-skull
arc-sweep AND the Mukha tiara-band across the brow into one gem-studded crown.

WHY the jewel-lotus throne IS the pillar: a stacked column of tiered lotus
thrones (her own base, repeated) threaded on a gold rod = the tileable shaft;
the gap-edge cap is a single gem-tipped lotus blossom inside a small closed
flame-ring with a glowing turquoise cabochon at the hub — her own forms,
symmetric and on-axis.

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
# Bone is the structural mass but pushed warm-pale so the GOLD + TURQUOISE read
# as the dominant treasure hues (this is the premium / high-end anchor). Coral
# is the tassel accent. Everything reads rich by drawn value, never by bloom.
BONE      = (236, 224, 206)   # warm pale bone (structural mass)
BONE_D    = (186, 168, 144)   # bone dark-core / shade
BONE_DD   = (132, 116,  96)   # deepest bone hollow (sockets, rib gaps)
BONE_SH   = (250, 244, 230)   # bone top-left rim-sheen
TURQ      = ( 56, 178, 178)   # turquoise — third-eye + cabochons + halo cores
TURQ_BR   = (138, 226, 222)   # hot turquoise inner / sheen
TURQ_HOT  = (208, 248, 244)   # hottest turquoise core (third-eye brightest)
TURQ_D    = ( 30, 112, 116)   # deep turquoise shade
GOLD      = (226, 182,  72)   # lavish gold — the dominant treasure metal
GOLD_BR   = (250, 220, 128)   # hot gold sheen / facet
GOLD_HOT  = (255, 244, 196)   # hottest gold spark
GOLD_D    = (166, 124,  44)   # deep gold shade (rim, recessed inlay)
CORAL     = (236, 110,  88)   # coral tassel accent
CORAL_BR  = (252, 170, 144)
CORAL_D   = (172,  62,  52)
INK       = ( 28,  22,  26)   # hard ink keyline
THIRD_EYE = ( 56, 178, 178)   # turquoise third-eye (the single brightest focal)

BG        = ( 88,  92,  98)   # neutral grey review backdrop
PANEL     = ( 70,  74,  82)
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


# ── a faceted jewel cabochon (the premium tell — HERO-only detail) ────────────
def cabochon(surf, c, r, s, col, br, glow=False):
    """A round gem in a gold bezel with a hard facet highlight. WHY a gold rim +
    a single bright facet pip: this is what makes the sprite read RICH by drawn
    jewel-edge value, not by bloom — the bezel separates the gem from bone and
    the pip gives it the cut-stone glint. `glow` reserves the brightest core for
    the focal cabochons only (third-eye + crown-centre)."""
    cx, cy = int(c[0]), int(c[1])
    # gold bezel
    triad_circle(surf, GOLD, (cx, cy), r + max(1, int(2 * s)),
                 ow=max(1, int(1.4 * s)), core=False, sheen=False)
    pygame.draw.circle(surf, GOLD_D, (cx, cy), r + max(1, int(2 * s)), max(1, int(1.2 * s)))
    # the stone
    triad_circle(surf, col, (cx, cy), r, ow=max(1, int(1.2 * s)), core=False)
    pygame.draw.circle(surf, lerp(col, INK, 0.4),
                       (cx + int(r * 0.30), cy + int(r * 0.32)), int(r * 0.62))
    pygame.draw.circle(surf, col, (cx, cy), int(r * 0.78))
    # the hard facet glint
    pygame.draw.circle(surf, br, (cx - int(r * 0.32), cy - int(r * 0.34)),
                       max(1, int(r * 0.34)))
    if glow:
        pygame.draw.circle(surf, TURQ_HOT, (cx - int(r * 0.16), cy - int(r * 0.18)),
                           max(1, int(r * 0.20)))


# ── a coral tassel — bell-cap + cord + fringe (HERO-only beadwork) ────────────
def tassel(surf, x, y, length, s, sgn=1):
    """A hanging coral tassel: a gold bell-cap, a beaded cord, a coral fringe of
    threads. WHY HERO-only: at 32px the threads are sub-pixel and would mush into
    the halo ring — these only survive on the big hero, dropped at gameplay scale
    per the two-scale rule."""
    # gold bell-cap
    triad_circle(surf, GOLD, (int(x), int(y)), max(1, int(3.2 * s)),
                 ow=max(1, int(1 * s)), core=False, sheen=False)
    # a couple of gold beads on the cord
    for k in (1, 2):
        by = y + k * int(4.5 * s)
        pygame.draw.circle(surf, GOLD_D, (int(x), int(by)), max(1, int(2.0 * s)))
        pygame.draw.circle(surf, GOLD_BR, (int(x - 1 * s), int(by - 1 * s)), max(1, int(0.9 * s)))
    # coral fringe threads spreading slightly
    base_y = y + int(11 * s)
    for k in range(-2, 3):
        tx = x + k * int(2.2 * s)
        ty = base_y + length + abs(k) * int(2 * s)
        pygame.draw.line(surf, CORAL_D, (int(x), int(base_y)), (int(tx), int(ty)), max(1, int(2.0 * s)))
        pygame.draw.line(surf, CORAL, (int(x), int(base_y)), (int(tx), int(ty)), max(1, int(1.2 * s)))
        pygame.draw.circle(surf, CORAL_BR, (int(tx), int(ty)), max(1, int(1.6 * s)))


# ── a single ornamental tiara/crown skull (cloned from Mukha tiara_skull) ─────
def tiara_skull(surf, cx, cy, r, s, lit=False):
    """Tiny pale-bone skull for the fused crown arc + tiara-band. WHY a domed
    cranium with two dark dots: it must punch a clean bone shape with two sockets
    at 32px. For ratna it is gem-studded — a turquoise brow-cabochon set on the
    forehead — but that gem is HERO-only; at small scale the bone dome carries it.
    `lit` reserves the hot turquoise eyes for the crown-CENTRE skull (the only
    crown glow)."""
    triad_circle(surf, BONE, (cx, cy), r, ow=max(1, int(1.4 * s)), core=False)
    jaw = [(cx - int(r * 0.5), cy + int(r * 0.5)),
           (cx + int(r * 0.5), cy + int(r * 0.5)),
           (cx + int(r * 0.32), cy + int(r * 0.94)),
           (cx - int(r * 0.32), cy + int(r * 0.94))]
    triad_blob(surf, BONE, jaw, ow=max(1, int(1.1 * s)))
    eye_c = TURQ_HOT if lit else INK
    for ex in (cx - int(r * 0.38), cx + int(r * 0.38)):
        pygame.draw.circle(surf, INK, (ex, cy + int(r * 0.02)), max(1, int(r * 0.26)))
        if lit:
            pygame.draw.circle(surf, eye_c, (ex, cy + int(r * 0.02)), max(1, int(r * 0.14)))
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.42)), max(1, int(r * 0.14)))


# ── crown-skull (cloned from Citipati crown_skull, for the arc-sweep) ─────────
def crown_skull(surf, cx, cy, r, s, lit=False):
    """Tiny bone skull for the Citipati 5-skull arc-SWEEP that rides the OUTER
    crown silhouette. Domed cranium, two small high-contrast sockets, a stub jaw.
    `lit` swaps the eyes to hot turquoise for the crown-centre (the one crown
    glow per the value ladder)."""
    triad_circle(surf, BONE, (cx, cy), r, ow=max(1, int(1.6 * s)), core=False)
    jaw = [(cx - int(r * 0.52), cy + int(r * 0.52)),
           (cx + int(r * 0.52), cy + int(r * 0.52)),
           (cx + int(r * 0.34), cy + int(r * 1.0)),
           (cx - int(r * 0.34), cy + int(r * 1.0))]
    triad_blob(surf, BONE, jaw, ow=max(1, int(1.2 * s)))
    eye_c = TURQ_HOT if lit else INK
    for ex in (cx - int(r * 0.38), cx + int(r * 0.38)):
        pygame.draw.circle(surf, INK, (ex, cy + int(r * 0.04)), max(1, int(r * 0.24)))
        if lit:
            pygame.draw.circle(surf, eye_c, (ex, cy + int(r * 0.04)), max(1, int(r * 0.13)))
    pygame.draw.circle(surf, INK, (cx, cy + int(r * 0.42)), max(1, int(r * 0.13)))
    pygame.draw.line(surf, INK,
                     (cx - int(r * 0.34), cy + int(r * 0.70)),
                     (cx + int(r * 0.34), cy + int(r * 0.70)),
                     max(1, int(1.2 * s)))


# ── the FULL enclosing flame-halo RING — prabhamandala (THE 32px element) ─────
def flame_halo(surf, cx, cy, rad, s, lobes=22, reach=1.0, full=True):
    """A complete enclosing lobed flame ring — the prabhamandala. Cloned from
    Citipati's flame_halo but rebuilt CLOSED: ratna is the ONLY sister with a
    full enclosing halo, and it is the locked element that carries the gameplay
    silhouette at true 32px. WHY value-graded gold→turquoise tongues, not orange
    fire: this halo is jewel-edged treasure, not a wrathful pyre — gold tongues
    with cool turquoise tips read as her premium prabhamandala and stay distinct
    from the wrathful sisters' ember halos.

    `full=True` draws the entire ring (no bottom gap); each tongue is a slim,
    separated flame so the ring reads as a clean lobed band with sky between the
    tongues — dense but never a solid disc. At 32px the lobed band collapses to
    the one bold ring that defines the silhouette."""
    base_r = rad * 0.94
    tip_r = rad * (1.10 + 0.26 * reach)
    half_w = (math.pi / lobes) * 0.46
    angles = [-math.pi / 2 + (i / lobes) * 2 * math.pi for i in range(lobes)]
    for ang in angles:
        if not full and math.sin(ang) > 0.5:
            continue
        a0 = ang - half_w
        a1 = ang + half_w
        base0 = (cx + math.cos(a0) * base_r, cy + math.sin(a0) * base_r)
        base1 = (cx + math.cos(a1) * base_r, cy + math.sin(a1) * base_r)
        tipp = (cx + math.cos(ang) * tip_r, cy + math.sin(ang) * tip_r)
        kink = (cx + math.cos(ang + half_w * 0.5) * (base_r + (tip_r - base_r) * 0.55),
                cy + math.sin(ang + half_w * 0.5) * (base_r + (tip_r - base_r) * 0.55))
        tongue = [base0, kink, tipp, base1]
        pygame.draw.polygon(surf, INK, tongue)
        pygame.draw.polygon(surf, GOLD, tongue)
        mid0 = (base0[0] + (tipp[0] - base0[0]) * 0.50, base0[1] + (tipp[1] - base0[1]) * 0.50)
        mid1 = (base1[0] + (tipp[0] - base1[0]) * 0.50, base1[1] + (tipp[1] - base1[1]) * 0.50)
        pygame.draw.polygon(surf, GOLD_BR, [base0, mid0, tipp, mid1])
        # cool turquoise tip = the jewel-treasure read, separates from gold body
        pygame.draw.polygon(surf, TURQ_BR, [mid0, tipp, mid1])
        pygame.draw.polygon(surf, INK, tongue, max(1, int(1.0 * s)))
    # a thin gold inner ring at the foot of the tongues ties the band together
    pygame.draw.circle(surf, GOLD_D, (int(cx), int(cy)), int(base_r), max(2, int(2.4 * s)))


# ── the six-arm radial fan (cloned from Mukha draw_arm_fan) ───────────────────
def draw_arm_fan(surf, sh_cx, sh_cy, s, hr):
    """Six fat bone arms splay in a wide symmetric STARBURST around the torso —
    the brood KIND tell. Cloned from Mukha: low-origin shoulders, spread
    ~[100,64,28]° off vertical, NO arm aimed straight up so a clean wedge of open
    sky stays above the crown. For ratna each arm carries a thin gold armlet band
    (HERO-only beadwork). Returns the six hand centres for the palm-skulls."""
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
        # a thin gold armlet band at the elbow (HERO inlay — sub-pixel at 32px)
        pygame.draw.circle(surf, GOLD, (int(elbow[0]), int(elbow[1])),
                           int(arm_th * 0.58), max(1, int(1.6 * s)))
        hands.append((sgn, d, hand))
    hands.sort(key=lambda h: (h[0], -h[1]))
    return [(int(h[2][0]), int(h[2][1])) for h in hands]


# ── an open palm cradling a TINY SKULL (the brood motif) ──────────────────────
def palm_skull(surf, hx, hy, s, ang, mid=True):
    """An open bone PALM (a small fan of finger ticks) cradling ONE tiny bone
    skull — the locked brood motif replacing Mukha's relic-discs. WHY the cupped
    palm + skull: at the fan tips this gives six even mid-value skulls in a ring
    (the value ladder's middle rung: brighter than the crown, dimmer than the
    third-eye). The palm fingers fan AWAY from the torso so the cup opens outward."""
    pr = int(7 * s)
    # the cupped palm — a small bone blob
    triad_circle(surf, BONE, (hx, hy), pr, ow=max(1, int(1.3 * s)), core=False)
    # finger ticks fanning outward
    for k in range(-2, 3):
        fa = ang + math.radians(k * 22)
        ex = hx + math.cos(fa) * pr * 1.9
        ey = hy + math.sin(fa) * pr * 1.9
        pygame.draw.line(surf, INK, (hx, hy), (int(ex), int(ey)), max(1, int(2.2 * s)))
        pygame.draw.line(surf, BONE, (hx, hy), (int(ex), int(ey)), max(1, int(1.3 * s)))
    # the tiny cradled skull, nudged outward into the cup
    skx = hx + int(math.cos(ang) * pr * 0.55)
    sky_ = hy + int(math.sin(ang) * pr * 0.55)
    sr = int(5.4 * s)
    # mid value: a touch warmer/darker bone so the palm-skulls sit BELOW the
    # third-eye but ABOVE the dim crown skulls in the ladder.
    triad_circle(surf, lerp(BONE, BONE_D, 0.25), (skx, sky_), sr,
                 ow=max(1, int(1.2 * s)), core=False)
    for ex in (skx - int(sr * 0.42), skx + int(sr * 0.42)):
        pygame.draw.circle(surf, INK, (ex, sky_ - int(sr * 0.05)), max(1, int(sr * 0.30)))
    pygame.draw.circle(surf, INK, (skx, sky_ + int(sr * 0.40)), max(1, int(sr * 0.16)))
    # a gold rim sliver around the cradled skull = the premium tell (HERO inlay)
    pygame.draw.circle(surf, GOLD, (skx, sky_), sr + max(1, int(1.4 * s)), max(1, int(1.2 * s)))


# ── the jewel-lotus throne mother ─────────────────────────────────────────────
def draw_ratna_padmini(surf, cx, cy, s):
    """Pint-sized jewel-lotus throne mother: a squat MUKHA chibi torso on a wide
    tiered gem-tipped lotus throne, framed by a FULL enclosing gold-turquoise
    flame-halo, under a six-arm radial fan whose palms each cradle a tiny skull.
    A gem-studded fused crown (Citipati 5-skull arc + Mukha tiara-band + turquoise
    brow-cabochons) tops the head; a turquoise third-eye slit is the single
    brightest pixel. `s` = unit scale around a ~150-unit figure."""

    head_c = (cx, cy - int(28 * s))
    hr = int(32 * s)

    # === FULL ENCLOSING FLAME-HALO (drawn FIRST → behind everything) ==========
    # WHY it wraps the whole figure, not just the head: a prabhamandala encloses
    # the deity. Centred low between head and torso so head, throne, and fan all
    # sit inside the ring. This is the locked 32px silhouette element.
    halo_c = (cx, cy - int(2 * s))
    flame_halo(surf, halo_c[0], halo_c[1], int(82 * s), s, lobes=24, reach=1.0, full=True)

    # === SIX-ARM RADIAL FAN (behind torso & head, frames the face) ============
    hands = draw_arm_fan(surf, head_c[0], head_c[1] + int(hr * 0.82), s, hr)

    # === TIERED GEM-TIPPED LOTUS THRONE (the wide MUKHA base, enriched) =======
    # WHY a tiered throne, not a flat base: three stacked petal tiers read as a
    # high-end throne. Per-petal gold-tipped gems are HERO-only; at 32px the
    # stacked tiers collapse to one wide pedestal mass under the body.
    base_y = cy + int(44 * s)
    for tier, (half, lift, pet) in enumerate(((40, 0, 6), (32, 14, 5), (24, 26, 4))):
        ty = base_y - int(lift * s)
        hw = int(half * s)
        petal = [(cx - hw, ty - int(6 * s)),
                 (cx - int(hw * 0.7), ty - int(13 * s)),
                 (cx + int(hw * 0.7), ty - int(13 * s)),
                 (cx + hw, ty - int(6 * s)),
                 (cx + int(hw * 0.8), ty + int(10 * s)),
                 (cx - int(hw * 0.8), ty + int(10 * s))]
        triad_blob(surf, BONE, petal,
                   core_pts=[(cx, ty - int(12 * s)), (cx + hw, ty - int(6 * s)),
                             (cx + int(hw * 0.8), ty + int(8 * s)), (cx, ty + int(6 * s))],
                   ow=max(1, int(1.6 * s)))
        # per-petal grooves + a gold-tipped gem in each petal (HERO inlay)
        for k in range(-(pet // 2), pet // 2 + 1):
            px = cx + int(k * (2 * half / max(1, pet)) * s)
            pygame.draw.line(surf, BONE_DD, (px, ty - int(12 * s)),
                             (px, ty + int(8 * s)), max(1, int(1.3 * s)))
            cabochon(surf, (px, ty - int(8 * s)), max(1, int(2.6 * s)), s,
                     CORAL if (k % 2) else TURQ, CORAL_BR if (k % 2) else TURQ_BR)
    # a turquoise seed-cabochon at the lotus heart — kept BELOW the third-eye so
    # it stays a secondary focal, never the brightest pixel.
    cabochon(surf, (cx, base_y - int(20 * s)), int(5 * s), s, TURQ, TURQ_BR)

    # === TORSO — a SHORT MUKHA rib barrel (squat, mass held low) ==============
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

    # === JEWELLED BEADWORK NECKLACE + a GOLD INLAY GIRDLE (HERO ornament) =====
    # WHY a 3-bead choker + a swag of cabochons across the chest: she must never
    # read naked — beadwork wraps the torso. All HERO-only; at 32px it collapses
    # into the torso mass under the halo. Gold girdle band at the waist.
    neck_y = rc_cy - rc_h // 2 + int(3 * s)
    swag = []
    for k in range(-3, 4):
        sxp = rc_cx + int(k * 5 * s)
        syp = neck_y + int(7 * s) + int(abs(k) * 1.4 * s)
        swag.append((sxp, syp))
    pygame.draw.lines(surf, GOLD_D, False, swag, max(1, int(2.0 * s)))
    for (sxp, syp) in swag:
        cabochon(surf, (sxp, syp), max(1, int(2.2 * s)), s, TURQ, TURQ_BR)
    # the gold girdle band at the waist with a coral centre cabochon
    gy = rc_cy + int(rc_h * 0.36)
    pygame.draw.line(surf, INK, (rc_cx - int(rc_w * 0.42), gy),
                     (rc_cx + int(rc_w * 0.42), gy), max(2, int(4.0 * s)))
    pygame.draw.line(surf, GOLD, (rc_cx - int(rc_w * 0.42), gy),
                     (rc_cx + int(rc_w * 0.42), gy), max(1, int(2.4 * s)))
    cabochon(surf, (rc_cx, gy), max(1, int(2.8 * s)), s, CORAL, CORAL_BR)

    # === SIX PALM-SKULLS — one cradled in each open palm (the motif) ==========
    for (hx, hy) in hands:
        oa = math.atan2(hy - rc_cy, hx - rc_cx)
        palm_skull(surf, hx, hy, s, oa)

    # === CORAL TASSELS hanging from the lowest pair of palms (HERO beadwork) ==
    # WHY only from the lowest hands: tassels read as treasure hanging from the
    # outstretched arms without crossing the face; sub-pixel at 32px, hero-only.
    low = sorted(hands, key=lambda h: -h[1])[:2]
    for (hx, hy) in low:
        tassel(surf, hx, hy + int(8 * s), int(16 * s), s)

    # === SKULL HEAD — chibi, scary-cute, three-eyed (the framed FACE) =========
    triad_circle(surf, BONE, head_c, hr, ow=max(2, int(2 * s)))
    for sgn in (-1, 1):   # cheek hollows
        pygame.draw.circle(surf, BONE_D,
                           (head_c[0] + sgn * int(hr * 0.66), head_c[1] + int(hr * 0.28)),
                           int(hr * 0.26))
    # two lower sockets — scary-CUTE, kept dimmer than the third eye (the ladder)
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.42)
        ey = head_c[1] + int(hr * 0.16)
        pygame.draw.circle(surf, BONE_DD, (ex, ey), int(hr * 0.30))
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.25))
        pygame.draw.circle(surf, TURQ_D, (ex + sgn * int(1 * s), ey + int(1 * s)),
                           int(hr * 0.12))
    # THIRD EYE — turquoise slit, the single BRIGHTEST pixel (AD hard rule).
    tex, tey = head_c[0], head_c[1] - int(hr * 0.34)
    pygame.draw.ellipse(surf, INK, (tex - int(7 * s), tey - int(9 * s), int(14 * s), int(18 * s)))
    pygame.draw.ellipse(surf, TURQ, (tex - int(6 * s), tey - int(8 * s), int(12 * s), int(16 * s)))
    pygame.draw.ellipse(surf, TURQ_BR, (tex - int(4 * s), tey - int(5 * s), int(8 * s), int(10 * s)))
    pygame.draw.circle(surf, TURQ_HOT, (tex - int(1 * s), tey - int(2 * s)), max(2, int(3.2 * s)))
    pygame.draw.circle(surf, (255, 255, 255), (tex - int(1 * s), tey - int(2 * s)),
                       max(1, int(1.6 * s)))
    # nose triangle
    pygame.draw.polygon(surf, BONE_DD,
                        [(head_c[0] - int(hr * 0.14), head_c[1] + int(hr * 0.30)),
                         (head_c[0] + int(hr * 0.14), head_c[1] + int(hr * 0.30)),
                         (head_c[0], head_c[1] + int(hr * 0.56))])
    # gentle grinning tooth row (the gentlest sister — softer grin, no fangs)
    my = head_c[1] + int(hr * 0.72)
    pygame.draw.line(surf, INK, (head_c[0] - int(hr * 0.44), my),
                     (head_c[0] + int(hr * 0.44), my), max(1, int(2 * s)))
    for k in range(-3, 4):
        pygame.draw.line(surf, INK, (head_c[0] + int(k * hr * 0.14), my - int(hr * 0.08)),
                         (head_c[0] + int(k * hr * 0.14), my + int(hr * 0.11)), max(1, int(1 * s)))

    # === FUSED GEM-STUDDED CROWN — Citipati arc-SWEEP + Mukha tiara-BAND =======
    # WHY both crown languages, fused: the locked rule. A WIDE 5-skull arc rides
    # the OUTER silhouette (the Citipati sweep) AND a gold tiara-band seats across
    # the brow with turquoise brow-cabochons (the Mukha band) — both visibly
    # present. Crown skulls are the DIMMEST rung of the value ladder; only the
    # centre skull is lit turquoise (the one crown glow).

    # (1) the Mukha tiara-BAND seated on the brow — gold, with brow-cabochons
    tiara_r = int(hr * 0.98)
    band_pts = []
    for i in range(11):
        a = math.radians(232 + i * (76 / 10))   # seated low across the brow
        band_pts.append((head_c[0] + math.cos(a) * tiara_r,
                         head_c[1] + math.sin(a) * tiara_r))
    pygame.draw.lines(surf, INK, False, band_pts, int(7 * s))
    pygame.draw.lines(surf, GOLD, False, band_pts, int(4 * s))
    pygame.draw.lines(surf, GOLD_BR, False, band_pts[:6], max(1, int(1.4 * s)))
    # three turquoise brow-cabochons studding the band (HERO inlay)
    for i in (2, 5, 8):
        bx, by = band_pts[i]
        cabochon(surf, (bx, by), max(1, int(3.0 * s)), s, TURQ, TURQ_BR)

    # (2) the Citipati 5-skull arc-SWEEP riding the OUTER crown silhouette
    skull_cr = hr * 1.46
    skull_r = int(hr * 0.34)
    for i in range(5):
        a = math.radians(218 + i * (104 / 4))
        sx = head_c[0] + math.cos(a) * skull_cr
        sy = head_c[1] + math.sin(a) * skull_cr
        crown_skull(surf, int(sx), int(sy), skull_r, s, lit=(i == 2))


# ── the jewel-lotus throne → pillar mirror ────────────────────────────────────
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """The jewel-lotus throne IS the pillar: a stacked column of tiered lotus
    thrones (her own base, repeated) threaded on a gold rod = the tileable shaft;
    the gap-edge cap is a single gem-tipped lotus blossom inside a small CLOSED
    flame-ring with a glowing turquoise cabochon at the hub — her own forms,
    symmetric and on-axis, never top-heavy.

    `cap` names the END that faces the GAP."""
    shaft_w = int(14 * s)
    # central gold rod the lotus tiers thread onto (her treasure metal)
    pygame.draw.rect(surf, INK, (cx - int(4 * s), top, int(8 * s), bot - top))
    pygame.draw.rect(surf, GOLD_D, (cx - int(3 * s), top, int(6 * s), bot - top))

    tier_pitch = int(26 * s)
    cap_room = int(38 * s)
    if cap == "bottom":
        b0, b1 = top + int(8 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(8 * s)
    y = b0
    idx = 0
    while y <= b1:
        # one lotus-throne tier: a wide petal block with per-petal grooves and a
        # cabochon at the centre (the hero inlay; at 32px the petal mass tiles).
        bw = shaft_w
        petal = [(cx - bw, y - int(9 * s)),
                 (cx - int(bw * 0.6), y - int(13 * s)),
                 (cx + int(bw * 0.6), y - int(13 * s)),
                 (cx + bw, y - int(9 * s)),
                 (cx + int(bw * 0.78), y + int(9 * s)),
                 (cx - int(bw * 0.78), y + int(9 * s))]
        triad_blob(surf, BONE, petal,
                   core_pts=[(cx, y - int(12 * s)), (cx + bw, y - int(9 * s)),
                             (cx + int(bw * 0.78), y + int(8 * s)), (cx, y + int(6 * s))],
                   sheen_pts=[(cx - bw, y - int(9 * s)), (cx - int(bw * 0.6), y - int(12 * s)),
                              (cx - int(bw * 0.3), y - int(9 * s)), (cx - bw, y + int(2 * s))],
                   ow=max(1, int(1.4 * s)))
        for k in (-2, -1, 0, 1, 2):
            px = cx + int(k * bw * 0.38)
            pygame.draw.line(surf, BONE_DD, (px, y - int(12 * s)),
                             (px, y + int(7 * s)), max(1, int(1.2 * s)))
        cabochon(surf, (cx, y - int(3 * s)), max(1, int(3.4 * s)), s,
                 TURQ if (idx % 2 == 0) else CORAL,
                 TURQ_BR if (idx % 2 == 0) else CORAL_BR)
        # a coral tassel hung off alternating sides (hero beadwork)
        side = -1 if (idx % 2 == 0) else 1
        tassel(surf, cx + side * (bw + int(3 * s)), y + int(2 * s), int(10 * s), s)
        idx += 1
        y += tier_pitch

    # === gap-edge cap: gem-tipped lotus blossom in a small CLOSED flame-ring ===
    cap_y = (bot - int(22 * s)) if cap == "bottom" else (top + int(22 * s))
    # the small closed flame-ring (her prabhamandala in miniature)
    flame_halo(surf, cx, cap_y, int(18 * s), s, lobes=14, reach=0.9, full=True)
    grow = +1 if cap == "bottom" else -1
    # a lotus blossom opening toward the gap
    for k in range(7):
        a = (math.radians(-90 + (k - 3) * 24) if grow > 0
             else math.radians(90 + (k - 3) * 24))
        tip = (cx + math.cos(a) * int(15 * s), cap_y + math.sin(a) * int(15 * s))
        pygame.draw.line(surf, INK, (cx, cap_y), tip, max(2, int(4 * s)))
        pygame.draw.line(surf, BONE, (cx, cap_y), tip, max(1, int(2.4 * s)))
        triad_circle(surf, BONE, (int(tip[0]), int(tip[1])), max(1, int(2.4 * s)),
                     ow=max(1, int(1 * s)), core=False, sheen=False)
    # gold collar where the blossom meets the shaft
    collar_y = cap_y - grow * int(22 * s)
    pygame.draw.rect(surf, INK, (cx - int(10 * s), collar_y - int(3 * s), int(20 * s), int(7 * s)))
    pygame.draw.rect(surf, GOLD, (cx - int(9 * s), collar_y - int(2 * s), int(18 * s), int(5 * s)))
    pygame.draw.rect(surf, GOLD_BR, (cx - int(9 * s), collar_y - int(2 * s), int(18 * s), int(2 * s)))
    # the glowing turquoise cabochon at the blossom hub (the gap glow)
    cabochon(surf, (cx, cap_y), int(6 * s), s, TURQ, TURQ_BR, glow=True)


# ── compose the review sheet ─────────────────────────────────────────────────
SS = 8


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def render_hero(boxw, boxh, draw_cx, draw_cy, scale):
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_ratna_padmini(big, draw_cx * SS, draw_cy * SS, scale * SS)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


def export_hero():
    """Standalone hi-res hero PNG (~1024px tall) per the higher-res brief."""
    HW, HH = 820, 1024
    big = pygame.Surface((HW * 2, HH * 2), pygame.SRCALPHA)
    draw_ratna_padmini(big, HW, int(HH * 1.04), 5.6)
    hero = pygame.transform.smoothscale(big, (HW, HH))
    hero = grow_outline(hero, INK + (255,), 2)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1_hero.png")
    pygame.image.save(hero, out)
    print("wrote", out)
    return out


def main():
    W, H = 1040, 860
    font_big = pygame.font.SysFont("DejaVu Sans", 30, bold=True)
    font = pygame.font.SysFont("DejaVu Sans", 17, bold=True)
    font_sm = pygame.font.SysFont("DejaVu Sans", 12)

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("RATNA-PADMINI", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "jewel-lotus throne mother  ·  mukha_citipati_court #5 · MUKHA body · turquoise+gold+coral · "
        "FULL enclosing flame-halo (the only sister) · round 1",
        True, LABEL_DIM), (300, 26))

    # === (a) BIG HERO =========================================================
    hero = render_hero(380, 500, 188, 256, 1.95)
    sheet.blit(hero, (14, 92))
    sheet.blit(font.render("Creature — hero (SS=8)", True, LABEL), (110, 596))
    sheet.blit(font_sm.render("FULL enclosing gold-turquoise flame-halo · six-arm fan · 6 palms each cradle a tiny skull.", True, LABEL_DIM), (14, 620))
    sheet.blit(font_sm.render("Fused crown: Citipati 5-skull arc-SWEEP + Mukha gold tiara-BAND + turquoise brow-cabochons.", True, LABEL_DIM), (14, 636))
    sheet.blit(font_sm.render("Tiered gem-lotus throne · beadwork · coral tassels. Turquoise third-eye = brightest pixel.", True, LABEL_DIM), (14, 652))

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
    pygame.draw.rect(sheet, (60, 58, 70), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar — jewel-lotus throne", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("stacked lotus-throne tiers on a gold rod =", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("shaft; gem-lotus blossom + closed flame-ring", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("+ glowing turquoise cabochon caps the gap", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px chips (day+night), blackout proof, palette =============
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 588))
    sheet.blit(font.render("True 32px gameplay-scale", True, LABEL), (panel_x + 16, 96))

    def chip32():
        big = pygame.Surface((120 * SS, 120 * SS), pygame.SRCALPHA)
        draw_ratna_padmini(big, 60 * SS, 62 * SS, (32 / 150.0) * SS)
        small = pygame.transform.smoothscale(big, (120, 120))
        return grow_outline(small, INK + (255,), 1)

    chip = chip32()

    day_y = 128
    vgrad(sheet, (panel_x + 20, day_y, 150, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 15, day_y + 15))
    sheet.blit(font_sm.render("32px on day sky", True, LABEL), (panel_x + 20, day_y + 156))

    night_y = day_y + 184
    vgrad(sheet, (panel_x + 20, night_y, 150, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 150, 150), 1)
    sheet.blit(chip, (panel_x + 20 + 15, night_y + 15))
    sheet.blit(font_sm.render("32px on night sky", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    # blackout / silhouette proof — fill the chip's alpha solid to read the shape
    def blackout32():
        big = pygame.Surface((120 * SS, 120 * SS), pygame.SRCALPHA)
        draw_ratna_padmini(big, 60 * SS, 62 * SS, (32 / 150.0) * SS)
        small = pygame.transform.smoothscale(big, (120, 120))
        mask = pygame.mask.from_surface(small)
        sil = mask.to_surface(setcolor=(20, 18, 24, 255), unsetcolor=(0, 0, 0, 0))
        return sil

    bo = blackout32()
    px2 = panel_x + 192
    pygame.draw.rect(sheet, (214, 214, 220), (px2, day_y, 150, 150))
    pygame.draw.rect(sheet, INK, (px2, day_y, 150, 150), 1)
    sheet.blit(bo, (px2 + 15, day_y + 15))
    sheet.blit(font_sm.render("blackout proof", True, LABEL), (px2, day_y + 156))
    sheet.blit(font_sm.render("(halo RING carries", True, LABEL_DIM), (px2, day_y + 172))
    sheet.blit(font_sm.render(" the 32px silhouette)", True, LABEL_DIM), (px2, day_y + 186))

    # a 32px pillar chip on both skies
    def pillar_chip32():
        big = pygame.Surface((44 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 22 * SS, 2 * SS, 128 * SS, 0.32 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (44, 130))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    px3 = panel_x + 192
    vgrad(sheet, (px3, night_y, 56, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (px3, night_y, 56, 150), 1)
    sheet.blit(pc, (px3 + 6, night_y + 10))
    vgrad(sheet, (px3 + 64, night_y, 56, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (px3 + 64, night_y, 56, 150), 1)
    sheet.blit(pc, (px3 + 70, night_y + 10))
    sheet.blit(font_sm.render("pillar 32px (day / night)", True, LABEL_DIM), (px3, night_y + 156))

    # palette swatches
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, 524))
    swatches = [
        (BONE, "warm pale bone"), (GOLD, "lavish gold"),
        (TURQ, "turquoise focal"), (TURQ_HOT, "third-eye core"),
        (CORAL, "coral tassel"), (GOLD_D, "deep-gold inlay"),
        (THIRD_EYE, "third-eye"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, 552
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 168
        ry = syp + row * 26
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, ry, 18, 18))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 26, ry + 3))

    pygame.draw.rect(sheet, PANEL, (14, 808, W - 28, 44))
    sheet.blit(font_sm.render(
        "HIGH-RES pipeline: SS=8 supersample -> smoothscale; standalone round_1_hero.png ~1024px tall.  "
        "STAY: flat fills · ink keyline (28,22,26) · dark-core->fill->top-left sheen triad · 1px grown outline · "
        "chibi scary-cute · procedural-only.",
        True, LABEL_DIM), (26, 821))
    sheet.blit(font_sm.render(
        "Two-scale rule: the FULL flame-halo RING carries the 32px silhouette; inlay + tassels + per-petal gems are HERO-ONLY.",
        True, LABEL_DIM), (26, 837))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out)
    return out


if __name__ == "__main__":
    export_hero()
    main()
