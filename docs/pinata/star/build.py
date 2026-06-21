"""STAR PIÑATA secret flyer skin — concept build (round 2).

The classic 7-point star piñata, the original piñata shape: a fat round core
hull with SEVEN cone spikes radiating outward like a spiky party sun. It must
read as a non-creature "spiky star party-ball" at 40px — nothing else in the
roster has radial spikes, so the silhouette alone carries the identity.

Round-2 lineage (art-director ITERATE notes folded in):
  * TRUE 7-point star with ONE point centred straight UP. The spokes are placed
    on the 7-fold axis (top point at -90°), and the bottom of the ring is a
    SPLAYED PAIR straddling the vertical — there is no spike pointing straight
    down — so the full radial ring reads above Pip's parcel instead of being
    amputated by it.
  * The whole star is RAISED on the canvas (hull centre lifted well above the
    composite centre) so the parcel, which hangs 12 px below the bird centre,
    hangs cleanly BELOW the star rather than occluding its lower half.
  * The crack tell is VALUE-FIRST: a 4-step value swing (dark sealed seam →
    dim lens → bright lens → mid) that is legible on the grayscale strip with
    no hue help. The opening is a VERTICAL diamond candy-glow lens (not a
    horizontal slot) so the widest frame never reads as a smiling mouth.
  * The night additive bloom is boosted ~35% (more reach + alpha) so the
    candy-glow seam is the genuine night focal anchor.
  * The cyan spike is shifted toward teal-green so it doesn't dissolve into the
    mid-blue day sky; the cream crepe-fringe keyline is kept exactly as-is.

Contract mirrors game/animal_ufo.py so a winner lifts straight in:
  * `build(wing_angle_deg) -> pygame.Surface` — one flat 64x84 SRCALPHA frame,
    core mass centred at (BCX,BCY); drawn UPRIGHT (no baked rotation — velocity
    tilt is applied later by the cached getter).
  * driven by `game.parrot._WING_ANGLES = (50,20,-10,-40)` → seam width + glow.
"""
import math
import pygame

from game.parrot import _aaellipse


# ── canvas + anchors (mirror animal_ufo.py) ──────────────────────────────────
COMPOSITE_W = 64
COMPOSITE_H = 84
# Pip's parcel hangs ~12 px below the bird centre (PARCEL_Y_OFFSET). The star is
# lifted ABOVE the composite centre so its whole radial ring clears the parcel.
BCX, BCY = 32, 30               # core hull centre, raised off centre

CORE_R = 14                     # round core hull radius (the spikes sit on it)
SPIKE_LEN = 13                  # cone reach beyond the hull edge (STUBBY)
SPIKE_HALF = 8                  # half-width of a cone base on the hull rim
N_SPIKES = 7                    # the canonical 7 points

# The bottom pair of the 7-fold ring is shortened + splayed so no spike drives
# straight down into the parcel; the full star then reads ABOVE the parcel.
BOTTOM_SPIKE_SCALE = 0.74       # length of the two lowest spikes vs the rest
# The apex is grown to the canvas ceiling (its tip just clears the top edge at
# BCY=30); going further would clip the point, so this is the max lead the
# raised-star layout allows while keeping the KEEP'd parcel clearance.
APEX_SPIKE_SCALE = 1.15


# ── palette ──────────────────────────────────────────────────────────────────
# Cone tips cycle the three candy colours over a mid-purple hull; a cream
# crepe-fringe rim keylines every spike so the dark party colours survive the
# night sky. The candy-glow seam is the bright value anchor in both biomes.
HULL_BODY   = (122,  63, 176)   # #7A3FB0 mid purple hull
HULL_DARK   = ( 78,  36, 118)   # shaded lower hull / cone roots
HULL_HI     = (164, 110, 214)   # upper-hull sheen

# Cyan shifted toward TEAL-GREEN so it doesn't dissolve into a mid-blue day sky.
CANDY = [
    ((232,  48, 122), (180,  24,  86)),   # magenta #E8307A  (tip, shade)
    (( 26, 196, 168), (  16, 132, 112)),  # teal-green #1AC4A8 (was cyan)
    ((244, 194,  51), (196, 142,  22)),   # gold    #F4C233
]

FRINGE      = (255, 244, 218)   # #FFF4DA cream crepe fringe rim / keyline
FRINGE_DK   = (214, 196, 158)   # fringe shade so the rim has its own form

# Candy-glow behind the seam: a warm white-hot interior that brightens as the
# crack opens. Drawn additive so it blooms out of the dark hull at night.
GLOW_CORE   = (255, 248, 220)   # hottest centre of the glow
GLOW_WARM   = (255, 196, 110)   # warm amber halo around it
SEAM_DARK   = ( 30,  14,  46)   # the dark crack itself (deep value contrast)

# Candy peeking through the widest crack (sweets spilling).
CANDY_DOTS  = [(255,  92, 150), (96, 232, 200), (255, 214,  96)]


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _phase(angle_deg):
    """Map a wing angle to a 0..3 crack-stage index. _WING_ANGLES runs
    50→-40, so stage advances 0→3 across the poses: shut → wide → snap back."""
    return int(round((50 - angle_deg) / 30.0)) % 4


# The crack tell is read as FOUR DISTINCT VALUE BEATS on the grayscale strip.
# Two ramps drive it, decoupled so geometry and brightness can be tuned apart:
#   _CRACK_BY_STAGE  → lens WIDTH (how far the seam has parted)
#   _LENS_VAL_BY_STAGE → lens LUMINANCE (how hot the interior glows)
# The luminance ramp is the acceptance criterion: four EVENLY-SPACED steps
# (sealed-dark → dim → brightest → a clearly different mid) so stages 1 and 3 do
# NOT collapse to the same gray. The mid beat (stage 3) sits between dim and
# bright, giving the pulse a living "breath" rather than a one-way wipe — but it
# is a genuinely distinct value, not a repeat of the dim stage.
_CRACK_BY_STAGE = (0.00, 0.40, 1.00, 0.60)
_LENS_VAL_BY_STAGE = (0.00, 0.34, 1.00, 0.50)


def _spike_geom(i):
    """Return (ang_rad, length_scale) for spike i of the 7-fold ring. The top
    point is centred straight UP (-90°); spikes are spaced evenly around the
    circle. The two LOWEST spikes are shortened so the ring's bottom is a
    splayed pair that clears the parcel — and crucially there is NO spike
    pointing straight down (7 is odd, so the bottom straddles the vertical)."""
    ang = -math.pi / 2 + (i / N_SPIKES) * math.tau
    # the two spikes whose direction points into the lower hemisphere most
    # steeply get shortened + read as the splayed bottom pair.
    downness = math.sin(ang)            # +1 = straight down, -1 = straight up
    scale = 1.0
    if downness > 0.6:
        scale = BOTTOM_SPIKE_SCALE
    elif i == 0:
        # the apex spoke is grown a touch so it is unambiguously the SINGLE
        # longest tip — the one point that reads as straight up at 40px.
        scale = APEX_SPIKE_SCALE
    return ang, scale


def _spike(surf, cx, cy, ang, length_scale, tip_color, tip_shade):
    """One cone spike radiating from the hull centre along `ang` (rad). The cone
    base sits on the hull rim and converges to a SINGLE point at the tip — a true
    triangle, not a flat-capped trapezoid (the flat cap's two corners used to
    straddle the vertical at the apex and read as two tips). A small cream pom
    sits dead-centre on the point so the tip never thins to a needle at 40px,
    while the single apex still reads as ONE point straight up. A cream keyline
    traces the whole cone so the dark candy colour survives the night sky."""
    reach = SPIKE_LEN * length_scale
    base_x = cx + math.cos(ang) * (CORE_R - 2)
    base_y = cy + math.sin(ang) * (CORE_R - 2)
    tip_x  = cx + math.cos(ang) * (CORE_R + reach)
    tip_y  = cy + math.sin(ang) * (CORE_R + reach)
    # perpendicular for the cone base width
    px, py = -math.sin(ang), math.cos(ang)
    bl = (base_x + px * SPIKE_HALF, base_y + py * SPIKE_HALF)
    br = (base_x - px * SPIKE_HALF, base_y - py * SPIKE_HALF)
    tip = (tip_x, tip_y)

    poly = [bl, tip, br]
    # shade half (lower side of the cone) then the lit candy colour on top
    pygame.draw.polygon(surf, tip_shade, poly)
    mid_base = ((bl[0] + br[0]) / 2, (bl[1] + br[1]) / 2)
    lit = [bl, tip, mid_base]
    pygame.draw.polygon(surf, tip_color, lit)
    # cream crepe keyline around the cone — the night-survival rim (KEEP AS-IS)
    pygame.draw.polygon(surf, FRINGE, poly, 1)
    # fringe pom cap centred ON the single point so the tip reads as one nub,
    # never a needle and never a split flat cap.
    pygame.draw.circle(surf, FRINGE, (int(tip_x), int(tip_y)), 2)
    pygame.draw.circle(surf, FRINGE_DK, (int(tip_x), int(tip_y)), 2, 1)


def _hull_fringe_rings(surf, cx, cy):
    """Two cream crepe fringe bands wrapped round the core hull — the piñata's
    layered crepe-paper read. Drawn as short radial ticks so they survive at
    small scale as a textured cream ring keylining the round body."""
    for ring_r, n in ((CORE_R - 1, 26), (CORE_R - 6, 20)):
        for i in range(n):
            a = (i / n) * math.tau
            x0 = cx + math.cos(a) * (ring_r - 2)
            y0 = cy + math.sin(a) * (ring_r - 2)
            x1 = cx + math.cos(a) * ring_r
            y1 = cy + math.sin(a) * ring_r
            col = FRINGE if i % 2 == 0 else FRINGE_DK
            pygame.draw.line(surf, col, (x0, y0), (x1, y1), 1)


def _crack_and_glow(surf, cx, cy, crack, lens_val):
    """The signature tell. A VERTICAL diamond seam down the core hull. As
    `crack` grows the seam parts into a vertical candy-glow LENS (a diamond,
    not a horizontal slot) with dark crack lips left + right; at the widest
    opening 1-2 candy dots peek through. A vertical/diamond lens never reads as
    a smiling mouth. Kept centred on the (raised) hull so it sits well above the
    parcel. VALUE-FIRST so it survives grayscale: `lens_val` (0..1) sets the
    interior luminance directly, decoupled from the geometric crack width, so
    the four stages land on four EVENLY-SPACED grayscale beats (no two stages
    collapse to the same gray)."""
    seam_cx, seam_cy = cx, cy        # the lens is centred on the hull
    half_h = CORE_R - 3              # the seam runs most of the hull height
    open_w = int(1 + crack * 8)      # horizontal half-width of the open lens

    if crack > 0.02:
        # warm glow lens behind the crack, drawn additive so it blooms at night.
        # Reach kept wide (night focal anchor); peak alpha pulled back ~10% from
        # round 2 so the bloom no longer bleeds over the white lens edge at 40px.
        # Alpha tracks `lens_val` so the brightest beat (stage 2) blooms most.
        gw = open_w * 2 + 28
        gh = half_h * 2 + 28
        glow = pygame.Surface((gw, gh), pygame.SRCALPHA)
        gx, gy = gw // 2, gh // 2
        for i in range(4, 0, -1):
            rr = i / 4.0
            a = int(170 * lens_val * (1.0 - (i - 1) / 4.0)) + 30
            col = GLOW_WARM if i > 1 else GLOW_CORE
            pygame.draw.ellipse(
                glow, (*col, a),
                pygame.Rect(gx - (open_w + 8) * rr, gy - (half_h + 4) * rr,
                            (open_w + 8) * 2 * rr, (half_h + 4) * 2 * rr))
        surf.blit(glow, (seam_cx - gx, seam_cy - gy),
                  special_flags=pygame.BLEND_RGBA_ADD)

    if crack > 0.04:
        # bright hot diamond core fill of the open lens (non-additive so it
        # stays solid and reads as a lit interior even on a bright day sky).
        # The lens VALUE tracks `lens_val` (not the crack width) so the four
        # stages land on evenly-spaced grayscale beats: a DIM lens at stage 1,
        # the white-hot peak at stage 2, a distinct MID at stage 3.
        warm = tuple(min(255, int(GLOW_WARM[c] * (0.42 + 0.58 * lens_val)))
                     for c in range(3))
        diamond = [
            (seam_cx, seam_cy - half_h),
            (seam_cx + open_w, seam_cy),
            (seam_cx, seam_cy + half_h),
            (seam_cx - open_w, seam_cy),
        ]
        pygame.draw.polygon(surf, warm, diamond)
        # the white-hot inner core scales with luminance, so the brightest beat
        # reads near-white and the mid beat stays a clearly cooler amber.
        if lens_val > 0.4:
            t = min(1.0, (lens_val - 0.4) / 0.6)
            core = tuple(int(GLOW_WARM[c] + (GLOW_CORE[c] - GLOW_WARM[c]) * t)
                         for c in range(3))
            inner = [
                (seam_cx, seam_cy - int(half_h * 0.72)),
                (seam_cx + max(1, int(open_w * 0.72)), seam_cy),
                (seam_cx, seam_cy + int(half_h * 0.72)),
                (seam_cx - max(1, int(open_w * 0.72)), seam_cy),
            ]
            pygame.draw.polygon(surf, core, inner)

    # the dark crack lips LEFT & RIGHT — the value contrast that survives gray.
    # As the lens widens the lips pull apart; this is the dark frame around the
    # bright interior that makes the value swing legible with no hue.
    lip = max(2, int(half_h * (1.0 - 0.12 * crack)))
    pygame.draw.line(surf, SEAM_DARK,
                     (seam_cx - open_w, seam_cy - lip),
                     (seam_cx - open_w, seam_cy + lip), 2)
    pygame.draw.line(surf, SEAM_DARK,
                     (seam_cx + open_w, seam_cy - lip),
                     (seam_cx + open_w, seam_cy + lip), 2)
    # the closed-seam groove when sealed so the tell exists even shut — a deep
    # near-black VERTICAL bar so stage 0 reads unambiguously DARKEST on the
    # grayscale strip (the dark anchor the bright lens stages swing away from).
    if crack <= 0.12:
        pygame.draw.line(surf, SEAM_DARK, (seam_cx - 1, seam_cy - lip),
                         (seam_cx - 1, seam_cy + lip), 2)
        pygame.draw.line(surf, SEAM_DARK, (seam_cx + 1, seam_cy - lip),
                         (seam_cx + 1, seam_cy + lip), 2)

    # candy dots spilling at the widest opening
    if crack > 0.7:
        for k, (dx, dy) in enumerate(((-1, -4), (2, 4), (-2, 1))):
            r = 2 if k < 2 else 1
            pygame.draw.circle(surf, CANDY_DOTS[k % 3],
                               (seam_cx + dx, seam_cy + dy), r)
            pygame.draw.circle(surf, FRINGE,
                               (seam_cx + dx, seam_cy + dy), r, 1)


def build(wing_angle_deg):
    surf = _new()
    ph = _phase(wing_angle_deg)
    crack = _CRACK_BY_STAGE[ph]
    lens_val = _LENS_VAL_BY_STAGE[ph]
    cx, cy = BCX, BCY

    # 1) Seven cone spikes FIRST so the round hull overlaps their roots and the
    #    silhouette reads as a unified spiky star, not loose triangles. The top
    #    point is centred upward; the bottom pair is splayed + shortened.
    for i in range(N_SPIKES):
        ang, scale = _spike_geom(i)
        tip, shade = CANDY[i % 3]
        _spike(surf, cx, cy, ang, scale, tip, shade)

    # 2) Round core hull — the dominant central mass the spikes radiate from.
    _aaellipse(surf, HULL_DARK, (cx, cy + 2), CORE_R, CORE_R)        # shadow
    _aaellipse(surf, HULL_BODY, (cx, cy), CORE_R, CORE_R)            # body
    _aaellipse(surf, HULL_HI, (cx - 4, cy - 5), CORE_R - 6, CORE_R - 8)  # sheen
    # cream rim keyline around the whole hull (night survival)
    pygame.draw.circle(surf, FRINGE, (cx, cy), CORE_R, 1)

    # 3) Crepe fringe bands wrapped on the hull, then the crack-&-glow tell on
    #    top so the glow is never buried under the fringe texture.
    _hull_fringe_rings(surf, cx, cy)
    _crack_and_glow(surf, cx, cy, crack, lens_val)

    return surf
