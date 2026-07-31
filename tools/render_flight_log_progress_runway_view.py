#!/usr/bin/env python3
"""
runway-view  ·  flight_log_progress  ·  round 1

The day cycle read as a single vertical runway in one-point perspective: the
player's run is a takeoff roll that ran out of pavement. Foreshortening is the
whole argument — the flown 18.4% of the day eats ~30% of the runway's screen
height, so the near events that would collide on a linear timeline separate on
their own.

Lighting is inverted against the usual "progress bar dims what's spent": the
UNFLOWN runway stays fully lit and saturated, hazing out toward the vanishing
point, while the FLOWN section is marked rather than dimmed — rubber laid down
the centreline and heat scorch, the evidence of having been there.

Run from the repo root:  python tools/render_flight_log_progress_runway_view.py
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

from game.draw import lerp_color, draw_cloud
from game.biome import PHASE_BOUNDARIES, palette_for_phase
from game.weather import (THERMAL_START_PHASE, THERMAL_PEAK_PHASE,
                          THERMAL_END_PHASE, SNOW_STORM_CENTER)
from game.config import LATE_GAME_PILLAR, CLOWN_START_PILLAR, RAIN_START_PILLAR


# ── canvas + perspective frame ───────────────────────────────────────────────

W, H = 360, 640
SS = 3                      # supersample factor for the geometry pass

Y_NEAR, Y_FAR = 560.0, 100.0
HW_NEAR, HW_FAR = 100.0, 35.0
CX = 180.0

# Depth grows linearly with phase, so screen-y goes as 1/(1+A·p). A sets how
# hard the near end stretches; 0.95 buys the near-event separation the concept
# is built on while still leaving the four late-phase bands legible up top.
A = 0.95
C = (Y_NEAR - Y_FAR) * (1.0 + A) / A
Y_VP = Y_NEAR - C


def phase_to_y(p):
    return Y_VP + C / (1.0 + A * p)


def hw_at_y(y):
    return HW_FAR + (HW_NEAR - HW_FAR) * (y - Y_FAR) / (Y_NEAR - Y_FAR)


def edges_at_y(y):
    hw = hw_at_y(y)
    return CX - hw, CX + hw


def scale_at_y(y):
    return hw_at_y(y) / HW_NEAR


def smoothstep(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def ymix(stops, y):
    """Multi-stop colour ramp keyed on screen-y rather than 0..1."""
    for i in range(len(stops) - 1):
        y0, c0 = stops[i]
        y1, c1 = stops[i + 1]
        if y <= y1:
            t = (y - y0) / (y1 - y0) if y1 > y0 else 0.0
            return lerp_color(c0, c1, smoothstep(t))
    return stops[-1][1]


def s(v):
    return int(round(v * SS))


# ── palette ──────────────────────────────────────────────────────────────────

DAY_PAL = palette_for_phase(0.0)

PAV_NEAR = (206, 174, 133)          # lit sandstone at the threshold
PAV_FAR = (216, 200, 177)           # same stone, washed by distance haze
HAZE = (240, 232, 210)

PAINT_NEAR = (252, 246, 232)
PAINT_FAR = (245, 239, 226)

# Apron stays below the pavement in value at every depth — the lit runway has
# to be the brightest thing on screen even where haze flattens everything.
APRON_STOPS = [(100.0, (140, 160, 142)),
               (168.0, (96, 124, 104)),
               (330.0, (56, 80, 66)),
               (640.0, (26, 40, 35))]

BAR_BODY = (74, 108, 132)
BAR_EDGE = (170, 206, 226)

SCARLET = (232, 62, 58)
SCARLET_HI = (255, 132, 112)

CREAM = (246, 240, 226)
SLATE = (24, 36, 48)

RUBBER = (56, 38, 30)
SCORCH = (48, 34, 27)


# ── mock run ─────────────────────────────────────────────────────────────────

DEATH_PHASE = 0.184
DEATH_PILLAR = 25
DAY_NO = 1
TIME_ALIVE = 47
DEATH_Y = phase_to_y(DEATH_PHASE)

GENIE_PHASE = THERMAL_PEAK_PHASE
CLOWN_PHASE = 0.403
RAIN_PHASE = 0.430
SNOW_PHASE = SNOW_STORM_CENTER


# ── surfaces ─────────────────────────────────────────────────────────────────

geo = pygame.Surface((W * SS, H * SS))
geo.fill((0, 0, 0))


def new_layer():
    return pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)


def pavement_mask():
    m = new_layer()
    pygame.draw.polygon(m, (255, 255, 255, 255), [
        (s(CX - HW_NEAR), s(Y_NEAR)), (s(CX + HW_NEAR), s(Y_NEAR)),
        (s(CX + HW_FAR), s(Y_FAR)), (s(CX - HW_FAR), s(Y_FAR))])
    return m


PAV_MASK = pavement_mask()


def clip_to_pavement(layer):
    layer.blit(PAV_MASK, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)


# ── sky ──────────────────────────────────────────────────────────────────────

def draw_sky():
    stops = [(0.0, DAY_PAL["sky_top"]),
             (0.52, DAY_PAL["sky_mid"]),
             (0.86, DAY_PAL["sky_bot"]),
             (1.0, DAY_PAL["horizon"])]
    rows = s(Y_FAR)
    for i in range(rows):
        t = i / max(1, rows - 1)
        col = None
        for k in range(len(stops) - 1):
            t0, c0 = stops[k]
            t1, c1 = stops[k + 1]
            if t <= t1:
                col = lerp_color(c0, c1, (t - t0) / (t1 - t0))
                break
        pygame.draw.line(geo, col or stops[-1][1], (0, i), (W * SS, i))


# ── apron ────────────────────────────────────────────────────────────────────

def draw_apron():
    for yy in range(s(Y_FAR), H * SS):
        y = yy / SS
        pygame.draw.line(geo, ymix(APRON_STOPS, y), (0, yy), (W * SS, yy))

    # Sparse scuff so the surround is not a dead flat fill; density thins with
    # distance the same way the pavement grain does.
    rng = random.Random(4021)
    scuff = new_layer()
    for _ in range(2600):
        y = Y_FAR + (H - Y_FAR) * (rng.random() ** 0.6)
        x = rng.uniform(0, W)
        xl, xr = edges_at_y(y)
        if xl - 3 < x < xr + 3:
            continue
        a = int(20 + 34 * rng.random())
        r = max(1, int(SS * (0.4 + 0.9 * scale_at_y(y))))
        c = (18, 30, 24) if rng.random() < 0.62 else (140, 160, 140)
        pygame.draw.circle(scuff, (*c, a), (s(x), s(y)), r)
    geo.blit(scuff, (0, 0))


# ── pavement ─────────────────────────────────────────────────────────────────

def draw_pavement():
    SEGS = 12
    y0, y1 = s(Y_FAR), s(Y_NEAR)
    for yy in range(y0, y1 + 1):
        y = yy / SS
        t = (Y_NEAR - y) / (Y_NEAR - Y_FAR)
        base = lerp_color(PAV_NEAR, PAV_FAR, smoothstep(t))
        xl, xr = edges_at_y(y)
        span = xr - xl
        for k in range(SEGS):
            u = (k + 0.5) / SEGS * 2 - 1
            # Pavement is crowned: the shoulders fall away from the light.
            f = 1.0 - 0.13 * (abs(u) ** 2.1)
            col = (int(base[0] * f), int(base[1] * f), int(base[2] * f))
            ax = s(xl + span * k / SEGS)
            bx = s(xl + span * (k + 1) / SEGS)
            pygame.draw.line(geo, col, (ax, yy), (bx, yy))

    # Aggregate grain.
    rng = random.Random(9137)
    grain = new_layer()
    for _ in range(5200):
        y = Y_FAR + (Y_NEAR - Y_FAR) * (rng.random() ** 0.55)
        xl, xr = edges_at_y(y)
        x = rng.uniform(xl, xr)
        sc = scale_at_y(y)
        a = int((14 + 30 * rng.random()) * (0.35 + 0.65 * sc))
        r = max(1, int(SS * 0.45 * sc + 0.5))
        c = (120, 96, 70) if rng.random() < 0.6 else (255, 246, 226)
        pygame.draw.circle(grain, (*c, a), (s(x), s(y)), r)
    clip_to_pavement(grain)
    geo.blit(grain, (0, 0))

    # Material lip at the pavement edge plus a contact shadow on the apron —
    # the runway is a raised slab, not a decal.
    lip = new_layer()
    for yy in range(y0, y1 + 1):
        y = yy / SS
        xl, xr = edges_at_y(y)
        t = (Y_NEAR - y) / (Y_NEAR - Y_FAR)
        a = int(150 - 60 * t)
        lw = max(1, int(SS * 0.9))
        pygame.draw.line(lip, (255, 244, 222, a), (s(xl), yy), (s(xl) + lw, yy))
        pygame.draw.line(lip, (255, 244, 222, a), (s(xr) - lw, yy), (s(xr), yy))
        sh = max(1, int(SS * (1.0 + 1.8 * (1 - t))))
        pygame.draw.line(lip, (14, 24, 20, int(90 - 40 * t)),
                         (s(xl) - sh, yy), (s(xl), yy))
        pygame.draw.line(lip, (14, 24, 20, int(90 - 40 * t)),
                         (s(xr), yy), (s(xr) + sh, yy))
    geo.blit(lip, (0, 0))


def draw_distance_haze():
    """Atmospheric recession on the lit half — the runway ahead does not dim,
    it dissolves."""
    haze = new_layer()
    for yy in range(s(Y_FAR), s(340.0)):
        y = yy / SS
        t = (340.0 - y) / (340.0 - Y_FAR)
        a = int(78 * smoothstep(t) ** 1.15)
        pygame.draw.line(haze, (*HAZE, a), (0, yy), (W * SS, yy))
    clip_to_pavement(haze)
    geo.blit(haze, (0, 0))


def draw_sun_streaks():
    """Low-angle light running up the unflown pavement; keeps the ahead half
    reading as lit rather than merely undrawn."""
    lay = new_layer()
    rng = random.Random(77)
    for i in range(6):
        p0 = DEATH_PHASE + (1.0 - DEATH_PHASE) * (i / 6.0) + rng.uniform(0, 0.04)
        p1 = min(1.0, p0 + rng.uniform(0.09, 0.20))
        ya, yb = phase_to_y(p0), phase_to_y(p1)
        u = rng.uniform(-0.60, 0.60)
        wa, wb = 0.52 * hw_at_y(ya), 0.52 * hw_at_y(yb)
        xa, xb = CX + u * hw_at_y(ya), CX + u * hw_at_y(yb)
        # Broad and faint: light, not a painted stripe. Anything stronger
        # competes with the centreline for the eye.
        pygame.draw.polygon(lay, (255, 246, 216, 10), [
            (s(xa - wa / 2), s(ya)), (s(xa + wa / 2), s(ya)),
            (s(xb + wb / 2), s(yb)), (s(xb - wb / 2), s(yb))])
    clip_to_pavement(lay)
    geo.blit(lay, (0, 0), special_flags=pygame.BLEND_ADD)


# ── markings: centreline + thresholds only ───────────────────────────────────

def paint_at_y(y):
    t = (Y_NEAR - y) / (Y_NEAR - Y_FAR)
    base = lerp_color(PAINT_NEAR, PAINT_FAR, smoothstep(t))
    pav = lerp_color(PAV_NEAR, PAV_FAR, smoothstep(t))
    return lerp_color(base, pav, 0.15 * t)


def draw_centreline():
    lay = new_layer()
    p = 0.012
    step = 0.0250
    dash = 0.0152
    while p < 0.995:
        pa, pb = p, min(0.995, p + dash)
        ya, yb = phase_to_y(pa), phase_to_y(pb)
        wa = 3.5 * scale_at_y(ya)
        wb = 3.5 * scale_at_y(yb)
        col = paint_at_y((ya + yb) * 0.5)
        pygame.draw.polygon(lay, (*col, 250), [
            (s(CX - wa / 2), s(ya)), (s(CX + wa / 2), s(ya)),
            (s(CX + wb / 2), s(yb)), (s(CX - wb / 2), s(yb))])
        p += step
    geo.blit(lay, (0, 0))


def _threshold_bank(y_base, y_top, spread, stripe_w, gap0):
    """Eight stripes symmetric about the centreline, per the real threshold
    convention — the one marking that says 'runway' with no words."""
    lay = new_layer()
    sb = scale_at_y(y_base)
    st = scale_at_y(y_top)
    col_b = paint_at_y(y_base)
    col_t = paint_at_y(y_top)
    col = lerp_color(col_b, col_t, 0.4)
    for i in range(4):
        o0 = gap0 + i * (stripe_w + spread)
        o1 = o0 + stripe_w
        for sgn in (-1, 1):
            pygame.draw.polygon(lay, (*col, 245), [
                (s(CX + sgn * o0 * sb), s(y_base)),
                (s(CX + sgn * o1 * sb), s(y_base)),
                (s(CX + sgn * o1 * st), s(y_top)),
                (s(CX + sgn * o0 * st), s(y_top))])
    clip_to_pavement(lay)
    geo.blit(lay, (0, 0))


def draw_thresholds():
    # Eight bars spanning ~80% of the half-width; a narrower bank stops
    # reading as a threshold and starts reading as touchdown-zone clutter.
    _threshold_bank(Y_NEAR - 0.5, Y_NEAR - 27.0, spread=8.0, stripe_w=12.0,
                    gap0=6.0)
    _threshold_bank(Y_FAR + 5.0, Y_FAR + 0.5, spread=8.0, stripe_w=12.0,
                    gap0=6.0)


# ── flown section: marked, never dimmed ──────────────────────────────────────

def draw_rubber_and_scorch():
    lay = new_layer()
    yy0, yy1 = s(DEATH_Y), s(Y_NEAR)
    for yy in range(yy0, yy1 + 1):
        y = yy / SS
        # Rubber accumulates toward the threshold: that end saw the whole run.
        t = (y - DEATH_Y) / (Y_NEAR - DEATH_Y)
        sc = scale_at_y(y)
        peak = 118 * smoothstep(t) ** 0.75
        for sgn in (-1, 1):
            for k in range(10):
                u0 = 5.0 + 20.0 * (k / 10.0)
                u1 = 5.0 + 20.0 * ((k + 1) / 10.0)
                # Soft shoulders on the band so it reads as deposit, not a stripe.
                f = math.sin(math.pi * (k + 0.5) / 10.0) ** 0.7
                a = int(peak * f)
                if a <= 1:
                    continue
                x0 = CX + sgn * u0 * sc
                x1 = CX + sgn * u1 * sc
                pygame.draw.line(lay, (*RUBBER, a),
                                 (s(min(x0, x1)), yy), (s(max(x0, x1)), yy))

    rng = random.Random(313)
    for i in range(9):
        p = rng.uniform(0.005, DEATH_PHASE - 0.004)
        y = phase_to_y(p)
        sc = scale_at_y(y)
        x = CX + rng.uniform(-0.55, 0.55) * hw_at_y(y)
        rad = rng.uniform(7, 17) * sc
        pts = []
        for k in range(11):
            ang = 2 * math.pi * k / 11
            rr = rad * (0.62 + 0.5 * rng.random())
            pts.append((s(x + math.cos(ang) * rr),
                        s(y + math.sin(ang) * rr * 0.55)))
        pygame.draw.polygon(lay, (*SCORCH, int(34 + 30 * rng.random())), pts)

    clip_to_pavement(lay)
    geo.blit(lay, (0, 0))


# ── skid arc ─────────────────────────────────────────────────────────────────

def _bez(p0, p1, p2, t):
    u = 1 - t
    return (u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
            u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1])


def _taper_strip(lay, pts, w0, w1, col, alpha):
    left, right = [], []
    n = len(pts)
    for i, (x, y) in enumerate(pts):
        t = i / (n - 1)
        w = w0 + (w1 - w0) * t
        j = min(n - 1, i + 1)
        k = max(0, i - 1)
        dx = pts[j][0] - pts[k][0]
        dy = pts[j][1] - pts[k][1]
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L, dx / L
        left.append((s(x + nx * w / 2), s(y + ny * w / 2)))
        right.append((s(x - nx * w / 2), s(y - ny * w / 2)))
    pygame.draw.polygon(lay, (*col, alpha), left + right[::-1])


def draw_skid():
    p0 = (CX + 1.0, phase_to_y(0.052))
    p1 = (CX - 6.0, phase_to_y(0.128))
    p2 = (134.0, DEATH_Y)
    pts = [_bez(p0, p1, p2, i / 46.0) for i in range(47)]
    lay = new_layer()
    _taper_strip(lay, pts, 11.0, 5.0, (30, 22, 20), 46)     # smear halo
    _taper_strip(lay, pts, 5.6, 2.4, (40, 28, 24), 215)     # rubber core
    _taper_strip(lay, pts[28:], 3.0, 1.6, SCARLET, 90)      # last contact
    clip_to_pavement(lay)
    geo.blit(lay, (0, 0))


# ── phase boundary bars + biome chips ────────────────────────────────────────

def draw_phase_bars():
    lay = new_layer()
    for p, _name in PHASE_BOUNDARIES:
        y = phase_to_y(p)
        yy = s(y)
        body_h = max(1, int(SS * 1.9))
        xl, xr = edges_at_y(y)
        # Over the apron the bar is a quiet rule; over the warm pavement it is
        # a cool band, so the temperature flip does the phase-change reading.
        pygame.draw.rect(lay, (46, 70, 84, 120), (0, yy, s(W), body_h))
        pygame.draw.rect(lay, (*BAR_BODY, 138),
                         (s(xl), yy, s(xr) - s(xl), body_h))
        pygame.draw.line(lay, (*BAR_EDGE, 150), (0, yy - 1), (s(W), yy - 1))
        pygame.draw.line(lay, (*BAR_EDGE, 215), (s(xl), yy - 1), (s(xr), yy - 1))
    geo.blit(lay, (0, 0))


def draw_chip(surface, cx, cy, phase, size=8):
    pal = palette_for_phase(phase)
    half = size / 2.0
    chip = pygame.Surface((s(size), s(size)), pygame.SRCALPHA)
    rows = s(size)
    for i in range(rows):
        t = i / max(1, rows - 1)
        if t < 0.5:
            col = lerp_color(pal["sky_top"], pal["sky_mid"], t * 2)
        else:
            col = lerp_color(pal["sky_mid"], pal["sky_bot"], (t - 0.5) * 2)
        pygame.draw.line(chip, col, (0, i), (s(size), i))
    mask = pygame.Surface((s(size), s(size)), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=s(2))
    chip.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surface.blit(chip, (s(cx - half), s(cy - half)))
    pygame.draw.rect(surface, (*CREAM, 210),
                     (s(cx - half), s(cy - half), s(size), s(size)),
                     max(1, int(SS * 0.5)), border_radius=s(2))


# ── event glyph boards ───────────────────────────────────────────────────────

def g_plume(lay, cx, cy, u, col):
    for sgn, lean in ((-1, 0.62), (0, 0.0), (1, 0.62)):
        tipx = cx + sgn * lean * u
        tipy = cy - u * (1.15 if sgn == 0 else 0.92)
        pygame.draw.polygon(lay, (*col, 255), [
            (s(cx - 0.22 * u), s(cy + 0.72 * u)),
            (s(cx + 0.22 * u), s(cy + 0.72 * u)),
            (s(tipx + 0.10 * u), s(tipy)),
            (s(tipx - 0.10 * u), s(tipy))])
    pygame.draw.ellipse(lay, (*col, 235),
                        (s(cx - 0.62 * u), s(cy + 0.60 * u),
                         s(1.24 * u), s(0.34 * u)))
    for dx, dy, r in ((-0.86, -0.28, 0.15), (0.86, -0.42, 0.13)):
        pygame.draw.circle(lay, (*col, 220),
                           (s(cx + dx * u), s(cy + dy * u)), max(1, s(r * u)))


def g_lamp(lay, cx, cy, u, col):
    pygame.draw.ellipse(lay, (*col, 255),
                        (s(cx - 0.72 * u), s(cy - 0.18 * u),
                         s(1.28 * u), s(0.72 * u)))
    pygame.draw.polygon(lay, (*col, 255), [
        (s(cx + 0.48 * u), s(cy + 0.02 * u)),
        (s(cx + 1.16 * u), s(cy - 0.46 * u)),
        (s(cx + 0.52 * u), s(cy + 0.34 * u))])
    pygame.draw.circle(lay, (*col, 255), (s(cx - 0.10 * u), s(cy - 0.26 * u)),
                       max(1, s(0.16 * u)))
    pygame.draw.circle(lay, (*col, 255), (s(cx - 0.78 * u), s(cy + 0.20 * u)),
                       max(2, s(0.30 * u)), max(1, s(0.11 * u)))
    for k, (dx, dy, r) in enumerate(((0.62, -0.72, 0.13),
                                     (0.86, -1.02, 0.10),
                                     (0.58, -1.26, 0.08))):
        pygame.draw.circle(lay, (*col, 210 - k * 40),
                           (s(cx + dx * u), s(cy + dy * u)), max(1, s(r * u)))


def g_diamond(lay, cx, cy, u, col):
    outer = [(s(cx), s(cy - u)), (s(cx + 0.74 * u), s(cy)),
             (s(cx), s(cy + u)), (s(cx - 0.74 * u), s(cy))]
    pygame.draw.polygon(lay, (*col, 255), outer)
    # Harlequin quartering — the clown gauntlet reads at 12 px this way.
    pygame.draw.polygon(lay, (*CREAM, 245), [
        (s(cx), s(cy - u)), (s(cx + 0.74 * u), s(cy)), (s(cx), s(cy))])
    pygame.draw.polygon(lay, (*CREAM, 245), [
        (s(cx), s(cy + u)), (s(cx - 0.74 * u), s(cy)), (s(cx), s(cy))])
    pygame.draw.circle(lay, (*col, 255), (s(cx), s(cy - 1.34 * u)),
                       max(1, s(0.17 * u)))


def g_drop(lay, cx, cy, u, col):
    pygame.draw.polygon(lay, (*col, 255), [
        (s(cx), s(cy - 1.05 * u)),
        (s(cx + 0.52 * u), s(cy + 0.34 * u)),
        (s(cx - 0.52 * u), s(cy + 0.34 * u))])
    pygame.draw.circle(lay, (*col, 255), (s(cx), s(cy + 0.30 * u)),
                       max(1, s(0.53 * u)))
    pygame.draw.circle(lay, (*CREAM, 190), (s(cx - 0.18 * u), s(cy + 0.22 * u)),
                       max(1, s(0.14 * u)))


def g_asterism(lay, cx, cy, u, col):
    for k in range(6):
        a = math.pi * k / 3.0
        ex, ey = cx + math.cos(a) * u, cy + math.sin(a) * u
        nx, ny = -math.sin(a), math.cos(a)
        t = 0.11 * u
        pygame.draw.polygon(lay, (*col, 255), [
            (s(cx + nx * t), s(cy + ny * t)), (s(cx - nx * t), s(cy - ny * t)),
            (s(ex - nx * t), s(ey - ny * t)), (s(ex + nx * t), s(ey + ny * t))])
        bx, by = cx + math.cos(a) * 0.58 * u, cy + math.sin(a) * 0.58 * u
        for ba in (a + 0.72, a - 0.72):
            fx, fy = bx + math.cos(ba) * 0.32 * u, by + math.sin(ba) * 0.32 * u
            pygame.draw.polygon(lay, (*col, 255), [
                (s(bx + nx * t * 0.8), s(by + ny * t * 0.8)),
                (s(bx - nx * t * 0.8), s(by - ny * t * 0.8)),
                (s(fx), s(fy))])
    pygame.draw.circle(lay, (*col, 255), (s(cx), s(cy)), max(1, s(0.2 * u)))


def draw_board(lay, y, glyph, tint, out=0.0):
    """Edge-lit plaque staked just outside the right runway edge, scaled by
    depth so the far events sit back without going illegible."""
    xr = edges_at_y(y)[1]
    sc = 0.60 + 0.40 * scale_at_y(y)
    bw, bh = 21.0 * sc, 17.5 * sc
    bx = xr + 7.0 + out
    r = pygame.Rect(s(bx), s(y - bh / 2), s(bw), s(bh))

    pygame.draw.line(lay, (*tint, 150), (s(xr), s(y)), (s(bx), s(y)),
                     max(1, int(SS * 0.7)))
    pygame.draw.line(lay, (*tint, 235), (s(xr - 3.5 * sc), s(y)),
                     (s(xr + 0.5), s(y)), max(1, int(SS * 1.1)))

    sh = r.move(0, s(1.4 * sc))
    pygame.draw.rect(lay, (10, 16, 22, 90), sh, border_radius=s(3 * sc))
    pygame.draw.rect(lay, (*SLATE, 240), r, border_radius=s(3 * sc))
    pygame.draw.rect(lay, (*tint, 120), r, max(1, int(SS * 0.55)),
                     border_radius=s(3 * sc))
    pygame.draw.line(lay, (*tint, 235), (r.left + s(2 * sc), r.top),
                     (r.right - s(2 * sc), r.top), max(1, int(SS * 0.7)))

    glyph(lay, bx + bw / 2, y, 4.6 * sc, tint)


def draw_events():
    lay = new_layer()

    # Geyser span bracket: the run ended INSIDE the thermal window, and the
    # bracket straddling the death line is what proves the two are distinct.
    ya, yb = phase_to_y(THERMAL_START_PHASE), phase_to_y(THERMAL_END_PHASE)
    amber = (255, 186, 92)
    steps = 60
    for i in range(steps):
        t0, t1 = i / steps, (i + 1) / steps
        y0 = ya + (yb - ya) * t0
        y1 = ya + (yb - ya) * t1
        x0 = edges_at_y(y0)[1] + 3.2
        x1 = edges_at_y(y1)[1] + 3.2
        # Bracket runs through the death line: its lower stub is flown, its
        # long lit run is the part of the thermal the player never saw.
        a = 235 if y0 < DEATH_Y else 95
        pygame.draw.line(lay, (*amber, a), (s(x0), s(y0)), (s(x1), s(y1)),
                         max(1, int(SS * 1.4)))
    for yt in (ya, yb):
        xt = edges_at_y(yt)[1] + 3.2
        a = 235 if yt < DEATH_Y else 130
        pygame.draw.line(lay, (*amber, a), (s(xt - 2.2), s(yt)),
                         (s(xt + 5.0), s(yt)), max(1, int(SS * 1.2)))

    draw_board(lay, phase_to_y(THERMAL_START_PHASE), g_plume, amber)
    draw_board(lay, phase_to_y(GENIE_PHASE), g_lamp, (255, 214, 120))
    draw_board(lay, phase_to_y(CLOWN_PHASE), g_diamond, (255, 120, 190))
    # Rain sits 12 px above the clown gauntlet — stepped outboard rather than
    # stacked, so both keep their true phase row.
    draw_board(lay, phase_to_y(RAIN_PHASE), g_drop, (130, 200, 255), out=22.0)
    draw_board(lay, phase_to_y(SNOW_PHASE), g_asterism, (206, 236, 255))

    geo.blit(lay, (0, 0))


# ── death marker ─────────────────────────────────────────────────────────────

def draw_death_marker():
    lay = new_layer()
    xl, xr = edges_at_y(DEATH_Y)
    yy = s(DEATH_Y)
    for k, a in ((3.4, 30), (1.9, 58)):
        pygame.draw.line(lay, (*SCARLET, a), (s(xl - 14), yy), (s(xr + 14), yy),
                         max(1, int(SS * k * 2)))
    pygame.draw.line(lay, (*SCARLET, 215), (s(xl - 13), yy), (s(xr + 13), yy),
                     max(1, int(SS * 1.05)))
    for sgn, ex in ((-1, xl - 13), (1, xr + 13)):
        pygame.draw.line(lay, (*SCARLET, 215),
                         (s(ex), s(DEATH_Y - 3.5)), (s(ex), s(DEATH_Y + 3.5)),
                         max(1, int(SS * 0.8)))

    mx = 134.0
    pygame.draw.circle(lay, (*SCARLET, 80), (s(mx), yy), s(8.5))
    # Cream collar: scarlet alone is close to the pavement in value, so the
    # marker needs a light ring to punch out of warm stone.
    pygame.draw.circle(lay, (*CREAM, 245), (s(mx), yy), s(5.8))
    pygame.draw.circle(lay, (*SCARLET, 255), (s(mx), yy), s(4.5))
    pygame.draw.circle(lay, (*SCARLET_HI, 255), (s(mx), yy), s(2.4))
    pygame.draw.circle(lay, (24, 10, 12, 255), (s(mx), yy), s(1.0))

    pygame.draw.line(lay, (*SCARLET, 215), (s(70), yy), (s(mx - 6.6), yy),
                     max(1, int(SS * 0.8)))
    pygame.draw.circle(lay, (*SCARLET, 215), (s(70), yy), max(1, s(1.4)))
    geo.blit(lay, (0, 0))


# ── teaser plate + footer ────────────────────────────────────────────────────

TEASER = pygame.Rect(4, 505, 158, 44)


def draw_teaser_plate():
    body = pygame.Surface((s(TEASER.w), s(TEASER.h)), pygame.SRCALPHA)
    # Mid-value slate: the plate crosses a near-black apron AND lit pavement,
    # so it has to sit above one and below the other to read as one object.
    pygame.draw.rect(body, (46, 66, 82, 232), body.get_rect(),
                     border_radius=s(4))
    pygame.draw.rect(body, (158, 186, 202, 235), body.get_rect(),
                     max(1, int(SS * 0.6)), border_radius=s(4))
    pygame.draw.rect(body, (255, 206, 120, 240),
                     (s(1.4), s(5), s(2.4), s(TEASER.h - 10)))
    alpha = pygame.Surface((s(TEASER.w), s(TEASER.h)), pygame.SRCALPHA)
    for i in range(s(TEASER.w)):
        u = i / (s(TEASER.w) - 1)
        a = 255 if u < 0.58 else int(255 - 78 * ((u - 0.58) / 0.42) ** 1.3)
        pygame.draw.line(alpha, (255, 255, 255, a), (i, 0), (i, s(TEASER.h)))
    body.blit(alpha, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    # Fade the edge that crosses onto the pavement so the flown-surface
    # evidence still reads underneath it.
    geo.blit(body, (s(TEASER.x), s(TEASER.y)))


def draw_footer():
    pygame.draw.rect(geo, (16, 24, 30), (0, s(584), s(W), s(H - 584)))
    pygame.draw.line(geo, (62, 84, 96), (0, s(584)), (s(W), s(584)),
                     max(1, int(SS * 0.7)))
    pill = pygame.Rect(s(132), s(585), s(96), s(30))
    pygame.draw.rect(geo, (34, 50, 62), pill, border_radius=s(15))
    pygame.draw.rect(geo, (128, 158, 178), pill, max(1, int(SS * 0.8)),
                     border_radius=s(15))
    pygame.draw.polygon(geo, CREAM, [
        (s(150), s(600)), (s(157), s(595)), (s(157), s(605))])


# ── build the geometry pass ──────────────────────────────────────────────────

draw_sky()
draw_apron()
draw_pavement()
draw_centreline()
draw_thresholds()
draw_rubber_and_scorch()
draw_skid()
draw_sun_streaks()
draw_distance_haze()
draw_phase_bars()
draw_events()
draw_death_marker()
draw_teaser_plate()
draw_footer()

base = pygame.transform.smoothscale(geo, (W, H))


# ── clouds (drawn at native scale by the shared helper) ──────────────────────

sky_lay = pygame.Surface((W, H), pygame.SRCALPHA)
for (cx, cy, sc, var) in ((56, 60, 0.54, 0), (128, 79, 0.38, 1),
                          (246, 56, 0.48, 2), (322, 80, 0.32, 3)):
    draw_cloud(sky_lay, cx, cy, sc, var, DAY_PAL)
sky_lay.set_alpha(215)
clip = pygame.Surface((W, H), pygame.SRCALPHA)
clip.blit(sky_lay, (0, 0))
pygame.draw.rect(clip, (0, 0, 0, 0), (0, int(Y_FAR) - 1, W, H))
base.blit(clip, (0, 0))


# ── text pass at native resolution ───────────────────────────────────────────

FONT_PATH = os.path.join("game", "assets", "LiberationSans-Bold.ttf")
_FONTS = {}


def font(size):
    if size not in _FONTS:
        _FONTS[size] = pygame.font.Font(FONT_PATH, size)
    return _FONTS[size]


def text(msg, size, col, x, y, anchor="topleft", shadow=(0, 0, 0, 130),
         spacing=0.0):
    f = font(size)
    if spacing:
        parts = [f.render(ch, True, col) for ch in msg]
        wtot = sum(p.get_width() for p in parts) + spacing * (len(parts) - 1)
        surf = pygame.Surface((int(wtot) + 2, f.get_height()), pygame.SRCALPHA)
        cx = 0.0
        for p in parts:
            surf.blit(p, (int(cx), 0))
            cx += p.get_width() + spacing
    else:
        surf = f.render(msg, True, col)
    r = surf.get_rect(**{anchor: (x, y)})
    if shadow:
        # Silhouette of the already-composed glyph run, so letter-spaced
        # headings keep a shadow that matches their advance widths.
        sh = surf.copy()
        sh.fill(shadow[:3], special_flags=pygame.BLEND_RGB_MULT)
        sh.set_alpha(shadow[3])
        base.blit(sh, (r.x + 1, r.y + 1))
    base.blit(surf, r.topleft)
    return r


# header
text("FLIGHT LOG", 13, CREAM, 10, 9, spacing=0.8)
text(f"DAY {DAY_NO}  ·  {TIME_ALIVE} s ALIVE", 8, (206, 224, 240), 11, 27)
pct = text(f"{int(round(DEATH_PHASE * 100))}%", 17, CREAM, 350, 7, "topright")
text("OF DAY 1 FLOWN", 6, (198, 218, 234), 350, pct.bottom + 1, "topright")

# far threshold plaque
plq = pygame.Rect(0, 0, 62, 13)
plq.center = (int(CX), 90)
pygame.draw.rect(base, (22, 36, 46), plq, border_radius=6)
pygame.draw.rect(base, (128, 160, 180), plq, 1, border_radius=6)
text("DAY COMPLETE", 6, CREAM, plq.centerx, plq.centery, "center", shadow=None)

# phase names + biome chips, alternating aprons, never rotated
chip_lay = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
for i, (p, name) in enumerate(PHASE_BOUNDARIES):
    y = phase_to_y(p)
    right = (i % 2 == 0)
    f = font(8)
    tw = f.size(name)[0]
    if right:
        tx = W - 4
        r = text(name, 8, CREAM, tx, int(round(y)), "midright")
        draw_chip(chip_lay, r.left - 6.0, y, p)
    else:
        r = text(name, 8, CREAM, 4, int(round(y)), "midleft")
        draw_chip(chip_lay, r.right + 6.0, y, p)
base.blit(pygame.transform.smoothscale(chip_lay, (W, H)), (0, 0))

# death callout — horizontal, left apron
text("ENDED HERE", 9, SCARLET_HI, 5, int(DEATH_Y) - 12, "midleft")
text(f"PILLAR {DEATH_PILLAR}", 8, CREAM, 5, int(DEATH_Y) + 1, "midleft")
text(f"DAY {DEATH_PHASE:.3f}", 8, (214, 226, 234), 5, int(DEATH_Y) + 13,
     "midleft")

# teaser strip
line1 = f"STILL AHEAD: GENIE LAMP AT PILLAR {LATE_GAME_PILLAR} ·"
line2 = (f"CLOWN GAUNTLET AT PILLAR {CLOWN_START_PILLAR} · "
         f"STORM AT {RAIN_START_PILLAR}")
tsize = 8
while tsize > 5 and max(font(tsize).size(line1)[0],
                        font(tsize).size(line2)[0]) > TEASER.w - 11:
    tsize -= 1
text(line1, tsize, CREAM, TEASER.x + 7, TEASER.centery - 7, "midleft")
text(line2, tsize, (226, 234, 240), TEASER.x + 7, TEASER.centery + 6, "midleft")

# footer
text("BACK", 12, CREAM, 190, 600, "center")

pygame.image.save(base, os.path.join(
    "docs", "flight_log_progress", "runway_view", "round_1.png"))
print("phase rows:", [(n, round(phase_to_y(p), 1)) for p, n in PHASE_BOUNDARIES])
print("death y", round(DEATH_Y, 1),
      "geyser-start y", round(phase_to_y(THERMAL_START_PHASE), 1),
      "separation px", round(phase_to_y(THERMAL_START_PHASE) - DEATH_Y, 1))
print("flown band px", round(Y_NEAR - DEATH_Y, 1),
      "= %.1f%% of runway for %.1f%% of day"
      % (100 * (Y_NEAR - DEATH_Y) / (Y_NEAR - Y_FAR), 100 * DEATH_PHASE))
