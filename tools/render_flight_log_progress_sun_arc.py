#!/usr/bin/env python3
"""
sun-arc  ·  flight-log progress screen  ·  round 1

The run is read as a sky dome: the day cycle IS the arc. A 150px horizon arc
carries the sun to where the run ended, the travelled span burns bright, and
everything still ahead sits on a quiet outer rail of event glyphs. The dome
behind it is painted at full biome saturation so the player sees the actual
hours they flew through rather than a legend describing them.

The prose sun position in the brief ((112, 355)) disagrees with the brief's own
arc_pos() code ((54, 318)); arc_pos() wins, because every phase tick and event
glyph is placed by the same function and a hand-offset sun would break the one
promise this layout makes — that angle equals time.
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

from game.weather import THERMAL_START_PHASE, THERMAL_END_PHASE, SNOW_STORM_CENTER
from game.config import LATE_GAME_PILLAR, CLOWN_START_PILLAR, RAIN_START_PILLAR
from game.biome import PHASE_BOUNDARIES, palette_for_phase
from game.draw import lerp_color, lerp_color_multi

W, H = 360, 640
CX, CY, R = 180, 400, 150
R_OUTER = 164
HORIZON_Y = 400
SS = 3

FONT_PATH = "/home/user/skybit/game/assets/LiberationSans-Bold.ttf"
_fonts: dict = {}


def font(size):
    if size not in _fonts:
        _fonts[size] = pygame.font.Font(FONT_PATH, size)
    return _fonts[size]


# ── palette ──────────────────────────────────────────────────────────────────
IVORY = (255, 246, 232)
GOLD = (255, 206, 112)
SCARLET = (240, 66, 60)

GEYSER_C = (146, 232, 255)
GENIE_C = (196, 150, 255)
CLOWN_C = (255, 118, 196)
RAIN_C = (150, 190, 255)
SNOW_C = (222, 244, 255)

GROUND_STOPS = [
    (0.00, (214, 168, 108)),
    (0.16, (192, 142, 88)),
    (0.42, (146, 100, 64)),
    (0.72, (94, 62, 44)),
    (1.00, (48, 32, 26)),
]

# Mock run
DEATH_PHASE = 0.184
DEATH_PILLAR = 25
DAY_N = 1
TIME_ALIVE = 47
PHASE_LABEL = "DAY"

GEYSER_SPAN = (THERMAL_START_PHASE, THERMAL_END_PHASE)
GENIE_PHASE = 0.300
CLOWN_PHASE = 0.403
RAIN_PHASE = 0.430
SNOW_PHASE = SNOW_STORM_CENTER


# ── geometry ─────────────────────────────────────────────────────────────────

def arc_pos(phase, radius=R):
    a = math.radians(180.0 - phase * 180.0)
    return (CX + radius * math.cos(a), CY - radius * math.sin(a))


def radial_unit(phase):
    """Outward-pointing unit vector at a phase, in screen coords (y down)."""
    a = math.radians(180.0 - phase * 180.0)
    return (math.cos(a), -math.sin(a))


def arc_points(p0, p1, radius, steps=None, scale=1):
    steps = steps or max(8, int(abs(p1 - p0) * 220))
    pts = []
    for i in range(steps + 1):
        p = p0 + (p1 - p0) * i / steps
        x, y = arc_pos(p, radius)
        pts.append((x * scale, y * scale))
    return pts


def text(surf, s, size, center=None, midleft=None, midright=None,
         color=IVORY, shadow=(0, 0, 0, 150), track=0):
    f = font(size)
    if track:
        # Manual letter-spacing keeps the header feeling like signage rather
        # than body copy; pygame has no tracking control.
        glyphs = [f.render(ch, True, color) for ch in s]
        tw = sum(g.get_width() for g in glyphs) + track * (len(s) - 1)
        th = f.get_height()
        img = pygame.Surface((tw, th), pygame.SRCALPHA)
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
        sh = (f.render(s, True, shadow[:3]) if not track else None)
        if sh is None:
            sh = img.copy()
            sh.fill((*shadow[:3], 255), special_flags=pygame.BLEND_RGBA_MULT)
        sh.set_alpha(shadow[3])
        surf.blit(sh, (rect.x + 1, rect.y + 1))
    surf.blit(img, rect)
    return rect


def soft_glow(radius, color, peak=110, falloff=2.0):
    """Additive glow with the falloff baked into RGB.

    BLEND_ADD ignores the source alpha channel, so an alpha-ramped glow blits
    as a flat hard-edged disc and blows the sky to white. Premultiplying keeps
    the ramp.
    """
    size = radius * 2 + 2
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    c = radius + 1
    for r in range(radius, 0, -1):
        f = (1 - (r / radius) ** falloff) * (peak / 255.0)
        s_col = (int(color[0] * f), int(color[1] * f), int(color[2] * f), 255)
        pygame.draw.circle(s, s_col, (c, c), r)
    return s


def chip(surf, rect, radius=6, fill=(14, 10, 18), alpha=152, border=(255, 246, 232), border_a=46):
    s = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(s, (*fill, alpha), s.get_rect(), border_radius=radius)
    if border_a:
        pygame.draw.rect(s, (*border, border_a), s.get_rect(), width=1, border_radius=radius)
    surf.blit(s, rect.topleft)


# ── sky dome ─────────────────────────────────────────────────────────────────

def draw_dome(surf):
    """Per-column sweep of the full seven-phase cycle at full saturation.

    Phase maps linearly across the canvas width rather than through the arc's
    cosine projection: the projection would crush SUNRISE into a 6px slice at
    the right edge, and the two mappings agree to within ~15px everywhere the
    eye can check them against a tick.
    """
    for x in range(W):
        pal = palette_for_phase(x / W)
        stops = [
            (0.00, pal["sky_top"]),
            (0.42, pal["sky_mid"]),
            (0.80, pal["sky_bot"]),
            (1.00, pal["horizon"]),
        ]
        for y in range(HORIZON_Y):
            surf.set_at((x, y), lerp_color_multi(stops, y / (HORIZON_Y - 1)))


def draw_stars(surf):
    rng = random.Random(20260731)
    for _ in range(190):
        x = rng.randrange(W)
        y = rng.randrange(0, HORIZON_Y - 30)
        base = palette_for_phase(x / W)["star_alpha"]
        if base < 8:
            continue
        # Stars thin out toward the horizon so the dome keeps a top-heavy sky.
        depth = 1.0 - (y / (HORIZON_Y - 30)) * 0.55
        a = int(base * depth * rng.uniform(0.45, 1.0))
        if a < 10:
            continue
        r = 1 if rng.random() < 0.78 else 2
        pygame.draw.circle(surf, (255, 252, 245, min(255, a)), (x, y), r)
        if r == 2 and rng.random() < 0.4:
            pygame.draw.line(surf, (255, 252, 245, a // 2), (x - 3, y), (x + 3, y))
            pygame.draw.line(surf, (255, 252, 245, a // 2), (x, y - 3), (x, y + 3))


def draw_moon(surf, cx, cy, r=13):
    glow = soft_glow(r * 3, (190, 214, 255), peak=74, falloff=2.4)
    surf.blit(glow, (cx - r * 3 - 1, cy - r * 3 - 1), special_flags=pygame.BLEND_ADD)
    m = pygame.Surface((r * 2 + 6, r * 2 + 6), pygame.SRCALPHA)
    c = (r + 3, r + 3)
    pygame.draw.circle(m, (236, 242, 255, 255), c, r)
    pygame.draw.circle(m, (206, 218, 245, 255), c, r, 0)
    for dx, dy, cr in ((-4, -3, 3), (2, 4, 2), (-1, 5, 1)):
        pygame.draw.circle(m, (222, 230, 250, 255), (c[0] + dx, c[1] + dy), cr)
    pygame.draw.circle(m, (246, 250, 255, 255), (c[0] - 3, c[1] - 4), r - 4)
    # Punching the shadow disc with a zero-alpha fill carves the crescent
    # without needing to know the dome colour underneath.
    pygame.draw.circle(m, (0, 0, 0, 0), (c[0] + 7, c[1] - 4), r)
    surf.blit(m, (cx - r - 3, cy - r - 3))


def draw_horizon_light(surf):
    bloom = pygame.Surface((W, 26), pygame.SRCALPHA)
    for x in range(W):
        hc = palette_for_phase(x / W)["horizon"]
        for i in range(24):
            f = 0.30 * (1 - i / 24) ** 2.1
            bloom.set_at((x, 23 - i), (int(hc[0] * f), int(hc[1] * f), int(hc[2] * f), 255))
    surf.blit(bloom, (0, HORIZON_Y - 24), special_flags=pygame.BLEND_ADD)
    for x in range(W):
        hc = palette_for_phase(x / W)["horizon"]
        surf.set_at((x, HORIZON_Y - 1), lerp_color(hc, (255, 255, 255), 0.35))
        surf.set_at((x, HORIZON_Y), lerp_color(hc, (60, 38, 26), 0.45))


def draw_ground(surf):
    h = H - HORIZON_Y
    for i in range(h):
        c = lerp_color_multi(GROUND_STOPS, i / (h - 1))
        pygame.draw.line(surf, c, (0, HORIZON_Y + i), (W - 1, HORIZON_Y + i))
    # Sandstone strata: a few dune lips just under the horizon give the band
    # material identity without adding noise behind the copy.
    rng = random.Random(4242)
    for k in range(5):
        y = HORIZON_Y + 4 + k * 4
        amp = 2.2 - k * 0.3
        col = lerp_color(lerp_color_multi(GROUND_STOPS, (y - HORIZON_Y) / h),
                         (255, 224, 176), 0.30 - k * 0.05)
        pts = []
        ph = rng.uniform(0, 6)
        for x in range(0, W + 1, 6):
            pts.append((x, y + math.sin(x * 0.035 + ph + k) * amp))
        pygame.draw.lines(surf, col, False, pts, 1)


# ── event glyphs (shared by the ring, the teaser rows and the legend) ─────────

def g_geyser(s, cx, cy, r, col=GEYSER_C):
    body = [(cx - r * 0.30, cy + r), (cx - r * 0.16, cy - r * 0.15),
            (cx - r * 0.42, cy - r * 0.75), (cx, cy - r * 1.05),
            (cx + r * 0.42, cy - r * 0.75), (cx + r * 0.16, cy - r * 0.15),
            (cx + r * 0.30, cy + r)]
    pygame.draw.polygon(s, (*col, 235), body)
    pygame.draw.polygon(s, (255, 255, 255, 200), body, max(1, int(r * 0.18)))
    pygame.draw.circle(s, (255, 255, 255, 220), (int(cx - r * 0.72), int(cy - r * 0.95)), max(1, int(r * 0.20)))
    pygame.draw.circle(s, (255, 255, 255, 190), (int(cx + r * 0.78), int(cy - r * 0.60)), max(1, int(r * 0.16)))


def g_genie(s, cx, cy, r, col=GENIE_C):
    body = [(cx - r * 0.95, cy + r * 0.30), (cx - r * 0.55, cy - r * 0.35),
            (cx + r * 0.35, cy - r * 0.35), (cx + r * 0.72, cy + r * 0.05),
            (cx + r * 0.30, cy + r * 0.55), (cx - r * 0.55, cy + r * 0.55)]
    pygame.draw.polygon(s, (*col, 240), body)
    pygame.draw.polygon(s, (255, 236, 190, 210), body, max(1, int(r * 0.16)))
    pygame.draw.line(s, (255, 236, 190, 230), (cx - r * 0.95, cy + r * 0.18),
                     (cx - r * 1.55, cy - r * 0.10), max(1, int(r * 0.26)))
    handle =[(cx + r * 0.55, cy - r * 0.25), (cx + r * 1.05, cy - r * 0.05),
              (cx + r * 0.95, cy + r * 0.42), (cx + r * 0.45, cy + r * 0.50)]
    pygame.draw.lines(s, (255, 236, 190, 220), False, handle, max(1, int(r * 0.18)))
    flame = [(cx - r * 1.55, cy - r * 0.18), (cx - r * 1.30, cy - r * 0.95),
             (cx - r * 1.10, cy - r * 0.22)]
    pygame.draw.polygon(s, (255, 216, 120, 245), flame)


def g_clown(s, cx, cy, r, col=CLOWN_C):
    d = [(cx, cy - r), (cx + r * 0.82, cy), (cx, cy + r), (cx - r * 0.82, cy)]
    pygame.draw.polygon(s, (*col, 240), d)
    left = [(cx, cy - r), (cx, cy + r), (cx - r * 0.82, cy)]
    pygame.draw.polygon(s, (255, 226, 118, 240), left)
    pygame.draw.polygon(s, (255, 255, 255, 210), d, max(1, int(r * 0.16)))
    pygame.draw.circle(s, (255, 255, 255, 230), (int(cx), int(cy)), max(1, int(r * 0.20)))


def g_rain(s, cx, cy, r, col=RAIN_C):
    drop = [(cx, cy - r * 1.05), (cx + r * 0.68, cy + r * 0.28),
            (cx + r * 0.34, cy + r * 0.86), (cx - r * 0.34, cy + r * 0.86),
            (cx - r * 0.68, cy + r * 0.28)]
    pygame.draw.polygon(s, (*col, 240), drop)
    pygame.draw.polygon(s, (235, 246, 255, 215), drop, max(1, int(r * 0.16)))
    pygame.draw.line(s, (255, 255, 255, 190), (cx - r * 0.22, cy + r * 0.10),
                     (cx - r * 0.30, cy + r * 0.52), max(1, int(r * 0.18)))


def g_snow(s, cx, cy, r, col=SNOW_C):
    w = max(1, int(r * 0.22))
    for k in range(6):
        a = math.radians(k * 60)
        ex, ey = cx + math.cos(a) * r, cy + math.sin(a) * r
        pygame.draw.line(s, (*col, 240), (cx, cy), (ex, ey), w)
        bx, by = cx + math.cos(a) * r * 0.62, cy + math.sin(a) * r * 0.62
        for sgn in (-1, 1):
            b = a + sgn * math.radians(48)
            pygame.draw.line(s, (*col, 220), (bx, by),
                             (bx + math.cos(b) * r * 0.36, by + math.sin(b) * r * 0.36), w)
    pygame.draw.circle(s, (255, 255, 255, 235), (int(cx), int(cy)), max(1, int(r * 0.24)))


GLYPHS = [
    (g_geyser, "GEYSER", GEYSER_C),
    (g_genie, "GENIE", GENIE_C),
    (g_clown, "CLOWN", CLOWN_C),
    (g_rain, "RAIN", RAIN_C),
    (g_snow, "SNOW", SNOW_C),
]


def glyph_pad(s, cx, cy, r):
    """Dark contact disc: lets a glyph sit ON the rail and read against any
    dome colour behind it."""
    pygame.draw.circle(s, (12, 9, 16, 148), (int(cx), int(cy)), int(r * 1.62))
    pygame.draw.circle(s, (255, 246, 232, 60), (int(cx), int(cy)), int(r * 1.62), 1)


# ── vector overlay (drawn at SS, downscaled once) ────────────────────────────

def draw_overlay(ss):
    k = SS

    def P(p, radius=R):
        x, y = arc_pos(p, radius)
        return (x * k, y * k)

    # Outer rail: a dotted concentric ring so the event glyphs read as beads on
    # a track rather than as free-floating icons.
    for i in range(0, 181, 2):
        p = i / 180
        x, y = P(p, R_OUTER)
        pygame.draw.circle(ss, (255, 246, 232, 58), (int(x), int(y)), int(0.9 * k))

    # Arc guide line: full-strength thin ivory over a dark keyline on BOTH
    # sides — an offset drop shadow leaves the line unsupported where the dome
    # runs bright (day at the left horizon, sunrise at the right).
    guide = arc_points(0.0, 1.0, R, 180, k)
    pygame.draw.lines(ss, (10, 8, 14, 130), False, guide, int(3.0 * k))
    pygame.draw.lines(ss, (255, 246, 232, 242), False, guide, int(2.0 * k))

    # Terminals
    for p in (0.0, 1.0):
        x, y = P(p)
        d = 4.2 * k
        pygame.draw.polygon(ss, (255, 246, 232, 235),
                            [(x, y - d), (x + d * 0.72, y), (x, y + d), (x - d * 0.72, y)])

    # Phase ticks at true angular positions
    for frac, name in PHASE_BOUNDARIES:
        if frac <= 0.0:
            continue
        ux, uy = radial_unit(frac)
        x, y = arc_pos(frac)
        a = ((x - ux * 6.5) * k, (y - uy * 6.5) * k)
        b = ((x + ux * 7.5) * k, (y + uy * 7.5) * k)
        pygame.draw.line(ss, (10, 8, 14, 110), (a[0], a[1] + 1.2 * k), (b[0], b[1] + 1.2 * k), int(2.4 * k))
        pygame.draw.line(ss, (255, 246, 232, 225), a, b, int(1.8 * k))

    # Travelled span — white-gold, thickening toward the sun. The additive
    # bloom under it is laid down natively (see burn_trail_bloom); here the
    # solid body is straight alpha so it keeps its gold at the tail.
    steps = 96
    for i in range(steps):
        p0 = DEATH_PHASE * i / steps
        p1 = DEATH_PHASE * (i + 1) / steps
        t = i / steps
        wdt = (2.4 + 3.8 * t ** 1.6) * k
        col = lerp_color((255, 184, 84), (255, 250, 226), t ** 0.8)
        pygame.draw.line(ss, (*col, int(150 + 105 * t)), P(p0), P(p1), int(wdt))
    for i in range(steps):
        p0 = DEATH_PHASE * i / steps
        p1 = DEATH_PHASE * (i + 1) / steps
        t = i / steps
        pygame.draw.line(ss, (255, 253, 240, int(110 + 145 * t)), P(p0), P(p1), max(1, int(1.4 * k)))

    # Geyser span bracket on the outer rail
    br = arc_points(GEYSER_SPAN[0], GEYSER_SPAN[1], R_OUTER, 60, k)
    pygame.draw.lines(ss, (10, 8, 14, 110), False, [(x, y + 1.2 * k) for x, y in br], int(2.6 * k))
    pygame.draw.lines(ss, (*GEYSER_C, 200), False, br, int(2.0 * k))
    for p in GEYSER_SPAN:
        ux, uy = radial_unit(p)
        x, y = arc_pos(p, R_OUTER)
        pygame.draw.line(ss, (*GEYSER_C, 225),
                         ((x - ux * 4.5) * k, (y - uy * 4.5) * k),
                         ((x + ux * 4.5) * k, (y + uy * 4.5) * k), int(2.0 * k))

    # Event glyphs at true angular positions. Rain is pushed to a wider radius
    # because it sits only 0.027 phase from the clown gauntlet — at R_OUTER the
    # two icons would overlap.
    ring_items = [
        (GEYSER_SPAN[0], R_OUTER, g_geyser, GEYSER_C),
        (GENIE_PHASE, R_OUTER, g_genie, GENIE_C),
        (CLOWN_PHASE, R_OUTER, g_clown, CLOWN_C),
        (RAIN_PHASE, R_OUTER + 18, g_rain, RAIN_C),
        (SNOW_PHASE, R_OUTER, g_snow, SNOW_C),
    ]
    for p, rad, fn, col in ring_items:
        x, y = arc_pos(p, rad)
        if rad != R_OUTER:
            ux, uy = radial_unit(p)
            ax, ay = arc_pos(p, R_OUTER)
            pygame.draw.line(ss, (*col, 150), (ax * k, ay * k),
                             ((x - ux * 6) * k, (y - uy * 6) * k), int(1.2 * k))
        glyph_pad(ss, x * k, y * k, 5.4 * k)
        fn(ss, x * k, y * k, 5.4 * k, col)

    # Death marker: scarlet notch on the arc, spurring inward into empty sky so
    # it cannot collide with the geyser plume 0.028 phase behind it.
    ux, uy = radial_unit(DEATH_PHASE)
    dx, dy = arc_pos(DEATH_PHASE)
    # The spur starts at the collar rather than at the arc point: run through
    # the sun's face and the scarlet bleeds the disc salmon.
    root = (dx - ux * 13.5, dy - uy * 13.5)
    tip = (dx - ux * 36, dy - uy * 36)
    pygame.draw.line(ss, (10, 8, 14, 150), (root[0] * k, root[1] * k), (tip[0] * k, tip[1] * k), int(4.6 * k))
    pygame.draw.line(ss, (*SCARLET, 255), (root[0] * k, root[1] * k), (tip[0] * k, tip[1] * k), int(3.0 * k))
    pygame.draw.circle(ss, (*SCARLET, 255), (int(tip[0] * k), int(tip[1] * k)), int(2.4 * k))
    pygame.draw.circle(ss, (10, 8, 14, 130), (int(dx * k), int(dy * k)), int(13.6 * k), int(4.0 * k))
    pygame.draw.circle(ss, (*SCARLET, 255), (int(dx * k), int(dy * k)), int(13.6 * k), int(2.8 * k))

    return tip


def burn_trail_bloom(surf):
    """Heat haze along the travelled span, brightening toward the sun."""
    # Kept deliberately low: the travelled span crosses the BRIGHT morning
    # sector, where additive light clips to flat white long before it reads as
    # heat.
    for i in range(34):
        t = i / 33
        p = DEATH_PHASE * 0.92 * t
        x, y = arc_pos(p)
        rad = int(4 + 6 * t ** 1.4)
        g = soft_glow(rad, lerp_color((255, 168, 66), (255, 232, 182), t),
                      peak=int(20 + 34 * t ** 1.5), falloff=1.9)
        surf.blit(g, (int(x) - rad - 1, int(y) - rad - 1), special_flags=pygame.BLEND_ADD)


def draw_sun(surf, ss):
    """Glow lands natively (additive), spokes and core at SS for clean edges."""
    x, y = arc_pos(DEATH_PHASE)
    for rad, col, a in ((36, (255, 172, 66), 56), (19, (255, 224, 148), 74)):
        g = soft_glow(rad, col, peak=a, falloff=2.1)
        surf.blit(g, (int(x) - rad - 1, int(y) - rad - 1), special_flags=pygame.BLEND_ADD)
    k = SS
    for i in range(16):
        a = math.radians(i * 22.5 + 6)
        ln = 21 if i % 2 == 0 else 15
        pygame.draw.line(ss, (255, 224, 150, 190),
                         ((x + math.cos(a) * 10.5) * k, (y + math.sin(a) * 10.5) * k),
                         ((x + math.cos(a) * ln) * k, (y + math.sin(a) * ln) * k), int(1.5 * k))
    pygame.draw.circle(ss, (255, 186, 84, 255), (int(x * k), int(y * k)), int(10.2 * k))
    pygame.draw.circle(ss, (255, 224, 146, 255), (int(x * k), int(y * k)), int(7.4 * k))
    pygame.draw.circle(ss, (255, 250, 224, 255), (int((x - 1.6) * k), int((y - 1.8) * k)), int(4.2 * k))


# ── screen ───────────────────────────────────────────────────────────────────

def render_screen():
    surf = pygame.Surface((W, H))
    draw_dome(surf)
    draw_stars(surf)
    draw_moon(surf, 252, 122)
    draw_horizon_light(surf)
    draw_ground(surf)

    # Top scrim: the dome runs at full saturation right to the top edge, so the
    # header needs its own contrast floor rather than a desaturated sky.
    scrim = pygame.Surface((W, 84), pygame.SRCALPHA)
    for y in range(84):
        pygame.draw.line(scrim, (8, 6, 12, int(128 * (1 - y / 84) ** 1.6)), (0, y), (W - 1, y))
    surf.blit(scrim, (0, 0))

    ss = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
    burn_trail_bloom(surf)
    draw_sun(surf, ss)
    spur_tip = draw_overlay(ss)

    # ── ground-band vector work shares the SS pass ──
    k = SS
    rows = [
        (g_genie, GENIE_C, f"GENIE LAMP AT PILLAR {LATE_GAME_PILLAR}"),
        (g_clown, CLOWN_C, f"CLOWN GAUNTLET AT PILLAR {CLOWN_START_PILLAR}"),
        (g_rain, RAIN_C, f"STORM AT {RAIN_START_PILLAR}"),
    ]
    tf = font(9)
    maxw = max(tf.size(t)[0] for _, _, t in rows)
    block_w = 16 + 10 + maxw
    gx = (W - block_w) / 2 + 8
    tx = gx + 8 + 10
    for i, (fn, col, _t) in enumerate(rows):
        fn(ss, gx * k, (452 + i * 18) * k, 6.2 * k, col)
    for i, (fn, _name, col) in enumerate(GLYPHS):
        cx = 36 + i * 72
        pygame.draw.circle(ss, (255, 246, 232, 26), (int(cx * k), int(517 * k)), int(11.8 * k))
        pygame.draw.circle(ss, (255, 246, 232, 46), (int(cx * k), int(517 * k)), int(11.8 * k), int(1.0 * k))
        fn(ss, cx * k, 517 * k, 6.8 * k, col)

    surf.blit(pygame.transform.smoothscale(ss, (W, H)), (0, 0))

    # ── text layer ──
    text(surf, "FLIGHT LOG", 25, center=(W // 2, 31), color=IVORY, track=3)
    text(surf, f"DAY {DAY_N}  ·  PILLAR {DEATH_PILLAR}  ·  0:{TIME_ALIVE:02d}", 12,
         center=(W // 2, 55), color=GOLD)
    pygame.draw.line(surf, (255, 206, 112, 90), (128, 68), (232, 68), 1)

    # Phase name labels — three only, all horizontal, chipped so they stay
    # legible against a fully saturated dome. NIGHT sits outside the arc in
    # open sky; the two horizon labels sit just inside it, because a 40px-wide
    # horizontal word cannot clear a 150px arc that meets the horizon only
    # 30px from the canvas edge — outside there, the chip would eat the arc's
    # own terminal.
    def phase_chip(label, cy, col=IVORY, center=None, left=None, right=None):
        f = font(9)
        r = pygame.Rect(0, 0, f.size(label)[0] + 14, 18)
        if center:
            r.center = (center, cy)
        elif left:
            r.midleft = (left, cy)
        else:
            r.midright = (right, cy)
        chip(surf, r, radius=9, alpha=162)
        text(surf, label, 9, center=r.center, color=col, shadow=None)

    phase_chip("DAY", 384, GOLD, left=43)
    phase_chip("NIGHT", 236, (198, 216, 255), center=262)
    phase_chip("SUNRISE", 384, (255, 196, 168), right=320)

    # Death callout, hung off the inward spur into the ahead sector.
    f = font(9)
    lead, rest = "ENDED HERE", f"  ·  PILLAR {DEATH_PILLAR}  ·  {PHASE_LABEL} {DEATH_PHASE:.3f}"
    w1, w2 = f.size(lead)[0], f.size(rest)[0]
    cw = w1 + w2 + 18
    cr = pygame.Rect(0, 0, cw, 21)
    cr.midleft = (int(spur_tip[0]) + 4, 332)
    if cr.right > W - 6:
        cr.right = W - 6
    chip(surf, cr, radius=6, alpha=170, border_a=64)
    text(surf, lead, 9, midleft=(cr.x + 9, cr.centery), color=SCARLET, shadow=None)
    text(surf, rest, 9, midleft=(cr.x + 9 + w1, cr.centery), color=IVORY, shadow=None)

    # ── ground band copy ──
    hr = font(10).size("STILL AHEAD")[0]
    text(surf, "STILL AHEAD", 10, center=(W // 2, 430), color=(255, 232, 186), track=2)
    for sgn in (-1, 1):
        x0 = W // 2 + sgn * (hr // 2 + 16)
        pygame.draw.line(surf, (255, 224, 170), (x0, 430), (x0 + sgn * 46, 430), 1)
    for i, (_fn, col, t) in enumerate(rows):
        text(surf, t, 9, midleft=(tx, 452 + i * 18), color=(255, 240, 216), shadow=(40, 22, 12, 160))

    pygame.draw.line(surf, (255, 226, 180, 70), (40, 499), (320, 499), 1)
    for i, (_fn, name, _c) in enumerate(GLYPHS):
        text(surf, name, 7, center=(36 + i * 72, 537), color=(255, 236, 206),
             shadow=(38, 22, 12, 150))

    # BACK pill
    pr = pygame.Rect(0, 0, 116, 34)
    pr.center = (W // 2, 598)
    sh = pygame.Surface((pr.w + 6, pr.h + 6), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 90), sh.get_rect(), border_radius=20)
    surf.blit(sh, (pr.x - 3, pr.y - 1))
    grad = pygame.Surface(pr.size, pygame.SRCALPHA)
    for y in range(pr.h):
        grad.fill(lerp_color((255, 226, 168), (226, 168, 96), y / (pr.h - 1)) + (255,),
                  pygame.Rect(0, y, pr.w, 1))
    mask = pygame.Surface(pr.size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=17)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(grad, pr.topleft)
    pygame.draw.rect(surf, (120, 76, 44), pr, width=1, border_radius=17)
    text(surf, "BACK", 13, center=(pr.centerx, pr.centery), color=(78, 46, 24),
         shadow=(255, 236, 196, 120), track=2)

    return surf


# ── review sheet ─────────────────────────────────────────────────────────────

def render_sheet(screen):
    pad, gap = 40, 40
    x1 = pad
    x2 = pad + W + gap
    top = 96
    sw = x2 + W * 2 + pad
    sh = top + H * 2 + 56
    sheet = pygame.Surface((sw, sh))
    for y in range(sh):
        sheet.fill(lerp_color((30, 30, 36), (18, 18, 22), y / (sh - 1)),
                   pygame.Rect(0, y, sw, 1))

    text(sheet, "FLIGHT LOG · PROGRESS SCREEN", 24, midleft=(pad, 38), color=IVORY, track=2)
    text(sheet, "CONCEPT: SUN ARC   ·   ROUND 1", 13, midleft=(pad, 66), color=GOLD, track=1)

    def framed(x, y, img, label):
        pygame.draw.rect(sheet, (72, 72, 82),
                         (x - 1, y - 1, img.get_width() + 2, img.get_height() + 2), 1)
        sheet.blit(img, (x, y))
        text(sheet, label, 12, midleft=(x, y + img.get_height() + 18),
             color=(190, 190, 200))

    framed(x1, top, screen, "1:1  ·  360×640 as shipped")
    framed(x2, top, pygame.transform.scale(screen, (W * 2, H * 2)),
           "2×  ·  true-pixel detail view")
    return sheet


def main():
    screen = render_screen()
    sheet = render_sheet(screen)
    out = "/home/user/skybit/docs/flight_log_progress/sun_arc/round_1.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())


if __name__ == "__main__":
    main()
