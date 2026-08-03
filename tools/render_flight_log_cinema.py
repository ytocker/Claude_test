#!/usr/bin/env python3
"""
cinema round 1 — HORIZON BURN.

A dead-flat horizon on near-black ink. Phase maps LINEARLY to x, so the
18% that was flown occupies exactly the left 18% of the screen. The flown
span is drawn as a heat ramp: dimmest at dawn (x=0), peaking at the death
terminus (x=66), where a three-layer glow sits and a thin light column
rises. Past the terminus a slate hairline gutters out entirely by x=280 —
the day literally ends in darkness.

Deliberately absent:
  - DAY COMPLETE. There is nothing at the right terminus yet; that is the
    point of the screen.
  - Labels on the four unreached event ticks. Pure mystery.
  - Any curvature. A dome reads as a journey with a shape; a flat line
    reads as a day with a length.
"""
import os
import math

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.draw import lerp_color

W, H = 360, 640
SS = 3
ROOT = "/home/user/skybit"
FONT_PATH = "/home/user/skybit/game/assets/LiberationSans-Bold.ttf"

INK = (6, 8, 14)
GOLD = (255, 206, 92)
CREAM = (246, 240, 230)
COOL = (150, 168, 196)
SLATE = (58, 62, 82)
SCRIM = (26, 22, 34)

DEATH_PHASE = 0.184
DEATH_X = int(DEATH_PHASE * W)   # 66 px, linear mapping
HORIZON_Y = 430

DEATH_PILLAR = 25
DAY_N = 1
TIME_ALIVE = 47

# Unreached events, x positions only. No names, no colours that identify them.
EVENT_XS = (60, 145, 155, 295)

_fonts: dict = {}


def font(size):
    if size not in _fonts:
        _fonts[size] = pygame.font.Font(FONT_PATH, size)
    return _fonts[size]


# ── text / chrome helpers (from render_flight_log_arc_count_r7.py) ───────────

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
    """Additive glow with the falloff baked into RGB.

    BLEND_ADD ignores the source alpha channel, so an alpha-ramped glow blits
    as a flat hard-edged disc. Premultiplying keeps the ramp.
    """
    size = radius * 2 + 2
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    c = radius + 1
    for r in range(radius, 0, -1):
        f = (1 - (r / radius) ** falloff) * (peak / 255.0)
        s_col = (int(color[0] * f), int(color[1] * f), int(color[2] * f), 255)
        pygame.draw.circle(s, s_col, (c, c), r)
    return s


def alpha_line(surf, rgba, p0, p1, width=1):
    """`surf` is an opaque Surface, so pygame.draw would ignore the alpha and
    stamp the colour at full strength. Route through a scratch layer."""
    lay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.line(lay, rgba, p0, p1, width)
    surf.blit(lay, (0, 0))


# ── the horizon, drawn at SS and downscaled once ─────────────────────────────

def draw_horizon(ss):
    """Everything that touches y=430 lives here, so the whole line goes
    through one supersample pass and one downscale. A 1px horizon composited
    natively would alias into a dotted seam the moment anything else lands
    near it."""
    k = SS
    y = HORIZON_Y * k

    # Flown burn — heat ramp. Dimmest at dawn, hottest at the terminus, so
    # the span reads as something still glowing rather than a bar that filled.
    for i in range(DEATH_X):
        t = i / max(1, DEATH_X - 1)
        a = int(76 + (255 - 76) * t)
        pygame.draw.line(ss, (*GOLD, a), (i * k, y), ((i + 1) * k, y), k)

    # Unlit remainder — flat 30 alpha out to x=200, guttering to nothing by
    # x=280. Never above 35, or the right of the screen becomes a loading bar.
    for i in range(DEATH_X, 280):
        if i <= 200:
            a = 30
        else:
            a = int(30 * (1.0 - (i - 200) / 80.0))
        if a <= 0:
            continue
        pygame.draw.line(ss, (*SLATE, a), (i * k, y), ((i + 1) * k, y), k)

    # Unreached events: 4px ticks hanging BELOW the dark horizon. Legible only
    # on close inspection — they are a hint that the day has structure, not a
    # legend of what that structure is.
    for ex in EVENT_XS:
        pygame.draw.line(ss, (*COOL, 40), (ex * k, (HORIZON_Y + 1) * k),
                         (ex * k, (HORIZON_Y + 5) * k), k)

    # Light column rising off the terminus — the only vertical in the frame.
    pygame.draw.line(ss, (*GOLD, 60), (DEATH_X * k, HORIZON_Y * k),
                     (DEATH_X * k, 385 * k), k)


# ── screen ───────────────────────────────────────────────────────────────────

def render_screen():
    surf = pygame.Surface((W, H))
    surf.fill(INK)

    ss = pygame.Surface((W * SS, H * SS), pygame.SRCALPHA)
    draw_horizon(ss)
    surf.blit(pygame.transform.smoothscale(ss, (W, H)), (0, 0))

    # Terminus glow, additive and native-res: three layers, hot core.
    for rad, col, peak in ((28, (255, 206, 92), 40),
                           (18, (255, 220, 120), 60),
                           (10, (255, 240, 160), 80)):
        g = soft_glow(rad, col, peak=peak, falloff=2.0)
        surf.blit(g, (DEATH_X - rad - 1, HORIZON_Y - rad - 1),
                  special_flags=pygame.BLEND_ADD)

    # ── banner: fully opaque dark neutral ──
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

    # ── headline, high in the empty ink ──
    pct = f"{DEATH_PHASE * 100:.0f}%"
    f_big, f_sml = font(21), font(11)
    w_pct = f_big.size(pct)[0]
    w_tail = f_sml.size("  OF THE DAY FLOWN")[0]
    r_pct = text(surf, pct, 21, center=(180, 104), color=GOLD, shadow=None)
    text(surf, "  OF THE DAY FLOWN", 11, midleft=(r_pct.right, 106), color=CREAM,
         shadow=None)
    alpha_line(surf, (255, 206, 92, 96), (r_pct.left, 120),
               (r_pct.right + w_tail, 120), 1)

    # ── death callout, floated just above the horizon, right of the glow ──
    f10, f8 = font(10), font(8)
    cw = max(f10.size("ENDED HERE")[0],
             f8.size(f"PILLAR {DEATH_PILLAR}  ·  0:{TIME_ALIVE:02d}")[0]) + 20
    cr = pygame.Rect(0, 0, cw, 34)
    cr.bottomleft = (DEATH_X + 20, 415)
    chip(surf, cr, radius=7, alpha=234, border_a=54)
    text(surf, "ENDED HERE", 10, midleft=(cr.x + 10, cr.y + 11), color=GOLD,
         shadow=None)
    text(surf, f"PILLAR {DEATH_PILLAR}  ·  0:{TIME_ALIVE:02d}", 8,
         midleft=(cr.x + 10, cr.y + 24), color=CREAM, shadow=None)

    # ── BACK pill ──
    pr = pygame.Rect(0, 0, 122, 36)
    pr.center = (W // 2, 597)
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

    return surf


OUT_SLUG = "cinema"
OUT_ROUND = "round_1"


def main():
    screen = render_screen()
    out = os.path.join(ROOT, "docs", "flight_log_arc_v2", OUT_SLUG, f"{OUT_ROUND}.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(screen, out)
    print(f"saved {out}  {pygame.image.load(out).get_size()}")


if __name__ == "__main__":
    main()
