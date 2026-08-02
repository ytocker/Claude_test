#!/usr/bin/env python3
"""
lantern_reach  ·  flight-log arc concept  ·  round 2

Philosophy: the entire arc exists as a cold engraved groove.
The parrot (the lantern) illuminated only what it reached — light falloff
does the flown/unflown split.  Hidden events are visible as dark engravings
but receive no light: you see shapes, not identities.

Round 2 changes vs round 1:
  - R 175 → 168 (prevents right terminus clipping)
  - Veil alpha 90 → 40 (stars / mountains breathe)
  - Flown arc: INK 7px keyline + gold 5px stroke
  - Header: FLIGHT LOG 16px y=28, subtitle 11px y=50 (includes 18.4%),
    1px GOLD rule at y=66, 66px band; "18.4% OF THE DAY FLOWN" strip removed
  - LIGHT SOURCE chip removed
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

from game.draw import lerp_color

# ── constants ────────────────────────────────────────────────────────────────
W, H = 360, 640
CX, CY, R = 180, 430, 168          # Fix 1: R was 175
EASE_P = 0.652

ROOT = "/home/user/skybit"
FONT_PATH = "/home/user/skybit/game/assets/LiberationSans-Bold.ttf"

INK   = (6,   8,  14)
GOLD  = (255, 206, 92)
CREAM = (246, 240, 230)
COOL  = (150, 168, 196)
SLATE = (58,  62,  82)

GROOVE_DARK  = (28, 34,  52)   # main groove fill
GROOVE_SHAD  = (10, 12,  20)   # shadow edge (outer)
GROOVE_HI    = (70, 80, 110)   # highlight edge (inner)

DEATH_PHASE  = 0.184
DAY_N        = 1
DEATH_PILLAR = 25
TIME_ALIVE   = 47

_fonts: dict = {}


def font(size):
    if size not in _fonts:
        _fonts[size] = pygame.font.Font(FONT_PATH, size)
    return _fonts[size]


# ── arc geometry ─────────────────────────────────────────────────────────────

def ease(p):
    return max(0.0, min(1.0, p)) ** EASE_P


def arc_angle(p):
    return math.pi * (1.0 - ease(p))


def arc_pos(p, radius=R):
    a = arc_angle(p)
    return (CX + radius * math.cos(a), CY - radius * math.sin(a))


def radial_unit(p):
    a = arc_angle(p)
    return (math.cos(a), -math.sin(a))


def arc_tangent_deg(p):
    e = 1e-4
    x0, y0 = arc_pos(max(0.0, p - e))
    x1, y1 = arc_pos(min(1.0, p + e))
    return math.degrees(math.atan2(-(y1 - y0), (x1 - x0)))


# ── glow helpers ──────────────────────────────────────────────────────────────

def soft_glow(radius, color, peak=110, falloff=2.0):
    """Additive glow surface — premultiplied so BLEND_ADD ramps correctly."""
    size = radius * 2 + 2
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    c = radius + 1
    for r in range(radius, 0, -1):
        f = (1 - (r / radius) ** falloff) * (peak / 255.0)
        s_col = (int(color[0] * f), int(color[1] * f), int(color[2] * f), 255)
        pygame.draw.circle(s, s_col, (c, c), r)
    return s


def blit_glow(surf, cx, cy, radius, color, peak=110, falloff=2.0):
    g = soft_glow(radius, color, peak=peak, falloff=falloff)
    surf.blit(g, (int(cx) - radius - 1, int(cy) - radius - 1),
              special_flags=pygame.BLEND_ADD)


# ── keyline helper ────────────────────────────────────────────────────────────

def add_ink(src, color=(6, 8, 14, 240), pad=2):
    mask = pygame.mask.from_surface(src, threshold=12)
    sil  = mask.to_surface(setcolor=color, unsetcolor=(0, 0, 0, 0))
    out  = pygame.Surface(
        (src.get_width() + pad * 2, src.get_height() + pad * 2), pygame.SRCALPHA)
    for dx in range(-pad, pad + 1):
        for dy in range(-pad, pad + 1):
            if dx or dy:
                out.blit(sil, (pad + dx, pad + dy))
    out.blit(src, (pad, pad))
    return out


# ── text helper ───────────────────────────────────────────────────────────────

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


def alpha_line(surf, rgba, p0, p1, width=1):
    lay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.line(lay, rgba, p0, p1, width)
    surf.blit(lay, (0, 0))


# ── Skybit background ─────────────────────────────────────────────────────────

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


# ── groove segment helper ─────────────────────────────────────────────────────

def draw_groove_arc(surf, p0, p1, steps=200, extra_r=0):
    """Draw a three-layer engraved groove between two phases.
    extra_r widens the groove on both sides for the geyser span.
    """
    for i in range(steps):
        pa = p0 + (p1 - p0) * i       / steps
        pb = p0 + (p1 - p0) * (i + 1) / steps
        # Shadow outer
        xa0, ya0 = arc_pos(pa, R + 1 + extra_r)
        xa1, ya1 = arc_pos(pb, R + 1 + extra_r)
        pygame.draw.line(surf, GROOVE_SHAD,
                         (int(xa0), int(ya0)), (int(xa1), int(ya1)), 2)
        # Main groove
        xb0, yb0 = arc_pos(pa, R + extra_r)
        xb1, yb1 = arc_pos(pb, R + extra_r)
        pygame.draw.line(surf, GROOVE_DARK,
                         (int(xb0), int(yb0)), (int(xb1), int(yb1)), 2)
        if extra_r:
            xc0, yc0 = arc_pos(pa, R - extra_r)
            xc1, yc1 = arc_pos(pb, R - extra_r)
            pygame.draw.line(surf, GROOVE_DARK,
                             (int(xc0), int(yc0)), (int(xc1), int(yc1)), 2)
        # Highlight inner
        xd0, yd0 = arc_pos(pa, R - 1 - extra_r)
        xd1, yd1 = arc_pos(pb, R - 1 - extra_r)
        pygame.draw.line(surf, GROOVE_HI,
                         (int(xd0), int(yd0)), (int(xd1), int(yd1)), 1)


def draw_notch(surf, p, radius=R, size=3):
    """Small engraved notch at a given phase and radius."""
    x, y = arc_pos(p, radius)
    ux, uy = radial_unit(p)
    ix, iy = int(x), int(y)
    # Shadow on outer side
    pygame.draw.circle(surf, GROOVE_SHAD, (int(x + ux), int(y + uy)), size)
    # Main dark mark
    pygame.draw.circle(surf, GROOVE_DARK, (ix, iy), size)
    # Highlight on inner side
    pygame.draw.circle(surf, GROOVE_HI, (int(x - ux), int(y - uy)), size - 1)


# ── death point coordinates ───────────────────────────────────────────────────
DEATH_X, DEATH_Y = arc_pos(DEATH_PHASE)   # recomputed from R=168


# ── main render ───────────────────────────────────────────────────────────────

def render():
    # 1. Background
    surf = build_skybit_bg(W, H)

    # Fix 3: Veil alpha reduced from 90 → 40 so stars and mountains breathe
    veil = pygame.Surface((W, H), pygame.SRCALPHA)
    veil.fill((6, 8, 20, 40))
    surf.blit(veil, (0, 0))

    # 2. Engrave the full arc groove (0→1), all phases
    draw_groove_arc(surf, 0.0, 1.0, steps=200)

    # 3. Engrave event depressions
    # GEYSER span: wider groove
    draw_groove_arc(surf, 0.167, 0.373, steps=100, extra_r=2)
    # Fix 1: notch radii recomputed for R=168
    # CLOWN notch: inward 6px → R-6 = 162
    draw_notch(surf, 0.403, radius=162, size=3)
    # RAIN notch: outward 6px → R+6 = 174
    draw_notch(surf, 0.430, radius=174, size=3)
    # SNOWSTORM notch at R=168 (was 175)
    draw_notch(surf, 0.820, radius=168, size=3)

    # 4. Light surface — warm radial falloff from death point (BLEND_ADD)
    light_surf = pygame.Surface((W, H), pygame.SRCALPHA)
    for r in range(68, 0, -4):
        a = int(180 * (1 - r / 68))
        lay = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(lay, (255, 206, 92, a), (r, r), r)
        light_surf.blit(lay, (int(DEATH_X) - r, int(DEATH_Y) - r))
    # Additional secondary warm pools along the flown arc
    for off_p in (0.0, 0.06, 0.12):
        px, py = arc_pos(DEATH_PHASE - off_p)
        for r in range(32, 0, -4):
            a = int(80 * (1 - r / 32))
            lay2 = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(lay2, (255, 190, 70, a), (r, r), r)
            light_surf.blit(lay2, (int(px) - r, int(py) - r))
    surf.blit(light_surf, (0, 0), special_flags=pygame.BLEND_ADD)

    # 5. Fix 4: Flown arc — 7px INK keyline + 5px gold stroke (was 5px/3px)
    #    Gold steps (200,160,60) at p=0 → (255,206,92) at p=DEATH_PHASE
    steps = 80
    for i in range(steps):
        pa = DEATH_PHASE * i       / steps
        pb = DEATH_PHASE * (i + 1) / steps
        t  = i / steps
        col = (int(200 + 55 * t), int(160 + 46 * t), int(60 + 32 * t))
        x0, y0 = arc_pos(pa)
        x1, y1 = arc_pos(pb)
        pygame.draw.line(surf, INK, (int(x0), int(y0)), (int(x1), int(y1)), 7)
        pygame.draw.line(surf, col, (int(x0), int(y0)), (int(x1), int(y1)), 5)

    # 6. DAY COMPLETE marker — ring position auto-follows R=168 via arc_pos(1.0)
    dc_x, dc_y = int(arc_pos(1.0)[0]), int(arc_pos(1.0)[1])
    pygame.draw.circle(surf, INK, (dc_x, dc_y), 13)
    pygame.draw.circle(surf, (115, 104, 46), (dc_x, dc_y), 11)
    pygame.draw.circle(surf, INK, (dc_x, dc_y), 7)
    pygame.draw.circle(surf, (115, 104, 46), (dc_x, dc_y), 5)
    # 2px INK keyline ring
    pygame.draw.circle(surf, INK, (dc_x, dc_y), 13, 2)

    # 7. Death point / light source — the macaw position
    dx, dy = int(DEATH_X), int(DEATH_Y)
    # Warm glow bloom
    blit_glow(surf, dx, dy, 26, (255, 230, 160), peak=90, falloff=1.8)
    blit_glow(surf, dx, dy, 14, (255, 220, 140), peak=140, falloff=2.0)
    # Bright point — 4px GOLD circle with 2px INK keyline
    pygame.draw.circle(surf, INK,  (dx, dy), 6)
    pygame.draw.circle(surf, GOLD, (dx, dy), 4)

    # 8. Fix 2: LIGHT SOURCE chip removed entirely.

    # 9. Fix 5: Normalized chrome header ──────────────────────────────────────
    # 66px header band (was 72px)
    SCRIM = (18, 14, 26)
    pygame.draw.rect(surf, SCRIM, (0, 0, W, 66))
    fade = pygame.Surface((W, 10), pygame.SRCALPHA)
    for i in range(10):
        fade.fill((*SCRIM, int(230 * (1 - i / 10) ** 1.4)), pygame.Rect(0, i, W, 1))
    surf.blit(fade, (0, 66))
    # 1px GOLD rule at y=66 (was y=72)
    alpha_line(surf, (*GOLD, 140), (0, 66), (W - 1, 66), 1)

    # "FLIGHT LOG" 16px GOLD centered at y=28 (was 22px)
    text(surf, "FLIGHT LOG", 16, center=(W // 2, 28), color=GOLD,
         track=4, shadow=None)

    # Subtitle 11px CREAM at y=50 — includes 18.4% (removes separate strip below)
    subtitle = (
        f"DAY {DAY_N}"
        f"  ·  PILLAR {DEATH_PILLAR}"
        f"  ·  0:{TIME_ALIVE:02d}"
        f"  ·  {DEATH_PHASE * 100:.1f}%"
    )
    text(surf, subtitle, 11, center=(W // 2, 50), color=CREAM, shadow=None)

    # Fix 5: "18.4% OF THE DAY FLOWN" strip removed — info lives in the header now.

    # BACK button — gold gradient pill 80×28 centred at (180, 610)
    pr = pygame.Rect(0, 0, 80, 28)
    pr.center = (W // 2, 610)
    # Shadow under button
    sh = pygame.Surface((pr.w + 8, pr.h + 8), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, 90), sh.get_rect(), border_radius=16)
    surf.blit(sh, (pr.x - 4, pr.y - 2))
    # Fill
    back_fill = pygame.Surface(pr.size, pygame.SRCALPHA)
    back_fill.fill((60, 46, 24, 255))
    pygame.draw.rect(back_fill, (60, 46, 24, 255), back_fill.get_rect(),
                     border_radius=14)
    # Clip to rounded rect via mask
    mask_s = pygame.Surface(pr.size, pygame.SRCALPHA)
    pygame.draw.rect(mask_s, (255, 255, 255, 255), mask_s.get_rect(), border_radius=14)
    back_fill.blit(mask_s, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(back_fill, pr.topleft)
    # GOLD border
    pygame.draw.rect(surf, GOLD, pr, width=2, border_radius=14)
    text(surf, "BACK", 12, center=(pr.centerx, pr.centery),
         color=GOLD, shadow=None, track=2)

    return surf


def main():
    surf = render()
    out = os.path.join(ROOT, "docs", "flight_log_arc", "lantern_reach", "round_2.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(surf, out)
    loaded = pygame.image.load(out)
    print(f"saved {out}  {loaded.get_size()}")


if __name__ == "__main__":
    main()
