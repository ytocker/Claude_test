"""SMART CART — secret legendary-tier flyer skin concept (round 1).

The AI self-checkout cart (Caper / Amazon Dash idiom) replaces Pip: a sleek
SQUARED basket on two wheels, topped by a vertical handle bar carrying a flat
rectangular SCREEN panel that juts forward — a "lollipop screen on a box"
profile. No other cart concept pairs a squared (non-flared) basket with an
emissive screen-on-a-stick, so that silhouette is what makes this read
INSTANTLY as a high-tech cart at 40px.

There are NO wings and NO live particles. The signature 4-frame tell is a
BLINKING SCANNER: a scan-beam bar on the screen cycles bright → dim → bright →
off across the four poses (a baked teal-glow ramp), plus a thin baked highlight
sweep travelling across the glass. The light pulse IS the motion — a pure VALUE
pulse, the strongest grayscale tell of the cart set, so the wheels can stay
static. At night the baked teal glow blooms and the cart becomes luminous: the
legendary-tier moment.

Contract mirrors game/animal_ufo.py so the winner lifts straight into a
production module:
  * `build(wing_angle_deg) -> pygame.Surface` — one flat 64x84 SRCALPHA frame;
    dominant basket mass centred at (BCX, BCY) = (32, 44); screen tell ABOVE
    centre; the 14px collision circle at (32,44) sits inside the basket mass.
  * 4 scanner-blink frames driven by `_WING_ANGLES = (50, 20, -10, -40)`.
  * drawn UPRIGHT — velocity tilt is applied later by the getter cache.
"""
import math
import pygame

from game.parrot import _aaellipse, _WING_ANGLES


# ── canvas + anchors (mirror animal_ufo.py) ──────────────────────────────────
COMPOSITE_W = 64
COMPOSITE_H = 84
DY = 12
BCX, BCY = 32, 32 + DY          # basket body centre → (32, 44)


# ── cool white-steel + teal-glow palette ─────────────────────────────────────
# The body is a near-white steel so the SQUARED mass survives a bright day sky;
# the teal screen is the colour pop on day and the luminous bloom on night.
BODY_HI     = (232, 240, 245)   # bright steel highlight band
BODY_MID    = (220, 230, 236)   # #DCE6EC body steel
BODY_LO     = (143, 163, 178)   # #8FA3B2 shadow steel
BODY_EDGE   = (74, 92, 104)     # dark contour so the squared mass has a hard rim

SCREEN_FRAME = (14, 110, 104)   # #0E6E68 teal bezel around the glass
SCREEN_CORE  = (35, 214, 196)   # #23D6C4 teal glow core
SCREEN_DIM   = (18, 120, 112)   # dimmed screen (scanner OFF poses)
SCREEN_DARK  = (9, 58, 56)      # deep glass base under the glow
SCAN_HOT     = (210, 255, 248)  # near-white hot scan bar at peak brightness
SWEEP_HI     = (180, 246, 238)  # baked highlight sweep across the glass

WHEEL_DARK  = (43, 49, 56)      # #2B3138 near-black tyre
WHEEL_KEY   = (236, 244, 248)   # bright keyline ring — pops wheels on night sky
WHEEL_HUB   = (188, 204, 214)   # steel hub plate

CARGO       = (96, 196, 210)    # cool teal-tinted cargo so it reads as the
CARGO_HI    = (170, 232, 238)   # cart's own goods, not a warm foreign block
CARGO_LO    = (52, 132, 150)


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _phase(angle_deg):
    """Map a wing angle (50→-40) to a 0..3 blink step. The scanner bar ramps
    bright → dim → bright → off one notch per pose; that value pulse reads as
    the cart's AI 'thinking', the way a real self-checkout scanner blinks."""
    return int(round((50 - angle_deg) / 30.0)) % 4


# Scanner brightness ramp across the 4 poses. A 4-step value cycle (peak → mid
# → peak → off) gives an unmistakable PULSE rather than a steady glow, and it
# survives grayscale because it is pure value, not hue. The sweep offset moves
# the baked highlight across the glass in lock-step so the screen feels live.
_SCAN_LEVEL = (1.0, 0.45, 0.85, 0.0)     # bright → dim → bright → off
_SWEEP_T    = (0.15, 0.45, 0.70, 1.0)    # highlight sweep position, left→right


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _vbanded_rect(surf, rect, c_hi, c_mid, c_lo, *, radius=3):
    """Fill a rounded rect with a vertical 3-stop value band (hi→mid→lo). The
    banding sells 'polished steel panel' and, being filled, is the load-bearing
    mass that survives 40px after any fine detail blurs away."""
    w, h = rect.w, rect.h
    layer = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        t = y / max(1, h - 1)
        if t < 0.5:
            col = _lerp(c_hi, c_mid, t / 0.5)
        else:
            col = _lerp(c_mid, c_lo, (t - 0.5) / 0.5)
        layer.fill((*col, 255), pygame.Rect(0, y, w, 1))
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=radius)
    layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(layer, rect.topleft)


def _glow_bloom(surf, rect, color, strength):
    """Bake a soft additive teal halo around the screen panel so it blooms on a
    dark night sky (the legendary moment) without punching transparent holes in
    the steel body. Stamped to a scratch surface and added; strength scales
    with the scanner level so the bloom pulses with the blink."""
    if strength <= 0.0:
        return
    pad = 7
    g = pygame.Surface((rect.w + pad * 2, rect.h + pad * 2), pygame.SRCALPHA)
    cx, cy = g.get_width() // 2, g.get_height() // 2
    for i in range(3, 0, -1):
        a = int((30 + (3 - i) * 26) * strength)
        rr = pygame.Rect(0, 0, rect.w + (4 - i) * 4, rect.h + (4 - i) * 4)
        rr.center = (cx, cy)
        pygame.draw.rect(g, (*color, a), rr, border_radius=5)
    surf.blit(g, (rect.x - pad, rect.y - pad), special_flags=pygame.BLEND_RGBA_ADD)


def _wheel(surf, cx, cy, r):
    """A BOLD near-black wheel with a bright keyline ring + a steel hub plate.
    Static by design: on this skin the SCANNER carries all the motion, so the
    wheels stay calm and the eye locks onto the pulsing screen above centre."""
    pygame.draw.circle(surf, WHEEL_KEY, (cx, cy), r + 1)
    pygame.draw.circle(surf, WHEEL_DARK, (cx, cy), r)
    pygame.draw.circle(surf, WHEEL_HUB, (cx, cy), r - 3)
    pygame.draw.circle(surf, WHEEL_DARK, (cx, cy), 1)


def build(wing_angle_deg):
    surf = _new()
    ph = _phase(wing_angle_deg)
    level = _SCAN_LEVEL[ph]
    sweep_t = _SWEEP_T[ph]

    # ── SQUARED basket: a clean rectangle (NOT flared) on two wheels ──────────
    # Wider than tall, vertical sides, slightly rounded corners. The squared
    # mass is the whole point: it separates this cart from the flared-trolley
    # silhouette at a glance. Centred so the (32,44) collision circle sits
    # inside the dominant mass.
    bw, bh = 40, 26
    basket = pygame.Rect(0, 0, bw, bh)
    basket.center = (BCX, BCY + 1)

    # teal-tinted cargo sitting IN the basket, drawn first so the basket front
    # rail overlaps it and it reads as goods inside the cart (and harmonises
    # with Pip's parcel, which hangs just below centre).
    cargo = pygame.Rect(0, 0, bw - 14, bh - 10)
    cargo.center = (BCX, basket.top + (bh - 10) // 2 + 2)
    _vbanded_rect(surf, cargo, CARGO_HI, CARGO, CARGO_LO, radius=2)
    pygame.draw.line(surf, CARGO_HI, (cargo.x + 2, cargo.y + 1),
                     (cargo.right - 3, cargo.y + 1), 1)

    # BOLD filled steel basket — vertical value band. Load-bearing read.
    _vbanded_rect(surf, basket, BODY_HI, BODY_MID, BODY_LO, radius=4)
    pygame.draw.rect(surf, BODY_EDGE, basket, 2, border_radius=4)

    # fat bright top rail across the open mouth + 3 suggested verticals. These
    # are heavy enough to hint 'basket' but the filled mass carries the read if
    # they blur at true 40px.
    pygame.draw.line(surf, BODY_HI, (basket.x + 2, basket.top + 2),
                     (basket.right - 3, basket.top + 2), 3)
    for fx in (-11, 0, 11):
        x = BCX + fx
        pygame.draw.line(surf, BODY_LO, (x, basket.top + 4), (x, basket.bottom - 3), 2)
        pygame.draw.line(surf, BODY_HI, (x - 1, basket.top + 4), (x - 1, basket.bottom - 3), 1)
    # one mid horizontal band so the steel reads as a panelled basket
    pygame.draw.line(surf, BODY_HI, (basket.x + 2, BCY + 2),
                     (basket.right - 3, BCY + 2), 1)

    # ── handle bar rising from the back, carrying the SCREEN on a stick ───────
    # A short vertical post off the top-right of the basket lifts the screen
    # ABOVE centre. The post is bold steel so the "screen on a stick" profile
    # holds at 40px.
    post_x = basket.right - 6
    post_top = basket.top - 16
    pygame.draw.line(surf, BODY_LO, (post_x, basket.top), (post_x, post_top + 2), 4)
    pygame.draw.line(surf, BODY_HI, (post_x - 1, basket.top), (post_x - 1, post_top + 2), 2)

    # ── the SCREEN panel: a flat teal-glow rectangle jutting FORWARD ──────────
    # This is the tell. It sits above centre, leaning toward the flight
    # direction (left). The baked outer glow blooms at night; the scan bar +
    # highlight sweep cycle across the 4 frames.
    sw, sh = 22, 15
    screen = pygame.Rect(0, 0, sw, sh)
    screen.center = (BCX - 1, post_top + 1)        # juts forward off the post

    # outer teal bloom first (additive) so the steel body overlaps its inner
    # edge and the glow reads as light spilling OFF the glass.
    _glow_bloom(surf, screen, SCREEN_CORE, 0.55 + 0.45 * level)

    # teal bezel + deep glass base
    pygame.draw.rect(surf, SCREEN_FRAME, screen.inflate(3, 3), border_radius=4)
    pygame.draw.rect(surf, SCREEN_DARK, screen, border_radius=3)

    # the lit glass: brightness ramps with the scanner level so the whole panel
    # pulses with the blink (off-pose stays a dim teal, never fully black, so
    # the screen never disappears from the silhouette).
    glow_col = _lerp(SCREEN_DIM, SCREEN_CORE, max(0.18, level))
    glass = screen.inflate(-4, -4)
    pygame.draw.rect(surf, glow_col, glass, border_radius=2)

    # SCAN BAR — a bright horizontal bar across the glass whose value is the
    # pulse. At peak it is near-white hot; off-pose it vanishes. This is the
    # grayscale-proof tell.
    if level > 0.05:
        bar_col = _lerp(SCREEN_CORE, SCAN_HOT, level)
        by = glass.top + glass.h // 2
        bar = pygame.Rect(glass.x + 1, by - 1, glass.w - 2, 3)
        bar_surf = pygame.Surface((bar.w, bar.h), pygame.SRCALPHA)
        bar_surf.fill((*bar_col, int(120 + 135 * level)))
        surf.blit(bar_surf, bar.topleft)
        # a hotter scan dot riding the bar, brightest at peak
        if level > 0.6:
            pygame.draw.circle(surf, SCAN_HOT, (glass.centerx, by), 2)

    # baked highlight SWEEP — a thin diagonal glass glint travelling left→right
    # across the four frames so the screen always feels alive even when the bar
    # is off.
    sx = glass.x + int(glass.w * sweep_t)
    pygame.draw.line(surf, SWEEP_HI, (sx, glass.top + 1), (sx - 3, glass.bottom - 1), 1)

    # ── two static wheels under the squared base ──────────────────────────────
    wy = basket.bottom + 5
    wr = 6
    _wheel(surf, BCX - 11, wy, wr)
    _wheel(surf, BCX + 11, wy, wr)
    # short steel struts from base corners down to each axle (fat, survive 40px)
    for sx0, wx in ((basket.x + 4, BCX - 11), (basket.right - 4, BCX + 11)):
        pygame.draw.line(surf, BODY_LO, (sx0, basket.bottom), (wx, wy), 3)
        pygame.draw.line(surf, BODY_HI, (sx0, basket.bottom), (wx, wy), 1)

    return surf
