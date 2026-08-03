#!/usr/bin/env python3
"""
arc_count/monolith round 1 — giant 18% hero number, minimal chrome.

MONOLITH concept: commanding dark slab aesthetic. Enormous GOLD hero metric,
compact 2-column stats, flat sharp-cornered death callout, bare BACK text.
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

# Sunlit dune on top, shadowed dune below
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
CLOWN_ZONE = (0.38, 0.42)
RAIN_ZONE  = (0.42, 0.46)
SNOW_ZONE  = (0.80, 0.85)
BEST_PHASE   = 0.31
BEST_PILLAR  = 40
BEST_TIME    = 78
CLOWN_PILLAR = 65

DEATH_PALETTE = palette_for_phase(DEATH_PHASE)
STAR_FLOOR_PHASE = 0.54


# ── the single phase→screen mapping ──────────────────────────────────────────
EASE_P = 0.652


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
    return 30.0 <= 180.0 * (1.0 - ease(p)) <= 150.0


DEATH_X, DEATH_Y = arc_pos(DEATH_PHASE)
STAR_FLOOR_X = arc_pos(STAR_FLOOR_PHASE)[0]


# ── veil ─────────────────────────────────────────────────────────────────────

def veil_strength(x):
    d = x - DEATH_X
    if d <= 0:
        return 0.0
    k = min(1.0, d / 13.0)
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
    """Additive glow with the falloff baked into RGB."""
    size = radius * 2 + 2
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    c = radius + 1
    for r in range(radius, 0, -1):
        f = (1 - (r / radius) ** falloff) * (peak / 255.0)
        s_col = (int(color[0] * f), int(color[1] * f), int(color[2] * f), 255)
        pygame.draw.circle(s, s_col, (c, c), r)
    return s


def alpha_line(surf, rgba, p0, p1, width=1):
    lay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.line(lay, rgba, p0, p1, width)
    surf.blit(lay, (0, 0))


def add_ink(src, color=(6, 8, 14, 240), pad=2):
    """Dilated dark keyline."""
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
    column = [lerp_color_multi(SKY_STOPS, y / (HORIZON_Y - 1)) for y in range(HORIZON_Y)]
    for x in range(W):
        k = veil_strength(x)
        col = column if k <= 0.0 else [veil(c, k) for c in column]
        for y in range(HORIZON_Y):
            v = vignette(x, y)
            c = col[y]
            surf.set_at((x, y), (int(c[0] * v), int(c[1] * v), int(c[2] * v)))


def draw_clouds(surf):
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


# ── event glyphs ─────────────────────────────────────────────────────────────

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


GLYPHS = [
    (g_geyser, "GEYSER", GEYSER_C),
    (g_clown, "CLOWN", CLOWN_C),
    (g_rain, "RAIN", RAIN_C),
    (g_snow, "SNOWSTORM", SNOW_C),
]


def stamp_glyph(dst, fn, cx, cy, r, col, ink_pad=2):
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

    # Event rail
    for i in range(0, 181):
        u = i / 180
        x, y = PU(u, R_INNER)
        if u <= u_death:
            col = (255, 226, 176, 108)
        else:
            col = (176, 190, 214, 44)
        pygame.draw.circle(ss, col, (int(x), int(y)), int(0.9 * k))

    # AHEAD run
    u_ahead_start = u_death + 12.0 / (R * math.pi)
    for _ai in range(100):
        _u0 = u_ahead_start + (1.0 - u_ahead_start) * _ai / 100
        _u1 = u_ahead_start + (1.0 - u_ahead_start) * (_ai + 1) / 100
        _a = int(55 - 38 * (_ai / 99))
        pygame.draw.line(ss, (*COOL, _a), PU(_u0), PU(_u1), max(1, int(2.8 * k)))
    for _di in range(90):
        if _di % 3 == 2:
            continue
        _u0 = u_ahead_start + (1.0 - u_ahead_start) * _di / 90
        _u1 = u_ahead_start + (1.0 - u_ahead_start) * (_di + 0.65) / 90
        _a = int(130 - 90 * (_di / 89))
        pygame.draw.line(ss, (*COOL, _a), PU(_u0), PU(_u1), max(1, int(1.1 * k)))

    # Phase ticks
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

    # NEWBIE PERIOD zone
    u_nb_end = ease(NEWBIE_END_PHASE)
    pts_nb = [PU(u_nb_end * i / 40, R_INNER) for i in range(41)]
    pygame.draw.lines(ss, (*NEWBIE_C, 160), False, pts_nb, int(2.2 * k))
    ux_nb, uy_nb = radial_unit(NEWBIE_END_PHASE)
    xnb, ynb = arc_pos(NEWBIE_END_PHASE, R_INNER)
    pygame.draw.line(ss, (*NEWBIE_C, 190),
                     ((xnb - ux_nb * 4.2) * k, (ynb - uy_nb * 4.2) * k),
                     ((xnb + ux_nb * 4.2) * k, (ynb + uy_nb * 4.2) * k), int(2.0 * k))

    # Geyser span bracket
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

    # Event glyphs
    ring_items = [
        (GEYSER_SPAN[0], R_INNER - 24, g_geyser, GEYSER_C),
        (CLOWN_PHASE, R_INNER, g_clown, CLOWN_C),
        (RAIN_PHASE, R_INNER - 22, g_rain, RAIN_C),
        (SNOW_PHASE, R_INNER, g_snow, SNOW_C),
    ]
    for p, rad, fn, col in ring_items:
        x, y = arc_pos(p, rad)
        if p > DEATH_PHASE:
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
            for _zt in (_z0, _z1):
                _ux_z, _uy_z = radial_unit(_zt)
                _ztx, _zty = arc_pos(_zt, R_INNER)
                pygame.draw.line(ss, (*col, 70),
                                 (int((_ztx - _ux_z * 3.5) * k), int((_zty - _uy_z * 3.5) * k)),
                                 (int((_ztx + _ux_z * 3.5) * k), int((_zty + _uy_z * 3.5) * k)),
                                 max(1, int(1.2 * k)))
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

    # TRAVELLED run
    steps = 96
    for pass_ink in (True, False):
        for i in range(steps):
            u0 = u_death * i / steps
            u1 = u_death * (i + 1) / steps
            t = i / steps
            core = 3.0 + 2.4 * t ** 1.4
            if pass_ink:
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

    # Bridge from arc rail to macaw center
    _ux_d, _uy_d = radial_unit(DEATH_PHASE)
    _mac = ((DEATH_X + _ux_d * 5.0) * k, (DEATH_Y + _uy_d * 5.0 - 1.0) * k)
    _tip = PU(u_death)
    pygame.draw.line(ss, (*INK, 250), _tip, _mac, int(9.4 * k))
    pygame.draw.line(ss, (255, 246, 214, 255), _tip, _mac, int(5.4 * k))

    # Personal best notch
    bx_b, by_b = arc_pos(BEST_PHASE, R)
    bxk, byk = int(bx_b * k), int(by_b * k)
    ux_b, uy_b = radial_unit(BEST_PHASE)
    pygame.draw.line(ss, (255, 206, 92, 130),
                     (int((bx_b - ux_b * 2) * k), int((by_b - uy_b * 2) * k)),
                     (int((bx_b + ux_b * 10) * k), int((by_b + uy_b * 10) * k)),
                     max(1, int(1.5 * k)))
    pygame.draw.polygon(ss, (*INK, 80),
                        [(bxk, byk - int(4.5 * k)), (bxk + int(3.5 * k), byk),
                         (bxk, byk + int(4.5 * k)), (bxk - int(3.5 * k), byk)])
    pygame.draw.polygon(ss, (255, 206, 92, 160),
                        [(bxk, byk - int(3.0 * k)), (bxk + int(2.3 * k), byk),
                         (bxk, byk + int(3.0 * k)), (bxk - int(2.3 * k), byk)])

    # Left terminal
    x, y = PU(0.0)
    pygame.draw.polygon(ss, (*INK, 240),
                        [(x, y - 5.0 * k), (x + 3.9 * k, y), (x, y + 5.0 * k),
                         (x - 3.9 * k, y)])
    pygame.draw.polygon(ss, (255, 226, 168, 255),
                        [(x, y - 3.6 * k), (x + 2.8 * k, y), (x, y + 3.6 * k),
                         (x - 2.8 * k, y)])


def trail_bloom(surf):
    u_death = ease(DEATH_PHASE)
    for i in range(30):
        t = i / 29
        x, y = pos_u(u_death * 0.95 * t)
        rad = int(6 + 8 * t ** 1.3)
        g = soft_glow(rad, lerp_color((255, 158, 60), (255, 224, 168), t),
                      peak=int(12 + 18 * t ** 1.4), falloff=1.9)
        surf.blit(g, (int(x) - rad - 1, int(y) - rad - 1), special_flags=pygame.BLEND_ADD)


# ── the sun, moved ahead of the bird ─────────────────────────────────────────

SUN_ARC_LEAD = 56.0


def sun_u():
    return min(1.0, ease(DEATH_PHASE) + (SUN_ARC_LEAD / R) / math.pi)


def arc_tangent_deg(p):
    """Climb angle of the arc at a phase, in degrees above horizontal."""
    e = 1e-4
    x0, y0 = arc_pos(max(0.0, p - e))
    x1, y1 = arc_pos(min(1.0, p + e))
    return math.degrees(math.atan2(-(y1 - y0), (x1 - x0)))


def draw_sun(surf, ss):
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

def macaw_backlight(surf):
    """Warm lift around the death point, laid down BEFORE the vector overlay."""
    tilt = arc_tangent_deg(DEATH_PHASE)
    tx = math.cos(math.radians(tilt))
    ty = -math.sin(math.radians(tilt))
    for off, rad, peak in ((0.0, 32, 54), (12.0, 26, 60), (24.0, 26, 36)):
        gx = DEATH_X - tx * off
        gy = DEATH_Y - ty * off
        g = soft_glow(rad, (255, 206, 138), peak=peak, falloff=2.0)
        surf.blit(g, (int(gx) - rad - 1, int(gy) - rad - 1),
                  special_flags=pygame.BLEND_ADD)


def draw_macaw(surf):
    tilt = arc_tangent_deg(DEATH_PHASE)
    ux, uy = radial_unit(DEATH_PHASE)
    tx = math.cos(math.radians(tilt))
    ty = -math.sin(math.radians(tilt))

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
    macaw_backlight(surf)
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

    bx, by, bw = draw_macaw(surf)

    # ── MONOLITH chrome ──────────────────────────────────────────────────────

    # Banner (y=0-74 scrim, hairline, FLIGHT LOG left / DAY N right)
    pygame.draw.rect(surf, SCRIM, (0, 0, W, 74))
    fade = pygame.Surface((W, 10), pygame.SRCALPHA)
    for i in range(10):
        fade.fill((*SCRIM, int(238*(1-i/10)**1.4)), pygame.Rect(0, i, W, 1))
    surf.blit(fade, (0, 74))
    alpha_line(surf, (*GOLD, 150), (0, 74), (W-1, 74), 1)
    text(surf, "FLIGHT LOG", 21, midleft=(18, 28), color=GOLD, track=3, shadow=None)
    text(surf, f"DAY {DAY_N}", 21, midright=(W-18, 28), color=GOLD, track=2, shadow=None)

    # Hero number — enormous GOLD "18%" at 80pt
    pct_str = f"{int(DEATH_PHASE*100)}%"
    f80 = pygame.font.Font(FONT_PATH, 80)
    pct_surf = f80.render(pct_str, True, GOLD)
    surf.blit(pct_surf, (W//2 - pct_surf.get_width()//2, 82))
    # Tiny "OF THE DAY FLOWN" below hero number
    text(surf, "OF THE DAY FLOWN", 8, center=(W//2, 82 + pct_surf.get_height() + 6),
         color=(180, 175, 165), track=3, shadow=None)

    # Stats block — 2 columns, compact, below hero number
    y_stats = 82 + pct_surf.get_height() + 22
    stat_pairs = [("DAY", str(DAY_N)), ("PILLAR", str(DEATH_PILLAR)), ("TIME", f"0:{TIME_ALIVE:02d}")]
    for i, (k, v) in enumerate(stat_pairs):
        ys = y_stats + i * 18
        text(surf, k, 8, midright=(W//2 - 8, ys), color=(130, 126, 118), track=2, shadow=None)
        text(surf, v, 9, midleft=(W//2 + 8, ys), color=CREAM, track=1, shadow=None)

    # Events line
    text(surf, "4 EVENTS UNSEALED AHEAD", 8, center=(W//2, y_stats + 60),
         color=(110, 108, 118), track=2, shadow=None)

    # DAY COMPLETE text
    xdc, ydc = pos_u(1.0)
    text(surf, "DAY COMPLETE", 8, midright=(W-6, int(ydc)+18), color=GOLD, shadow=None)

    # Death callout — flat sharp-cornered dark box, no connector lines
    call_w, call_h = 118, 30
    call_x = int(bx) + 18
    call_y = int(by) - 40
    call_surf = pygame.Surface((call_w, call_h), pygame.SRCALPHA)
    pygame.draw.rect(call_surf, (*SCRIM, 220), call_surf.get_rect())  # no border_radius
    pygame.draw.rect(call_surf, (*GOLD, 90), call_surf.get_rect(), 1)  # 1px gold border
    surf.blit(call_surf, (call_x, call_y))
    text(surf, "ENDED HERE", 9, midleft=(call_x+8, call_y+10), color=GOLD, shadow=None)
    text(surf, f"PILLAR {DEATH_PILLAR}", 8, midleft=(call_x+8, call_y+22), color=(170, 165, 155), shadow=None)

    # BACK — bare tracked text, no pill, no border
    text(surf, "BACK", 13, center=(W//2, 597), color=GOLD, track=4, shadow=None)

    return surf, (bx, by), sun_xy


OUT_SLUG = "arc_count/monolith"
OUT_ROUND = "round_1"


def main():
    screen, bird_xy, sun_xy = render_screen()
    out = os.path.join(ROOT, "docs", "flight_log_arc_v2", OUT_SLUG, f"{OUT_ROUND}.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(screen, out)
    loaded = pygame.image.load(out)
    print(f"saved {out}  {loaded.get_size()}")


if __name__ == "__main__":
    main()
