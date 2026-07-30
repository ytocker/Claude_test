"""Flight Log concept `strata_core` — review sheet renderer.

A run is drawn as a geological core sample read BOTTOM-UP: the base of the
core is pillar 0 (launch), the top is pillar 175 (a full biome day). The
rock's colour IS the biome palette at that depth, so the sample reads
cyan -> amber -> rose -> lavender -> night-blue -> purple -> peach as the eye
climbs. Where the run ended the record is physically broken: a red fracture
with a 3 px fault throw. Everything above it is territory the player never
flew, so it is desaturated and hazed — never darkened, because dimming would
collide with the palette's own night and destroy the whole premise.

Event zones sit on two spatial registers so they can never be confused:
gameplay on the LEFT face of the core, weather on the RIGHT face.

Offline tool. Writes a labelled sheet under docs/; ships nothing to the game.
"""
from __future__ import annotations

import math
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((8, 8))

from game.biome import PHASE_BOUNDARIES, palette_for_phase  # noqa: E402
from game.config import (CLOWN_SLOT_PILLARS, CLOWN_START_PILLAR,  # noqa: E402
                         COIN_RUSH_INTERVAL, CYCLE_FINALE_PHASE_HI)
from game.draw import NEAR_BLACK, UI_CREAM, lerp_color  # noqa: E402
from game.weather import (RAIN_DRIZZLE_START, RAIN_STORM_PEAK,  # noqa: E402
                          RAIN_STORM_WIDTH, SNOW_STORM_CENTER,
                          SNOW_STORM_WIDTH, THERMAL_END_PHASE,
                          THERMAL_START_PHASE, _phase_for_pillar,
                          _SNOW_LOWER_EDGE)

# Mirrored from hud.py rather than imported: game.hud drags the whole
# entity/parrot stack in and this tool only needs three swatches.
_GOLD_BRIGHT = (240, 192, 64)
_GOLD_MUTED = (200, 160, 50)
_RED_FAULT = (235, 55, 45)

W, H = 360, 640

# ── core geometry ───────────────────────────────────────────────────────────
CORE_X0, CORE_X1 = 80, 280
CORE_W = CORE_X1 - CORE_X0
CORE_Y0, CORE_Y1 = 110, 590          # top = day complete, bottom = launch
SPAN = CORE_Y1 - CORE_Y0
DAY_PILLARS = 175
THROW = 3                            # fault offset of the unflown block
BED_SPACING = 8                      # bedding-plane pitch down the core

# The run being logged.
RUN_PILLARS, RUN_SCORE, RUN_DAY, RUN_SECONDS = 25, 25, 1, 47

# Most runs die inside the first fifth of a day. On a linear phase axis that
# squashes everything the player actually lived into a sliver at the bottom,
# so the axis is lifted by phase**0.75: early phase gets more pixels, the tail
# compresses, and the median run still occupies readable rock.
AXIS_LIFT = 0.75


def t_for_phase(p: float) -> float:
    return max(0.0, min(1.0, p)) ** AXIS_LIFT


def y_for_phase(p: float) -> float:
    return CORE_Y1 - t_for_phase(p) * SPAN


def phase_for_y(y: float) -> float:
    t = max(0.0, min(1.0, (CORE_Y1 - y) / SPAN))
    return t ** (1.0 / AXIS_LIFT)


def y_for_pillar(p: int) -> float:
    return y_for_phase(_phase_for_pillar(p))


# Event windows read from the live game rather than hand-copied, so the log
# can never drift from where the player actually met the storm.
CLOWN_LO = _phase_for_pillar(CLOWN_START_PILLAR)
CLOWN_HI = _phase_for_pillar(CLOWN_START_PILLAR + CLOWN_SLOT_PILLARS)
COIN_RUSH_PILLARS = list(range(COIN_RUSH_INTERVAL, DAY_PILLARS + 1,
                               COIN_RUSH_INTERVAL))
FINALE_LO, FINALE_HI = CYCLE_FINALE_PHASE_HI, 1.0
RAIN_LO, RAIN_HI = RAIN_DRIZZLE_START, RAIN_STORM_PEAK + RAIN_STORM_WIDTH
SNOW_LO, SNOW_HI = _SNOW_LOWER_EDGE, SNOW_STORM_CENTER + SNOW_STORM_WIDTH / 2
THERM_LO, THERM_HI = THERMAL_START_PHASE, THERMAL_END_PHASE


# ── colour helpers ──────────────────────────────────────────────────────────

def clamp8(v: float) -> int:
    return 0 if v < 0 else (255 if v > 255 else int(v))


def shade(c, f: float):
    return (clamp8(c[0] * f), clamp8(c[1] * f), clamp8(c[2] * f))


def lum(c) -> float:
    return c[0] * 0.299 + c[1] * 0.587 + c[2] * 0.114


_FONT_PATH = os.path.join(ROOT, "game", "assets", "LiberationSans-Bold.ttf")
_fonts: dict[int, pygame.font.Font] = {}


def font(size: int) -> pygame.font.Font:
    f = _fonts.get(size)
    if f is None:
        f = pygame.font.Font(_FONT_PATH, size)
        _fonts[size] = f
    return f


def caps_width(text: str, size: int, tracking: int = 1) -> int:
    f = font(size)
    text = text.upper()
    return sum(f.size(ch)[0] for ch in text) + tracking * max(0, len(text) - 1)


def fit_tracking(text: str, size: int, max_w: int) -> int:
    """Tracking is what makes 7-8 px caps legible, but not at the cost of
    running out of the gutter — the long labels give it up instead of
    shrinking to a size that stops reading at all."""
    return 1 if caps_width(text, size, 1) <= max_w else 0


def caps(surf, text, x, y, size, color, alpha=255, tracking=1, right=False):
    text = text.upper()
    f = font(size)
    w = caps_width(text, size, tracking)
    cx = x - w if right else x
    for ch in text:
        img = f.render(ch, True, color)
        if alpha < 255:
            img.set_alpha(alpha)
        surf.blit(img, (cx, y))
        cx += f.size(ch)[0] + tracking
    return pygame.Rect(x - w if right else x, y, w, f.get_height())


def dotted(surf, x0, x1, y, color, alpha=110):
    if x1 <= x0:
        return
    line = pygame.Surface((x1 - x0, 1), pygame.SRCALPHA)
    for i in range(x1 - x0):
        if i % 3 != 2:
            line.set_at((i, 0), (*color, alpha))
    surf.blit(line, (x0, y))


def dodge(y: float, blocked: list[float], gap: int, lo: float, hi: float,
          up: int = 0, down: int = 0) -> int:
    """Nudge a label off any row already claimed by another annotation while
    keeping it inside the band it points at. `up`/`down` describe how far the
    label's own plate reaches beyond its leader row, so a tall two-line
    callout clears its neighbours by its real extent, not by its anchor."""
    def clear(c):
        return all(not (c - up - gap < b < c + down + gap) for b in blocked)
    for step in range(0, 60, 3):
        for cand in (y + step, y - step):
            if lo <= cand <= hi and clear(cand):
                return int(cand)
    return int(y)


# ── per-row rock palette ────────────────────────────────────────────────────
# Each row of the core is one moment of the biome day. Stone and sky keys are
# blended 50/50: pure stone_* barely moves across the cycle (sandstone stays
# sandstone) and pure sky_* loses all rock character. The half-mix keeps the
# material reading as rock while making the time-of-day unmistakable.

def row_tones(y: float):
    pal = palette_for_phase(phase_for_y(y))
    body = lerp_color(pal["stone_mid"], pal["sky_mid"], 0.5)
    dark = lerp_color(pal["stone_dark"], pal["sky_top"], 0.5)
    lit = lerp_color(pal["stone_light"], pal["sky_bot"], 0.5)
    return body, dark, lit, pal["stone_accent"]


# Cylindrical cross-core shading. The stops hold the 18% shadow / 22% lit
# faces but ramp between them, so the sample reads as a round column rather
# than three flat stripes.
_SHADE_STOPS = (0.00, 0.14, 0.26, 0.62, 0.80, 1.00)


def _column_mix(u: float):
    for i in range(len(_SHADE_STOPS) - 1):
        a, b = _SHADE_STOPS[i], _SHADE_STOPS[i + 1]
        if u <= b:
            return i, (u - a) / (b - a) if b > a else 0.0
    return len(_SHADE_STOPS) - 2, 1.0


_COL_MIX = [_column_mix(x / (CORE_W - 1)) for x in range(CORE_W)]

# Vertical mineral fabric: a smoothed per-column bias so the grain runs down
# the core the way a real fabric does instead of looking like TV static.
_rnd_fabric = random.Random(1907)
_raw = [_rnd_fabric.uniform(-1.0, 1.0) for _ in range(CORE_W)]
_FABRIC = [sum(_raw[max(0, i - 2):i + 3]) / len(_raw[max(0, i - 2):i + 3])
           for i in range(CORE_W)]

SPEC_X = 272 - CORE_X0                # 1 px specular down the lit face
FACE_L1 = 120 - CORE_X0               # gameplay register ends here
FACE_R0 = 240 - CORE_X0               # weather register starts here


def build_core_body() -> pygame.Surface:
    surf = pygame.Surface((CORE_W, SPAN), pygame.SRCALPHA)
    rnd = random.Random(311)
    for row in range(SPAN):
        body, dark, lit, _ = row_tones(CORE_Y0 + row)
        stops = (shade(dark, 0.78), dark, body,
                 lerp_color(body, lit, 0.22), lerp_color(body, lit, 0.30), lit)
        for x in range(CORE_W):
            i, t = _COL_MIX[x]
            a, b = stops[i], stops[i + 1]
            g = rnd.gauss(0.0, 4.2) + _FABRIC[x] * 5.0
            surf.set_at((x, row), (
                clamp8(a[0] + (b[0] - a[0]) * t + g),
                clamp8(a[1] + (b[1] - a[1]) * t + g),
                clamp8(a[2] + (b[2] - a[2]) * t + g), 255))
        spec = lerp_color(lit, (255, 255, 255), 0.42)
        surf.set_at((SPEC_X, row), (*spec, 255))
    return surf


def px_scale(surf, x, y, f: float, add=0):
    if 0 <= x < surf.get_width() and 0 <= y < surf.get_height():
        c = surf.get_at((x, y))
        surf.set_at((x, y), (clamp8(c[0] * f + add), clamp8(c[1] * f + add),
                             clamp8(c[2] * f + add), c[3]))


def draw_laminations(surf):
    """Bedding planes every ~8 px, each with a bounded random walk of lateral
    wobble, so the layering looks deposited rather than ruled."""
    rnd = random.Random(42)
    k, y = 0, CORE_Y1 - 2
    while y > CORE_Y0 + 2:
        row = int(y) - CORE_Y0
        strong, relief = (k % 3 == 0), (k % 2 == 0)
        f = 0.63 if strong else 0.78
        dy = 0.0
        gap_at = rnd.randint(0, CORE_W - 1) if rnd.random() < 0.35 else -1
        for x in range(CORE_W):
            dy = max(-2.0, min(2.0, dy + rnd.uniform(-0.55, 0.55)))
            if gap_at >= 0 and abs(x - gap_at) < 14:
                continue
            yy = row + int(round(dy))
            px_scale(surf, x, yy, f)
            if strong:
                px_scale(surf, x, yy + 1, 0.72)
            if relief:
                px_scale(surf, x, yy - 1, 1.0, add=9)
        for _ in range(rnd.randint(0, 3)):     # coarse clasts riding the bed
            px_scale(surf, rnd.randint(2, CORE_W - 3), row - rnd.randint(0, 2),
                     1.0, add=rnd.randint(8, 22))
        y -= BED_SPACING
        k += 1


def draw_phase_planes(surf):
    """Each named time-of-day starts on a marker bed — the 2 px accent plane
    is what the gutter label points at."""
    for frac, _name in PHASE_BOUNDARIES:
        if frac <= 0.0:
            continue
        y = y_for_phase(frac)
        row = int(round(y)) - CORE_Y0
        if not (2 <= row < SPAN - 2):
            continue
        accent = row_tones(y)[3]
        rnd = random.Random(int(frac * 10000))
        dy = 0.0
        for x in range(CORE_W):
            dy = max(-1.5, min(1.5, dy + rnd.uniform(-0.4, 0.4)))
            yy = row + int(round(dy))
            for o, f in ((0, 1.0), (1, 0.86)):
                if 0 <= yy + o < SPAN:
                    surf.set_at((x, yy + o), (*shade(accent, f), 255))
            px_scale(surf, x, yy + 2, 0.58)


# ── LEFT FACE: gameplay register ────────────────────────────────────────────

def draw_clown_inclusions(surf):
    """Violet euhedral inclusions in a trail — the clown gauntlet reads as a
    run of hard angular crystals the flight had to thread."""
    rnd = random.Random(514)
    y_lo, y_hi = y_for_phase(CLOWN_HI), y_for_phase(CLOWN_LO)
    for i in range(5):
        t = (i + 0.5) / 5.0
        cy = y_hi + (y_lo - y_hi) * t + rnd.uniform(-3, 3) - CORE_Y0
        cx = 22 + rnd.uniform(-9, 11)
        r = rnd.uniform(4.2, 7.6)
        pts = []
        for k in range(5):
            ang = -math.pi / 2 + k * (2 * math.pi / 5) + rnd.uniform(-0.34, 0.34)
            rr = r * rnd.uniform(0.72, 1.24)
            pts.append((cx + math.cos(ang) * rr, cy + math.sin(ang) * rr))
        pygame.draw.polygon(surf, (34, 16, 62), [(p[0] + 1, p[1] + 1) for p in pts])
        pygame.draw.polygon(surf, (90, 50, 160), pts)
        facet = [(cx + (p[0] - cx) * 0.58 - 1.1, cy + (p[1] - cy) * 0.58 - 1.3)
                 for p in pts[:3]]
        pygame.draw.polygon(surf, (142, 96, 216), facet)
        pygame.draw.line(surf, (250, 246, 255), pts[0], pts[1], 1)
        pygame.draw.line(surf, (208, 190, 255), pts[4], pts[0], 1)


def pyrite_slots():
    """(pillar, core-local x, core-local row) per coin rush. Sulphide cubes
    grow ON the bedding, so each is snapped to its nearest lamination — which
    also stops the eleven of them reading as a ruled dotted line."""
    rnd = random.Random(88)
    out, base = [], CORE_Y1 - 2 - CORE_Y0
    for p in COIN_RUSH_PILLARS:
        row = int(round(y_for_pillar(p))) - CORE_Y0
        k = int(round((base - row) / BED_SPACING))
        out.append((p, 13 + rnd.randint(-4, 8), base - k * BED_SPACING - 3))
    return out


def _cube(surf, x, row):
    pygame.draw.rect(surf, (18, 12, 8), (x + 1, row + 1, 6, 6))
    pygame.draw.rect(surf, _GOLD_BRIGHT, (x, row, 6, 6))
    pygame.draw.line(surf, (255, 236, 176), (x, row), (x + 5, row))
    pygame.draw.line(surf, (255, 236, 176), (x, row), (x, row + 5))
    pygame.draw.line(surf, (118, 84, 20), (x, row + 5), (x + 5, row + 5))
    pygame.draw.line(surf, (118, 84, 20), (x + 5, row), (x + 5, row + 5))
    surf.set_at((x + 1, row + 1), (255, 250, 222, 255))


def draw_pyrite_cubes(surf):
    for _p, x, row in pyrite_slots():
        _cube(surf, x, row)


def draw_finale_vein(surf):
    """The day-end finale is a continuous rush, so it stops being separate
    cubes and becomes a solid gold stringer running out the top of the core."""
    y_bot = y_for_phase(FINALE_LO) - CORE_Y0
    y_top = 0
    rnd = random.Random(96)
    pts, x = [], 17.0
    for row in range(int(y_top), int(y_bot) + 1, 3):
        x = max(9.0, min(28.0, x + rnd.uniform(-1.6, 1.6)))
        pts.append((x, row))
    if len(pts) > 1:
        pygame.draw.lines(surf, (110, 78, 18), False,
                          [(p[0] + 1, p[1] + 1) for p in pts], 4)
        pygame.draw.lines(surf, _GOLD_BRIGHT, False, pts, 3)
        pygame.draw.lines(surf, (255, 236, 176), False,
                          [(p[0] - 1, p[1]) for p in pts], 1)
    for p in pts[1::5]:
        _cube(surf, int(p[0]) - 2, int(p[1]))


# ── RIGHT FACE: weather register ────────────────────────────────────────────

def draw_rain_seep(surf):
    """Percolation stain: water enters at the storm band and runs DOWN, so
    the drips hang below the zone instead of floating inside it."""
    r0 = int(y_for_phase(RAIN_HI)) - CORE_Y0
    r1 = int(y_for_phase(RAIN_LO)) - CORE_Y0
    rnd = random.Random(613)
    stain = pygame.Surface((CORE_W, SPAN), pygame.SRCALPHA)
    edge = float(FACE_R0)
    for row in range(max(0, r0), min(SPAN, r1 + 1)):
        edge = max(FACE_R0 - 4, min(FACE_R0 + 14, edge + rnd.uniform(-1.3, 1.3)))
        fade = min(1.0, min(row - r0, r1 - row) / 12.0)
        a = int(60 * (0.35 + 0.65 * fade))
        pygame.draw.line(stain, (86, 126, 184, a), (int(edge), row),
                         (CORE_W - 1, row))
    for k in range(3):
        dx = FACE_R0 + 6 + k * 11 + rnd.randint(-2, 2)
        length = rnd.randint(22, 40)
        for j in range(length):
            a = int(66 * (1.0 - j / length) ** 1.4)
            wdt = 2 if j < length * 0.45 else 1
            pygame.draw.line(stain, (86, 126, 184, a), (dx, r1 + j),
                             (dx + wdt - 1, r1 + j))
    surf.blit(stain, (0, 0))


def draw_snow_frost(surf):
    """Micro-crystal frost crust, clustered and denser toward the exposed
    right edge where the squall actually hit the rock."""
    r0 = max(0, int(y_for_phase(SNOW_HI)) - CORE_Y0)
    r1 = min(SPAN - 1, int(y_for_phase(SNOW_LO)) - CORE_Y0)
    rnd = random.Random(2210)
    crust = pygame.Surface((CORE_W, SPAN), pygame.SRCALPHA)
    for row in range(r0, r1 + 1):
        fade = min(1.0, (r1 - row) / 26.0)
        pygame.draw.line(crust, (232, 244, 255, int(26 * fade)),
                         (FACE_R0 - 2, row), (CORE_W - 1, row))
    for _ in range(9):
        cx = rnd.randint(FACE_R0, CORE_W - 3)
        cy = rnd.randint(r0 + 2, max(r0 + 3, r1 - 2))
        for _ in range(rnd.randint(7, 13)):
            px, py = cx + rnd.randint(-7, 7), cy + rnd.randint(-7, 7)
            if not (FACE_R0 - 3 <= px < CORE_W and r0 <= py <= r1):
                continue
            if rnd.random() < 0.45:
                pygame.draw.rect(crust, (250, 253, 255, 180), (px, py, 2, 1))
            else:
                pygame.draw.circle(crust, (238, 248, 255, 180), (px, py), 1)
    surf.blit(crust, (0, 0))


def draw_thermal_vesicles(surf):
    """Gas vesicles frozen into the rock — the morning thermal as bubbles
    that rose through the melt."""
    y_top, y_bot = y_for_phase(THERM_HI), y_for_phase(THERM_LO)
    rnd = random.Random(404)
    bub = pygame.Surface((CORE_W, SPAN), pygame.SRCALPHA)
    for _ in range(10):
        cx = rnd.randint(FACE_R0 + 1, CORE_W - 5)
        cy = int(rnd.uniform(y_top + 5, y_bot - 5)) - CORE_Y0
        r = rnd.randint(3, 6)
        pygame.draw.circle(bub, (128, 78, 26, 120), (cx, cy), r)
        pygame.draw.circle(bub, (240, 178, 78, 120), (cx, cy), max(1, r - 1))
        pygame.draw.circle(bub, (255, 224, 160, 130),
                           (cx - max(1, r // 3), cy - max(1, r // 3)), 1)
    surf.blit(bub, (0, 0))


# ── death fracture ──────────────────────────────────────────────────────────

def fracture_points():
    y0 = y_for_pillar(RUN_PILLARS)
    rnd = random.Random(7)
    return [(CORE_X0 + i * (CORE_W / 10.0),
             y0 + (0.0 if i in (0, 10) else rnd.uniform(-4.0, 4.0)))
            for i in range(11)]


def fracture_column_y(pts):
    out = []
    for x in range(CORE_W):
        gx = CORE_X0 + x
        for i in range(len(pts) - 1):
            x0, y0 = pts[i]
            x1, y1 = pts[i + 1]
            if x0 <= gx <= x1:
                t = (gx - x0) / (x1 - x0) if x1 > x0 else 0.0
                out.append(y0 + (y1 - y0) * t)
                break
        else:
            out.append(pts[-1][1])
    return out


def split_blocks(core, col_y):
    """Cut the core into the flown block and the unflown block."""
    lower, upper = core.copy(), core.copy()
    for x in range(CORE_W):
        cut = max(0, min(SPAN, int(round(col_y[x])) - CORE_Y0))
        lower.fill((0, 0, 0, 0), (x, 0, 1, cut))
        upper.fill((0, 0, 0, 0), (x, cut, 1, SPAN - cut))
    return lower, upper


def veil_unflown(block, col_y):
    """Unflown ground is pulled toward grey and lifted with white haze, never
    darkened — dimming would collide with the palette's own night, and the
    whole premise of the core is that colour means time of day. The
    desaturation ramps with distance so the rows just past the fracture still
    show what the run was about to fly into."""
    depth = max(1.0, sum(col_y) / len(col_y) - CORE_Y0)
    for x in range(CORE_W):
        cut = max(0, min(SPAN, int(round(col_y[x])) - CORE_Y0))
        for row in range(cut):
            c = block.get_at((x, row))
            if c[3] == 0:
                continue
            ramp = min(1.0, (cut - row) / depth) ** 0.85
            chroma = 1.0 - 0.60 * ramp
            haze = (8.0 + 22.0 * ramp) / 255.0
            g = lum(c)
            out = []
            for ch in (c[0], c[1], c[2]):
                v = g + (ch - g) * chroma
                out.append(clamp8(v + (255 - v) * haze))
            block.set_at((x, row), (*out, c[3]))


def draw_fracture(surf, pts):
    """The white core line is what survives a greyscale check; the red is
    atmosphere around it."""
    fx = pygame.Surface((W, H), pygame.SRCALPHA)
    for wdt, alpha in ((13, 40), (9, 80), (5, 180)):
        pygame.draw.lines(fx, (*_RED_FAULT, alpha), False, pts, wdt)
        for p in pts:
            pygame.draw.circle(fx, (*_RED_FAULT, alpha),
                               (int(p[0]), int(p[1])), wdt // 2)
    surf.blit(fx, (0, 0))
    pygame.draw.lines(surf, NEAR_BLACK, False, [(x, y - 3) for x, y in pts], 1)
    pygame.draw.lines(surf, (255, 255, 255), False, pts, 2)


# ── screen ──────────────────────────────────────────────────────────────────

def draw_header(surf):
    caps(surf, "FLIGHT LOG", 14, 22, 18, _GOLD_BRIGHT, tracking=2)
    caps(surf, f"DAY {RUN_DAY}    CORE LOG    {RUN_SECONDS // 60}:"
               f"{RUN_SECONDS % 60:02d}", 15, 48, 9, (146, 144, 168))
    f = font(44)
    img = f.render(str(RUN_SCORE), True, UI_CREAM)
    rect = img.get_rect(topright=(346, 18))
    sh = f.render(str(RUN_SCORE), True, (0, 0, 0))
    sh.set_alpha(150)
    surf.blit(sh, (rect.x + 2, rect.y + 3))
    surf.blit(img, rect.topleft)
    caps(surf, "PILLARS", 346, rect.bottom - 4, 8, _GOLD_MUTED, alpha=225,
         tracking=2, right=True)
    rule = pygame.Surface((332, 1), pygame.SRCALPHA)
    for i in range(332):
        rule.set_at((i, 0), (*_GOLD_MUTED,
                             min(255, int(120 * (1 - i / 331.0) ** 0.7) + 18)))
    surf.blit(rule, (14, 92))


def draw_left_gutter(surf, y_frac):
    """Depth ruler plus the gameplay register's callouts. Ruler numbers hug
    the core and callouts start at the far edge, so the two never queue up in
    the same column."""
    ruler_rows = []
    for p in range(25, DAY_PILLARS + 1, 25):
        y = int(round(y_for_pillar(p)))
        flown = p <= RUN_PILLARS
        col = UI_CREAM if flown else (138, 138, 158)
        a = 235 if flown else 175
        tick = pygame.Surface((8, 1), pygame.SRCALPHA)
        tick.fill((*col, a))
        surf.blit(tick, (70, y))
        # The last tick is already named by the core's own DAY-COMPLETE cap,
        # so repeating "175" here would just crowd the busiest corner.
        if p < DAY_PILLARS:
            caps(surf, str(p), 66, y - 5, 8, col, alpha=a, right=True)
            ruler_rows.append(y)

    def callout(lines, y_target, swatch, lo, hi):
        y = dodge(y_target, ruler_rows, 6, lo, hi,
                  up=3 + len(lines) * 10, down=6)
        wid = max(caps_width(l, 7, fit_tracking(l, 7, 41)) for l in lines)
        top = y - 3 - len(lines) * 10
        plate = pygame.Rect(13, top - 2, wid + 4, len(lines) * 10 + 2)
        pl = pygame.Surface(plate.size, pygame.SRCALPHA)
        pl.fill((*NEAR_BLACK, 185))
        surf.blit(pl, plate.topleft)
        for i, line in enumerate(lines):
            caps(surf, line, 15, top + i * 10, 7, UI_CREAM, alpha=235,
                 tracking=fit_tracking(line, 7, 41))
        pygame.draw.rect(surf, swatch, (7, y - 2, 4, 4))
        dotted(surf, 13, 78, y, swatch, 130)

    callout(["CLOWN", "GAUNTLET"],
            (y_for_phase(CLOWN_LO) + y_for_phase(CLOWN_HI)) / 2,
            (128, 82, 205), y_for_phase(CLOWN_HI) + 6,
            y_for_phase(CLOWN_LO) - 6)
    rush_y = CORE_Y0 + pyrite_slots()[0][2] + 3
    callout(["COIN RUSH", "x11"], rush_y, _GOLD_BRIGHT, rush_y - 6, rush_y + 24)
    callout(["FINALE RUSH"], y_for_phase(FINALE_LO) - 4, (255, 236, 176),
            CORE_Y0 + 12, y_for_phase(FINALE_LO))


def draw_right_gutter(surf, y_frac):
    """Phase planes get named here. The weather register hangs off the same
    gutter but right-aligned behind a colour swatch, so the two annotation
    families never read as one list."""
    phase_rows = []
    for frac, name in PHASE_BOUNDARIES:
        y = int(round(y_for_phase(frac)))
        phase_rows.append(y)
        flown = y >= y_frac
        a = 235 if flown else 170
        edge = 282 if flown else 285
        tick = pygame.Surface((288 - edge, 1), pygame.SRCALPHA)
        tick.fill((*UI_CREAM, a - 60))
        surf.blit(tick, (edge, y))
        caps(surf, name, 290, y - 5, 8, UI_CREAM, alpha=a,
             tracking=fit_tracking(name, 8, 61))

    tab_rows = [y_frac - 4, y_frac + 4]
    for label, col, lo_p, hi_p in (
        ("THERMAL", (245, 190, 110), THERM_LO, THERM_HI),
        ("RAIN SEEP", (150, 190, 235), RAIN_LO, RAIN_HI),
        ("SNOW FROST", (222, 238, 255), SNOW_LO, SNOW_HI),
    ):
        y_lo, y_hi = y_for_phase(hi_p) + 8, y_for_phase(lo_p) - 8
        y = dodge((y_lo + y_hi) / 2, phase_rows + tab_rows, 16, y_lo, y_hi)
        flown = y >= y_frac
        a = 220 if flown else 180
        tr = fit_tracking(label, 7, 52)
        caps(surf, label, 352, y - 4, 7, col, alpha=a, tracking=tr, right=True)
        sw = 352 - caps_width(label, 7, tr) - 7
        pygame.draw.rect(surf, col, (sw, y - 2, 4, 4))
        dotted(surf, 282 if flown else 285, sw - 2, y, col, 120)


def draw_back_pill(surf):
    cx, cy, pw, ph = 180, 616, 92, 22
    body = pygame.Surface((pw, ph), pygame.SRCALPHA)
    pygame.draw.rect(body, (12, 8, 38, 200), (0, 0, pw, ph), border_radius=ph // 2)
    pygame.draw.rect(body, _GOLD_BRIGHT, (0, 0, pw, ph), width=2,
                     border_radius=ph // 2)
    surf.blit(body, (cx - pw // 2, cy - ph // 2))
    caps(surf, "BACK", cx - caps_width("BACK", 12, 2) // 2, cy - 8, 12,
         _GOLD_BRIGHT, tracking=2)


def centred_caps(surf, text, y, size, color, alpha=255, tracking=1):
    caps(surf, text, 180 - caps_width(text, size, tracking) // 2, y, size,
         color, alpha=alpha, tracking=tracking)


def render_screen() -> pygame.Surface:
    surf = pygame.Surface((W, H))
    surf.fill(NEAR_BLACK)

    core = build_core_body()
    draw_laminations(core)
    draw_phase_planes(core)
    draw_thermal_vesicles(core)
    draw_rain_seep(core)
    draw_snow_frost(core)
    draw_clown_inclusions(core)
    draw_pyrite_cubes(core)
    draw_finale_vein(core)

    pts = fracture_points()
    col_y = fracture_column_y(pts)
    y_frac = sum(col_y) / len(col_y)
    lower, upper = split_blocks(core, col_y)
    veil_unflown(upper, col_y)

    # Bed the sample into the background before the blocks land on it.
    halo = pygame.Surface((CORE_W + 26, SPAN + 26), pygame.SRCALPHA)
    for i in range(13):
        pygame.draw.rect(halo, (110, 120, 160, int(2 + 13 * (i / 12.0) ** 1.8)),
                         (i, i, CORE_W + 26 - 2 * i, SPAN + 26 - 2 * i), 1)
    surf.blit(halo, (CORE_X0 - 13, CORE_Y0 - 13))

    surf.blit(lower, (CORE_X0, CORE_Y0))
    surf.blit(upper, (CORE_X0 + THROW, CORE_Y0))

    # The sample's own outline steps at the break, so the throw is legible
    # even with the red stripped out.
    fl, fr = col_y[0], col_y[-1]
    for (x, top, bot) in ((CORE_X0 - 1, fl, CORE_Y1), (CORE_X1, fr, CORE_Y1),
                          (CORE_X0 - 1 + THROW, CORE_Y0, fl),
                          (CORE_X1 + THROW, CORE_Y0, fr)):
        pygame.draw.line(surf, (6, 6, 14), (x, int(top)), (x, int(bot)))
    rim = pygame.Surface((1, int(CORE_Y1 - fl)), pygame.SRCALPHA)
    rim.fill((*UI_CREAM, 55))
    surf.blit(rim, (CORE_X0, int(fl)))
    surf.blit(rim, (CORE_X1 - 1, int(fl)))
    pygame.draw.line(surf, _GOLD_MUTED, (CORE_X0, CORE_Y1 - 1),
                     (CORE_X1 - 1, CORE_Y1 - 1), 2)
    pygame.draw.line(surf, _GOLD_MUTED, (CORE_X0 + THROW, CORE_Y0),
                     (CORE_X1 - 1 + THROW, CORE_Y0), 2)

    draw_header(surf)
    centred_caps(surf, f"PILLAR {DAY_PILLARS}  ·  FULL DAY", 100, 7,
                 _GOLD_MUTED, alpha=215)
    centred_caps(surf, "PILLAR 0  ·  LAUNCH", 593, 7, _GOLD_MUTED, alpha=215)

    draw_left_gutter(surf, y_frac)
    draw_right_gutter(surf, y_frac)
    draw_fracture(surf, pts)

    # "You are here" tab — the only saturated red on the screen.
    tab = pygame.Rect(282, int(y_frac) - 7, 21, 14)
    pygame.draw.rect(surf, (150, 20, 18), tab.inflate(2, 2), border_radius=2)
    pygame.draw.rect(surf, (222, 44, 38), tab, border_radius=2)
    pygame.draw.line(surf, (255, 128, 116), (tab.x + 1, tab.y + 1),
                     (tab.right - 2, tab.y + 1))
    n = str(RUN_SCORE)
    caps(surf, n, tab.centerx - caps_width(n, 9, 1) // 2, tab.y + 2, 9,
         (28, 4, 4))

    draw_back_pill(surf)
    return surf


# ── review sheet ────────────────────────────────────────────────────────────

def build_sheet(screen) -> pygame.Surface:
    board = pygame.Surface((1100, 900))
    board.fill((10, 10, 20))
    for y in range(0, 900, 40):
        pygame.draw.line(board, (16, 16, 30), (0, y), (1100, y))
    for x in range(0, 1100, 40):
        pygame.draw.line(board, (16, 16, 30), (x, 0), (x, 900))

    caps(board, "SKYBIT  ·  FLIGHT LOG  ·  CONCEPT: STRATA CORE  ·  ROUND 1",
         30, 22, 19, _GOLD_BRIGHT, tracking=2)
    caps(board, "PROCEDURAL · 360x640 CANVAS · MOCK RUN: 25 PILLARS, DAY 1, "
                "0:47 · NEW SCREEN, NO CURRENT DESIGN TO COMPARE",
         31, 50, 11, (140, 140, 162))

    def place(img, x, y, cap):
        caps(board, cap, x, y - 14, 10, (170, 170, 192))
        pygame.draw.rect(board, (58, 58, 78), (x - 1, y - 1, img.get_width() + 2,
                                               img.get_height() + 2), 1)
        board.blit(img, (x, y))

    place(screen, 30, 100, "1x — FULL SCREEN, 360x640")
    for rect, factor, cap, x, y in (
        (pygame.Rect(60, 396, 300, 120), 2,
         "2x — DEATH FRACTURE · FAULT THROW · DEPTH RULER · TAB", 430, 100),
        (pygame.Rect(60, 104, 300, 120), 2,
         "2x — DAY-COMPLETE CAP · FINALE VEIN · SNOW FROST · UNFLOWN HAZE",
         430, 372),
        (pygame.Rect(78, 282, 96, 76), 3,
         "3x — CLOWN INCLUSIONS · PYRITE", 430, 644),
        (pygame.Rect(228, 300, 96, 76), 3,
         "3x — RAIN SEEP · LAMINATION", 750, 644),
    ):
        crop = pygame.Surface(rect.size)
        crop.blit(screen, (0, 0), rect)
        place(pygame.transform.scale(crop, (rect.w * factor, rect.h * factor)),
              x, y, cap)
    return board


def main():
    screen = render_screen()
    sheet = build_sheet(screen)
    out_dir = os.path.join(ROOT, "docs", "flight_log", "strata_core")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    main()
