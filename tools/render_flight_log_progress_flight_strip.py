"""flight-strip — the Flight Log progress screen as a printed ATC flight-progress strip.

The run is a physical document: cream stock, ruled field boxes whose HEIGHTS are
the real phase spans of the day cycle, a live sky-colour ribbon down the left
margin, event glyphs in the gutter at their true phases, and a completion column.
The player flew a sliver of DAY, so a perforation crosses the DAY box at the death
phase and a scarlet rubber stamp straddles it. Everything BELOW the perforation is
still fully printed at full contrast but unstamped — the unearned-but-claimable
mass is the hero of the screen, not a faded ghost of one.

Scratch tooling for review only; game/ is untouched.
"""
import os
import math
import random

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.biome import PHASE_BOUNDARIES, palette_for_phase, CYCLE_SECONDS
from game.config import LATE_GAME_PILLAR, CLOWN_START_PILLAR, RAIN_START_PILLAR
from game.weather import THERMAL_START_PHASE, SNOW_STORM_CENTER


# ── canvas / geometry ────────────────────────────────────────────────────────

W, H = 360, 640
STRIP_X, STRIP_Y = 26, 86
STRIP_W, STRIP_H = 308, 470
BODY_H = 430                      # the seven phase boxes; footer takes the rest
PAPER_TILT = -1.5                 # a document laid down by hand, not by CAD

DEATH_PHASE = 0.184
DEATH_PILLAR = 25
DAY_NUM = 1
TIME_ALIVE = 47

# Column rails inside the paper (local x).
CHIP_X0, CHIP_X1 = 10, 23         # live sky/land colour ribbon
GUT_X0, GUT_X1 = 25, 53           # event-code gutter
FIELD_X0 = 57                     # phase name + remarks field
TICK_RULE = 251                   # divider before the completion column
TICK_CX = 276

# ── ink + stock palette ──────────────────────────────────────────────────────

SCREEN_BG = (8, 8, 20)
PAPER = (220, 200, 170)
PAPER_HI = (233, 216, 189)
PAPER_LO = (206, 184, 152)
INK = (58, 43, 30)
INK_SOFT = (104, 84, 60)
INK_FAINT = (156, 135, 106)
PERF_INK = (176, 152, 118)
STAMP_RED = (188, 40, 38)
HEAD_CREAM = (238, 230, 214)
HEAD_MUTED = (146, 148, 176)


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


# ── cached stock texture ─────────────────────────────────────────────────────
# Paper grain and vignette are static for the life of the panel, so they bake
# once into module-level surfaces; a per-frame per-pixel pass would be fatal on
# the WASM target.

_GRAIN = None
_VIGNETTE = None


def grain(w, h):
    global _GRAIN
    if _GRAIN is not None:
        return _GRAIN
    rng = random.Random(20240731)
    g = pygame.Surface((w, h), pygame.SRCALPHA)

    # Soft mottling: low-res noise stretched up reads as pulp density variation
    # rather than the uniform TV-static a full-res random pass gives.
    lw, lh = w // 8, h // 8
    low = pygame.Surface((lw, lh), pygame.SRCALPHA)
    for y in range(lh):
        for x in range(lw):
            v = rng.random()
            if v < 0.5:
                low.set_at((x, y), (40, 26, 10, int(rng.random() * 16)))
            else:
                low.set_at((x, y), (255, 244, 224, int(rng.random() * 18)))
    g.blit(pygame.transform.smoothscale(low, (w, h)), (0, 0))

    # Fibre streaks — short horizontal strands, the tell of cheap bond stock.
    for _ in range(90):
        x = rng.randrange(w)
        y = rng.randrange(h)
        ln = rng.randrange(4, 22)
        dark = rng.random() < 0.55
        c = (52, 36, 18, rng.randrange(8, 16)) if dark else (255, 246, 228, rng.randrange(8, 18))
        pygame.draw.line(g, c, (x, y), (min(w - 1, x + ln), y))

    # Fine speckle on top for tooth.
    for _ in range(5200):
        x = rng.randrange(w)
        y = rng.randrange(h)
        if rng.random() < 0.5:
            g.set_at((x, y), (46, 30, 14, rng.randrange(8, 26)))
        else:
            g.set_at((x, y), (255, 248, 232, rng.randrange(8, 28)))

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
    pins strike a tired ribbon. Legibility survives; a true dot mask would not
    at 9 px."""
    s = tracked(text, size, color, tracking)
    mask = pygame.Surface(s.get_size(), pygame.SRCALPHA)
    mask.fill((255, 255, 255, 255))
    for y in range(0, s.get_height(), 2):
        pygame.draw.line(mask, (255, 255, 255, 150), (0, y), (s.get_width(), y))
    s.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return s


def dashed_h(surf, x0, x1, y, color, on=4, off=4, width=1):
    x = x0
    while x < x1:
        pygame.draw.line(surf, color, (x, y), (min(x1, x + on), y), width)
        x += on + off


def dotted_leader(surf, x0, x1, y, color):
    x = x0
    while x < x1:
        surf.set_at((int(x), int(y)), color)
        x += 3


# ── event glyphs (printed line-art in the gutter) ────────────────────────────

def g_geyser(s, cx, cy):
    """Thermal plume: a vent lip with a narrowing column of spray."""
    pygame.draw.line(s, INK, (cx - 7, cy + 7), (cx + 7, cy + 7), 2)
    plume = [(cx - 5, cy + 6), (cx - 2, cy - 2), (cx - 1, cy - 8),
             (cx + 1, cy - 8), (cx + 2, cy - 2), (cx + 5, cy + 6)]
    pygame.draw.polygon(s, INK, plume, 2)
    pygame.draw.line(s, INK_SOFT, (cx - 4, cy + 2), (cx - 6, cy - 2), 1)
    pygame.draw.line(s, INK_SOFT, (cx + 4, cy + 2), (cx + 6, cy - 2), 1)
    pygame.draw.circle(s, INK, (cx - 5, cy - 6), 1)
    pygame.draw.circle(s, INK, (cx + 5, cy - 5), 1)


def g_lamp(s, cx, cy):
    """Genie lamp: squat body, spout, handle loop, one curl of smoke."""
    body = pygame.Rect(cx - 7, cy - 1, 12, 8)
    pygame.draw.ellipse(s, INK, body, 2)
    pygame.draw.polygon(s, INK, [(cx + 4, cy + 1), (cx + 10, cy - 3),
                                 (cx + 10, cy - 1), (cx + 5, cy + 4)], 0)
    pygame.draw.line(s, INK, (cx - 7, cy + 1), (cx - 10, cy + 4), 2)
    pygame.draw.line(s, INK, (cx - 10, cy + 4), (cx - 6, cy + 6), 2)
    pygame.draw.line(s, INK, (cx - 2, cy - 2), (cx, cy - 6), 1)
    pygame.draw.line(s, INK, (cx, cy - 6), (cx - 3, cy - 9), 1)
    pygame.draw.line(s, INK, (cx - 6, cy + 8), (cx + 5, cy + 8), 2)


def g_clown(s, cx, cy):
    """Harlequin diamond: quartered lozenge, two solid quadrants."""
    pts = [(cx, cy - 9), (cx + 7, cy), (cx, cy + 9), (cx - 7, cy)]
    pygame.draw.polygon(s, INK, [(cx, cy - 9), (cx + 7, cy), (cx, cy)], 0)
    pygame.draw.polygon(s, INK, [(cx, cy), (cx - 7, cy), (cx, cy + 9)], 0)
    pygame.draw.polygon(s, INK, pts, 2)
    pygame.draw.circle(s, INK, (cx + 3, cy + 4), 1)
    pygame.draw.circle(s, INK, (cx - 3, cy - 4), 1)


def g_rain(s, cx, cy):
    """Storm-front teardrop with two slanted fall strokes."""
    pygame.draw.polygon(s, INK, [(cx, cy - 9), (cx + 5, cy - 1), (cx - 5, cy - 1)], 0)
    pygame.draw.circle(s, INK, (cx, cy + 1), 5)
    pygame.draw.circle(s, PAPER, (cx - 1, cy), 2)
    pygame.draw.line(s, INK_SOFT, (cx - 9, cy + 2), (cx - 11, cy + 7), 1)
    pygame.draw.line(s, INK_SOFT, (cx + 9, cy + 2), (cx + 7, cy + 7), 1)


def g_snow(s, cx, cy):
    """Six-spoke asterism with crossbars."""
    for i in range(6):
        a = i * math.pi / 3
        dx, dy = math.cos(a), math.sin(a)
        pygame.draw.line(s, INK, (cx, cy), (cx + dx * 8, cy + dy * 8), 2)
        bx, by = cx + dx * 5, cy + dy * 5
        px, py = -dy * 2.6, dx * 2.6
        pygame.draw.line(s, INK, (bx - px, by - py), (bx + px, by + py), 1)
    pygame.draw.circle(s, INK, (cx, cy), 2)


GLYPHS = {'geyser': g_geyser, 'lamp': g_lamp, 'clown': g_clown,
          'rain': g_rain, 'snow': g_snow}


# ── completion column marks ──────────────────────────────────────────────────

def empty_box(s, cx, cy):
    """Pre-printed, waiting. Crisp rule + a faint interior dot grid so it reads
    as a field to be filled, not as an absence."""
    r = pygame.Rect(0, 0, 17, 17)
    r.center = (cx, cy)
    pygame.draw.rect(s, INK_SOFT, r, 1)
    for yy in range(r.top + 4, r.bottom - 2, 4):
        for xx in range(r.left + 4, r.right - 2, 4):
            s.set_at((xx, yy), INK_FAINT)


def stamped_tick(s, cx, cy):
    """A tick pressed with a real nib: doubled stroke, slight overshoot."""
    r = pygame.Rect(0, 0, 17, 17)
    r.center = (cx, cy)
    pygame.draw.rect(s, INK_SOFT, r, 1)
    a = (cx - 6, cy + 1)
    b = (cx - 2, cy + 5)
    c = (cx + 8, cy - 7)
    pygame.draw.lines(s, INK, False, [a, b, c], 3)
    pygame.draw.lines(s, (36, 26, 16), False,
                      [(a[0], a[1] - 1), (b[0], b[1] - 1), (c[0] + 1, c[1] - 1)], 1)


def logged_ring(s, cx, cy, r=13):
    """Ring the flown event glyph — the controller's 'seen and logged' circle."""
    pygame.draw.circle(s, (92, 70, 46), (cx, cy), r, 1)
    pygame.draw.circle(s, (92, 70, 46), (cx + 1, cy), r, 1)


# ── the rubber stamp ─────────────────────────────────────────────────────────

def death_stamp(text):
    f = F(15)
    img = tracked(text, 15, STAMP_RED, 1)
    pad_x, pad_y = 11, 9
    w = img.get_width() + pad_x * 2
    h = img.get_height() + pad_y * 2
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(s, STAMP_RED, pygame.Rect(0, 0, w, h), 3, border_radius=3)
    pygame.draw.rect(s, STAMP_RED, pygame.Rect(5, 5, w - 10, h - 10), 1, border_radius=2)
    s.blit(img, (pad_x, pad_y))

    # Starved-ribbon roughening: multiply the alpha channel with a blotchy mask
    # so the impression is uneven the way a hand-pressed rubber stamp is. The
    # global 214 keeps it inked without letting scarlet own the panel below.
    rng = random.Random(4242)
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    mask.fill((255, 255, 255, 214))
    for _ in range(150):
        rx, ry = rng.randrange(w), rng.randrange(h)
        rr = rng.randrange(1, 4)
        pygame.draw.circle(mask, (255, 255, 255, rng.randrange(40, 140)), (rx, ry), rr)
    for _ in range(4):
        ry = rng.randrange(h)
        pygame.draw.line(mask, (255, 255, 255, rng.randrange(70, 130)),
                         (rng.randrange(0, w // 2), ry), (w, ry), 1)
    s.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    # Large display type only — body text stays axis-aligned so it never smears.
    return pygame.transform.rotozoom(s, 8.0, 1.0)


# ── the strip ────────────────────────────────────────────────────────────────

def rows():
    out = []
    for i, (p0, name) in enumerate(PHASE_BOUNDARIES):
        p1 = PHASE_BOUNDARIES[i + 1][0] if i + 1 < len(PHASE_BOUNDARIES) else 1.0
        out.append((name, p0, p1))
    return out


EVENTS = [
    (THERMAL_START_PHASE, 'geyser', 'GEYSER FIELD', None),
    (0.300, 'lamp', 'GENIE LAMP', LATE_GAME_PILLAR),
    (0.403, 'clown', 'CLOWN GAUNTLET', CLOWN_START_PILLAR),
    (0.430, 'rain', 'STORM FRONT', RAIN_START_PILLAR),
    (SNOW_STORM_CENTER, 'snow', 'SNOW SQUALL', None),
]


def build_strip():
    s = pygame.Surface((STRIP_W, STRIP_H), pygame.SRCALPHA)
    s.fill(PAPER)

    # Stock lighting: sheets catch a little more light at the top edge.
    for y in range(STRIP_H):
        t = y / STRIP_H
        c = (int(PAPER_HI[0] + (PAPER_LO[0] - PAPER_HI[0]) * t),
             int(PAPER_HI[1] + (PAPER_LO[1] - PAPER_HI[1]) * t),
             int(PAPER_HI[2] + (PAPER_LO[2] - PAPER_HI[2]) * t))
        pygame.draw.line(s, c, (0, y), (STRIP_W, y))
    s.blit(grain(STRIP_W, STRIP_H), (0, 0))

    def py(p):
        return p * BODY_H

    # ── colour ribbon: a continuous sample of the real day cycle ─────────────
    # Sky on the wide lane, ground on the narrow one, resampled per scanline so
    # the ribbon IS the palette rather than seven flat swatches.
    for y in range(BODY_H):
        pal = palette_for_phase(y / BODY_H)
        pygame.draw.line(s, pal['sky_mid'], (CHIP_X0, y), (CHIP_X0 + 8, y))
        pygame.draw.line(s, pal['ground_mid'], (CHIP_X0 + 9, y), (CHIP_X1 - 1, y))
    pygame.draw.rect(s, INK_SOFT, pygame.Rect(CHIP_X0, 0, CHIP_X1 - CHIP_X0, BODY_H), 1)
    pygame.draw.line(s, (0, 0, 0, 70), (CHIP_X0 + 8, 0), (CHIP_X0 + 8, BODY_H))

    # ── ruled form: column rails + row rules ────────────────────────────────
    for x in (GUT_X1, TICK_RULE):
        pygame.draw.line(s, INK_FAINT, (x, 0), (x, BODY_H))
    pygame.draw.rect(s, INK_SOFT, pygame.Rect(4, 0, STRIP_W - 8, BODY_H), 1)

    perf_y = int(py(DEATH_PHASE))
    stamp = death_stamp('ENDED HERE · PILLAR %d' % DEATH_PILLAR)
    stamp_top = perf_y - stamp.get_height() // 2
    stamp_bot = perf_y + stamp.get_height() // 2

    rr = rows()
    header_bot = {}
    for name, p0, p1 in rr:
        y0, y1 = py(p0), py(p1)
        if p0 > 0:
            pygame.draw.line(s, INK_SOFT, (4, int(y0)), (STRIP_W - 4, int(y0)), 1)
            pygame.draw.line(s, (238, 224, 200), (4, int(y0) + 1), (STRIP_W - 4, int(y0) + 1), 1)

        # DAY's marks live in the flown sliver above the perforation; every other
        # row centres in its box.
        mid = (y0 + min(y1, perf_y)) / 2 if p0 == 0.0 else (y0 + y1) / 2

        # Name and duration share one header line with a dotted leader between —
        # the second line stays free for the row's event codes.
        label = tracked(name, 14, INK, 1)
        ty = int(y0) + 5
        s.blit(label, (FIELD_X0, ty))
        dur = tracked('%d SEC' % int((p1 - p0) * CYCLE_SECONDS), 9, INK_SOFT, 1)
        dx = TICK_RULE - 6 - dur.get_width()
        s.blit(dur, (dx, ty + 5))
        dotted_leader(s, FIELD_X0 + label.get_width() + 6, dx - 5,
                      ty + label.get_height() - 6, INK_FAINT)
        header_bot[name] = ty + label.get_height()

        if p0 == 0.0:
            stamped_tick(s, TICK_CX, int(mid))
        else:
            empty_box(s, TICK_CX, int(mid))

    # ── event codes in the gutter, at their true phases ─────────────────────
    gut_cx = (GUT_X0 + GUT_X1) // 2
    used = {}
    for ph, kind, label, pillar in EVENTS:
        y = py(ph)
        row = next(r for r in rr if r[1] <= ph < r[2] or (ph >= 1.0 and r[2] == 1.0))
        # Snow lands a hair past the PREDAWN/SUNRISE rule; nudge the glyph clear
        # of the rule while it still belongs to the predawn squall.
        if kind == 'snow':
            row = rr[-2]
            gy = py(row[2]) - 9
        else:
            gy = y
        # Clown and storm sit 11 px apart — stagger across the gutter so the two
        # marks never read as one blob.
        gdx = -6 if kind == 'clown' else (6 if kind == 'rain' else 0)
        GLYPHS[kind](s, int(gut_cx + gdx), int(gy))
        if kind == 'geyser':
            logged_ring(s, int(gut_cx + gdx), int(gy))

        txt = label if pillar is None else '%s · P%d' % (label, pillar)
        img = tracked(txt, 9, INK, 1)
        ih = img.get_height()
        tx = TICK_RULE - 6 - img.get_width()

        # Keep the caption out of the row header and off the stamp, and stack
        # captions that share a row. The glyph holds the true phase; the caption
        # only has to point at it.
        ly = gy
        floor = header_bot[row[0]] + ih // 2 + 3
        ly = max(ly, floor)
        ly = max(ly, used.get(row[0], 0) + ih + 2)
        if stamp_top - ih < ly < stamp_bot:
            ly = min(stamp_top - ih // 2 - 4, max(floor, stamp_top - ih // 2 - 4))
        ly = min(ly, py(row[2]) - ih // 2 - 3)
        used[row[0]] = ly
        s.blit(img, (tx, int(ly) - ih // 2))

        # Dog-legged leader — the glyph stays on its phase even when the caption
        # has to step aside.
        kx = GUT_X1 + 12
        dotted_leader(s, GUT_X1 + 5, kx, int(gy), INK_FAINT)
        if abs(ly - gy) > 2:
            for yy in range(int(min(ly, gy)), int(max(ly, gy)), 3):
                s.set_at((kx, yy), INK_FAINT)
        dotted_leader(s, kx, tx - 4, int(ly), INK_FAINT)

    # ── flown region: handled paper, above the perforation ──────────────────
    wash = pygame.Surface((STRIP_W - 8, perf_y), pygame.SRCALPHA)
    wash.fill((146, 116, 74, 26))
    pygame.draw.rect(wash, (128, 98, 60, 22), pygame.Rect(0, perf_y - 14, STRIP_W - 8, 14))
    s.blit(wash, (4, 0))

    # ── perforation (a fold-line, not a tear: the strip continues) ──────────
    dashed_h(s, 4, STRIP_W - 4, perf_y, PERF_INK, on=5, off=4, width=1)
    dashed_h(s, 4, STRIP_W - 4, perf_y + 1, (240, 228, 206), on=5, off=4, width=1)
    for ex in (2, STRIP_W - 3):
        pygame.draw.circle(s, PERF_INK, (ex, perf_y), 2, 1)

    # Ink smudge where a thumb dragged across the fresh line.
    sm = pygame.Surface((90, 26), pygame.SRCALPHA)
    rng = random.Random(77)
    for _ in range(9):
        cx = rng.randrange(10, 80)
        cy = rng.randrange(6, 20)
        pygame.draw.ellipse(sm, (74, 54, 34, rng.randrange(28, 66)),
                            pygame.Rect(cx, cy, rng.randrange(8, 22), rng.randrange(3, 7)))
    sm = pygame.transform.smoothscale(pygame.transform.smoothscale(sm, (30, 9)), (90, 26))
    s.blit(sm, (96, perf_y - 18))

    # ── footer remarks ──────────────────────────────────────────────────────
    fy = BODY_H
    pygame.draw.line(s, INK_SOFT, (4, fy), (STRIP_W - 4, fy), 1)
    pygame.draw.line(s, INK_FAINT, (4, fy + 3), (STRIP_W - 4, fy + 3), 1)
    pygame.draw.rect(s, INK_SOFT, pygame.Rect(4, fy, STRIP_W - 8, STRIP_H - fy - 4), 1)

    s.blit(tracked('REMARKS', 8, INK_SOFT, 2), (10, fy + 8))
    lines = ['STILL AHEAD: GENIE LAMP AT PILLAR %d ·' % LATE_GAME_PILLAR,
             'CLOWN GAUNTLET AT PILLAR %d · STORM AT %d' % (CLOWN_START_PILLAR,
                                                            RAIN_START_PILLAR)]
    ly = fy + 18
    for ln in lines:
        img = dotmatrix(ln, 9, INK, 1)
        if img.get_width() > STRIP_W - 24:
            img = dotmatrix(ln, 9, INK, 0)
        s.blit(img, (11, ly))
        ly += 12

    serial = tracked('SB-1', 7, INK_FAINT, 1)
    s.blit(serial, (STRIP_W - 10 - serial.get_width(), fy + 8))

    # ── stamp + stock finish ────────────────────────────────────────────────
    s.blit(stamp, (STRIP_W // 2 - stamp.get_width() // 2, stamp_top))

    s.blit(vignette(STRIP_W, STRIP_H), (0, 0))
    pygame.draw.rect(s, (188, 166, 134), pygame.Rect(0, 0, STRIP_W, STRIP_H), 1,
                     border_radius=3)

    # Rounded corners via an alpha-only multiply — keeps the paper a cut sheet.
    mask = pygame.Surface((STRIP_W, STRIP_H), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     pygame.Rect(0, 0, STRIP_W, STRIP_H), 0, border_radius=3)
    s.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return s


# ── screen ───────────────────────────────────────────────────────────────────

def build_screen():
    scr = pygame.Surface((W, H))
    scr.fill(SCREEN_BG)

    # A faint pool of light behind the document so the cream doesn't float on
    # dead black.
    glow = pygame.Surface((64, 64), pygame.SRCALPHA)
    for i in range(32, 0, -1):
        pygame.draw.circle(glow, (30, 32, 56, 5), (32, 32), i)
    scr.blit(pygame.transform.smoothscale(glow, (420, 560)), (-30, 40))

    title = tracked('FLIGHT LOG', 22, HEAD_CREAM, 3)
    scr.blit(title, (W // 2 - title.get_width() // 2, 22))
    stats = tracked('DAY %d  ·  PILLAR %d  ·  0:%02d' % (DAY_NUM, DEATH_PILLAR, TIME_ALIVE),
                    11, HEAD_MUTED, 1)
    scr.blit(stats, (W // 2 - stats.get_width() // 2, 54))
    pygame.draw.line(scr, (40, 42, 68), (W // 2 - 70, 74), (W // 2 + 70, 74), 1)

    strip = build_strip()
    rot = pygame.transform.rotozoom(strip, PAPER_TILT, 1.0)
    cx, cy = STRIP_X + STRIP_W // 2, STRIP_Y + STRIP_H // 2
    rect = rot.get_rect(center=(cx, cy))

    shadow = pygame.mask.from_surface(rot).to_surface(
        setcolor=(0, 0, 0, 80), unsetcolor=(0, 0, 0, 0))
    soft = pygame.transform.smoothscale(
        pygame.transform.smoothscale(shadow, (rect.w // 4, rect.h // 4)), (rect.w, rect.h))
    scr.blit(soft, (rect.x + 4, rect.y + 5))
    scr.blit(shadow, (rect.x + 3, rect.y + 3))
    scr.blit(rot, rect.topleft)

    pill = pygame.Rect(0, 0, 104, 32)
    pill.center = (W // 2, 598)
    pygame.draw.rect(scr, (22, 24, 44), pill, 0, border_radius=16)
    pygame.draw.rect(scr, (86, 92, 128), pill, 1, border_radius=16)
    bt = tracked('BACK', 13, (222, 226, 244), 2)
    scr.blit(bt, (pill.centerx - bt.get_width() // 2, pill.centery - bt.get_height() // 2))
    return scr


def build_details(scr):
    """2x crops of the load-bearing areas, for review at reading size."""
    crops = [('PERFORATION + DEATH STAMP', pygame.Rect(24, 128, 316, 108)),
             ('EVENT GUTTER  CLOWN / STORM STAGGER', pygame.Rect(24, 232, 260, 96)),
             ('FOOTER REMARKS  (DOT-MATRIX)', pygame.Rect(24, 500, 316, 78))]
    pad = 14
    zw = max(c.w for _, c in crops) * 2
    zh = sum(c.h * 2 + 26 for _, c in crops) + pad * (len(crops) + 1)
    sheet = pygame.Surface((zw + pad * 2, zh))
    sheet.fill((16, 16, 28))
    y = pad
    for label, r in crops:
        img = pygame.transform.scale(scr.subsurface(r).copy(), (r.w * 2, r.h * 2))
        lab = tracked(label, 11, (200, 204, 226), 2)
        sheet.blit(lab, (pad, y))
        y += 20
        sheet.blit(img, (pad, y))
        pygame.draw.rect(sheet, (60, 62, 88), pygame.Rect(pad, y, r.w * 2, r.h * 2), 1)
        y += r.h * 2 + pad
    return sheet


def main():
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           'docs', 'flight_log_progress', 'flight_strip')
    os.makedirs(out_dir, exist_ok=True)
    scr = build_screen()
    pygame.image.save(scr, os.path.join(out_dir, 'round_1.png'))
    pygame.image.save(build_details(scr), os.path.join(out_dir, 'round_1_details.png'))
    print('wrote', out_dir)


if __name__ == '__main__':
    main()
