#!/usr/bin/env python3
"""
sky-ruler  ·  flight_log_progress  ·  round 1

The ruler IS the sky. One 300x34 ribbon carries a full-saturation horizontal
sweep of the real biome palette, so the seven times of day are read as colour
rather than as seven labelled boxes. Nothing ahead of the player is dimmed,
hatched or greyed: the day the player has NOT seen yet is the most beautiful
thing on the screen, because that is the thing the screen is selling. Progress
is therefore marked additively -- a lit top rail over the flown 18% -- and the
one place where two marks would collide (geyser start 0.156 vs. death 0.184,
3.6 px apart at true scale) is solved the way a chart solves it: a x5 loupe
inset, joined to the ribbon by tapered guides, where the same two marks sit
42 px apart and can both be labelled.
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

from game.biome import PHASE_BOUNDARIES, palette_for_phase, CYCLE_SECONDS
from game.weather import (THERMAL_START_PHASE, THERMAL_END_PHASE,
                          SNOW_STORM_CENTER, _phase_for_pillar,
                          pillar_for_phase, GENIE_PILLAR)
from game.config import (LATE_GAME_PILLAR, CLOWN_START_PILLAR,
                         RAIN_START_PILLAR)
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


# ── palette ──────────────────────────────────────────────────────────────────
GOLD        = (240, 192,  64)
GOLD_PALE   = (255, 232, 168)
GOLD_WARM   = (255, 208, 120)
SCARLET     = (255,  78,  78)
SCARLET_PAL = (255, 158, 158)
INK         = (  6,   8,  14)
SLATE       = ( 24,  29,  44)
SLATE_D     = ( 15,  19,  31)
MUTED       = (146, 160, 186)
MUTED_D     = (100, 113, 138)
ICE         = (198, 230, 255)
STEAM       = (196, 240, 250)
VIOLET      = (232, 118, 226)
RAINBLUE    = (126, 186, 255)

# ── geometry ─────────────────────────────────────────────────────────────────
RIB_X, RIB_Y, RIB_W, RIB_H = 30, 210, 300, 34
RIB_R = RIB_X + RIB_W

LOUPE = pygame.Rect(33, 114, 96, 64)
LOUPE_P0, LOUPE_P1 = 0.140, 0.200       # phase window the loupe magnifies

DEATH_PHASE = 0.184
DAY_N       = 1
TIME_ALIVE  = 47
DEATH_PILLAR = 25


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


def soft_shadow(surf, rect, radius, spread=5, peak=34):
    """Outer ring first: draw.rect replaces pixels, so an inside-out stack
    would erase every brighter layer it was built on."""
    s = pygame.Surface((rect.w + spread * 2, rect.h + spread * 2),
                       pygame.SRCALPHA)
    for i in range(spread, 0, -1):
        a = int(peak * (1 - i / (spread + 1)) ** 0.7)
        pygame.draw.rect(s, (0, 0, 0, a),
                         (spread - i, spread - i + 2,
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


def glyph_diamond(size, col=VIOLET):
    S = size * SS
    g = _gsurf(size)
    lite = (255, 214, 250)
    top, rgt, bot, lft = (0.5, 0.03), (0.97, 0.5), (0.5, 0.97), (0.03, 0.5)
    ctr = (0.5, 0.5)
    _poly(g, S, [ctr, top, rgt], lite)
    _poly(g, S, [ctr, rgt, bot], col)
    _poly(g, S, [ctr, bot, lft], lite)
    _poly(g, S, [ctr, lft, top], col)
    pygame.draw.lines(g, (255, 255, 255, 210), True,
                      [(x * S, y * S) for x, y in (top, rgt, bot, lft)],
                      max(1, int(0.05 * S)))
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
    "clown":  glyph_diamond,
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
def build_sky_strip(w, h, p0, p1, step=2):
    """Each 2 px column is a miniature sky for its phase: sky_top -> sky_mid ->
    sky_bot down the strip's height. Sampling the live palette means the ruler
    can never drift out of sync with the sky the player actually flew through."""
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
    return s


def draw_ribbon(surf):
    strip = build_sky_strip(RIB_W, RIB_H, 0.0, 1.0, 2)
    surf.blit(strip, (RIB_X, RIB_Y))

    flown_w = DEATH_PHASE * RIB_W

    # Progress is ADDITIVE only. A warm bloom lifts the flown span instead of
    # a scrim knocking the unflown day back -- the unflown day is the product.
    bloom = pygame.Surface((int(flown_w), RIB_H))
    for y in range(RIB_H):
        f = (1.0 - y / RIB_H) ** 1.7
        pygame.draw.line(bloom, (int(58 * f), int(42 * f), int(14 * f)),
                         (0, y), (int(flown_w), y))
    surf.blit(bloom, (RIB_X, RIB_Y), special_flags=pygame.BLEND_RGB_ADD)

    # 3 px lit rail + 1 px raised bevel: the flown span reads as a machined
    # edge catching light, which needs no colour of its own to be seen.
    rail = pygame.Surface((int(flown_w), 5), pygame.SRCALPHA)
    for x in range(int(flown_w)):
        t = x / max(1.0, flown_w - 1)
        c = lerp_color(GOLD_WARM, (255, 252, 240), t ** 0.7)
        pygame.draw.rect(rail, (*c, 255), (x, 0, 1, 3))
        pygame.draw.rect(rail, (*lerp_color(GOLD, (210, 150, 70), t), 130),
                         (x, 3, 1, 1))
        pygame.draw.rect(rail, (60, 34, 12, 90), (x, 4, 1, 1))
    surf.blit(rail, (RIB_X, RIB_Y))

    glow = pygame.Surface((int(flown_w) + 24, 18), pygame.SRCALPHA)
    for i in range(8, -1, -1):
        a = int(30 * (1 - i / 9) ** 1.4)
        pygame.draw.rect(glow, (255, 196, 110, a),
                         (12 - i, 7 - i, int(flown_w) + i * 2, 3 + i * 2))
    surf.blit(glow, (RIB_X - 12, RIB_Y - 7))

    # Loupe window brackets — brightening marks, never a scrim.
    for phv in (LOUPE_P0, LOUPE_P1):
        wx = int(px(phv))
        wl = pygame.Surface((1, RIB_H), pygame.SRCALPHA)
        wl.fill((255, 255, 255, 105))
        surf.blit(wl, (wx, RIB_Y))

    pygame.draw.rect(surf, (0, 0, 0), (RIB_X - 1, RIB_Y - 1,
                                       RIB_W + 2, RIB_H + 2), width=1)
    edge = pygame.Surface((RIB_W + 4, RIB_H + 4), pygame.SRCALPHA)
    pygame.draw.rect(edge, (*GOLD, 46), edge.get_rect(), width=1)
    surf.blit(edge, (RIB_X - 2, RIB_Y - 2))


def draw_death_marker(surf):
    x = px(DEATH_PHASE)
    # BLEND_RGB_ADD reads RGB and ignores source alpha, so the falloff has to
    # live in the channel values; the blade goes on afterwards to stay pure.
    halo = pygame.Surface((11, RIB_H + 6))
    for i, v in ((2, 16), (1, 30), (0, 52)):
        pygame.draw.rect(halo, (v, int(v * 0.16), int(v * 0.16)),
                         (4 - i * 2, 0, 3 + i * 4, RIB_H + 6))
    surf.blit(halo, (int(x) - 6, RIB_Y - 3), special_flags=pygame.BLEND_RGB_ADD)

    pygame.draw.rect(surf, SCARLET, (int(x) - 1, RIB_Y, 2, RIB_H))

    # chevron head, pointing down into the strip
    ch = pygame.Surface((13 * SS, 10 * SS), pygame.SRCALPHA)
    pygame.draw.polygon(ch, SCARLET, [(1 * SS, 0), (12 * SS, 0),
                                      (6.5 * SS, 9.5 * SS)])
    pygame.draw.polygon(ch, (255, 200, 200), [(3 * SS, 1 * SS), (10 * SS, 1 * SS),
                                              (6.5 * SS, 3.4 * SS)])
    surf.blit(pygame.transform.smoothscale(ch, (13, 10)),
              (int(x) - 6, RIB_Y - 9))
    pygame.draw.rect(surf, SCARLET, (int(x) - 1, RIB_Y + RIB_H, 2, 3))


def draw_death_callout(surf):
    """Flows RIGHT, into the ahead region: the eye leaves the failure and lands
    on the day still unseen, which is the screen's whole argument."""
    x, y = px(DEATH_PHASE), 201
    pygame.draw.line(surf, (8, 10, 18), (int(x) + 8, y - 1), (121, y - 1), 5)
    pygame.draw.line(surf, SCARLET, (int(x) + 8, y), (119, y), 1)
    pygame.draw.circle(surf, SCARLET, (119, y), 2)
    text(surf, f"PILLAR {DEATH_PILLAR}  ·  YOU FELL HERE", 9, SCARLET_PAL,
         (125, y), "midleft", shadow=170)


# ═════════════════════════════════════════════════════════════════════════════
# loupe
# ═════════════════════════════════════════════════════════════════════════════
def draw_loupe_guides(surf):
    """Tapered guides — wide at the loupe, narrow where they touch the ribbon,
    so the eye reads the direction of the magnification."""
    bx, by = 24, LOUPE.bottom - 2
    bw, bh = 120, (RIB_Y - by) + 2
    s = pygame.Surface((bw * SS, bh * SS), pygame.SRCALPHA)

    def q(x0, x1, w0, w1):
        pygame.draw.polygon(s, (*GOLD_PALE, 215), [
            ((x0 - bx - w0) * SS, 0), ((x0 - bx + w0) * SS, 0),
            ((x1 - bx + w1) * SS, bh * SS), ((x1 - bx - w1) * SS, bh * SS)])

    pygame.draw.polygon(s, (*GOLD, 26), [
        ((LOUPE.left - bx) * SS, 0), ((LOUPE.right - bx) * SS, 0),
        ((px(LOUPE_P1) - bx) * SS, bh * SS), ((px(LOUPE_P0) - bx) * SS, bh * SS)])
    q(LOUPE.left, px(LOUPE_P0), 1.6, 0.8)
    q(LOUPE.right, px(LOUPE_P1), 1.6, 0.8)
    surf.blit(pygame.transform.smoothscale(s, (bw, bh)), (bx, by))


def draw_loupe(surf):
    r = LOUPE
    soft_shadow(surf, r, 8, spread=5, peak=40)
    panel(surf, r, 8, (46, 56, 82), (23, 29, 46), (0, 0, 0, 0), 255)

    # Range left, magnification right: it leaves the centre of the header row
    # clear for the death chevron, which has to sit above its own blade.
    text(surf, "0.140 – 0.200", 7, MUTED_D, (r.x + 8, r.y + 11), "midleft")
    text(surf, "x5", 9, GOLD, (r.right - 8, r.y + 11), "midright")

    bx, by, bw, bh = r.x + 3, r.y + 19, 90, 22
    surf.blit(build_sky_strip(bw, bh, LOUPE_P0, LOUPE_P1, 2), (bx, by))

    def lx(phv):
        return bx + (phv - LOUPE_P0) / (LOUPE_P1 - LOUPE_P0) * bw

    fw = int(lx(DEATH_PHASE) - bx)
    bl = pygame.Surface((fw, bh))
    for y in range(bh):
        f = (1.0 - y / bh) ** 1.7
        pygame.draw.line(bl, (int(58 * f), int(42 * f), int(14 * f)),
                         (0, y), (fw, y))
    surf.blit(bl, (bx, by), special_flags=pygame.BLEND_RGB_ADD)
    for i in range(fw):
        t = i / max(1, fw - 1)
        c = lerp_color(GOLD_WARM, (255, 252, 240), t ** 0.7)
        pygame.draw.rect(surf, c, (bx + i, by, 1, 3))
        pygame.draw.rect(surf, lerp_color(GOLD, (210, 150, 70), t),
                         (bx + i, by + 3, 1, 1))
    pygame.draw.rect(surf, (0, 0, 0), (bx - 1, by - 1, bw + 2, bh + 2), width=1)

    gx = lx(THERMAL_START_PHASE)
    pygame.draw.line(surf, (*STEAM, 200), (int(gx), by), (int(gx), by + bh), 1)
    draw_glyph(surf, "geyser", 15, gx, by + bh // 2)

    dx = int(lx(DEATH_PHASE))
    pygame.draw.rect(surf, SCARLET, (dx - 1, by, 2, bh))
    ch = pygame.Surface((11 * SS, 8 * SS), pygame.SRCALPHA)
    pygame.draw.polygon(ch, SCARLET, [(0, 0), (11 * SS, 0), (5.5 * SS, 8 * SS)])
    surf.blit(pygame.transform.smoothscale(ch, (11, 8)), (dx - 5, by - 8))

    ly = by + bh + 3
    aline(surf, STEAM, (int(gx), ly), (int(gx), ly + 3), alpha=130)
    aline(surf, SCARLET, (dx, ly), (dx, ly + 3), alpha=150)
    text(surf, "GEYSER", 7, STEAM, (gx, ly + 8), "center")
    text(surf, f"PILLAR {pillar_for_phase(THERMAL_START_PHASE)}", 6, MUTED_D,
         (gx, ly + 15), "center")
    text(surf, "YOU FELL", 7, SCARLET_PAL, (dx, ly + 8), "center")
    text(surf, f"PILLAR {DEATH_PILLAR}", 6, MUTED_D, (dx, ly + 15), "center")

    ring = pygame.Surface((r.w * SS, r.h * SS), pygame.SRCALPHA)
    pygame.draw.rect(ring, (*GOLD, 160), ring.get_rect(), width=SS,
                     border_radius=8 * SS)
    pygame.draw.rect(ring, (255, 255, 255, 34), (SS, SS, (r.w - 2) * SS,
                                                 (r.h - 2) * SS),
                     width=SS, border_radius=7 * SS)
    surf.blit(pygame.transform.smoothscale(ring, r.size), r.topleft)


# ═════════════════════════════════════════════════════════════════════════════
# ticks, phase labels, event rail
# ═════════════════════════════════════════════════════════════════════════════
LABELLED = {"DAY", "NIGHT", "SUNRISE"}


def draw_ticks(surf):
    """Four of the seven boundaries carry no type at all. A tick is enough
    where the colour either side already says which phase it divides."""
    for frac, name in PHASE_BOUNDARIES:
        x = int(px(frac))
        if name in LABELLED:
            pygame.draw.line(surf, GOLD_PALE, (x, RIB_Y + RIB_H + 1),
                             (x, RIB_Y + RIB_H + 8), 1)
        else:
            t = pygame.Surface((1, 5), pygame.SRCALPHA)
            t.fill((*MUTED, 165))
            surf.blit(t, (x, RIB_Y + RIB_H + 1))


def _phase_label_pos(frac, name):
    img = _render(name, 9, GOLD_PALE, 1.0)
    lx = px(frac) + 3
    if lx + img.get_width() > RIB_R:
        lx = RIB_R - img.get_width()
    return lx


EVENTS = [
    ("geyser", THERMAL_START_PHASE, None),
    ("lamp",   _phase_for_pillar(LATE_GAME_PILLAR), None),
    ("clown",  _phase_for_pillar(CLOWN_START_PILLAR), -6.0),
    ("rain",   _phase_for_pillar(RAIN_START_PILLAR), +9.0),
    ("snow",   SNOW_STORM_CENTER, None),
]
GLYPH_Y = 282


def draw_event_rail(surf):
    # Geyser is a WINDOW, not a moment: a translucent span band under the strip
    # says "this whole stretch erupts" without stealing the strip's colour.
    gx0, gx1 = px(THERMAL_START_PHASE), px(THERMAL_END_PHASE)
    band = pygame.Surface((int(gx1 - gx0) + 1, 9), pygame.SRCALPHA)
    pygame.draw.rect(band, (*STEAM, 62), (0, 2, band.get_width(), 3))
    pygame.draw.rect(band, (*STEAM, 150), (0, 0, 1, 8))
    pygame.draw.rect(band, (*STEAM, 150), (band.get_width() - 1, 0, 1, 8))
    surf.blit(band, (int(gx0), RIB_Y + RIB_H + 2))

    # Clown (0.403) and rain (0.430) land 8 px apart at true scale, so their
    # glyphs step aside and an angled leader keeps each pinned to its real x.
    for kind, phv, off in EVENTS:
        x = px(phv)
        gxp = x + (off or 0.0)
        top = (int(x), RIB_Y + RIB_H + 2)
        bot = (int(gxp), GLYPH_Y - 9)
        aline(surf, MUTED, top, bot, alpha=185)
        pygame.draw.circle(surf, MUTED, top, 1)

    # Type last: the halo knocks the leaders out from behind each label, which
    # is how a chart keeps a rule and a word in the same place.
    for frac, name in PHASE_BOUNDARIES:
        if name not in LABELLED:
            continue
        aline(surf, GOLD_PALE, (int(px(frac)), 249), (int(px(frac)), 252),
              alpha=130)
        text(surf, name, 9, GOLD_PALE, (_phase_label_pos(frac, name), 257),
             "midleft", spacing=1.0, halo=115, shadow=160)

    for kind, phv, off in EVENTS:
        draw_glyph(surf, kind, 16, px(phv) + (off or 0.0), GLYPH_Y)


# ═════════════════════════════════════════════════════════════════════════════
# panels
# ═════════════════════════════════════════════════════════════════════════════
def panel(surf, rect, radius=10, top=SLATE, bot=SLATE_D, ring=(*GOLD, 70),
          alpha=232):
    """Built at SSx and smoothscaled so the corners are genuinely round —
    pygame's border_radius alone leaves stair-steps at these small radii."""
    w, h = rect.w * SS, rect.h * SS
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        c = lerp_color(top, bot, y / max(1, h))
        pygame.draw.line(s, (*c, alpha), (0, y), (w, y))
    m = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(m, (255, 255, 255, 255), m.get_rect(),
                     border_radius=radius * SS)
    s.blit(m, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    if ring[3] if len(ring) > 3 else True:
        pygame.draw.rect(s, ring, s.get_rect(), width=SS,
                         border_radius=radius * SS)
    surf.blit(pygame.transform.smoothscale(s, rect.size), rect.topleft)


def draw_teaser(surf):
    r = pygame.Rect(24, 298, 312, 52)
    soft_shadow(surf, r, 10, spread=4, peak=30)
    panel(surf, r, 10, (54, 42, 78), (34, 26, 54), (*GOLD, 110), 250)
    lr = text(surf, "STILL AHEAD", 9, GOLD, (r.x + 12, r.y + 13), "midleft",
              spacing=1.6)
    aline(surf, GOLD, (lr.right + 8, r.y + 13), (r.right - 12, r.y + 13),
          alpha=80)
    # The nouns carry the tease; the connective tissue steps back a value.
    body = (222, 229, 242)
    runs(surf, [("GENIE LAMP", GOLD_PALE), (f"  AT PILLAR {LATE_GAME_PILLAR}", body),
                ("   ·   ", MUTED_D), ("CLOWN GAUNTLET", GOLD_PALE),
                (f"  AT {CLOWN_START_PILLAR}", body)], r.x + 12, r.y + 29, 9)
    runs(surf, [("STORM", GOLD_PALE), (f"  AT {RAIN_START_PILLAR}", body),
                ("   ·   ", MUTED_D), ("SNOWFALL", GOLD_PALE),
                ("  BEFORE DAWN", body)], r.x + 12, r.y + 42, 9)


LEGEND = [("geyser", "GEYSER PLUME"), ("lamp", "GENIE LAMP"),
          ("clown", "CLOWN GAUNTLET"), ("rain", "RAIN STORM"),
          ("snow", "SNOWFALL")]


def draw_legend(surf):
    lr = text(surf, "EVENT KEY", 8, MUTED_D, (30, 366), "midleft", spacing=1.4)
    aline(surf, MUTED, (lr.right + 8, 366), (330, 366), alpha=52)
    for i, (kind, name) in enumerate(LEGEND):
        col, row = i % 2, i // 2
        cx = 38 + col * 156
        cy = 386 + row * 21
        draw_glyph(surf, kind, 15, cx, cy)
        text(surf, name, 9, (206, 216, 234), (cx + 12, cy), "midleft")


def draw_phase_table(surf):
    lr = text(surf, "PHASE TABLE", 8, MUTED_D, (30, 452), "midleft",
              spacing=1.4)
    aline(surf, MUTED, (lr.right + 8, 452), (330, 452), alpha=52)

    bounds = [f for f, _ in PHASE_BOUNDARIES] + [1.0]
    rows = []
    for i, (frac, name) in enumerate(PHASE_BOUNDARIES):
        p_start = max(1, pillar_for_phase(frac))
        p_end = pillar_for_phase(bounds[i + 1]) - 1
        rows.append((frac, bounds[i + 1], name, p_start, p_end))

    for i, (f0, f1, name, p0, p1) in enumerate(rows):
        col, row = i % 2, i // 2
        x = 28 + col * 156
        y = 470 + row * 21
        sw = build_sky_strip(20, 11, f0 + (f1 - f0) * 0.18,
                             f0 + (f1 - f0) * 0.82, 2)
        surf.blit(sw, (x, y - 5))
        pygame.draw.rect(surf, (0, 0, 0), (x - 1, y - 6, 22, 13), width=1)
        flown = DEATH_PHASE >= f1
        part = f0 <= DEATH_PHASE < f1
        if flown or part:
            pygame.draw.rect(surf, GOLD_WARM, (x, y - 5, 20, 2))
        text(surf, name, 8, (206, 216, 234) if (flown or part) else MUTED,
             (x + 27, y), "midleft")
        text(surf, f"{p0}–{p1}", 8, MUTED_D, (x + 146, y), "midright")


def draw_header(surf):
    tr = text(surf, "FLIGHT LOG", 23, GOLD, (W // 2, 31), "center",
              spacing=3.0, shadow=190)
    for x0, x1 in ((30, tr.left - 10), (tr.right + 10, 330)):
        aline(surf, GOLD, (x0, 31), (x1, 31), alpha=95)
    text(surf, f"DAY {DAY_N}  —  HOW FAR YOU GOT INTO THE DAY", 9, MUTED,
         (W // 2, 51), "center", spacing=0.8)
    aline(surf, MUTED, (30, 64), (330, 64), alpha=42)

    pct = int(round(DEATH_PHASE * 100))
    r = text(surf, f"{pct}%", 32, GOLD_PALE, (30, 88), "midleft", shadow=200)
    text(surf, "OF THE DAY FLOWN", 9, (216, 224, 240), (r.right + 9, 80),
         "midleft", spacing=0.6)
    text(surf, f"{100 - pct}% STILL UNSEEN", 9, GOLD, (r.right + 9, 95),
         "midleft", spacing=0.6)
    text(surf, f"PILLAR {DEATH_PILLAR}", 11, (216, 224, 240), (330, 80),
         "midright")
    text(surf, f"{TIME_ALIVE} s ALIVE", 9, MUTED, (330, 95), "midright")


def draw_back_pill(surf):
    r = pygame.Rect(0, 0, 160, 36)
    r.center = (W // 2, 598)
    soft_shadow(surf, r, 18, spread=5, peak=44)
    panel(surf, r, 18, (40, 32, 56), (22, 16, 38), (*GOLD, 185), 244)
    text(surf, "BACK", 18, GOLD_PALE, r.center, "center")


# ═════════════════════════════════════════════════════════════════════════════
# background
# ═════════════════════════════════════════════════════════════════════════════
def draw_background(surf):
    for y in range(H):
        t = y / (H - 1)
        c = lerp_color((6, 8, 15), (30, 40, 62), t ** 0.85)
        pygame.draw.line(surf, c, (0, y), (W, y))

    rnd = random.Random(20260731)
    stars = pygame.Surface((W, H), pygame.SRCALPHA)
    for _ in range(120):
        x, y = rnd.randrange(W), rnd.randrange(H)
        a = rnd.randint(20, 130)
        rr = 1 if rnd.random() < 0.85 else 2
        pygame.draw.circle(stars, (200, 220, 255, a), (x, y), rr)
    for _ in range(7):
        x, y = rnd.randrange(W), rnd.randrange(int(H * 0.7))
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
def main():
    surf = pygame.Surface((W, H))
    draw_background(surf)
    draw_header(surf)
    draw_loupe_guides(surf)
    draw_ribbon(surf)
    draw_death_marker(surf)
    draw_death_callout(surf)
    draw_loupe(surf)
    draw_ticks(surf)
    draw_event_rail(surf)
    draw_teaser(surf)
    draw_legend(surf)
    draw_phase_table(surf)
    draw_back_pill(surf)

    out = "/home/user/skybit/docs/flight_log_progress/sky_ruler/round_1.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(surf, out)
    print("saved", out, surf.get_size())


if __name__ == "__main__":
    main()
