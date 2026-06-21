"""CLASSIC TROLLEY — secret flyer skin concept (round 1).

A flying supermarket cart replaces Pip. The universal cart read is a
trapezoid basket FLARED OPEN at the top, narrow at the bottom, sitting on
two wheels, with a single curved push-handle hooking up off the back-right.
There are NO wings: the "flap" is reinterpreted as SPINNING WHEELS — each
wheel hub cycles a 4-phase spoke cross (+ → × → + → ×) and the whole cart
bobs 1px so it reads as rolling through the air.

The prior-failure trap for a wire trolley is that thin diagonal grid lines
VANISH at 40px and turn to mush. So the load-bearing read here is a BOLD
FILLED basket mass + two BOLD wheels; the wire grid is only SUGGESTED by a
few fat verticals that are allowed to drop entirely at 40px without losing
the silhouette.

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

WHEEL_DARK  = (43, 49, 56)      # #2B3138 near-black tyre
WHEEL_KEY   = (242, 245, 248)   # #F2F5F8 keyline — pops the wheels on night sky
WHEEL_HUB   = (232, 237, 242)   # bright hub plate (the value-flip disc)
SPOKE_DARK  = (43, 49, 56)      # spoke cross cut into the bright hub (value flip)

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


def _wheel(surf, cx, cy, r, phase):
    """A BOLD near-black wheel with a bright keyline ring, a bright hub plate,
    and a spoke cross cut into the hub as a VALUE FLIP (dark spokes on the
    bright plate). The cross orientation cycles + → × → + → × across the four
    phases, which is the rolling tell that survives grayscale (a value flip
    inside a solid disc, not a hue change)."""
    # bright keyline ring first so it haloes the tyre on a dark night sky
    pygame.draw.circle(surf, WHEEL_KEY, (cx, cy), r + 1)
    # near-black tyre body
    pygame.draw.circle(surf, WHEEL_DARK, (cx, cy), r)
    # bright hub plate — the disc the spoke cross is cut into
    hub_r = r - 2
    pygame.draw.circle(surf, WHEEL_HUB, (cx, cy), hub_r)
    # spoke cross: phase 0/2 → upright "+", phase 1/3 → diagonal "×"
    ang0 = 0 if phase % 2 == 0 else 45
    for k in range(4):
        a = math.radians(ang0 + k * 90)
        ex = cx + int(round(math.cos(a) * hub_r))
        ey = cy + int(round(math.sin(a) * hub_r))
        pygame.draw.line(surf, SPOKE_DARK, (cx, cy), (ex, ey), 2)
    # small dark centre cap so the cross reads as anchored at the axle
    pygame.draw.circle(surf, WHEEL_DARK, (cx, cy), 2)


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

    # cargo block sitting IN the basket (warm accent) — drawn first so the
    # basket front grid overlaps it and it reads as goods inside the cart.
    cargo = [
        (BCX - 13, top_y + 2),
        (BCX + 13, top_y + 2),
        (BCX + 9, BCY + 2 + bob),
        (BCX - 9, BCY + 2 + bob),
    ]
    _vbanded_polygon(surf, cargo, top_y + 2, BCY + 2 + bob, CARGO_HI, CARGO, CARGO_LO)
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
    wy = bot_y + 5 + bob
    wr = 6
    _wheel(surf, BCX - 9, wy, wr, ph)
    _wheel(surf, BCX + 9, wy, wr, ph)
    # short steel struts from the base corners down to each axle (fat, survive)
    pygame.draw.line(surf, STEEL_LO, (BCX - bot_hw + 2, bot_y), (BCX - 9, wy), 3)
    pygame.draw.line(surf, STEEL_LO, (BCX + bot_hw - 2, bot_y), (BCX + 9, wy), 3)
    pygame.draw.line(surf, STEEL_HI, (BCX - bot_hw + 2, bot_y), (BCX - 9, wy), 1)
    pygame.draw.line(surf, STEEL_HI, (BCX + bot_hw - 2, bot_y), (BCX + 9, wy), 1)

    return surf
