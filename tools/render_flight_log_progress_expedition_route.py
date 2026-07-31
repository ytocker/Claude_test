#!/usr/bin/env python3
"""
expedition-route  ·  flight_log_progress  ·  round 2

The day cycle drawn as a surveyed expedition route on a sandstone field plate.
Octolinear, because Beck's rule -- horizontals, verticals and 45s only -- is
what buys the horizontal station names: three stacked runs give ~1050 px of
usable path, so all seven time-of-day phases set flat at full size instead of
stacking or rotating.

Round 2 rebalances the schematic around the run the player actually flew.
Run one now carries only the first quarter of the day, so the opening -- the
geyser field, the death -- gets four times the pixels per phase of the
untouched night on run three. Chevrons ride the whole line: a boustrophedon
map has no inherent reading order, and without arrowheads the fold-back run
reads right-to-left as a second, parallel track.

The value hierarchy is inverted from round one. Surveyed track is heavy and
saturated (burnt amber, full weight); projected track is a thin, faint ink
line -- the standard survey convention, and the one that makes the flown
sliver the darkest thing on the plate instead of the lightest.
"""
import os
import sys
import math
import random
import colorsys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.biome import PHASE_BOUNDARIES, palette_for_phase
from game.weather import (THERMAL_START_PHASE, THERMAL_END_PHASE, SNOW_STORM_CENTER,
                          _phase_for_pillar)
from game.config import LATE_GAME_PILLAR, CLOWN_START_PILLAR, RAIN_START_PILLAR

# Pillar-gated events ride the same phase axis as the weather ones, so the map
# has a single ruler: every mark sits at the phase the player will actually
# reach it, not at a decorative slot.
LAMP_PHASE = _phase_for_pillar(LATE_GAME_PILLAR)
CLOWN_PHASE = _phase_for_pillar(CLOWN_START_PILLAR)
RAIN_PHASE = _phase_for_pillar(RAIN_START_PILLAR)


W, H = 360, 640
SS = 3                                  # supersample factor for every curve

FONT_PATH = os.path.join(ROOT, "game", "assets", "LiberationSans-Bold.ttf")
_FONTS = {}


def font(size):
    if size not in _FONTS:
        _FONTS[size] = pygame.font.Font(FONT_PATH, size)
    return _FONTS[size]


# ── plate palette ────────────────────────────────────────────────────────────
PARCH_TOP = (236, 221, 191)
PARCH_BOT = (221, 202, 168)
PARCH_PANEL = (228, 211, 178)
PARCH_CORE = (233, 218, 187)            # knockout fill inside ahead-beads
INK = (70, 44, 29)
INK_SOFT = (128, 99, 71)
INK_FAINT = (168, 145, 116)
CREAM = (252, 242, 218)
# Burnt amber rather than the round-one additive glaze: additive blending on a
# 220-luma plate clipped straight to near-white, so the flown run came out as
# the LIGHTEST mark on a sheet where every other mark is dark. Flat and dark
# gives the surveyed track the top of the value hierarchy where it belongs.
RAIL = (168, 76, 20)
AMBER = (206, 132, 48)
WASH = (204, 138, 58)
SCARLET = (172, 40, 32)
SLATE = (74, 96, 130)


def lerp_c(a, b, t):
    return (round(a[0] + (b[0] - a[0]) * t),
            round(a[1] + (b[1] - a[1]) * t),
            round(a[2] + (b[2] - a[2]) * t))


def lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


PARCH_L = lum(PARCH_TOP)


# ── mock run ─────────────────────────────────────────────────────────────────
DEATH_PHASE = 0.184
DEATH_PILLAR = 25
DAY_NUMBER = 1
TIME_ALIVE = 47
PCT_INTO_DAY = round(DEATH_PHASE * 100)
PCT_UNCHARTED = round((1.0 - DEATH_PHASE) * 100)


# ── route geometry ───────────────────────────────────────────────────────────
# Runs are symmetric about x=180 including the chamfers (30..330), so the map
# shares one centre axis with the title, the cartouche and the BACK pill.
LEFT, RIGHT = 52, 308
ROW_Y = (144, 252, 360)
CH = 22

RUN1 = [(LEFT, ROW_Y[0]), (RIGHT, ROW_Y[0])]
CNR1 = [(RIGHT, ROW_Y[0]), (RIGHT + CH, ROW_Y[0] + CH),
        (RIGHT + CH, ROW_Y[1] - CH), (RIGHT, ROW_Y[1])]
RUN2 = [(RIGHT, ROW_Y[1]), (LEFT, ROW_Y[1])]
CNR2 = [(LEFT, ROW_Y[1]), (LEFT - CH, ROW_Y[1] + CH),
        (LEFT - CH, ROW_Y[2] - CH), (LEFT, ROW_Y[2])]
RUN3 = [(LEFT, ROW_Y[2]), (RIGHT, ROW_Y[2])]

# Phase span per leg. The whole point of a schematic is that scale is a design
# choice: run one buys the first quarter of the day -- everything the player
# actually flew, plus the geyser mouth they died in -- at 4x the density of
# run three, which carries the entire untouched night.
LEGS = [
    (RUN1, 0.00, 0.25),
    (CNR1, 0.25, 0.26),
    (RUN2, 0.26, 0.58),
    (CNR2, 0.58, 0.59),
    (RUN3, 0.59, 1.00),
]

FULL_PATH = (RUN1 + CNR1[1:] + RUN2[1:] + CNR2[1:] + RUN3[1:])


def _len_for_phase(p):
    """Arc length along FULL_PATH at a day phase -- the legs are contiguous, so
    it is just the completed legs plus a linear slice of the current one."""
    acc = 0.0
    for pts, p0, p1 in LEGS:
        L = _cum(pts)[-1]
        if p >= p1:
            acc += L
        else:
            return acc + L * max(0.0, (p - p0) / (p1 - p0))
    return acc


def _cum(pts):
    out = [0.0]
    for a, b in zip(pts, pts[1:]):
        out.append(out[-1] + math.dist(a, b))
    return out


def _walk(pts, s):
    """Point + unit direction at arc length s along a polyline."""
    cum = _cum(pts)
    s = max(0.0, min(cum[-1], s))
    for i in range(len(pts) - 1):
        if s <= cum[i + 1] or i == len(pts) - 2:
            seg = cum[i + 1] - cum[i]
            t = (s - cum[i]) / seg if seg else 0.0
            ax, ay = pts[i]
            bx, by = pts[i + 1]
            d = math.hypot(bx - ax, by - ay) or 1.0
            return (ax + (bx - ax) * t, ay + (by - ay) * t,
                    (bx - ax) / d, (by - ay) / d)
    return (*pts[-1], 1.0, 0.0)


def at_phase(p):
    """(x, y, dx, dy) for a day phase in [0,1]."""
    p = max(0.0, min(1.0, p))
    for pts, p0, p1 in LEGS:
        if p0 <= p <= p1:
            t = (p - p0) / (p1 - p0)
            return _walk(pts, t * _cum(pts)[-1])
    return _walk(RUN3, _cum(RUN3)[-1])


# ── stroking ─────────────────────────────────────────────────────────────────
def stroke(surf, pts, w, color):
    """Thick polyline as quads + round joins, drawn on the SS surface."""
    r = w * SS / 2.0
    for a, b in zip(pts, pts[1:]):
        ax, ay = a[0] * SS, a[1] * SS
        bx, by = b[0] * SS, b[1] * SS
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy)
        if L < 1e-6:
            continue
        nx, ny = -dy / L * r, dx / L * r
        pygame.draw.polygon(surf, color, [(ax + nx, ay + ny), (bx + nx, by + ny),
                                          (bx - nx, by - ny), (ax - nx, ay - ny)])
    if r >= 1:
        for p in pts:
            pygame.draw.circle(surf, color, (int(round(p[0] * SS)),
                                             int(round(p[1] * SS))), int(round(r)))


def poly(surf, pts, color):
    pygame.draw.polygon(surf, color, [(p[0] * SS, p[1] * SS) for p in pts])


def sample_phase_range(p0, p1, n=140):
    return [at_phase(p0 + (p1 - p0) * i / n)[:2] for i in range(n + 1)]


def disc(surf, x, y, r, color):
    pygame.draw.circle(surf, color, (int(round(x * SS)), int(round(y * SS))),
                       int(round(r * SS)))


def ring(surf, x, y, r, w, outer, inner):
    disc(surf, x, y, r, outer)
    disc(surf, x, y, r - w, inner)


# ── parchment ────────────────────────────────────────────────────────────────
def build_parchment():
    """Cached noise plate: gradient + blotch + fibre + speck, built once."""
    surf = pygame.Surface((W, H)).convert()
    for y in range(H):
        pygame.draw.line(surf, lerp_c(PARCH_TOP, PARCH_BOT, y / (H - 1)),
                         (0, y), (W, y))

    rng = random.Random(20260731)

    stain = pygame.Surface((W, H), pygame.SRCALPHA)
    for _ in range(90):
        cx, cy = rng.randrange(-20, W + 20), rng.randrange(-20, H + 20)
        r = rng.randint(18, 70)
        a = rng.randint(6, 16)
        tone = (176, 152, 116, a) if rng.random() < 0.6 else (255, 246, 224, a)
        pygame.draw.circle(stain, tone, (cx, cy), r)
    surf.blit(stain, (0, 0))

    fibre = pygame.Surface((W, H), pygame.SRCALPHA)
    for _ in range(520):
        x, y = rng.randrange(W), rng.randrange(H)
        L = rng.randint(3, 11)
        a = rng.randint(10, 26)
        if rng.random() < 0.5:
            pygame.draw.line(fibre, (150, 126, 94, a), (x, y), (x + L, y))
        else:
            pygame.draw.line(fibre, (255, 250, 232, a), (x, y), (x + L, y))
    surf.blit(fibre, (0, 0))

    for _ in range(26000):
        x, y = rng.randrange(W), rng.randrange(H)
        r, g, b = surf.get_at((x, y))[:3]
        d = rng.randint(-13, 11)
        surf.set_at((x, y), (max(0, min(255, r + d)),
                             max(0, min(255, g + d)),
                             max(0, min(255, b + d))))

    edge = pygame.Surface((W, H), pygame.SRCALPHA)
    for i in range(26):
        a = int(30 * (1 - i / 26) ** 1.6)
        if a <= 0:
            continue
        pygame.draw.line(edge, (128, 100, 70, a), (i, 0), (i, H))
        pygame.draw.line(edge, (128, 100, 70, a), (W - 1 - i, 0), (W - 1 - i, H))
        pygame.draw.line(edge, (128, 100, 70, a), (0, i), (W, i))
        pygame.draw.line(edge, (128, 100, 70, a), (0, H - 1 - i), (W, H - 1 - i))
    surf.blit(edge, (0, 0))
    return surf


# ── type ─────────────────────────────────────────────────────────────────────
def ls_surf(size, text, color, sp=1):
    f = font(size)
    glyphs = [f.render(ch, True, color) for ch in text]
    w = sum(g.get_width() for g in glyphs) + sp * max(0, len(text) - 1)
    h = max((g.get_height() for g in glyphs), default=1)
    out = pygame.Surface((max(1, w), h), pygame.SRCALPHA)
    x = 0
    for g in glyphs:
        out.blit(g, (x, 0))
        x += g.get_width() + sp
    return out


def put(dst, surf, x, y, anchor="center"):
    r = surf.get_rect()
    setattr(r, anchor, (x, y))
    dst.blit(surf, r)
    return r


# ── event glyphs ─────────────────────────────────────────────────────────────
# One optical box for the whole set: every glyph is authored inside a 16x16
# square centred on its hang point, so the pendant row keeps an even rhythm no
# matter how differently shaped the marks are. Ink linework carries the read;
# each glyph is allowed exactly one saturated fill, and no more.
GBOX = 16


def _P(cx, cy, k, dx, dy):
    return (cx + dx * k, cy + dy * k)


def glyph_geyser(s, cx, cy, k=1.0):
    """Thermal vent: lipped mouth at the box floor, jet rising to the ceiling."""
    def p(dx, dy):
        return _P(cx, cy, k, dx, dy)

    jet_ink = [p(-3.4, 6.6), p(-4.6, -0.6), p(-6.0, -4.6),
               p(6.0, -4.6), p(4.6, -0.6), p(3.4, 6.6)]
    poly(s, jet_ink, INK)
    for dx, dy, r in ((-3.0, -5.2, 3.4), (3.0, -5.2, 3.4), (0, -6.6, 3.6)):
        disc(s, *p(dx, dy), r * k, INK)
    jet = [p(-2.2, 6.4), p(-3.4, -0.6), p(-4.7, -4.4),
           p(4.7, -4.4), p(3.4, -0.6), p(2.2, 6.4)]
    poly(s, jet, AMBER)
    for dx, dy, r in ((-3.0, -5.2, 2.3), (3.0, -5.2, 2.3), (0, -6.6, 2.5)):
        disc(s, *p(dx, dy), r * k, AMBER)
    stroke(s, [p(-8, 7), p(-2.6, 7)], 2.0 * k, INK)
    stroke(s, [p(2.6, 7), p(8, 7)], 2.0 * k, INK)


def glyph_lamp(s, cx, cy, k=1.0):
    """Genie lamp: bellied body, long spout, ring handle, one amber wisp."""
    def p(dx, dy):
        return _P(cx, cy, k, dx, dy)

    body = [p(math.cos(a / 24 * math.tau) * 5.6 - 0.6,
              math.sin(a / 24 * math.tau) * 3.6 + 2.4) for a in range(24)]
    poly(s, body, INK)
    poly(s, [p(-4.4, 1.0), p(-8.0, -1.2), p(-4.4, 4.6)], INK)
    ring(s, *p(5.4, 1.0), 2.9 * k, 1.3 * k, INK, PARCH_PANEL)
    poly(s, [p(-2.0, -1.0), p(2.0, -1.0), p(1.3, -3.4), p(-1.3, -3.4)], INK)
    disc(s, *p(-6.2, -4.0), 1.9 * k, AMBER)
    disc(s, *p(-4.8, -6.8), 1.3 * k, AMBER)


def glyph_clown(s, cx, cy, k=1.0):
    """Harlequin lozenge -- quartered diamond with a scarlet pip."""
    def p(dx, dy):
        return _P(cx, cy, k, dx, dy)

    top, bot = p(0, -7.6), p(0, 7.6)
    lft, rgt = p(-5.4, 0), p(5.4, 0)
    mid = p(0, 0)
    for tri, col in (((top, lft, mid), INK), ((top, rgt, mid), PARCH_CORE),
                     ((bot, lft, mid), PARCH_CORE), ((bot, rgt, mid), INK)):
        poly(s, list(tri), col)
    stroke(s, [top, rgt, bot, lft, top], 1.4 * k, INK)
    disc(s, *mid, 1.9 * k, SCARLET)


def glyph_rain(s, cx, cy, k=1.0):
    """Teardrop plus two slanted fall ticks."""
    def p(dx, dy):
        return _P(cx, cy, k, dx, dy)

    drop = [p(0, -7.8)]
    for i in range(19):
        a = math.pi * (-0.34 + 1.68 * i / 18)
        drop.append(p(math.sin(a) * 5.0, 1.6 - math.cos(a) * 5.0))
    poly(s, drop, INK)
    inner = [p(0, -5.6)]
    for i in range(19):
        a = math.pi * (-0.34 + 1.68 * i / 18)
        inner.append(p(math.sin(a) * 3.6, 1.6 - math.cos(a) * 3.6))
    poly(s, inner, SLATE)
    for dx in (-6.6, 6.6):
        stroke(s, [p(dx, 0.4), p(dx - 1.2, 5.0)], 1.5 * k, INK)


def glyph_snow(s, cx, cy, k=1.0):
    """Six-spoke asterism with barbs."""
    def p(dx, dy):
        return _P(cx, cy, k, dx, dy)

    for i in range(6):
        a = i / 6 * math.tau
        stroke(s, [p(0, 0), p(math.cos(a) * 7.4, math.sin(a) * 7.4)], 1.6 * k, INK)
        for sgn in (-1, 1):
            ba = a + sgn * 0.85
            mx, my = math.cos(a) * 4.6, math.sin(a) * 4.6
            stroke(s, [p(mx, my), p(mx + math.cos(ba) * 3.0, my + math.sin(ba) * 3.0)],
                   1.3 * k, INK)
    disc(s, *p(0, 0), 2.6 * k, INK)
    disc(s, *p(0, 0), 1.5 * k, SLATE)


# ── the macaw ────────────────────────────────────────────────────────────────
def glyph_macaw(s, cx, cy, k=1.0):
    """Death marker, built from the game bird's own proportions: long swept
    tail behind, deep chest, small round head set forward, hooked beak and a
    raised wing. Those five bumps are the whole read -- a colour-blind player
    gets the mark from silhouette alone, which a coloured bead can never do."""
    def p(dx, dy):
        return _P(cx, cy, k, dx, dy)

    tail = [p(-2.0, -0.4), p(-11.4, 3.2), p(-10.6, 5.6), p(-1.6, 3.6)]
    body = [p(-3.4, -0.8), p(0.2, -4.2), p(4.2, -3.0), p(5.4, 0.2),
            p(3.0, 3.6), p(-1.0, 4.0)]
    wing = [p(0.6, -2.6), p(-3.6, -9.2), p(1.4, -8.2), p(4.0, -3.4)]
    head = (5.0, -4.4, 3.0)
    beak = [p(7.4, -5.4), p(10.4, -3.6), p(7.6, -2.0), p(6.4, -3.8)]

    for shape in (tail, body, wing):
        poly(s, shape, INK)
        stroke(s, shape + [shape[0]], 2.6 * k, INK)
    disc(s, *p(head[0], head[1]), (head[2] + 1.3) * k, INK)
    poly(s, beak, INK)
    stroke(s, beak + [beak[0]], 1.6 * k, INK)

    for shape in (tail, body, wing):
        poly(s, shape, SCARLET)
    disc(s, *p(head[0], head[1]), head[2] * k, SCARLET)
    stroke(s, [p(0.6, -2.6), p(-1.4, -7.2)], 1.2 * k, INK)
    disc(s, *p(5.4, -5.0), 0.9 * k, INK)


# ── station beads ────────────────────────────────────────────────────────────
# Parchment sits on a ~40 deg warm axis. Any bead landing inside +/-25 deg of
# it dissolves into the plate at bead size, which is exactly what golden hour,
# sunset and sunrise all do if you take their sky colour literally. Offenders
# are pushed across into the cool half, then spread so no two stations share a
# hue neighbourhood, then darkened until they clear the plate on value too.
PARCH_HUE = colorsys.rgb_to_hls(*[c / 255 for c in PARCH_TOP])[0] * 360
HUE_GUARD = 25.0
BEAD_MIN_DL = 92.0


def _hue_sep(a, b):
    d = abs(a - b) % 360.0
    return min(d, 360.0 - d)


def _build_bead_colors():
    out, taken = {}, []
    for ph, name in PHASE_BOUNDARIES:
        c = palette_for_phase(ph)["sky_mid"]
        h, l, sat = colorsys.rgb_to_hls(*[max(0.0, min(1.0, v / 255)) for v in c])
        hd = h * 360.0
        sat = max(sat, 0.58)
        if _hue_sep(hd, PARCH_HUE) < HUE_GUARD:
            hd = (PARCH_HUE + HUE_GUARD + 9.0) % 360.0
        for _ in range(720):
            if (_hue_sep(hd, PARCH_HUE) >= HUE_GUARD
                    and all(_hue_sep(hd, t) >= HUE_GUARD for t in taken)):
                break
            hd = (hd + 1.0) % 360.0
        taken.append(hd)
        l = min(l, 0.44)
        for _ in range(40):
            r, g, b = colorsys.hls_to_rgb(hd / 360.0, l, sat)
            col = (round(r * 255), round(g * 255), round(b * 255))
            if PARCH_L - lum(col) >= BEAD_MIN_DL:
                break
            l = max(0.05, l - 0.02)
        out[name] = col
    return out


BEADS = _build_bead_colors()


# ── the screen ───────────────────────────────────────────────────────────────
CART = pygame.Rect(26, 400, 308, 104)
KEY_COLS = (44, 152, 254)
KEY_ROWS = (534, 558)
PILL = pygame.Rect(120, 580, 120, 36)

# Default hang; short/long only ever resolve a collision, and only by changing
# the LEADER LENGTH. Leaning a pendant would make the plate look like it has
# three different conventions instead of one.
HANG_MID, HANG_SHORT, HANG_LONG = 24, 17, 32

PENDANTS = [
    (THERMAL_START_PHASE, glyph_geyser, HANG_SHORT),   # clears the death flag
    (LAMP_PHASE, glyph_lamp, HANG_MID),
    (CLOWN_PHASE, glyph_clown, HANG_SHORT),            # 21 px from the rain mark
    (RAIN_PHASE, glyph_rain, HANG_LONG),
    (SNOW_STORM_CENTER, glyph_snow, HANG_MID),
]


def render_screen():
    screen = build_parchment()

    frame = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.rect(frame, (*INK, 105), pygame.Rect(9, 9, W - 18, H - 18), 1)
    pygame.draw.rect(frame, (*INK, 45), pygame.Rect(12, 12, W - 24, H - 24), 1)
    for cx, cy, sx, sy in ((9, 9, 1, 1), (W - 10, 9, -1, 1),
                           (9, H - 10, 1, -1), (W - 10, H - 10, -1, -1)):
        pygame.draw.line(frame, (*INK, 130), (cx, cy + 7 * sy), (cx + 7 * sx, cy))
    screen.blit(frame, (0, 0))

    band_l = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
    ahead_l = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
    rail_l = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
    marks = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)

    # ── thermal corridor: a zone the route runs THROUGH ───────────────────
    # A thin dash rule parallel to the track just reads as a second line. A
    # wide wash with a hatched boundary is unambiguously an area.
    corr = sample_phase_range(THERMAL_START_PHASE, THERMAL_END_PHASE, 160)
    stroke(band_l, corr, 23, (*WASH, 92))
    for i in range(0, len(corr) - 1, 5):
        x, y = corr[i]
        nx, ny = corr[min(i + 1, len(corr) - 1)]
        dx, dy = nx - x, ny - y
        d = math.hypot(dx, dy) or 1.0
        px, py = -dy / d, dx / d
        if py > 0:
            px, py = -px, -py
        ex, ey = x + px * 11.5, y + py * 11.5
        stroke(band_l, [(ex, ey), (ex - px * 4.2 + dx / d * 4.2,
                                   ey - py * 4.2 + dy / d * 4.2)], 1.3, (*WASH, 210))
    for end, sgn in ((corr[0], 1), (corr[-1], -1)):
        stroke(band_l, [(end[0], end[1] - 11.5), (end[0], end[1] + 11.5)],
               1.6, (*WASH, 210))

    # ── projected route: thin, faint, still fully continuous ─────────────
    stroke(ahead_l, FULL_PATH, 3, INK)

    # ── surveyed rail: full weight, full chroma, flat ────────────────────
    flown = sample_phase_range(0.0, DEATH_PHASE, 90)
    stroke(rail_l, flown, 4, RAIL)

    # ── travel chevrons ──────────────────────────────────────────────────
    # The single fix for a boustrophedon map: without them the fold-back run
    # reads left-to-right like the other two and the whole day runs backwards.
    dpt = at_phase(DEATH_PHASE)[:2]
    beads_xy = [at_phase(ph)[:2] for ph, _ in PHASE_BOUNDARIES]
    cum = _cum(FULL_PATH)
    flown_len = _len_for_phase(DEATH_PHASE)
    step = 58.0
    s = step * 0.55
    while s < cum[-1]:
        base, s = s, s + step
        # A chevron that lands on a station is dropped rather than drawn over
        # it -- but dropping outright tore 116 px holes in the rhythm, so slide
        # it along the track first and only give up if nowhere is clear.
        hit = None
        for off in (0, 12, -12, 20, -20):
            t = base + off
            if not (6 < t < cum[-1] - 10):
                continue
            cand = _walk(FULL_PATH, t)
            if math.dist(cand[:2], dpt) < 16:
                continue
            if any(math.dist(cand[:2], b) < 10.5 for b in beads_xy):
                continue
            hit = (t, cand)
            break
        if hit is None:
            continue
        base, (x, y, dx, dy) = hit
        nx, ny = -dy, dx
        head = [(x + dx * 3.1, y + dy * 3.1),
                (x - dx * 2.2 + nx * 2.6, y - dy * 2.2 + ny * 2.6),
                (x - dx * 0.5, y - dy * 0.5),
                (x - dx * 2.2 - nx * 2.6, y - dy * 2.2 - ny * 2.6)]
        # Cream reads on the dark surveyed rail; ink reads on the faint
        # projected line. Same mark, whichever ground it lands on.
        poly(marks, head, CREAM if base <= flown_len else INK)

    # ── terminus cap ─────────────────────────────────────────────────────
    ex, ey, _, _ = at_phase(1.0)
    stroke(marks, [(ex + 1.5, ey - 7), (ex + 1.5, ey + 7)], 3, INK)

    # ── event pendants: one convention, straight down, common 16 px box ──
    for ph, fn, hang in PENDANTS:
        x, y, _, _ = at_phase(ph)
        stroke(marks, [(x, y + 3), (x, y + hang - GBOX / 2 + 1)], 1.4, INK_SOFT)
        fn(marks, x, y + hang)

    # ── stations ─────────────────────────────────────────────────────────
    for ph, name in PHASE_BOUNDARIES:
        x, y, _, _ = at_phase(ph)
        col = BEADS[name]
        if ph <= DEATH_PHASE:
            disc(marks, x, y, 6.4, INK)
            disc(marks, x, y, 4.8, col)
        else:
            # Hollow: the ink rim states "charted", the parchment core states
            # "not yet flown", and the pip keeps the phase's identity colour.
            disc(marks, x, y, 5.6, INK)
            disc(marks, x, y, 3.9, PARCH_CORE)
            disc(marks, x, y, 1.9, col)

    # ── death marker: macaw + swallowtail flag ───────────────────────────
    dx_, dy_ = dpt
    lab_a, lab_b = "ENDED HERE", "PILLAR %d · %d s ALOFT" % (DEATH_PILLAR, TIME_ALIVE)
    wa = ls_surf(9, lab_a, SCARLET, 1).get_width()
    wb = ls_surf(7, lab_b, INK, 1).get_width()
    tail = 8
    bw = tail + 9 + max(wa, wb) + 12
    flag_top, flag_bot = dy_ + 30, dy_ + 70
    stroke(marks, [(dx_, dy_ + 5), (dx_, flag_bot - 1)], 1.6, INK)
    banner = [(dx_, flag_top), (dx_ - bw, flag_top),
              (dx_ - bw + tail, (flag_top + flag_bot) / 2),
              (dx_ - bw, flag_bot), (dx_, flag_bot)]
    poly(marks, banner, CREAM)
    stroke(marks, banner + [banner[0]], 1.4, INK)
    poly(marks, [(dx_ - 5, flag_top), (dx_, flag_top),
                 (dx_, flag_bot), (dx_ - 5, flag_bot)], SCARLET)
    # A parchment knockout under the bird so the rail never runs through it:
    # the mark has to be the single most isolated blob on the plate.
    disc(marks, dx_, dy_ - 1, 9.4, (*PARCH_CORE, 232))
    glyph_macaw(marks, dx_, dy_, 0.86)

    # ── panels ───────────────────────────────────────────────────────────
    notch = 9
    cpoly = [(CART.left + notch, CART.top), (CART.right - notch, CART.top),
             (CART.right, CART.top + notch), (CART.right, CART.bottom - notch),
             (CART.right - notch, CART.bottom), (CART.left + notch, CART.bottom),
             (CART.left, CART.bottom - notch), (CART.left, CART.top + notch)]
    poly(marks, cpoly, (*PARCH_PANEL, 235))
    stroke(marks, cpoly + [cpoly[0]], 1.4, INK)
    inner = [(p[0] + (3 if p[0] < CART.centerx else -3),
              p[1] + (3 if p[1] < CART.centery else -3)) for p in cpoly]
    stroke(marks, inner + [inner[0]], 0.8, (*INK, 90))

    pygame.draw.rect(marks, (*PARCH_PANEL, 250),
                     pygame.Rect(PILL.x * SS, PILL.y * SS, PILL.w * SS, PILL.h * SS),
                     border_radius=18 * SS)
    pygame.draw.rect(marks, INK,
                     pygame.Rect(PILL.x * SS, PILL.y * SS, PILL.w * SS, PILL.h * SS),
                     width=2 * SS, border_radius=18 * SS)
    ax, ay = PILL.x + 26, PILL.centery
    stroke(marks, [(ax + 4, ay - 5), (ax - 1, ay), (ax + 4, ay + 5)], 2, INK)

    # ── key swatches, drawn from the same code the map uses ──────────────
    c0, c1, c2 = KEY_COLS
    r0, r1 = KEY_ROWS
    disc(marks, c0, r0, 6.4, INK)
    disc(marks, c0, r0, 4.8, BEADS["DAY"])
    disc(marks, c0, r1, 5.6, INK)
    disc(marks, c0, r1, 3.9, PARCH_CORE)
    disc(marks, c0, r1, 1.9, BEADS["NIGHT"])
    stroke(marks, [(c1 - 10, r0), (c1 + 10, r0)], 4, RAIL)
    poly(marks, [(c1 + 3.1, r0), (c1 - 2.2, r0 - 2.6),
                 (c1 - 0.5, r0), (c1 - 2.2, r0 + 2.6)], CREAM)
    glyph_macaw(marks, c1 + 1, r1, 0.74)
    stroke(marks, [(c2 - 11, r0), (c2 + 9, r0)], 12, (*WASH, 92))
    for t in range(4):
        hx = c2 - 9 + t * 6
        stroke(marks, [(hx, r0 - 6), (hx + 3.6, r0 - 2.4)], 1.3, (*WASH, 210))
    stroke(marks, [(c2, r1 - 9), (c2, r1 - 4)], 1.4, INK_SOFT)
    glyph_clown(marks, c2, r1 + 2, 0.62)

    # ── composite ────────────────────────────────────────────────────────
    screen.blit(pygame.transform.smoothscale(band_l, (W, H)), (0, 0))
    ahead = pygame.transform.smoothscale(ahead_l, (W, H))
    ahead.set_alpha(152)                 # projected track sits at ~60% ink
    screen.blit(ahead, (0, 0))
    screen.blit(pygame.transform.smoothscale(rail_l, (W, H)), (0, 0))
    screen.blit(pygame.transform.smoothscale(marks, (W, H)), (0, 0))

    # ── type layer ───────────────────────────────────────────────────────
    put(screen, ls_surf(8, "SKYBIT · AERIAL SURVEY", INK_SOFT, 2), 180, 24)
    put(screen, ls_surf(27, "FLIGHT LOG", INK, 2), 180, 38, "midtop")
    put(screen, ls_surf(9, "EXPEDITION 001  ·  MORNING  ·  %d%% INTO DAY %d"
                        % (PCT_INTO_DAY, DAY_NUMBER), INK_SOFT, 1), 180, 76)

    rule = pygame.Surface((W, H), pygame.SRCALPHA)
    for yy, a in ((95, 120), (98, 55)):
        pygame.draw.line(rule, (*INK, a), (26, yy), (166, yy))
        pygame.draw.line(rule, (*INK, a), (194, yy), (334, yy))
    pygame.draw.polygon(rule, (*INK, 150), [(180, 91), (185, 96.5), (180, 102), (175, 96.5)])
    pygame.draw.line(rule, (*INK, 70), (26, 512), (334, 512))
    pygame.draw.line(rule, (*INK, 70), (26, 570), (334, 570))
    screen.blit(rule, (0, 0))

    for ph, name in PHASE_BOUNDARIES:
        x, y, _, _ = at_phase(ph)
        s = ls_surf(9, name, INK, 1)
        put(screen, s, min(max(x, 14 + s.get_width() / 2), W - 14 - s.get_width() / 2),
            y - 16, "midbottom")

    put(screen, ls_surf(8, "DAY 2", INK_SOFT, 1), 302, ROW_Y[2] - 16, "midbottom")

    bx = dx_ - bw + tail + 9
    put(screen, ls_surf(9, lab_a, SCARLET, 1), bx, flag_top + 14, "midleft")
    put(screen, ls_surf(7, lab_b, INK, 1), bx, flag_top + 29, "midleft")

    # ── cartouche copy ───────────────────────────────────────────────────
    put(screen, ls_surf(15, "%d%% OF THE DAY UNCHARTED" % PCT_UNCHARTED, INK, 1),
        180, CART.top + 20)
    pygame.draw.line(screen, INK_FAINT, (104, CART.top + 34), (256, CART.top + 34))
    rows = [(glyph_lamp, "GENIE LAMP", "PILLAR %d" % LATE_GAME_PILLAR),
            (glyph_clown, "CLOWN GAUNTLET", "PILLAR %d" % CLOWN_START_PILLAR),
            (glyph_rain, "STORM FRONT", "PILLAR %d" % RAIN_START_PILLAR)]
    for i, (_fn, what, where) in enumerate(rows):
        yy = CART.top + 52 + i * 20
        wl = put(screen, ls_surf(9, what, INK, 1), 68, yy, "midleft")
        wr = put(screen, ls_surf(9, where, INK_SOFT, 1), 306, yy, "midright")
        for dx in range(wl.right + 6, wr.left - 4, 4):
            screen.set_at((dx, yy + 4), INK_FAINT)

    for cx, r, txt in ((c0, r0, "LOGGED"), (c0, r1, "AHEAD"),
                       (c1, r0, "FLOWN"), (c1, r1, "ENDED"),
                       (c2, r0, "HAZARD"), (c2, r1, "EVENT")):
        put(screen, ls_surf(8, txt, INK, 1), cx + 14, r, "midleft")
    put(screen, ls_surf(7, "KEY", INK_FAINT, 2), 26, 516, "topleft")

    put(screen, ls_surf(12, "BACK", INK, 2), 190, PILL.centery)
    return screen


# ── cartouche glyph pass (needs the SS pipeline, so it rides a second layer) ──
def add_cartouche_glyphs(screen):
    layer = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
    for i, fn in enumerate((glyph_lamp, glyph_clown, glyph_rain)):
        fn(layer, 48, CART.top + 52 + i * 20, 0.75)
    screen.blit(pygame.transform.smoothscale(layer, (W, H)), (0, 0))


# ── review sheet ─────────────────────────────────────────────────────────────
def squint(surf, factor=4):
    """4x down/up resample -- the standard 'does it read from across the room'
    pass. Whatever survives it is the composition."""
    w, h = surf.get_size()
    small = pygame.transform.smoothscale(surf, (max(1, w // factor), max(1, h // factor)))
    return pygame.transform.smoothscale(small, (w, h))


def build_sheet(screen):
    SW, SH = 1010, 960
    sheet = pygame.Surface((SW, SH))
    for y in range(SH):
        pygame.draw.line(sheet, lerp_c((52, 49, 46), (36, 34, 33), y / (SH - 1)),
                         (0, y), (SW, y))

    put(sheet, font(19).render(
        "SKYBIT  ·  FLIGHT LOG PROGRESS  ·  CONCEPT: EXPEDITION ROUTE  ·  ROUND 2",
        True, (238, 228, 210)), 24, 22, "midleft")
    put(sheet, font(11).render(
        "flown run is the hero: 1/4 of the day on run one · chevrons everywhere · macaw death mark · hollow ahead-beads",
        True, (156, 146, 136)), 24, 44, "midleft")

    def panel(x, y, surf, label, scale=1.0):
        if scale != 1.0:
            surf = pygame.transform.smoothscale(
                surf, (int(surf.get_width() * scale), int(surf.get_height() * scale)))
        pygame.draw.rect(sheet, (18, 17, 16),
                         pygame.Rect(x - 2, y - 2, surf.get_width() + 4,
                                     surf.get_height() + 4))
        sheet.blit(surf, (x, y))
        put(sheet, font(12).render(label, True, (176, 166, 154)),
            x, y + surf.get_height() + 12, "midleft")
        return y + surf.get_height() + 20

    panel(24, 68, screen, "FULL SCREEN  ·  360 × 640  ·  1:1")

    sq = pygame.transform.smoothscale(squint(screen), (108, 192))
    panel(24, 740, sq, "SQUINT 4×", 1.0)

    det = pygame.Surface((130, 116))
    det.blit(screen, (0, 0), pygame.Rect(172, 118, 130, 116))
    panel(160, 740, det, "DEATH MARK  ·  1.6×  ·  macaw, knockout, flag", 1.6)

    route = pygame.Surface((340, 300))
    route.blit(screen, (0, 0), pygame.Rect(10, 108, 340, 300))
    panel(416, 68, route, "ROUTE BAND  ·  1.65×  ·  chevrons, beads, corridor, pendants", 1.65)

    lower = pygame.Surface((340, 230))
    lower.blit(screen, (0, 0), pygame.Rect(10, 396, 340, 230))
    panel(416, 600, lower, "CARTOUCHE · KEY · FOOTER  ·  1.35×", 1.35)

    return sheet


def main():
    screen = render_screen()
    add_cartouche_glyphs(screen)

    out_dir = os.path.join(ROOT, "docs", "flight_log_progress", "expedition_route")
    os.makedirs(out_dir, exist_ok=True)
    sheet = build_sheet(screen)
    path = os.path.join(out_dir, "round_2.png")
    pygame.image.save(sheet, path)
    print("saved", path, sheet.get_size())

    # ── verification ─────────────────────────────────────────────────────
    print("\n-- stations (parch hue %.1f, L %.1f) --" % (PARCH_HUE, PARCH_L))
    hues = []
    for ph, name in PHASE_BOUNDARIES:
        x, y, _, _ = at_phase(ph)
        c = BEADS[name]
        h = colorsys.rgb_to_hls(*[v / 255 for v in c])[0] * 360
        hues.append((name, h))
        print("  %-12s ph %.4f (%6.1f,%3.0f)  %s  hue %5.1f  dPARCH %5.1f  dL %5.1f"
              % (name, ph, x, y, c, h, _hue_sep(h, PARCH_HUE), PARCH_L - lum(c)))
    worst = min((_hue_sep(a[1], b[1]), a[0], b[0])
                for i, a in enumerate(hues) for b in hues[i + 1:])
    print("  closest bead pair: %.1f deg  (%s / %s)" % worst)

    print("\n-- rail vs projected line (dL from parchment) --")
    for lbl, px, py in (("flown rail", 150, ROW_Y[0]),
                        ("projected run2", 140, ROW_Y[1]),
                        ("projected run3", 140, ROW_Y[2]),
                        ("plate", 150, ROW_Y[0] - 40)):
        best = None
        for yy in range(py - 4, py + 5):
            c = screen.get_at((px, yy))[:3]
            if best is None or lum(c) < lum(best):
                best = c
        print("  %-15s %s  dL %5.1f" % (lbl, best, PARCH_L - lum(best)))

    print("\n-- squint 4x: mean darkness in a 22 px box --")
    sq = squint(screen)
    def box_dark(cx, cy, r=11):
        tot = n = 0
        for yy in range(int(cy - r), int(cy + r)):
            for xx in range(int(cx - r), int(cx + r)):
                if 0 <= xx < W and 0 <= yy < H:
                    tot += max(0.0, PARCH_L - lum(sq.get_at((xx, yy))[:3]))
                    n += 1
        return tot / max(1, n)
    dxp, dyp = at_phase(DEATH_PHASE)[:2]
    spots = [("MACAW", dxp, dyp)]
    for ph, name in PHASE_BOUNDARIES:
        x, y, _, _ = at_phase(ph)
        spots.append(("bead " + name, x, y))
    for ph, fn, hang in PENDANTS:
        x, y, _, _ = at_phase(ph)
        spots.append(("pend " + fn.__name__[6:], x, y + hang))
    ranked = sorted(((box_dark(x, y), n) for n, x, y in spots), reverse=True)
    for v, n in ranked:
        print("  %-16s %6.2f%s" % (n, v, "   <-- most isolated" if n == ranked[0][1] else ""))

    print("\n-- raw pixels through the death point (y=%d) --" % dyp)
    row = [screen.get_at((x, int(dyp)))[:3] for x in range(int(dxp) - 14, int(dxp) + 15, 4)]
    print("  " + "  ".join("%3d" % round(lum(c)) for c in row))

    print("\n-- layout collisions --")
    def vspan(name, a, b):
        return (name, a, b)
    bands = [vspan("run1 names", ROW_Y[0] - 27, ROW_Y[0] - 16),
             vspan("run1 geyser", ROW_Y[0] + HANG_SHORT - 8, ROW_Y[0] + HANG_SHORT + 8),
             vspan("run1 flag", ROW_Y[0] + 30, ROW_Y[0] + 70),
             vspan("run2 names", ROW_Y[1] - 27, ROW_Y[1] - 16),
             vspan("run2 pend", ROW_Y[1] + HANG_SHORT - 8, ROW_Y[1] + HANG_LONG + 8),
             vspan("run3 names", ROW_Y[2] - 27, ROW_Y[2] - 16),
             vspan("run3 pend", ROW_Y[2] + HANG_MID - 8, ROW_Y[2] + HANG_MID + 8),
             vspan("cartouche", CART.top, CART.bottom),
             vspan("key", 512, 566),
             vspan("footer", PILL.top, PILL.bottom)]
    prev = None
    for n, a, b in bands:
        gap = "" if prev is None else "  gap %+d" % (a - prev)
        print("  %-13s %3d..%3d%s" % (n, a, b, gap))
        prev = b
    lx = dxp - (8 + 9 + max(ls_surf(9, "ENDED HERE", SCARLET, 1).get_width(),
                            ls_surf(7, "PILLAR 25 · 47 s ALOFT", INK, 1).get_width()) + 12)
    print("  flag left edge x=%.0f (frame inner 12)" % lx)
    print("  route extent x %d..%d  centre %.1f" % (LEFT - CH, RIGHT + CH,
                                                    ((LEFT - CH) + (RIGHT + CH)) / 2))

    print("\n-- station name extents (frame is 12..348) --")
    spans = []
    for ph, name in PHASE_BOUNDARIES:
        x, y, _, _ = at_phase(ph)
        w = ls_surf(9, name, INK, 1).get_width()
        cx = min(max(x, 14 + w / 2), W - 14 - w / 2)
        spans.append((y, cx - w / 2, cx + w / 2, name))
    for y, a, b, name in spans:
        clash = [n for yy, aa, bb, n in spans
                 if n != name and yy == y and aa < b and a < bb]
        print("  %-12s row %3.0f  x %5.1f..%5.1f%s"
              % (name, y, a, b, "  CLASH " + str(clash) if clash else ""))


if __name__ == "__main__":
    main()
