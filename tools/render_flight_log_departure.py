#!/usr/bin/env python3
"""departure_board · flight_log · round_1

The Flight Log read as a split-flap airport departures board. Seven rows =
the seven time-of-day phases of Skybit's day cycle; each row is 24 flap tiles
across its pillar span, so a whole run reads as one board of sky-coloured
flaps. Every tile carries TWO registers split by its hinge — weather forecast
above, gameplay event below — which is what lets a single tile say "it rained
here AND there was a coin rush" without inventing a third colour.

Unflown phases stay on the board, because a departures board shows the flights
you have not taken yet: their flaps go slate but keep their chroma, and the
left-gutter colour chip stays at full saturation so all seven hues of the day
are legible at a glance even on a 25-pillar run.
"""
import os
import sys
import pathlib

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from PIL import Image, ImageDraw

from game.biome import PHASE_BOUNDARIES, palette_for_phase
from game.draw import lerp_color, NEAR_BLACK, UI_CREAM

W, H = 360, 640

_GOLD_BRIGHT = (240, 192, 64)
_GOLD_MUTED = (216, 184, 85)

BOARD_BOT = (18, 20, 26)
SEP = (30, 32, 38)
HOUSING = (9, 9, 16)

DEATH_BODY = (200, 40, 40)
DEATH_HI = (255, 110, 100)
DEATH_LO = (180, 30, 30)

RAIN_C = (120, 185, 255)
SNOW_C = (228, 238, 252)
THERM_C = (255, 194, 96)
CLOWN_C = (255, 130, 195)
RUSH_C = (255, 214, 90)

SLATE = (40, 44, 60)

FONT_PATH = "/home/user/skybit/game/assets/LiberationSans-Bold.ttf"
_fcache: dict = {}


def font(size):
    f = _fcache.get(size)
    if f is None:
        f = pygame.font.Font(FONT_PATH, size)
        _fcache[size] = f
    return f


# ── run data ────────────────────────────────────────────────────────────────
PILLARS_CLEARED = 25
SCORE = 25
DAY_N = 1
RUN_SECONDS = 47
COINS = 0

# Pillar span of each named phase. Pillar accrual is NOT linear in phase
# (scroll speed ramps through the early run), so the mapping is carried as an
# explicit knot table rather than derived from the phase fractions.
PILLAR_SPANS = [
    (0.0, 33.7), (33.7, 57.7), (57.7, 85.1), (85.1, 109.1),
    (109.1, 136.5), (136.5, 157.1), (157.1, 175.0),
]
TOTAL_PILLARS = 175.0

WEATHER_ZONES = [("THERMAL", 0.106, 0.206, "thermal"),
                 ("RAIN", 0.430, 0.690, "rain"),
                 ("SNOW", 0.780, 1.000, "snow")]
CLOWN_ZONE = (0.403, 0.539)
RUSH_EVERY = 15
FINALE_PILLARS = 3

ROW_TOPS = [96, 154, 212, 270, 328, 386, 444]
ROW_H = 58
TILES = 24
FIELD_X, FIELD_W = 72, 196
TILE_W = 7
PITCH = FIELD_W / TILES
TILE_TOP_OFF, TILE_H = 9, 40

LAB_X0, LAB_X1 = 272, 348


def phase_bounds(i):
    lo = PHASE_BOUNDARIES[i][0]
    hi = PHASE_BOUNDARIES[i + 1][0] if i + 1 < len(PHASE_BOUNDARIES) else 1.0
    return lo, hi


def phase_to_pillar(ph):
    for i in range(7):
        lo, hi = phase_bounds(i)
        if lo <= ph <= hi:
            p0, p1 = PILLAR_SPANS[i]
            t = (ph - lo) / (hi - lo) if hi > lo else 0.0
            return p0 + t * (p1 - p0)
    return TOTAL_PILLARS


# ── small drawing helpers ───────────────────────────────────────────────────

def vgrad(surf, rect, stops):
    """Vertical multi-stop gradient. `stops` = [(t, colour), ...] ascending."""
    x, y, w, h = rect
    for i in range(h):
        t = i / max(1, h - 1)
        for k in range(len(stops) - 1):
            t0, c0 = stops[k]
            t1, c1 = stops[k + 1]
            if t0 <= t <= t1:
                pygame.draw.line(surf,
                                 lerp_color(c0, c1,
                                            (t - t0) / (t1 - t0) if t1 > t0 else 0.0),
                                 (x, y + i), (x + w - 1, y + i))
                break


def round_mask(surf, radius):
    m = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.rect(m, (255, 255, 255, 255), m.get_rect(), border_radius=radius)
    surf.blit(m, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)


def text(surf, txt, pos, size, colour, anchor="topleft", max_w=None, alpha=255):
    """Anchored text that steps down a point at a time until it fits `max_w` —
    the phase names differ by eight characters and the gutter is 60px wide."""
    s = size
    f = font(s)
    img = f.render(txt, True, colour)
    while max_w and img.get_width() > max_w and s > 5:
        s -= 1
        f = font(s)
        img = f.render(txt, True, colour)
    if alpha < 255:
        img.set_alpha(alpha)
    r = img.get_rect(**{anchor: pos})
    surf.blit(img, r.topleft)
    return r


def text_shadowed(surf, txt, pos, size, colour, anchor="topleft", sa=150):
    f = font(size)
    sh = f.render(txt, True, NEAR_BLACK)
    sh.set_alpha(sa)
    img = f.render(txt, True, colour)
    r = img.get_rect(**{anchor: pos})
    surf.blit(sh, (r.x + 1, r.y + 1))
    surf.blit(img, r.topleft)
    return r


# ── tile glyphs ─────────────────────────────────────────────────────────────
# Every glyph is stamped twice: a near-black copy one pixel down, then the
# bright face. Flaps are sky gradients, so a bare 1px glyph loses its edge
# against a pale DAY tile without that keyline.

def _stamp(surf, fn, cx, cy, colour):
    fn(surf, cx, cy + 1, (0, 0, 0, 150))
    fn(surf, cx, cy, colour)


def _g_rain(surf, cx, cy, c):
    pygame.draw.line(surf, c, (cx - 1, cy - 3), (cx - 1, cy - 1))
    pygame.draw.line(surf, c, (cx + 1, cy - 1), (cx + 1, cy + 1))
    pygame.draw.line(surf, c, (cx - 1, cy + 2), (cx - 1, cy + 3))


def _g_snow(surf, cx, cy, c):
    pygame.draw.line(surf, c, (cx, cy - 3), (cx, cy + 3))
    pygame.draw.line(surf, c, (cx - 2, cy - 2), (cx + 2, cy + 2))
    pygame.draw.line(surf, c, (cx - 2, cy + 2), (cx + 2, cy - 2))


def _g_thermal(surf, cx, cy, c):
    pygame.draw.line(surf, c, (cx, cy - 1), (cx, cy + 3))
    pygame.draw.polygon(surf, c, [(cx - 2, cy - 1), (cx + 2, cy - 1), (cx, cy - 4)])


def _g_clown(surf, cx, cy, c):
    for dx, dy in ((0, -3), (-2, 1), (2, 1)):
        pygame.draw.rect(surf, c, (cx + dx - 1, cy + dy - 1, 2, 2))


def _g_rush(surf, cx, cy, c):
    pygame.draw.circle(surf, c, (cx, cy), 3, 1)


def _g_finale(surf, cx, cy, c):
    for ox in (-3, 0, 3):
        pygame.draw.line(surf, c, (cx + ox - 1, cy - 2), (cx + ox + 1, cy))
        pygame.draw.line(surf, c, (cx + ox + 1, cy), (cx + ox - 1, cy + 2))


WEATHER_GLYPH = {"rain": (_g_rain, RAIN_C), "snow": (_g_snow, SNOW_C),
                 "thermal": (_g_thermal, THERM_C)}
PLAY_GLYPH = {"clown": (_g_clown, CLOWN_C), "rush": (_g_rush, RUSH_C),
              "finale": (_g_finale, RUSH_C)}


# ── flaps ───────────────────────────────────────────────────────────────────

def lift(c, amount=12):
    """Flaps are printed cards read against the board's own backlight, so the
    whole ramp is nudged up. Without it the NIGHT row's sky_top (5,8,30) sits
    within a pixel of the housing black and those flaps vanish."""
    return tuple(min(255, v + amount) for v in c)


_CHIP_FLOOR = 165


def chip_ramp(pal):
    """The phase's own sky ramp scaled by ONE factor so a dark phase clears the
    board's near-black. Scaling every channel of every stop alike keeps hue and
    saturation exact — the chip really is full chroma."""
    stops = [pal["sky_top"], pal["sky_mid"], pal["sky_bot"]]
    peak = max(max(c) for c in stops)
    k = _CHIP_FLOOR / peak if 0 < peak < _CHIP_FLOOR else 1.0
    return [(t, tuple(min(255, int(v * k)) for v in c))
            for t, c in zip((0.0, 0.5, 1.0), stops)]


def sky_stops(pal):
    return [(0.0, lift(pal["sky_top"])), (0.5, lift(pal["sky_mid"])),
            (1.0, lift(pal["sky_bot"]))]


def flap_edges(t, flown):
    """1px lit top edge + 1px cast shade along the bottom — the card's
    thickness. Unflown flaps skip the highlight: an unlit flap has no specular,
    which separates them without stealing any chroma."""
    if flown:
        hl = pygame.Surface((TILE_W, 1), pygame.SRCALPHA)
        hl.fill((255, 255, 255, 60))
        t.blit(hl, (0, 0))
    sh = pygame.Surface((TILE_W, 1), pygame.SRCALPHA)
    sh.fill((0, 0, 0, 110))
    t.blit(sh, (0, TILE_H - 1))


def draw_tile(surf, x, y, pal, flown, weather, play):
    """One split-flap: 3-stop sky gradient, hinged at the vertical midpoint,
    upper register = weather, lower register = gameplay."""
    t = pygame.Surface((TILE_W, TILE_H), pygame.SRCALPHA)
    vgrad(t, (0, 0, TILE_W, TILE_H), sky_stops(pal))

    half = TILE_H // 2
    if weather:
        fn, c = WEATHER_GLYPH[weather]
        _stamp(t, fn, TILE_W // 2, half // 2 + 1, c)
    if play:
        fn, c = PLAY_GLYPH[play]
        _stamp(t, fn, TILE_W // 2, half + half // 2 - 1, c)

    # Hinge: the black seam plus a one-pixel lit lip on the flap below it, so
    # the tile reads as two physical cards rather than a printed stripe.
    pygame.draw.line(t, NEAR_BLACK, (0, half - 1), (TILE_W - 1, half - 1))
    if flown:
        lip = pygame.Surface((TILE_W, 1), pygame.SRCALPHA)
        lip.fill((255, 255, 255, 40))
        t.blit(lip, (0, half))
    flap_edges(t, flown)

    if not flown:
        ov = pygame.Surface((TILE_W, TILE_H), pygame.SRCALPHA)
        ov.fill((*SLATE, 60))
        t.blit(ov, (0, 0))

    round_mask(t, 1)
    surf.blit(t, (x, y))


def build_death_tile():
    t = pygame.Surface((TILE_W, TILE_H), pygame.SRCALPHA)
    half = TILE_H // 2
    vgrad(t, (0, 0, TILE_W, half), [(0.0, DEATH_HI), (1.0, DEATH_BODY)])
    vgrad(t, (0, half, TILE_W, TILE_H - half), [(0.0, DEATH_BODY), (1.0, DEATH_LO)])
    pygame.draw.line(t, NEAR_BLACK, (0, half - 1), (TILE_W - 1, half - 1))
    # Engraved ▼: a pale under-stamp gives the black chevron its cut edge.
    cx, cy = TILE_W // 2, half + 1
    pygame.draw.polygon(t, (255, 235, 232),
                        [(cx - 3, cy - 3), (cx + 3, cy - 3), (cx, cy + 2)])
    pygame.draw.polygon(t, (10, 6, 10),
                        [(cx - 2, cy - 3), (cx + 2, cy - 3), (cx, cy + 1)])
    flap_edges(t, True)
    round_mask(t, 1)
    return t


def death_glow(surf, x, y):
    """Value spread: the terminus bleeds red into its neighbours so the eye
    lands on it before it reads any glyph. Composited, not added — an additive
    bleed blew the pale DAY flaps beside it out to white."""
    pad = 6
    g = pygame.Surface((TILE_W + pad * 2, TILE_H + pad * 2), pygame.SRCALPHA)
    for r in range(pad, 0, -1):
        a = int(52 * (1 - (r - 1) / pad) ** 1.4)
        pygame.draw.rect(g, (215, 48, 40, a),
                         (pad - r, pad - r, TILE_W + r * 2, TILE_H + r * 2),
                         border_radius=r + 1)
    surf.blit(g, (x - pad, y - pad))


def led(surf, cx, cy, state):
    if state == "grounded":
        core, halo = (255, 90, 80), (230, 50, 40)
    elif state == "cleared":
        core, halo = (255, 210, 120), _GOLD_BRIGHT
    else:
        d = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(d, (*_GOLD_MUTED, 80), (4, 4), 3)
        pygame.draw.circle(d, (*NEAR_BLACK, 120), (4, 4), 3, 1)
        surf.blit(d, (cx - 4, cy - 4))
        return
    g = pygame.Surface((14, 14), pygame.SRCALPHA)
    for r in range(6, 2, -1):
        pygame.draw.circle(g, (*halo, int(70 * (7 - r) / 4)), (7, 7), r)
    surf.blit(g, (cx - 7, cy - 7), special_flags=pygame.BLEND_ADD)
    pygame.draw.circle(surf, halo, (cx, cy), 3)
    pygame.draw.circle(surf, core, (cx - 1, cy - 1), 1)


# ── rows ────────────────────────────────────────────────────────────────────

def row_events(i):
    """Per-row tile registers plus the right-column label lines."""
    lo, hi = phase_bounds(i)
    p0, p1 = PILLAR_SPANS[i]
    weather = [None] * TILES
    play = [None] * TILES
    wlines, glines = [], []

    def tiles_over(a, b):
        for j in range(TILES):
            t0 = lo + (hi - lo) * j / TILES
            t1 = lo + (hi - lo) * (j + 1) / TILES
            if t1 > a and t0 < b:
                yield j

    for name, z0, z1, key in WEATHER_ZONES:
        a, b = max(lo, z0), min(hi, z1)
        if b <= a:
            continue
        for j in tiles_over(a, b):
            weather[j] = key
        wlines.append("%s · %d-%d" % (name, round(phase_to_pillar(a)),
                                      round(phase_to_pillar(b))))

    rushes = [p for p in range(RUSH_EVERY, int(TOTAL_PILLARS) + 1, RUSH_EVERY)
              if p0 <= p < p1]
    for p in rushes:
        play[min(TILES - 1, int((p - p0) / (p1 - p0) * TILES))] = "rush"

    a, b = max(lo, CLOWN_ZONE[0]), min(hi, CLOWN_ZONE[1])
    if b > a:
        for j in tiles_over(a, b):
            play[j] = "clown"
        glines.append("CLOWN · %d-%d" % (round(phase_to_pillar(a)),
                                         round(phase_to_pillar(b))))

    fin0 = TOTAL_PILLARS - FINALE_PILLARS
    if p1 > fin0:
        for j in range(TILES):
            if p0 + (p1 - p0) * (j + 1) / TILES > fin0:
                play[j] = "finale"
        glines.append("FINALE · %d-%d" % (round(fin0) + 1, int(TOTAL_PILLARS)))

    if rushes:
        glines.append("RUSH ×%d" % len(rushes))
    return weather, play, wlines, glines


def draw_row(surf, i):
    top = ROW_TOPS[i]
    lo, hi = phase_bounds(i)
    p0, p1 = PILLAR_SPANS[i]
    name = PHASE_BOUNDARIES[i][1]
    anchor = palette_for_phase(lo)

    death_tile = -1
    if p0 <= PILLARS_CLEARED < p1:
        death_tile = min(TILES - 1,
                         int((PILLARS_CLEARED - p0) / (p1 - p0) * TILES))
    row_flown = p1 <= PILLARS_CLEARED
    state = "cleared" if row_flown else ("grounded" if death_tile >= 0 else "pending")
    dim = 255 if state != "pending" else 150

    # Left gutter, all three elements flush left. The status lamp sits at the
    # far end of the pillar-range line rather than beside the name: the name
    # line needs the whole 60px gutter or "GOLDEN HOUR" has to drop a type size
    # and break the rhythm the other six rows hold.
    text(surf, name, (8, top + 17), 8, UI_CREAM, "midleft", max_w=60, alpha=dim)
    text(surf, "P.%d-%d" % (round(p0), round(p1)), (8, top + 29), 7,
         _GOLD_MUTED, "midleft", max_w=50, alpha=dim)
    led(surf, 63, top + 29, state)

    # The chip holds full chroma on every row: it is the only place the seven
    # hues of the day are all readable on a short run. It samples the phase's
    # OWN keyframe rather than the row midpoint — a midpoint sample is already
    # half cross-faded into the next phase, which collapsed DUSK and NIGHT into
    # the same muddy violet.
    chip = pygame.Surface((58, 4))
    vgrad(chip, (0, 0, 58, 4), chip_ramp(anchor))
    surf.blit(chip, (8, top + 38))

    ty = top + TILE_TOP_OFF
    pygame.draw.rect(surf, HOUSING, (FIELD_X - 3, ty - 3, FIELD_W + 6, TILE_H + 6),
                     border_radius=2)

    weather, play, wlines, glines = row_events(i)
    for j in range(TILES):
        if j == death_tile:
            continue
        x = FIELD_X + int(round(j * PITCH))
        flown = (p0 + (p1 - p0) * (j + 0.5) / TILES) <= PILLARS_CLEARED
        pal = palette_for_phase(lo + (hi - lo) * (j + 0.5) / TILES)
        draw_tile(surf, x, ty, pal, flown, weather[j], play[j])

    if death_tile >= 0:
        dx = FIELD_X + int(round(death_tile * PITCH))
        death_glow(surf, dx, ty)
        surf.blit(build_death_tile(), (dx, ty))

    # ── right label column ──
    if state == "grounded":
        wash = pygame.Surface((LAB_X1 - LAB_X0 + 6, 44), pygame.SRCALPHA)
        wash.fill((150, 30, 26, 34))
        surf.blit(wash, (LAB_X0 - 3, top + 8))
        plate_w = LAB_X1 - LAB_X0
        pygame.draw.rect(surf, (30, 6, 8), (LAB_X0, top + 11, plate_w, 15),
                         border_radius=2)
        vg = pygame.Surface((plate_w - 2, 13))
        vgrad(vg, (0, 0, plate_w - 2, 13),
              [(0.0, (235, 70, 60)), (1.0, (170, 24, 24))])
        surf.blit(vg, (LAB_X0 + 1, top + 12))
        text(surf, "GROUNDED · %d" % PILLARS_CLEARED,
             (LAB_X0 + plate_w // 2, top + 18), 9, (18, 4, 6), "center",
             max_w=plate_w - 6)
        lines = ([(t, UI_CREAM) for t in wlines] +
                 [(t, _GOLD_MUTED) for t in glines])[:2]
        ys = [top + 34, top + 45]
    else:
        lines = [(t, UI_CREAM) for t in wlines] + [(t, _GOLD_MUTED) for t in glines]
        if not wlines:
            lines.insert(0, ("—", (128, 132, 152)))
        lines = lines[:3]
        n = len(lines)
        ys = [top + 29 + (k - (n - 1) / 2) * 12 for k in range(n)]
    for (txt, col), yy in zip(lines, ys):
        text(surf, txt, (LAB_X0 + 1, yy), 7, col, "midleft",
             max_w=LAB_X1 - LAB_X0, alpha=255 if txt == "—" else dim)


# ── chrome ──────────────────────────────────────────────────────────────────

def status_plate(surf, x, y, w, h, label, size=9):
    pygame.draw.rect(surf, (30, 6, 8), (x, y, w, h), border_radius=2)
    vg = pygame.Surface((w - 2, h - 2))
    vgrad(vg, (0, 0, w - 2, h - 2), [(0.0, (235, 70, 60)), (1.0, (170, 24, 24))])
    surf.blit(vg, (x + 1, y + 1))
    text(surf, label, (x + w // 2, y + h // 2), size, (18, 4, 6), "center",
         max_w=w - 6)


def draw_header(surf):
    text_shadowed(surf, "FLIGHT LOG", (20, 22), 17, _GOLD_BRIGHT, "topleft")
    text(surf, "SKYBIT DEPARTURES", (21, 47), 7, _GOLD_MUTED, "midleft")

    status_plate(surf, 340 - 74, 22, 74, 16, "GROUNDED")
    text(surf, "DAY %d · RUN 0m %02ds" % (DAY_N, RUN_SECONDS), (340, 47), 7,
         _GOLD_MUTED, "midright")

    text(surf, "PHASE", (9, 87), 7, _GOLD_MUTED, "midleft")
    text(surf, "FLIGHT PATH  ·  24 SEGMENTS", (FIELD_X + FIELD_W // 2, 87), 7,
         _GOLD_MUTED, "center")
    text(surf, "EVENTS", (LAB_X1, 87), 7, _GOLD_MUTED, "midright")
    r = pygame.Surface((344, 1), pygame.SRCALPHA)
    r.fill((*_GOLD_MUTED, 90))
    surf.blit(r, (8, 93))


def draw_footer(surf):
    text(surf, "SCORE", (20, 516), 8, _GOLD_MUTED, "topleft")
    text_shadowed(surf, str(SCORE), (20, 524), 40, _GOLD_BRIGHT, "topleft")

    items = ["0m %02ds" % RUN_SECONDS, "%d COINS" % COINS,
             "PILLAR %d" % PILLARS_CLEARED]
    x0, x1 = 100, 348
    cw = (x1 - x0) / 3
    for k, it in enumerate(items):
        text(surf, it, (int(x0 + cw * (k + 0.5)), 556), 11, UI_CREAM, "center")
        if k:
            d = pygame.Surface((1, 18), pygame.SRCALPHA)
            d.fill((*_GOLD_MUTED, 70))
            surf.blit(d, (int(x0 + cw * k), 547))

    text(surf, "BOARD %d OF 7  ·  DAY %d 75%%" % (DAY_N, DAY_N), (180, 582), 9,
         _GOLD_MUTED, "center")

    bw, bh = 100, 26
    bx, by = 180 - bw // 2, 612 - bh // 2
    pygame.draw.rect(surf, (10, 10, 20), (bx, by, bw, bh), border_radius=13)
    pygame.draw.rect(surf, _GOLD_MUTED, (bx, by, bw, bh), width=1, border_radius=13)
    text(surf, "BACK", (180, 612), 12, _GOLD_BRIGHT, "center")


def render_board():
    surf = pygame.Surface((W, H))
    vgrad(surf, (0, 0, W, H), [(0.0, NEAR_BLACK), (1.0, BOARD_BOT)])
    draw_header(surf)
    for y in ROW_TOPS + [ROW_TOPS[-1] + ROW_H]:
        pygame.draw.line(surf, SEP, (10, y), (349, y))
    for i in range(7):
        draw_row(surf, i)
    sep = pygame.Surface((332, 1), pygame.SRCALPHA)
    sep.fill((*_GOLD_MUTED, 60))
    surf.blit(sep, (14, 506))
    draw_footer(surf)
    pygame.draw.rect(surf, _GOLD_MUTED, (8, 8, 344, 624), width=2)
    return surf


# ── legend panel (review sheet only) ────────────────────────────────────────

def _sample_flap(kind):
    if kind == "death":
        return build_death_tile()
    host = pygame.Surface((TILE_W, TILE_H), pygame.SRCALPHA)
    draw_tile(host, 0, 0, palette_for_phase(0.44), kind == "flown", "rain", "rush")
    return host


def _glyph_chip(fn, col):
    """The glyph alone on a dark chip — a board flap is only 7px wide, so a
    scaled-up flap in the key would be a tall stripe with a speck in it."""
    c = pygame.Surface((11, 11))
    c.fill((22, 24, 36))
    fn(c, 5, 5, col)
    out = pygame.transform.scale(c, (22, 22))
    pygame.draw.rect(out, (58, 60, 78), (0, 0, 22, 22), width=1)
    return out


def render_legend(w, h):
    s = pygame.Surface((w, h))
    vgrad(s, (0, 0, w, h), [(0.0, (12, 12, 24)), (1.0, (18, 20, 26))])
    pygame.draw.rect(s, _GOLD_MUTED, (0, 0, w, h), width=1)
    text(s, "HOW TO READ THE BOARD", (14, 18), 12, _GOLD_BRIGHT, "midleft")

    ay0 = 44
    for k, (kind, label) in enumerate((("flown", "FLOWN"),
                                       ("slate", "NOT FLOWN"),
                                       ("death", "GROUNDED"))):
        fx = 22 + k * 58
        s.blit(pygame.transform.scale(_sample_flap(kind),
                                      (TILE_W * 4, TILE_H * 4)), (fx, ay0))
        text(s, label, (fx + TILE_W * 2, ay0 + TILE_H * 4 + 10), 8, UI_CREAM,
             "center")
    rail = 22 + 2 * 58 + TILE_W * 4
    lx = rail + 16
    for yy, head, sub, col in ((ay0 + 34, "UPPER HALF", "WEATHER", UI_CREAM),
                               (ay0 + 122, "LOWER HALF", "GAMEPLAY", _GOLD_BRIGHT)):
        ln = pygame.Surface((13, 1), pygame.SRCALPHA)
        ln.fill((*_GOLD_MUTED, 110))
        s.blit(ln, (rail + 2, yy))
        text(s, head, (lx, yy - 6), 10, col, "midleft")
        text(s, sub, (lx, yy + 6), 9, _GOLD_MUTED, "midleft")
    hy = ay0 + TILE_H * 2
    ln = pygame.Surface((13, 1), pygame.SRCALPHA)
    ln.fill((*_GOLD_MUTED, 80))
    s.blit(ln, (rail + 2, hy))
    text(s, "HINGE", (lx, hy), 8, _GOLD_MUTED, "midleft")

    gy = ay0 + TILE_H * 4 + 32
    text(s, "WEATHER · ABOVE HINGE", (16, gy), 9, _GOLD_MUTED, "midleft")
    text(s, "GAMEPLAY · BELOW HINGE", (w // 2 + 8, gy), 9, _GOLD_MUTED, "midleft")
    groups = ([("RAIN", _g_rain, RAIN_C), ("SNOW", _g_snow, SNOW_C),
               ("THERMAL", _g_thermal, THERM_C)],
              [("CLOWN", _g_clown, CLOWN_C), ("COIN RUSH", _g_rush, RUSH_C),
               ("FINALE", _g_finale, RUSH_C)])
    for col_i, group in enumerate(groups):
        cx = 16 if col_i == 0 else w // 2 + 8
        for k, (label, fn, colr) in enumerate(group):
            yy = gy + 14 + k * 30
            s.blit(_glyph_chip(fn, colr), (cx, yy))
            text(s, label, (cx + 30, yy + 11), 10, UI_CREAM, "midleft")

    ly = gy + 14 + 3 * 30 + 18
    text(s, "ROW STATUS LAMP", (16, ly), 9, _GOLD_MUTED, "midleft")
    for k, (label, st) in enumerate((("CLEARED", "cleared"),
                                     ("GROUNDED", "grounded"),
                                     ("NOT FLOWN", "pending"))):
        cx = 26 + k * 112
        led(s, cx, ly + 26, st)
        text(s, label, (cx + 11, ly + 26), 9, UI_CREAM, "midleft")
    return s


# ── review sheet ────────────────────────────────────────────────────────────
BG = (8, 8, 18)
INK = (232, 226, 208)
INK_DIM = (150, 148, 174)


def to_pil(surf):
    return Image.frombytes("RGB", surf.get_size(),
                           pygame.image.tostring(surf, "RGB"))


board = render_board()
pil = to_pil(board)

MARGIN, HEAD, GAP = 26, 76, 30
COL_A_W = W * 2
COL_B_W = W
COL_C_W = W * 2
SHEET_W = MARGIN * 2 + COL_A_W + GAP + COL_B_W + GAP + COL_C_W
SHEET_H = HEAD + H * 2 + GAP

sheet = Image.new("RGB", (SHEET_W, SHEET_H), BG)
d = ImageDraw.Draw(sheet)
d.text((MARGIN, 20), "departure_board  ·  flight_log  ·  round_1", fill=INK)
d.text((MARGIN, 42),
       "split-flap departures board · 7 rows = the 7 day-cycle phases · 24 flaps per "
       "row · weather above the hinge, gameplay below · mock run: 25 pillars, score 25, 47s",
       fill=INK_DIM)

ax, ay = MARGIN, HEAD
sheet.paste(pil.resize((COL_A_W, H * 2), Image.NEAREST), (ax, ay))
d.rectangle([ax - 1, ay - 1, ax + COL_A_W, ay + H * 2], outline=(52, 52, 70))
d.text((ax, ay - 16), "FULL BOARD · 2×", fill=INK_DIM)

bx = MARGIN + COL_A_W + GAP
sheet.paste(pil, (bx, ay))
d.rectangle([bx - 1, ay - 1, bx + W, ay + H], outline=(52, 52, 70))
d.text((bx, ay - 16), "1× ACTUAL SIZE (360×640 canvas)", fill=INK_DIM)

LEG_H = 430
ly = ay + H + 60
sheet.paste(to_pil(render_legend(W, LEG_H)), (bx, ly))
d.text((bx, ly - 16), "KEY", fill=INK_DIM)

cx = bx + W + GAP
# Terminus crop: the death flap and its neighbours at 6× nearest, so the
# engraved chevron and the red bleed can be judged pixel by pixel.
_DEATH_TILE_X = FIELD_X + int(round(17 * PITCH))
tx0, ty0, tw, th = _DEATH_TILE_X + TILE_W // 2 - 30, 95, 60, 60
sheet.paste(pil.crop((tx0, ty0, tx0 + tw, ty0 + th)).resize((tw * 6, th * 6),
                                                            Image.NEAREST), (cx, ay))
d.rectangle([cx - 1, ay - 1, cx + tw * 6, ay + th * 6], outline=(52, 52, 70))
d.text((cx, ay - 16), "TERMINUS FLAP · 6×", fill=INK_DIM)

ry = ay + th * 6 + 46
sheet.paste(pil.crop((0, 92, W, 216)).resize((W * 2, 124 * 2), Image.NEAREST),
            (cx, ry))
d.rectangle([cx - 1, ry - 1, cx + W * 2, ry + 124 * 2], outline=(52, 52, 70))
d.text((cx, ry - 16), "ROW ANATOMY · 2× — DAY (flown, terminus) over GOLDEN HOUR "
                      "(unflown)", fill=INK_DIM)

fy = ry + 124 * 2 + 46
sheet.paste(pil.crop((0, 500, W, 640)).resize((W * 2, 140 * 2), Image.NEAREST),
            (cx, fy))
d.rectangle([cx - 1, fy - 1, cx + W * 2, fy + 140 * 2], outline=(52, 52, 70))
d.text((cx, fy - 16), "FOOTER · 2×", fill=INK_DIM)

OUTDIR = pathlib.Path(os.environ.get(
    "DEPARTURE_OUTDIR", "/home/user/skybit/docs/flight_log/departure_board"))
OUTDIR.mkdir(parents=True, exist_ok=True)
OUT = OUTDIR / "round_1.png"
sheet.save(OUT)
print("saved %dx%d -> %s" % (sheet.size[0], sheet.size[1], OUT))
