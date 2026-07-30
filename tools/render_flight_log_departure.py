#!/usr/bin/env python3
"""departure_board · flight_log · round_2

The Flight Log read as a split-flap airport departures board. Seven rows =
the seven time-of-day phases of Skybit's day cycle; each row is 24 flap tiles
across its pillar span, so a whole run reads as one board of sky-coloured
flaps. Every tile carries TWO registers split by its hinge — weather forecast
above, gameplay event below.

Layout hierarchy revised for median short runs: the phase where you died
dominates at ~108 px with progress bar and macaw tumble silhouette; all
unseen phases collapse into a single 90 px "STILL AHEAD" teaser rather than
six identical empty cards.
"""
import os
import sys
import pathlib
import math

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

# ── palette ─────────────────────────────────────────────────────────────────
_GOLD_BRIGHT  = (240, 192, 64)
_GOLD_MUTED   = (216, 184, 85)
_GOLD_STATUS  = (200, 160, 40)     # FLOWN badge gradient top
_SCARLET      = (210, 36, 36)      # ENDED HERE mid
_SCARLET_HI   = (255, 72, 62)
_SCARLET_LO   = (155, 18, 18)
_SLATE_DIM    = (100, 108, 132)    # UNSEEN labels

BOARD_BOT = (18, 20, 26)
SEP       = (30, 32, 38)
HOUSING   = (9,  9, 16)

RAIN_C  = (120, 185, 255)
SNOW_C  = (228, 238, 252)
THERM_C = (255, 194, 96)
CLOWN_C = (255, 130, 195)
RUSH_C  = (255, 214, 90)
FINAL_C = (255, 224, 100)

SLATE   = (40, 44, 60)

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
SCORE           = 25
DAY_N           = 1
RUN_SECONDS     = 47
COINS           = 0

# Pillar span of each named phase — carried as an explicit knot table because
# pillar accrual is not linear with phase (scroll speed ramps through
# the early run), so derivation from phase fractions would be wrong.
PILLAR_SPANS = [
    (0.0,   33.7),  (33.7,  57.7),  (57.7,  85.1),  (85.1, 109.1),
    (109.1, 136.5), (136.5, 157.1), (157.1, 175.0),
]
TOTAL_PILLARS = 175.0

WEATHER_ZONES = [
    ("THERMAL", 0.106, 0.206, "thermal"),
    ("RAIN",    0.430, 0.690, "rain"),
    ("SNOW",    0.780, 1.000, "snow"),
]
CLOWN_ZONE    = (0.403, 0.539)
RUSH_EVERY    = 15
FINALE_PILLARS = 3

# ── layout ──────────────────────────────────────────────────────────────────
BAND_W    = 20           # left colour band width
CARD_L    = 8            # card left inside gold border
CARD_R    = 352          # card right inside gold border
CARD_W    = CARD_R - CARD_L

DEATH_H   = 108          # dominant card height
PASSED_H  = 54           # FLOWN card height
AHEAD_H   = 90           # STILL AHEAD teaser height

TILES      = 24
FIELD_X    = CARD_L + BAND_W + 4    # flap field left
FIELD_W    = 196
TILE_W     = 7
PITCH      = FIELD_W / TILES
TILE_H     = 36          # slightly taller than round_1 to breathe inside cards
TILE_YOFF  = 8           # gap above tile row inside card


# ── small drawing helpers ───────────────────────────────────────────────────

def vgrad(surf, rect, stops):
    """Vertical multi-stop gradient. stops = [(t, colour), ...] ascending."""
    x, y, w, h = rect
    for i in range(h):
        t = i / max(1, h - 1)
        for k in range(len(stops) - 1):
            t0, c0 = stops[k]
            t1, c1 = stops[k + 1]
            if t0 <= t <= t1:
                span = (t1 - t0) or 1.0
                pygame.draw.line(surf, lerp_color(c0, c1, (t - t0) / span),
                                 (x, y + i), (x + w - 1, y + i))
                break


def text(surf, txt, pos, size, colour, anchor="topleft", max_w=None, alpha=255):
    """Anchored text; auto-shrinks to fit max_w but never below 10 px.
    Ten-pixel minimum keeps every label legible on 360 px physical canvas."""
    s = max(10, size)
    f = font(s)
    img = f.render(txt, True, colour)
    while max_w and img.get_width() > max_w and s > 10:
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


def round_mask(surf, radius):
    m = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.rect(m, (255, 255, 255, 255), m.get_rect(), border_radius=radius)
    surf.blit(m, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)


# ── procedural vector event icons ─────────────────────────────────────────
# All six icons are drawn from pygame primitives — no SysFont, no emoji.
# Each is centred at (cx, cy) and fits an 8×8 bounding box for tile glyphs
# or a 12×12 box for label icons.

def _g_thermal(surf, cx, cy, c):
    """Upward triangle (geyser plume) + three shimmer dots below."""
    pygame.draw.polygon(surf, c, [(cx, cy - 4), (cx - 3, cy + 1), (cx + 3, cy + 1)])
    for dx in (-2, 0, 2):
        pygame.draw.rect(surf, c, (cx + dx - 1, cy + 3, 2, 2))


def _g_rain(surf, cx, cy, c):
    """Three slanted rain streaks."""
    pygame.draw.line(surf, c, (cx - 1, cy - 3), (cx - 1, cy - 1))
    pygame.draw.line(surf, c, (cx + 1, cy - 1), (cx + 1, cy + 1))
    pygame.draw.line(surf, c, (cx - 1, cy + 2), (cx - 1, cy + 3))


def _g_snow(surf, cx, cy, c):
    """Six-spoke asterisk (three crossing lines at 60° intervals)."""
    pygame.draw.line(surf, c, (cx, cy - 3), (cx, cy + 3))
    pygame.draw.line(surf, c, (cx - 2, cy - 2), (cx + 2, cy + 2))
    pygame.draw.line(surf, c, (cx - 2, cy + 2), (cx + 2, cy - 2))


def _g_clown(surf, cx, cy, c):
    """Diamond shape."""
    pygame.draw.polygon(surf, c,
                        [(cx, cy - 4), (cx + 3, cy), (cx, cy + 4), (cx - 3, cy)])


def _g_rush(surf, cx, cy, c):
    """Coin ring — open circle implies collectible value."""
    pygame.draw.circle(surf, c, (cx, cy), 3, 1)


def _g_finale(surf, cx, cy, c):
    """Five-point star polygon."""
    pts = []
    for i in range(10):
        a = math.pi * i / 5 - math.pi / 2
        r = 5 if i % 2 == 0 else 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    pygame.draw.polygon(surf, c, pts)


WEATHER_GLYPH = {
    "rain":    (_g_rain,    RAIN_C),
    "snow":    (_g_snow,    SNOW_C),
    "thermal": (_g_thermal, THERM_C),
}
PLAY_GLYPH = {
    "clown":  (_g_clown,  CLOWN_C),
    "rush":   (_g_rush,   RUSH_C),
    "finale": (_g_finale, FINAL_C),
}


def _stamp(surf, fn, cx, cy, colour):
    """Near-black under-copy then bright face; flap sky gradient eats bare marks."""
    fn(surf, cx, cy + 1, (0, 0, 0, 150))
    fn(surf, cx, cy, colour)


def draw_icon_label(surf, cx, cy, kind, alpha=255):
    """Event icon at 12×12 scale for card labels; shadow + face on SRCALPHA temp."""
    rec = WEATHER_GLYPH.get(kind) or PLAY_GLYPH.get(kind)
    if not rec:
        return
    fn, col = rec
    tmp = pygame.Surface((16, 16), pygame.SRCALPHA)
    fn(tmp, 8, 9, (0, 0, 0, 110))   # shadow
    fn(tmp, 8, 8, col)               # face
    if alpha < 255:
        tmp.set_alpha(alpha)
    surf.blit(tmp, (cx - 8, cy - 8))


# ── flap tile ────────────────────────────────────────────────────────────────

def lift(c, amount=12):
    """Flaps are lit by the board's back-light so the whole ramp nudges up;
    without it the NIGHT row (5,8,30 sky_top) hides behind the housing black."""
    return tuple(min(255, v + amount) for v in c)


_CHIP_FLOOR = 165


def chip_ramp(pal):
    """Full-chroma phase gradient scaled so even dark phases clear the board
    near-black. Uniform scaling keeps hue and saturation exact."""
    stops = [pal["sky_top"], pal["sky_mid"], pal["sky_bot"]]
    peak = max(max(c) for c in stops)
    k = _CHIP_FLOOR / peak if 0 < peak < _CHIP_FLOOR else 1.0
    return [(t, tuple(min(255, int(v * k)) for v in c))
            for t, c in zip((0.0, 0.5, 1.0), stops)]


def sky_stops(pal):
    return [(0.0, lift(pal["sky_top"])), (0.5, lift(pal["sky_mid"])),
            (1.0, lift(pal["sky_bot"]))]


def card_bg_color(pal, mix=0.07):
    """The phase's sky_mid hue bled into board-black at 7%; card backgrounds are
    distinct from the board while staying dark enough for text contrast."""
    return lerp_color(BOARD_BOT, pal["sky_mid"], mix)


def flap_edges(t, flown):
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
    vgrad(t, (0, 0, TILE_W, half), [(0.0, _SCARLET_HI), (1.0, _SCARLET)])
    vgrad(t, (0, half, TILE_W, TILE_H - half), [(0.0, _SCARLET), (1.0, _SCARLET_LO)])
    pygame.draw.line(t, NEAR_BLACK, (0, half - 1), (TILE_W - 1, half - 1))
    cx, cy = TILE_W // 2, half + 1
    # Engraved ▼: pale under-stamp gives the black chevron its cut edge.
    pygame.draw.polygon(t, (255, 235, 232),
                        [(cx - 3, cy - 3), (cx + 3, cy - 3), (cx, cy + 2)])
    pygame.draw.polygon(t, (10, 6, 10),
                        [(cx - 2, cy - 3), (cx + 2, cy - 3), (cx, cy + 1)])
    flap_edges(t, True)
    round_mask(t, 1)
    return t


def death_glow(surf, x, y):
    """Value spread: the terminus bleeds red into its neighbours so the eye
    lands on it before reading any glyph. Composited, not added — additive
    bleed blows pale DAY flaps out to white."""
    pad = 6
    g = pygame.Surface((TILE_W + pad * 2, TILE_H + pad * 2), pygame.SRCALPHA)
    for r in range(pad, 0, -1):
        a = int(52 * (1 - (r - 1) / pad) ** 1.4)
        pygame.draw.rect(g, (215, 48, 40, a),
                         (pad - r, pad - r, TILE_W + r * 2, TILE_H + r * 2),
                         border_radius=r + 1)
    surf.blit(g, (x - pad, y - pad))


# ── LED status lamp ──────────────────────────────────────────────────────────

def led(surf, cx, cy, state):
    if state == "ended":
        core, halo = (255, 90, 80), (230, 50, 40)
    elif state == "flown":
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


# ── macaw tumble silhouette ──────────────────────────────────────────────────

def draw_macaw_tumble(surf, cx, cy, color):
    """Tumbling parrot silhouette: body angled, wings spread, tail fanned.
    Draw onto an SRCALPHA surface so the caller controls opacity."""
    # Body: angled teardrop polygon (~45° tilt)
    body = [
        (cx + 10, cy - 5), (cx + 4,  cy - 12),
        (cx - 6,  cy - 10), (cx - 12, cy -  2),
        (cx - 8,  cy + 10), (cx + 2,  cy +  9),
    ]
    pygame.draw.polygon(surf, color, body)
    # Head at upper-right of body
    pygame.draw.circle(surf, color, (cx + 13, cy - 10), 8)
    # Beak: small wedge off the head
    pygame.draw.polygon(surf, color,
                        [(cx + 20, cy - 12), (cx + 26, cy - 8), (cx + 20, cy - 5)])
    # Upper wing sweeping up-left
    pygame.draw.polygon(surf, color,
                        [(cx + 2, cy - 5), (cx - 8, cy - 18),
                         (cx - 14, cy - 12), (cx - 5, cy - 6)])
    # Lower wing sweeping down-left
    pygame.draw.polygon(surf, color,
                        [(cx, cy + 4), (cx - 6, cy + 18),
                         (cx - 12, cy + 12), (cx - 5, cy + 5)])
    # Tail feathers at lower-left
    pygame.draw.polygon(surf, color,
                        [(cx - 10, cy + 6), (cx - 20, cy + 14),
                         (cx - 18, cy + 4), (cx - 10, cy)])


# ── event data extraction ────────────────────────────────────────────────────

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


def row_events(i):
    """Per-row tile registers and structured event list [(kind, p0, p1), ...]."""
    lo, hi = phase_bounds(i)
    p0, p1 = PILLAR_SPANS[i]
    weather = [None] * TILES
    play    = [None] * TILES
    wevents, gevents = [], []

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
        wevents.append((key, round(phase_to_pillar(a)),
                        round(phase_to_pillar(b))))

    rushes = [p for p in range(RUSH_EVERY, int(TOTAL_PILLARS) + 1, RUSH_EVERY)
              if p0 <= p < p1]
    for p in rushes:
        play[min(TILES - 1, int((p - p0) / (p1 - p0) * TILES))] = "rush"

    a, b = max(lo, CLOWN_ZONE[0]), min(hi, CLOWN_ZONE[1])
    if b > a:
        for j in tiles_over(a, b):
            play[j] = "clown"
        gevents.append(("clown", round(phase_to_pillar(a)),
                        round(phase_to_pillar(b))))

    fin0 = TOTAL_PILLARS - FINALE_PILLARS
    if p1 > fin0:
        for j in range(TILES):
            if p0 + (p1 - p0) * (j + 1) / TILES > fin0:
                play[j] = "finale"
        gevents.append(("finale", round(fin0) + 1, int(TOTAL_PILLARS)))

    if rushes:
        gevents.append(("rush", rushes[0], rushes[-1]))

    return weather, play, wevents, gevents


# ── status badge ─────────────────────────────────────────────────────────────

def draw_status_badge(surf, x, y, w, h, label, is_ended=False):
    """Scarlet for ENDED HERE; gold for FLOWN. Both use gradient fill + dark text."""
    if is_ended:
        border_col = (40, 8, 10)
        grad_top, grad_bot = _SCARLET_HI, _SCARLET_LO
        ink = (250, 215, 205)
    else:
        border_col = (28, 18, 4)
        grad_top, grad_bot = (255, 205, 80), (175, 125, 24)
        ink = (28, 16, 4)
    pygame.draw.rect(surf, border_col, (x, y, w, h), border_radius=2)
    vg = pygame.Surface((w - 2, h - 2))
    vgrad(vg, (0, 0, w - 2, h - 2),
          [(0.0, grad_top), (1.0, grad_bot)])
    surf.blit(vg, (x + 1, y + 1))
    text(surf, label, (x + w // 2, y + h // 2), 10, ink, "center", max_w=w - 4)


# ── progress bar ─────────────────────────────────────────────────────────────

def draw_progress_bar(surf, x, y, w, h, frac, fill_col, track_col=(28, 30, 42)):
    """Horizontal pill-style bar; frac in [0, 1]. Gloss sliver on top half."""
    pygame.draw.rect(surf, track_col, (x, y, w, h), border_radius=h // 2)
    fw = max(h, int(w * max(0.0, min(1.0, frac))))
    if fw > 0:
        pygame.draw.rect(surf, fill_col, (x, y, fw, h), border_radius=h // 2)
        gl = pygame.Surface((fw, max(1, h // 2)), pygame.SRCALPHA)
        gl.fill((255, 255, 255, 28))
        surf.blit(gl, (x, y))


# ── left colour band (20 px) ─────────────────────────────────────────────────

def draw_left_band(surf, top, h, pal, scarlet=False):
    """20 px full-height band at card left edge; identifies the phase by hue.
    Drawn as a flat rect so the right edge is square (the card's own border
    radius handles the top-left and bottom-left corners of the whole card)."""
    band = pygame.Surface((BAND_W, h))
    if scarlet:
        vgrad(band, (0, 0, BAND_W, h),
              [(0.0, _SCARLET_HI), (0.45, _SCARLET), (1.0, _SCARLET_LO)])
    else:
        vgrad(band, (0, 0, BAND_W, h), chip_ramp(pal))
    surf.blit(band, (CARD_L, top))


# ── DEATH CARD ───────────────────────────────────────────────────────────────

def draw_death_card(surf, top, phase_idx):
    """108 px dominant card: big status + phase name, flap row, progress bar,
    2 event labels, macaw tumble silhouette at the right edge."""
    lo, hi = phase_bounds(phase_idx)
    p0, p1 = PILLAR_SPANS[phase_idx]
    name = PHASE_BOUNDARIES[phase_idx][1]
    pal  = palette_for_phase(lo)
    bg   = card_bg_color(pal, mix=0.06)

    # Card background — very dark phase tint, no border radius so the 20 px
    # left band sits flush against the left edge without a gap.
    pygame.draw.rect(surf, bg, (CARD_L, top, CARD_W, DEATH_H))

    # Left band: phase sky gradient (the phase colour still names the row even
    # though the card is in an "ended" state, so readers can locate the phase
    # in the day cycle at a glance without relying on the text label alone).
    draw_left_band(surf, top, DEATH_H, pal, scarlet=False)

    # Scarlet accent bar along the top of the band to signal termination.
    surf.fill(_SCARLET, (CARD_L, top, BAND_W, 3))

    # ── "ENDED HERE" badge ──
    badge_x = CARD_L + BAND_W + 6
    draw_status_badge(surf, badge_x, top + 7, 88, 16, "ENDED HERE", is_ended=True)
    led(surf, badge_x + 96, top + 15, "ended")

    # ── Phase name ──
    text_shadowed(surf, name, (badge_x + 110, top + 15), 15, UI_CREAM, "midleft",
                  sa=140)

    # ── Macaw tumble silhouette at the right edge ──
    # A warm-dark shape contrast-reads against the card's tinted navy BG;
    # alpha composite blends it into the top-right corner without hard edge.
    bird_surf = pygame.Surface((54, 48), pygame.SRCALPHA)
    draw_macaw_tumble(bird_surf, 27, 26, (190, 78, 68, 165))
    surf.blit(bird_surf, (CARD_R - 56, top + 2))

    # ── Progress bar ──
    frac = (PILLARS_CLEARED - p0) / (p1 - p0) if p1 > p0 else 0.0
    frac = max(0.0, min(1.0, frac))
    bar_x = badge_x
    bar_y = top + 30
    bar_w = CARD_W - BAND_W - 12
    draw_progress_bar(surf, bar_x, bar_y, bar_w, 7, frac, _SCARLET)
    pct_label = "PILLAR %d OF %d  ·  %d%% THROUGH %s" % (
        int(PILLARS_CLEARED), int(p1), int(frac * 100), name)
    text(surf, pct_label, (bar_x, bar_y + 10), 10, _GOLD_MUTED, "topleft",
         max_w=bar_w)

    # ── Flap row ──
    death_tile = min(TILES - 1,
                     int((PILLARS_CLEARED - p0) / (p1 - p0) * TILES))
    ty = top + TILE_YOFF + 48    # sit below the progress info
    pygame.draw.rect(surf, HOUSING,
                     (FIELD_X - 3, ty - 3, FIELD_W + 6, TILE_H + 6),
                     border_radius=2)
    weather, play, wevents, gevents = row_events(phase_idx)
    for j in range(TILES):
        if j == death_tile:
            continue
        x = FIELD_X + int(round(j * PITCH))
        flown = (p0 + (p1 - p0) * (j + 0.5) / TILES) <= PILLARS_CLEARED
        row_pal = palette_for_phase(lo + (hi - lo) * (j + 0.5) / TILES)
        draw_tile(surf, x, ty, row_pal, flown, weather[j], play[j])
    dx = FIELD_X + int(round(death_tile * PITCH))
    death_glow(surf, dx, ty)
    surf.blit(build_death_tile(), (dx, ty))

    # ── Event labels (right of flap field, 2 max) ──
    all_evs = wevents + [e for e in gevents if e[0] != "rush"]
    evs = all_evs[:2]
    lx  = FIELD_X + FIELD_W + 8
    lw  = CARD_R - lx - 4
    if evs:
        row_h = (TILE_H + 6) // max(1, len(evs))
        for k, (kind, ep0, ep1) in enumerate(evs):
            ey_center = ty - 3 + row_h * k + row_h // 2
            draw_icon_label(surf, lx + 8, ey_center, kind)
            col = (WEATHER_GLYPH.get(kind) or PLAY_GLYPH.get(kind, (None, RUSH_C)))[1]
            text(surf, "%d–%d" % (ep0, ep1),
                 (lx + 18, ey_center), 10, col, "midleft", max_w=lw - 18)
    else:
        text(surf, "—", (lx + lw // 2, ty + TILE_H // 2), 10, _SLATE_DIM, "center")


# ── FLOWN CARD ───────────────────────────────────────────────────────────────

def draw_flown_card(surf, top, phase_idx):
    """54 px compact card for phases already cleared."""
    lo, hi = phase_bounds(phase_idx)
    p0, p1 = PILLAR_SPANS[phase_idx]
    name = PHASE_BOUNDARIES[phase_idx][1]
    pal  = palette_for_phase(lo)
    bg   = card_bg_color(pal, mix=0.07)

    pygame.draw.rect(surf, bg, (CARD_L, top, CARD_W, PASSED_H))
    draw_left_band(surf, top, PASSED_H, pal, scarlet=False)

    badge_x = CARD_L + BAND_W + 6
    draw_status_badge(surf, badge_x, top + 5, 44, 14, "FLOWN", is_ended=False)
    led(surf, badge_x + 52, top + 12, "flown")
    text(surf, name, (badge_x + 66, top + 12), 12, UI_CREAM, "midleft", max_w=96)
    text(surf, "pillars %d–%d" % (round(p0), round(p1)),
         (badge_x + 66, top + 26), 10, _GOLD_MUTED, "midleft", max_w=96)

    # Flap row
    ty = top + 6
    pygame.draw.rect(surf, HOUSING,
                     (FIELD_X - 3, ty - 3, FIELD_W + 6, TILE_H + 6),
                     border_radius=2)
    weather, play, wevents, gevents = row_events(phase_idx)
    for j in range(TILES):
        x = FIELD_X + int(round(j * PITCH))
        row_pal = palette_for_phase(lo + (hi - lo) * (j + 0.5) / TILES)
        draw_tile(surf, x, ty, row_pal, True, weather[j], play[j])

    # Event labels
    all_evs = wevents + [e for e in gevents if e[0] != "rush"]
    evs = all_evs[:2]
    lx = FIELD_X + FIELD_W + 8
    lw = CARD_R - lx - 4
    if evs:
        row_h = (TILE_H + 6) // max(1, len(evs))
        for k, (kind, ep0, ep1) in enumerate(evs):
            ey_center = ty - 3 + row_h * k + row_h // 2
            draw_icon_label(surf, lx + 8, ey_center, kind, alpha=180)
            col = (WEATHER_GLYPH.get(kind) or PLAY_GLYPH.get(kind, (None, RUSH_C)))[1]
            text(surf, "%d–%d" % (ep0, ep1),
                 (lx + 18, ey_center), 10, col, "midleft", max_w=lw - 18, alpha=180)


# ── STILL AHEAD teaser ───────────────────────────────────────────────────────

def _desaturate(color, amount=0.55):
    """Mix toward grey; kills chroma while keeping brightness so unseen swatches
    are clearly distinguishable in hue but visually quieter than the flown row."""
    avg = sum(color) // 3
    return tuple(int(v + (avg - v) * amount) for v in color)


_PHASE_INITIALS = {
    "DAY": "D", "GOLDEN HOUR": "GH", "SUNSET": "SS",
    "DUSK": "DK", "NIGHT": "NT", "PREDAWN": "PD", "SUNRISE": "SR",
}

_JUICY_ORDER = ["clown", "rain", "snow", "finale", "thermal", "rush"]


def draw_still_ahead(surf, top, phase_indices):
    """90 px single teaser block collapsing all unseen phases into one row of
    sky swatches plus a preview of the 2-3 most distinctive upcoming events."""
    if not phase_indices:
        return

    blk_bg = (13, 14, 22)
    pygame.draw.rect(surf, blk_bg, (CARD_L, top, CARD_W, AHEAD_H))
    # Top hairline to separate from the card above
    pygame.draw.rect(surf, (38, 40, 56), (CARD_L, top, CARD_W, 1))

    # Left accent band: desaturated blend of all unseen phase colours
    band = pygame.Surface((BAND_W, AHEAD_H))
    band.fill((26, 28, 40))
    surf.blit(band, (CARD_L, top))

    hdr_x = CARD_L + BAND_W + 8
    text(surf, "STILL AHEAD  ·  %d PHASES UNSEEN" % len(phase_indices),
         (hdr_x, top + 8), 10, _SLATE_DIM, "midleft",
         max_w=CARD_W - BAND_W - 12)

    # ── sky swatch row ──
    n      = len(phase_indices)
    sw_area = CARD_W - BAND_W - 8        # total width for swatches
    sw_gap  = 3
    sw_w    = (sw_area - (n - 1) * sw_gap) // n
    sw_h    = 36
    sw_y    = top + 22

    for k, i in enumerate(phase_indices):
        lo   = phase_bounds(i)[0]
        name = PHASE_BOUNDARIES[i][1]
        pal  = palette_for_phase(lo)
        sx   = CARD_L + BAND_W + 4 + k * (sw_w + sw_gap)

        stops_des = [
            (0.0, _desaturate(lift(pal["sky_top"]))),
            (0.5, _desaturate(lift(pal["sky_mid"]))),
            (1.0, _desaturate(lift(pal["sky_bot"]))),
        ]
        sw_surf = pygame.Surface((sw_w, sw_h))
        vgrad(sw_surf, (0, 0, sw_w, sw_h), stops_des)
        # Dim overlay — unseen
        ov = pygame.Surface((sw_w, sw_h), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 55))
        sw_surf.blit(ov, (0, 0))
        surf.blit(sw_surf, (sx, sw_y))
        pygame.draw.rect(surf, (48, 50, 68), (sx, sw_y, sw_w, sw_h), width=1)

        initial = _PHASE_INITIALS.get(name, name[:2])
        text(surf, initial, (sx + sw_w // 2, sw_y + sw_h // 2), 10,
             (195, 200, 218), "center", max_w=sw_w - 2)

    # ── event preview strip ──
    # Collect unique non-rush events from unseen phases in "juicy" priority order.
    seen_kinds: set = set()
    preview: list = []
    for kind in _JUICY_ORDER:
        for i in phase_indices:
            _, _, wevents, gevents = row_events(i)
            all_e = wevents + gevents
            for ev_kind, ep0, ep1 in all_e:
                if ev_kind == kind and kind not in seen_kinds:
                    seen_kinds.add(kind)
                    preview.append((kind, ep0, ep1))
                    break
        if len(preview) >= 3:
            break

    ev_y  = sw_y + sw_h + 7
    ex    = hdr_x
    avail = CARD_R - hdr_x - 4
    for kind, ep0, ep1 in preview:
        col   = (WEATHER_GLYPH.get(kind) or PLAY_GLYPH.get(kind, (None, RUSH_C)))[1]
        col_d = tuple(int(v * 0.65) for v in col)   # dim version for unseen
        draw_icon_label(surf, ex + 7, ev_y + 6, kind, alpha=150)
        r = text(surf, kind.upper() + " %d–%d" % (ep0, ep1),
                 (ex + 17, ev_y + 1), 10, _SLATE_DIM, "topleft",
                 max_w=min(80, avail // len(preview) - 4), alpha=170)
        ex += r.width + 22
        if ex >= CARD_R - 30:
            break


# ── header ───────────────────────────────────────────────────────────────────

def draw_header(surf):
    text_shadowed(surf, "FLIGHT LOG", (20, 22), 17, _GOLD_BRIGHT, "topleft")
    text(surf, "SKYBIT DEPARTURES", (21, 47), 10, _GOLD_MUTED, "midleft")

    draw_status_badge(surf, CARD_R - 82, 22, 82, 16, "ENDED HERE", is_ended=True)
    text(surf, "DAY %d  ·  0m %02ds" % (DAY_N, RUN_SECONDS), (CARD_R, 47),
         10, _GOLD_MUTED, "midright")

    text(surf, "PHASE", (CARD_L + 2, 82), 10, _GOLD_MUTED, "midleft")
    text(surf, "FLIGHT PATH  ·  24 FLAPS", (FIELD_X + FIELD_W // 2, 82),
         10, _GOLD_MUTED, "center")
    text(surf, "EVENTS", (CARD_R - 2, 82), 10, _GOLD_MUTED, "midright")
    sep = pygame.Surface((CARD_W - 2, 1), pygame.SRCALPHA)
    sep.fill((*_GOLD_MUTED, 90))
    surf.blit(sep, (CARD_L + 1, 88))


# ── footer / stats panel ─────────────────────────────────────────────────────

def draw_footer(surf, y_start):
    """Stats panel fills from the last card to the board bottom. The back
    button anchors to the bottom of the board so it sits in the same physical
    thumb-zone regardless of run length; the score and stats distribute
    naturally in the space above it."""
    sep = pygame.Surface((CARD_W - 4, 1), pygame.SRCALPHA)
    sep.fill((*_GOLD_MUTED, 60))
    surf.blit(sep, (CARD_L + 2, y_start))

    # Back button always at the board bottom (anchored, thumb-reachable).
    bw, bh = 120, 30
    bx = 180 - bw // 2
    by = 618 - bh     # inside the 8 px bottom border with a 4 px gap
    pygame.draw.rect(surf, (10, 10, 20), (bx, by, bw, bh), border_radius=15)
    pygame.draw.rect(surf, _GOLD_MUTED, (bx, by, bw, bh), width=1,
                     border_radius=15)
    text(surf, "BACK", (180, by + bh // 2), 13, _GOLD_BRIGHT, "center")

    # Metadata line just above the back button
    meta_y = by - 20
    text(surf, "BOARD %d OF 7  ·  DAY %d" % (DAY_N, DAY_N), (180, meta_y),
         10, _GOLD_MUTED, "center")

    # Flight progress bar above the metadata
    prog_frac = PILLARS_CLEARED / TOTAL_PILLARS
    prog_y    = meta_y - 42
    text(surf, "FLIGHT PROGRESS  ·  %.0f%% OF FULL DAY 1 ROUTE" % (prog_frac * 100),
         (CARD_L + 4, prog_y), 10, _GOLD_MUTED, "topleft", max_w=CARD_W - 8)
    draw_progress_bar(surf, CARD_L + 4, prog_y + 14, CARD_W - 8, 7,
                      prog_frac, _GOLD_BRIGHT)

    # Score (big) + three stat columns in the remaining space below y_start
    y = y_start + 22

    text(surf, "SCORE", (CARD_L + 4, y), 10, _GOLD_MUTED, "topleft")
    text_shadowed(surf, str(SCORE), (CARD_L + 4, y + 14), 44, _GOLD_BRIGHT,
                  "topleft")

    pill_data = [
        ("TIME",   "0m %02ds" % RUN_SECONDS),
        ("COINS",  str(COINS)),
        ("PILLAR", str(PILLARS_CLEARED)),
    ]
    px0   = CARD_L + 4 + 74     # right of the large score number
    pill_w = (CARD_R - px0 - 4) // 3
    for k, (lbl, val) in enumerate(pill_data):
        px = px0 + k * pill_w
        text(surf, lbl, (px + pill_w // 2, y + 10), 10, _GOLD_MUTED,
             "center", max_w=pill_w)
        text(surf, val, (px + pill_w // 2, y + 26), 15, UI_CREAM,
             "center", max_w=pill_w)
        if k:
            div = pygame.Surface((1, 26), pygame.SRCALPHA)
            div.fill((*_GOLD_MUTED, 60))
            surf.blit(div, (px, y + 12))


# ── board render ─────────────────────────────────────────────────────────────

def render_board():
    surf = pygame.Surface((W, H))
    vgrad(surf, (0, 0, W, H), [(0.0, NEAR_BLACK), (1.0, BOARD_BOT)])

    draw_header(surf)

    # Classify phases: find the death phase; everything before it is FLOWN,
    # everything after (and not the death phase itself) is UNSEEN.
    death_phase  = -1
    flown_phases = []
    for i in range(7):
        p0, p1 = PILLAR_SPANS[i]
        if p1 <= PILLARS_CLEARED:
            flown_phases.append(i)
        elif p0 <= PILLARS_CLEARED < p1 and death_phase < 0:
            death_phase = i
    unseen_phases = [i for i in range(7)
                     if i not in flown_phases and i != death_phase]

    y = 90
    pygame.draw.line(surf, SEP, (CARD_L, y), (CARD_R, y))
    y += 2

    for i in flown_phases:
        draw_flown_card(surf, y, i)
        y += PASSED_H
        pygame.draw.line(surf, SEP, (CARD_L, y), (CARD_R, y))
        y += 2

    if death_phase >= 0:
        draw_death_card(surf, y, death_phase)
        y += DEATH_H
        pygame.draw.line(surf, SEP, (CARD_L, y), (CARD_R, y))
        y += 2

    if unseen_phases:
        draw_still_ahead(surf, y, unseen_phases)
        y += AHEAD_H
        pygame.draw.line(surf, SEP, (CARD_L, y), (CARD_R, y))
        y += 2

    draw_footer(surf, y)

    # Board chrome border
    pygame.draw.rect(surf, _GOLD_MUTED, (8, 8, 344, 624), width=2)
    return surf


# ── legend (key panel for review sheet) ─────────────────────────────────────

def _sample_flap(kind):
    if kind == "death":
        return build_death_tile()
    host = pygame.Surface((TILE_W, TILE_H), pygame.SRCALPHA)
    draw_tile(host, 0, 0, palette_for_phase(0.44), kind == "flown", "rain", "rush")
    return host


def _glyph_chip(fn, col):
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
                                       ("slate", "UNSEEN"),
                                       ("death", "ENDED HERE"))):
        fx = 22 + k * 58
        s.blit(pygame.transform.scale(_sample_flap(kind),
                                      (TILE_W * 4, TILE_H * 4)), (fx, ay0))
        text(s, label, (fx + TILE_W * 2, ay0 + TILE_H * 4 + 10), 10, UI_CREAM,
             "center")

    rail = 22 + 2 * 58 + TILE_W * 4
    lx = rail + 16
    for yy, head, sub, col in ((ay0 + 34, "UPPER HALF", "WEATHER", UI_CREAM),
                               (ay0 + 122, "LOWER HALF", "GAMEPLAY", _GOLD_BRIGHT)):
        ln = pygame.Surface((13, 1), pygame.SRCALPHA)
        ln.fill((*_GOLD_MUTED, 110))
        s.blit(ln, (rail + 2, yy))
        text(s, head, (lx, yy - 6), 10, col, "midleft")
        text(s, sub,  (lx, yy + 6), 10, _GOLD_MUTED, "midleft")
    hy = ay0 + TILE_H * 2
    ln = pygame.Surface((13, 1), pygame.SRCALPHA)
    ln.fill((*_GOLD_MUTED, 80))
    s.blit(ln, (rail + 2, hy))
    text(s, "HINGE", (lx, hy), 10, _GOLD_MUTED, "midleft")

    gy = ay0 + TILE_H * 4 + 32
    text(s, "WEATHER · ABOVE HINGE", (16, gy), 10, _GOLD_MUTED, "midleft")
    text(s, "GAMEPLAY · BELOW HINGE", (w // 2 + 8, gy), 10, _GOLD_MUTED,
         "midleft")
    groups = (
        [("RAIN",    _g_rain,    RAIN_C),
         ("SNOW",    _g_snow,    SNOW_C),
         ("THERMAL", _g_thermal, THERM_C)],
        [("CLOWN",     _g_clown,  CLOWN_C),
         ("COIN RUSH", _g_rush,   RUSH_C),
         ("FINALE",    _g_finale, FINAL_C)],
    )
    for col_i, group in enumerate(groups):
        cx = 16 if col_i == 0 else w // 2 + 8
        for k, (label, fn, colr) in enumerate(group):
            yy = gy + 16 + k * 30
            s.blit(_glyph_chip(fn, colr), (cx, yy))
            text(s, label, (cx + 30, yy + 11), 10, UI_CREAM, "midleft")

    ly = gy + 16 + 3 * 30 + 18
    text(s, "ROW STATUS LAMP", (16, ly), 10, _GOLD_MUTED, "midleft")
    for k, (label, st) in enumerate((("FLOWN", "flown"),
                                     ("ENDED HERE", "ended"),
                                     ("UNSEEN", "pending"))):
        cx = 26 + k * 112
        led(s, cx, ly + 26, st)
        text(s, label, (cx + 11, ly + 26), 10, UI_CREAM, "midleft")
    return s


# ── review sheet ─────────────────────────────────────────────────────────────
BG      = (8, 8, 18)
INK     = (232, 226, 208)
INK_DIM = (150, 148, 174)


def to_pil(surf):
    return Image.frombytes("RGB", surf.get_size(),
                           pygame.image.tostring(surf, "RGB"))


board = render_board()
pil   = to_pil(board)

MARGIN   = 26
HEAD     = 76
GAP      = 30
COL_A_W  = W * 2
COL_B_W  = W
COL_C_W  = W * 2
SHEET_W  = MARGIN * 2 + COL_A_W + GAP + COL_B_W + GAP + COL_C_W
SHEET_H  = HEAD + H * 2 + GAP

sheet = Image.new("RGB", (SHEET_W, SHEET_H), BG)
d     = ImageDraw.Draw(sheet)
d.text((MARGIN, 20), "departure_board  ·  flight_log  ·  round_2", fill=INK)
d.text((MARGIN, 42),
       "hierarchy inversion · 20 px band · phase tint BG · "
       "procedural icons · ENDED HERE / FLOWN / UNSEEN · macaw tumble · "
       "mock: 25 pillars, score 25, 47 s",
       fill=INK_DIM)

ax, ay = MARGIN, HEAD
sheet.paste(pil.resize((COL_A_W, H * 2), Image.NEAREST), (ax, ay))
d.rectangle([ax - 1, ay - 1, ax + COL_A_W, ay + H * 2], outline=(52, 52, 70))
d.text((ax, ay - 16), "FULL BOARD · 2×", fill=INK_DIM)

bx = MARGIN + COL_A_W + GAP
sheet.paste(pil, (bx, ay))
d.rectangle([bx - 1, ay - 1, bx + W, ay + H], outline=(52, 52, 70))
d.text((bx, ay - 16), "1× ACTUAL SIZE (360×640)", fill=INK_DIM)

LEG_H = 430
ly = ay + H + 60
sheet.paste(to_pil(render_legend(W, LEG_H)), (bx, ly))
d.text((bx, ly - 16), "KEY", fill=INK_DIM)

cx = bx + W + GAP

# Death card + still-ahead at 2× for close-up inspection
death_card_top = 90 + 2    # header rule y + gap
dc_crop_y = death_card_top
dc_crop_h = DEATH_H + 4 + AHEAD_H
dc_pil = pil.crop((0, dc_crop_y, W, dc_crop_y + dc_crop_h))
dc_2x = dc_pil.resize((W * 2, dc_crop_h * 2), Image.NEAREST)
sheet.paste(dc_2x, (cx, ay))
d.rectangle([cx - 1, ay - 1, cx + W * 2, ay + dc_crop_h * 2], outline=(52, 52, 70))
d.text((cx, ay - 16), "DEATH CARD + STILL AHEAD · 2×", fill=INK_DIM)

# Terminus flap close-up 6×
ry = ay + dc_crop_h * 2 + 46
death_tile_x = FIELD_X + int(round(
    min(TILES - 1, int((PILLARS_CLEARED - 0.0) / (33.7 - 0.0) * TILES)) * PITCH))
tx0 = death_tile_x + TILE_W // 2 - 28
ty0 = dc_crop_y + TILE_YOFF + 48
tw, th = 56, TILE_H + 12
tc = pil.crop((tx0, ty0, tx0 + tw, ty0 + th))
sheet.paste(tc.resize((tw * 6, th * 6), Image.NEAREST), (cx, ry))
d.rectangle([cx - 1, ry - 1, cx + tw * 6, ry + th * 6], outline=(52, 52, 70))
d.text((cx, ry - 16), "TERMINUS FLAP · 6×", fill=INK_DIM)

# Footer close-up at 2×
footer_crop_top = 90 + 2 + DEATH_H + 2 + AHEAD_H + 2
footer_crop_h = H - footer_crop_top
fy = ry + th * 6 + 46
fc = pil.crop((0, footer_crop_top, W, footer_crop_top + footer_crop_h))
sheet.paste(fc.resize((W * 2, footer_crop_h * 2), Image.NEAREST), (cx, fy))
d.rectangle([cx - 1, fy - 1, cx + W * 2, fy + footer_crop_h * 2],
            outline=(52, 52, 70))
d.text((cx, fy - 16), "FOOTER / STATS PANEL · 2×", fill=INK_DIM)

OUTDIR = pathlib.Path(os.environ.get(
    "DEPARTURE_OUTDIR",
    "/home/user/skybit/docs/flight_log/departure_board"))
OUTDIR.mkdir(parents=True, exist_ok=True)
OUT = OUTDIR / "round_2.png"
sheet.save(OUT)
print("saved %dx%d -> %s" % (sheet.size[0], sheet.size[1], OUT))
