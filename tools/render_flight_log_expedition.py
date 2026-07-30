"""Round-1 review render of the `expedition_board` Flight Log concept.

The board reads like a printed expedition chart: the 175-pillar day is wrapped
across five strictly left-to-right lanes so every lane keeps the same reading
direction the game itself scrolls in. Return travel between lanes is a
de-emphasised gutter wire, never route, so the eye never mistakes it for
distance flown.

Offline tool — writes docs/flight_log/expedition_board/round_1.png. Nothing
here is imported by the game.
"""
from __future__ import annotations

import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

from game.biome import palette_for_phase  # noqa: E402
from game.draw import NEAR_BLACK, UI_CREAM, lerp_color  # noqa: E402
from game.weather import _phase_for_pillar  # noqa: E402

W, H = 360, 640

_GOLD_BRIGHT = (240, 192, 64)
_GOLD_MUTED = (200, 160, 50)
_RED_OUTLINE = (168, 32, 16)
_SCARLET_TOP = (240, 55, 55)
_SCARLET_BOT = (148, 20, 20)
_DEATH_RED = (232, 48, 44)

_FONT_BOLD = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          os.pardir, "game", "assets",
                          "LiberationSans-Bold.ttf")

# ── board geometry ───────────────────────────────────────────────────────────
LANES = 5
PER_LANE = 35
DAY_PILLARS = LANES * PER_LANE
LANE_CY = [127, 213, 299, 385, 471]
BAND_H = 62                    # full lane band (sky wash + both event registers)
ROAD_H = 14
INNER_X0, INNER_X1 = 20, 340
SEG_W = (INNER_X1 - INNER_X0) / PER_LANE

DEATH_PILLAR = 25
TIME_ALIVE = 47
COINS = 18

_ZONE_ALPHA = 50               # zone wash strength on the road half it owns

_TINT = {
    "thermal": (255, 176, 96),
    "rain": (120, 170, 235),
    "snow": (205, 234, 255),
    "clown": (176, 120, 235),
    "gold": _GOLD_BRIGHT,
}

_fonts: dict = {}
_pal_cache: dict = {}


def _font(size):
    f = _fonts.get(size)
    if f is None:
        f = pygame.font.Font(_FONT_BOLD, size)
        _fonts[size] = f
    return f


def _pal(phase):
    # Palette interpolation is the single hottest call in the sky wash; the
    # board only needs 4-decimal temporal resolution to look continuous.
    k = round(phase, 4)
    p = _pal_cache.get(k)
    if p is None:
        p = palette_for_phase(k)
        _pal_cache[k] = p
    return p


_phase_tab = [0.0] + [_phase_for_pillar(p) for p in range(1, DAY_PILLARS + 2)]


def phase_at(pillar_f: float) -> float:
    """Phase at a fractional pillar position, linearly blended between the
    two integer pillars it sits between."""
    pillar_f = max(0.0, min(DAY_PILLARS + 0.999, pillar_f))
    i = int(pillar_f)
    t = pillar_f - i
    return _phase_tab[i] + (_phase_tab[i + 1] - _phase_tab[i]) * t


def pillar_for_phase(phase: float) -> int:
    for p in range(1, DAY_PILLARS + 1):
        if _phase_tab[p] >= phase:
            return p
    return DAY_PILLARS


def lane_of(pillar: int) -> int:
    return (pillar - 1) // PER_LANE


def seg_x(pillar: int) -> tuple[float, float]:
    """Left/right x of one pillar's paving stone inside its own lane."""
    s = (pillar - 1) % PER_LANE
    return INNER_X0 + s * SEG_W, INNER_X0 + (s + 1) * SEG_W


# ── small drawing helpers ────────────────────────────────────────────────────

def _caps(surf, txt, x, y, size, color, tracking=1, anchor="left",
          shadow=NEAR_BLACK):
    """Letter-spaced caps. Tracking is what makes 7px labels read as engraved
    board lettering instead of a smudge. `y` is the vertical centre."""
    f = _font(size)
    glyphs = [(c, f.render(c, True, color)) for c in txt]
    total = sum(g.get_width() for _, g in glyphs) + tracking * (len(glyphs) - 1)
    gx = x if anchor == "left" else (x - total if anchor == "right"
                                     else x - total // 2)
    gy = y - glyphs[0][1].get_height() // 2 if glyphs else y
    for c, img in glyphs:
        if shadow is not None:
            sh = f.render(c, True, shadow)
            surf.blit(sh, (gx + 1, gy + 1))
        surf.blit(img, (gx, gy))
        gx += img.get_width() + tracking
    return total


def _caps_w(txt, size, tracking=1):
    f = _font(size)
    return sum(f.size(c)[0] for c in txt) + tracking * (len(txt) - 1)


def _outlined(surf, txt, x, y, size, fill, outline=_RED_OUTLINE, px=2,
              anchor="left"):
    f = _font(size)
    img = f.render(txt, True, fill)
    out = f.render(txt, True, outline)
    rx = x if anchor == "left" else x - img.get_width()
    ry = y - img.get_height() // 2
    for ox, oy in ((-px, 0), (px, 0), (0, -px), (0, px),
                   (-px, -px), (px, -px), (-px, px), (px, px)):
        surf.blit(out, (rx + ox, ry + oy))
    surf.blit(img, (rx, ry))
    return pygame.Rect(rx, ry, img.get_width(), img.get_height())


def _cut_rect_pts(x, y, w, h, cut):
    return [(x + cut, y), (x + w - cut, y), (x + w, y + cut),
            (x + w, y + h - cut), (x + w - cut, y + h), (x + cut, y + h),
            (x, y + h - cut), (x, y + cut)]


def _octagon(cx, cy, r):
    k = r * 0.42
    return [(cx - k, cy - r), (cx + k, cy - r), (cx + r, cy - k),
            (cx + r, cy + k), (cx + k, cy + r), (cx - k, cy + r),
            (cx - r, cy + k), (cx - r, cy - k)]


def _mix(a, b, t):
    return lerp_color(a, b, t)


# ── medallion glyphs (engraved: dark cut + light lip) ────────────────────────

def _glyph_thermal(surf, cx, cy, c):
    pygame.draw.line(surf, c, (cx, cy + 4), (cx, cy - 2), 1)
    pygame.draw.line(surf, c, (cx - 3, cy + 1), (cx, cy - 2), 1)
    pygame.draw.line(surf, c, (cx + 3, cy + 1), (cx, cy - 2), 1)
    pygame.draw.line(surf, c, (cx, cy + 4), (cx + 3, cy + 4), 1)
    pygame.draw.line(surf, c, (cx - 4, cy - 4), (cx - 2, cy - 5), 1)
    pygame.draw.line(surf, c, (cx + 2, cy - 5), (cx + 4, cy - 4), 1)


def _glyph_rain(surf, cx, cy, c):
    for i, ox in enumerate((-4, 0, 4)):
        oy = -1 if i == 1 else 1
        pygame.draw.line(surf, c, (cx + ox + 1, cy - 4 + oy),
                         (cx + ox - 1, cy + 2 + oy), 1)
        surf.set_at((cx + ox - 1, cy + 3 + oy), c)


def _glyph_snow(surf, cx, cy, c):
    for ang in (90, 30, 150):
        dx = math.cos(math.radians(ang)) * 5
        dy = math.sin(math.radians(ang)) * 5
        pygame.draw.line(surf, c, (cx - dx, cy - dy), (cx + dx, cy + dy), 1)
    for ang in (90, 30, 150):
        dx = math.cos(math.radians(ang)) * 5
        dy = math.sin(math.radians(ang)) * 5
        pygame.draw.line(surf, c, (cx + dx * 0.62 - dy * 0.22,
                                   cy + dy * 0.62 + dx * 0.22),
                         (cx + dx, cy + dy), 1)


def _glyph_die(surf, cx, cy, c):
    pygame.draw.rect(surf, c, (cx - 5, cy - 5, 11, 11), 1)
    for ox, oy in ((-2, -2), (2, -2), (0, 0), (-2, 2), (2, 2)):
        surf.set_at((cx + ox, cy + oy), c)


def _glyph_chevrons(surf, cx, cy, c):
    for i, ox in enumerate((-4, 0, 4)):
        pygame.draw.line(surf, c, (cx + ox - 1, cy - 4), (cx + ox + 2, cy), 1)
        pygame.draw.line(surf, c, (cx + ox + 2, cy), (cx + ox - 1, cy + 4), 1)


def _medallion(surf, cx, cy, glyph, pal, tint, r=9):
    """Cut-corner stone disc: stone_dark body pushed toward the zone tint,
    stone_light rim, glyph cut in stone_accent over a 1px black shadow so it
    survives both the bright day lanes and the desaturated unflown ones."""
    body = _mix(pal["stone_dark"], tint, 0.34)
    shade = pygame.Surface((r * 2 + 6, r * 2 + 6), pygame.SRCALPHA)
    pygame.draw.polygon(shade, (*NEAR_BLACK, 150),
                        _octagon(r + 3, r + 3 + 1, r + 1))
    surf.blit(shade, (cx - r - 3, cy - r - 3))
    pygame.draw.polygon(surf, body, _octagon(cx, cy, r))
    pygame.draw.polygon(surf, pal["stone_light"], _octagon(cx, cy, r), 1)
    pygame.draw.polygon(surf, _mix(body, NEAR_BLACK, 0.35),
                        _octagon(cx, cy, r - 2), 1)
    gsh = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    glyph(gsh, r, r + 1, (*NEAR_BLACK, 190))
    surf.blit(gsh, (cx - r, cy - r))
    gl = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    glyph(gl, r, r, pal["stone_accent"])
    surf.blit(gl, (cx - r, cy - r))


# ── the screen ───────────────────────────────────────────────────────────────

def _lane_sky(lane):
    """Opaque 320x62 slice of that lane's sky, evolving left to right. Each
    column carries the real sky_top/mid/bot ramp for the pillar under it, so a
    lane is literally a horizontal core-sample of the day."""
    surf = pygame.Surface((INNER_X1 - INNER_X0, BAND_H))
    half = BAND_H / 2
    for px in range(INNER_X1 - INNER_X0):
        t = px / (INNER_X1 - INNER_X0)
        p = _pal(phase_at(lane * PER_LANE + t * PER_LANE + 0.5))
        top, mid, bot = p["sky_top"], p["sky_mid"], p["sky_bot"]
        for py in range(BAND_H):
            if py < half:
                c = lerp_color(top, mid, py / half)
            else:
                c = lerp_color(mid, bot, (py - half) / half)
            surf.set_at((px, py), c)
    return surf


def _lane_stars(surf, lane, top_y):
    """Stars only where the palette actually calls for them, so the night
    lanes gain a texture the day lanes never do."""
    rnd = random.Random(1700 + lane)
    for _ in range(90):
        px = rnd.randrange(INNER_X1 - INNER_X0)
        py = rnd.randrange(BAND_H)
        p = _pal(phase_at(lane * PER_LANE
                          + px / (INNER_X1 - INNER_X0) * PER_LANE + 0.5))
        a = int(p["star_alpha"])
        if a < 40:
            continue
        b = rnd.randrange(60, 100) / 100.0
        v = int(210 * b)
        dot = pygame.Surface((1, 1), pygame.SRCALPHA)
        dot.fill((255, 255, 245, int(a * b)))
        surf.blit(dot, (INNER_X0 + px, top_y + py))
        if b > 0.92:
            surf.set_at((INNER_X0 + px, top_y + py), (v + 45, v + 45, 255))


def _road_segment(surf, lane, seg, cy, gold):
    """One paving stone == one pillar. The seam between stones is the whole
    point: the player can count the stones they actually cleared."""
    pillar = lane * PER_LANE + seg + 1
    p = _pal(phase_at(pillar - 0.5))
    lo, mid, dk = p["stone_light"], p["stone_mid"], p["stone_dark"]
    acc = p["stone_accent"]
    if gold:
        lo = _mix(lo, _GOLD_BRIGHT, 0.45)
        mid = _mix(mid, _GOLD_BRIGHT, 0.45)
        dk = _mix(dk, _GOLD_MUTED, 0.35)
        acc = _mix(acc, (255, 240, 190), 0.6)
    x0 = int(round(INNER_X0 + seg * SEG_W))
    x1 = int(round(INNER_X0 + (seg + 1) * SEG_W))
    y0 = cy - ROAD_H // 2
    body_h = ROAD_H - 3
    for i in range(1, body_h):
        t = (i - 1) / max(1, body_h - 2)
        c = lerp_color(lo, mid, t / 0.55) if t < 0.55 else \
            lerp_color(mid, dk, (t - 0.55) / 0.45)
        pygame.draw.line(surf, c, (x0, y0 + i), (x1 - 1, y0 + i))
    pygame.draw.line(surf, acc, (x0, y0), (x1 - 1, y0))
    pygame.draw.line(surf, NEAR_BLACK, (x0, y0 + ROAD_H - 2),
                     (x1 - 1, y0 + ROAD_H - 2))
    pygame.draw.line(surf, NEAR_BLACK, (x0, y0 + ROAD_H - 1),
                     (x1 - 1, y0 + ROAD_H - 1))
    rnd = random.Random(42 + pillar)
    grain = pygame.Surface((max(1, x1 - x0), body_h), pygame.SRCALPHA)
    for _ in range(3):
        gx = rnd.randrange(max(1, x1 - x0))
        gy = rnd.randrange(2, body_h - 1)
        c = lo if rnd.random() < 0.5 else dk
        grain.set_at((gx, gy), (*c, 105))
    surf.blit(grain, (x0, y0 + 1))
    seam = pygame.Surface((1, body_h), pygame.SRCALPHA)
    seam.fill((*NEAR_BLACK, 90))
    surf.blit(seam, (x0, y0 + 1))


def _return_wire(surf, lane):
    """Carriage return between lanes. Solid only in the side margins, dashed
    across the gutter, always 2px stone_dark at alpha 60 — it must never be
    mistaken for flown distance."""
    cy = LANE_CY[lane]
    ny = LANE_CY[lane + 1]
    gy = (cy + BAND_H // 2 + ny - BAND_H // 2) // 2
    wire = pygame.Surface((W, H), pygame.SRCALPHA)
    col = (*_mix(_pal(phase_at(lane * PER_LANE + 34))["stone_dark"],
                 (255, 255, 255), 0.15), 60)
    pygame.draw.line(wire, col, (INNER_X1, cy), (350, cy), 2)
    pygame.draw.line(wire, col, (350, cy), (350, gy), 2)
    pygame.draw.line(wire, col, (10, gy), (10, ny), 2)
    pygame.draw.line(wire, col, (10, ny), (INNER_X0, ny), 2)
    x = 350
    while x > 10:
        pygame.draw.line(wire, col, (x, gy), (max(10, x - 3), gy), 2)
        x -= 8
    pygame.draw.polygon(wire, col, [(18, gy - 3), (18, gy + 3), (13, gy)])
    surf.blit(wire, (0, 0))


def _zone_spans(p0, p1):
    """Split a pillar range into per-lane (lane, x0, x1, opens, closes) runs."""
    out = []
    for lane in range(LANES):
        lo = max(p0, lane * PER_LANE + 1)
        hi = min(p1, (lane + 1) * PER_LANE)
        if lo > hi:
            continue
        x0 = seg_x(lo)[0]
        x1 = seg_x(hi)[1]
        out.append((lane, x0, x1, lo == p0, hi == p1))
    return out


def _zone(surf, spec):
    p0, p1 = spec["p0"], spec["p1"]
    tint = _TINT[spec["tint"]]
    above = spec["register"] == "weather"
    runs = _zone_spans(p0, p1)
    if not runs:
        return
    widest = max(runs, key=lambda r: r[2] - r[1])
    for lane, x0, x1, opens, closes in runs:
        cy = LANE_CY[lane]
        wash = pygame.Surface((max(1, int(x1 - x0)), ROAD_H // 2),
                              pygame.SRCALPHA)
        wash.fill((*tint, _ZONE_ALPHA))
        surf.blit(wash, (int(x0), cy - ROAD_H // 2 + 1 if above else cy))
        by = cy - 13 if above else cy + 13
        br = pygame.Surface((W, 8), pygame.SRCALPHA)
        pygame.draw.line(br, (*tint, 150), (int(x0), 4), (int(x1) - 1, 4), 1)
        if opens:
            pygame.draw.line(br, (*tint, 190), (int(x0), 1), (int(x0), 6), 1)
        if closes:
            pygame.draw.line(br, (*tint, 190),
                             (int(x1) - 1, 1), (int(x1) - 1, 6), 1)
        surf.blit(br, (0, by - 4))
        # Continuation carets tell the eye the zone runs on into the next lane
        # rather than ending at the paper edge.
        car = pygame.Surface((W, 12), pygame.SRCALPHA)
        if not opens:
            pygame.draw.polygon(car, (*tint, 175),
                                [(int(x0) + 5, 1), (int(x0) + 5, 9),
                                 (int(x0) + 1, 5)])
        if not closes:
            pygame.draw.polygon(car, (*tint, 175),
                                [(int(x1) - 6, 1), (int(x1) - 6, 9),
                                 (int(x1) - 2, 5)])
        surf.blit(car, (0, (cy - 22 if above else cy + 22) - 6))
        if (lane, x0, x1) != (widest[0], widest[1], widest[2]):
            continue
        my = cy - 22 if above else cy + 22
        pal = _pal(phase_at(lane * PER_LANE + 17))
        lw = _caps_w(spec["label"], 7)
        if spec["anchor"] == "start":
            mx = int(x0) + 10
        else:
            mx = int((x0 + x1) / 2)
        mx = max(INNER_X0 + 10, min(mx, INNER_X1 - 10))
        # A medallion must sit inside the span it annotates, so the LABEL is
        # what flips sides when the span runs into the right margin.
        if mx + 13 + lw <= INNER_X1 - 2:
            lx, la = mx + 13, "left"
        else:
            lx, la = mx - 13, "right"
        _medallion(surf, mx, my, spec["glyph"], pal, tint)
        _caps(surf, spec["label"], lx, my, 7, UI_CREAM, tracking=1, anchor=la)


def _coin_rush_marks(surf):
    for p in range(15, DAY_PILLARS + 1, 15):
        lane = lane_of(p)
        cy = LANE_CY[lane]
        x0, x1 = seg_x(p)
        cx = int((x0 + x1) / 2)
        tick = pygame.Surface((4, 7), pygame.SRCALPHA)
        pygame.draw.line(tick, (*_GOLD_BRIGHT, 235), (1, 0), (1, 4), 2)
        pygame.draw.line(tick, (*_GOLD_MUTED, 140), (0, 5), (3, 5), 1)
        surf.blit(tick, (cx - 1, cy + ROAD_H // 2 + 1))


def _death_marker(surf):
    x = int(round(INNER_X0 + (DEATH_PILLAR % PER_LANE) * SEG_W))
    cy = LANE_CY[lane_of(DEATH_PILLAR)]
    top, bot = cy - 31, cy + 31
    halo = pygame.Surface((26, BAND_H + 8), pygame.SRCALPHA)
    for r in range(9, 0, -1):
        a = int(120 * (1 - (r - 1) / 9.0) ** 1.6)
        pygame.draw.rect(halo, (*_DEATH_RED, a),
                         (13 - r - 1, 4 - r, 2 + r * 2, BAND_H + r * 2))
    surf.blit(halo, (x - 13, top - 4))
    pygame.draw.line(surf, (255, 255, 255), (x, top), (x, bot), 2)
    # Pennant: white-cored red swallowtail. Shape alone identifies the run's
    # end even with every hue stripped out.
    py = cy - 15
    pts = [(x + 1, py - 7), (x + 13, py - 7), (x + 9, py), (x + 13, py + 7),
           (x + 1, py + 7)]
    sh = pygame.Surface((20, 20), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (*NEAR_BLACK, 150),
                        [(px - x + 4, pyy - py + 9) for px, pyy in pts])
    surf.blit(sh, (x - 3, py - 9))
    pygame.draw.polygon(surf, (255, 255, 255), pts)
    inner = [(x + 3, py - 5), (x + 11, py - 5), (x + 7, py), (x + 11, py + 5),
             (x + 3, py + 5)]
    pygame.draw.polygon(surf, _DEATH_RED, inner)
    pygame.draw.line(surf, (255, 255, 255), (x + 3, py - 3), (x + 3, py + 3), 2)
    return x


def _stat_chip(surf, x, y, w, h, label, value):
    plate = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(plate, (26, 26, 46, 245), _cut_rect_pts(0, 0, w, h, 5))
    pygame.draw.polygon(plate, (*_GOLD_MUTED, 130),
                        _cut_rect_pts(0, 0, w, h, 5), 1)
    surf.blit(plate, (x, y))
    _caps(surf, label, x + 10, y + h // 2, 7, _GOLD_MUTED, tracking=1)
    _caps(surf, value, x + w - 10, y + h // 2, 12, UI_CREAM, tracking=0,
          anchor="right")


def _back_pill(surf, cx, cy):
    pw, ph = 116, 30
    x, y = cx - pw // 2, cy - ph // 2
    sh = pygame.Surface((pw + 4, ph + 4), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 95), (0, 0, pw + 4, ph + 4),
                     border_radius=(ph + 4) // 2)
    surf.blit(sh, (x - 2, y + 5))
    pill = pygame.Surface((pw, ph), pygame.SRCALPHA)
    for yy in range(ph):
        pygame.draw.line(pill, lerp_color(_SCARLET_TOP, _SCARLET_BOT,
                                          yy / (ph - 1)),
                         (0, yy), (pw - 1, yy))
    frost = pygame.Surface((pw, ph), pygame.SRCALPHA)
    for yy in range(ph // 2):
        frost.fill((255, 245, 220, int(50 * (1 - yy / (ph / 2)))),
                   (0, yy, pw, 1))
    pill.blit(frost, (0, 0))
    mask = pygame.Surface((pw, ph), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, pw, ph),
                     border_radius=ph // 2)
    pill.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    pygame.draw.rect(pill, _GOLD_BRIGHT, (0, 0, pw, ph), width=2,
                     border_radius=ph // 2)
    surf.blit(pill, (x, y))
    _caps(surf, "BACK", cx, cy, 13, (255, 255, 255), tracking=2,
          anchor="center", shadow=(90, 12, 12))


def _legend(surf, y):
    """The board has two spatial registers; the key states that outright so
    the player never has to infer it from the medallions alone."""
    pygame.draw.line(surf, (*_GOLD_MUTED, 90), (20, y - 13), (340, y - 13), 1)
    items = [("WEATHER ABOVE", "up"), ("EVENTS BELOW", "down"),
             ("RUN END", "flag")]
    widths = [16 + _caps_w(t, 7) for t, _ in items]
    gap = (320 - sum(widths)) // (len(items) - 1)
    x = 20
    for (txt, kind), wd in zip(items, widths):
        if kind == "up":
            pygame.draw.polygon(surf, _TINT["rain"],
                                [(x + 1, y + 3), (x + 9, y + 3), (x + 5, y - 4)])
        elif kind == "down":
            pygame.draw.polygon(surf, _TINT["clown"],
                                [(x + 1, y - 4), (x + 9, y - 4), (x + 5, y + 3)])
        else:
            pygame.draw.polygon(surf, (255, 255, 255),
                                [(x + 1, y - 5), (x + 10, y - 5), (x + 7, y),
                                 (x + 10, y + 5), (x + 1, y + 5)])
            pygame.draw.polygon(surf, _DEATH_RED,
                                [(x + 3, y - 3), (x + 8, y - 3), (x + 5, y),
                                 (x + 8, y + 3), (x + 3, y + 3)])
        _caps(surf, txt, x + 15, y, 7, UI_CREAM, tracking=1)
        x += wd + gap


def _desaturate(surf, rect, keep=0.40):
    """Unflown territory loses chroma, never luminance — the labels there must
    stay as readable as the flown ones."""
    sub = surf.subsurface(rect).copy()
    grey = pygame.transform.grayscale(sub)
    grey.set_alpha(int(255 * (1.0 - keep)))
    surf.blit(grey, rect.topleft)


ZONES = [
    dict(register="weather", tint="thermal", glyph=_glyph_thermal,
         label="THERMALS", anchor="start",
         p0=pillar_for_phase(0.106), p1=pillar_for_phase(0.206)),
    dict(register="weather", tint="rain", glyph=_glyph_rain,
         label="RAINBAND", anchor="center",
         p0=pillar_for_phase(0.43), p1=pillar_for_phase(0.69)),
    dict(register="weather", tint="snow", glyph=_glyph_snow,
         label="SNOW SQUALL", anchor="center",
         p0=pillar_for_phase(0.78), p1=DAY_PILLARS),
    dict(register="event", tint="clown", glyph=_glyph_die,
         label="CLOWN GAUNTLET", anchor="center",
         p0=pillar_for_phase(0.403), p1=pillar_for_phase(0.539)),
    dict(register="event", tint="gold", glyph=_glyph_chevrons,
         label="FINALE", anchor="center",
         p0=DAY_PILLARS - 2, p1=DAY_PILLARS),
]


def render_screen():
    surf = pygame.Surface((W, H))
    surf.fill(NEAR_BLACK)

    # ── header ──
    _outlined(surf, "FLIGHT LOG", 20, 42, 18, _GOLD_BRIGHT, px=2)
    _caps(surf, "DAY 1  ·  ROUTE CHART", 21, 66, 8, (168, 158, 140),
          tracking=1)
    f = _font(44)
    img = f.render("25", True, (252, 244, 220))
    rim = f.render("25", True, (150, 108, 20))
    rr = img.get_rect()
    rr.right, rr.centery = 340, 44
    for ox, oy in ((-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, -2),
                   (-2, 2), (2, 2)):
        surf.blit(rim, (rr.x + ox, rr.y + oy))
    surf.blit(img, rr.topleft)
    _caps(surf, "PILLARS CLEARED", 340, 72, 7, _GOLD_MUTED, tracking=1,
          anchor="right")
    rule = pygame.Surface((320, 1), pygame.SRCALPHA)
    for i in range(320):
        t = min(i, 319 - i) / 60.0
        rule.set_at((i, 0), (*_GOLD_MUTED, int(150 * min(1.0, t))))
    surf.blit(rule, (20, 86))

    # ── lanes ──
    for lane in range(LANES):
        cy = LANE_CY[lane]
        top = cy - BAND_H // 2
        sky = _lane_sky(lane)
        sky.set_alpha(140)
        surf.blit(sky, (INNER_X0, top))
        # Cut corners keep the lane plates in the same family as the in-game
        # HUD plates instead of reading as plain web rectangles.
        for cx0, cy0, sx, sy in ((INNER_X0, top, 1, 1),
                                 (INNER_X1 - 1, top, -1, 1),
                                 (INNER_X0, top + BAND_H - 1, 1, -1),
                                 (INNER_X1 - 1, top + BAND_H - 1, -1, -1)):
            pygame.draw.polygon(surf, NEAR_BLACK,
                                [(cx0, cy0), (cx0 + 6 * sx, cy0),
                                 (cx0, cy0 + 6 * sy)])
        _lane_stars(surf, lane, top)
        pal_edge = _pal(phase_at(lane * PER_LANE + 17))
        pygame.draw.polygon(surf, _mix(pal_edge["stone_dark"], NEAR_BLACK, 0.3),
                            _cut_rect_pts(INNER_X0 - 2, top - 1,
                                          INNER_X1 - INNER_X0 + 3,
                                          BAND_H + 1, 6), 1)
        for seg in range(PER_LANE):
            pillar = lane * PER_LANE + seg + 1
            _road_segment(surf, lane, seg, cy, pillar % 15 == 0)
        _caps(surf, "%02d" % (lane + 1), 8, cy, 8,
              pal_edge["stone_accent"], tracking=1)

    for lane in range(LANES - 1):
        _return_wire(surf, lane)

    for spec in ZONES:
        _zone(surf, spec)
    _coin_rush_marks(surf)

    # ── unflown territory ──
    # Clipped to the lane plates: draining chroma from the bare NEAR_BLACK
    # margin would leave a visible seam between flown and unflown background.
    death_x = int(round(INNER_X0 + (DEATH_PILLAR % PER_LANE) * SEG_W))
    plate_x, plate_w = INNER_X0 - 2, INNER_X1 - INNER_X0 + 4
    _desaturate(surf, pygame.Rect(death_x, LANE_CY[0] - BAND_H // 2,
                                  plate_x + plate_w - death_x, BAND_H))
    for lane in range(1, LANES):
        _desaturate(surf, pygame.Rect(plate_x, LANE_CY[lane] - BAND_H // 2,
                                      plate_w, BAND_H))

    _death_marker(surf)

    # ── footer ──
    _legend(surf, 528)
    _stat_chip(surf, 20, 558, 152, 26, "TIME", "0:%02d" % TIME_ALIVE)
    _stat_chip(surf, 188, 558, 152, 26, "COINS", str(COINS))
    _back_pill(surf, 180, 612)
    return surf


# ── review sheet ─────────────────────────────────────────────────────────────

SHEET_W, SHEET_H = 1200, 1600


def _panel(sheet, screen, dst, crop, scale, caption):
    sub = screen.subsurface(crop)
    big = pygame.transform.scale(sub, (crop.w * scale, crop.h * scale))
    fr = pygame.Rect(dst[0] - 2, dst[1] - 2, big.get_width() + 4,
                     big.get_height() + 4)
    pygame.draw.rect(sheet, (60, 58, 78), fr, 2)
    sheet.blit(big, dst)
    _caps(sheet, caption, dst[0], dst[1] - 14, 11, (206, 198, 178), tracking=1)


def build_sheet(screen):
    sheet = pygame.Surface((SHEET_W, SHEET_H))
    sheet.fill((22, 22, 32))
    _outlined(sheet, "FLIGHT LOG  ·  EXPEDITION BOARD", 32, 34, 22,
              _GOLD_BRIGHT, px=2)
    _caps(sheet, "ROUND 1  ·  175-PILLAR DAY WRAPPED ACROSS 5 LEFT-TO-RIGHT "
                 "LANES  ·  RUN ENDED AT PILLAR 25", 34, 62, 11,
          (170, 164, 148), tracking=1)
    pygame.draw.line(sheet, (*_GOLD_MUTED, 90), (32, 78), (1168, 78), 1)

    _panel(sheet, screen, (32, 104), pygame.Rect(0, 0, W, H), 1,
           "FULL SCREEN — ACTUAL SIZE 360×640")
    _panel(sheet, screen, (440, 104), pygame.Rect(0, 86, W, 270), 2,
           "2×  LANES 01–03  (DAY → GOLDEN → DUSK/NIGHT)")
    _panel(sheet, screen, (440, 690), pygame.Rect(0, 346, W, 292), 2,
           "2×  LANES 04–05 + KEY + FOOTER")
    _panel(sheet, screen, (32, 790), pygame.Rect(222, 92, 118, 78), 3,
           "3×  RUN-END PENNANT + DESATURATION EDGE")
    _panel(sheet, screen, (32, 1058), pygame.Rect(96, 92, 118, 78), 3,
           "3×  THERMALS MEDALLION + COIN-RUSH STONE")
    _panel(sheet, screen, (56, 1330), pygame.Rect(0, 262, W, 76), 3,
           "3×  LANE 03 — WEATHER REGISTER ABOVE, EVENT REGISTER BELOW")
    return sheet


def main():
    screen = render_screen()
    sheet = build_sheet(screen)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir,
                       "docs", "flight_log", "expedition_board")
    os.makedirs(out, exist_ok=True)
    path = os.path.normpath(os.path.join(out, "round_1.png"))
    pygame.image.save(sheet, path)
    print(path, sheet.get_size())


if __name__ == "__main__":
    main()
