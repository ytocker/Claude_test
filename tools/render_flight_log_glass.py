#!/usr/bin/env python3
"""
glass — rain-streaked cockpit canopy.

Two hard-separated layers on the 360x640 canvas:

  Layer 1  the world BEHIND the glass: warm atmospheric backdrop plus a
           knocked-back r7 sun-arc, all of it content seen THROUGH the wet
           canopy.
  Layer 2  the canopy itself: ~110 supersampled rain streaks, a raking
           specular sheen and a corner vignette, blitted over everything.

There is no gaussian blur and no smoothscale ping-pong anywhere in this
renderer.  The softness is entirely diegetic: it is rain on glass, drawn as
geometry, and the only downscale in the file is the single 3x resolve of the
canopy layer.

The death marker is the one element that sits IN FRONT of the canopy — the
pilot's own ending is not something the weather is allowed to soften.  Events
the run never reached stay behind the glass, dim and unnamed.
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

from game.draw import lerp_color, lerp_color_multi

W, H = 360, 640
SS = 3
HORIZON_Y = 430

ROOT = "/home/user/skybit"
FONT_PATH = "/home/user/skybit/game/assets/LiberationSans-Bold.ttf"
_fonts: dict = {}

# ── palette ──────────────────────────────────────────────────────────────────
INK = (6, 8, 14)
GOLD = (255, 206, 92)
CREAM = (246, 240, 230)
COOL = (150, 168, 196)
SLATE = (58, 62, 82)
SCRIM = (26, 22, 34)
GEYSER_C = (146, 232, 255)
CLOWN_C = (255, 118, 196)
RAIN_C = (150, 190, 255)
SNOW_C = (222, 244, 255)

# ── arc geometry (identical to r7) ───────────────────────────────────────────
CX, CY, R = 180, 430, 175
R_INNER = 159
EASE_P = 0.652


def ease(p):
    return max(0.0, min(1.0, p)) ** EASE_P


def pos_u(u, radius=R):
    a = math.pi * (1.0 - u)
    return (CX + radius * math.cos(a), CY - radius * math.sin(a))


def arc_pos(p, radius=R):
    return pos_u(ease(p), radius)


def radial_unit(p):
    a = math.pi * (1.0 - ease(p))
    return (math.cos(a), -math.sin(a))


# ── run data ─────────────────────────────────────────────────────────────────
DEATH_PHASE = 0.184
DEATH_PILLAR = 25
DAY_N = 1
TIME_ALIVE = 47
PHASE_LABEL = "DAY"

CLOWN_PHASE = 0.403
RAIN_PHASE = 0.430
SNOW_PHASE = 0.820

DEATH_X, DEATH_Y = arc_pos(DEATH_PHASE)


# ── text / chrome helpers (copied from r7) ───────────────────────────────────

def font(size):
    if size not in _fonts:
        _fonts[size] = pygame.font.Font(FONT_PATH, size)
    return _fonts[size]


def text(surf, s, size, center=None, midleft=None, midright=None,
         color=CREAM, shadow=(0, 0, 0, 150), track=0):
    f = font(size)
    if track:
        glyphs = [f.render(ch, True, color) for ch in s]
        tw = sum(g.get_width() for g in glyphs) + track * (len(s) - 1)
        th = f.get_height()
        img = pygame.Surface((max(1, tw), th), pygame.SRCALPHA)
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
        sh = img.copy()
        sh.fill((*shadow[:3], 255), special_flags=pygame.BLEND_RGBA_MULT)
        sh.set_alpha(shadow[3])
        surf.blit(sh, (rect.x + 1, rect.y + 1))
    surf.blit(img, rect)
    return rect


def chip(surf, rect, radius=6, fill=(18, 15, 24), alpha=234,
         border=CREAM, border_a=54):
    s = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(s, (*fill, alpha), s.get_rect(), border_radius=radius)
    if border_a:
        pygame.draw.rect(s, (*border, border_a), s.get_rect(), width=1,
                         border_radius=radius)
    surf.blit(s, rect.topleft)


def soft_glow(radius, color, peak=110, falloff=2.0):
    """Additive glow with the falloff premultiplied into RGB — BLEND_ADD
    ignores source alpha, so an alpha ramp would blit as a flat disc."""
    size = radius * 2 + 2
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    c = radius + 1
    for r in range(radius, 0, -1):
        f = (1 - (r / radius) ** falloff) * (peak / 255.0)
        s_col = (int(color[0] * f), int(color[1] * f), int(color[2] * f), 255)
        pygame.draw.circle(s, s_col, (c, c), r)
    return s


def alpha_line(surf, rgba, p0, p1, width=1):
    lay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.line(lay, rgba, p0, p1, width)
    surf.blit(lay, (0, 0))


# ── LAYER 1 · behind the canopy ──────────────────────────────────────────────

SKY_STOPS = [
    (0.00, (14, 18, 40)),      # deep navy at the top of the dome
    (0.34, (30, 34, 62)),
    (0.62, (72, 62, 82)),
    (0.86, (150, 106, 90)),
    (1.00, (206, 150, 98)),    # warm amber sitting on the horizon
]

GROUND_STOPS = [
    (0.00, (58, 40, 34)),
    (0.28, (40, 29, 27)),
    (1.00, (14, 12, 16)),
]


def draw_backdrop(surf):
    """Sky above the horizon, dark ground below, plus a low amber bloom that
    keeps the horizon reading as light source rather than as a seam."""
    for y in range(HORIZON_Y):
        c = lerp_color_multi(SKY_STOPS, y / (HORIZON_Y - 1))
        pygame.draw.line(surf, c, (0, y), (W - 1, y))
    gh = H - HORIZON_Y
    for i in range(gh):
        c = lerp_color_multi(GROUND_STOPS, i / (gh - 1))
        pygame.draw.line(surf, c, (0, HORIZON_Y + i), (W - 1, HORIZON_Y + i))

    # Horizon bloom — additive, warm, and centred slightly left so it agrees
    # with the flown quarter of the arc rather than fighting it.
    bloom = pygame.Surface((W, 40), pygame.SRCALPHA)
    for x in range(W):
        fx = 1.0 - 0.55 * min(1.0, abs(x - 128) / 240.0)
        for i in range(38):
            f = 0.30 * fx * (1 - i / 38) ** 2.1
            bloom.set_at((x, 37 - i),
                         (int(228 * f), int(158 * f), int(96 * f), 255))
    surf.blit(bloom, (0, HORIZON_Y - 38), special_flags=pygame.BLEND_ADD)
    pygame.draw.line(surf, (196, 146, 100), (0, HORIZON_Y - 1), (W - 1, HORIZON_Y - 1))
    pygame.draw.line(surf, (26, 20, 20), (0, HORIZON_Y), (W - 1, HORIZON_Y))


def draw_arc_behind(surf):
    """The r7 sun-arc geometry, flattened to ~40% presence.

    Flown portion warm gold, the rest cool slate, both routed through a single
    SRCALPHA scratch layer so the authored alphas actually survive — drawing
    straight onto an opaque surface would stamp them at full strength.
    """
    lay = pygame.Surface((W, H), pygame.SRCALPHA)
    u_death = ease(DEATH_PHASE)

    # Cool remainder of the day: a plan, not an achievement.
    steps = 120
    for i in range(steps):
        u0 = u_death + (1.0 - u_death) * i / steps
        u1 = u_death + (1.0 - u_death) * (i + 1) / steps
        t = i / (steps - 1)
        a = int(96 - 54 * t)
        pygame.draw.line(lay, (*SLATE, a), pos_u(u0), pos_u(u1), 4)
        pygame.draw.line(lay, (*COOL, int(a * 0.85)), pos_u(u0), pos_u(u1), 2)

    # Dotted event rail inside the arc.
    for i in range(0, 181):
        u = i / 180
        x, y = pos_u(u, R_INNER)
        col = (255, 226, 176, 62) if u <= u_death else (176, 190, 214, 26)
        pygame.draw.circle(lay, col, (int(x), int(y)), 1)

    # Flown portion — warm gold, knocked back but still the warmer of the two.
    for i in range(72):
        u0 = u_death * i / 72
        u1 = u_death * (i + 1) / 72
        t = i / 71
        col = lerp_color((214, 148, 74), (255, 214, 158), t ** 0.75)
        pygame.draw.line(lay, (*col, int(120 + 60 * t)), pos_u(u0), pos_u(u1),
                         int(3 + 2 * t))
    for i in range(72):
        u0 = u_death * i / 72
        u1 = u_death * (i + 1) / 72
        t = i / 71
        pygame.draw.line(lay, (255, 244, 218, int(60 + 70 * t)),
                         pos_u(u0), pos_u(u1), 1)

    # Left terminal — sunrise, on the lit side.
    lx, ly = pos_u(0.0)
    pygame.draw.polygon(lay, (255, 226, 168, 150),
                        [(lx, ly - 4), (lx + 3, ly), (lx, ly + 4), (lx - 3, ly)])
    # Right terminal — DAY COMPLETE, cool and unearned.
    rx, ry = pos_u(1.0)
    pygame.draw.polygon(lay, (*COOL, 130),
                        [(rx, ry - 5), (rx + 4, ry), (rx, ry + 5), (rx - 4, ry)])

    surf.blit(lay, (0, 0))


UNREACHED = [
    (CLOWN_PHASE, R_INNER, CLOWN_C),
    (RAIN_PHASE, R_INNER - 22, RAIN_C),
    (SNOW_PHASE, R_INNER, SNOW_C),
]


def draw_events_behind(surf):
    """Phase events as dim hue-tinted dots.  Reached events get a filled dot;
    unreached ones get a width=1 ring and a '?' at a third brightness, and
    they stay behind the rain — naming them would be the whole spoiler."""
    lay = pygame.Surface((W, H), pygame.SRCALPHA)

    # Reached: the geyser zone opened at 0.167, just before the run ended.
    gx, gy = arc_pos(0.167, R_INNER)
    pygame.draw.circle(lay, (*GEYSER_C, 150), (int(gx), int(gy)), 3)
    pygame.draw.circle(lay, (*GEYSER_C, 70), (int(gx), int(gy)), 6, width=1)

    for p, rad, col in UNREACHED:
        x, y = arc_pos(p, rad)
        pygame.draw.circle(lay, (*col, 62), (int(x), int(y)), 6, width=1)
        if rad != R_INNER:
            ax, ay = arc_pos(p, R_INNER)
            pygame.draw.line(lay, (*col, 34), (ax, ay), (x, y), 1)
    surf.blit(lay, (0, 0))

    for p, rad, col in UNREACHED:
        x, y = arc_pos(p, rad)
        text(surf, "?", 11, center=(int(x), int(y)),
             color=tuple(c // 3 for c in col), shadow=None)


# ── LAYER 2 · the canopy ─────────────────────────────────────────────────────

def draw_canopy(surf):
    """~110 rain streaks on one 3x SRCALPHA surface, resolved with a single
    smoothscale.

    The lean is 2-5px of horizontal drift across a streak's whole length: this
    is water creeping on a curved canopy at cruise, not motion lines.  Anything
    steeper reads as speed and pulls the eye sideways off the death point.
    """
    rng = random.Random(7)
    lay = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
    SW, SH = W * SS, H * SS

    for i in range(110):
        x = rng.uniform(-10, SW + 10)
        # Denser in the upper two thirds: a squared draw biases the mass up.
        if rng.random() < 0.72:
            y = rng.uniform(0, SH * 0.66)
        else:
            y = rng.uniform(SH * 0.66, SH)
        length = rng.uniform(20, 90)
        lean = rng.uniform(2, 5) * (1 if rng.random() < 0.62 else -1)
        # Staggered alphas — a uniform draw over 18-46 makes the field read as
        # one flat scrim instead of as individual runnels of water.
        a = [18, 24, 30, 36, 42, 46][i % 6] + rng.randint(-3, 3)
        a = max(14, min(50, a))
        wid = 2 if rng.random() < 0.66 else 3
        pygame.draw.line(lay, (*RAIN_C, a), (x, y), (x + lean, y + length), wid)
        # A brighter head where the bead sits at the leading edge of the run.
        if rng.random() < 0.34:
            pygame.draw.circle(lay, (*SNOW_C, min(70, a + 22)),
                               (int(x + lean), int(y + length)), 2)

    # Beads between the streaks — 1-2px in output, so 3-6px here.
    for _ in range(20):
        bx = rng.uniform(0, SW)
        by = rng.uniform(0, SH * 0.9)
        br = rng.choice((3, 4, 5, 6))
        pygame.draw.circle(lay, (*SNOW_C, 60), (int(bx), int(by)), br)

    surf.blit(pygame.transform.smoothscale(lay, (W, H)), (0, 0))


def draw_specular(surf):
    """Raking sheen along the inner screen edge, top-left to mid-right.

    One line only.  A second offset rake was tried and reads as a pair of
    scratches in the acrylic rather than as light travelling across it.
    """
    alpha_line(surf, (240, 244, 248, 28), (0, 0), (180, 320), 2)


def draw_vignette(surf):
    """Dark corners.  Authored small and scaled up — a per-pixel pass at 1:1
    costs 230k set_at calls to produce the identical soft falloff."""
    vw, vh = 90, 160
    v = pygame.Surface((vw, vh), pygame.SRCALPHA)
    cx, cy = vw / 2, vh / 2
    md = math.hypot(cx, cy)
    for y in range(vh):
        for x in range(vw):
            d = math.hypot(x - cx, y - cy) / md
            a = int(150 * max(0.0, (d - 0.38) / 0.62) ** 1.8)
            if a:
                v.set_at((x, y), (4, 6, 14, a))
    surf.blit(pygame.transform.smoothscale(v, (W, H)), (0, 0))


# ── death marker · in front of the canopy ────────────────────────────────────

def draw_death(surf):
    dx, dy = int(DEATH_X), int(DEATH_Y)
    for rad, col, peak in ((22, (255, 176, 74), 70),
                           (14, (255, 206, 92), 50),
                           (8, (255, 232, 168), 35)):
        g = soft_glow(rad, col, peak=peak, falloff=2.0)
        surf.blit(g, (dx - rad - 1, dy - rad - 1), special_flags=pygame.BLEND_ADD)
    pygame.draw.circle(surf, (*INK, 255), (dx, dy), 8)
    pygame.draw.circle(surf, GOLD, (dx, dy), 6)
    pygame.draw.circle(surf, (252, 246, 232), (dx - 1, dy - 1), 3)

    f10, f8 = font(10), font(8)
    body = f"PILLAR {DEATH_PILLAR}  ·  {PHASE_LABEL} 18.4%"
    cw = max(f10.size("ENDED HERE")[0], f8.size(body)[0]) + 20
    cr = pygame.Rect(0, 0, cw, 34)
    cr.topleft = (132, 322)

    # Connector, ink first so the gold hairline holds over the rain field.
    alpha_line(surf, (10, 8, 14, 190), (dx + 6, dy + 7), (cr.x - 1, cr.y + 7), 3)
    alpha_line(surf, (255, 214, 140, 225), (dx + 6, dy + 6), (cr.x - 2, cr.y + 6), 1)

    chip(surf, cr, radius=7, alpha=238, border_a=72)
    text(surf, "ENDED HERE", 10, midleft=(cr.x + 10, cr.y + 11), color=GOLD,
         shadow=None)
    text(surf, body, 8, midleft=(cr.x + 10, cr.y + 24), color=CREAM, shadow=None)


# ── chrome ───────────────────────────────────────────────────────────────────

def draw_banner(surf):
    pygame.draw.rect(surf, SCRIM, (0, 0, W, 74))
    fade = pygame.Surface((W, 10), pygame.SRCALPHA)
    for i in range(10):
        fade.fill((*SCRIM, int(238 * (1 - i / 10) ** 1.4)), pygame.Rect(0, i, W, 1))
    surf.blit(fade, (0, 74))
    alpha_line(surf, (255, 206, 92, 150), (0, 74), (W - 1, 74), 1)
    text(surf, f"FLIGHT LOG  ·  DAY {DAY_N}", 21, center=(W // 2, 28), color=GOLD,
         track=3, shadow=None)
    text(surf, f"PILLAR {DEATH_PILLAR}   ·   0:{TIME_ALIVE:02d}", 12,
         center=(W // 2, 55), color=CREAM, shadow=None)


def draw_back(surf):
    pr = pygame.Rect(0, 0, 122, 36)
    pr.center = (180, 597)
    sh = pygame.Surface((pr.w + 8, pr.h + 8), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 100), sh.get_rect(), border_radius=21)
    surf.blit(sh, (pr.x - 4, pr.y - 1))
    grad = pygame.Surface(pr.size, pygame.SRCALPHA)
    for y in range(pr.h):
        grad.fill(lerp_color((255, 228, 172), (226, 168, 96), y / (pr.h - 1)) + (255,),
                  pygame.Rect(0, y, pr.w, 1))
    mask = pygame.Surface(pr.size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=18)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(grad, pr.topleft)
    pygame.draw.rect(surf, (110, 68, 38), pr, width=1, border_radius=18)
    text(surf, "BACK", 13, center=(pr.centerx, pr.centery), color=(66, 40, 20),
         shadow=None, track=2)


# ── screen ───────────────────────────────────────────────────────────────────

def render_screen():
    surf = pygame.Surface((W, H))

    # Layer 1 — everything seen through the glass.
    draw_backdrop(surf)
    draw_arc_behind(surf)
    draw_events_behind(surf)

    # Layer 2 — the canopy itself.
    draw_canopy(surf)
    draw_specular(surf)
    draw_vignette(surf)

    # In front of the glass.
    draw_death(surf)

    # Chrome last so it is always crisp.
    draw_banner(surf)
    draw_back(surf)
    return surf


def main():
    surf = render_screen()
    out = "/home/user/skybit/docs/flight_log_arc_v2/glass/round_1.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(surf, out)
    print(f"saved {out}  {pygame.image.load(out).get_size()}")


if __name__ == "__main__":
    main()
