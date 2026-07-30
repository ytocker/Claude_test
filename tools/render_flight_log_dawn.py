#!/usr/bin/env python3
"""dawn_to_dusk_panorama · flight_log · round_1

The run's whole day painted as one full-bleed horizon, read left to right.
The x axis is deliberately NONLINEAR: a sqrt-warp anchors the death column at
a comfortable reading position so the flown sliver gets magnified while the
long unflown tail compresses. Two spatial registers stay visible at once —
weather lives in the sky band, gameplay events live in an inlay ribbon at the
mountain base — so the screen is never a single-channel timeline.

Renders a review sheet: the 360x640 screen in colour, the same screen in
greyscale (proving the death marker survives on shape + value alone), and two
2x detail crops.
"""
import os
import sys
import math
import random

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.draw import lerp_color, NEAR_BLACK, UI_CREAM
from game.biome import palette_for_phase, PHASE_BOUNDARIES
from game.weather import _phase_for_pillar

W, H = 360, 640
HORIZON_Y = 395
FAR_BASE, NEAR_BASE = 395, 440
RIBBON_TOP, RIBBON_BOT = 452, 470
HAZE_TOP, HAZE_BOT = 366, 402

_GOLD_BRIGHT = (240, 192, 64)
_GOLD_MUTED = (200, 160, 50)
_PANEL_DARK = (12, 8, 38)

# Mock run: 25 pillars cleared, 47 s, day 1.
RUN = dict(pillars=25, score=25, phase=0.1839, day=1, time_alive=47, coins=38)
DAY_PILLARS = 175

_FONT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "game", "assets", "LiberationSans-Bold.ttf")
_fonts = {}


def font(size):
    f = _fonts.get(size)
    if f is None:
        f = pygame.font.Font(_FONT_PATH, size)
        _fonts[size] = f
    return f


# ── nonlinear day axis ───────────────────────────────────────────────────────
# sqrt of the reached phase, not the phase itself: a 25-pillar run is only 18%
# of the day, and a linear axis would squeeze the part the player actually flew
# into a 65px sliver. The warp buys it 157px of screen while still leaving the
# unflown tail legible enough to advertise what is out there.
F = RUN["phase"]
X_D = int(round(min(max(0.20 + 0.55 * math.sqrt(F), 0.28), 0.86) * W))


def phase_at_x(x):
    if x <= X_D:
        return F * (x / X_D)
    return F + (1.0 - F) * (x - X_D) / (W - X_D)


def x_at_phase(s):
    if s <= F:
        return s / F * X_D
    return X_D + (s - F) / (1.0 - F) * (W - X_D)


def alpha_layer():
    return pygame.Surface((W, H), pygame.SRCALPHA)


def zone_feather(x, x0, x1, edge=10.0):
    """0..1 envelope that fades a weather zone in and out at its edges — a
    hard vertical cut would read as a UI bar rather than as weather."""
    if x < x0 or x > x1:
        return 0.0
    return min(1.0, min(x - x0, x1 - x) / edge)


# ── sky ──────────────────────────────────────────────────────────────────────

def paint_sky(surf):
    for x in range(W):
        pal = palette_for_phase(phase_at_x(x) % 1.0)
        top, mid, bot = pal["sky_top"], pal["sky_mid"], pal["sky_bot"]
        hz = pal["horizon"]
        for y in range(HORIZON_Y + 1):
            t = y / HORIZON_Y
            if t < 0.55:
                c = lerp_color(top, mid, t / 0.55)
            else:
                c = lerp_color(mid, bot, (t - 0.55) / 0.45)
            if y > HORIZON_Y - 78:
                g = (y - (HORIZON_Y - 78)) / 78.0
                c = lerp_color(c, hz, 0.5 * g * g)
            surf.set_at((x, y), c)


def paint_celestials(surf):
    """Sun in the day block, moon at the night block. Without them the strip
    is a colour gradient; with them it is unmistakably one day passing, and
    they give the flown left third and the compressed night a focal point
    each so neither half is dead space."""
    for x_ph, y, r, core, glow, gr in (
            (0.055, 116, 11, (255, 248, 214), (255, 214, 130), 44),
            (0.640, 138, 8, (232, 238, 250), (150, 180, 235), 34)):
        cx = int(x_at_phase(x_ph))
        # Premultiplied on an opaque black plate: BLEND_RGB_ADD adds raw channel
        # values, so an alpha-ramped SRCALPHA halo would add its full colour at
        # every ring and blow the bloom to flat white.
        halo = pygame.Surface((W, H))
        for rad in range(gr, 0, -1):
            k = 0.34 * (1 - rad / gr) ** 2.0
            pygame.draw.circle(halo, tuple(int(c * k) for c in glow), (cx, y), rad)
        surf.blit(halo, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        pygame.draw.circle(surf, core, (cx, y), r)
    # Crescent: bite the moon with the sky behind it so it reads as a phase.
    mx = int(x_at_phase(0.640))
    pal = palette_for_phase(0.640)
    pygame.draw.circle(surf, lerp_color(pal["sky_top"], pal["sky_mid"], 0.35),
                       (mx - 5, 135), 7)


def paint_stars(surf):
    """Star density follows the palette's own star_alpha, so the compressed
    night block earns visual weight the flat sky gradient can't give it."""
    rng = random.Random(1207)
    layer = alpha_layer()
    for _ in range(320):
        x = rng.randrange(W)
        y = rng.randrange(6, 330)
        sa = palette_for_phase(phase_at_x(x) % 1.0)["star_alpha"]
        if sa < 12:
            continue
        a = int(sa * rng.uniform(0.35, 1.0) * (1.0 - y / 460.0))
        if a <= 4:
            continue
        r = 1 if rng.random() < 0.82 else 2
        pygame.draw.circle(layer, (255, 250, 235, min(255, a)), (x, y), r)
    surf.blit(layer, (0, 0))


# ── weather register (sky band) ──────────────────────────────────────────────

def paint_thermals(surf, p0, p1):
    x0, x1 = x_at_phase(p0), x_at_phase(p1)
    layer = alpha_layer()
    rng = random.Random(77)
    for i in range(6):
        bx = x0 + (x1 - x0) * (i + 0.5) / 6.0
        ph = rng.uniform(0, 6.28)
        top = rng.uniform(196, 236)
        prev = None
        for y in range(390, int(top), -2):
            climb = (390 - y) / (390 - top)
            wx = bx + math.sin(y * 0.045 + ph) * (4 + 9 * climb)
            a = int(80 * (1 - climb) ** 0.7 * zone_feather(wx, x0, x1, 12))
            if prev is not None and a > 3:
                col = lerp_color((255, 186, 96), (255, 232, 176), climb)
                pygame.draw.line(layer, (*col, a), prev, (wx, y), 2)
            prev = (wx, y)
    surf.blit(layer, (0, 0))


def paint_rain(surf, p0, p1):
    x0, x1 = x_at_phase(p0), x_at_phase(p1)
    layer = alpha_layer()
    rng = random.Random(311)
    for x in range(int(x0) - 60, int(x1) + 4, 4):
        for band in range(2):
            sx = x + band * 2 + rng.uniform(-1.5, 1.5)
            y_top = rng.uniform(126, 190)
            y_bot = rng.uniform(360, HORIZON_Y)
            ex = sx + (y_bot - y_top) * 0.34
            f = zone_feather((sx + ex) * 0.5, x0, x1, 14)
            if f <= 0:
                continue
            a = int(100 * f * rng.uniform(0.45, 1.0))
            pygame.draw.line(layer, (152, 176, 208, a), (sx, y_top), (ex, y_bot), 1)
    # Two forks, offset so the register reads as a storm cell not a texture.
    for seed, bx in ((5, x0 + (x1 - x0) * 0.34), (9, x0 + (x1 - x0) * 0.68)):
        r2 = random.Random(seed)
        pts, cx, cy = [], bx, 138.0
        while cy < 322:
            pts.append((cx, cy))
            cx += r2.uniform(-9, 9)
            cy += r2.uniform(20, 34)
        pygame.draw.lines(layer, (255, 255, 255, 70), False, pts, 4)
        pygame.draw.lines(layer, (255, 255, 250, 235), False, pts, 1)
        if len(pts) >= 3:
            bx2, by2 = pts[-3]
            pygame.draw.lines(layer, (255, 255, 250, 190), False,
                              [(bx2, by2), (bx2 - 11, by2 + 20), (bx2 - 7, by2 + 40)], 1)
    surf.blit(layer, (0, 0))


def paint_snow(surf, p0, p1):
    x0, x1 = x_at_phase(p0), x_at_phase(p1)
    layer = alpha_layer()
    for x in range(int(x0), W):
        f = zone_feather(x, x0, x1 + 1, 16)
        for y in range(150, HORIZON_Y):
            v = (y - 150) / (HORIZON_Y - 150)
            a = int(92 * f * (0.15 + 0.85 * v))
            if a > 2:
                layer.set_at((x, y), (222, 231, 242, a))
    rng = random.Random(2024)
    for _ in range(220):
        x = rng.uniform(x0, W)
        y = rng.uniform(140, HORIZON_Y - 2)
        a = int(215 * zone_feather(x, x0, x1 + 1, 16) * rng.uniform(0.4, 1.0))
        if a > 6:
            pygame.draw.circle(layer, (255, 255, 255, a), (int(x), int(y)),
                               1 if rng.random() < 0.75 else 2)
    surf.blit(layer, (0, 0))


def paint_horizon_haze(surf):
    """Atmospheric band where sky meets land. Laid over the FAR ridge but
    under the near one so distance reads as veiling, and it doubles as the
    legibility rail for the phase labels — otherwise a 7px caption would land
    on a bright sunrise column and vanish."""
    layer = alpha_layer()
    for y in range(HAZE_TOP, HAZE_BOT + 1):
        t = min(1.0, (y - HAZE_TOP) / 18.0)
        pygame.draw.line(layer, (*NEAR_BLACK, int(165 * t ** 1.3)), (0, y), (W - 1, y))
    surf.blit(layer, (0, 0))


# ── ridges ───────────────────────────────────────────────────────────────────

def ridge_profile(rng, n, y_base, crest_lo, crest_hi, valley_lo, valley_hi):
    """Per-column top edge for one silhouette. Vertices alternate crest and
    valley so the ridge actually has a skyline instead of a wobbling band."""
    xs = [i * (W - 1) / (n - 1) for i in range(n)]
    ys = []
    for i in range(n):
        if i % 2 == 0:
            ys.append(y_base - rng.uniform(crest_lo, crest_hi))
        else:
            ys.append(y_base - rng.uniform(valley_lo, valley_hi))
    prof = []
    for x in range(W):
        i = 0
        while i < n - 2 and x > xs[i + 1]:
            i += 1
        span = xs[i + 1] - xs[i]
        t = (x - xs[i]) / span if span else 0.0
        prof.append(ys[i] + (ys[i + 1] - ys[i]) * t)
    return prof


def paint_ridge(surf, prof, key, dark_to, rim=True):
    """Filled per column rather than as one flat polygon: a single fill colour
    would kill the left-to-right day gradient exactly where the land meets it."""
    for x in range(W):
        pal = palette_for_phase(phase_at_x(x) % 1.0)
        base = pal[key]
        top = int(prof[x])
        for y in range(top, H):
            d = (y - top) / max(1.0, H - top)
            surf.set_at((x, y), lerp_color(base, dark_to, min(1.0, d * 1.25)))
        if rim:
            surf.set_at((x, top), lerp_color(base, pal["sky_bot"], 0.42))


# ── gameplay register (inlay ribbon) ─────────────────────────────────────────

def paint_ribbon_base(surf):
    for x in range(W):
        pal = palette_for_phase(phase_at_x(x) % 1.0)
        body = lerp_color(pal["stone_dark"], (10, 8, 20), 0.42)
        for y in range(RIBBON_TOP, RIBBON_BOT):
            surf.set_at((x, y), lerp_color(body, lerp_color(body, (0, 0, 0), 0.35),
                                           (y - RIBBON_TOP) / 18.0))
        surf.set_at((x, RIBBON_TOP - 1), lerp_color(pal["stone_accent"], body, 0.35))


def paint_ribbon_events(surf):
    layer = alpha_layer()
    # Clown gauntlet — the one long-form gameplay event, so it gets a bar.
    cx0, cx1 = x_at_phase(0.403), x_at_phase(0.539)
    pygame.draw.rect(layer, (96, 64, 160, 160),
                     (cx0, RIBBON_TOP, max(3, cx1 - cx0), RIBBON_BOT - RIBBON_TOP))
    pygame.draw.rect(layer, (168, 138, 232, 190),
                     (cx0, RIBBON_TOP, max(3, cx1 - cx0), RIBBON_BOT - RIBBON_TOP), 1)
    surf.blit(layer, (0, 0))

    dcx, dcy, r = int((cx0 + cx1) * 0.5), (RIBBON_TOP + RIBBON_BOT) // 2, 7
    pygame.draw.polygon(surf, (140, 108, 210),
                        [(dcx, dcy - r), (dcx + r, dcy), (dcx, dcy + r), (dcx - r, dcy)])
    pygame.draw.polygon(surf, (232, 224, 255),
                        [(dcx, dcy - r), (dcx + r, dcy), (dcx, dcy + r), (dcx - r, dcy)], 1)
    for px, py in ((-3, -1), (0, 0), (3, 1)):
        surf.set_at((dcx + px, dcy + py), (255, 255, 255))

    # Coin rushes: notches on the ribbon's top edge. Flown ones ring bright,
    # unflown ones drop to muted gold — chroma, never brightness, marks the
    # boundary.
    for p in range(15, DAY_PILLARS + 1, 15):
        x = int(x_at_phase(_phase_for_pillar(p)))
        if x >= W:
            continue
        col = _GOLD_BRIGHT if x <= X_D else _GOLD_MUTED
        pygame.draw.line(surf, col, (x, RIBBON_TOP - 3), (x, RIBBON_TOP + 3), 2)

    # Finale rush — the day's last three pillars all resolve inside 2px of the
    # right edge under the warp, so they read as one deliberate end-cap block
    # instead of three notches fighting over the same column.
    fx = min(W - 5, int(x_at_phase(min(0.999, _phase_for_pillar(DAY_PILLARS - 2)))) - 3)
    pygame.draw.rect(surf, _GOLD_MUTED,
                     (fx, RIBBON_TOP - 4, W - fx, RIBBON_BOT - RIBBON_TOP + 4))
    pygame.draw.rect(surf, (255, 226, 150),
                     (fx, RIBBON_TOP - 4, W - fx, RIBBON_BOT - RIBBON_TOP + 4), 1)


# ── unflown territory ────────────────────────────────────────────────────────

def desaturate_ahead(surf, x_from, chroma=0.40, value=1.05):
    """Ahead of the death column the day is drained of colour, not of light:
    darkening would read as 'night' in a screen whose whole subject is
    time of day."""
    for x in range(x_from, W):
        for y in range(H):
            r, g, b = surf.get_at((x, y))[:3]
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            surf.set_at((x, y), (
                max(0, min(255, int((lum + (r - lum) * chroma) * value))),
                max(0, min(255, int((lum + (g - lum) * chroma) * value))),
                max(0, min(255, int((lum + (b - lum) * chroma) * value)))))


# ── labels + marker ──────────────────────────────────────────────────────────

def outline_text(surf, txt, size, center, color, outline=NEAR_BLACK, ow=1):
    f = font(size)
    img = f.render(txt, True, color)
    sh = f.render(txt, True, outline)
    r = img.get_rect(center=center)
    for dx in range(-ow, ow + 1):
        for dy in range(-ow, ow + 1):
            if dx or dy:
                surf.blit(sh, (r.x + dx, r.y + dy))
    surf.blit(img, r.topleft)
    return r


def paint_phase_labels(surf):
    """All seven times of day get a name. The compressed right half can't hold
    them on one line, so they stagger across two rows rather than dropping the
    most characterful bands (sunset, sunrise) off the log entirely."""
    rows = ([], [])
    row_y = (380, 392)
    for frac, name in PHASE_BOUNDARIES:
        x = x_at_phase(frac)
        if x > W - 6:
            continue
        short = {"GOLDEN HOUR": "GOLDEN"}.get(name, name)
        wpx = font(7).size(short)[0]
        r = 0 if not any(abs(x - px) < (wpx + pw) * 0.5 + 5 for px, pw in rows[0]) else 1
        rows[r].append((x, wpx))
        cx = max(wpx // 2 + 3, min(W - wpx // 2 - 3, int(x)))
        y = row_y[r]
        tick = alpha_layer()
        pygame.draw.line(tick, (255, 255, 255, 110), (x, 356), (x, y - 5), 1)
        surf.blit(tick, (0, 0))
        outline_text(surf, short, 7, (cx, y),
                     UI_CREAM if x <= X_D else (198, 196, 192))


def paint_death_marker(surf):
    halo = alpha_layer()
    for dx in range(-4, 5):
        a = int(180 * (1 - abs(dx) / 5.0) ** 1.5)
        pygame.draw.line(halo, (228, 46, 46, a), (X_D + dx, 96), (X_D + dx, RIBBON_BOT))
    surf.blit(halo, (0, 0))
    pygame.draw.line(surf, (255, 255, 255), (X_D, 96), (X_D, RIBBON_BOT), 2)

    py = 430
    tri = [(X_D - 7, py), (X_D + 7, py), (X_D, py + 10)]
    pygame.draw.polygon(surf, NEAR_BLACK, [(x + 1, y + 1) for x, y in tri])
    pygame.draw.polygon(surf, (214, 42, 42), tri)
    pygame.draw.polygon(surf, (255, 255, 255), tri, 1)

    label = f"YOU · PILLAR {RUN['pillars']}"
    lw = font(9).size(label)[0]
    cx = max(lw // 2 + 6, min(W - lw // 2 - 6, X_D))
    pygame.draw.line(surf, (255, 255, 255), (X_D, 92), (X_D, 96), 2)
    outline_text(surf, label, 9, (cx, 84), UI_CREAM)


# ── chrome ───────────────────────────────────────────────────────────────────

def paint_scrims(surf):
    layer = alpha_layer()
    for y in range(0, 104):
        pygame.draw.line(layer, (*NEAR_BLACK, int(190 * (1 - y / 104.0) ** 0.85)),
                         (0, y), (W - 1, y))
    for y in range(478, H):
        pygame.draw.line(layer, (*NEAR_BLACK, int(200 * min(1.0, (y - 478) / 30.0))),
                         (0, y), (W - 1, y))
    surf.blit(layer, (0, 0))


def stat_glyph(surf, kind, cx, cy):
    c = _GOLD_MUTED
    if kind == "time":
        pygame.draw.circle(surf, c, (cx, cy), 6, 1)
        pygame.draw.line(surf, c, (cx, cy), (cx, cy - 4), 1)
        pygame.draw.line(surf, c, (cx, cy), (cx + 3, cy + 1), 1)
    elif kind == "coin":
        pygame.draw.circle(surf, c, (cx, cy), 6, 1)
        pygame.draw.circle(surf, c, (cx, cy), 3, 1)
    else:
        pygame.draw.rect(surf, c, (cx - 4, cy - 6, 8, 12), 1)
        pygame.draw.line(surf, c, (cx - 6, cy - 6), (cx + 5, cy - 6), 1)
        pygame.draw.line(surf, c, (cx - 6, cy + 5), (cx + 5, cy + 5), 1)


def paint_chrome(surf):
    outline_text(surf, "F L I G H T   L O G", 20, (100, 27), _GOLD_BRIGHT)
    outline_text(surf, f"DAY {RUN['day']}  ·  {round(F * 100)}% OF THE DAY",
                 8, (100, 46), (198, 178, 138))

    score = font(44).render(str(RUN["score"]), True, _GOLD_BRIGHT)
    sr = score.get_rect(midright=(344, 44))
    sh = font(44).render(str(RUN["score"]), True, NEAR_BLACK)
    surf.blit(sh, (sr.x + 2, sr.y + 2))
    surf.blit(score, sr.topleft)
    outline_text(surf, "SCORE", 8, (sr.centerx, 72), (198, 178, 138))

    stats = (("time", f"0:{RUN['time_alive']:02d}", "TIME"),
             ("coin", str(RUN["coins"]), "COINS"),
             ("pillar", str(RUN["pillars"]), "PILLARS"))
    for i, (kind, val, lab) in enumerate(stats):
        cx = 70 + i * 110
        stat_glyph(surf, kind, cx, 502)
        outline_text(surf, val, 15, (cx, 523), UI_CREAM)
        outline_text(surf, lab, 9, (cx, 540), (188, 166, 126))
    for dx in (125, 235):
        div = alpha_layer()
        pygame.draw.line(div, (*_GOLD_MUTED, 85), (dx, 496), (dx, 544))
        surf.blit(div, (0, 0))

    img = font(15).render("BACK", True, _GOLD_BRIGHT)
    pw, ph = max(150, img.get_width() + 24), img.get_height() + 12
    x, y = 180 - pw // 2, 608 - ph // 2
    body = pygame.Surface((pw, ph), pygame.SRCALPHA)
    pygame.draw.rect(body, (*_PANEL_DARK, 210), (0, 0, pw, ph), border_radius=ph // 2)
    pygame.draw.rect(body, _GOLD_BRIGHT, (0, 0, pw, ph), width=2, border_radius=ph // 2)
    surf.blit(body, (x, y))
    surf.blit(img, img.get_rect(center=(180, 608)))


# ── compose ──────────────────────────────────────────────────────────────────

def render_screen():
    s = pygame.Surface((W, H))
    s.fill(NEAR_BLACK)
    paint_sky(s)
    paint_stars(s)
    paint_celestials(s)
    paint_thermals(s, 0.106, 0.206)
    paint_rain(s, 0.43, 0.69)
    paint_snow(s, 0.78, 1.0)

    rng = random.Random(42)
    far = ridge_profile(rng, 9, FAR_BASE, 30, 50, 4, 15)
    near = ridge_profile(rng, 7, NEAR_BASE, 20, 35, 2, 9)
    paint_ridge(s, far, "mtn_far", (12, 12, 26))
    paint_horizon_haze(s)
    paint_ridge(s, near, "mtn_near", (8, 8, 18))
    paint_ribbon_base(s)

    desaturate_ahead(s, X_D + 1)

    paint_scrims(s)
    paint_phase_labels(s)
    paint_ribbon_events(s)
    paint_death_marker(s)
    paint_chrome(s)
    return s


def greyscale(src):
    out = pygame.Surface(src.get_size())
    for x in range(src.get_width()):
        for y in range(src.get_height()):
            r, g, b = src.get_at((x, y))[:3]
            v = int(0.299 * r + 0.587 * g + 0.114 * b)
            out.set_at((x, y), (v, v, v))
    return out


def sheet(screen, grey):
    SW, SH = 1176, 768
    sh = pygame.Surface((SW, SH))
    sh.fill((26, 26, 34))
    outline_text(sh, "SKYBIT · FLIGHT LOG · dawn_to_dusk_panorama · round 1",
                 18, (SW // 2, 26), _GOLD_BRIGHT, (10, 10, 14))

    def frame(surf, x, y, cap):
        pygame.draw.rect(sh, (70, 68, 80), (x - 1, y - 1, surf.get_width() + 2,
                                            surf.get_height() + 2), 1)
        sh.blit(surf, (x, y))
        outline_text(sh, cap, 12, (x + surf.get_width() // 2,
                                   y + surf.get_height() + 14), UI_CREAM, (10, 10, 14))

    frame(screen, 24, 64, "1x · in-game scale (360x640)")
    frame(grey, 408, 64, "greyscale proof · marker survives on shape + value")

    crops = ((pygame.Rect(70, 336, 180, 112), "2x · marker, ridges, event ribbon"),
             (pygame.Rect(180, 128, 180, 112), "2x · weather register + unflown drain"))
    for i, (rect, cap) in enumerate(crops):
        z = pygame.transform.scale(screen.subsurface(rect), (360, 224))
        frame(z, 792, 64 + i * 268, cap)

    outline_text(sh, "mock run: 25 pillars · 47s · biome phase 0.184 · day 1",
                 11, (972, 620), (188, 186, 196), (10, 10, 14))
    outline_text(sh, "axis warped by sqrt(phase): flown 18% of day -> 44% of width",
                 11, (972, 640), (188, 186, 196), (10, 10, 14))
    return sh


if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(root, "docs", "flight_log", "dawn_to_dusk_panorama")
    os.makedirs(out_dir, exist_ok=True)
    screen = render_screen()
    pygame.image.save(sheet(screen, greyscale(screen)),
                      os.path.join(out_dir, "round_1.png"))
    print("saved", os.path.join(out_dir, "round_1.png"), "x_d =", X_D)
