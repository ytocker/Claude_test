"""CLASSIC TROLLEY — secret flyer skin concept (round 2).

A flying supermarket cart replaces Pip. The universal cart read is a
trapezoid basket FLARED OPEN at the top, narrow at the bottom, sitting on
two wheels, with a single curved push-handle hooking up off the back-right.
There are NO wings: the "flap" is reinterpreted as SPINNING WHEELS.

Round-2 fix — the spin tell is the concept's whole motion premise and it
died at 40px, so the wheels are rebuilt around legibility at true scale:
  * FAT round wheels with a bright hub plate and a SINGLE bold spoke BAR
    (not a fine cross cut into a small disc — that turned to sub-pixel mush).
  * The spin is re-told as that bar ROTATING through ~4 stepped angles
    (vertical → diagonal → horizontal → diagonal). A rotating bar is NOT
    rotationally self-similar the way a +→× flip is, so it reads as MOTION
    in grayscale at 40px. Paired with a 1px bob.
  * Tyres lifted off near-black to a dark STEEL so the two wheels don't
    collapse into one black blob on a bright DAY sky; the bright keyline
    ring carries the per-wheel edge so the pair stays visually SEPARATE.
  * Wider wheel TRACK so a strip of sky shows between the two circles —
    a visible gap is what actually sells "two wheels" at 40px.
  * Cargo is seated HIGHER inside the basket, clear of the wheel zone, so
    nothing occludes the wheels (the wheels are the tell). Pip's parcel is
    composited by the game and now sits above the wheels, not on them.

The prior wire-trolley trap (thin diagonal grid lines vanish at 40px) is
still avoided: the load-bearing read is a BOLD FILLED basket mass + two
BOLD wheels; the wire grid is only SUGGESTED by a few fat verticals that
are allowed to drop entirely at 40px without losing the silhouette.

Contract mirrors game/animal_ufo.py so the winner lifts straight into a
production module:
  * `build(wing_angle_deg) -> pygame.Surface` — one flat 64x84 SRCALPHA
    frame; basket body mass centred at (BCX, BCY) = (32, 44).
  * 4 wheel-spin frames driven by `_WING_ANGLES = (50, 20, -10, -40)`.
  * drawn UPRIGHT — velocity tilt is applied later by the getter cache.
"""
import math
import pygame

from game.parrot import _aaellipse


# ── canvas + anchors (mirror animal_ufo.py) ──────────────────────────────────
COMPOSITE_W = 64
COMPOSITE_H = 84
DY = 12
BCX, BCY = 32, 32 + DY          # basket body centre → (32, 44)


# ── chrome-steel palette ─────────────────────────────────────────────────────
# Vertical value banding sells "polished metal" — a light highlight band, a
# mid band, and a shadow band. On DAY the wheel keyline carries the read; on
# NIGHT the light steel band IS the silhouette against the dark sky.
STEEL_HI    = (232, 237, 242)   # #E8EDF2 chrome highlight
STEEL_MID   = (159, 176, 190)   # #9FB0BE mid steel
STEEL_LO    = (91, 107, 120)    # #5B6B78 shadow steel
STEEL_EDGE  = (60, 74, 86)      # darker rim/contour so the mass has a hard edge

# Tyres are dark STEEL, not near-black: on a bright DAY sky two near-black
# discs an axle apart muddied into one dark blob. Dark steel + a bright
# keyline ring per wheel keeps each circle reading as its own object.
WHEEL_TYRE  = (74, 84, 96)      # #4A5460 dark steel tyre (lifted off black)
WHEEL_TYRE_LO = (54, 62, 72)    # lower-arc tyre shade for a touch of roundness
WHEEL_KEY   = (244, 247, 250)   # #F4F7FA keyline ring — the per-wheel edge
WHEEL_HUB   = (236, 240, 245)   # bright hub plate (the disc the bar sits on)
SPOKE_DARK  = (40, 46, 54)      # the single bold spoke BAR (dark on the bright hub)
AXLE_DARK   = (40, 46, 54)      # tiny centre cap so the bar reads anchored at the axle

CARGO       = (240, 162, 58)    # #F0A23A warm cargo accent
CARGO_HI    = (255, 198, 110)   # cargo highlight
CARGO_LO    = (188, 116, 30)    # cargo shadow

HANDLE_HI   = (232, 237, 242)   # handle catches the same chrome light
HANDLE_LO   = (91, 107, 120)


# 4 spin phases — mapped from _WING_ANGLES so the getter's frame index drives
# the spoke-cross orientation + the 1px bob. Imported from parrot so the cache
# factory and gameplay lib stay in lock-step.
from game.parrot import _WING_ANGLES


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _phase(angle_deg):
    """Map a wing angle (50→-40) to a 0..3 spin step. The basket bobs and the
    spoke cross flips +/× one notch per pose so the wheels read as rolling."""
    return int(round((50 - angle_deg) / 30.0)) % 4


def _vbanded_polygon(surf, pts, top_y, bot_y, c_hi, c_mid, c_lo):
    """Fill a polygon with a vertical 3-stop value band (hi→mid→lo top to
    bottom). Painted by clipping horizontal bars to a mask of the polygon so
    the chrome banding follows the trapezoid edges exactly. This is the BOLD
    filled mass that survives 40px after the wire grid drops out."""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1 = int(min(xs)), int(max(xs)) + 1
    y0, y1 = int(min(ys)), int(max(ys)) + 1
    w, h = x1 - x0, y1 - y0
    layer = pygame.Surface((w, h), pygame.SRCALPHA)
    # vertical value ramp painted as 1px bars, hi at top → lo at bottom
    span = max(1, bot_y - top_y)
    for y in range(h):
        t = max(0.0, min(1.0, (y + y0 - top_y) / span))
        if t < 0.5:
            k = t / 0.5
            col = tuple(int(c_hi[i] + (c_mid[i] - c_hi[i]) * k) for i in range(3))
        else:
            k = (t - 0.5) / 0.5
            col = tuple(int(c_mid[i] + (c_lo[i] - c_mid[i]) * k) for i in range(3))
        layer.fill((*col, 255), pygame.Rect(0, y, w, 1))
    # clamp the band to the polygon silhouette
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), [(p[0] - x0, p[1] - y0) for p in pts])
    layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(layer, (x0, y0))


# The bar steps through these absolute angles, one per spin phase. They are
# NOT 90°-apart (that would make a single bar look the same every other frame
# the way + and × do); ~45° steps walk the bar vertical → diagonal →
# horizontal → diagonal so consecutive frames are always distinguishable.
_BAR_ANGLES = (90, 45, 0, 135)   # degrees: vertical, /, horizontal, \


def _wheel(surf, cx, cy, r, phase):
    """A FAT wheel built for 40px legibility: a bright keyline ring (the per-
    wheel edge), a dark-STEEL tyre, a bright hub plate, and a SINGLE bold
    spoke BAR across the hub. The bar steps through _BAR_ANGLES so it visibly
    ROTATES frame to frame — a rotating bar is not rotationally self-similar,
    so the spin survives grayscale at true scale (the round-1 fine spoke
    cross was sub-pixel mush). The bar runs edge-to-edge through the hub so
    it stays ~2px even after downscale."""
    # bright keyline ring first — haloes the tyre and, crucially, draws a
    # bright edge between the two wheels so the pair never fuses into a blob.
    pygame.draw.circle(surf, WHEEL_KEY, (cx, cy), r + 1)
    # dark-steel tyre body (lifted off near-black so it separates on day sky)
    pygame.draw.circle(surf, WHEEL_TYRE, (cx, cy), r)
    # a hair of lower-arc shade for roundness, without darkening the whole tyre
    pygame.draw.circle(surf, WHEEL_TYRE_LO, (cx, cy + 1), r, 2)
    # bright hub plate — the disc the single bar is read against (value flip)
    hub_r = r - 2
    pygame.draw.circle(surf, WHEEL_HUB, (cx, cy), hub_r)
    # the single bold spoke BAR, drawn edge-to-edge across the hub at the
    # phase's angle. Width 3 in the 64px build so it survives the ~0.65x
    # downscale to play size as a clear ~2px bar.
    a = math.radians(_BAR_ANGLES[phase % 4])
    dx = math.cos(a) * hub_r
    dy = math.sin(a) * hub_r
    pygame.draw.line(surf, SPOKE_DARK,
                     (cx - dx, cy - dy), (cx + dx, cy + dy), 3)
    # tiny centre cap so the bar reads anchored at the axle
    pygame.draw.circle(surf, AXLE_DARK, (cx, cy), 2)


def build(wing_angle_deg):
    surf = _new()
    ph = _phase(wing_angle_deg)
    bob = (0, -1, 0, 1)[ph]                       # 1px vertical roll bob

    # ── basket trapezoid: FLARED OPEN at the top, narrow at the bottom ──
    # Wider than tall; this flared mass + the rear handle-hook is the universal
    # "shopping cart" read. Coordinates are relative to the body centre so the
    # collision circle at (32,44) stays inside the dominant mass.
    top_y = BCY - 11 + bob
    bot_y = BCY + 9 + bob
    top_hw = 22                                   # half-width at the flared top
    bot_hw = 14                                   # half-width at the narrow base
    basket = [
        (BCX - top_hw, top_y),                    # top-left lip
        (BCX + top_hw, top_y),                    # top-right lip
        (BCX + bot_hw, bot_y),                    # bottom-right
        (BCX - bot_hw, bot_y),                    # bottom-left
    ]

    # cargo block sitting HIGH in the basket (warm accent) — drawn first so
    # the basket front grid overlaps it and it reads as goods inside the cart.
    # Seated near the flared mouth and kept well ABOVE the basket base so it
    # never reaches down into the wheel zone (the wheels are the spin tell;
    # nothing — cargo or Pip's composited parcel — should occlude them).
    cargo_bot = top_y + 11
    cargo = [
        (BCX - 13, top_y + 2),
        (BCX + 13, top_y + 2),
        (BCX + 10, cargo_bot),
        (BCX - 10, cargo_bot),
    ]
    _vbanded_polygon(surf, cargo, top_y + 2, cargo_bot, CARGO_HI, CARGO, CARGO_LO)
    pygame.draw.line(surf, CARGO_HI, (BCX - 11, top_y + 3), (BCX + 11, top_y + 3), 1)

    # BOLD filled basket mass — chrome vertical banding. This is the load-
    # bearing read; everything below it (wire grid) is allowed to drop at 40px.
    _vbanded_polygon(surf, basket, top_y, bot_y, STEEL_HI, STEEL_MID, STEEL_LO)

    # hard contour so the trapezoid keeps a crisp metal edge on a bright sky
    pygame.draw.polygon(surf, STEEL_EDGE, basket, 2)

    # flared top RIM — a fat bright bar across the open mouth: the single most
    # cart-defining line, so it gets full weight and never drops.
    pygame.draw.line(surf, STEEL_HI, (BCX - top_hw, top_y), (BCX + top_hw, top_y), 3)
    pygame.draw.line(surf, STEEL_EDGE, (BCX - top_hw, top_y + 2),
                     (BCX + top_hw, top_y + 2), 1)

    # SUGGESTED wire grid: 3 fat verticals only (no thin diagonals). These are
    # deliberately heavy so they survive a little, but the basket mass already
    # carries the read if they blur away at true 40px.
    for fx in (-9, 0, 9):
        x = BCX + fx
        # taper the vertical toward the narrow base, following the trapezoid
        tx = BCX + int(fx * (bot_hw / top_hw))
        pygame.draw.line(surf, STEEL_LO, (x, top_y + 3), (tx, bot_y - 2), 2)
        pygame.draw.line(surf, STEEL_HI, (x - 1, top_y + 3), (tx - 1, bot_y - 2), 1)
    # one mid horizontal rail to read as a basket band (kept fat)
    pygame.draw.line(surf, STEEL_HI, (BCX - 19, BCY - 1 + bob),
                     (BCX + 19, BCY - 1 + bob), 2)
    pygame.draw.line(surf, STEEL_EDGE, (BCX - 19, BCY + 1 + bob),
                     (BCX + 19, BCY + 1 + bob), 1)

    # ── push-handle: a single curved bar hooking UP off the back-right ──
    # The handle-hook is half the cart read, so it is drawn bold (3px) with a
    # chrome highlight. It arcs from the top-back of the basket up and to the
    # right, ending in the rounded grip players push.
    hx = BCX + top_hw                              # anchor at the top-right lip
    hy = top_y + 1
    # vertical riser up from the basket back
    rise_top = hy - 16
    pygame.draw.line(surf, HANDLE_LO, (hx, hy), (hx + 5, rise_top + 2), 4)
    pygame.draw.line(surf, HANDLE_HI, (hx, hy), (hx + 5, rise_top + 2), 2)
    # curved grip arcing back over the top (the push-bar)
    grip = pygame.Rect(hx - 9, rise_top - 4, 16, 14)
    pygame.draw.arc(surf, HANDLE_LO, grip, math.radians(-20), math.radians(110), 4)
    pygame.draw.arc(surf, HANDLE_HI, grip, math.radians(-20), math.radians(110), 2)
    # rounded grip cap
    pygame.draw.circle(surf, HANDLE_HI, (hx - 6, rise_top), 2)

    # ── two spinning wheels under the narrow base ──
    # FAT wheels (r=8) on a WIDE track (±13) so a clear strip of sky shows
    # between the two circles at 40px — centres 26px apart vs 16px edge-to-
    # edge tyre, ~10px gap in the 64px build → a real gap survives downscale.
    # That visible gap is what reads as TWO wheels rather than one blob. They
    # sit a touch lower so the clean cargo-free space below the basket frames
    # them. Struts are drawn first so the wheels overlap the strut tops.
    wy = bot_y + 7 + bob
    wr = 8
    wtrack = 13
    pygame.draw.line(surf, STEEL_LO, (BCX - bot_hw + 2, bot_y), (BCX - wtrack, wy - 3), 3)
    pygame.draw.line(surf, STEEL_LO, (BCX + bot_hw - 2, bot_y), (BCX + wtrack, wy - 3), 3)
    pygame.draw.line(surf, STEEL_HI, (BCX - bot_hw + 2, bot_y), (BCX - wtrack, wy - 3), 1)
    pygame.draw.line(surf, STEEL_HI, (BCX + bot_hw - 2, bot_y), (BCX + wtrack, wy - 3), 1)
    _wheel(surf, BCX - wtrack, wy, wr, ph)
    _wheel(surf, BCX + wtrack, wy, wr, ph)

    return surf
