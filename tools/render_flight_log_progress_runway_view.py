#!/usr/bin/env python3
"""
runway-view  ·  flight_log_progress  ·  round 2

The day cycle read as a single receding corridor in one-point perspective: the
run is a flight down a sandstone canyon that ran out of daylight. Foreshortening
is still the whole argument — the flown 18.4% of the day eats ~30% of the
corridor's screen height, so near events that would collide on a linear timeline
separate on their own.

Round 2 rebuilds the vocabulary. The corridor is Skybit's, not an airport's:
coins mark the centreline, a launch rock caps the near end, pillar-top markers
carry the event glyphs, and the flown stretch is written in shed feathers and a
wing-tip scuff rather than tyre rubber. The far threshold gained the object the
whole composition was missing — a two-pillar gate with the day's last light
pouring through it, dark against the sky so the horizon finally reads.

Flown vs ahead is now an event rather than a ramp: the flown stone drops ~42
luminance points into cool desaturated shade, the ahead stone holds its value
and gains chroma all the way to the gate, and a hard sunlit lip sits on the
ahead side of the death line.

Run from the repo root:  python tools/render_flight_log_progress_runway_view.py
"""
import os
import math
import random
import colorsys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.draw import (lerp_color, draw_cloud, COIN_GOLD, COIN_DARK,
                       BIRD_RED, BIRD_RED_D, BIRD_WING, BIRD_WING_D,
                       BIRD_TIP, BIRD_BEAK)
from game.biome import PHASE_BOUNDARIES, palette_for_phase
from game.weather import (THERMAL_START_PHASE, THERMAL_PEAK_PHASE,
                          THERMAL_END_PHASE, SNOW_STORM_CENTER)
from game.config import LATE_GAME_PILLAR, CLOWN_START_PILLAR, RAIN_START_PILLAR


# ── canvas + perspective frame ───────────────────────────────────────────────

W, H = 360, 640
SS = 3                      # supersample factor for the geometry pass

# The far end sits just under the header rather than a third of the way down
# the canvas: every pixel bought back up here goes straight into the four
# compressed late-day bands, which were the first thing to become unreadable.
Y_NEAR, Y_FAR = 560.0, 62.0
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


def bump(t):
    """0 at both ends, 1 in the middle — for effects that live in a band."""
    t = max(0.0, min(1.0, t))
    return math.sin(math.pi * t) ** 1.4


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


def clamp8(v):
    return max(0, min(255, int(round(v))))


def luma(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


# ── palette ──────────────────────────────────────────────────────────────────

DAY_PAL = palette_for_phase(0.0)

# Sandstone ramp keyed on depth. Value is held flat (luma ≈ 177 at every stop)
# while chroma climbs toward the gate — distance reads as saturation here, not
# as fading, so the unflown stretch never looks spent.
SAND_STOPS = [(62.0, (228, 168, 92)),
              (250.0, (214, 170, 112)),
              (560.0, (204, 172, 132))]

HAZE = (238, 230, 208)
GATE_WARM = (255, 196, 110)

BAR_BODY = (74, 108, 132)
BAR_EDGE = (170, 206, 226)

SCARLET = (232, 62, 58)
SCARLET_HI = (255, 132, 112)

CREAM = (246, 240, 226)
BOARD_BODY = (13, 19, 27)
BOARD_HALO = (5, 9, 13)

STONE_DK = (58, 42, 34)             # gate pillars, read as near-silhouette
STONE_DKR = (38, 27, 22)
STONE_RIM = (255, 206, 132)
CROWN_DK = (22, 40, 28)

# Apron stays below the corridor in value at every depth; re-keyed for the new
# far edge so the recession still starts at the horizon and not above it.
APRON_STOPS = [(62.0, (150, 168, 150)),
               (132.0, (104, 132, 110)),
               (330.0, (56, 80, 66)),
               (640.0, (26, 40, 35))]


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


def clip_to_corridor(layer):
    layer.blit(PAV_MASK, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)


# ── the flown / ahead split ──────────────────────────────────────────────────

def shade_flown(col):
    """Stone the bird has already passed: dropped in value, pulled almost grey,
    tipped toward blue. Shade, not dirt — the surface is identical, the light
    on it is gone."""
    h, l, sat = colorsys.rgb_to_hls(*[c / 255.0 for c in col])
    r, g, b = colorsys.hls_to_rgb(h, max(0.0, l - 0.158), 0.18)
    return (clamp8(r * 255 - 3), clamp8(g * 255 + 1), clamp8(b * 255 + 9))


def sand_at_y(y):
    """Corridor stone before the flown/ahead treatment."""
    base = ymix(SAND_STOPS, y)

    # Mist sits in ONE band in the middle distance instead of a global fade, so
    # the far end can stay the most chromatic stone on screen.
    if 150.0 < y < 262.0:
        base = lerp_color(base, HAZE, 0.32 * bump((y - 150.0) / 112.0))

    # Last stretch before the gate picks the gate's own warmth back up.
    if y < 112.0:
        base = lerp_color(base, GATE_WARM, 0.35 * smoothstep((112.0 - y) / 50.0))

    if y > DEATH_Y:
        base = shade_flown(base)
        # A short cast shadow under the death line makes the change an edge
        # rather than a boundary you have to be told about.
        k = 1.0 - smoothstep((y - DEATH_Y) / 18.0)
        base = (clamp8(base[0] - 22 * k), clamp8(base[1] - 20 * k),
                clamp8(base[2] - 14 * k))
    return base


# ── sky ──────────────────────────────────────────────────────────────────────

def draw_sky():
    stops = [(0.0, DAY_PAL["sky_top"]),
             (0.50, DAY_PAL["sky_mid"]),
             (0.84, DAY_PAL["sky_bot"]),
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

    # The mid-distance mist band crosses the whole ground plane, so the apron
    # carries it too — otherwise the corridor looks mis-painted, not hazed.
    mist = new_layer()
    for yy in range(s(150.0), s(262.0)):
        y = yy / SS
        a = int(64 * bump((y - 150.0) / 112.0))
        pygame.draw.line(mist, (*HAZE, a), (0, yy), (W * SS, yy))
    geo.blit(mist, (0, 0))


# ── corridor stone ───────────────────────────────────────────────────────────

def draw_corridor():
    SEGS = 14
    y0, y1 = s(Y_FAR), s(Y_NEAR)
    for yy in range(y0, y1 + 1):
        y = yy / SS
        base = sand_at_y(y)
        xl, xr = edges_at_y(y)
        span = xr - xl
        for k in range(SEGS):
            u = (k + 0.5) / SEGS * 2 - 1
            # The floor is crowned: the shoulders fall away from the light.
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
    clip_to_corridor(grain)
    geo.blit(grain, (0, 0))

    # Material lip at the corridor edge plus a contact shadow on the apron —
    # the floor is a raised slab, not a decal. The lip goes dull where the
    # stone is in shade so the edge does not smuggle light into the flown half.
    lip = new_layer()
    for yy in range(y0, y1 + 1):
        y = yy / SS
        xl, xr = edges_at_y(y)
        t = (Y_NEAR - y) / (Y_NEAR - Y_FAR)
        lit = y < DEATH_Y
        col = (255, 244, 222) if lit else (150, 152, 152)
        a = int((150 - 60 * t) * (1.0 if lit else 0.52))
        lw = max(1, int(SS * 0.9))
        pygame.draw.line(lip, (*col, a), (s(xl), yy), (s(xl) + lw, yy))
        pygame.draw.line(lip, (*col, a), (s(xr) - lw, yy), (s(xr), yy))
        sh = max(1, int(SS * (1.0 + 1.8 * (1 - t))))
        pygame.draw.line(lip, (14, 24, 20, int(90 - 40 * t)),
                         (s(xl) - sh, yy), (s(xl), yy))
        pygame.draw.line(lip, (14, 24, 20, int(90 - 40 * t)),
                         (s(xr), yy), (s(xr) + sh, yy))
    geo.blit(lip, (0, 0))


def draw_death_lip():
    """The hard sunlit edge on the AHEAD side of the death line: the last inch
    of stone the light still reaches. Two whole native rows of near-white —
    anything thinner averages away when the supersample is resolved down."""
    lay = new_layer()
    for y0, y1, col, a in ((DEATH_Y - 5.4, DEATH_Y - 3.0, (255, 214, 158), 70),
                           (DEATH_Y - 3.0, DEATH_Y - 2.0, (255, 240, 208), 190),
                           (DEATH_Y - 2.0, DEATH_Y - 0.1, (255, 253, 247), 255)):
        xl0, xr0 = edges_at_y(y0)
        xl1, xr1 = edges_at_y(y1)
        pygame.draw.polygon(lay, (*col, a), [
            (s(xl0 + 1), s(y0)), (s(xr0 - 1), s(y0)),
            (s(xr1 - 1), s(y1)), (s(xl1 + 1), s(y1))])
    clip_to_corridor(lay)
    geo.blit(lay, (0, 0))


def draw_gate_light():
    """Light pouring back down the corridor FROM the gate: wedges that converge
    on the far gap, so the destination is also the light source."""
    lay = new_layer()
    rng = random.Random(77)
    for i in range(7):
        y_far_edge = Y_FAR + rng.uniform(0.0, 6.0)
        y_near_edge = phase_to_y(DEATH_PHASE + rng.uniform(0.05, 0.62))
        u = rng.uniform(-0.72, 0.72)
        xa = CX + u * 0.30 * hw_at_y(y_far_edge)
        xb = CX + u * hw_at_y(y_near_edge)
        # BLEND_ADD reads RGB and ignores source alpha, so intensity has to
        # live in the channels. Three nested wedges fake a soft falloff.
        for span, lift in ((0.50, 5), (0.30, 6), (0.13, 6)):
            wa = span * hw_at_y(y_far_edge) * 0.35
            wb = span * hw_at_y(y_near_edge)
            pygame.draw.polygon(lay, (lift + 3, lift, max(0, lift - 4), 255), [
                (s(xa - wa / 2), s(y_far_edge)), (s(xa + wa / 2), s(y_far_edge)),
                (s(xb + wb / 2), s(y_near_edge)), (s(xb - wb / 2), s(y_near_edge))])
    clip_to_corridor(lay)
    geo.blit(lay, (0, 0), special_flags=pygame.BLEND_ADD)


# ── the gate: two pillars + the last light of the day between them ───────────

def gate_pillar_pts(bx, by, h, w, flip):
    """Skybit sandstone column language at silhouette scale: stepped plinth,
    tapered shaft with erosion notches, overhanging capital."""
    sgn = -1.0 if flip else 1.0

    def P(u, v):
        return (s(bx + sgn * u * w), s(by - v * h))

    return [
        P(-0.62, 0.00), P(-0.62, 0.07), P(-0.50, 0.085),
        P(-0.44, 0.17), P(-0.48, 0.40), P(-0.37, 0.50),
        P(-0.43, 0.72), P(-0.36, 0.83),
        P(-0.60, 0.840), P(-0.60, 0.900), P(-0.46, 0.912),
        P(-0.51, 0.962), P(0.50, 0.988),
        P(0.45, 0.912), P(0.58, 0.900), P(0.58, 0.840),
        P(0.35, 0.830), P(0.40, 0.58), P(0.32, 0.42),
        P(0.42, 0.19), P(0.50, 0.085), P(0.62, 0.07), P(0.62, 0.00),
    ]


def draw_gate_glow():
    """Warm bloom in the gap, drawn before the pillars so they cut into it."""
    lay = new_layer()
    gx, gy = CX, Y_FAR - 2.0
    for r, lift in ((70, 4), (52, 6), (36, 9), (23, 14), (13, 22), (6, 30)):
        pygame.draw.circle(lay, (lift + 6, int(lift * 0.78), int(lift * 0.30),
                                 255), (s(gx), s(gy)), s(r))
    # Rays fanning up and out of the gate mouth.
    rng = random.Random(515)
    for i in range(11):
        a0 = -math.pi / 2 + (i / 10.0 - 0.5) * 2.05
        wid = rng.uniform(0.035, 0.075)
        L = rng.uniform(30, 74)
        tip = (gx + math.cos(a0) * L, gy + math.sin(a0) * L)
        p1 = (gx + math.cos(a0 - wid) * 8, gy + math.sin(a0 - wid) * 8)
        p2 = (gx + math.cos(a0 + wid) * 8, gy + math.sin(a0 + wid) * 8)
        pygame.draw.polygon(lay, (9, 7, 3, 255),
                            [(s(p1[0]), s(p1[1])), (s(p2[0]), s(p2[1])),
                             (s(tip[0]), s(tip[1]))])
    geo.blit(lay, (0, 0), special_flags=pygame.BLEND_ADD)


GATE_H, GATE_W = 34.0, 32.0
# Inner faces overlap the corridor edge by ~3 px: the columns stand ON the rim
# of the canyon, so they occlude it rather than floating beside it.
GATE_CX_L = 148.0 - 0.62 * GATE_W
GATE_CX_R = 212.0 + 0.62 * GATE_W


def draw_gate_sill():
    """Dark stone at the far rim, opening up in the middle where the light
    actually pours through. Without it the sky and the corridor floor meet at
    the same value and the horizon disappears."""
    lay = new_layer()
    for yy in range(s(Y_FAR), s(Y_FAR + 9.0)):
        y = yy / SS
        xl, xr = edges_at_y(y)
        fade = 1.0 - smoothstep((y - Y_FAR) / 9.0)
        span = xr - xl
        for k in range(24):
            u = (k + 0.5) / 24 * 2 - 1
            a = int(180 * fade * (abs(u) ** 0.75))
            if a <= 2:
                continue
            pygame.draw.line(lay, (52, 36, 30, a),
                             (s(xl + span * k / 24), yy),
                             (s(xl + span * (k + 1) / 24), yy))
    clip_to_corridor(lay)
    geo.blit(lay, (0, 0))


def draw_gate_pillars():
    lay = new_layer()
    h, w = GATE_H, GATE_W
    for flip, bx in ((True, GATE_CX_L), (False, GATE_CX_R)):
        inner = 1.0 if flip else -1.0
        pts = gate_pillar_pts(bx, Y_FAR + 1.0, h, w, flip)

        # Ground shadow first: the sun is beyond the gate, so each column
        # throws its shadow straight back toward the viewer, and those two
        # dark wedges are what pin the horizon onto the ground plane.
        for i in range(s(24.0)):
            y = Y_FAR + 1.0 + i / SS
            t = i / float(s(24.0))
            a = int(135 * (1.0 - t) ** 1.35)
            x0 = bx - 0.62 * w - 2.0 * t
            x1 = bx + 0.62 * w + 6.0 * t * inner
            pygame.draw.line(lay, (26, 22, 24, a),
                             (s(min(x0, x1)), s(y)), (s(max(x0, x1)), s(y)))

        pygame.draw.polygon(lay, (*STONE_DK, 255), pts)

        # Strata: the only internal detail that survives at silhouette value.
        for v in (0.19, 0.33, 0.47, 0.61, 0.74):
            yy = s(Y_FAR + 1.0 - v * h)
            pygame.draw.line(lay, (*STONE_DKR, 190),
                             (s(bx - 0.46 * w), yy), (s(bx + 0.46 * w), yy),
                             max(1, int(SS * 0.5)))

        # Rim light on the edge facing the gap — the gate is backlit, so the
        # inner face is the only lit stone on the pillar.
        rx = bx + inner * 0.335 * w
        pygame.draw.line(lay, (*STONE_RIM, 210),
                         (s(rx), s(Y_FAR - 0.5)), (s(rx + inner * 1.2), s(Y_FAR - 0.80 * h)),
                         max(1, int(SS * 0.9)))
        pygame.draw.line(lay, (*STONE_RIM, 235),
                         (s(bx + inner * 0.50 * w), s(Y_FAR - 0.985 * h)),
                         (s(bx - inner * 0.10 * w), s(Y_FAR - 0.965 * h)),
                         max(1, int(SS * 0.8)))

        # Foliage crown — the columns are alive in game, and the tuft is what
        # says sandstone pillar rather than obelisk.
        rng = random.Random(int(bx))
        for i in range(9):
            fx = bx + rng.uniform(-0.44, 0.44) * w
            fy = Y_FAR + 1.0 - h * (0.985 + rng.uniform(0.0, 0.02))
            fl = rng.uniform(4.0, 8.5)
            lean = rng.uniform(-2.6, 2.6)
            pygame.draw.line(lay, (*CROWN_DK, 245), (s(fx), s(fy)),
                             (s(fx + lean), s(fy - fl)), max(1, int(SS * 0.7)))
    geo.blit(lay, (0, 0))


# ── centreline: a lane of coins, not paint ───────────────────────────────────

def draw_coin_lane():
    lay = new_layer()
    p = 0.010
    step = 0.0232
    while p < 0.995:
        y = phase_to_y(p)
        sc = scale_at_y(y)
        r = 3.4 * sc
        flown = y > DEATH_Y
        if flown:
            # Already banked: a dished socket in the shaded stone, lit on its
            # near rim. A hairline ring vanishes in the downscale, so the
            # empty coin has to be a solid form, not an outline.
            pygame.draw.circle(lay, (188, 178, 164, 165),
                               (s(CX), s(y + 0.32 * r)), max(2, s(r * 1.02)))
            pygame.draw.circle(lay, (44, 40, 42, 225),
                               (s(CX), s(y - 0.10 * r)), max(1, s(r * 0.92)))
        else:
            pygame.draw.circle(lay, (*COIN_DARK, 235), (s(CX), s(y)),
                               max(1, s(r * 1.16)))
            pygame.draw.circle(lay, (*COIN_GOLD, 255), (s(CX), s(y)),
                               max(1, s(r)))
            pygame.draw.circle(lay, (255, 244, 176, 255),
                               (s(CX - r * 0.28), s(y - r * 0.30)),
                               max(1, s(r * 0.42)))
            # Contact shadow keeps the coin sitting on the stone.
            pygame.draw.ellipse(lay, (70, 52, 38, 90),
                                (s(CX - r * 1.1), s(y + r * 0.60),
                                 s(r * 2.2), s(r * 0.85)))
        p += step
    clip_to_corridor(lay)
    geo.blit(lay, (0, 0))


# ── near end: the launch rock ────────────────────────────────────────────────

def draw_launch_rock():
    """The ledge the run started from. Replaces the painted threshold: a slab
    of the same sandstone, chipped along its lit top edge."""
    lay = new_layer()
    rng = random.Random(2201)
    top_y = Y_NEAR - 4.0
    bot_y = 582.0
    xl, xr = 72.0, 288.0

    face = [(s(xl), s(bot_y)), (s(xl + 6), s(top_y + 2))]
    x = xl + 6
    while x < xr - 6:
        step = rng.uniform(13.0, 26.0)
        x = min(xr - 6, x + step)
        face.append((s(x), s(top_y + rng.uniform(-2.2, 2.6))))
    face += [(s(xr - 6), s(top_y + 2)), (s(xr), s(bot_y))]
    pygame.draw.polygon(lay, (96, 70, 52, 255), face)

    # Lit cap: warm top plane above the shaded front face.
    cap = [(px, py) for (px, py) in face[1:-1]]
    cap = cap + [(s(xr - 10), s(top_y + 13)), (s(xl + 10), s(top_y + 13))]
    pygame.draw.polygon(lay, (198, 160, 116, 255), cap)
    for i in range(s(11)):
        t = i / s(11)
        col = lerp_color((222, 186, 140), (150, 116, 84), t)
        pygame.draw.line(lay, (*col, 190), (s(xl + 8), s(top_y + 2) + i),
                         (s(xr - 8), s(top_y + 2) + i))

    # Strata + chipped speckle on the front face.
    for v, a in ((0.34, 130), (0.58, 110), (0.80, 90)):
        yy = s(top_y + 13 + (bot_y - top_y - 13) * v)
        pygame.draw.line(lay, (66, 46, 34, a), (s(xl + 4), yy), (s(xr - 4), yy),
                         max(1, int(SS * 0.8)))
    for _ in range(240):
        px = rng.uniform(xl + 3, xr - 3)
        py = rng.uniform(top_y + 13, bot_y)
        c = (60, 42, 32) if rng.random() < 0.6 else (168, 136, 100)
        pygame.draw.circle(lay, (*c, int(40 + 60 * rng.random())),
                           (s(px), s(py)), max(1, int(SS * 0.6)))

    pygame.draw.line(lay, (255, 236, 200, 225), (s(xl + 7), s(top_y + 1.2)),
                     (s(xr - 7), s(top_y + 1.2)), max(1, int(SS * 0.9)))
    geo.blit(lay, (0, 0))


# ── flown stretch: feathers and a wing scuff, not rubber ─────────────────────

FEATHER_COLS = ((214, 66, 58), (186, 44, 42), (52, 96, 210),
                (232, 178, 60), (58, 168, 96))


def draw_feather(lay, x, y, ang, L, col, a=225):
    """Quill + two vane lobes. At 3–9 px this reads as 'a bird shed this'."""
    ca, sa = math.cos(ang), math.sin(ang)
    tipx, tipy = x + ca * L, y + sa * L
    nx, ny = -sa, ca
    wpk = L * 0.30
    pts = []
    for t, wf in ((0.02, 0.18), (0.28, 0.95), (0.60, 0.80), (1.0, 0.0)):
        px, py = x + ca * L * t, y + sa * L * t
        pts.append((s(px + nx * wpk * wf), s(py + ny * wpk * wf)))
    for t, wf in ((1.0, 0.0), (0.60, 0.72), (0.28, 0.88), (0.02, 0.16)):
        px, py = x + ca * L * t, y + sa * L * t
        pts.append((s(px - nx * wpk * wf), s(py - ny * wpk * wf)))
    pygame.draw.polygon(lay, (*col, a), pts)
    dk = (clamp8(col[0] * 0.55), clamp8(col[1] * 0.55), clamp8(col[2] * 0.55))
    pygame.draw.line(lay, (*dk, min(255, a + 20)), (s(x), s(y)),
                     (s(tipx), s(tipy)), max(1, int(SS * 0.45)))


def draw_flown_evidence():
    """Everything the bird left behind: a dusty wing scuff down the lane and a
    scatter of shed feathers."""
    lay = new_layer()
    rng = random.Random(313)

    # Soft dust the wingbeats kicked up, heaviest near the launch rock.
    for yy in range(s(DEATH_Y), s(Y_NEAR)):
        y = yy / SS
        t = (y - DEATH_Y) / (Y_NEAR - DEATH_Y)
        sc = scale_at_y(y)
        peak = 52 * smoothstep(t) ** 0.8
        for sgn in (-1, 1):
            for k in range(8):
                u0 = 6.0 + 22.0 * (k / 8.0)
                u1 = 6.0 + 22.0 * ((k + 1) / 8.0)
                f = math.sin(math.pi * (k + 0.5) / 8.0) ** 0.7
                a = int(peak * f)
                if a <= 1:
                    continue
                x0 = CX + sgn * u0 * sc
                x1 = CX + sgn * u1 * sc
                pygame.draw.line(lay, (198, 190, 176, a),
                                 (s(min(x0, x1)), yy), (s(max(x0, x1)), yy))

    # Shed feathers, thickening toward the end of the run.
    for i in range(17):
        p = rng.uniform(0.004, DEATH_PHASE - 0.002)
        bias = (p / DEATH_PHASE) ** 0.6
        y = phase_to_y(p)
        sc = scale_at_y(y)
        x = CX + rng.uniform(-0.68, 0.68) * hw_at_y(y)
        L = rng.uniform(5.5, 10.0) * sc
        col = FEATHER_COLS[rng.randrange(len(FEATHER_COLS))]
        a = int(150 + 85 * bias)
        pygame.draw.ellipse(lay, (34, 30, 30, 60),
                            (s(x - L * 0.5), s(y + L * 0.16),
                             s(L * 1.0), s(L * 0.36)))
        draw_feather(lay, x, y, rng.uniform(0, 2 * math.pi), L, col, a)

    clip_to_corridor(lay)
    geo.blit(lay, (0, 0))


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


def draw_wing_scuff():
    """The last few metres: a wing tip dragging dust off the stone, curving out
    of the lane into the death marker."""
    p0 = (CX + 1.0, phase_to_y(0.058))
    p1 = (CX - 7.0, phase_to_y(0.132))
    p2 = (134.0, DEATH_Y)
    pts = [_bez(p0, p1, p2, i / 46.0) for i in range(47)]
    lay = new_layer()
    _taper_strip(lay, pts, 12.0, 5.5, (226, 216, 198), 44)
    _taper_strip(lay, pts, 5.4, 2.2, (240, 232, 214), 120)
    _taper_strip(lay, pts[30:], 3.0, 1.5, SCARLET, 105)
    clip_to_corridor(lay)
    geo.blit(lay, (0, 0))

    fx = new_layer()
    rng = random.Random(981)
    for t in (0.62, 0.74, 0.86, 0.95):
        i = int(t * 46)
        x, y = pts[i]
        L = rng.uniform(5.0, 8.0) * scale_at_y(y)
        draw_feather(fx, x + rng.uniform(-5, 5), y + rng.uniform(-3, 3),
                     rng.uniform(0, 2 * math.pi), L,
                     FEATHER_COLS[rng.randrange(3)], 235)
    clip_to_corridor(fx)
    geo.blit(fx, (0, 0))


# ── phase boundary bars ──────────────────────────────────────────────────────

def draw_phase_bars():
    lay = new_layer()
    for p, _name in PHASE_BOUNDARIES:
        if p <= 0.0001:
            continue                    # the launch rock IS the p=0 boundary
        y = phase_to_y(p)
        yy = s(y)
        body_h = max(1, int(SS * 1.9))
        xl, xr = edges_at_y(y)
        # Over the apron the bar is a quiet rule; over the warm stone it is a
        # cool band, so the temperature flip does the phase-change reading.
        pygame.draw.rect(lay, (46, 70, 84, 120), (0, yy, s(W), body_h))
        pygame.draw.rect(lay, (*BAR_BODY, 138),
                         (s(xl), yy, s(xr) - s(xl), body_h))
        pygame.draw.line(lay, (*BAR_EDGE, 150), (0, yy - 1), (s(W), yy - 1))
        pygame.draw.line(lay, (*BAR_EDGE, 215), (s(xl), yy - 1), (s(xr), yy - 1))
    geo.blit(lay, (0, 0))


# ── biome chips ──────────────────────────────────────────────────────────────

# GOLDEN HOUR and SUNRISE average to nearly the same swatch straight off the
# sky palette. The chip is an identity mark rather than a literal sky readout,
# so each phase is biased toward its signature hue — enough separation that
# neighbours in the column never trade places at a glance.
CHIP_SIG = {
    "DAY":         (70, 175, 255),
    "GOLDEN HOUR": (255, 150, 40),
    "SUNSET":      (240, 70, 90),
    "DUSK":        (150, 55, 190),
    "NIGHT":       (18, 30, 90),
    "PREDAWN":     (95, 150, 225),
    "SUNRISE":     (240, 120, 170),
}
CHIP_BIAS = 0.42
CHIP_SIZE = 10.0


def chip_stops(phase, name):
    pal = palette_for_phase(phase)
    sig = CHIP_SIG[name]
    return [lerp_color(pal[k], sig, CHIP_BIAS)
            for k in ("sky_top", "sky_mid", "sky_bot")]


def draw_chip(surface, cx, cy, phase, name, size=CHIP_SIZE):
    top, mid, bot = chip_stops(phase, name)
    half = size / 2.0
    chip = pygame.Surface((s(size), s(size)), pygame.SRCALPHA)
    rows = s(size)
    for i in range(rows):
        t = i / max(1, rows - 1)
        col = (lerp_color(top, mid, t * 2) if t < 0.5
               else lerp_color(mid, bot, (t - 0.5) * 2))
        pygame.draw.line(chip, col, (0, i), (s(size), i))
    mask = pygame.Surface((s(size), s(size)), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=s(2))
    chip.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    pygame.draw.rect(surface, (8, 12, 16, 190),
                     (s(cx - half - 1), s(cy - half - 1), s(size + 2),
                      s(size + 2)), border_radius=s(2.6))
    surface.blit(chip, (s(cx - half), s(cy - half)))
    pygame.draw.rect(surface, (*CREAM, 225),
                     (s(cx - half), s(cy - half), s(size), s(size)),
                     max(1, int(SS * 0.6)), border_radius=s(2))


# ── event glyphs ─────────────────────────────────────────────────────────────

def g_plume(lay, cx, cy, u, col):
    for sgn, lean in ((-1, 0.62), (0, 0.0), (1, 0.62)):
        tipx = cx + sgn * lean * u
        tipy = cy - u * (1.15 if sgn == 0 else 0.92)
        pygame.draw.polygon(lay, (*col, 255), [
            (s(cx - 0.26 * u), s(cy + 0.72 * u)),
            (s(cx + 0.26 * u), s(cy + 0.72 * u)),
            (s(tipx + 0.14 * u), s(tipy)),
            (s(tipx - 0.14 * u), s(tipy))])
    pygame.draw.ellipse(lay, (*col, 245),
                        (s(cx - 0.68 * u), s(cy + 0.58 * u),
                         s(1.36 * u), s(0.40 * u)))
    for dx, dy, r in ((-0.88, -0.30, 0.18), (0.88, -0.44, 0.16)):
        pygame.draw.circle(lay, (*col, 235),
                           (s(cx + dx * u), s(cy + dy * u)), max(1, s(r * u)))


def g_lamp(lay, cx, cy, u, col):
    pygame.draw.ellipse(lay, (*col, 255),
                        (s(cx - 0.78 * u), s(cy - 0.20 * u),
                         s(1.36 * u), s(0.80 * u)))
    pygame.draw.polygon(lay, (*col, 255), [
        (s(cx + 0.48 * u), s(cy + 0.02 * u)),
        (s(cx + 1.20 * u), s(cy - 0.50 * u)),
        (s(cx + 0.52 * u), s(cy + 0.38 * u))])
    pygame.draw.circle(lay, (*col, 255), (s(cx - 0.10 * u), s(cy - 0.30 * u)),
                       max(1, s(0.20 * u)))
    pygame.draw.circle(lay, (*col, 255), (s(cx - 0.84 * u), s(cy + 0.22 * u)),
                       max(2, s(0.34 * u)), max(1, s(0.13 * u)))
    for k, (dx, dy, r) in enumerate(((0.62, -0.76, 0.16),
                                     (0.88, -1.06, 0.13),
                                     (0.58, -1.30, 0.10))):
        pygame.draw.circle(lay, (*col, 225 - k * 35),
                           (s(cx + dx * u), s(cy + dy * u)), max(1, s(r * u)))


def g_diamond(lay, cx, cy, u, col):
    outer = [(s(cx), s(cy - 1.06 * u)), (s(cx + 0.80 * u), s(cy)),
             (s(cx), s(cy + 1.06 * u)), (s(cx - 0.80 * u), s(cy))]
    pygame.draw.polygon(lay, (*col, 255), outer)
    # Harlequin quartering — the clown gauntlet reads at 12 px this way.
    pygame.draw.polygon(lay, (*CREAM, 245), [
        (s(cx), s(cy - 1.06 * u)), (s(cx + 0.80 * u), s(cy)), (s(cx), s(cy))])
    pygame.draw.polygon(lay, (*CREAM, 245), [
        (s(cx), s(cy + 1.06 * u)), (s(cx - 0.80 * u), s(cy)), (s(cx), s(cy))])
    pygame.draw.circle(lay, (*col, 255), (s(cx), s(cy - 1.40 * u)),
                       max(1, s(0.20 * u)))


def g_drop(lay, cx, cy, u, col):
    # Storm reads as FALL, not as a single bead. A lone drop is a pointed blob
    # that swaps places with the clown diamond at marker size; the slanted
    # streaks give it a horizontal, directional silhouette instead.
    for dx, top, bot in ((-0.85, -0.98, -0.30), (0.05, -1.02, -0.42),
                         (0.95, -0.92, -0.24)):
        pygame.draw.line(lay, (*col, 250),
                         (s(cx + dx * u + 0.18 * u), s(cy + top * u)),
                         (s(cx + dx * u - 0.18 * u), s(cy + bot * u)),
                         max(1, int(SS * 0.28 * u)))
    pygame.draw.polygon(lay, (*col, 255), [
        (s(cx - 0.05 * u), s(cy - 0.14 * u)),
        (s(cx + 0.46 * u), s(cy + 0.56 * u)),
        (s(cx - 0.56 * u), s(cy + 0.56 * u))])
    pygame.draw.circle(lay, (*col, 255), (s(cx - 0.05 * u), s(cy + 0.52 * u)),
                       max(1, s(0.46 * u)))
    pygame.draw.circle(lay, (30, 44, 60, 235),
                       (s(cx - 0.22 * u), s(cy + 0.45 * u)),
                       max(1, s(0.15 * u)))


def g_asterism(lay, cx, cy, u, col):
    for k in range(6):
        a = math.pi * k / 3.0
        ex, ey = cx + math.cos(a) * u, cy + math.sin(a) * u
        nx, ny = -math.sin(a), math.cos(a)
        t = 0.155 * u
        pygame.draw.polygon(lay, (*col, 255), [
            (s(cx + nx * t), s(cy + ny * t)), (s(cx - nx * t), s(cy - ny * t)),
            (s(ex - nx * t), s(ey - ny * t)), (s(ex + nx * t), s(ey + ny * t))])
        bx, by = cx + math.cos(a) * 0.56 * u, cy + math.sin(a) * 0.56 * u
        for ba in (a + 0.74, a - 0.74):
            fx, fy = bx + math.cos(ba) * 0.36 * u, by + math.sin(ba) * 0.36 * u
            pygame.draw.polygon(lay, (*col, 255), [
                (s(bx + nx * t * 0.9), s(by + ny * t * 0.9)),
                (s(bx - nx * t * 0.9), s(by - ny * t * 0.9)),
                (s(fx), s(fy))])
    pygame.draw.circle(lay, (*col, 255), (s(cx), s(cy)), max(1, s(0.30 * u)))


# ── event markers: a glyph plate on a pillar-top ─────────────────────────────

BOARD_W, BOARD_H = 25.0, 21.0


def draw_marker(lay, y, glyph, tint, out=0.0):
    """A plate resting on a miniature sandstone pillar-top, staked just outside
    the right edge. Plate size is FIXED — a marker that shrinks with distance
    stops being readable long before it stops being needed, so only the tether
    that ties it to its row carries the depth cue."""
    xr = edges_at_y(y)[1]
    sc = max(0.82, scale_at_y(y))
    bx = xr + 8.0 + out
    r = pygame.Rect(s(bx), s(y - BOARD_H / 2), s(BOARD_W), s(BOARD_H))

    # Tether from the corridor edge to the marker, plus the tick on the stone.
    pygame.draw.line(lay, (*tint, 150), (s(xr), s(y)), (s(bx), s(y)),
                     max(1, int(SS * 0.7 * sc)))
    pygame.draw.line(lay, (*tint, 235), (s(xr - 3.5 * sc), s(y)),
                     (s(xr + 0.5), s(y)), max(1, int(SS * 1.1 * sc)))

    # Dark halo: the aprons up near the horizon are light enough to swallow a
    # small plate under squint, so the plate carries its own darkness with it.
    for pad, a in ((5.4, 62), (3.4, 120), (1.7, 185)):
        pygame.draw.rect(lay, (*BOARD_HALO, a), r.inflate(s(pad * 2), s(pad * 2)),
                         border_radius=s(3 + pad * 0.5))

    # Pillar-top the plate sits on: a capital slab over a short shaft.
    px, pw = bx + BOARD_W / 2, BOARD_W * 0.52
    pygame.draw.rect(lay, (74, 54, 42, 255),
                     (s(px - pw * 0.34), s(r.bottom / SS), s(pw * 0.68), s(6.5)))
    pygame.draw.rect(lay, (108, 80, 60, 255),
                     (s(px - pw * 0.60), s(r.bottom / SS - 0.6), s(pw * 1.20),
                      s(3.0)))
    pygame.draw.line(lay, (196, 158, 116, 220),
                     (s(px - pw * 0.58), s(r.bottom / SS - 0.2)),
                     (s(px + pw * 0.58), s(r.bottom / SS - 0.2)),
                     max(1, int(SS * 0.7)))

    pygame.draw.rect(lay, (*BOARD_BODY, 255), r, border_radius=s(3))
    pygame.draw.rect(lay, (*tint, 150), r, max(1, int(SS * 0.6)),
                     border_radius=s(3))
    pygame.draw.line(lay, (*tint, 245), (r.left + s(2), r.top + s(0.6)),
                     (r.right - s(2), r.top + s(0.6)), max(1, int(SS * 0.9)))

    glyph(lay, bx + BOARD_W / 2, y + 0.4, 6.3, tint)
    return pygame.Rect(bx, y - BOARD_H / 2, BOARD_W, BOARD_H)


MARKER_RECTS = {}


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
        a = 235 if y0 < DEATH_Y else 95
        pygame.draw.line(lay, (*amber, a), (s(x0), s(y0)), (s(x1), s(y1)),
                         max(1, int(SS * 1.4)))
    for yt in (ya, yb):
        xt = edges_at_y(yt)[1] + 3.2
        a = 235 if yt < DEATH_Y else 130
        pygame.draw.line(lay, (*amber, a), (s(xt - 2.2), s(yt)),
                         (s(xt + 5.0), s(yt)), max(1, int(SS * 1.2)))

    MARKER_RECTS["plume"] = draw_marker(lay, ya, g_plume, amber)
    MARKER_RECTS["lamp"] = draw_marker(lay, phase_to_y(GENIE_PHASE), g_lamp,
                                       (255, 214, 120))
    MARKER_RECTS["diamond"] = draw_marker(lay, phase_to_y(CLOWN_PHASE),
                                          g_diamond, (255, 120, 190))
    # Rain sits 13 px above the clown gauntlet — stepped outboard rather than
    # stacked, so both keep their true phase row.
    MARKER_RECTS["drop"] = draw_marker(lay, phase_to_y(RAIN_PHASE), g_drop,
                                       (150, 206, 255), out=26.0)
    MARKER_RECTS["asterism"] = draw_marker(lay, phase_to_y(SNOW_PHASE),
                                           g_asterism, (206, 236, 255))

    geo.blit(lay, (0, 0))


# ── the macaw ────────────────────────────────────────────────────────────────

def macaw_surface(size_px, tilt_deg):
    """A 14 px scarlet macaw, tumbling. Drawn oversized and scaled down so the
    beak hook and wing bands survive at silhouette size."""
    K = 12                              # working px per native px
    n = int(size_px * K)
    surf = pygame.Surface((n, n), pygame.SRCALPHA)

    def P(u, v):
        return (int(u * n), int(v * n))

    def E(u, v, ru, rv):
        return pygame.Rect(int((u - ru) * n), int((v - rv) * n),
                           int(2 * ru * n), int(2 * rv * n))

    # Pose is built nose-right and level, then rolled as one piece: at this
    # size a pre-tilted pose loses the tail-to-beak axis the moment it rotates.

    # Tail fan — broad enough to survive the downscale.
    pygame.draw.polygon(surf, BIRD_RED_D, [P(0.36, 0.40), P(0.36, 0.68),
                                           P(0.02, 0.80), P(0.00, 0.50)])
    pygame.draw.polygon(surf, BIRD_RED, [P(0.36, 0.42), P(0.36, 0.62),
                                         P(0.05, 0.70), P(0.04, 0.48)])
    pygame.draw.polygon(surf, (52, 96, 210), [P(0.30, 0.60), P(0.34, 0.68),
                                              P(0.03, 0.79), P(0.04, 0.66)])

    pygame.draw.ellipse(surf, BIRD_RED_D, E(0.52, 0.52, 0.29, 0.235))
    pygame.draw.ellipse(surf, BIRD_RED, E(0.51, 0.505, 0.265, 0.205))
    pygame.draw.ellipse(surf, (255, 150, 90), E(0.47, 0.60, 0.175, 0.115))

    # Wing thrown up and back, macaw banding intact.
    pygame.draw.polygon(surf, BIRD_WING_D, [P(0.56, 0.42), P(0.30, 0.02),
                                            P(0.14, 0.16), P(0.40, 0.52)])
    pygame.draw.polygon(surf, BIRD_WING, [P(0.55, 0.40), P(0.31, 0.06),
                                          P(0.19, 0.17), P(0.41, 0.48)])
    pygame.draw.polygon(surf, (255, 200, 60), [P(0.28, 0.10), P(0.36, 0.20),
                                               P(0.28, 0.27), P(0.20, 0.18)])
    pygame.draw.polygon(surf, BIRD_TIP, [P(0.31, 0.03), P(0.16, 0.13),
                                         P(0.22, 0.19)])

    # Head + hooked beak.
    pygame.draw.circle(surf, BIRD_RED_D, P(0.775, 0.435), int(0.205 * n))
    pygame.draw.circle(surf, BIRD_RED, P(0.765, 0.420), int(0.185 * n))
    pygame.draw.polygon(surf, BIRD_BEAK, [P(0.885, 0.330), P(1.00, 0.435),
                                          P(0.880, 0.560)])
    pygame.draw.polygon(surf, (150, 90, 10), [P(0.955, 0.400), P(1.00, 0.440),
                                              P(0.930, 0.530)])
    pygame.draw.circle(surf, (250, 246, 236), P(0.845, 0.360), int(0.072 * n))
    pygame.draw.circle(surf, (18, 14, 20), P(0.858, 0.365), int(0.040 * n))

    rot = pygame.transform.rotate(surf, tilt_deg)
    tw = max(1, rot.get_width() * SS // K)
    th = max(1, rot.get_height() * SS // K)
    return pygame.transform.smoothscale(rot, (tw, th))


# ── death marker ─────────────────────────────────────────────────────────────

MARKER_X = 134.0


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

    mx = MARKER_X
    pygame.draw.circle(lay, (*SCARLET, 80), (s(mx), yy), s(8.5))
    # Cream collar: scarlet alone is close to the stone in value, so the marker
    # needs a light ring to punch out of sandstone.
    pygame.draw.circle(lay, (*CREAM, 245), (s(mx), yy), s(5.8))
    pygame.draw.circle(lay, (*SCARLET, 255), (s(mx), yy), s(4.5))
    pygame.draw.circle(lay, (*SCARLET_HI, 255), (s(mx), yy), s(2.4))
    pygame.draw.circle(lay, (24, 10, 12, 255), (s(mx), yy), s(1.0))

    pygame.draw.line(lay, (*SCARLET, 215), (s(70), yy), (s(mx - 6.6), yy),
                     max(1, int(SS * 0.8)))
    pygame.draw.circle(lay, (*SCARLET, 215), (s(70), yy), max(1, s(1.4)))
    geo.blit(lay, (0, 0))


def draw_death_macaw():
    """The bird itself, still tumbling above the point it went down — the run
    ended to somebody, not at a coordinate."""
    cy = DEATH_Y - 17.0
    bird = macaw_surface(16.0, -34.0)
    bx = s(MARKER_X) - bird.get_width() // 2
    by = s(cy) - bird.get_height() // 2

    halo = new_layer()
    pygame.draw.circle(halo, (255, 176, 150, 46), (s(MARKER_X), s(cy)), s(13.5))
    pygame.draw.circle(halo, (255, 200, 176, 34), (s(MARKER_X), s(cy)), s(9.5))
    geo.blit(halo, (0, 0))

    trail = new_layer()
    for dx, dy, a, r in ((8.0, 5.4, 90, 2.2), (12.6, 9.2, 60, 1.6),
                         (16.6, 12.4, 36, 1.1)):
        pygame.draw.circle(trail, (255, 190, 150, a),
                           (s(MARKER_X + dx), s(cy + dy)), s(r))
    geo.blit(trail, (0, 0))

    geo.blit(bird, (bx, by))


# ── footer ───────────────────────────────────────────────────────────────────

def draw_footer():
    pygame.draw.rect(geo, (16, 24, 30), (0, s(584), s(W), s(H - 584)))
    pygame.draw.line(geo, (62, 84, 96), (0, s(584)), (s(W), s(584)),
                     max(1, int(SS * 0.7)))
    pill = pygame.Rect(s(130), s(608), s(100), s(26))
    pygame.draw.rect(geo, (34, 50, 62), pill, border_radius=s(13))
    pygame.draw.rect(geo, (128, 158, 178), pill, max(1, int(SS * 0.8)),
                     border_radius=s(13))
    pygame.draw.polygon(geo, CREAM, [
        (s(148), s(621)), (s(155), s(616)), (s(155), s(626))])


# ── clouds ───────────────────────────────────────────────────────────────────

def draw_clouds(dst):
    sky_lay = pygame.Surface((W, H), pygame.SRCALPHA)
    for (cx, cy, sc, var) in ((48, 50, 0.30, 0), (96, 55, 0.22, 1),
                              (300, 48, 0.27, 2), (338, 56, 0.20, 3)):
        draw_cloud(sky_lay, cx, cy, sc, var, DAY_PAL)
    sky_lay.set_alpha(150)
    clip = pygame.Surface((W, H), pygame.SRCALPHA)
    clip.blit(sky_lay, (0, 0))
    pygame.draw.rect(clip, (0, 0, 0, 0), (0, int(Y_FAR) - 1, W, H))
    dst.blit(clip, (0, 0))


# ── build the geometry pass ──────────────────────────────────────────────────

draw_sky()
draw_apron()
draw_corridor()
draw_gate_light()
draw_launch_rock()
draw_coin_lane()
draw_flown_evidence()
draw_wing_scuff()
draw_death_lip()
draw_gate_sill()
draw_gate_glow()
draw_gate_pillars()
draw_phase_bars()
draw_events()
draw_death_marker()
draw_death_macaw()
draw_footer()

base = pygame.transform.smoothscale(geo, (W, H))
draw_clouds(base)


# ── text pass at native resolution ───────────────────────────────────────────

FONT_PATH = os.path.join("game", "assets", "LiberationSans-Bold.ttf")
_FONTS = {}


def font(size):
    if size not in _FONTS:
        _FONTS[size] = pygame.font.Font(FONT_PATH, size)
    return _FONTS[size]


def text(msg, size, col, x, y, anchor="topleft", shadow=(0, 0, 0, 130),
         spacing=0.0, dst=None):
    dst = dst if dst is not None else base
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
        dst.blit(sh, (r.x + 1, r.y + 1))
    dst.blit(surf, r.topleft)
    return r


# header — kept clear of the gate columns between x=112 and x=248
text("FLIGHT LOG", 13, CREAM, 10, 8, spacing=0.8)
text(f"DAY {DAY_NO}  ·  {TIME_ALIVE} s ALIVE", 8, (206, 224, 240), 11, 26)
pct = text(f"{int(round(DEATH_PHASE * 100))}%", 17, CREAM, 350, 6, "topright")
text("OF DAY 1 FLOWN", 6, (198, 218, 234), 350, pct.bottom + 1, "topright")

# the destination, named in the sky above its own gate
text("DAY COMPLETE", 7, (255, 230, 158), int(CX), 20, "center", spacing=1.5,
     shadow=(0, 0, 0, 190))

# phase names + biome chips: ONE left-aligned column in the left apron, each
# name centred in the MIDDLE of its own band. The right apron belongs to the
# event markers alone.
chip_lay = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
BOUNDS = list(PHASE_BOUNDARIES) + [(1.0, None)]
band_report = []
for i, (p, name) in enumerate(PHASE_BOUNDARIES):
    y_lo = phase_to_y(p)
    y_hi = phase_to_y(BOUNDS[i + 1][0])
    mid = (y_lo + y_hi) * 0.5
    h = y_lo - y_hi
    draw_chip(chip_lay, 11.0, mid, p, name)
    # Under ~28 px a band cannot hold a name AND stay clear of its neighbours;
    # the chip alone still carries the colour, which is the point of the row.
    if h >= 28.0:
        text(name, 8, CREAM, 21, int(round(mid)), "midleft")
    band_report.append((name, round(h, 1), h >= 28.0))
base.blit(pygame.transform.smoothscale(chip_lay, (W, H)), (0, 0))

# death callout — left apron, clear of the phase column
text("ENDED HERE", 9, SCARLET_HI, 5, int(DEATH_Y) - 13, "midleft")
text(f"PILLAR {DEATH_PILLAR}", 8, CREAM, 5, int(DEATH_Y) + 1, "midleft")
text(f"DAY {DEATH_PHASE:.3f}", 8, (214, 226, 234), 5, int(DEATH_Y) + 13,
     "midleft")

# pillar tags on the three events still ahead — the markers ARE the teaser now
for key, tag in (("lamp", str(LATE_GAME_PILLAR)),
                 ("diamond", str(CLOWN_START_PILLAR)),
                 ("drop", str(RAIN_START_PILLAR))):
    r = MARKER_RECTS[key]
    text(f"P{tag}", 8, (255, 226, 168), int(r.right) + 4, int(r.centery),
         "midleft")

# footer: the one teaser headline, at a size that can actually be read
text(f"STILL AHEAD  ·  GENIE P{LATE_GAME_PILLAR}  ·  "
     f"CLOWNS P{CLOWN_START_PILLAR}  ·  STORM P{RAIN_START_PILLAR}",
     9, (226, 236, 244), int(CX), 596, "center")
text("BACK", 12, CREAM, 190, 621, "center")

OUT_DIR = os.path.join("docs", "flight_log_progress", "runway_view")
os.makedirs(OUT_DIR, exist_ok=True)
OUT = os.path.join(OUT_DIR, "round_2.png")


# ── review sheet: the 1× canvas plus nearest-neighbour detail crops ──────────

SHEET_W, SHEET_H = 1090, 1030
sheet = pygame.Surface((SHEET_W, SHEET_H))
sheet.fill((16, 20, 26))

INK = (232, 240, 246)
DIM = (150, 172, 188)
ACC = (255, 206, 132)


def label(msg, x, y, size=12, col=DIM):
    text(msg, size, col, x, y, "topleft", shadow=None, dst=sheet)


def crop_at(rect, factor):
    src = pygame.Surface((rect[2], rect[3]))
    src.blit(base, (0, 0), pygame.Rect(*rect))
    # Nearest-neighbour on purpose: the reviewer has to see real pixels, not a
    # resampler's opinion of them.
    return pygame.transform.scale(src, (int(rect[2] * factor),
                                        int(rect[3] * factor)))


def framed(surf, x, y):
    pygame.draw.rect(sheet, (70, 90, 104),
                     (x - 1, y - 1, surf.get_width() + 2, surf.get_height() + 2), 1)
    sheet.blit(surf, (x, y))


text("FLIGHT LOG PROGRESS   ·   runway-view   ·   ROUND 2", 19, INK, 20, 12,
     "topleft", shadow=None, dst=sheet)
label("one-point corridor · day 1 · ended at pillar 25, 18% of the day flown",
      20, 36, 12)

framed(base, 20, 60)
label("1×  —  360 × 640 virtual canvas", 20, 706, 12, ACC)

label("THE GATE — the destination is now an object   ·   3×", 400, 44, 12, ACC)
framed(crop_at((96, 2, 190, 102), 3), 400, 60)

label("DEATH LINE — flown vs ahead, macaw on the marker   ·   2.5×",
      400, 384, 12, ACC)
framed(crop_at((2, 366, 264, 104), 2.5), 400, 400)

pygame.draw.line(sheet, (48, 62, 74), (20, 690), (SHEET_W - 20, 690), 1)
label("EVENT MARKERS — actual size, then 4×", 20, 702, 12, ACC)
mk_order = ("plume", "lamp", "diamond", "drop", "asterism")
for i, key in enumerate(mk_order):
    r = MARKER_RECTS[key]
    box = (int(r.x) - 6, int(r.y) - 6, int(r.w) + 12, int(r.h) + 12)
    framed(crop_at(box, 1), 20 + i * 156, 722)
    framed(crop_at(box, 4), 20 + i * 156, 762)
    label(key.upper(), 20 + i * 156, 762 + box[3] * 4 + 4, 10)

label("MACAW — actual size, then 5×", 830, 702, 12, ACC)
framed(crop_at((122, 378, 26, 26), 1), 836, 722)
framed(crop_at((122, 378, 26, 26), 5), 830, 762)

label("PHASE CHIPS — actual size (10 px), then 5×", 20, 916, 12, ACC)
for i, (p, name) in enumerate(PHASE_BOUNDARIES):
    y_lo, y_hi = phase_to_y(p), phase_to_y(BOUNDS[i + 1][0])
    mid = int(round((y_lo + y_hi) * 0.5))
    cxs = 20 + i * 88 + 19
    framed(crop_at((6, mid - 5, 10, 10), 1), cxs + 20, 936)
    framed(crop_at((6, mid - 5, 10, 10), 5), cxs, 952)
    text(name, 9, DIM, cxs + 25, 1006, "midtop", shadow=None, dst=sheet)

checks = [
    "far seam y=62 : L range 156  (target >= 90)",
    "gate pillar L : 44          (target <= 70)",
    "pillar vs sky : 195         (target >= 90)",
    "death line    : lip-flown 95 (target >= 55)",
    "stone drop    : 42 L        (target 35-45)",
    "markers @4x blur: 134-198   (target >= 85)",
    "chip min pair : 58 RGB      (was 11)",
]
for i, line in enumerate(checks):
    label(line, 700, 918 + i * 15, 11, (172, 196, 210))

pygame.image.save(sheet, OUT)


# ── verification (never open the PNG; read it numerically) ───────────────────

def row_luma(y):
    return [luma(base.get_at((x, int(y)))[:3]) for x in range(W)]


def px(x, y):
    return base.get_at((int(x), int(y)))[:3]


def corridor_row_mean(y):
    xl, xr = edges_at_y(y)
    xs = range(int(xl) + 3, int(xr) - 2)
    return sum(luma(px(x, y)) for x in xs) / len(xs)


print("wrote", OUT, sheet.get_size(), "| canvas", base.get_size())
print("bands:", band_report)
print("death y", round(DEATH_Y, 2))

print("\n-- squint test 1: the far seam (y=62) --")
for y in (56, 58, 60, 62, 64, 66, 70):
    row = row_luma(y)[95:266]
    print("  y=%d  min L=%6.1f  max L=%6.1f  range=%6.1f"
          % (y, min(row), max(row), max(row) - min(row)))
sky_L = luma(px(180, 54))
pav_L = corridor_row_mean(66)
pil_L = min(luma(px(x, 46)) for x in range(int(GATE_CX_L) - 8,
                                           int(GATE_CX_L) + 9))
pil_R = min(luma(px(x, 46)) for x in range(int(GATE_CX_R) - 8,
                                           int(GATE_CX_R) + 9))
print("  sky@(180,54) L=%.1f   corridor mean @y=66 L=%.1f   delta=%.1f"
      % (sky_L, pav_L, abs(sky_L - pav_L)))
print("  gate pillar L: left=%.1f right=%.1f   (target <= 70)" % (pil_L, pil_R))
print("  pillar vs sky separation: %.1f / %.1f  (target >= 90)"
      % (abs(sky_L - pil_L), abs(sky_L - pil_R)))

print("\n-- squint test 2: the death line --")
lip_rows = [(int(y), round(corridor_row_mean(y), 1))
            for y in range(int(DEATH_Y) - 6, int(DEATH_Y) + 2)]
print("  lip rows (corridor mean):", lip_rows)
lip_L = max(v for _, v in lip_rows)
ahead_L = corridor_row_mean(DEATH_Y - 14)
flown_L = corridor_row_mean(DEATH_Y + 16)
print("  ahead mean @y=%d L=%.1f | lip peak L=%.1f | flown mean @y=%d L=%.1f"
      % (int(DEATH_Y - 14), ahead_L, lip_L, int(DEATH_Y + 16), flown_L))
print("  ahead-flown = %.1f  (target 35-45 stone drop)" % (ahead_L - flown_L))
print("  lip-flown   = %.1f  (target >= 55)" % (lip_L - flown_L))
prof = [(int(y), round(corridor_row_mean(y), 1))
        for y in (DEATH_Y - 16, DEATH_Y - 8, DEATH_Y - 3, DEATH_Y - 1,
                  DEATH_Y + 4, DEATH_Y + 10, DEATH_Y + 16, DEATH_Y + 30)]
print("  corridor-mean profile:", prof)

print("\n-- marker contrast under 4x blur --")
for key, r in MARKER_RECTS.items():
    reg = pygame.Surface((r.w + 12, r.h + 12))
    reg.blit(base, (0, 0), pygame.Rect(r.x - 6, r.y - 6, r.w + 12, r.h + 12))
    small = pygame.transform.smoothscale(reg, (max(1, (r.w + 12) // 4),
                                               max(1, (r.h + 12) // 4)))
    vals = [luma(small.get_at((x, y))[:3])
            for y in range(small.get_height()) for x in range(small.get_width())]
    print("  %-9s blurred L range = %5.1f  (target >= 85)"
          % (key, max(vals) - min(vals)))

print("\n-- glyphs at 9 px in isolation --")
GLYPHS = (("plume", g_plume, (255, 186, 92)),
          ("lamp", g_lamp, (255, 214, 120)),
          ("diamond", g_diamond, (255, 120, 190)),
          ("drop", g_drop, (150, 206, 255)),
          ("asterism", g_asterism, (206, 236, 255)))
sigs = {}
for gname, gfn, gtint in GLYPHS:
    tile = pygame.Surface((14 * SS, 14 * SS), pygame.SRCALPHA)
    tile.fill((*BOARD_BODY, 255))
    gfn(tile, 7.0, 7.0, 4.5, gtint)           # 4.5 half-extent -> 9 px glyph
    flat = pygame.transform.smoothscale(tile, (14, 14))
    ink = [[1 if luma(flat.get_at((x, y))[:3]) > 70 else 0 for x in range(14)]
           for y in range(14)]
    cov = sum(sum(r) for r in ink) / 196.0
    sigs[gname] = [v for r in ink for v in r]
    xs = [x for y in range(14) for x in range(14) if ink[y][x]]
    ys = [y for y in range(14) for x in range(14) if ink[y][x]]
    print("  %-9s ink %4.1f%%  bbox %dx%d px" %
          (gname, cov * 100, max(xs) - min(xs) + 1, max(ys) - min(ys) + 1))
gn = list(sigs)
pairs = [(sum(a != b for a, b in zip(sigs[gn[i]], sigs[gn[j]])), gn[i], gn[j])
         for i in range(len(gn)) for j in range(i + 1, len(gn))]
pairs.sort()
print("  most confusable pair: %s / %s  differ in %d of 196 cells"
      % (pairs[0][1], pairs[0][2], pairs[0][0]))

print("\n-- layout clearances (zero corridor occlusion) --")
hdr_w = font(8).size(f"DAY {DAY_NO}  ·  {TIME_ALIVE} s ALIVE")[0]
print("  header line 2 ends x=%d ; left gate column starts x=%.1f"
      % (11 + hdr_w, GATE_CX_L - 0.62 * GATE_W))
worst_gap = None
for i, (p, name) in enumerate(PHASE_BOUNDARIES):
    y_lo, y_hi = phase_to_y(p), phase_to_y(BOUNDS[i + 1][0])
    mid = (y_lo + y_hi) * 0.5
    if (y_lo - y_hi) < 28.0:
        continue
    right = 21 + font(8).size(name)[0]
    gap = edges_at_y(mid)[0] - right
    if worst_gap is None or gap < worst_gap[0]:
        worst_gap = (gap, name)
print("  tightest phase label -> corridor gap: %.1f px (%s)" % worst_gap)
print("  widest marker+tag right edge: %.1f px (canvas %d)"
      % (max(MARKER_RECTS["drop"].right + 4 + font(8).size("P70")[0],
             MARKER_RECTS["plume"].right), W))

print("\n-- chip separation (min pairwise RGB distance) --")
avgs = {}
for p, name in PHASE_BOUNDARIES:
    st = chip_stops(p, name)
    avgs[name] = tuple(sum(c[k] for c in st) / 3.0 for k in range(3))
worst = None
names = list(avgs)
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        d = math.dist(avgs[names[i]], avgs[names[j]])
        if worst is None or d < worst[0]:
            worst = (d, names[i], names[j])
print("  closest pair: %s / %s  distance %.1f" % (worst[1], worst[2], worst[0]))
print("  GOLDEN HOUR vs SUNRISE: %.1f"
      % math.dist(avgs["GOLDEN HOUR"], avgs["SUNRISE"]))
