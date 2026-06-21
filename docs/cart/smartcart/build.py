"""SMART CART — secret legendary-tier flyer skin concept.

The AI self-checkout cart (Caper / Amazon Dash idiom) replaces Pip: a sleek
SQUARED basket on two bold dark wheels, topped by a slim POST that cantilevers
a flat rectangular SCREEN forward over the front of the basket — a self-checkout
TERMINAL, a "tablet on a stick", not a robot head. The screen sits lifted off
the body with a sliver of post showing beneath it, so the eye reads terminal,
never helmet. No other cart concept pairs a squared (non-flared) basket with a
cantilevered emissive terminal screen, so that silhouette reads INSTANTLY as a
high-tech cart at 40px.

There are NO wings and NO live particles. The signature 4-frame tell is a
whole-screen VALUE PULSE: the glass luminosity steps hot → dim → hot → dark
across the four poses (a baked teal-glow ramp). The PANEL'S OWN BRIGHTNESS is
the motion — a pure value pulse, the strongest grayscale tell of the cart set,
so the wheels can stay static and the silhouette never changes frame-to-frame.
At night an additive teal bloom around the screen lights up the upper steel and
spills into the dusk — the legendary-tier moment, near-invisible by day.

Contract mirrors game/animal_ufo.py so the winner lifts straight into a
production module:
  * `build(wing_angle_deg) -> pygame.Surface` — one flat 64x84 SRCALPHA frame;
    dominant basket mass centred at (BCX, BCY) = (32, 44); screen tell ABOVE
    centre; the 14px collision circle at (32,44) sits inside the basket mass.
  * 4 value-pulse frames driven by `_WING_ANGLES = (50, 20, -10, -40)`.
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
SCREEN_CORE  = (35, 214, 196)   # #23D6C4 teal glow core (hot floor of the ramp)
SCREEN_HOT   = (216, 255, 250)  # near-white glass at peak luminosity
SCREEN_DARK  = (9, 58, 56)      # deep glass base under the glow
SCREEN_FLOOR = (16, 78, 76)     # dim-but-never-black dark floor (f3)
SCAN_HOT     = (210, 255, 248)  # secondary scan-bar accent at peak
POST_HI      = (208, 222, 230)  # lit edge of the cantilever post
POST_LO      = (120, 140, 154)  # shadow edge of the post (under the screen)

WHEEL_DARK  = (43, 49, 56)      # #2B3138 near-black tyre
WHEEL_KEY   = (236, 244, 248)   # bright keyline ring — pops wheels on night sky
WHEEL_HUB   = (188, 204, 214)   # steel hub plate

CARGO       = (96, 196, 210)    # cool teal-tinted cargo so it reads as the
CARGO_HI    = (170, 232, 238)   # cart's own goods, not a warm foreign block
CARGO_LO    = (52, 132, 150)


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _phase(angle_deg):
    """Map a wing angle (50→-40) to a 0..3 pulse step. The glass luminosity
    ramps hot → dim → hot → dark one notch per pose; that whole-screen value
    pulse reads as the cart's AI 'thinking', the way a real self-checkout
    terminal blinks while it works."""
    return int(round((50 - angle_deg) / 30.0)) % 4


# Whole-screen luminosity ramp across the 4 poses. f0 hot (near-white glass),
# f1 dim, f2 hot, f3 dark floor — an unmistakable light → dark → light → dark
# beat that survives grayscale because it is pure value, not hue. The off pose
# (f3) is a pure DIM of the same screen: no new internal shapes, so the
# silhouette never changes frame-to-frame.
_GLASS_LEVEL = (1.0, 0.40, 0.80, 0.0)    # hot → dim → hot → dark floor
# Secondary scan-bar accent rides the same beat but is demoted: faint on dim
# poses, gone on the dark floor. The pulse, not the bar, is the tell.
_BAR_LEVEL   = (0.85, 0.30, 0.65, 0.0)


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
    """Bake a soft additive teal halo around the screen so it BLOOMS on a dark
    night sky (the legendary moment) while staying near-invisible on a bright
    day sky — additive light simply has nowhere to go against pale blue but
    lights up dramatically against dusk. The halo deliberately overshoots the
    screen so it spills onto the upper steel body and a few px into the sky;
    strength scales with the glass level so the bloom pulses with the beat."""
    if strength <= 0.0:
        return
    pad = 18
    g = pygame.Surface((rect.w + pad * 2, rect.h + pad * 2), pygame.SRCALPHA)
    cx, cy = g.get_width() // 2, g.get_height() // 2
    # wide soft outer falloff (spills into sky + onto the upper steel body),
    # tightening to a bright inner core hugging the glass — many low-alpha rings
    # add to a smooth additive bloom rather than a hard ring. The outermost,
    # widest rings are what light up the steel and the dusk at night; against a
    # pale day sky the same additive light has nowhere to go, so it stays
    # restrained without any biome branch.
    rings = (
        (rect.w + 32, rect.h + 32, 16),
        (rect.w + 26, rect.h + 26, 22),
        (rect.w + 20, rect.h + 20, 30),
        (rect.w + 14, rect.h + 14, 40),
        (rect.w + 9,  rect.h + 9,  54),
        (rect.w + 4,  rect.h + 4,  72),
    )
    for w, h, a in rings:
        rr = pygame.Rect(0, 0, w, h)
        rr.center = (cx, cy)
        pygame.draw.rect(g, (*color, int(a * strength)), rr,
                         border_radius=max(5, h // 3))
    surf.blit(g, (rect.x - pad, rect.y - pad), special_flags=pygame.BLEND_RGBA_ADD)


def _wheel(surf, cx, cy, r):
    """A BOLD near-black wheel with a bright keyline ring + a steel hub plate.
    Static by design: on this skin the VALUE PULSE carries all the motion, so
    the wheels stay calm and the eye locks onto the pulsing screen above."""
    pygame.draw.circle(surf, WHEEL_KEY, (cx, cy), r + 1)
    pygame.draw.circle(surf, WHEEL_DARK, (cx, cy), r)
    pygame.draw.circle(surf, WHEEL_HUB, (cx, cy), r - 3)
    pygame.draw.circle(surf, WHEEL_DARK, (cx, cy), 1)


def build(wing_angle_deg):
    surf = _new()
    ph = _phase(wing_angle_deg)
    level = _GLASS_LEVEL[ph]
    bar = _BAR_LEVEL[ph]

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
    # with Pip's parcel, which hangs just below centre). Kept LOW so it never
    # fights the screen above.
    cargo = pygame.Rect(0, 0, bw - 14, bh - 12)
    cargo.center = (BCX, basket.top + (bh - 12) // 2 + 4)
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

    # ── POST: a slim mast rising from the back, cantilevering the screen ──────
    # The post is the thing that makes this a TERMINAL, not a helmet: the screen
    # is lifted clear of the body on it and tilts FORWARD over the front of the
    # basket. A sliver of post stays visible beneath the screen so the eye reads
    # "tablet on a stick". Two-tone so it doesn't read as a flat stick.
    post_x = basket.right - 9
    post_top = basket.top - 14          # screen rides ABOVE the basket top
    pygame.draw.line(surf, POST_LO, (post_x, basket.top - 1), (post_x, post_top + 4), 4)
    pygame.draw.line(surf, POST_HI, (post_x - 1, basket.top - 1), (post_x - 1, post_top + 4), 2)

    # ── the SCREEN: a flat teal terminal cantilevered FORWARD off the post ────
    # This is the tell. It sits ABOVE centre, lifted off the body and pushed
    # toward the flight direction (left) so it overhangs the front of the
    # basket. The additive bloom blooms at night; the whole glass luminosity
    # pulses across the 4 frames. A small mounting neck links post→screen so the
    # cantilever reads, and the gap beneath the screen shows a sliver of post.
    sw, sh = 23, 14
    screen = pygame.Rect(0, 0, sw, sh)
    # forward (leftward) cantilever: screen centre sits left of the post, and
    # ABOVE the basket top with a clear air gap (the lift off the body).
    screen.center = (BCX - 3, post_top - 1)

    # mounting neck: a stubby diagonal arm from the post up to the screen's back
    # corner, so the screen visibly hangs off the mast rather than floating.
    neck_top = (screen.right - 3, screen.bottom - 2)
    pygame.draw.line(surf, POST_LO, (post_x, post_top + 3), neck_top, 4)
    pygame.draw.line(surf, POST_HI, (post_x - 1, post_top + 3), (neck_top[0] - 1, neck_top[1]), 2)

    # ── night bloom (additive) ── stamped BEFORE the bezel so the steel body
    # and the dusk receive the spill. Pulses with the glass level; on day the
    # pale sky swallows it (restrained), on night it lights up the upper steel.
    _glow_bloom(surf, screen, SCREEN_CORE, 0.30 + 0.70 * level)

    # teal bezel + deep glass base — the bezel carries the DAY silhouette so the
    # screen never goes flat / flashlight-glitchy when the bloom is dialled down.
    pygame.draw.rect(surf, SCREEN_FRAME, screen.inflate(3, 3), border_radius=4)
    pygame.draw.rect(surf, SCREEN_DARK, screen, border_radius=3)

    # the lit glass — WHOLE-PANEL luminosity is the pulse. Hot poses go toward
    # near-white; the dim pose is mid teal; the dark floor (f3) is a dim teal
    # that never goes black, so the screen stays in the silhouette and gains NO
    # new internal shapes (pure dimming).
    glass = screen.inflate(-4, -4)
    if level >= 0.99:
        glass_col = SCREEN_HOT
    elif level <= 0.01:
        glass_col = SCREEN_FLOOR
    elif level >= 0.5:
        glass_col = _lerp(SCREEN_CORE, SCREEN_HOT, (level - 0.5) / 0.5)
    else:
        glass_col = _lerp(SCREEN_FLOOR, SCREEN_CORE, level / 0.5)
    pygame.draw.rect(surf, glass_col, glass, border_radius=2)

    # a fixed bezel inner highlight on the top edge — present every frame so the
    # screen EDGE always reads (day silhouette) regardless of the pulse level.
    pygame.draw.line(surf, SCREEN_FRAME, (glass.x, glass.top - 1),
                     (glass.right - 1, glass.top - 1), 1)

    # SECONDARY scan-bar accent — demoted: a faint horizontal tick that rides
    # the same beat but is no longer the tell. Gone on the dark floor.
    if bar > 0.05:
        bar_col = _lerp(SCREEN_CORE, SCAN_HOT, bar)
        by = glass.top + glass.h // 2
        b = pygame.Rect(glass.x + 1, by - 1, glass.w - 2, 2)
        bsurf = pygame.Surface((b.w, b.h), pygame.SRCALPHA)
        bsurf.fill((*bar_col, int(70 + 90 * bar)))
        surf.blit(bsurf, b.topleft)

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
