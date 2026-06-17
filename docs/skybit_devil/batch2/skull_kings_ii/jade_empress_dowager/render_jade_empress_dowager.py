"""
Round-1 concept renderer for JADE EMPRESS DOWAGER — KING SKULL II, concept #1
(MANDATORY-CRADLE, 6 arms). Headless Pygame; ELEVATED pipeline (SS=6 ->
smoothscale) so the carved-jade facets + gold filigree survive the downscale.
Clones the house grammar from regent_koschei: flat triad shading
(dark-core -> fill -> top-left sheen) via triad_blob / triad_circle, the
bone_limb skeleton joint helper, grow_outline ink ring, and the full review
SHEET LAYOUT (hero / mirrored pillar / 32px day+night chips / silhouette proof
/ palette strip). Procedural-only (no PNGs, no game.* imports).

WHY this king is NOT Koschei: the locked brief forbids a throne frame and a
radiating back-fan (those are Koschei's reads). So the dominant mass here is a
SOLID carved-jade BELL-trapezoid sunk to the ground — a kneeling matriarch
carved from one block of spinach jade. No stiles, no dais, no rib-spire fan.

WHY the crown is a single VERTICAL plume (not a fan / not a radial burst): a
fan-spread crown would collide with Sunfire's sunburst. Instead one tall carved
jade phoenix-PLUME blade rises from the head to a single jade SKULL finial at
the apex — the brood's above-head skull-crown, kept as a lone vertical spire.

WHY the cradled skull owns the brightest pixel: the hard gate is that the pale
mutton-jade CRADLE-SKULL stays the single brightest + focal point. The body is
mid-value spinach jade; the gold filigree is kept thin and DELIBERATELY darker
than the pale skull so the gilt never out-shines the focal. Only the lap skull
gets the pale-jade glow + halo.

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
pygame.display.set_mode((1, 1))

# -- PINNED PALETTE (locked re-spec brief) -------------------------------------
# spinach-jade carved-stone body = the ONE dominant mass.
JADE      = (110, 168, 128)   # spinach-jade carved body (dominant fill)
JADE_D    = ( 70, 116,  88)   # jade shade / dark-core
JADE_DD   = ( 46,  82,  64)   # deepest carved hollow (recesses, eye-pits)
JADE_SH   = (214, 228, 206)   # mutton-fat jade top-left rim-sheen
# the SINGLE pale focal — the cupped cradle-skull (pale mutton-jade glow).
SKULL     = (196, 236, 214)   # pale-jade cradled skull (the focal)
SKULL_BR  = (224, 248, 232)   # brighter skull body
SKULL_HOT = (244, 255, 248)   # hottest skull core (must stay the brightest pixel)
SKULL_D   = (150, 200, 178)   # skull shade
SKULL_RIM = (110, 160, 140)   # skull socket / rim
# thin GOLD filigree — a worked-metal LINE accent ONLY (kept dull, below skull).
# WHY kept dark + thin: a bright/filled gold becomes a 2nd warm mass that steals
# the focal from the pale skull. Gold reads as carved trim at hero scale and
# dissolves at 32px.
GOLD      = (214, 176,  96)   # thin gold filigree base
GOLD_HI   = (236, 208, 140)   # tight specular pip (deliberately < skull core)
GOLD_D    = (150, 116,  52)   # recessed gold shadow
INK       = ( 28,  22,  30)   # house ink keyline

BG        = ( 96, 100, 108)
PANEL     = ( 74,  78,  88)
DAY_SKY_T = (120, 196, 236)
DAY_SKY_B = (196, 232, 244)
NIGHT_T   = ( 22,  26,  54)
NIGHT_B   = ( 48,  44,  82)
LABEL     = (238, 240, 244)
LABEL_DIM = (188, 196, 208)


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


def bone_limb(surf, p0, p1, p2, thick, s, joint=True, color=JADE):
    """Carved-jade arm rendered as the house two-segment limb. Re-skinned to
    jade so the six arms read as the matriarch's own carved stone, not bone."""
    for (a, b) in ((p0, p1), (p1, p2)):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = max(1.0, math.hypot(dx, dy))
        nx, ny = -dy / L * thick / 2, dx / L * thick / 2
        quad = [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny),
                (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]
        triad_blob(surf, color, quad,
                   sheen_pts=[(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny),
                              (b[0] + nx * 0.3, b[1] + ny * 0.3),
                              (a[0] + nx * 0.3, a[1] + ny * 0.3)],
                   ow=max(1, int(thick * 0.18)))
    if joint:
        triad_circle(surf, color, p1, int(thick * 0.62), ow=max(1, int(1.2 * s)),
                     core=False)


# -- thin GOLD filigree primitives (worked-metal LINE accents) ----------------
def filigree_band(surf, x0, x1, y, s):
    """A 1-2px gold edge-line + darker shadow-line tracing the bell hem/waist.
    WHY line-work not fill: at 32px a filled gold band consolidates into a 2nd
    warm mass that competes with the pale skull. A top gold line + a darker
    bottom shadow reads as carved gilt trim ON the jade yet dissolves to nothing
    at 32px so gold never becomes a second read."""
    lw = max(1, int(1.3 * s))
    pygame.draw.line(surf, GOLD, (x0, y), (x1, y), lw)
    pygame.draw.line(surf, GOLD_D, (x0, y + lw), (x1, y + lw), max(1, int(1.0 * s)))
    pygame.draw.line(surf, GOLD_HI, (x0 + (x1 - x0) * 0.10, y),
                     ((x0 + x1) / 2, y), max(1, int(0.8 * s)))


def filigree_swirl(surf, cx, cy, r, s):
    """A tiny gold scroll-curl (the dowager's filigree). Kept as thin arcs so
    the gilt area stays minuscule."""
    rect = (cx - r, cy - r, r * 2, r * 2)
    pygame.draw.arc(surf, GOLD, rect, math.radians(20), math.radians(300),
                    max(1, int(1.3 * s)))
    pygame.draw.circle(surf, GOLD_HI, (cx - int(r * 0.2), cy - int(r * 0.2)),
                       max(1, int(0.9 * s)))


# -- the CRADLE-SKULL : the single brightest focal ----------------------------
def cradle_skull(surf, cx, cy, r, s):
    """The pale mutton-jade skull cupped in the lap — the focal. Carries its own
    soft glow halo so it owns the brightest pixel; no other element is haloed."""
    for (rr, a) in ((r * 1.95, 26), (r * 1.5, 46), (r * 1.18, 84)):
        halo = pygame.Surface((int(rr * 2) + 4, int(rr * 2) + 4), pygame.SRCALPHA)
        pygame.draw.circle(halo, SKULL_BR + (a,), (int(rr) + 2, int(rr) + 2), int(rr))
        surf.blit(halo, (cx - int(rr) - 2, cy - int(rr) - 2))
    # cranium dome
    triad_circle(surf, SKULL, (cx, cy), r, ow=max(1, int(1.4 * s)), core=False)
    # cheek/jaw taper below the dome
    jaw = [(cx - int(r * 0.62), cy + int(r * 0.28)),
           (cx + int(r * 0.62), cy + int(r * 0.28)),
           (cx + int(r * 0.34), cy + int(r * 0.92)),
           (cx - int(r * 0.34), cy + int(r * 0.92))]
    triad_blob(surf, SKULL, jaw,
               sheen_pts=[(cx - int(r * 0.62), cy + int(r * 0.28)),
                          (cx - int(r * 0.1), cy + int(r * 0.28)),
                          (cx - int(r * 0.18), cy + int(r * 0.9)),
                          (cx - int(r * 0.34), cy + int(r * 0.9))],
               ow=max(1, int(1.2 * s)))
    # two ink eye-sockets so a pale dot resolves to a skull when zoomed
    for sgn in (-1, 1):
        ex = cx + sgn * int(r * 0.42)
        ey = cy + int(r * 0.04)
        pygame.draw.circle(surf, SKULL_RIM, (ex, ey), int(r * 0.34))
        pygame.draw.circle(surf, INK, (ex, ey), int(r * 0.27))
    # nasal pit + a couple of teeth ticks
    pygame.draw.polygon(surf, INK,
                        [(cx - int(r * 0.1), cy + int(r * 0.34)),
                         (cx + int(r * 0.1), cy + int(r * 0.34)),
                         (cx, cy + int(r * 0.56))])
    my = cy + int(r * 0.72)
    pygame.draw.line(surf, INK, (cx - int(r * 0.34), my), (cx + int(r * 0.34), my),
                     max(1, int(1.4 * s)))
    for k in (-1, 0, 1):
        pygame.draw.line(surf, INK, (cx + int(k * r * 0.2), my - int(r * 0.05)),
                         (cx + int(k * r * 0.2), my + int(r * 0.1)),
                         max(1, int(1 * s)))
    # the hottest core — the single brightest pixel of the whole hero
    pygame.draw.circle(surf, SKULL_HOT, (cx - int(r * 0.2), cy - int(r * 0.24)),
                       max(1, int(r * 0.28)))


# -- the vertical jade phoenix-PLUME crown + skull finial ---------------------
def plume_crown(surf, cx, base_y, h, w, s):
    """ONE tall carved-jade blade rising to a single jade SKULL finial at the
    apex. WHY a lone vertical spire (no fan): a fan-spread or radial burst would
    collide with Sunfire's sunburst crown. A single blade + apex skull is the
    brood's above-head skull-crown kept as a distinct vertical tell that survives
    32px as a green spike topped by a pale point."""
    tipy = base_y - h
    # the carved blade — a tall leaf with a gentle S-curve, widest at mid
    blade = [(cx - w * 0.18, base_y),
             (cx + w * 0.18, base_y),
             (cx + w * 0.50, base_y - h * 0.40),
             (cx + w * 0.16, base_y - h * 0.74),
             (cx, tipy + h * 0.10),
             (cx - w * 0.16, base_y - h * 0.74),
             (cx - w * 0.50, base_y - h * 0.40)]
    triad_blob(surf, JADE, blade,
               core_pts=[(cx, base_y),
                         (cx + w * 0.34, base_y - h * 0.40),
                         (cx + w * 0.10, base_y - h * 0.72),
                         (cx, tipy + h * 0.12)],
               sheen_pts=[(cx - w * 0.16, base_y),
                          (cx - w * 0.50, base_y - h * 0.40),
                          (cx - w * 0.10, base_y - h * 0.70),
                          (cx - w * 0.02, base_y - h * 0.20)],
               ow=max(1, int(1.4 * s)))
    # a central carved spine rib up the blade
    pygame.draw.line(surf, JADE_DD, (cx, base_y - int(2 * s)),
                     (cx, tipy + int(h * 0.12)), max(1, int(1.6 * s)))
    # thin gold filigree veins fanning off the spine (the dowager's gilt)
    for fr in (0.30, 0.52, 0.70):
        for sgn in (-1, 1):
            yy = base_y - h * fr
            pygame.draw.line(surf, GOLD, (cx, yy),
                             (cx + sgn * w * (0.34 - fr * 0.12), yy - h * 0.06),
                             max(1, int(1.0 * s)))
    # the apex jade SKULL finial — the above-head skull-crown
    fr_r = max(3, int(w * 0.30))
    fy = tipy + fr_r
    triad_circle(surf, JADE, (cx, fy), fr_r, ow=max(1, int(1.2 * s)), core=False)
    # jaw nub
    pygame.draw.polygon(surf, JADE,
                        [(cx - int(fr_r * 0.5), fy + int(fr_r * 0.5)),
                         (cx + int(fr_r * 0.5), fy + int(fr_r * 0.5)),
                         (cx, fy + int(fr_r * 1.02))])
    pygame.draw.polygon(surf, INK,
                        [(cx - int(fr_r * 0.5), fy + int(fr_r * 0.5)),
                         (cx + int(fr_r * 0.5), fy + int(fr_r * 0.5)),
                         (cx, fy + int(fr_r * 1.02))], max(1, int(1 * s)))
    for sgn in (-1, 1):
        pygame.draw.circle(surf, INK, (cx + sgn * int(fr_r * 0.4), fy),
                           max(1, int(fr_r * 0.26)))
    # a thin gold bezel collar where the finial meets the blade tip
    pygame.draw.circle(surf, GOLD, (cx, fy + int(fr_r * 0.6)), max(1, int(fr_r * 0.9)),
                       max(1, int(1.0 * s)))


# -- the kneeling carved-jade BELL matriarch ----------------------------------
def draw_empress(surf, cx, cy, s):
    """Dominant mass = a solid carved-jade BELL-trapezoid kneeling to the ground.
    Six arms: lower FOUR cup the lap cradle-skull, upper TWO splay a jade fan +
    a ribbon-scroll. No throne, no back-fan."""
    head_c = (cx, cy - int(40 * s))
    hr = int(20 * s)
    ground_y = cy + int(58 * s)

    # === THE BELL BODY (the one dominant mass) ===============================
    # a broad trapezoid that flares to a wide rounded hem sunk to the ground.
    bell_top_w = int(26 * s)
    bell_bot_w = int(58 * s)
    bell_top_y = cy - int(14 * s)
    bell = [(cx - bell_top_w, bell_top_y),
            (cx + bell_top_w, bell_top_y),
            (cx + int(bell_bot_w * 0.78), cy + int(24 * s)),
            (cx + bell_bot_w, ground_y - int(6 * s)),
            (cx + int(bell_bot_w * 0.86), ground_y),
            (cx - int(bell_bot_w * 0.86), ground_y),
            (cx - bell_bot_w, ground_y - int(6 * s)),
            (cx - int(bell_bot_w * 0.78), cy + int(24 * s))]
    triad_blob(surf, JADE, bell,
               core_pts=[(cx - int(4 * s), bell_top_y + int(4 * s)),
                         (cx + int(bell_bot_w * 0.74), cy + int(24 * s)),
                         (cx + int(bell_bot_w * 0.80), ground_y - int(4 * s)),
                         (cx - int(4 * s), ground_y - int(4 * s))],
               sheen_pts=[(cx - bell_top_w, bell_top_y),
                          (cx - int(4 * s), bell_top_y),
                          (cx - int(bell_bot_w * 0.5), cy + int(28 * s)),
                          (cx - bell_bot_w, ground_y - int(6 * s))],
               ow=max(1, int(1.8 * s)))
    # carved vertical fold-lines down the bell (jade carving, not gilt)
    for f in (-0.62, -0.32, 0.0, 0.32, 0.62):
        x_top = cx + f * bell_top_w * 1.4
        x_bot = cx + f * bell_bot_w * 0.92
        pygame.draw.line(surf, JADE_DD, (x_top, bell_top_y + int(8 * s)),
                         (x_bot, ground_y - int(4 * s)), max(1, int(1.6 * s)))
    # thin gold filigree hem band + a waist band (the gilt trim)
    filigree_band(surf, cx - int(bell_bot_w * 0.82), cx + int(bell_bot_w * 0.82),
                  ground_y - int(8 * s), s)
    filigree_band(surf, cx - int(bell_bot_w * 0.46), cx + int(bell_bot_w * 0.46),
                  cy + int(20 * s), s)
    for sgn in (-1, 1):
        filigree_swirl(surf, cx + sgn * int(bell_bot_w * 0.52),
                       cy + int(36 * s), max(2, int(5 * s)), s)

    # === UPPER TWO ARMS — jade FAN (left) + ribbon-SCROLL (right) ============
    # drawn BEHIND the lap cradle so the cradle reads foreground.
    sh_l = (cx - int(20 * s), cy - int(20 * s))
    sh_r = (cx + int(20 * s), cy - int(20 * s))
    # left upper arm raising a folded jade fan
    el_l = (cx - int(34 * s), cy - int(14 * s))
    hand_l = (cx - int(42 * s), cy - int(30 * s))
    bone_limb(surf, sh_l, el_l, hand_l, int(6 * s), s, color=JADE)
    fan_pts = [hand_l]
    for k in range(5):
        a = math.radians(118 + k * 17)
        fan_pts.append((hand_l[0] + math.cos(a) * int(26 * s),
                        hand_l[1] - math.sin(a) * int(26 * s)))
    triad_blob(surf, JADE, fan_pts, ow=max(1, int(1.2 * s)))
    for k in range(5):
        a = math.radians(118 + k * 17)
        pygame.draw.line(surf, JADE_DD, hand_l,
                         (hand_l[0] + math.cos(a) * int(26 * s),
                          hand_l[1] - math.sin(a) * int(26 * s)), max(1, int(1.2 * s)))
    # gold rib on the fan's leading edge
    pygame.draw.line(surf, GOLD, hand_l,
                     (hand_l[0] + math.cos(math.radians(118)) * int(26 * s),
                      hand_l[1] - math.sin(math.radians(118)) * int(26 * s)),
                     max(1, int(1.0 * s)))
    # right upper arm holding a curling ribbon-scroll
    el_r = (cx + int(34 * s), cy - int(14 * s))
    hand_r = (cx + int(42 * s), cy - int(28 * s))
    bone_limb(surf, sh_r, el_r, hand_r, int(6 * s), s, color=JADE)
    ribbon = [hand_r,
              (hand_r[0] + int(10 * s), hand_r[1] - int(18 * s)),
              (hand_r[0] - int(4 * s), hand_r[1] - int(30 * s)),
              (hand_r[0] + int(12 * s), hand_r[1] - int(40 * s)),
              (hand_r[0] + int(2 * s), hand_r[1] - int(30 * s)),
              (hand_r[0] + int(16 * s), hand_r[1] - int(18 * s)),
              (hand_r[0] + int(6 * s), hand_r[1] - int(2 * s))]
    triad_blob(surf, JADE, ribbon, ow=max(1, int(1.1 * s)))
    pygame.draw.line(surf, GOLD,
                     (hand_r[0] + int(4 * s), hand_r[1] - int(6 * s)),
                     (hand_r[0] + int(8 * s), hand_r[1] - int(36 * s)),
                     max(1, int(1.0 * s)))

    # === LAP CRADLE-SKULL position ===========================================
    skull_c = (cx, cy + int(18 * s))
    skull_r = int(15 * s)

    # === LOWER FOUR ARMS — cupping the cradle ================================
    # two inner + two outer pairs of jade arms whose four hands cup the skull.
    arm_th = int(6 * s)
    # outer pair: wider shoulders, hands meeting under the skull
    for sgn in (-1, 1):
        sho = (cx + sgn * int(22 * s), cy - int(10 * s))
        elb = (cx + sgn * int(30 * s), cy + int(14 * s))
        hnd = (skull_c[0] + sgn * int(15 * s), skull_c[1] + int(12 * s))
        bone_limb(surf, sho, elb, hnd, arm_th, s, color=JADE)
    # inner pair: closer shoulders, hands cupping the skull's underside
    for sgn in (-1, 1):
        sho = (cx + sgn * int(12 * s), cy - int(6 * s))
        elb = (cx + sgn * int(20 * s), cy + int(16 * s))
        hnd = (skull_c[0] + sgn * int(8 * s), skull_c[1] + int(15 * s))
        bone_limb(surf, sho, elb, hnd, arm_th, s, color=JADE)

    # === SKULL HEAD (the empress's own face above the bell) ==================
    triad_circle(surf, JADE, head_c, hr, ow=max(2, int(2 * s)))
    for sgn in (-1, 1):
        pygame.draw.circle(surf, JADE_D,
                           (head_c[0] + sgn * int(hr * 0.66), head_c[1] + int(hr * 0.30)),
                           int(hr * 0.26))
    for sgn in (-1, 1):
        ex = head_c[0] + sgn * int(hr * 0.44)
        ey = head_c[1] + int(hr * 0.04)
        pygame.draw.circle(surf, JADE_DD, (ex, ey), int(hr * 0.34))
        pygame.draw.circle(surf, INK, (ex, ey), int(hr * 0.28))
        # a tiny pale glint so the face stays scary-CUTE not dead
        pygame.draw.circle(surf, SKULL, (ex - int(1 * s), ey - int(2 * s)),
                           max(1, int(hr * 0.08)))
    # gentle carved brow
    for sgn in (-1, 1):
        brow = [(head_c[0] + sgn * int(hr * 0.72), head_c[1] - int(hr * 0.30)),
                (head_c[0] + sgn * int(hr * 0.12), head_c[1] - int(hr * 0.06)),
                (head_c[0] + sgn * int(hr * 0.14), head_c[1] + int(hr * 0.02)),
                (head_c[0] + sgn * int(hr * 0.76), head_c[1] - int(hr * 0.20))]
        pygame.draw.polygon(surf, JADE_DD, brow)
    # nasal + a small serene smile of teeth
    pygame.draw.polygon(surf, JADE_DD,
                        [(head_c[0] - int(hr * 0.12), head_c[1] + int(hr * 0.30)),
                         (head_c[0] + int(hr * 0.12), head_c[1] + int(hr * 0.30)),
                         (head_c[0], head_c[1] + int(hr * 0.54))])
    my = head_c[1] + int(hr * 0.72)
    pygame.draw.line(surf, INK, (head_c[0] - int(hr * 0.40), my - int(hr * 0.02)),
                     (head_c[0] + int(hr * 0.40), my + int(hr * 0.04)),
                     max(1, int(2 * s)))
    for k in range(-2, 3):
        pygame.draw.line(surf, INK,
                         (head_c[0] + int(k * hr * 0.17), my - int(hr * 0.05)),
                         (head_c[0] + int(k * hr * 0.17), my + int(hr * 0.09)),
                         max(1, int(1 * s)))
    # a thin gold filigree diadem across the brow (royal, kept dull)
    pygame.draw.line(surf, GOLD,
                     (head_c[0] - int(hr * 0.8), head_c[1] - int(hr * 0.5)),
                     (head_c[0] + int(hr * 0.8), head_c[1] - int(hr * 0.5)),
                     max(1, int(1.3 * s)))

    # === CRADLE-SKULL drawn LAST so it owns the foreground + brightest pixel ==
    cradle_skull(surf, skull_c[0], skull_c[1], skull_r, s)
    # four small jade fingertips curling over the skull's lower edge (so the
    # FOUR cupped hands read as holding it, even at 32px)
    for sgn in (-1, 1):
        for off in (8, 15):
            fx = skull_c[0] + sgn * int(off * s)
            fy = skull_c[1] + int(13 * s)
            tip = [(fx - sgn * int(3 * s), fy - int(2 * s)),
                   (fx + sgn * int(3 * s), fy - int(1 * s)),
                   (fx + sgn * int(2 * s), fy + int(7 * s)),
                   (fx - sgn * int(2 * s), fy + int(6 * s))]
            triad_blob(surf, JADE, tip, ow=max(1, int(1.1 * s)))

    # === VERTICAL PLUME CROWN above the head =================================
    plume_crown(surf, head_c[0], head_c[1] - int(hr * 0.92),
                int(hr * 2.6), int(hr * 1.0), s)


# -- the jade-bell -> pillar mirror -------------------------------------------
def draw_pillar(surf, cx, top, bot, s, cap="bottom"):
    """Mirrored pillar built from the empress's OWN forms: stacked carved-jade
    bell drums cinched by gold filigree bands, capped by a plume + skull finial
    + a lap cradle-skull at the gap end."""
    shaft_w = int(18 * s)
    pygame.draw.rect(surf, INK, (cx - int(4 * s), top, int(8 * s), bot - top))

    pitch = int(30 * s)
    cap_room = int(46 * s)
    if cap == "bottom":
        b0, b1 = top + int(8 * s), bot - cap_room
    else:
        b0, b1 = top + cap_room, bot - int(8 * s)
    y = b0
    while y <= b1:
        # a carved-jade bell drum segment (the empress's bell repeated)
        drum = [(cx - int(8 * s), y - int(12 * s)),
                (cx + int(8 * s), y - int(12 * s)),
                (cx + int(12 * s), y + int(4 * s)),
                (cx + int(11 * s), y + int(13 * s)),
                (cx - int(11 * s), y + int(13 * s)),
                (cx - int(12 * s), y + int(4 * s))]
        triad_blob(surf, JADE, drum,
                   sheen_pts=[(cx - int(8 * s), y - int(12 * s)),
                              (cx - int(1 * s), y - int(12 * s)),
                              (cx - int(2 * s), y + int(12 * s)),
                              (cx - int(11 * s), y + int(12 * s))],
                   ow=max(1, int(1.3 * s)))
        # carved fold ribs
        for f in (-0.5, 0.0, 0.5):
            pygame.draw.line(surf, JADE_DD, (cx + f * int(8 * s), y - int(10 * s)),
                             (cx + f * int(11 * s), y + int(12 * s)),
                             max(1, int(1.3 * s)))
        # gold filigree cinch band between drums
        filigree_band(surf, cx - shaft_w * 0.7, cx + shaft_w * 0.7,
                      y + int(13 * s), s)
        y += pitch

    cap_y = (bot - int(30 * s)) if cap == "bottom" else (top + int(30 * s))
    fan_dir = -1 if cap == "bottom" else 1
    # cap drum (rounded bell head)
    triad_circle(surf, JADE, (cx, cap_y), int(15 * s), ow=max(1, int(1.4 * s)),
                 core=False)
    filigree_band(surf, cx - int(13 * s), cx + int(13 * s),
                  cap_y + fan_dir * int(12 * s), s)
    # a small cradle-skull set at the cap (the gap-facing focal of the pillar)
    sk_y = cap_y + fan_dir * int(2 * s)
    cradle_skull(surf, cx, sk_y, int(9 * s), s)
    # a short vertical plume rising AWAY from the gap (toward the wall)
    plume_crown(surf, cx, cap_y - fan_dir * int(15 * s),
                fan_dir * int(34 * s) * -1 if fan_dir > 0 else int(34 * s),
                int(11 * s), s)


# -- compose the review sheet -------------------------------------------------
SS = 6


def render_creature_chip(boxw, boxh, draw_cx, draw_cy, scale):
    big = pygame.Surface((boxw * SS, boxh * SS), pygame.SRCALPHA)
    draw_empress(big, draw_cx * SS, draw_cy * SS, scale * SS)
    small = pygame.transform.smoothscale(big, (boxw, boxh))
    return grow_outline(small, INK + (255,), 1)


def vgrad(surf, rect, top_col, bot_col):
    x, y, w, h = rect
    for j in range(h):
        pygame.draw.line(surf, lerp(top_col, bot_col, j / max(1, h - 1)),
                         (x, y + j), (x + w, y + j))


def load_fonts():
    """FONT is five levels up from this script; SysFont fallback if missing."""
    base = os.path.dirname(os.path.abspath(__file__))
    fp = os.path.join(base, "..", "..", "..", "..", "..",
                      "game", "assets", "LiberationSans-Bold.ttf")
    try:
        return (pygame.font.Font(fp, 30), pygame.font.Font(fp, 17),
                pygame.font.Font(fp, 12))
    except Exception:
        return (pygame.font.SysFont("DejaVu Sans", 30, bold=True),
                pygame.font.SysFont("DejaVu Sans", 17, bold=True),
                pygame.font.SysFont("DejaVu Sans", 12))


def main():
    W, H = 1180, 820
    font_big, font, font_sm = load_fonts()

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    pygame.draw.rect(sheet, PANEL, (0, 0, W, 56))
    sheet.blit(font_big.render("JADE EMPRESS DOWAGER", True, LABEL), (24, 13))
    sheet.blit(font_sm.render(
        "KING SKULL II #1  ·  kneeling carved-jade BELL · vertical phoenix-PLUME + jade skull finial · "
        "6 arms (4 cup the cradle, 2 splay fan+scroll) · pale-jade cradle-skull focal · round 1",
        True, LABEL_DIM), (360, 26))

    # === (a) BIG HERO =========================================================
    hero = render_creature_chip(360, 480, 178, 226, 1.70)
    sheet.blit(hero, (14, 86))
    sheet.blit(font.render("Creature — hero", True, LABEL), (110, 566))
    sheet.blit(font_sm.render("Solid carved-jade BELL kneeling to the ground (NO throne / NO back-fan).", True, LABEL_DIM), (14, 590))
    sheet.blit(font_sm.render("Six arms: lower FOUR cup the lap cradle-skull, upper TWO splay a jade fan", True, LABEL_DIM), (14, 606))
    sheet.blit(font_sm.render("+ ribbon-scroll. Crown = ONE vertical jade plume to a jade skull finial.", True, LABEL_DIM), (14, 622))

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
    pygame.draw.rect(sheet, (60, 64, 72), (pcx + 8, 86 + 250, 134, 96))
    sheet.blit(font_sm.render("GAP", True, LABEL_DIM), (pcx + 56, 86 + 250 + 40))
    sheet.blit(font.render("Pillar — jade bell-drums", True, LABEL), (pcx - 4, 690))
    sheet.blit(font_sm.render("stacked carved-jade bell drums, gold filigree", True, LABEL_DIM), (pcx - 4, 714))
    sheet.blit(font_sm.render("cinch bands; plume + cradle-skull cap", True, LABEL_DIM), (pcx - 4, 730))
    sheet.blit(font_sm.render("(mirrored top<->bottom, on-axis, bottom-rooted)", True, LABEL_DIM), (pcx - 4, 746))

    # === (c) TRUE 32px chips on day + night sky + SILHOUETTE proof =============
    panel_x = 660
    pygame.draw.rect(sheet, PANEL, (panel_x, 86, W - panel_x - 14, 560))
    sheet.blit(font.render("True 32px gameplay-scale chip", True, LABEL), (panel_x + 16, 96))

    def chip32(night=False):
        big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
        draw_empress(big, 48 * SS, 54 * SS, (32 / 140.0) * SS)
        small = pygame.transform.smoothscale(big, (96, 96))
        # WHY a widened pale-jade rim on the night chip: the mid-value jade mass
        # can sink into a dark night sky; a soft skull-coloured halo carries the
        # silhouette while the pale cradle-skull stays the brightest point.
        if night:
            base = grow_outline(small, SKULL_RIM + (255,), 2)
            return grow_outline(base, INK + (200,), 1)
        return grow_outline(small, INK + (255,), 1)

    day_chip = chip32(night=False)
    night_chip = chip32(night=True)

    day_y = 128
    vgrad(sheet, (panel_x + 20, day_y, 150, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, day_y, 150, 150), 1)
    sheet.blit(day_chip, (panel_x + 20 + 27, day_y + 27))
    sheet.blit(font_sm.render("32px on day sky", True, LABEL), (panel_x + 20, day_y + 156))

    night_y = day_y + 184
    vgrad(sheet, (panel_x + 20, night_y, 150, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (panel_x + 20, night_y, 150, 150), 1)
    sheet.blit(night_chip, (panel_x + 20 + 27 - 1, night_y + 27 - 1))
    sheet.blit(font_sm.render("32px on night sky (jade rim)", True, LABEL_DIM), (panel_x + 20, night_y + 156))

    # silhouette proof — blacked-out hero so the kneeling-bell read is checked
    def silhouette():
        big = pygame.Surface((150 * SS, 200 * SS), pygame.SRCALPHA)
        draw_empress(big, 75 * SS, 92 * SS, 1.22 * SS)
        small = pygame.transform.smoothscale(big, (150, 200))
        mask = pygame.mask.from_surface(small)
        sil = pygame.Surface((150, 200), pygame.SRCALPHA)
        solid = mask.to_surface(setcolor=(18, 18, 20, 255), unsetcolor=(0, 0, 0, 0))
        sil.blit(solid, (0, 0))
        return sil

    sil_x = panel_x + 196
    pygame.draw.rect(sheet, (210, 212, 216), (sil_x, day_y, 150, 200))
    pygame.draw.rect(sheet, INK, (sil_x, day_y, 150, 200), 1)
    sheet.blit(silhouette(), (sil_x, day_y))
    sheet.blit(font_sm.render("silhouette proof", True, LABEL_DIM), (sil_x, day_y + 204))
    sheet.blit(font_sm.render("(low kneeling bell + vertical plume)", True, LABEL_DIM), (sil_x, day_y + 220))

    def pillar_chip32():
        big = pygame.Surface((40 * SS, 130 * SS), pygame.SRCALPHA)
        draw_pillar(big, 20 * SS, 2 * SS, 128 * SS, 0.34 * SS, cap="bottom")
        small = pygame.transform.smoothscale(big, (40, 130))
        return grow_outline(small, INK + (255,), 1)

    pc = pillar_chip32()
    px2 = sil_x + 168
    vgrad(sheet, (px2, day_y, 56, 150), DAY_SKY_T, DAY_SKY_B)
    pygame.draw.rect(sheet, INK, (px2, day_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 8, day_y + 10))
    vgrad(sheet, (px2, night_y, 56, 150), NIGHT_T, NIGHT_B)
    pygame.draw.rect(sheet, INK, (px2, night_y, 56, 150), 1)
    sheet.blit(pc, (px2 + 8, night_y + 10))
    sheet.blit(font_sm.render("pillar", True, LABEL_DIM), (px2 + 4, day_y - 16))
    sheet.blit(font_sm.render("gap-cap", True, LABEL_DIM), (px2 - 2, night_y - 16))

    # palette swatches
    sheet.blit(font.render("Pinned palette", True, LABEL), (panel_x + 16, 510))
    swatches = [
        (JADE, "spinach-jade body"), (JADE_D, "jade shade"),
        (SKULL, "pale cradle-skull"), (SKULL_HOT, "skull hot core"),
        (JADE_SH, "mutton-fat sheen"), (GOLD, "gold filigree"),
        (GOLD_HI, "filigree highlight"), (JADE_DD, "carved hollow"),
        (SKULL_RIM, "skull socket"), (INK, "ink keyline"),
    ]
    sxp, syp = panel_x + 16, 538
    for i, (c, name) in enumerate(swatches):
        col, row = i % 2, i // 2
        rx = sxp + col * 188
        ry = syp + row * 24
        pygame.draw.rect(sheet, INK, (rx - 1, ry - 1, 20, 20))
        pygame.draw.rect(sheet, c, (rx, ry, 18, 18))
        sheet.blit(font_sm.render(name, True, LABEL), (rx + 26, ry + 3))

    pygame.draw.rect(sheet, PANEL, (14, 770, W - 28, 40))
    sheet.blit(font_sm.render(
        "KNEELING carved-jade BELL (no throne / no back-fan — de-collides from Koschei).  Crown = ONE vertical plume + jade skull finial (de-collides from Sunfire's burst).  "
        "GOLD filigree kept THIN + dull so the pale cradle-skull stays the single brightest focal.  SS=6 supersample -> smoothscale · procedural-only.",
        True, LABEL_DIM), (26, 783))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out)

    self_check()


def self_check():
    """Render the hero alone and verify (1) the brightest pixel sits inside the
    pale cradle-skull (the focal owns the peak), and (2) gold reads as a thin
    accent — strongly-gold pixels stay a small fraction of jade body."""
    surf = pygame.Surface((400, 540), pygame.SRCALPHA)
    draw_empress(surf, 200, 250, 2.0)
    px = pygame.surfarray.pixels3d(surf)
    a = pygame.surfarray.pixels_alpha(surf)
    w, h = surf.get_size()
    best_lum, best_xy = -1, (0, 0)
    gold_n, jade_n = 0, 0
    for x in range(0, w, 2):
        for yy in range(0, h, 2):
            if a[x, yy] < 40:
                continue
            r, g, b = int(px[x, yy][0]), int(px[x, yy][1]), int(px[x, yy][2])
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            if lum > best_lum:
                best_lum, best_xy = lum, (x, yy)
            # crude gold detector: warm, mid-bright, blue clearly lowest
            if r > 150 and 110 < g < 215 and b < 150 and r >= g and (g - b) > 30 and (r - b) > 70:
                gold_n += 1
            # crude jade-body detector: green-dominant mid value
            if 60 < r < 200 and g > 110 and g >= r and abs(g - b) < 90 and b < g:
                jade_n += 1
    bx, by = best_xy
    r, g, b = int(px[bx, by][0]), int(px[bx, by][1]), int(px[bx, by][2])
    # skull-core hue: very bright + near-white-green (high all channels)
    is_skull = (r > 210 and g > 230 and b > 210)
    del px, a
    print("self-check: brightest pixel @", best_xy, "rgb", (r, g, b),
          "lum %.0f" % best_lum, "-> skull-core?", is_skull)
    print("self-check: gold px ~%d  vs jade px ~%d  -> gold fraction %.2f"
          % (gold_n, jade_n, gold_n / max(1, gold_n + jade_n)))
    tells_check()


def tells_check():
    """At true 32px confirm the focal + crown survive: a pale skull point exists
    in the lower lap band AND a green plume rises above the head band."""
    big = pygame.Surface((96 * SS, 96 * SS), pygame.SRCALPHA)
    draw_empress(big, 48 * SS, 54 * SS, (32 / 140.0) * SS)
    small = pygame.transform.smoothscale(big, (96, 96))
    px = pygame.surfarray.pixels3d(small)
    al = pygame.surfarray.pixels_alpha(small)
    w, h = small.get_size()
    pale_n, pale_lum = 0, 0.0
    plume_n = 0
    upper = int(h * 0.40)   # crown plume band (top — plume + skull finial sit here)
    lower = int(h * 0.52)   # lap cradle band (below mid)
    for x in range(w):
        for y in range(h):
            if al[x, y] < 60:
                continue
            r, g, b = int(px[x, y][0]), int(px[x, y][1]), int(px[x, y][2])
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            # pale cradle-skull: bright + near-neutral-green, in the lower band
            if y > lower and r > 180 and g > 200 and b > 180:
                pale_n += 1
                pale_lum = max(pale_lum, lum)
            # green plume: green-dominant jade in the top band
            if y < upper and g > 110 and g >= r and b < g:
                plume_n += 1
    del px, al
    print("self-check 32px: pale cradle px=%d (peak lum %.0f) | plume jade px=%d "
          "-> cradle tell? %s | plume tell? %s"
          % (pale_n, pale_lum, plume_n, pale_n >= 1, plume_n >= 1))


if __name__ == "__main__":
    main()
