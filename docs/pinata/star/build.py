"""STAR PIÑATA secret flyer skin — concept build.

The classic 7-point star piñata, the original piñata shape: a fat round core
hull with SEVEN cone spikes radiating outward like a spiky party sun. It must
read as a non-creature "spiky star party-ball" at 40px — nothing else in the
roster has radial spikes, so the silhouette alone carries the identity.

The 4-frame tell is CRACK & GLOW (no wings, no particles): a horizontal seam
across the core hull splits wider across the four poses while a warm candy-glow
brightens behind it and 1-2 candy dots peek out by the widest frame, then snaps
shut to loop. It survives grayscale because it is a VALUE pulse — a dark seam
opening over a bright interior — not a hue trick. The seam is kept at/above the
hull centre because Pip's parcel hangs just below centre in play and would
otherwise occlude the tell.

Contract mirrors game/animal_ufo.py so a winner lifts straight in:
  * `build(wing_angle_deg) -> pygame.Surface` — one flat 64x84 SRCALPHA frame,
    core mass centred at (BCX,BCY)=(32,44); drawn UPRIGHT (no baked rotation —
    velocity tilt is applied later by the cached getter).
  * driven by `game.parrot._WING_ANGLES = (50,20,-10,-40)` → seam width + glow.
"""
import math
import pygame

from game.parrot import _aaellipse


# ── canvas + anchors (mirror animal_ufo.py) ──────────────────────────────────
COMPOSITE_W = 64
COMPOSITE_H = 84
DY = 12
BCX, BCY = 32, 32 + DY          # core hull centre → (32, 44)

CORE_R = 15                     # round core hull radius (the spikes sit on it)
SPIKE_LEN = 13                  # cone reach beyond the hull edge (STUBBY)
SPIKE_HALF = 9                  # half-width of a cone base on the hull rim
N_SPIKES = 7                    # the canonical 7 points


# ── palette ──────────────────────────────────────────────────────────────────
# Cone tips alternate the three candy colours over a mid-purple hull; a cream
# crepe-fringe rim keylines every spike so the dark party colours survive the
# night sky. The candy-glow seam is the bright value anchor in both biomes.
HULL_BODY   = (122,  63, 176)   # #7A3FB0 mid purple hull
HULL_DARK   = ( 78,  36, 118)   # shaded lower hull / cone roots
HULL_HI     = (164, 110, 214)   # upper-hull sheen

CANDY = [
    ((232,  48, 122), (180,  24,  86)),   # magenta #E8307A  (tip, shade)
    (( 31, 182, 214), (  22, 120, 150)),  # cyan    #1FB6D6
    ((244, 194,  51), (196, 142,  22)),   # gold    #F4C233
]

FRINGE      = (255, 244, 218)   # #FFF4DA cream crepe fringe rim / keyline
FRINGE_DK   = (214, 196, 158)   # fringe shade so the rim has its own form

# Candy-glow behind the seam: a warm white-hot interior that brightens as the
# crack opens. Drawn additive so it blooms out of the dark hull at night.
GLOW_CORE   = (255, 246, 214)   # hottest centre of the glow
GLOW_WARM   = (255, 196, 110)   # warm amber halo around it
SEAM_DARK   = ( 38,  18,  58)   # the dark crack itself (value contrast)

# Candy peeking through the widest crack (sweets spilling).
CANDY_DOTS  = [(255,  92, 150), (96, 220, 244), (255, 214,  96)]


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _phase(angle_deg):
    """Map a wing angle to a 0..3 crack-stage index. _WING_ANGLES runs
    50→-40, so stage advances 0→3 across the poses: shut → wide → snap back."""
    return int(round((50 - angle_deg) / 30.0)) % 4


# Crack opening (0..1) per stage. 0 = sealed seam, peak = widest split with
# candy peeking, then the last stage eases back so the loop snaps shut. A
# non-monotonic curve makes the pulse read as a living "breath", not a wipe.
_CRACK_BY_STAGE = (0.10, 0.55, 1.00, 0.42)


def _spike(surf, cx, cy, ang, tip_color, tip_shade):
    """One stubby cone spike radiating from the hull centre along `ang` (rad).
    The cone base sits on the hull rim; the tip is fringe-tipped (a cream cap),
    never a thin needle, so it doesn't vanish at 40px. A cream keyline traces
    the whole cone so the dark candy colour survives the night sky."""
    base_x = cx + math.cos(ang) * (CORE_R - 2)
    base_y = cy + math.sin(ang) * (CORE_R - 2)
    tip_x  = cx + math.cos(ang) * (CORE_R + SPIKE_LEN)
    tip_y  = cy + math.sin(ang) * (CORE_R + SPIKE_LEN)
    # perpendicular for the cone base width
    px, py = -math.sin(ang), math.cos(ang)
    bl = (base_x + px * SPIKE_HALF, base_y + py * SPIKE_HALF)
    br = (base_x - px * SPIKE_HALF, base_y - py * SPIKE_HALF)
    # blunt the tip into a short flat cap (the fringe pom) instead of a point
    tl = (tip_x + px * 2.4, tip_y + py * 2.4)
    tr = (tip_x - px * 2.4, tip_y - py * 2.4)

    poly = [bl, tl, tr, br]
    # shade half (lower side of the cone) then the lit candy colour on top
    pygame.draw.polygon(surf, tip_shade, poly)
    lit = [bl, tl, ((tl[0] + tr[0]) / 2, (tl[1] + tr[1]) / 2),
           ((bl[0] + br[0]) / 2, (bl[1] + br[1]) / 2)]
    pygame.draw.polygon(surf, tip_color, lit)
    # cream crepe keyline around the cone — the night-survival rim
    pygame.draw.polygon(surf, FRINGE, poly, 1)
    # fringe pom cap at the tip (a small cream nub) so the point never needles
    pygame.draw.line(surf, FRINGE, tl, tr, 2)
    pygame.draw.circle(surf, FRINGE, (int(tip_x), int(tip_y)), 2)
    pygame.draw.circle(surf, FRINGE_DK, (int(tip_x), int(tip_y)), 2, 1)


def _hull_fringe_rings(surf, cx, cy):
    """Two cream crepe fringe bands wrapped round the core hull — the piñata's
    layered crepe-paper read. Drawn as short radial ticks so they survive at
    small scale as a textured cream ring keylining the round body."""
    for ring_r, n in ((CORE_R - 1, 28), (CORE_R - 6, 22)):
        for i in range(n):
            a = (i / n) * math.tau
            x0 = cx + math.cos(a) * (ring_r - 2)
            y0 = cy + math.sin(a) * (ring_r - 2)
            x1 = cx + math.cos(a) * ring_r
            y1 = cy + math.sin(a) * ring_r
            col = FRINGE if i % 2 == 0 else FRINGE_DK
            pygame.draw.line(surf, col, (x0, y0), (x1, y1), 1)


def _crack_and_glow(surf, cx, cy, crack):
    """The signature tell. A horizontal seam across the upper-half of the core
    hull. As `crack` grows the seam parts into a lens of warm candy-glow with a
    dark crack lip top and bottom; at the widest opening 1-2 candy dots peek
    through. Kept at/above hull centre so Pip's parcel (hung below) never hides
    it. Value-first so it survives grayscale."""
    seam_y = cy - 3                      # at/above centre
    half_w = CORE_R - 4                  # seam spans most of the hull width
    open_h = int(1 + crack * 8)          # vertical gap of the crack

    if crack > 0.05:
        # warm glow lens behind the crack, drawn additive so it blooms at night
        gw, gh = half_w * 2 + 8, open_h * 2 + 10
        glow = pygame.Surface((gw, gh), pygame.SRCALPHA)
        gx, gy = gw // 2, gh // 2
        for i in range(3, 0, -1):
            rr = i / 3.0
            a = int(150 * crack * (1.0 - (i - 1) / 3.0)) + 40
            col = GLOW_WARM if i > 1 else GLOW_CORE
            pygame.draw.ellipse(
                glow, (*col, a),
                pygame.Rect(gx - half_w * rr, gy - open_h * rr,
                            half_w * 2 * rr, open_h * 2 * rr))
        surf.blit(glow, (cx - gx, seam_y - gy),
                  special_flags=pygame.BLEND_RGBA_ADD)
        # bright hot core fill of the open lens (non-additive so it stays solid
        # and reads as a lit interior even on a bright day sky)
        pygame.draw.ellipse(
            surf, GLOW_CORE,
            pygame.Rect(cx - int(half_w * 0.7), seam_y - int(open_h * 0.7),
                        int(half_w * 1.4), int(open_h * 1.4)))

    # the dark crack lips top & bottom — the value contrast that survives gray
    lip = max(1, int(half_w * (1.0 - 0.15 * crack)))
    pygame.draw.line(surf, SEAM_DARK,
                     (cx - lip, seam_y - open_h), (cx + lip, seam_y - open_h),
                     2)
    pygame.draw.line(surf, SEAM_DARK,
                     (cx - lip, seam_y + open_h), (cx + lip, seam_y + open_h),
                     2)
    # the closed-seam centre line at low crack so the tell exists even sealed
    if crack <= 0.2:
        pygame.draw.line(surf, SEAM_DARK, (cx - lip, seam_y),
                         (cx + lip, seam_y), 1)

    # candy dots spilling at the widest opening
    if crack > 0.7:
        for k, (dx, dy) in enumerate(((-5, 1), (4, -1), (0, 3))):
            r = 2 if k < 2 else 1
            pygame.draw.circle(surf, CANDY_DOTS[k % 3],
                               (cx + dx, seam_y + dy), r)
            pygame.draw.circle(surf, FRINGE, (cx + dx, seam_y + dy), r, 1)


def build(wing_angle_deg):
    surf = _new()
    ph = _phase(wing_angle_deg)
    crack = _CRACK_BY_STAGE[ph]
    cx, cy = BCX, BCY

    # 1) Seven cone spikes FIRST so the round hull overlaps their roots and the
    #    silhouette reads as a unified spiky star, not loose triangles. The top
    #    point is centred upward; the rest are evenly spaced around the circle.
    for i in range(N_SPIKES):
        ang = -math.pi / 2 + (i / N_SPIKES) * math.tau
        tip, shade = CANDY[i % 3]
        _spike(surf, cx, cy, ang, tip, shade)

    # 2) Round core hull — the dominant central mass the spikes radiate from.
    _aaellipse(surf, HULL_DARK, (cx, cy + 2), CORE_R, CORE_R)        # shadow
    _aaellipse(surf, HULL_BODY, (cx, cy), CORE_R, CORE_R)            # body
    _aaellipse(surf, HULL_HI, (cx - 4, cy - 5), CORE_R - 6, CORE_R - 8)  # sheen
    # cream rim keyline around the whole hull (night survival)
    pygame.draw.circle(surf, FRINGE, (cx, cy), CORE_R, 1)

    # 3) Crepe fringe bands wrapped on the hull, then the crack-&-glow tell on
    #    top so the glow is never buried under the fringe texture.
    _hull_fringe_rings(surf, cx, cy)
    _crack_and_glow(surf, cx, cy, crack)

    return surf
