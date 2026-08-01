"""flight-strip — the Flight Log progress screen as a printed ATC flight-progress strip.

The run is a physical document: cream stock, ruled field boxes whose HEIGHTS are
the real phase spans of the day cycle, a live sky-colour ribbon down the left
margin, event glyphs in the gutter at their true phases, and a FLOWN column of
pre-printed boxes. The player flew a sliver of DAY, so a punched perforation
crosses the DAY box at the death phase and a scarlet rubber stamp straddles it.
Everything BELOW the perforation is printed at full contrast but UNSTAMPED — the
unearned-but-claimable mass is the hero of the screen, not a faded ghost of one.

Scratch tooling for review only; game/ is untouched.
"""
import os
import math
import random
import colorsys

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.biome import palette_for_phase, CYCLE_SECONDS
from game.config import SCROLL_BASE, PIPE_SPACING

# ── constants not present in this branch's stripped game modules ─────────────
# Values mirror the authored brief; see render_flight_log_cable_tape.py.
PHASE_BOUNDARIES = [
    (0.000, "DAY"),
    (0.231, "GOLDEN HOUR"),
    (0.363, "SUNSET"),
    (0.513, "DUSK"),
    (0.644, "NIGHT"),
    (0.794, "PREDAWN"),
    (0.906, "SUNRISE"),
]
LATE_GAME_PILLAR    = 50
CLOWN_START_PILLAR  = 65
RAIN_START_PILLAR   = 70
SCROLL_NEWBIE_BASE  = 125.0
PIPE_SPACING_NEWBIE = 370
RAMP_PIPES          = 25
PLATEAU_PIPES       = 5
# Geyser starts at pillar ~47, expressed as phase over the base 320 s cycle.
THERMAL_START_PHASE = 50.0 / 320.0
# Snow squall centre: pillar 139 at 320 s cycle ≈ phase 0.804, +0.10 width offset.
SNOW_STORM_CENTER   = 0.904


# ── canvas / geometry ────────────────────────────────────────────────────────

W, H = 360, 640
STRIP_X, STRIP_Y = 26, 86
STRIP_W, STRIP_H = 308, 470
BODY_H = 412                      # header band + seven phase boxes
HEAD_H = 20                       # column-header band above the boxes
ROWS_H = BODY_H - HEAD_H
PAPER_TILT = -1.5                 # a document laid down by hand, not by CAD

DEATH_PHASE = 0.184
DEATH_PILLAR = 25
DAY_NUM = 1
TIME_ALIVE = 47

# Column rails inside the paper (local x). The ribbon carries the whole day
# cycle, so it gets real width instead of a hairline stripe; the gutter is sized
# to hold TWO half-scale event glyphs side by side without either leaving it.
CHIP_X0, CHIP_X1 = 8, 32          # live sky/land colour ribbon
GUT_X0, GUT_X1 = 34, 68           # event-code gutter
FIELD_X0 = 72                     # phase name + remarks field
TICK_RULE = 250                   # divider before the FLOWN column
TICK_CX = 279                     # optical centre of the FLOWN column

# ── ink + stock palette ──────────────────────────────────────────────────────

PAPER = (220, 200, 170)
PAPER_HI = (233, 216, 189)
PAPER_LO = (206, 184, 152)
INK = (58, 43, 30)
INK_SOFT = (104, 84, 60)
INK_FAINT = (156, 135, 106)
PERF_INK = (44, 34, 24)           # the punched rule itself
PERF_HOLE = (6, 8, 14)            # daylight through the sheet
PERF_VALLEY = (108, 86, 62)
STAMP_RED = (152, 28, 30)
BOX_BLUE = (46, 74, 116)          # unstamped = a form field waiting to be filled
HEAD_CREAM = (238, 230, 214)
HEAD_MUTED = (176, 166, 152)


def _tint(rgb, k):
    return tuple(max(0, min(255, int(c * k))) for c in rgb)


# The screen sits in the sky the run died under, dropped to a viewing-table
# darkness so the cream stock still reads as the brightest thing on the panel.
DEATH_SKY = palette_for_phase(DEATH_PHASE)['sky_mid']
SCREEN_BG = _tint(DEATH_SKY, 0.30)


def font(size):
    return pygame.font.Font(
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     'game', 'assets', 'LiberationSans-Bold.ttf'), size)


_font_cache = {}


def F(size):
    f = _font_cache.get(size)
    if f is None:
        f = font(size)
        _font_cache[size] = f
    return f


def luma(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def stock_at(y):
    """Colour of the bare stock at local y — the gradient runs DIM at the top to
    BRIGHT at the bottom so the unflown mass, not the flown sliver, catches the
    light."""
    t = max(0.0, min(1.0, y / STRIP_H))
    return tuple(int(PAPER_LO[i] + (PAPER_HI[i] - PAPER_LO[i]) * t) for i in range(3))


# ── pillar model ─────────────────────────────────────────────────────────────
# The strip is a goal list, so every row is labelled in PILLARS, not seconds.
# Pillars accumulate at scroll/spacing, both of which ease from the newbie
# endpoints to the regular ones across the onboarding ramp; integrating that
# reproduces the authored event phases (clown at P65 = phase 0.403, storm at
# P70 = 0.430) to the pillar.

def _pillar_times():
    out = [0.0]
    t = 0.0
    for n in range(0, 400):
        if n < PLATEAU_PIPES:
            rt = 0.0
        else:
            x = min(1.0, (n - PLATEAU_PIPES) / max(1, RAMP_PIPES - PLATEAU_PIPES))
            rt = 1.0 - (1.0 - x) ** 2
        scroll = SCROLL_NEWBIE_BASE + (SCROLL_BASE - SCROLL_NEWBIE_BASE) * rt
        spacing = PIPE_SPACING_NEWBIE + (PIPE_SPACING - PIPE_SPACING_NEWBIE) * rt
        t += spacing / scroll
        out.append(t)
    return out


_PT = _pillar_times()


def pillar_at(phase):
    t = phase * CYCLE_SECONDS
    n = 0
    while n + 1 < len(_PT) and _PT[n + 1] <= t:
        n += 1
    return n


# ── cached stock texture ─────────────────────────────────────────────────────
# Paper grain and vignette are static for the life of the panel, so they bake
# once into module-level surfaces. The grain is authored at quarter resolution
# and smoothscaled up: a full-res per-pixel pass is a visible hitch on WASM, and
# pulp density variation is low-frequency anyway.

_GRAIN = None
_VIGNETTE = None


def grain(w, h):
    global _GRAIN
    if _GRAIN is not None:
        return _GRAIN
    rng = random.Random(20240731)
    lw, lh = w // 4, h // 4
    low = pygame.Surface((lw, lh), pygame.SRCALPHA)

    for y in range(lh):
        for x in range(lw):
            if rng.random() < 0.5:
                low.set_at((x, y), (40, 26, 10, int(rng.random() * 22)))
            else:
                low.set_at((x, y), (255, 244, 224, int(rng.random() * 24)))

    # Fibre streaks — short horizontal strands, the tell of cheap bond stock.
    for _ in range(40):
        x = rng.randrange(lw)
        y = rng.randrange(lh)
        ln = rng.randrange(2, 7)
        dark = rng.random() < 0.55
        c = (52, 36, 18, rng.randrange(20, 40)) if dark else (255, 246, 228, rng.randrange(20, 46))
        pygame.draw.line(low, c, (x, y), (min(lw - 1, x + ln), y))

    g = pygame.transform.smoothscale(low, (w, h))

    # A sparse full-res speck pass for tooth — cheap enough to survive WASM.
    for _ in range(900):
        x = rng.randrange(w)
        y = rng.randrange(h)
        if rng.random() < 0.5:
            g.set_at((x, y), (46, 30, 14, rng.randrange(10, 26)))
        else:
            g.set_at((x, y), (255, 248, 232, rng.randrange(10, 28)))

    _GRAIN = g
    return g


def vignette(w, h):
    global _VIGNETTE
    if _VIGNETTE is not None:
        return _VIGNETTE
    v = pygame.Surface((w, h), pygame.SRCALPHA)
    steps = 30
    for i in range(steps):
        a = int(22 * (1.0 - i / steps) ** 1.7)
        if a <= 0:
            continue
        pygame.draw.rect(v, (58, 40, 22, a), pygame.Rect(i, i, w - 2 * i, h - 2 * i), 1)
    _VIGNETTE = v
    return v


# ── text helpers ─────────────────────────────────────────────────────────────

def tracked(text, size, color, tracking=0):
    """Letterspaced caps. Tracking is what separates 'printed by a machine'
    from 'typed in a text box' at these sizes."""
    f = F(size)
    glyphs = [f.render(ch, True, color) for ch in text]
    wsum = sum(g.get_width() for g in glyphs) + tracking * max(0, len(text) - 1)
    hmax = max(g.get_height() for g in glyphs) if glyphs else 0
    s = pygame.Surface((max(1, wsum), max(1, hmax)), pygame.SRCALPHA)
    x = 0
    for g in glyphs:
        s.blit(g, (x, 0))
        x += g.get_width() + tracking
    return s


def dotmatrix(text, size, color, tracking=1):
    """Ribbon-printer look: alternating raster rows print lighter because the
    pins strike a tired ribbon. Reserved for the REMARKS label — on body copy it
    only costs legibility."""
    s = tracked(text, size, color, tracking)
    mask = pygame.Surface(s.get_size(), pygame.SRCALPHA)
    mask.fill((255, 255, 255, 255))
    for y in range(0, s.get_height(), 2):
        pygame.draw.line(mask, (255, 255, 255, 150), (0, y), (s.get_width(), y))
    s.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return s


def dotted_leader(surf, x0, x1, y, color, pitch=2):
    x = x0
    while x < x1:
        surf.set_at((int(x), int(y)), color)
        x += pitch


# ── printed-ink transform for the sky ribbon ─────────────────────────────────

def printed_ink(rgb, y):
    """Screen light -> offset ink. Value drops and saturation lifts, then the
    result is forced at least 60 luma below the stock it is printed on: a sky
    swatch that sits near the paper's own value reads as a stain, not as a
    printed band."""
    r, g, b = (c / 255.0 for c in rgb)
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    v = min(1.0, v * 0.60)
    s = min(1.0, s * 1.18)
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    out = [r * 255.0, g * 255.0, b * 255.0]
    floor = luma(stock_at(y)) - 60.0
    lv = luma(out)
    if lv > floor and lv > 0:
        k = max(0.0, floor) / lv
        out = [c * k for c in out]
    return tuple(int(max(0, min(255, c))) for c in out)


# ── event glyphs (printed line-art in the gutter) ────────────────────────────
# Every glyph is authored around a unit scale k so a pair sharing one phase can
# be drawn at 0.7 and still sit wholly inside the gutter rails.

def _w(k, base=2):
    return max(1, int(round(base * k)))


def g_geyser(s, cx, cy, k=1.0):
    """Thermal plume: a vent lip with a narrowing column of spray."""
    P = lambda dx, dy: (cx + dx * k, cy + dy * k)
    pygame.draw.line(s, INK, P(-7, 7), P(7, 7), _w(k))
    pygame.draw.polygon(s, INK, [P(-5, 6), P(-2, -2), P(-1, -8),
                                 P(1, -8), P(2, -2), P(5, 6)], _w(k))
    pygame.draw.line(s, INK_SOFT, P(-4, 2), P(-6, -2), 1)
    pygame.draw.line(s, INK_SOFT, P(4, 2), P(6, -2), 1)
    pygame.draw.circle(s, INK, P(-5, -6), _w(k, 1))
    pygame.draw.circle(s, INK, P(5, -5), _w(k, 1))


def g_lamp(s, cx, cy, k=1.0):
    """Genie lamp: squat body, spout, handle loop, one curl of smoke."""
    P = lambda dx, dy: (cx + dx * k, cy + dy * k)
    body = pygame.Rect(0, 0, int(12 * k), int(8 * k))
    body.topleft = P(-7, -1)
    pygame.draw.ellipse(s, INK, body, _w(k))
    pygame.draw.polygon(s, INK, [P(4, 1), P(9, -3), P(9, -1), P(5, 4)], 0)
    pygame.draw.line(s, INK, P(-7, 1), P(-9, 4), _w(k))
    pygame.draw.line(s, INK, P(-9, 4), P(-6, 6), _w(k))
    pygame.draw.line(s, INK, P(-2, -2), P(0, -6), 1)
    pygame.draw.line(s, INK, P(0, -6), P(-3, -9), 1)
    pygame.draw.line(s, INK, P(-6, 8), P(5, 8), _w(k))


def g_clown(s, cx, cy, k=1.0):
    """Harlequin diamond: quartered lozenge, two solid quadrants."""
    P = lambda dx, dy: (cx + dx * k, cy + dy * k)
    pts = [P(0, -9), P(7, 0), P(0, 9), P(-7, 0)]
    pygame.draw.polygon(s, INK, [P(0, -9), P(7, 0), P(0, 0)], 0)
    pygame.draw.polygon(s, INK, [P(0, 0), P(-7, 0), P(0, 9)], 0)
    pygame.draw.polygon(s, INK, pts, _w(k))


def g_rain(s, cx, cy, k=1.0):
    """Storm-front teardrop with two slanted fall strokes."""
    P = lambda dx, dy: (cx + dx * k, cy + dy * k)
    pygame.draw.polygon(s, INK, [P(0, -9), P(5, -1), P(-5, -1)], 0)
    pygame.draw.circle(s, INK, P(0, 1), max(2, int(5 * k)))
    pygame.draw.circle(s, stock_at(cy), P(-1, 0), max(1, int(2 * k)))
    pygame.draw.line(s, INK_SOFT, P(-7, 3), P(-8, 8), 1)
    pygame.draw.line(s, INK_SOFT, P(7, 3), P(6, 8), 1)


def g_snow(s, cx, cy, k=1.0):
    """Six-spoke asterism with crossbars."""
    for i in range(6):
        a = i * math.pi / 3
        dx, dy = math.cos(a), math.sin(a)
        pygame.draw.line(s, INK, (cx, cy), (cx + dx * 8 * k, cy + dy * 8 * k), _w(k))
        bx, by = cx + dx * 5 * k, cy + dy * 5 * k
        px, py = -dy * 2.6 * k, dx * 2.6 * k
        pygame.draw.line(s, INK, (bx - px, by - py), (bx + px, by + py), 1)
    pygame.draw.circle(s, INK, (cx, cy), _w(k))


GLYPHS = {'geyser': g_geyser, 'lamp': g_lamp, 'clown': g_clown,
          'rain': g_rain, 'snow': g_snow}


# ── FLOWN column marks ───────────────────────────────────────────────────────

BOX_W, BOX_H = 21, 17


def empty_box(s, cx, cy):
    """Pre-printed and waiting. Indigo gives 'unclaimed' its own colour identity
    so the column reads as six open fields rather than six absences."""
    r = pygame.Rect(0, 0, BOX_W, BOX_H)
    r.center = (cx, cy)
    pygame.draw.rect(s, BOX_BLUE, r, 1)
    for dx in (0, BOX_W - 4):
        pygame.draw.line(s, BOX_BLUE, (r.left + dx, r.top + 1), (r.left + dx + 3, r.top + 1), 1)
        pygame.draw.line(s, BOX_BLUE, (r.left + dx, r.bottom - 2), (r.left + dx + 3, r.bottom - 2), 1)


def macaw_tick(s, cx, cy):
    """The flown mark is Pip himself, inked into the box — the one silhouette on
    the sheet the player already owns."""
    r = pygame.Rect(0, 0, BOX_W, BOX_H)
    r.center = (cx, cy)
    pygame.draw.rect(s, INK_SOFT, r, 1)
    px, py = cx - 1, cy + 1
    pygame.draw.polygon(s, INK, [(px - 4, py - 1), (px - 9, py + 5),
                                 (px - 8, py + 1), (px - 4, py + 2)])
    pygame.draw.ellipse(s, INK, pygame.Rect(px - 5, py - 3, 10, 8))
    pygame.draw.circle(s, INK, (px + 4, py - 4), 3)
    pygame.draw.polygon(s, INK, [(px + 6, py - 5), (px + 9, py - 4), (px + 6, py - 2)])
    pygame.draw.line(s, (232, 214, 186), (px - 2, py - 1), (px + 1, py + 2), 1)


def logged_ring(s, cx, cy, r=13):
    """Ring the flown event glyph — the controller's 'seen and logged' circle."""
    pygame.draw.circle(s, (92, 70, 46), (cx, cy), r, 1)
    pygame.draw.circle(s, (92, 70, 46), (cx + 1, cy), r, 1)


# ── the rubber stamp ─────────────────────────────────────────────────────────

def death_stamp(text, target_w, max_h):
    img = tracked(text, 19, STAMP_RED, 4)
    pad_x, pad_y = 15, 8
    w = img.get_width() + pad_x * 2
    h = img.get_height() + pad_y * 2
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(s, STAMP_RED, pygame.Rect(0, 0, w, h), 3, border_radius=3)
    pygame.draw.rect(s, STAMP_RED, pygame.Rect(5, 5, w - 10, h - 10), 1, border_radius=2)
    s.blit(img, (pad_x, pad_y))

    # Starved-ribbon roughening: multiply the alpha with a blotchy mask so the
    # impression is uneven the way a hand-pressed stamp is. The 236 floor keeps
    # the ink deep — a pale stamp read as a decal rather than a verdict.
    rng = random.Random(4242)
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    mask.fill((255, 255, 255, 236))
    for _ in range(150):
        rx, ry = rng.randrange(w), rng.randrange(h)
        rr = rng.randrange(1, 4)
        pygame.draw.circle(mask, (255, 255, 255, rng.randrange(60, 170)), (rx, ry), rr)
    for _ in range(4):
        ry = rng.randrange(h)
        pygame.draw.line(mask, (255, 255, 255, rng.randrange(90, 150)),
                         (rng.randrange(0, w // 2), ry), (w, ry), 1)
    s.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    # A hand tilts the stamp a few degrees; more than that and it reads as a
    # sticker rotated in software.
    s = pygame.transform.rotozoom(s, 4.5, 1.0)
    k = min(target_w / s.get_width(), max_h / s.get_height())
    return pygame.transform.smoothscale(
        s, (int(s.get_width() * k), int(s.get_height() * k)))


def ink_bbox(surf):
    rects = pygame.mask.from_surface(surf, 12).get_bounding_rects()
    if not rects:
        return surf.get_rect()
    r = rects[0]
    for o in rects[1:]:
        r = r.union(o)
    return r


# ── the strip ────────────────────────────────────────────────────────────────

def rows():
    out = []
    for i, (p0, name) in enumerate(PHASE_BOUNDARIES):
        p1 = PHASE_BOUNDARIES[i + 1][0] if i + 1 < len(PHASE_BOUNDARIES) else 1.0
        out.append((name, p0, p1))
    return out


RIBBON_CODE = {'DAY': 'DAY', 'GOLDEN HOUR': 'GLD', 'SUNSET': 'SET', 'DUSK': 'DSK',
               'NIGHT': 'NGT', 'PREDAWN': 'PRE', 'SUNRISE': 'RIS'}

EVENTS = [
    (THERMAL_START_PHASE, 'geyser', 'GEYSER FIELD', None),
    (0.300, 'lamp', 'GENIE LAMP', LATE_GAME_PILLAR),
    (0.403, 'clown', 'CLOWN GAUNTLET', CLOWN_START_PILLAR),
    (0.430, 'rain', 'STORM FRONT', RAIN_START_PILLAR),
    (SNOW_STORM_CENTER, 'snow', 'SNOW SQUALL', None),
]


def py(p):
    return HEAD_H + p * ROWS_H


def build_strip():
    s = pygame.Surface((STRIP_W, STRIP_H), pygame.SRCALPHA)
    s.fill(PAPER)
    for y in range(STRIP_H):
        pygame.draw.line(s, stock_at(y), (0, y), (STRIP_W, y))
    s.blit(grain(STRIP_W, STRIP_H), (0, 0))

    perf_y = int(py(DEATH_PHASE))
    rr = rows()

    # ── column header band ──────────────────────────────────────────────────
    # The whole document decodes off this line: a FLOWN column with one mark in
    # it and six empty boxes below says 'unstamped = unearned' before any body
    # copy is read.
    pygame.draw.rect(s, (198, 180, 150), pygame.Rect(4, 0, STRIP_W - 8, HEAD_H))
    cols = [('SKY', CHIP_X0, CHIP_X1), ('LOG', GUT_X0, GUT_X1),
            ('PHASE', FIELD_X0, TICK_RULE - 4), ('FLOWN', TICK_RULE + 4, STRIP_W - 6)]
    for name, x0, x1 in cols:
        img = tracked(name, 12, INK, 1)
        if img.get_width() > (x1 - x0) + 4:
            img = tracked(name, 12, INK, 0)
        s.blit(img, ((x0 + x1) // 2 - img.get_width() // 2, HEAD_H // 2 - img.get_height() // 2))
    pygame.draw.line(s, INK, (4, HEAD_H - 2), (STRIP_W - 4, HEAD_H - 2), 1)
    pygame.draw.line(s, INK_SOFT, (4, HEAD_H), (STRIP_W - 4, HEAD_H), 1)

    # ── colour ribbon: a continuous sample of the real day cycle ─────────────
    # Sky on the wide lane, ground on the narrow one, resampled per scanline so
    # the ribbon IS the palette rather than seven flat swatches — run through the
    # printed-ink transform so it sits ON the stock instead of glowing off it.
    for y in range(HEAD_H, BODY_H):
        p = (y - HEAD_H) / ROWS_H
        pal = palette_for_phase(p)
        pygame.draw.line(s, printed_ink(pal['sky_mid'], y), (CHIP_X0, y), (CHIP_X0 + 15, y))
        pygame.draw.line(s, printed_ink(pal['ground_mid'], y), (CHIP_X0 + 16, y), (CHIP_X1 - 1, y))
    pygame.draw.rect(s, INK_SOFT,
                     pygame.Rect(CHIP_X0, HEAD_H, CHIP_X1 - CHIP_X0, BODY_H - HEAD_H), 1)
    pygame.draw.line(s, (0, 0, 0, 70), (CHIP_X0 + 15, HEAD_H), (CHIP_X0 + 15, BODY_H))

    # ── ruled form: column rails + row rules ────────────────────────────────
    for x in (GUT_X1, TICK_RULE):
        pygame.draw.line(s, INK_FAINT, (x, 0), (x, BODY_H))
    pygame.draw.rect(s, INK_SOFT, pygame.Rect(4, 0, STRIP_W - 8, BODY_H), 1)

    # ── the stamp, sized and placed before anything can collide with it ─────
    # 55% of the sheet, pushed right: that buys a 120px+ run of bare perforation
    # on the left, and keeps every scarlet pixel clear of the first unflown row
    # name below the fold.
    stamp = death_stamp('18% FLOWN', int(STRIP_W * 0.55), 50)
    sb = ink_bbox(stamp)
    stamp_pos = (STRIP_W - 8 - sb.right, 106 - sb.bottom)
    stamp_ink = pygame.Rect(stamp_pos[0] + sb.x, stamp_pos[1] + sb.y, sb.w, sb.h)

    header_bot = {}
    for name, p0, p1 in rr:
        y0, y1 = py(p0), py(p1)
        if p0 > 0:
            pygame.draw.line(s, INK_SOFT, (4, int(y0)), (STRIP_W - 4, int(y0)), 1)
            pygame.draw.line(s, (238, 224, 200), (4, int(y0) + 1), (STRIP_W - 4, int(y0) + 1), 1)

        label = tracked(name, 14, INK, 1)
        ty = int(y0) + 3
        s.blit(label, (FIELD_X0, ty))

        # Pillar range, not elapsed time: the strip is a list of things still to
        # reach, and a player counts pillars, never seconds.
        rng_txt = 'P%d–P%d' % (pillar_at(p0), pillar_at(p1) if p1 < 1.0 else pillar_at(0.9999))
        dur = tracked(rng_txt, 10, INK_SOFT, 1)
        dx = TICK_RULE - 6 - dur.get_width()
        s.blit(dur, (dx, ty + 4))
        dotted_leader(s, FIELD_X0 + label.get_width() + 6, dx - 5,
                      ty + label.get_height() - 6, INK_FAINT)
        # Cap height, not line height — the font's descender space is empty air
        # that captions below are free to use.
        header_bot[name] = ty + 13

        # DAY's mark rides high in the flown sliver so the stamp has clean air;
        # every other row centres in its box.
        if p0 == 0.0:
            macaw_tick(s, TICK_CX, 44)
        else:
            empty_box(s, TICK_CX, int((y0 + y1) / 2))

        # Ribbon boundary: an ink tick plus a three-letter code on a cream chip.
        # The chip is what makes the ribbon decodable with the colour removed.
        code = RIBBON_CODE.get(name)
        if code:
            pygame.draw.line(s, INK, (CHIP_X0, int(y0)), (CHIP_X1 - 1, int(y0)), 1)
            ci = tracked(code, 7, INK, 0)
            chip = pygame.Rect(0, 0, ci.get_width() + 4, ci.get_height() + 1)
            chip.midtop = ((CHIP_X0 + CHIP_X1) // 2, int(y0) + 2)
            pygame.draw.rect(s, (238, 228, 206), chip)
            s.blit(ci, (chip.x + 2, chip.y))

    # ── event codes in the gutter, at their true phases ─────────────────────
    gut_cx = (GUT_X0 + GUT_X1) // 2
    # Clown and storm are 11 px apart on the sheet. They share ONE y and sit
    # shoulder to shoulder at 0.7 scale, both wholly inside the gutter rails,
    # with their captions stacked to the right.
    pair_y = (py(0.403) + py(0.430)) / 2
    layout = {'clown': (GUT_X0 + 10, pair_y, 0.70),
              'rain': (GUT_X1 - 10, pair_y, 0.70)}

    used = {}
    for ph, kind, label, pillar in EVENTS:
        row = next(r for r in rr if r[1] <= ph < r[2] or (ph >= 1.0 and r[2] == 1.0))
        # Snow lands a hair past the PREDAWN/SUNRISE rule; nudge the glyph clear
        # of the rule while it still belongs to the predawn squall.
        if kind == 'snow':
            row = rr[-2]
            gx, gy, k = gut_cx, py(row[2]) - 10, 1.0
        else:
            gx, gy, k = layout.get(kind, (gut_cx, py(ph), 1.0))
        GLYPHS[kind](s, int(gx), int(gy), k)
        if kind == 'geyser':
            logged_ring(s, int(gx), int(gy))

        pnum = pillar if pillar is not None else pillar_at(ph)
        img = tracked('%s · P%d' % (label, pnum), 9, INK, 1)
        ih = img.get_height()
        tx = TICK_RULE - 6 - img.get_width()

        # The glyph holds the true phase; the caption only has to point at it —
        # so captions dodge the row header, the stamp, and each other.
        ly = gy
        floor = header_bot[row[0]] + ih // 2 + 3
        ly = max(ly, floor)
        ly = max(ly, used.get(row[0], 0) + ih + 2)
        cap_rect = pygame.Rect(tx, int(ly) - ih // 2, img.get_width(), ih)
        if cap_rect.colliderect(stamp_ink.inflate(0, 8)):
            ly = stamp_ink.top - ih // 2 - 6
        ly = min(ly, py(row[2]) - ih // 2 - 3)
        used[row[0]] = ly
        s.blit(img, (tx, int(ly) - ih // 2))

        # Dog-legged leader — the glyph stays on its phase even when the caption
        # has to step aside.
        kx = GUT_X1 + 12
        dotted_leader(s, GUT_X1 + 5, kx, int(gy), INK_SOFT)
        if abs(ly - gy) > 2:
            for yy in range(int(min(ly, gy)), int(max(ly, gy)), 2):
                s.set_at((kx, yy), INK_SOFT)
        dotted_leader(s, kx, tx - 4, int(ly), INK_SOFT)

    # ── flown region: handled paper, above the perforation ──────────────────
    wash = pygame.Surface((STRIP_W - 8, perf_y), pygame.SRCALPHA)
    wash.fill((146, 116, 74, 26))
    pygame.draw.rect(wash, (128, 98, 60, 22), pygame.Rect(0, perf_y - 14, STRIP_W - 8, 14))
    s.blit(wash, (4, 0))

    # Ink smudge where a thumb dragged across the fresh line.
    sm = pygame.Surface((90, 26), pygame.SRCALPHA)
    rng = random.Random(77)
    for _ in range(9):
        cx = rng.randrange(10, 80)
        cy = rng.randrange(6, 20)
        pygame.draw.ellipse(sm, (74, 54, 34, rng.randrange(28, 66)),
                            pygame.Rect(cx, cy, rng.randrange(8, 22), rng.randrange(3, 7)))
    sm = pygame.transform.smoothscale(pygame.transform.smoothscale(sm, (30, 9)), (90, 26))
    s.blit(sm, (100, perf_y - 20))

    # ── footer remarks ──────────────────────────────────────────────────────
    fy = BODY_H
    pygame.draw.line(s, INK_SOFT, (4, fy), (STRIP_W - 4, fy), 1)
    pygame.draw.line(s, INK_FAINT, (4, fy + 3), (STRIP_W - 4, fy + 3), 1)
    pygame.draw.rect(s, INK_SOFT, pygame.Rect(4, fy, STRIP_W - 8, STRIP_H - fy - 4), 1)

    s.blit(dotmatrix('REMARKS', 8, INK_SOFT, 2), (11, fy + 5))
    serial = tracked('SB-1', 7, INK_FAINT, 1)
    s.blit(serial, (STRIP_W - 11 - serial.get_width(), fy + 6))

    # One line, set at reading size, with the thing it names drawn beside it.
    teaser = tracked('NEXT: GENIE LAMP · PILLAR %d' % LATE_GAME_PILLAR, 12, INK, 1)
    s.blit(teaser, (11, fy + 16))
    g_lamp(s, 11 + teaser.get_width() + 15, fy + 22, 0.85)

    tail = tracked('6 OF 7 PHASES UNSTAMPED · 82%% UNFLOWN', 9, INK_SOFT, 1)
    s.blit(tail, (11, fy + 33))

    # ── stamp ───────────────────────────────────────────────────────────────
    s.blit(stamp, stamp_pos)

    # ── perforation — drawn LAST, over ink and stamp alike ──────────────────
    # This is the strongest horizontal on the sheet by design: a punched line the
    # eye lands on first, so 'you got here' and 'the rest is still printed' are
    # one read. Real holes at full ink, a continuous rule so no x along the run
    # is bare stock, and a two-pixel valley under it for the sheet's thickness.
    # Where the run crosses dark ink — sky ribbon, logged geyser, the stamp
    # itself — the die crushes fibre and lifts pigment, so a bleached edge is
    # laid in ABOVE the line. Bare stock gets none of it: a highlight under the
    # rule would only cancel the very contrast the line exists for.
    for x in range(4, STRIP_W - 4):
        if luma(s.get_at((x, perf_y - 2))[:3]) < 150:
            s.set_at((x, perf_y - 1), (240, 228, 204))
    pygame.draw.line(s, PERF_INK, (4, perf_y), (STRIP_W - 5, perf_y), 1)
    for hx in range(8, STRIP_W - 6, 8):
        pygame.draw.circle(s, PERF_HOLE, (hx, perf_y), 1)
    pygame.draw.line(s, PERF_VALLEY, (4, perf_y + 1), (STRIP_W - 5, perf_y + 1), 1)
    pygame.draw.line(s, (174, 152, 122), (4, perf_y + 2), (STRIP_W - 5, perf_y + 2), 1)
    for ex in (2, STRIP_W - 3):
        pygame.draw.circle(s, PERF_INK, (ex, perf_y), 2, 1)

    # ── stock finish ────────────────────────────────────────────────────────
    s.blit(vignette(STRIP_W, STRIP_H), (0, 0))
    pygame.draw.rect(s, (188, 166, 134), pygame.Rect(0, 0, STRIP_W, STRIP_H), 1,
                     border_radius=3)

    # Rounded corners via an alpha-only multiply — keeps the paper a cut sheet.
    mask = pygame.Surface((STRIP_W, STRIP_H), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     pygame.Rect(0, 0, STRIP_W, STRIP_H), 0, border_radius=3)
    s.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return s, perf_y, stamp_ink


# ── screen ───────────────────────────────────────────────────────────────────

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


def build_screen():
    scr = pygame.Surface((W, H))
    bg = build_skybit_bg()
    scr.blit(bg, (0, 0))

    title = tracked('FLIGHT LOG', 22, HEAD_CREAM, 3)
    scr.blit(title, (W // 2 - title.get_width() // 2, 22))
    stats = tracked('DAY %d  ·  PILLAR %d  ·  0:%02d' % (DAY_NUM, DEATH_PILLAR, TIME_ALIVE),
                    11, HEAD_MUTED, 1)
    scr.blit(stats, (W // 2 - stats.get_width() // 2, 54))
    pygame.draw.line(scr, _tint(DEATH_SKY, 0.5), (W // 2 - 70, 74), (W // 2 + 70, 74), 1)

    strip, perf_y, stamp_ink = build_strip()
    rot = pygame.transform.rotozoom(strip, PAPER_TILT, 1.0)
    cx, cy = STRIP_X + STRIP_W // 2, STRIP_Y + STRIP_H // 2
    rect = rot.get_rect(center=(cx, cy))

    shadow = pygame.mask.from_surface(rot).to_surface(
        setcolor=(0, 0, 0, 90), unsetcolor=(0, 0, 0, 0))
    soft = pygame.transform.smoothscale(
        pygame.transform.smoothscale(shadow, (rect.w // 4, rect.h // 4)), (rect.w, rect.h))
    scr.blit(soft, (rect.x + 4, rect.y + 6))
    scr.blit(shadow, (rect.x + 3, rect.y + 3))
    scr.blit(rot, rect.topleft)

    pill = pygame.Rect(0, 0, 104, 32)
    pill.center = (W // 2, 600)
    pygame.draw.rect(scr, _tint(DEATH_SKY, 0.16), pill, 0, border_radius=16)
    pygame.draw.rect(scr, _tint(DEATH_SKY, 0.55), pill, 1, border_radius=16)
    bt = tracked('BACK', 13, (238, 232, 220), 2)
    scr.blit(bt, (pill.centerx - bt.get_width() // 2, pill.centery - bt.get_height() // 2))
    return scr, strip, perf_y, stamp_ink


# ── review sheet ─────────────────────────────────────────────────────────────

CROPS = [('COLUMN HEADER BAND — SKY / LOG / PHASE / FLOWN', pygame.Rect(20, 76, 320, 48)),
         ('PUNCHED PERFORATION + 55% STAMP · 127PX CLEAR RUN', pygame.Rect(20, 136, 320, 92)),
         ('EVENT GUTTER — CLOWN + STORM SHOULDER TO SHOULDER', pygame.Rect(20, 248, 260, 92)),
         ('FOOTER — ONE-LINE TEASER + INLINE LAMP', pygame.Rect(20, 486, 320, 80))]


def build_sheet(scr):
    pad = 16
    zw = max(c.w for _, c in CROPS) * 2
    left_w = W + pad
    right_h = sum(c.h * 2 + 24 for _, c in CROPS) + pad * len(CROPS)
    sh = max(H + 30, right_h) + pad * 2
    sheet = pygame.Surface((left_w + zw + pad * 2, sh))
    sheet.fill((14, 13, 18))

    lab = tracked('FLIGHT LOG — FLIGHT STRIP — ROUND 2', 12, (214, 206, 190), 2)
    sheet.blit(lab, (pad, pad))
    sheet.blit(scr, (pad, pad + 22))
    pygame.draw.rect(sheet, (70, 64, 56), pygame.Rect(pad, pad + 22, W, H), 1)

    y = pad + 22
    x = pad + left_w
    for label, r in CROPS:
        img = pygame.transform.scale(scr.subsurface(r).copy(), (r.w * 2, r.h * 2))
        sheet.blit(tracked(label, 11, (208, 200, 184), 1), (x, y))
        y += 18
        sheet.blit(img, (x, y))
        pygame.draw.rect(sheet, (70, 64, 56), pygame.Rect(x, y, r.w * 2, r.h * 2), 1)
        y += r.h * 2 + pad
    return sheet


def squint_report(strip, perf_y, stamp_ink):
    print('perf_y (strip local) =', perf_y)
    print('stamp ink bbox =', stamp_ink, ' width %% of strip = %.1f' %
          (100.0 * stamp_ink.w / STRIP_W))
    stock_l = luma(stock_at(perf_y))
    for x in (80, 120, 160, 200, 240):
        pc = strip.get_at((x, perf_y))[:3]
        above = strip.get_at((x, perf_y - 4))[:3]
        print('  x=%3d  perf=%-16s over=%-16s d(local)=%6.1f  d(stock)=%6.1f'
              % (x, pc, above, luma(above) - luma(pc), stock_l - luma(pc)))
    # Every x along the run, measured against the stock the line is punched
    # through — that is what the eye compares a perforation to, whether ink or
    # stamp happens to sit on top of it.
    allmin = min(stock_l - luma(strip.get_at((x, perf_y))[:3])
                 for x in range(6, STRIP_W - 6))
    print('  min delta vs stock across full run = %.1f' % allmin)
    print('  SQUINT TEST (holes vs paper): %s' % ('PASS' if allmin >= 110 else 'FAIL'))

    # Supplementary: the punched band's own internal step (crush highlight to
    # hole), which is what the eye actually resolves where ink sits on the run.
    step = min(max(abs(luma(strip.get_at((x, perf_y + d))[:3]) -
                       luma(strip.get_at((x, perf_y))[:3])) for d in (-1, 2))
               for x in range(6, STRIP_W - 6))
    print('  min internal band step = %.1f' % step)

    # strongest horizontal check: compare against the heaviest row rule
    rule_y = int(py(0.23125))
    rd = luma(strip.get_at((160, rule_y - 4))[:3]) - luma(strip.get_at((160, rule_y))[:3])
    print('  row rule delta = %.1f (perf must dominate)' % rd)

    # clearance: stamp ink vs GOLDEN HOUR row name
    gh_top = int(py(0.23125)) + 3
    print('  stamp ink bottom = %d, GOLDEN HOUR glyph top = %d, clearance = %d'
          % (stamp_ink.bottom, gh_top, gh_top - stamp_ink.bottom))
    print('  clear perforation run left of stamp = %d px' % (stamp_ink.left - 4))

    # Ribbon separation from stock, skipping the boundary ticks and code chips.
    bounds = [int(py(p)) for p, _ in PHASE_BOUNDARIES] + [perf_y]
    worst_r = 999
    for y in range(HEAD_H + 2, BODY_H - 2):
        if any(abs(y - b) < 14 for b in bounds):
            continue
        st = luma(stock_at(y))
        for x in (CHIP_X0 + 4, CHIP_X0 + 20):
            worst_r = min(worst_r, st - luma(strip.get_at((x, y))[:3]))
    print('  min ribbon-vs-stock delta = %.1f' % worst_r)
    print('  perf over ribbon: sky=%s ground=%s'
          % (strip.get_at((CHIP_X0 + 4, perf_y))[:3], strip.get_at((CHIP_X0 + 20, perf_y))[:3]))


def main():
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           'docs', 'flight_log_progress', 'flight_strip')
    os.makedirs(out_dir, exist_ok=True)
    scr, strip, perf_y, stamp_ink = build_screen()
    out_r3 = os.path.join(out_dir, "round_3.png")
    pygame.image.save(scr, out_r3)
    loaded = pygame.image.load(out_r3)
    print(f"saved {out_r3}  {loaded.get_size()}")
    pygame.image.save(build_sheet(scr), os.path.join(out_dir, 'round_2.png'))
    squint_report(strip, perf_y, stamp_ink)
    print('wrote', out_dir)


if __name__ == '__main__':
    main()
