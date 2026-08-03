#!/usr/bin/env python3
"""
arc_count round 7 — arc to macaw center, DAY COMPLETE left, day N in header.

Applies the approved rule-set to the round-3 sun_arc visual:
  - Weather determines the Skybit background only.
  - Events shown: NEWBIE PERIOD (0.0–0.20), GEYSER (~0.167), CLOWN (0.403),
    RAIN (0.430), SNOWSTORM (0.820), DAY COMPLETE (1.0).
  - Nothing past the death point reveals future events — maximum mystery.

Baseline removals vs round-3:
  - Phase chips (GOLDEN/SUNSET/DUSK/NIGHT) — weather labels removed.
  - GENIE glyph and phase — not in the approved event list.
  - "STILL AHEAD" text — spoils mystery.
  - "GENIE LAMP" / "CLOWN GAUNTLET" ground labels — spoils mystery.
  - Bottom glyph disc legend row — shows all event colors and names.
  - "DAY" / "PREDAWN · SUNRISE" ground text — weather / time-of-day.

Baseline additions:
  - NEWBIE PERIOD zone arc (p=0.0–0.20) along the event rail.
  - Upgraded DAY COMPLETE terminal: gold diamond with ink ring.

Direction C changes (arc_count):
  - Glyphs past death are ink-filled silhouettes: shape visible, identity hidden.
  - NEWBIE PERIOD label uses full text.
  - DAY COMPLETE prominent sun-disc glow at right terminus.
"""
import os
import math
import random

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.biome import palette_for_phase
from game.draw import lerp_color, lerp_color_multi
from game import parrot as _parrot

# Phase constants inlined (game modules have been refactored)
THERMAL_START_PHASE = 50.0 / 300.0   # ≈ 0.167
THERMAL_END_PHASE   = 112.0 / 300.0  # ≈ 0.373
SNOW_STORM_CENTER   = 0.82
LATE_GAME_PILLAR    = 55
CLOWN_START_PILLAR  = 65
PHASE_BOUNDARIES = [
    (0.00, "DAY"),
    (0.18, "GOLDEN HOUR"),
    (0.32, "SUNSET"),
    (0.48, "DUSK"),
    (0.62, "NIGHT"),
    (0.78, "PREDAWN"),
    (0.90, "SUNRISE"),
]

W, H = 360, 640
HORIZON_Y = 430
CX, CY, R = 180, 430, 175
R_INNER = 159          # event-glyph rail, inside the arc
R_LABEL = 205          # phase-name chips, outside the arc
SS = 3

ROOT = "/home/user/skybit"
FONT_PATH = "/home/user/skybit/game/assets/LiberationSans-Bold.ttf"
_fonts: dict = {}


def font(size):
    if size not in _fonts:
        _fonts[size] = pygame.font.Font(FONT_PATH, size)
    return _fonts[size]


# ── palette ──────────────────────────────────────────────────────────────────
INK = (6, 8, 14)
CREAM = (246, 240, 230)
GOLD = (255, 206, 92)
DEEP_BROWN = (46, 30, 20)
SCRIM = (26, 22, 34)
SLATE = (58, 62, 82)          # what the unearned sky is pulled toward
COOL = (150, 168, 196)

NEWBIE_C = (240, 180, 120)
GEYSER_C = (146, 232, 255)
CLOWN_C = (255, 118, 196)
RAIN_C = (150, 190, 255)
SNOW_C = (222, 244, 255)

# Sunlit dune on top, shadowed dune below: the split gives the band two text
# treatments that both clear AA instead of one that clears neither.
GROUND_STOPS = [
    (0.00, (222, 178, 118)),
    (0.30, (206, 160, 102)),
    (0.44, (150, 102, 66)),
    (0.70, (92, 60, 42)),
    (1.00, (42, 28, 22)),
]

# Mock run
DEATH_PHASE = 0.184
DEATH_PILLAR = 25
DAY_N = 1
TIME_ALIVE = 47
PHASE_LABEL = "DAY"

NEWBIE_END_PHASE = 0.20
GEYSER_SPAN = (THERMAL_START_PHASE, THERMAL_END_PHASE)
CLOWN_PHASE = 0.403
RAIN_PHASE = 0.430
SNOW_PHASE = SNOW_STORM_CENTER
CLOWN_ZONE = (0.38, 0.42)   # bracket around CLOWN_PHASE 0.403
RAIN_ZONE  = (0.42, 0.46)   # bracket around RAIN_PHASE 0.430
SNOW_ZONE  = (0.80, 0.85)   # bracket around SNOW_PHASE 0.820
BEST_PHASE   = 0.31   # personal best run, slightly past current death
BEST_PILLAR  = 40     # personal best pillar reached
BEST_TIME    = 78     # personal best seconds
CLOWN_PILLAR = 65     # first sealed event's pillar position

DEATH_PALETTE = palette_for_phase(DEATH_PHASE)
STAR_FLOOR_PHASE = 0.54       # nothing starry may appear before the dusk band


# ── the single phase→screen mapping ──────────────────────────────────────────
# Every dome column, arc point, tick, glyph and label goes through this pair.
# Round 1 ran the dome on a linear x and the arc on a raw cosine; the two
# disagreed by up to 16px, which is more than a tick is wide.

EASE_P = 0.652                # phase**EASE_P: first 20% of the day → 35% of arc


def ease(p):
    return max(0.0, min(1.0, p)) ** EASE_P


def unease(u):
    return max(0.0, min(1.0, u)) ** (1.0 / EASE_P)


def pos_u(u, radius=R):
    a = math.pi * (1.0 - u)
    return (CX + radius * math.cos(a), CY - radius * math.sin(a))


def arc_pos(p, radius=R):
    return pos_u(ease(p), radius)


def radial_unit(p):
    """Outward-pointing unit vector at a phase, in screen coords (y down)."""
    a = math.pi * (1.0 - ease(p))
    return (math.cos(a), -math.sin(a))


def phase_at_x(x):
    """Exact inverse of the mapping — what time of day a dome column shows."""
    t = (x - CX) / R
    if t <= -1.0:
        return 0.0
    if t >= 1.0:
        return 1.0
    return unease(1.0 - math.acos(t) / math.pi)


def in_label_band(p):
    """Only the upper 120° of the arc has room for a horizontal pill. Below
    that the arc is steep, the phases are compressed and a chip would sit on
    top of its own neighbours."""
    return 30.0 <= 180.0 * (1.0 - ease(p)) <= 150.0


DEATH_X, DEATH_Y = arc_pos(DEATH_PHASE)
STAR_FLOOR_X = arc_pos(STAR_FLOOR_PHASE)[0]


# ── veil ─────────────────────────────────────────────────────────────────────

def veil_strength(x):
    """0 across the sky that was flown, ramping to 1 across the sky that
    wasn't. The 13px ramp keeps it an atmospheric front rather than a seam."""
    d = x - DEATH_X
    if d <= 0:
        return 0.0
    k = min(1.0, d / 13.0)
    # Deepens with distance so the far end of the day reads as genuinely unlit.
    return k * (0.88 + 0.12 * min(1.0, d / 150.0))


def veil(c, k):
    """Chroma ×0.5 and value pulled toward a neutral slate at full strength."""
    if k <= 0.0:
        return (int(c[0]), int(c[1]), int(c[2]))
    lum = 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    r = c[0] + (lum - c[0]) * 0.5 * k
    g = c[1] + (lum - c[1]) * 0.5 * k
    b = c[2] + (lum - c[2]) * 0.5 * k
    v = 1.0 - 0.48 * k
    r, g, b = r * v, g * v, b * v
    r += (SLATE[0] - r) * 0.22 * k
    g += (SLATE[1] - g) * 0.22 * k
    b += (SLATE[2] - b) * 0.22 * k
    return (max(0, min(255, int(r))), max(0, min(255, int(g))),
            max(0, min(255, int(b))))


# ── text / chrome helpers ────────────────────────────────────────────────────

def text(surf, s, size, center=None, midleft=None, midright=None,
         color=CREAM, shadow=(0, 0, 0, 150), track=0):
    f = font(size)
    if track:
        # Manual letter-spacing keeps headers reading as signage; pygame has no
        # tracking control.
        glyphs = [f.render(ch, True, color) for ch in s]
        tw = sum(g.get_width() for g in glyphs) + track * (len(s) - 1)
        th = f.get_height()
        img = pygame.Surface((max(1, tw), th), pygame.SRCALPHA)
        x = 0
        for ch, g in zip(s, glyphs):
            img.blit(g, (x, 0))
            x += g.get_width() + track
    else:
        img = f.render(s, True, color)
    rect = img.get_rect()
    if center:
        rect.center = center
    elif midleft:
        rect.midleft = midleft
    elif midright:
        rect.midright = midright
    if shadow:
        sh = img.copy()
        sh.fill((*shadow[:3], 255), special_flags=pygame.BLEND_RGBA_MULT)
        sh.set_alpha(shadow[3])
        surf.blit(sh, (rect.x + 1, rect.y + 1))
    surf.blit(img, rect)
    return rect


def chip(surf, rect, radius=6, fill=(18, 15, 24), alpha=234,
         border=CREAM, border_a=54):
    s = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(s, (*fill, alpha), s.get_rect(), border_radius=radius)
    if border_a:
        pygame.draw.rect(s, (*border, border_a), s.get_rect(), width=1,
                         border_radius=radius)
    surf.blit(s, rect.topleft)


def soft_glow(radius, color, peak=110, falloff=2.0):
    """Additive glow with the falloff baked into RGB.

    BLEND_ADD ignores the source alpha channel, so an alpha-ramped glow blits
    as a flat hard-edged disc. Premultiplying keeps the ramp.
    """
    size = radius * 2 + 2
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    c = radius + 1
    for r in range(radius, 0, -1):
        f = (1 - (r / radius) ** falloff) * (peak / 255.0)
        s_col = (int(color[0] * f), int(color[1] * f), int(color[2] * f), 255)
        pygame.draw.circle(s, s_col, (c, c), r)
    return s


def alpha_line(surf, rgba, p0, p1, width=1):
    """`surf` is an opaque Surface, so pygame.draw would ignore the alpha and
    stamp the colour at full strength. Route through a scratch layer."""
    lay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.line(lay, rgba, p0, p1, width)
    surf.blit(lay, (0, 0))


def add_ink(src, color=(6, 8, 14, 240), pad=2):
    """Dilated dark keyline — the only thing that guarantees a small sprite
    holds its silhouette over both a bright dune and a dark veiled sky."""
    mask = pygame.mask.from_surface(src, threshold=12)
    sil = mask.to_surface(setcolor=color, unsetcolor=(0, 0, 0, 0))
    out = pygame.Surface((src.get_width() + pad * 2, src.get_height() + pad * 2),
                         pygame.SRCALPHA)
    for dx in range(-pad, pad + 1):
        for dy in range(-pad, pad + 1):
            if dx or dy:
                out.blit(sil, (pad + dx, pad + dy))
    out.blit(src, (pad, pad))
    return out


# ── sky ──────────────────────────────────────────────────────────────────────

SKY_STOPS = [
    (0.00, DEATH_PALETTE["sky_top"]),
    (0.42, DEATH_PALETTE["sky_mid"]),
    (0.80, DEATH_PALETTE["sky_bot"]),
    (1.00, DEATH_PALETTE["horizon"]),
]


# A gentle vignette, centred on the flown quarter rather than on the canvas:
# it pulls the four corners down without touching the death point, which is
# the cheapest way to stop a cream-bright horizon competing with the subject.
VIG_C = (150, 250)
VIG_D = 290.0
VIG_S = 0.34


def vignette(x, y):
    d = math.hypot(x - VIG_C[0], y - VIG_C[1]) / VIG_D
    return 1.0 - VIG_S * min(1.0, d) ** 1.7


def sky_at(x, y):
    c = veil(lerp_color_multi(SKY_STOPS, y / (HORIZON_Y - 1)), veil_strength(x))
    v = vignette(x, y)
    return (int(c[0] * v), int(c[1] * v), int(c[2] * v))


def draw_dome(surf):
    """One sky — the death-phase sky — veiled column by column past the point
    the run ended."""
    column = [lerp_color_multi(SKY_STOPS, y / (HORIZON_Y - 1)) for y in range(HORIZON_Y)]
    for x in range(W):
        k = veil_strength(x)
        col = column if k <= 0.0 else [veil(c, k) for c in column]
        for y in range(HORIZON_Y):
            v = vignette(x, y)
            c = col[y]
            surf.set_at((x, y), (int(c[0] * v), int(c[1] * v), int(c[2] * v)))


def draw_clouds(surf):
    """Two lit cumulus in the flown wedge, one ghost bank in the veil.

    The lit pair is doing real work: it is most of the value energy that keeps
    the earned quarter of the sky ahead of the other three quarters at squint.
    """
    def puff(cx, cy, w, h, top, bot, alpha):
        s = pygame.Surface((w + 8, h + 8), pygame.SRCALPHA)
        lobes = [(w * 0.26, h * 0.62, w * 0.26, h * 0.36),
                 (w * 0.52, h * 0.44, w * 0.32, h * 0.44),
                 (w * 0.76, h * 0.62, w * 0.24, h * 0.32)]
        for lx, ly, lrx, lry in lobes:
            pygame.draw.ellipse(s, (*bot, alpha),
                                (lx - lrx + 4, ly - lry + 4, lrx * 2, lry * 2))
        for lx, ly, lrx, lry in lobes:
            pygame.draw.ellipse(s, (*top, alpha),
                                (lx - lrx + 4, ly - lry * 1.05 + 4,
                                 lrx * 2, lry * 1.5))
        pygame.draw.ellipse(s, (*bot, alpha),
                            (4, h * 0.72 + 4, w, h * 0.30))
        surf.blit(s, (cx - w // 2, cy - h // 2))

    puff(44, 194, 60, 28, (250, 234, 208), (232, 194, 156), 214)
    puff(32, 352, 68, 28, (252, 238, 214), (236, 200, 160), 224)
    puff(238, 172, 96, 34, (108, 114, 132), (86, 92, 110), 118)


def draw_ghost_night(surf):
    """The night the run never reached: faint stars and an unrisen moon, held
    strictly to phases at or past dusk so nothing starry shows over sunset."""
    rng = random.Random(20260731)
    lay = pygame.Surface((W, HORIZON_Y), pygame.SRCALPHA)
    placed = 0
    while placed < 160:
        x = rng.randrange(int(STAR_FLOOR_X) + 2, W)
        y = rng.randrange(78, HORIZON_Y - 40)
        p = phase_at_x(x)
        if p < STAR_FLOOR_PHASE:
            continue
        base = palette_for_phase(p)["star_alpha"]
        placed += 1
        if base < 8:
            continue
        depth = 1.0 - (y / (HORIZON_Y - 40)) * 0.5
        a = int((base / 235.0) * 78 * depth * rng.uniform(0.5, 1.0))
        if a < 8:
            continue
        r = 1 if rng.random() < 0.85 else 2
        pygame.draw.circle(lay, (226, 234, 250, a), (x, y), r)
    surf.blit(lay, (0, 0))

    mx, my = pos_u(ease(0.6438), 142)
    m = pygame.Surface((26, 26), pygame.SRCALPHA)
    pygame.draw.circle(m, (206, 216, 238, 118), (13, 13), 9)
    for dx, dy, cr in ((-3, -2, 2), (2, 3, 2), (0, 4, 1)):
        pygame.draw.circle(m, (186, 196, 220, 118), (13 + dx, 13 + dy), cr)
    # Punching the shadow disc with a zero-alpha fill carves the crescent
    # without needing to know the sky colour underneath.
    pygame.draw.circle(m, (0, 0, 0, 0), (19, 9), 9)
    surf.blit(m, (int(mx) - 13, int(my) - 13))


def draw_horizon_light(surf):
    hc = DEATH_PALETTE["horizon"]
    bloom = pygame.Surface((W, 28), pygame.SRCALPHA)
    for x in range(W):
        k = veil_strength(x)
        c = veil(hc, k)
        gain = 0.34 * (1.0 - 0.62 * k)
        for i in range(26):
            f = gain * (1 - i / 26) ** 2.0
            bloom.set_at((x, 25 - i), (int(c[0] * f), int(c[1] * f), int(c[2] * f), 255))
    surf.blit(bloom, (0, HORIZON_Y - 26), special_flags=pygame.BLEND_ADD)
    for x in range(W):
        c = veil(hc, veil_strength(x))
        surf.set_at((x, HORIZON_Y - 1), lerp_color(c, (255, 255, 255), 0.30))
        surf.set_at((x, HORIZON_Y), lerp_color(c, (40, 26, 18), 0.55))


def draw_ground(surf):
    h = H - HORIZON_Y
    for i in range(h):
        c = lerp_color_multi(GROUND_STOPS, i / (h - 1))
        pygame.draw.line(surf, c, (0, HORIZON_Y + i), (W - 1, HORIZON_Y + i))
    rng = random.Random(4242)
    for k in range(4):
        y = HORIZON_Y + 5 + k * 4
        amp = 2.0 - k * 0.3
        col = lerp_color(lerp_color_multi(GROUND_STOPS, (y - HORIZON_Y) / h),
                         (255, 228, 184), 0.26 - k * 0.05)
        pts = []
        ph = rng.uniform(0, 6)
        for x in range(0, W + 1, 6):
            pts.append((x, y + math.sin(x * 0.035 + ph + k) * amp))
        pygame.draw.lines(surf, col, False, pts, 1)


# ── event glyphs (shared by the rail, the teaser rows and the legend) ─────────

def g_geyser(s, cx, cy, r, col=GEYSER_C):
    body = [(cx - r * 0.30, cy + r), (cx - r * 0.16, cy - r * 0.15),
            (cx - r * 0.42, cy - r * 0.75), (cx, cy - r * 1.05),
            (cx + r * 0.42, cy - r * 0.75), (cx + r * 0.16, cy - r * 0.15),
            (cx + r * 0.30, cy + r)]
    pygame.draw.polygon(s, (*col, 255), body)
    pygame.draw.polygon(s, (255, 255, 255, 210), body, max(1, int(r * 0.18)))
    pygame.draw.circle(s, (255, 255, 255, 230), (int(cx - r * 0.72), int(cy - r * 0.95)), max(1, int(r * 0.20)))
    pygame.draw.circle(s, (255, 255, 255, 200), (int(cx + r * 0.78), int(cy - r * 0.60)), max(1, int(r * 0.16)))


def g_clown(s, cx, cy, r, col=CLOWN_C):
    d = [(cx, cy - r), (cx + r * 0.82, cy), (cx, cy + r), (cx - r * 0.82, cy)]
    pygame.draw.polygon(s, (*col, 255), d)
    left = [(cx, cy - r), (cx, cy + r), (cx - r * 0.82, cy)]
    pygame.draw.polygon(s, (255, 226, 118, 250), left)
    pygame.draw.polygon(s, (255, 255, 255, 215), d, max(1, int(r * 0.16)))
    pygame.draw.circle(s, (255, 255, 255, 235), (int(cx), int(cy)), max(1, int(r * 0.20)))


def g_rain(s, cx, cy, r, col=RAIN_C):
    drop = [(cx, cy - r * 1.05), (cx + r * 0.68, cy + r * 0.28),
            (cx + r * 0.34, cy + r * 0.86), (cx - r * 0.34, cy + r * 0.86),
            (cx - r * 0.68, cy + r * 0.28)]
    pygame.draw.polygon(s, (*col, 255), drop)
    pygame.draw.polygon(s, (235, 246, 255, 220), drop, max(1, int(r * 0.16)))
    pygame.draw.line(s, (255, 255, 255, 200), (cx - r * 0.22, cy + r * 0.10),
                     (cx - r * 0.30, cy + r * 0.52), max(1, int(r * 0.18)))


def g_snow(s, cx, cy, r, col=SNOW_C):
    w = max(1, int(r * 0.22))
    for k in range(6):
        a = math.radians(k * 60)
        ex, ey = cx + math.cos(a) * r, cy + math.sin(a) * r
        pygame.draw.line(s, (*col, 255), (cx, cy), (ex, ey), w)
        bx, by = cx + math.cos(a) * r * 0.62, cy + math.sin(a) * r * 0.62
        for sgn in (-1, 1):
            b = a + sgn * math.radians(48)
            pygame.draw.line(s, (*col, 230), (bx, by),
                             (bx + math.cos(b) * r * 0.36, by + math.sin(b) * r * 0.36), w)
    pygame.draw.circle(s, (255, 255, 255, 245), (int(cx), int(cy)), max(1, int(r * 0.24)))


# Silhouettes chosen to survive a colourblind read and a 1× downscale: a tall
# narrow plume, a diamond, a teardrop, a six-point star.
GLYPHS = [
    (g_geyser, "GEYSER", GEYSER_C),
    (g_clown, "CLOWN", CLOWN_C),
    (g_rain, "RAIN", RAIN_C),
    (g_snow, "SNOWSTORM", SNOW_C),
]


def stamp_glyph(dst, fn, cx, cy, r, col, ink_pad=2):
    """Render a glyph onto its own surface so it can carry a dilated ink
    keyline — colour alone does not survive a greyscale or squint read."""
    side = int(r * 5) + 12
    tmp = pygame.Surface((side, side), pygame.SRCALPHA)
    fn(tmp, side / 2, side / 2, r, col)
    out = add_ink(tmp, (6, 8, 14, 235), ink_pad)
    dst.blit(out, (int(cx - out.get_width() / 2), int(cy - out.get_height() / 2)))


# ── arc overlay (drawn at SS, downscaled once) ───────────────────────────────

def draw_overlay(ss):
    k = SS
    u_death = ease(DEATH_PHASE)

    def PU(u, radius=R):
        x, y = pos_u(u, radius)
        return (x * k, y * k)

    # Event rail: dotted, warm where it was flown, near-invisible in the veil.
    for i in range(0, 181):
        u = i / 180
        x, y = PU(u, R_INNER)
        if u <= u_death:
            col = (255, 226, 176, 108)
        else:
            col = (176, 190, 214, 44)
        pygame.draw.circle(ss, col, (int(x), int(y)), int(0.9 * k))

    # AHEAD run — thin, cool, ~35% alpha, no glow, no keyline. It has to read
    # as a plan, not an achievement.
    # The 3× downscale roughly halves a hairline's effective density, so the
    # authored alpha is set high enough to LAND at ~35% once composited.
    u_ahead_start = u_death + 12.0 / (R * math.pi)   # skip macaw half-width
    # Pass 1: wide dim haze — fades from death toward right terminus
    for _ai in range(100):
        _u0 = u_ahead_start + (1.0 - u_ahead_start) * _ai / 100
        _u1 = u_ahead_start + (1.0 - u_ahead_start) * (_ai + 1) / 100
        _a = int(55 - 38 * (_ai / 99))
        pygame.draw.line(ss, (*COOL, _a), PU(_u0), PU(_u1), max(1, int(2.8 * k)))
    # Pass 2: dashed bright centerline, fading as it recedes
    for _di in range(90):
        if _di % 3 == 2:
            continue
        _u0 = u_ahead_start + (1.0 - u_ahead_start) * _di / 90
        _u1 = u_ahead_start + (1.0 - u_ahead_start) * (_di + 0.65) / 90
        _a = int(130 - 90 * (_di / 89))
        pygame.draw.line(ss, (*COOL, _a), PU(_u0), PU(_u1), max(1, int(1.1 * k)))

    # Phase ticks at TRUE phases: the eased mapping compresses early morning,
    # and the uneven tick spacing is the only thing that admits it.
    for frac, name in PHASE_BOUNDARIES:
        if frac <= 0.0:
            continue
        ux, uy = radial_unit(frac)
        x, y = arc_pos(frac)
        a = ((x - ux * 6.0) * k, (y - uy * 6.0) * k)
        b = ((x + ux * 7.0) * k, (y + uy * 7.0) * k)
        pygame.draw.line(ss, (10, 8, 14, 120), (a[0], a[1] + 1.2 * k),
                         (b[0], b[1] + 1.2 * k), int(2.2 * k))
        pygame.draw.line(ss, (196, 208, 228, 150), a, b, int(1.6 * k))

    # DAY COMPLETE — scaled-up gold diamond
    x, y = PU(1.0)
    pygame.draw.polygon(ss, (*INK, 200),
                        [(x, y - 5.5 * k), (x + 4.3 * k, y), (x, y + 5.5 * k),
                         (x - 4.3 * k, y)])
    pygame.draw.polygon(ss, (255, 206, 92, 240),
                        [(x, y - 4.1 * k), (x + 3.2 * k, y), (x, y + 4.1 * k),
                         (x - 3.2 * k, y)])
    pygame.draw.polygon(ss, (*INK, 180),
                        [(x, y - 4.1 * k), (x + 3.2 * k, y), (x, y + 4.1 * k),
                         (x - 3.2 * k, y)], int(2.0 * k))

    # NEWBIE PERIOD zone (p=0.0–0.20): warm arc on R_INNER, always in the lit side.
    u_nb_end = ease(NEWBIE_END_PHASE)
    pts_nb = [PU(u_nb_end * i / 40, R_INNER) for i in range(41)]
    pygame.draw.lines(ss, (*NEWBIE_C, 160), False, pts_nb, int(2.2 * k))
    ux_nb, uy_nb = radial_unit(NEWBIE_END_PHASE)
    xnb, ynb = arc_pos(NEWBIE_END_PHASE, R_INNER)
    pygame.draw.line(ss, (*NEWBIE_C, 190),
                     ((xnb - ux_nb * 4.2) * k, (ynb - uy_nb * 4.2) * k),
                     ((xnb + ux_nb * 4.2) * k, (ynb + uy_nb * 4.2) * k), int(2.0 * k))

    # Geyser span bracket — the run started INSIDE it, so the bracket is split:
    # lit for the part that was flown, veiled for the part that wasn't.
    ub = (ease(GEYSER_SPAN[0]), ease(GEYSER_SPAN[1]))
    for seg_a, seg_b, col, wid in (
            (ub[0], min(u_death, ub[1]), (*GEYSER_C, 235), 2.2),
            (min(u_death, ub[1]), ub[1], (150, 176, 196, 92), 1.6)):
        if seg_b - seg_a <= 1e-4:
            continue
        pts = [PU(seg_a + (seg_b - seg_a) * i / 40, R_INNER) for i in range(41)]
        if col[3] > 150:
            pygame.draw.lines(ss, (10, 8, 14, 130), False,
                              [(px, py + 1.2 * k) for px, py in pts], int((wid + 1.2) * k))
        pygame.draw.lines(ss, col, False, pts, int(wid * k))
    for p, bright in ((GEYSER_SPAN[0], True), (GEYSER_SPAN[1], False)):
        ux, uy = radial_unit(p)
        x, y = arc_pos(p, R_INNER)
        col = (*GEYSER_C, 235) if bright else (150, 176, 196, 110)
        pygame.draw.line(ss, col, ((x - ux * 4.2) * k, (y - uy * 4.2) * k),
                         ((x + ux * 4.2) * k, (y + uy * 4.2) * k), int(2.0 * k))

    # Event glyphs at true angular positions. Rain rides a tighter radius: it
    # sits 0.027 phase from the clown gauntlet and would otherwise collide.
    ring_items = [
        (GEYSER_SPAN[0], R_INNER - 24, g_geyser, GEYSER_C),
        (CLOWN_PHASE, R_INNER, g_clown, CLOWN_C),
        (RAIN_PHASE, R_INNER - 22, g_rain, RAIN_C),
        (SNOW_PHASE, R_INNER, g_snow, SNOW_C),
    ]
    for p, rad, fn, col in ring_items:
        x, y = arc_pos(p, rad)
        if p > DEATH_PHASE:
            # Zone bracket — a short arc segment marking the event's territory
            _zone_map = {
                CLOWN_PHASE: CLOWN_ZONE,
                RAIN_PHASE:  RAIN_ZONE,
                SNOW_PHASE:  SNOW_ZONE,
            }
            _z0, _z1 = _zone_map.get(p, (max(0.0, p - 0.02), min(1.0, p + 0.02)))
            _pts_z = []
            for _zi in range(16):
                _zp = _z0 + (_z1 - _z0) * _zi / 15
                _zx, _zy = arc_pos(_zp, R_INNER)
                _pts_z.append((int(_zx * k), int(_zy * k)))
            pygame.draw.lines(ss, (*col, 55), False, _pts_z, max(1, int(1.3 * k)))
            # Zone end ticks
            for _zt in (_z0, _z1):
                _ux_z, _uy_z = radial_unit(_zt)
                _ztx, _zty = arc_pos(_zt, R_INNER)
                pygame.draw.line(ss, (*col, 70),
                                 (int((_ztx - _ux_z * 3.5) * k), int((_zty - _uy_z * 3.5) * k)),
                                 (int((_ztx + _ux_z * 3.5) * k), int((_zty + _uy_z * 3.5) * k)),
                                 max(1, int(1.2 * k)))
            # Connector for off-rail glyphs
            if rad != R_INNER:
                ax, ay = arc_pos(p, R_INNER)
                pygame.draw.line(ss, (*col, 45), (int(ax * k), int(ay * k)),
                                 (int(x * k), int(y * k)), max(1, int(0.8 * k)))
        else:
            if rad != R_INNER:
                ax, ay = arc_pos(p, R_INNER)
                pygame.draw.line(ss, (*col, 120), (ax * k, ay * k), (x * k, y * k),
                                 int(1.0 * k))
            stamp_glyph(ss, fn, x * k, y * k, 5.2 * k, col, ink_pad=int(1.4 * k))

    # TRAVELLED run last, so nothing crosses it: gold core between two 1px ink
    # keylines. The keyline is what buys it >110 L separation over a bright
    # morning dune AND over the veiled slate at the same time.
    steps = 96
    for pass_ink in (True, False):
        for i in range(steps):
            u0 = u_death * i / steps
            u1 = u_death * (i + 1) / steps
            t = i / steps
            core = 3.0 + 2.4 * t ** 1.4
            if pass_ink:
                # 2px a side, not 1. A 1px keyline authored at 3× straddles the
                # output grid and averages to a mid-grey wherever it lands off
                # a pixel boundary — measured, it never got darker than L=160
                # against a core at L=245. 2px always lands one clean ink pixel.
                pygame.draw.line(ss, (*INK, 250), PU(u0), PU(u1),
                                 int((core + 4.0) * k))
            else:
                col = lerp_color((255, 176, 74), (255, 246, 214), t ** 0.75)
                pygame.draw.line(ss, (*col, 255), PU(u0), PU(u1), int(core * k))
    for i in range(steps):
        u0 = u_death * i / steps
        u1 = u_death * (i + 1) / steps
        t = i / steps
        pygame.draw.line(ss, (255, 252, 238, int(120 + 135 * t)), PU(u0), PU(u1),
                         max(1, int(1.3 * k)))

    # Bridge from arc rail to macaw center — makes the gold trail end AT the bird
    _ux_d, _uy_d = radial_unit(DEATH_PHASE)
    _mac = ((DEATH_X + _ux_d * 5.0) * k, (DEATH_Y + _uy_d * 5.0 - 1.0) * k)
    _tip = PU(u_death)
    pygame.draw.line(ss, (*INK, 250), _tip, _mac, int(9.4 * k))
    pygame.draw.line(ss, (255, 246, 214, 255), _tip, _mac, int(5.4 * k))

    # Personal best notch — gold diamond on the arc past death, shows achievable gap
    bx_b, by_b = arc_pos(BEST_PHASE, R)
    bxk, byk = int(bx_b * k), int(by_b * k)
    ux_b, uy_b = radial_unit(BEST_PHASE)
    # Stem outward from arc
    pygame.draw.line(ss, (255, 206, 92, 130),
                     (int((bx_b - ux_b * 2) * k), int((by_b - uy_b * 2) * k)),
                     (int((bx_b + ux_b * 10) * k), int((by_b + uy_b * 10) * k)),
                     max(1, int(1.5 * k)))
    # Ink outer diamond
    pygame.draw.polygon(ss, (*INK, 80),
                        [(bxk, byk - int(4.5 * k)), (bxk + int(3.5 * k), byk),
                         (bxk, byk + int(4.5 * k)), (bxk - int(3.5 * k), byk)])
    # Gold inner diamond
    pygame.draw.polygon(ss, (255, 206, 92, 160),
                        [(bxk, byk - int(3.0 * k)), (bxk + int(2.3 * k), byk),
                         (bxk, byk + int(3.0 * k)), (bxk - int(2.3 * k), byk)])

    # Left terminal: the start of the day, on the lit side.
    x, y = PU(0.0)
    pygame.draw.polygon(ss, (*INK, 240),
                        [(x, y - 5.0 * k), (x + 3.9 * k, y), (x, y + 5.0 * k),
                         (x - 3.9 * k, y)])
    pygame.draw.polygon(ss, (255, 226, 168, 255),
                        [(x, y - 3.6 * k), (x + 2.8 * k, y), (x, y + 3.6 * k),
                         (x - 2.8 * k, y)])


def trail_bloom(surf):
    """Warm haze under the flown run only. Deliberately low — its job is to
    lift the earned quarter of the sky at squint, not to bloom to white."""
    u_death = ease(DEATH_PHASE)
    for i in range(30):
        t = i / 29
        x, y = pos_u(u_death * 0.95 * t)
        rad = int(6 + 8 * t ** 1.3)
        g = soft_glow(rad, lerp_color((255, 158, 60), (255, 224, 168), t),
                      peak=int(12 + 18 * t ** 1.4), falloff=1.9)
        surf.blit(g, (int(x) - rad - 1, int(y) - rad - 1), special_flags=pygame.BLEND_ADD)


# ── the sun, moved ahead of the bird ─────────────────────────────────────────

SUN_ARC_LEAD = 56.0            # px of arc length between macaw and sun


def sun_u():
    return min(1.0, ease(DEATH_PHASE) + (SUN_ARC_LEAD / R) / math.pi)


def draw_sun(surf, ss):
    """Pale and hazed: the sun is in the veiled sky now. It marks that the day
    carried on, and must stay quieter than the bird that stopped.

    Its corona only fans FORWARD. A full ring at this radius reaches back into
    the macaw's beak, and the whole point of moving the sun off the death angle
    was to stop the two reading as one object.
    """
    x, y = pos_u(sun_u())
    tilt = arc_tangent_deg(DEATH_PHASE)
    fx, fy = math.cos(math.radians(tilt)), -math.sin(math.radians(tilt))
    g = soft_glow(20, (206, 198, 188), peak=26, falloff=2.2)
    surf.blit(g, (int(x) - 21, int(y) - 21), special_flags=pygame.BLEND_ADD)
    k = SS
    for i in range(12):
        a = math.radians(i * 30 + 8)
        dx, dy = math.cos(a), math.sin(a)
        if dx * fx + dy * fy < 0.05:
            continue
        pygame.draw.line(ss, (214, 206, 194, 130),
                         ((x + dx * 7.6) * k, (y + dy * 7.6) * k),
                         ((x + dx * 11.4) * k, (y + dy * 11.4) * k), int(1.2 * k))
    pygame.draw.circle(ss, (94, 98, 114, 200), (int(x * k), int(y * k)), int(6.2 * k))
    pygame.draw.circle(ss, (216, 202, 178, 240), (int(x * k), int(y * k)), int(5.2 * k))
    pygame.draw.circle(ss, (238, 226, 202, 240), (int((x - 1.1) * k), int((y - 1.2) * k)),
                       int(2.9 * k))
    return (x, y)


# ── the macaw at the death point ─────────────────────────────────────────────

def arc_tangent_deg(p):
    """Climb angle of the arc at a phase, in degrees above horizontal."""
    e = 1e-4
    x0, y0 = arc_pos(max(0.0, p - e))
    x1, y1 = arc_pos(min(1.0, p + e))
    return math.degrees(math.atan2(-(y1 - y0), (x1 - x0)))


def macaw_backlight(surf):
    """Warm lift around the death point, laid down BEFORE the vector overlay.

    Additive light run after the overlay would wash the trail's ink keyline
    straight out — which is exactly what it did before this was split out.
    """
    tilt = arc_tangent_deg(DEATH_PHASE)
    tx = math.cos(math.radians(tilt))
    ty = -math.sin(math.radians(tilt))
    # Trailing BACK along the flown run so the sun ahead of her stays clear.
    for off, rad, peak in ((0.0, 32, 54), (12.0, 26, 60), (24.0, 26, 36)):
        gx = DEATH_X - tx * off
        gy = DEATH_Y - ty * off
        # Warm rather than white: over a sky this bright an additive glow clips
        # channel by channel, and a neutral one clips straight to flat white.
        g = soft_glow(rad, (255, 206, 138), peak=peak, falloff=2.0)
        surf.blit(g, (int(gx) - rad - 1, int(gy) - rad - 1),
                  special_flags=pygame.BLEND_ADD)


def draw_macaw(surf):
    """Single-frame macaw canted along the tangent, ink-keylined, with a short
    cast shadow smeared along the rail underneath her.

    Composited natively rather than into the supersampled overlay: her keyline
    is only 2px, and a 3× downscale averages it into a grey smudge.
    """
    tilt = arc_tangent_deg(DEATH_PHASE)
    ux, uy = radial_unit(DEATH_PHASE)
    tx = math.cos(math.radians(tilt))
    ty = -math.sin(math.radians(tilt))

    # Cast shadow along the rail, slightly behind — plants her ON the arc
    # instead of floating over it.
    sx = DEATH_X - tx * 2.0 + ux * 1.2
    sy = DEATH_Y - ty * 2.0 + uy * 1.2 + 1.6
    alpha_line(surf, (8, 6, 12, 150),
               (sx - tx * 8, sy - ty * 8), (sx + tx * 5, sy + ty * 5), 5)

    src = _parrot.get_parrot(1, tilt)
    scale = 24.0 / 68.0
    small = pygame.transform.smoothscale(
        src, (max(1, int(src.get_width() * scale)),
              max(1, int(src.get_height() * scale))))
    bird = add_ink(small, (6, 8, 14, 220), 1)
    # Lifted off the rail along the outward normal so the gold trail runs under
    # her belly rather than through it.
    bx = DEATH_X + ux * 5.0
    by = DEATH_Y + uy * 5.0 - 1.0
    surf.blit(bird, (int(bx - bird.get_width() / 2), int(by - bird.get_height() / 2)))
    return (bx, by, bird.get_width())


# ── skybit background ────────────────────────────────────────────────────────

def build_skybit_bg(w=360, h=640):
    surf = pygame.Surface((w, h))
    sky_bot_y = int(h * 0.62)
    for y in range(sky_bot_y):
        t = y / sky_bot_y
        c = (
            int(8  + (18 - 8)  * t),
            int(12 + (40 - 12) * t),
            int(40 + (90 - 40) * t),
        )
        pygame.draw.line(surf, c, (0, y), (w - 1, y))
    for y in range(sky_bot_y, h):
        pygame.draw.line(surf, (10, 16, 48), (0, y), (w - 1, y))
    rng = random.Random(20260801)
    star_zone = int(h * 0.55)
    for _ in range(40):
        sx, sy = rng.randrange(w), rng.randrange(star_zone)
        a = rng.randint(100, 210)
        r = 1 if rng.random() < 0.8 else 2
        lay = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(lay, (220, 230, 255, a), (r + 1, r + 1), r)
        surf.blit(lay, (sx - r - 1, sy - r - 1))
    far_y = int(h * 0.60)
    pts_far = [(0, h)]
    for x in range(0, w + 1, 3):
        offs = (math.sin(x * 0.022 + 1.4) * 28 + math.sin(x * 0.041 + 0.6) * 14)
        pts_far.append((x, far_y + int(offs)))
    pts_far.append((w, h))
    pygame.draw.polygon(surf, (35, 45, 100), pts_far)
    near_y = int(h * 0.70)
    pts_near = [(0, h)]
    for x in range(0, w + 1, 3):
        offs = (math.sin(x * 0.033 + 2.1) * 22 + math.sin(x * 0.058 + 1.0) * 10)
        pts_near.append((x, near_y + int(offs)))
    pts_near.append((w, h))
    pygame.draw.polygon(surf, (22, 30, 72), pts_near)
    return surf


# ── screen ───────────────────────────────────────────────────────────────────

def render_screen():
    surf = pygame.Surface((W, H))
    bg = build_skybit_bg(W, H)
    surf.blit(bg, (0, 0))
    # Dark veil on the unearned side (right of death position)
    vx = int(DEATH_X)
    for dx in range(14):
        a = int(140 * (1 - dx / 14))
        lay = pygame.Surface((1, H), pygame.SRCALPHA)
        lay.fill((6, 8, 20, a))
        surf.blit(lay, (vx - 7 + dx, 0))
    veil_surf = pygame.Surface((W - vx, H), pygame.SRCALPHA)
    veil_surf.fill((6, 8, 20, 140))
    surf.blit(veil_surf, (vx, 0))

    ss = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
    trail_bloom(surf)
    sun_xy = draw_sun(surf, ss)
    draw_overlay(ss)

    surf.blit(pygame.transform.smoothscale(ss, (W, H)), (0, 0))

    # "?" markers for events the player didn't reach
    _sealed_markers = [
        (CLOWN_PHASE, R_INNER,      CLOWN_C),
        (RAIN_PHASE,  R_INNER - 22, RAIN_C),
        (SNOW_PHASE,  R_INNER,      SNOW_C),
    ]
    for _sm_p, _sm_r, _sm_c in _sealed_markers:
        if _sm_p > DEATH_PHASE:
            _smx, _smy = arc_pos(_sm_p, _sm_r)
            _qcol = tuple(c // 3 for c in _sm_c)
            text(surf, "?", 11, center=(int(_smx), int(_smy)), color=_qcol, shadow=None)

    # DAY COMPLETE — 3-layer aspirational glow
    xdc, ydc = pos_u(1.0)
    for rad, col_g, peak in ((28, (255, 180, 60), 30), (18, (255, 206, 92), 50), (10, (255, 230, 140), 70)):
        g_dc = soft_glow(rad, col_g, peak=peak, falloff=2.0)
        surf.blit(g_dc, (int(xdc) - rad - 1, int(ydc) - rad - 1), special_flags=pygame.BLEND_ADD)
    pygame.draw.circle(surf, (255, 240, 180), (int(xdc), int(ydc)), 7)
    pygame.draw.circle(surf, (255, 255, 220), (int(xdc) - 1, int(ydc) - 1), 4)

    text(surf, "DAY COMPLETE", 9, midright=(W - 6, int(ydc) + 18), color=GOLD, shadow=None)

    bx, by, bw = draw_macaw(surf)

    # ── banner: fully opaque dark neutral, no sky bleeding through ──
    pygame.draw.rect(surf, SCRIM, (0, 0, W, 74))
    fade = pygame.Surface((W, 10), pygame.SRCALPHA)
    for i in range(10):
        fade.fill((*SCRIM, int(238 * (1 - i / 10) ** 1.4)), pygame.Rect(0, i, W, 1))
    surf.blit(fade, (0, 74))
    alpha_line(surf, (255, 206, 92, 150), (0, 74), (W - 1, 74), 1)

    text(surf, f"FLIGHT LOG  ·  DAY {DAY_N}", 21, center=(W // 2, 28), color=GOLD, track=3, shadow=None)
    text(surf, f"PILLAR {DEATH_PILLAR}   ·   0:{TIME_ALIVE:02d}", 12,
         center=(W // 2, 55), color=CREAM, shadow=None)

    # ── headline, in the quiet sky above the apex ──
    pct = f"{DEATH_PHASE * 100:.0f}%"
    f_big, f_sml = font(21), font(11)
    w_pct = f_big.size(pct)[0]
    w_tail = f_sml.size("  OF THE DAY FLOWN")[0]
    x0 = (W - (w_pct + w_tail)) / 2
    text(surf, pct, 21, midleft=(x0, 104), color=GOLD, shadow=(0, 0, 0, 170))
    text(surf, "  OF THE DAY FLOWN", 11, midleft=(x0 + w_pct, 106), color=CREAM,
         shadow=(0, 0, 0, 170))
    alpha_line(surf, (255, 206, 92, 96), (int(x0), 120),
               (int(x0 + w_pct + w_tail), 120), 1)

    # ENCOUNTERED strip — chips for zones/events the player flew through
    alpha_line(surf, (100, 95, 90, 70), (18, 128), (342, 128), 1)
    text(surf, "FLEW THROUGH", 7, midleft=(18, 135), color=(150, 145, 140), shadow=None)
    enc_chip_x = 18
    enc_chip_y = 143
    for enc_lbl, enc_col in (("NEWBIE PERIOD", NEWBIE_C), ("GEYSER ZONE", GEYSER_C)):
        f_enc = font(8)
        enc_tw = f_enc.size(enc_lbl)[0]
        enc_cw, enc_ch = enc_tw + 12, 18
        # drop shadow
        enc_sh = pygame.Surface((enc_cw + 2, enc_ch + 2), pygame.SRCALPHA)
        pygame.draw.rect(enc_sh, (*INK, 70), enc_sh.get_rect(), border_radius=4)
        surf.blit(enc_sh, (enc_chip_x - 1, enc_chip_y + 1))
        # background
        enc_bg = pygame.Surface((enc_cw, enc_ch), pygame.SRCALPHA)
        pygame.draw.rect(enc_bg, (24, 20, 30, 200), enc_bg.get_rect(), border_radius=4)
        surf.blit(enc_bg, (enc_chip_x, enc_chip_y))
        # border (dimmed color, full opacity)
        enc_border = tuple(max(0, c // 3) for c in enc_col)
        pygame.draw.rect(surf, enc_border, (enc_chip_x, enc_chip_y, enc_cw, enc_ch),
                         width=1, border_radius=4)
        text(surf, enc_lbl, 8, center=(enc_chip_x + enc_cw // 2, enc_chip_y + enc_ch // 2),
             color=enc_col, shadow=None)
        enc_chip_x += enc_cw + 6

    # NEWBIE PERIOD label — full text, inside the arc
    nx, ny = arc_pos(0.10, R_INNER - 18)
    text(surf, "NEWBIE PERIOD", 8, center=(int(nx), int(ny)), color=NEWBIE_C, shadow=None)

    # BEST label — paired with the notch drawn in draw_overlay
    bx_lbl, by_lbl = arc_pos(BEST_PHASE, R + 16)
    text(surf, "BEST", 7, center=(int(bx_lbl), int(by_lbl)), color=(255, 206, 92), shadow=None)

    # Sealed event count — bottom of the sky region, centered
    text(surf, "3 EVENTS SEALED", 9, center=(W // 2, 390), color=(180, 185, 200), shadow=None)

    # Nearest sealed event teaser — distance without naming the event
    _nearest_dist = CLOWN_PILLAR - DEATH_PILLAR
    text(surf, f">  NEAREST SEALED:  ~{_nearest_dist} PILLARS AHEAD", 8,
         center=(W // 2, 406), color=(148, 152, 172), shadow=None)

    # ── death callout, hung off the macaw into the open dome interior ──
    alpha_line(surf, (10, 8, 14, 200), (int(bx) + 6, int(by) + 13), (127, 319), 1)
    alpha_line(surf, (255, 226, 168, 225), (int(bx) + 5, int(by) + 12), (126, 318), 1)
    f9, f8 = font(10), font(8)
    cw = max(f9.size("ENDED HERE")[0], f8.size(f"PILLAR {DEATH_PILLAR}  ·  {PHASE_LABEL} 18.4%")[0]) + 20
    cr = pygame.Rect(0, 0, cw, 34)
    cr.topleft = (120, 316)
    chip(surf, cr, radius=7, alpha=238, border_a=66)
    text(surf, "ENDED HERE", 10, midleft=(cr.x + 10, cr.y + 11), color=GOLD, shadow=None)
    text(surf, f"PILLAR {DEATH_PILLAR}  ·  {PHASE_LABEL} 18.4%", 8,
         midleft=(cr.x + 10, cr.y + 24), color=CREAM, shadow=None)

    # BACK pill
    pr = pygame.Rect(0, 0, 122, 36)
    pr.center = (W // 2, 597)
    sh = pygame.Surface((pr.w + 8, pr.h + 8), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 100), sh.get_rect(), border_radius=21)
    surf.blit(sh, (pr.x - 4, pr.y - 1))
    grad = pygame.Surface(pr.size, pygame.SRCALPHA)
    for y in range(pr.h):
        grad.fill(lerp_color((255, 228, 172), (226, 168, 96), y / (pr.h - 1)) + (255,),
                  pygame.Rect(0, y, pr.w, 1))
    mask = pygame.Surface(pr.size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=18)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(grad, pr.topleft)
    pygame.draw.rect(surf, (110, 68, 38), pr, width=1, border_radius=18)
    text(surf, "BACK", 13, center=(pr.centerx, pr.centery), color=(66, 40, 20),
         shadow=None, track=2)

    return surf, (bx, by), sun_xy


# ── squint pass ──────────────────────────────────────────────────────────────

def box_blur(surf, r):
    """Separable box blur over the raw RGB buffer — pygame 2.6 has no
    transform.box_blur and numpy is not a dependency of this repo."""
    w, h = surf.get_size()
    src = list(pygame.image.tostring(surf, "RGB"))
    tmp = [0] * (w * h * 3)
    for y in range(h):
        row = src[y * w * 3:(y + 1) * w * 3]
        for c in range(3):
            ch = row[c::3]
            pre = [0] * (w + 1)
            s = 0
            for i, v in enumerate(ch):
                s += v
                pre[i + 1] = s
            out = []
            for i in range(w):
                a, b = max(0, i - r), min(w, i + r + 1)
                out.append((pre[b] - pre[a]) // (b - a))
            tmp[y * w * 3 + c:(y + 1) * w * 3:3] = out
    dst = [0] * (w * h * 3)
    stride = w * 3
    for x in range(w):
        for c in range(3):
            col = tmp[x * 3 + c::stride]
            pre = [0] * (h + 1)
            s = 0
            for i, v in enumerate(col):
                s += v
                pre[i + 1] = s
            out = []
            for i in range(h):
                a, b = max(0, i - r), min(h, i + r + 1)
                out.append((pre[b] - pre[a]) // (b - a))
            dst[x * 3 + c::stride] = out
    return pygame.image.fromstring(bytes(dst), (w, h), "RGB")


def lum(c):
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def _lin(v):
    v /= 255.0
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def rel_lum(c):
    return 0.2126 * _lin(c[0]) + 0.7152 * _lin(c[1]) + 0.0722 * _lin(c[2])


def contrast(a, b):
    la, lb = rel_lum(a), rel_lum(b)
    if la < lb:
        la, lb = lb, la
    return (la + 0.05) / (lb + 0.05)


def annulus_mean(blur, cx, cy, r0, r1):
    tot, n = 0.0, 0
    for a in range(0, 360, 6):
        for r in range(r0, r1 + 1, 2):
            x = int(cx + math.cos(math.radians(a)) * r)
            y = int(cy + math.sin(math.radians(a)) * r)
            if 0 <= x < W and 0 <= y < HORIZON_Y:
                tot += lum(blur.get_at((x, y))[:3])
                n += 1
    return tot / max(1, n)


def region_mean_lum(blur, x0, x1, y0, y1, step=3):
    tot, n = 0.0, 0
    for x in range(x0, x1, step):
        for y in range(y0, y1, step):
            tot += lum(blur.get_at((x, y))[:3])
            n += 1
    return tot / max(1, n)


# ── review sheet ─────────────────────────────────────────────────────────────

def render_sheet(screen, squint, notes):
    pad, gap = 40, 36
    x1 = pad
    x2 = x1 + W + gap
    x3 = x2 + W + gap
    top = 112
    sw = x3 + W * 2 + pad
    sh = top + H * 2 + 200
    sheet = pygame.Surface((sw, sh))
    for y in range(sh):
        sheet.fill(lerp_color((30, 30, 36), (17, 17, 21), y / (sh - 1)),
                   pygame.Rect(0, y, sw, 1))

    text(sheet, "FLIGHT LOG · PROGRESS SCREEN", 24, midleft=(pad, 40), color=CREAM,
         track=2)
    text(sheet, "CONCEPT: SUN ARC   ·   ROUND 2", 13, midleft=(pad, 68), color=GOLD,
         track=1)
    text(sheet, "one sky (death phase) · veiled ahead-dome · gold trail w/ ink keyline · "
                "macaw at death point · single eased phase→x mapping",
         11, midleft=(pad, 90), color=(168, 168, 180))

    def framed(x, y, img, label):
        pygame.draw.rect(sheet, (72, 72, 82),
                         (x - 1, y - 1, img.get_width() + 2, img.get_height() + 2), 1)
        sheet.blit(img, (x, y))
        text(sheet, label, 12, midleft=(x, y + img.get_height() + 18),
             color=(190, 190, 200))

    framed(x1, top, screen, "1:1  ·  360×640 as shipped")
    framed(x2, top, squint, "1:1  ·  SQUINT (box blur r=4)")
    framed(x3, top, pygame.transform.scale(screen, (W * 2, H * 2)),
           "2×  ·  true-pixel detail view")

    ny = top + H + 56
    for i, line in enumerate(notes):
        col = GOLD if line.startswith("·") else (196, 200, 210)
        text(sheet, line, 12, midleft=(pad, ny + i * 19), color=col)
    return sheet


OUT_SLUG = "arc_count"
OUT_ROUND = "round_7"


def main():
    screen, bird_xy, sun_xy = render_screen()
    out = os.path.join(ROOT, "docs", "flight_log_arc_v2", OUT_SLUG, f"{OUT_ROUND}.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(screen, out)
    loaded = pygame.image.load(out)
    print(f"saved {out}  {loaded.get_size()}")


if __name__ == "__main__":
    main()
