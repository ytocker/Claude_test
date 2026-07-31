#!/usr/bin/env python3
"""
sky-ruler  ·  flight_log_progress  ·  round 2

The ruler IS the sky. One 300x52 ribbon carries a full-saturation sweep of the
real biome palette, so the times of day are read as colour rather than as
labelled boxes. Nothing ahead of the player is dimmed or greyed: the day the
player has NOT seen is the most beautiful thing on the screen, because that is
what the screen is selling. Progress is therefore marked additively -- a lit
rail over the flown 18%, keylined in ink so it survives against a bright
daylight sky -- and the one place two marks would collide (geyser 0.156 vs.
death 0.184, 8 px apart at true scale) is handed wholesale to a x5 loupe: the
main strip carries ONLY the death blade inside that window, so the loupe owns
its subject instead of echoing it.

Five tiers, top to bottom: title / hero percentage / sky ribbon / STILL AHEAD /
BACK. Everything that was a second way of saying the same thing -- phase table,
event key, death callout -- is gone, and the pixels went into the ribbon.
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

from game.biome import PHASE_BOUNDARIES, palette_for_phase
from game.weather import (THERMAL_START_PHASE, SNOW_STORM_CENTER,
                          _phase_for_pillar)
from game.config import LATE_GAME_PILLAR, RAIN_START_PILLAR
from game.draw import lerp_color


W, H = 360, 640
SS = 3                                   # supersample factor for AA shapes

FONT = "/home/user/skybit/game/assets/LiberationSans-Bold.ttf"
_fonts = {}


def _font(size):
    f = _fonts.get(size)
    if f is None:
        f = pygame.font.Font(FONT, size)
        _fonts[size] = f
    return f


# ── type scale ───────────────────────────────────────────────────────────────
# Four sizes and nothing else. Anything smaller than MICRO is unreadable on a
# phone held at arm's length, so it may as well not be drawn.
HERO, SECT, BODY_S, MICRO = 32, 16, 12, 10

# ── palette ──────────────────────────────────────────────────────────────────
GOLD        = (240, 192,  64)            # hud.py _GOLD_BRIGHT
GOLD_PALE   = (255, 232, 168)            # hud.py _GOLD_PALE
GOLD_DEEP   = (255, 176,  56)
RAIL_CORE   = (255, 246, 214)
SCARLET     = (255,  78,  78)
SCARLET_PAL = (255, 158, 158)
INK         = (  6,   8,  14)
PANEL_DARK  = ( 12,   8,  38)            # hud.py _PANEL_DARK
PANEL_LIGHT = ( 26,  18,  62)            # hud.py _PANEL_LIGHTER
FRAME_WARM  = (120,  96,  64)
BODY_TXT    = (226, 232, 244)
MUTED       = (176, 188, 212)
MUTED_D     = (146, 160, 186)
ICE         = (198, 230, 255)
STEAM       = (196, 240, 250)
RAINBLUE    = (126, 186, 255)

# ── geometry ─────────────────────────────────────────────────────────────────
RIB_X, RIB_Y, RIB_W, RIB_H = 30, 292, 300, 52
RIB_R = RIB_X + RIB_W

LOUPE = pygame.Rect(24, 138, 156, 96)
LOUPE_P0, LOUPE_P1 = 0.140, 0.200       # phase window the loupe magnifies

DEATH_PHASE = 0.184
DAY_N       = 1
TIME_ALIVE  = 47
DEATH_PILLAR = 25

TICK_Y  = RIB_Y + RIB_H + 8
LABEL_Y = TICK_Y + 14
GLYPH_Y = 392


def px(phase):
    """Phase -> x on the main ribbon."""
    return RIB_X + phase * RIB_W


# ═════════════════════════════════════════════════════════════════════════════
# primitives
# ═════════════════════════════════════════════════════════════════════════════
def aline(surf, color, p0, p1, alpha=255, width=1):
    """pygame.draw writes pixels rather than blending them, and the sheet is an
    opaque canvas, so every translucent hairline has to route through a scratch
    SRCALPHA surface or it lands at full strength."""
    pad = width + 2
    minx = int(min(p0[0], p1[0])) - pad
    miny = int(min(p0[1], p1[1])) - pad
    maxx = int(max(p0[0], p1[0])) + pad
    maxy = int(max(p0[1], p1[1])) + pad
    tmp = pygame.Surface((maxx - minx, maxy - miny), pygame.SRCALPHA)
    pygame.draw.line(tmp, color, (p0[0] - minx, p0[1] - miny),
                     (p1[0] - minx, p1[1] - miny), width)
    if alpha < 255:
        tmp.set_alpha(alpha)
    surf.blit(tmp, (minx, miny))


def soft_shadow(surf, rect, radius, spread=5, peak=34, drop=2):
    """Outer ring first: draw.rect replaces pixels, so an inside-out stack
    would erase every brighter layer it was built on."""
    s = pygame.Surface((rect.w + spread * 2, rect.h + spread * 2 + drop),
                       pygame.SRCALPHA)
    for i in range(spread, 0, -1):
        a = int(peak * (1 - i / (spread + 1)) ** 0.7)
        pygame.draw.rect(s, (0, 0, 0, a),
                         (spread - i, spread - i + drop,
                          rect.w + i * 2, rect.h + i * 2),
                         border_radius=radius + i)
    surf.blit(s, (rect.x - spread, rect.y - spread))


# ═════════════════════════════════════════════════════════════════════════════
# text
# ═════════════════════════════════════════════════════════════════════════════
def _render(txt, size, color, spacing=0):
    f = _font(size)
    if spacing <= 0:
        return f.render(txt, True, color)
    imgs = [f.render(c, True, color) for c in txt]
    w = int(round(sum(i.get_width() for i in imgs) + spacing * (len(txt) - 1)))
    h = max(i.get_height() for i in imgs)
    s = pygame.Surface((max(1, w), h), pygame.SRCALPHA)
    x = 0.0
    for i in imgs:
        s.blit(i, (int(round(x)), 0))
        x += i.get_width() + spacing
    return s


def text(surf, txt, size, color, pos, anchor="midleft", spacing=0,
         alpha=255, halo=0, halo_col=INK, shadow=0):
    """Halo is a knockout: leader lines are drawn first and the halo cuts the
    label out of them, which is how a chart keeps type legible over rules."""
    img = _render(txt, size, color, spacing)
    r = img.get_rect(**{anchor: pos})
    if halo:
        h = _render(txt, size, halo_col, spacing)
        h.set_alpha(halo)
        for dx in (-2, -1, 0, 1, 2):
            for dy in (-2, -1, 0, 1, 2):
                if dx or dy:
                    surf.blit(h, (r.x + dx, r.y + dy))
    if shadow:
        s = _render(txt, size, INK, spacing)
        s.set_alpha(shadow)
        surf.blit(s, (r.x + 1, r.y + 1))
    if alpha < 255:
        img.set_alpha(alpha)
    surf.blit(img, r.topleft)
    return r


def runs(surf, parts, x, y, size, shadow=150):
    """One baseline, several colours — so a sentence can carry hierarchy
    without breaking into separate lines."""
    for txt, col in parts:
        r = text(surf, txt, size, col, (x, y), "midleft", shadow=shadow)
        x = r.right
    return x


# ═════════════════════════════════════════════════════════════════════════════
# glyphs — drawn at SSx then smoothscaled so diagonals and curves antialias
# without pygame.draw.arc / gfxdraw (neither is WASM-safe)
# ═════════════════════════════════════════════════════════════════════════════
def _gsurf(size):
    return pygame.Surface((size * SS, size * SS), pygame.SRCALPHA)


def _put(dst, g, size, cx, cy):
    dst.blit(pygame.transform.smoothscale(g, (size, size)),
             (int(round(cx - size / 2)), int(round(cy - size / 2))))


def _poly(g, S, pts, col):
    pygame.draw.polygon(g, col, [(x * S, y * S) for x, y in pts])


def _circ(g, S, cx, cy, r, col):
    pygame.draw.circle(g, col, (int(cx * S), int(cy * S)), max(1, int(r * S)))


def glyph_geyser(size, col=STEAM):
    S = size * SS
    g = _gsurf(size)
    _poly(g, S, [(0.44, 0.90), (0.39, 0.58), (0.28, 0.36), (0.34, 0.15),
                 (0.50, 0.05), (0.66, 0.15), (0.72, 0.36), (0.61, 0.58),
                 (0.56, 0.90)], col)
    _circ(g, S, 0.19, 0.40, 0.065, col)
    _circ(g, S, 0.82, 0.47, 0.055, col)
    _circ(g, S, 0.25, 0.66, 0.045, col)
    pygame.draw.rect(g, (*col, 190),
                     (0.16 * S, 0.88 * S, 0.68 * S, 0.09 * S))
    return g


def glyph_lamp(size, col=GOLD):
    S = size * SS
    g = _gsurf(size)
    pygame.draw.ellipse(g, col, (0.20 * S, 0.44 * S, 0.50 * S, 0.30 * S))
    _poly(g, S, [(0.64, 0.50), (0.98, 0.40), (0.98, 0.48), (0.66, 0.62)], col)
    pygame.draw.ellipse(g, col, (0.00 * S, 0.40 * S, 0.23 * S, 0.30 * S))
    pygame.draw.ellipse(g, (0, 0, 0, 0),
                        (0.045 * S, 0.455 * S, 0.13 * S, 0.19 * S))
    _circ(g, S, 0.45, 0.40, 0.075, col)
    pygame.draw.rect(g, col, (0.26 * S, 0.72 * S, 0.40 * S, 0.07 * S))
    _circ(g, S, 0.80, 0.24, 0.055, (*col, 150))
    _circ(g, S, 0.90, 0.11, 0.040, (*col, 95))
    return g


def glyph_drop(size, col=RAINBLUE):
    S = size * SS
    g = _gsurf(size)
    _poly(g, S, [(0.50, 0.02), (0.79, 0.48), (0.84, 0.66),
                 (0.16, 0.66), (0.21, 0.48)], col)
    _circ(g, S, 0.50, 0.63, 0.335, col)
    _circ(g, S, 0.37, 0.66, 0.10, (235, 248, 255, 210))
    return g


def glyph_snow(size, col=ICE):
    S = size * SS
    g = _gsurf(size)
    wid = max(1, int(0.075 * S))
    for k in range(6):
        a = math.radians(k * 60 - 90)
        ex, ey = 0.5 + 0.46 * math.cos(a), 0.5 + 0.46 * math.sin(a)
        pygame.draw.line(g, col, (0.5 * S, 0.5 * S), (ex * S, ey * S), wid)
        for f, bl in ((0.60, 0.15), (0.86, 0.11)):
            bx, by = 0.5 + 0.46 * f * math.cos(a), 0.5 + 0.46 * f * math.sin(a)
            for da in (0.85, -0.85):
                tx = bx + bl * math.cos(a + da)
                ty = by + bl * math.sin(a + da)
                pygame.draw.line(g, col, (bx * S, by * S), (tx * S, ty * S),
                                 max(1, wid - SS // 2))
    _circ(g, S, 0.5, 0.5, 0.075, col)
    return g


GLYPHS = {
    "geyser": glyph_geyser,
    "lamp":   glyph_lamp,
    "rain":   glyph_drop,
    "snow":   glyph_snow,
}
_GLYPH_CACHE = {}


def draw_glyph(dst, kind, size, cx, cy):
    key = (kind, size)
    g = _GLYPH_CACHE.get(key)
    if g is None:
        g = GLYPHS[kind](size)
        _GLYPH_CACHE[key] = g
    _put(dst, g, size, cx, cy)


# ═════════════════════════════════════════════════════════════════════════════
# the ribbon itself
# ═════════════════════════════════════════════════════════════════════════════
_STRIP_CACHE = {}


def sky_strip(w, h, p0, p1, step=2):
    """Each 2 px column is a miniature sky for its phase: sky_top -> sky_mid ->
    sky_bot down the strip's height. Sampling the live palette means the ruler
    can never drift out of sync with the sky the player actually flew through.

    Cached: a per-column palette solve is far too expensive to repeat on a
    screen that redraws every frame, and the strip never changes."""
    key = (w, h, p0, p1, step)
    s = _STRIP_CACHE.get(key)
    if s is not None:
        return s
    s = pygame.Surface((w, h))
    x = 0
    while x < w:
        ph = (p0 + (p1 - p0) * ((x + step * 0.5) / w)) % 1.0
        pal = palette_for_phase(ph)
        top, mid, bot = pal["sky_top"], pal["sky_mid"], pal["sky_bot"]
        for y in range(h):
            t = y / (h - 1)
            c = (lerp_color(top, mid, t / 0.55) if t < 0.55
                 else lerp_color(mid, bot, (t - 0.55) / 0.45))
            pygame.draw.rect(s, c, (x, y, step, 1))
        x += step
    _STRIP_CACHE[key] = s
    return s


def flown_rail(surf, x0, y0, width, span, tall=True):
    """Warm at the origin, resolving to a near-white spark at the leading edge:
    the run reads as heat that has burned forward and is about to run out.

    The 1 px INK undercut is the whole reason the rail survives: over a noon
    sky a pale gold line is only ~2.9:1 against the body it sits on, but the
    ink boundary under it is >6:1, so the eye locks onto the EDGE rather than
    the fill. Value keyline, not hue."""
    core_h = 2 if tall else 2
    r = pygame.Surface((span, core_h + 1), pygame.SRCALPHA)
    for i in range(span):
        t = i / max(1.0, span - 1)
        c = lerp_color(GOLD_DEEP, RAIL_CORE, t ** 0.75)
        spark = max(0.0, (i - (span - 8)) / 8.0)
        if spark > 0:
            c = lerp_color(c, (255, 255, 255), spark ** 0.8)
        pygame.draw.rect(r, (*c, 255), (i, 0, 1, core_h))
        pygame.draw.rect(r, (*INK, 255), (i, core_h, 1, 1))
    surf.blit(r, (x0, y0))


def rail_terminus(surf, x, y, height=5):
    """A hard stop. The rail does not fade out — it hits a raised gold notch
    and the scarlet blade begins one pixel later, which is what a run ending
    actually feels like."""
    pygame.draw.rect(surf, INK, (x - 4, y - height - 1, 5, height + 1))
    for i, c in enumerate((GOLD, GOLD_PALE, RAIL_CORE)):
        pygame.draw.rect(surf, c, (x - 3 + i, y - height, 1, height))


def frame_shadow(surf):
    """Outline rings only, laid down AFTER everything that could brighten the
    band around the ribbon (guide cone, rail glow). In the night sector the
    ribbon body and the page sit at ~1.06:1, so the separation has to come
    from a dark moat plus a warm keyline — and a moat that anything is allowed
    to paint over is not a moat."""
    for off in range(7, 0, -1):
        a = (0, 140, 118, 98, 74, 50, 30, 15)[off]
        r = pygame.Rect(RIB_X - 1 - off, RIB_Y - 1 - off,
                        RIB_W + 2 + off * 2, RIB_H + 2 + off * 2 + 1)
        sh = pygame.Surface(r.size, pygame.SRCALPHA)
        pygame.draw.rect(sh, (0, 0, 0, a), sh.get_rect(), width=1,
                         border_radius=min(off, 3))
        surf.blit(sh, r.topleft)


def draw_ribbon(surf):
    surf.blit(sky_strip(RIB_W, RIB_H, 0.0, 1.0, 2), (RIB_X, RIB_Y))

    flown_w = int(DEATH_PHASE * RIB_W)

    # Progress is ADDITIVE only. A warm bloom lifts the flown span instead of
    # a scrim knocking the unflown day back -- the unflown day is the product.
    bloom = pygame.Surface((flown_w, RIB_H))
    for y in range(RIB_H):
        f = (1.0 - y / RIB_H) ** 1.7
        pygame.draw.line(bloom, (int(58 * f), int(42 * f), int(14 * f)),
                         (0, y), (flown_w, y))
    surf.blit(bloom, (RIB_X, RIB_Y), special_flags=pygame.BLEND_RGB_ADD)

    # Specular runs the FULL width, under the rail: it belongs to the ribbon as
    # an object, not to the flown span, so the unflown day gets the same
    # machined top edge and does not read as a leftover.
    aline(surf, (255, 255, 255), (RIB_X, RIB_Y), (RIB_R - 1, RIB_Y), alpha=51)

    flown_rail(surf, RIB_X, RIB_Y, RIB_W, flown_w - 3)

    # The rail's heat blooms DOWN into the sky it is lying on, not out onto the
    # page: bleeding warmth past the frame is what erased the ribbon's own
    # edge in round 1.
    glow = pygame.Surface((flown_w, 14), pygame.SRCALPHA)
    for y in range(14):
        pygame.draw.line(glow, (255, 196, 110, int(30 * (1 - y / 14) ** 1.6)),
                         (0, y), (flown_w, y))
    surf.blit(glow, (RIB_X, RIB_Y + 3))

    # Loupe window brackets — brightening marks, never a scrim.
    for phv in (LOUPE_P0, LOUPE_P1):
        wl = pygame.Surface((1, RIB_H), pygame.SRCALPHA)
        wl.fill((255, 255, 255, 120))
        surf.blit(wl, (int(px(phv)), RIB_Y))

    frame_shadow(surf)

    # Warm mid-value keyline, not black: a black outline on a near-black page
    # is invisible, which is exactly where the night sector was losing its
    # edge. A 46%-value warm line reads against both the sky and the page.
    pygame.draw.rect(surf, FRAME_WARM,
                     (RIB_X - 1, RIB_Y - 1, RIB_W + 2, RIB_H + 2), width=1)

    # Last, on top of the frame: the terminus is a raised feature of the rail,
    # so the ribbon's own moat must not grey it down.
    rail_terminus(surf, RIB_X + flown_w - 3, RIB_Y)


def draw_death_marker(surf):
    x = int(px(DEATH_PHASE))
    # BLEND_RGB_ADD reads RGB and ignores source alpha, so the falloff has to
    # live in the channel values; the blade goes on afterwards to stay pure.
    # Kept strictly inside the strip: an additive bloom spilling onto the page
    # would raise the very band the ribbon's keyline needs to stay dark.
    halo = pygame.Surface((15, RIB_H))
    for i, v in ((2, 14), (1, 26), (0, 46)):
        pygame.draw.rect(halo, (v, int(v * 0.16), int(v * 0.16)),
                         (6 - i * 2, 0, 3 + i * 4, RIB_H))
    surf.blit(halo, (x - 7, RIB_Y), special_flags=pygame.BLEND_RGB_ADD)

    # 1 px ink | 2 px scarlet | 1 px ink. The ink flanks are what make the mark
    # colourblind-safe: it is a black-white-black edge before it is red, so it
    # survives both a deuteranope and a squint at arm's length.
    top = RIB_Y - 7
    bot = RIB_Y + RIB_H + 4
    pygame.draw.rect(surf, INK, (x - 2, top, 1, bot - top))
    pygame.draw.rect(surf, INK, (x + 1, top, 1, bot - top))
    pygame.draw.rect(surf, SCARLET, (x - 1, top, 2, bot - top))

    ch = pygame.Surface((17 * SS, 13 * SS), pygame.SRCALPHA)
    pygame.draw.polygon(ch, INK, [(0, 0), (17 * SS, 0), (8.5 * SS, 13 * SS)])
    pygame.draw.polygon(ch, SCARLET, [(2 * SS, 1.6 * SS), (15 * SS, 1.6 * SS),
                                      (8.5 * SS, 10.6 * SS)])
    pygame.draw.polygon(ch, (255, 206, 206),
                        [(4 * SS, 3 * SS), (13 * SS, 3 * SS),
                         (8.5 * SS, 6 * SS)])
    surf.blit(pygame.transform.smoothscale(ch, (17, 13)), (x - 8, RIB_Y - 19))


# ═════════════════════════════════════════════════════════════════════════════
# loupe — owns the 0.140–0.200 window outright
# ═════════════════════════════════════════════════════════════════════════════
def draw_loupe_guides(surf):
    """Tapered guides — wide at the loupe, narrow where they touch the ribbon,
    so the eye reads the direction of the magnification. The cone is opaque
    enough to be one solid frustum: below ~50 alpha it broke into two unrelated
    diagonal lines with nothing between them.

    It darkens in value AND alpha as it descends, which is both how a light
    cone actually falls off and the only way the ribbon's own keyline can hold
    3:1 against the page it lands on — a flat gold wash right up to the frame
    swamps the frame."""
    bx, by = 18, LOUPE.bottom - 2
    bw, bh = 172, (RIB_Y - by) + 2

    def ramped(draw, a_top, a_bot):
        s = pygame.Surface((bw * SS, bh * SS), pygame.SRCALPHA)
        draw(s)
        ramp = pygame.Surface((bw * SS, bh * SS), pygame.SRCALPHA)
        for y in range(bh * SS):
            t = y / max(1, bh * SS - 1)
            v = int(255 * (1.0 - 0.80 * t ** 1.6))
            a = int(a_top + (a_bot - a_top) * t ** 1.8)
            pygame.draw.line(ramp, (v, v, v, a), (0, y), (bw * SS, y))
        s.blit(ramp, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(pygame.transform.smoothscale(s, (bw, bh)), (bx, by))

    def body(s):
        pygame.draw.polygon(s, (*GOLD, 255), [
            ((LOUPE.left - bx) * SS, 0), ((LOUPE.right - bx) * SS, 0),
            ((px(LOUPE_P1) - bx) * SS, bh * SS),
            ((px(LOUPE_P0) - bx) * SS, bh * SS)])

    def rails(s):
        for x0, x1 in ((LOUPE.left, px(LOUPE_P0)),
                       (LOUPE.right, px(LOUPE_P1))):
            pygame.draw.polygon(s, (*GOLD_PALE, 255), [
                ((x0 - bx - 1.6) * SS, 0), ((x0 - bx + 1.6) * SS, 0),
                ((x1 - bx + 0.8) * SS, bh * SS),
                ((x1 - bx - 0.8) * SS, bh * SS)])

    ramped(body, 68, 16)
    ramped(rails, 235, 46)


def shipping_panel(surf, rect, radius=10, alpha=246):
    """hud.py's stat-card recipe: _PANEL_LIGHTER -> _PANEL_DARK body, 2 px
    gold border, inner top sheen, inner bottom shadow. Built at SSx so the
    corners are genuinely round at these small radii."""
    w, h = rect.w * SS, rect.h * SS
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        c = lerp_color(PANEL_LIGHT, PANEL_DARK, y / max(1, h - 1))
        pygame.draw.line(s, (*c, alpha), (0, y), (w, y))
    m = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(m, (255, 255, 255, 255), m.get_rect(),
                     border_radius=radius * SS)
    s.blit(m, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    pygame.draw.rect(s, GOLD, s.get_rect(), width=2 * SS,
                     border_radius=radius * SS)
    pygame.draw.line(s, (*GOLD_PALE, 140), (10 * SS, 3 * SS),
                     (w - 10 * SS, 3 * SS), SS)
    pygame.draw.line(s, (0, 0, 0, 80), (10 * SS, h - 4 * SS),
                     (w - 10 * SS, h - 4 * SS), SS)
    surf.blit(pygame.transform.smoothscale(s, rect.size), rect.topleft)


def draw_loupe(surf):
    r = LOUPE
    soft_shadow(surf, r, 10, spread=6, peak=68, drop=3)
    shipping_panel(surf, r, 10)

    text(surf, "×5", SECT, GOLD, (r.x + 13, r.y + 16), "midleft", shadow=170)
    text(surf, "0.140 – 0.200", MICRO, MUTED_D, (r.right - 13, r.y + 16),
         "midright")

    bx, by, bw, bh = r.x + 10, r.y + 30, 136, 26
    surf.blit(sky_strip(bw, bh, LOUPE_P0, LOUPE_P1, 2), (bx, by))

    def lx(phv):
        return bx + (phv - LOUPE_P0) / (LOUPE_P1 - LOUPE_P0) * bw

    fw = int(lx(DEATH_PHASE) - bx)
    bl = pygame.Surface((fw, bh))
    for y in range(bh):
        f = (1.0 - y / bh) ** 1.7
        pygame.draw.line(bl, (int(58 * f), int(42 * f), int(14 * f)),
                         (0, y), (fw, y))
    surf.blit(bl, (bx, by), special_flags=pygame.BLEND_RGB_ADD)
    aline(surf, (255, 255, 255), (bx, by), (bx + bw - 1, by), alpha=51)
    flown_rail(surf, bx, by, bw, fw - 3)

    gx = int(lx(THERMAL_START_PHASE))
    pygame.draw.rect(surf, INK, (gx - 2, by, 1, bh))
    pygame.draw.rect(surf, INK, (gx + 1, by, 1, bh))
    pygame.draw.rect(surf, STEAM, (gx - 1, by, 2, bh))
    draw_glyph(surf, "geyser", 16, gx, by + bh // 2 + 1)

    rail_terminus(surf, bx + fw - 3, by, 4)
    # No chevron in here: the loupe exists to give these two marks room, and a
    # second arrowhead would only claw back the space it just bought. The blade
    # standing proud of the strip is terminus enough at x5.
    dx = int(lx(DEATH_PHASE))
    pygame.draw.rect(surf, INK, (dx - 2, by - 6, 1, bh + 6))
    pygame.draw.rect(surf, INK, (dx + 1, by - 6, 1, bh + 6))
    pygame.draw.rect(surf, SCARLET, (dx - 1, by - 6, 2, bh + 6))

    pygame.draw.rect(surf, FRAME_WARM, (bx - 1, by - 1, bw + 2, bh + 2),
                     width=1)

    ly = by + bh + 3
    aline(surf, STEAM, (gx, ly), (gx, ly + 4), alpha=150)
    aline(surf, SCARLET, (dx, ly), (dx, ly + 4), alpha=170)
    text(surf, "GEYSER", MICRO, STEAM, (gx, ly + 12), "center")
    text(surf, "YOU FELL", MICRO, SCARLET_PAL, (dx, ly + 12), "center")
    text(surf, f"PILLAR {DEATH_PILLAR}", MICRO, GOLD_PALE, (dx, ly + 24),
         "center")


# ═════════════════════════════════════════════════════════════════════════════
# ticks, phase labels, event rail
# ═════════════════════════════════════════════════════════════════════════════
LABELLED = {"DAY", "NIGHT", "SUNRISE"}

# Three events, well spaced, no legend: a lamp, a raindrop and a snowflake do
# not need a key to be understood, and the geyser now lives in the loupe.
EVENTS = [
    ("lamp", _phase_for_pillar(LATE_GAME_PILLAR), "GENIE LAMP", GOLD,
     "right"),
    ("rain", _phase_for_pillar(RAIN_START_PILLAR), "RAIN STORM", RAINBLUE,
     "left"),
    ("snow", SNOW_STORM_CENTER, "SNOWFALL", ICE, "center"),
]


def draw_ticks(surf):
    """Four of the seven boundaries carry no type at all. A tick is enough
    where the colour either side already says which phase it divides."""
    for frac, name in PHASE_BOUNDARIES:
        x = int(px(frac))
        if name in LABELLED:
            pygame.draw.line(surf, GOLD_PALE, (x, TICK_Y), (x, TICK_Y + 6), 1)
        else:
            t = pygame.Surface((1, 4), pygame.SRCALPHA)
            t.fill((*MUTED, 175))
            surf.blit(t, (x, TICK_Y))


def draw_event_rail(surf):
    for kind, phv, name, col, side in EVENTS:
        x = int(px(phv))
        pygame.draw.line(surf, col, (x, TICK_Y), (x, TICK_Y + 9), 1)
        aline(surf, col, (x, TICK_Y + 9), (x, GLYPH_Y - 11), alpha=95)

    # Type last: the halo knocks the leaders out from behind each label, which
    # is how a chart keeps a rule and a word in the same place.
    for frac, name in PHASE_BOUNDARIES:
        if name not in LABELLED:
            continue
        img = _render(name, MICRO, GOLD_PALE, 1.0)
        lx = min(px(frac) + 4, RIB_R - img.get_width())
        text(surf, name, MICRO, GOLD_PALE, (lx, LABEL_Y), "midleft",
             spacing=1.0, halo=125, shadow=160)

    for kind, phv, name, col, side in EVENTS:
        x = px(phv)
        draw_glyph(surf, kind, 20, x, GLYPH_Y)
        if side == "right":
            text(surf, name, MICRO, MUTED, (x - 14, GLYPH_Y), "midright",
                 shadow=170)
        elif side == "left":
            text(surf, name, MICRO, MUTED, (x + 14, GLYPH_Y), "midleft",
                 shadow=170)
        else:
            text(surf, name, MICRO, MUTED, (x, GLYPH_Y + 16), "center",
                 shadow=170)


# ═════════════════════════════════════════════════════════════════════════════
# panels
# ═════════════════════════════════════════════════════════════════════════════
def draw_teaser(surf):
    r = pygame.Rect(24, 424, 312, 74)
    soft_shadow(surf, r, 12, spread=5, peak=54, drop=3)
    shipping_panel(surf, r, 12)

    lr = text(surf, "STILL AHEAD", SECT, GOLD, (r.x + 16, r.y + 21), "midleft",
              spacing=2.0, shadow=180)
    aline(surf, GOLD, (lr.right + 10, r.y + 21), (r.right - 16, r.y + 21),
          alpha=90)

    # One named thing with a distance, one thing you can feel. Four bullets was
    # a schedule; two lines is a lure — specificity plus scarcity.
    ahead = LATE_GAME_PILLAR - DEATH_PILLAR
    runs(surf, [("GENIE LAMP", GOLD_PALE),
                (f"   {ahead} PILLARS AHEAD", BODY_TXT)],
         r.x + 16, r.y + 46, BODY_S)
    runs(surf, [("SNOWFALL", GOLD_PALE),
                ("   BEFORE DAWN", BODY_TXT)],
         r.x + 16, r.y + 64, BODY_S)


def draw_header(surf):
    tr = text(surf, "FLIGHT LOG", SECT, GOLD, (W // 2, 30), "center",
              spacing=3.4, shadow=190)
    for x0, x1 in ((30, tr.left - 12), (tr.right + 12, 330)):
        aline(surf, GOLD, (x0, 30), (x1, 30), alpha=95)
    text(surf, f"DAY {DAY_N}   ·   HOW FAR YOU GOT INTO THE DAY", MICRO, MUTED,
         (W // 2, 48), "center", spacing=0.8)
    aline(surf, MUTED, (30, 62), (330, 62), alpha=48)

    pct = int(round(DEATH_PHASE * 100))
    r = text(surf, f"{pct}%", HERO, GOLD_PALE, (30, 96), "midleft", shadow=200)
    text(surf, "OF THE DAY FLOWN", BODY_S, BODY_TXT, (r.right + 11, 86),
         "midleft", spacing=0.4)
    # The unseen share is the pitch, so it gets the second-largest type on the
    # screen and the brand colour; the flown share is only the receipt.
    text(surf, f"{100 - pct}% STILL UNSEEN", SECT, GOLD, (r.right + 11, 107),
         "midleft", spacing=0.4, shadow=180)
    text(surf, f"{TIME_ALIVE} s ALIVE", BODY_S, MUTED_D, (330, 96), "midright")


def draw_back_pill(surf):
    r = pygame.Rect(0, 0, 168, 42)
    r.center = (W // 2, 574)
    soft_shadow(surf, r, 21, spread=6, peak=72, drop=3)
    shipping_panel(surf, r, 21)
    text(surf, "BACK", SECT, GOLD_PALE, r.center, "center", spacing=2.0,
         shadow=190)


# ═════════════════════════════════════════════════════════════════════════════
# background
# ═════════════════════════════════════════════════════════════════════════════
def draw_background(surf):
    for y in range(H):
        t = y / (H - 1)
        c = lerp_color((6, 8, 15), (30, 40, 62), t ** 0.85)
        pygame.draw.line(surf, c, (0, y), (W, y))

    # Nothing twinkles inside the ribbon's shadow moat: a star sitting in the
    # dark band around a solid object is both physically wrong and enough on
    # its own to drop the frame under 3:1 for the few columns it touches.
    moat = pygame.Rect(RIB_X, RIB_Y, RIB_W, RIB_H).inflate(22, 22)

    rnd = random.Random(20260731)
    stars = pygame.Surface((W, H), pygame.SRCALPHA)
    for _ in range(120):
        x, y = rnd.randrange(W), rnd.randrange(H)
        if moat.collidepoint(x, y):
            continue
        a = rnd.randint(20, 130)
        rr = 1 if rnd.random() < 0.85 else 2
        pygame.draw.circle(stars, (200, 220, 255, a), (x, y), rr)
    for _ in range(7):
        x, y = rnd.randrange(W), rnd.randrange(int(H * 0.7))
        if moat.collidepoint(x, y):
            continue
        pygame.draw.circle(stars, (255, 255, 255, 190), (x, y), 1)
        pygame.draw.circle(stars, (170, 200, 255, 40), (x, y), 3)
    surf.blit(stars, (0, 0))

    # A low ridgeline gives the panel stack a horizon to sit above, and puts
    # the footer pill in the world rather than floating on a flat field. The
    # ranges have to be markedly DARKER than the sky or they vanish into it —
    # the earlier near-tone pair read as one flat field.
    glow = pygame.Surface((W, 96), pygame.SRCALPHA)
    for y in range(96):
        pygame.draw.line(glow, (52, 74, 116, int(46 * (y / 96) ** 2.0)),
                         (0, y), (W, y))
    surf.blit(glow, (0, 462))

    rnd2 = random.Random(4242)
    far = [(0, H)]
    x = -10
    while x < W + 20:
        far.append((x, 548 + rnd2.randint(-9, 12)))
        x += rnd2.randint(22, 40)
    far.append((W, H))
    pygame.draw.polygon(surf, (15, 20, 33), far)

    mid = [(0, H)]
    x = -10
    while x < W + 20:
        mid.append((x, 578 + rnd2.randint(-14, 8)))
        x += rnd2.randint(34, 58)
    mid.append((W, H))
    pygame.draw.polygon(surf, (11, 14, 24), mid)

    near = [(0, H), (-20, 632), (34, 598), (82, 614), (132, 590),
            (188, 610), (236, 596), (290, 616), (334, 598), (380, 626),
            (W, H)]
    pygame.draw.polygon(surf, (6, 8, 14), near)


# ═════════════════════════════════════════════════════════════════════════════
# squint / contrast audit — printed, never displayed
# ═════════════════════════════════════════════════════════════════════════════
def _lin(v):
    v /= 255.0
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def _lum(c):
    return 0.2126 * _lin(c[0]) + 0.7152 * _lin(c[1]) + 0.0722 * _lin(c[2])


def _cr(a, b):
    la, lb = _lum(a), _lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def audit(surf):
    dx = int(px(DEATH_PHASE))
    print("\n── death blade squint test  (x =", dx, ") ───────────────")
    worst = 99.0
    for dy in (2, 12, 22, 32, 42, 50):
        y = RIB_Y + dy
        left = surf.get_at((dx - 6, y))[:3]
        ink_l = surf.get_at((dx - 2, y))[:3]
        core = surf.get_at((dx, y))[:3]
        ink_r = surf.get_at((dx + 1, y))[:3]
        right = surf.get_at((dx + 6, y))[:3]
        c = max(_cr(core, left), _cr(core, right),
                _cr(ink_l, left), _cr(ink_r, right))
        worst = min(worst, c)
        print(f"  y+{dy:<3} L{left} ink{ink_l} core{core} ink{ink_r} "
              f"R{right}   best-edge {c:.2f}:1")
    print(f"  worst edge contrast along the blade: {worst:.2f}:1")

    print("\n── flown rail vs ribbon body ─────────────────────────────")
    worst_core = worst_ink = 99.0
    for x in range(RIB_X + 2, RIB_X + int(DEATH_PHASE * RIB_W) - 4, 6):
        core = surf.get_at((x, RIB_Y))[:3]
        under = surf.get_at((x, RIB_Y + 2))[:3]
        body = surf.get_at((x, RIB_Y + 4))[:3]
        worst_core = min(worst_core, _cr(core, body))
        worst_ink = min(worst_ink, _cr(under, body))
    print(f"  core  {RAIL_CORE} vs body : min {worst_core:.2f}:1")
    print(f"  ink undercut keyline vs body : min {worst_ink:.2f}:1  "
          f"(this is the value keyline)")
    print(f"  assembly (best of the two) at every x : "
          f"min {max(worst_core, worst_ink):.2f}:1")

    print("\n── ribbon frame vs page ──────────────────────────────────")
    # The terminus notch and the death blade deliberately stand proud of the
    # frame; they are marks, not frame, so they are audited separately above.
    marks = range(dx - 8, dx + 3)
    for lbl, ky, py in (("top", RIB_Y - 1, RIB_Y - 4),
                        ("bottom", RIB_Y + RIB_H, RIB_Y + RIB_H + 3)):
        worst_f, wx = 99.0, 0
        for x in range(RIB_X, RIB_R):
            if x in marks:
                continue
            c = _cr(surf.get_at((x, ky))[:3], surf.get_at((x, py))[:3])
            if c < worst_f:
                worst_f, wx = c, x
        print(f"  {lbl:<7} worst keyline-vs-page over 300 px: "
              f"{worst_f:.2f}:1  (at x={wx})")
    night_x = int(px(0.70))
    k, p = (surf.get_at((night_x, RIB_Y - 1))[:3],
            surf.get_at((night_x, RIB_Y - 4))[:3])
    print(f"  night sector x={night_x}: keyline {k} vs page {p} = "
          f"{_cr(k, p):.2f}:1   (was 1.06:1 body-vs-page in round 1)")


# ═════════════════════════════════════════════════════════════════════════════
def main():
    surf = pygame.Surface((W, H))
    draw_background(surf)
    draw_header(surf)
    draw_loupe_guides(surf)
    draw_ribbon(surf)
    draw_death_marker(surf)
    draw_loupe(surf)
    draw_ticks(surf)
    draw_event_rail(surf)
    draw_teaser(surf)
    draw_back_pill(surf)

    out = "/home/user/skybit/docs/flight_log_progress/sky_ruler/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(surf, out)
    print("saved", out, surf.get_size())
    audit(surf)


if __name__ == "__main__":
    main()
