#!/usr/bin/env python3
"""
weathered_dial  ·  flight-log arc concept  ·  round 2

Philosophy: the day is a calibrated instrument bezel.
  Flown zone   = finished brass (machined, graduated)
  Past death   = unfinished gunmetal
  Hidden events = empty jewel sockets (count visible, identity absent)
  Death        = steel needle from centre, frozen inside the NEWBIE red sector

Round 2 changes:
  Fix 1: GEYSER jewel moved to p=0.167 (inside flown brass zone)
  Fix 2: GENIE socket removed (3 hidden sockets remain: CLOWN, RAIN, SNOWSTORM)
  Fix 3: Sockets normalized: CLOWN R=164, RAIN R=172, SNOWSTORM R=168
          All sockets: 7px dark well, 2px (96,102,120) rim, 2px INK keyline
  Fix 4: Brass palette pulled toward GOLD hue
  Fix 5: NEWBIE red band truncated at DEATH_PHASE (0.184), not 0.20
  Fix 6: Removed bare "DAY" label; removed P.25 from callout chip;
          header updated to spec (y=28/50/66, 18.4% in subhead)
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

# ── constants ────────────────────────────────────────────────────────────────

ROOT      = "/home/user/skybit"
FONT_PATH = "/home/user/skybit/game/assets/LiberationSans-Bold.ttf"
_fonts: dict = {}

W, H = 360, 640

INK   = (6,   8,  14)
GOLD  = (255, 206, 92)
CREAM = (246, 240, 230)
COOL  = (150, 168, 196)
SLATE = (58,  62,  82)

# Fix 4: brass palette pulled toward GOLD hue
BRASS_FILL    = (140, 106, 44)    # darker, more GOLD-family amber (was 168,132,72)
BRASS_SPEC_HI = (210, 175, 98)    # (was 232,196,128)
BRASS_SPEC_LO = (120, 88,  32)    # (was 150,116,64)
BRASS_TICK    = (80,  60,  24)    # darker amber (was 74,54,30)
GUNMETAL      = (62,  66,  80)    # unchanged — warm-to-cool contrast is the point
CAUTION_RED   = (158, 52,  46)
STEEL         = (178, 186, 200)
RED_TIP       = (214, 64,  54)

# Arc geometry
CX, CY   = 180, 430
R        = 168
EASE_P   = 0.652

DEATH_PHASE  = 0.184
DEATH_PILLAR = 25
DAY_N        = 1
TIME_ALIVE   = 47

# Fix 1: GEYSER moved to p=0.167 (inside flown brass zone, before death at 0.184)
GEYSER_PHASE  = 0.167  # was 0.27
CLOWN_PHASE   = 0.403
RAIN_PHASE    = 0.430
# Fix 2: GENIE_PHASE removed entirely
SNOW_PHASE    = 0.820


# ── fonts ────────────────────────────────────────────────────────────────────

def font(size):
    if size not in _fonts:
        _fonts[size] = pygame.font.Font(FONT_PATH, size)
    return _fonts[size]


# ── arc maths ────────────────────────────────────────────────────────────────

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


# ── background ───────────────────────────────────────────────────────────────

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


# ── helpers ──────────────────────────────────────────────────────────────────

def lerp(a, b, t):
    return a + (b - a) * t


def lerp_color(a, b, t):
    t = max(0.0, min(1.0, t))
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def alpha_line(surf, rgba, p0, p1, width=1):
    lay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.line(lay, rgba, p0, p1, width)
    surf.blit(lay, (0, 0))


def draw_text(surf, s, size, center=None, midleft=None, color=CREAM):
    f = font(size)
    img = f.render(s, True, color)
    rect = img.get_rect()
    if center:
        rect.center = center
    elif midleft:
        rect.midleft = midleft
    surf.blit(img, rect)


# ── annular sector helpers ───────────────────────────────────────────────────

def annular_pts(r_in, r_out, deg_start, deg_end, cx=CX, cy=CY, step=1):
    """Return (inner_pts, outer_pts) lists walking from deg_start to deg_end."""
    inner, outer = [], []
    a = deg_start
    while (a >= deg_end if deg_start > deg_end else a <= deg_end):
        rad = math.radians(a)
        inner.append((cx + r_in  * math.cos(rad), cy - r_in  * math.sin(rad)))
        outer.append((cx + r_out * math.cos(rad), cy - r_out * math.sin(rad)))
        if deg_start > deg_end:
            a -= step
        else:
            a += step
        if abs(a - deg_end) < step * 0.5:
            break
    rad = math.radians(deg_end)
    inner.append((cx + r_in  * math.cos(rad), cy - r_in  * math.sin(rad)))
    outer.append((cx + r_out * math.cos(rad), cy - r_out * math.sin(rad)))
    return inner, outer


def draw_annular_sector(surf, r_in, r_out, deg_start, deg_end, color, cx=CX, cy=CY):
    """Fill annular sector by drawing concentric arc slices as quads."""
    inner, outer = annular_pts(r_in, r_out, deg_start, deg_end, cx, cy, step=1)
    # Build a polygon: inner forward + outer reversed
    poly = inner + list(reversed(outer))
    if len(poly) >= 3:
        pygame.draw.polygon(surf, color, [(int(x), int(y)) for x, y in poly])


def draw_annular_arc(surf, radius, deg_start, deg_end, color, width=2, cx=CX, cy=CY, step=2):
    pts = []
    a = deg_start
    direction = -1 if deg_start > deg_end else 1
    while True:
        rad = math.radians(a)
        pts.append((int(cx + radius * math.cos(rad)), int(cy - radius * math.sin(rad))))
        if direction == -1 and a <= deg_end:
            break
        if direction == 1  and a >= deg_end:
            break
        a += direction * step
    if len(pts) >= 2:
        pygame.draw.lines(surf, color, False, pts, width)


# ── bezel: flown zone (180° → 120.3°) ───────────────────────────────────────
#
# angle convention: standard math angle in degrees, y-up
# 180° = left  = p=0 (START)
# 120.3° ≈ death angle
# 0°  = right = p=1 (END)

DEATH_ANGLE_DEG  = math.degrees(arc_angle(DEATH_PHASE))   # ≈ 120.3
# Fix 5: NEWBIE band ends at DEATH_PHASE (0.184), not 0.20
NEWBIE_END_DEG   = math.degrees(arc_angle(DEATH_PHASE))   # was arc_angle(0.20)
START_DEG        = 180.0
END_DEG          = 0.0

CLOWN_DEG   = math.degrees(arc_angle(CLOWN_PHASE))         # ≈ 80.5
RAIN_DEG    = math.degrees(arc_angle(RAIN_PHASE))          # ≈ 76.2
# Fix 2: GENIE_DEG removed
SNOW_DEG    = math.degrees(arc_angle(SNOW_PHASE))          # ≈ 21.8
GEYSER_DEG  = math.degrees(arc_angle(GEYSER_PHASE))        # now ≈ 123.5° (inside flown zone)


def draw_bezel_flown(surf):
    """Brass annular sector from 180° down to death angle (120.3°)."""
    d_start = START_DEG
    d_end   = DEATH_ANGLE_DEG
    # Fill
    draw_annular_sector(surf, 162, 174, d_start, d_end, BRASS_FILL)
    # Specular sweep: 3px arc at R=171
    lay = pygame.Surface((W, H), pygame.SRCALPHA)
    n_steps = int(d_start - d_end) + 1
    for i in range(n_steps):
        t   = i / max(1, n_steps - 1)
        deg = d_start - t * (d_start - d_end)
        col = lerp_color(BRASS_SPEC_HI, BRASS_SPEC_LO, t)
        rad = math.radians(deg)
        x   = int(CX + 171 * math.cos(rad))
        y   = int(CY - 171 * math.sin(rad))
        pygame.draw.circle(lay, (*col, 200), (x, y), 2)
    surf.blit(lay, (0, 0))
    # Graduation ticks every 3°
    deg = d_start
    while deg >= d_end:
        rad  = math.radians(deg)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        every_15 = abs(deg % 15) < 0.5
        r0 = 163
        r1 = 167 if every_15 else 169
        w  = 4 if every_15 else 2
        x0 = int(CX + r0 * cos_a)
        y0 = int(CY - r0 * sin_a)
        x1 = int(CX + r1 * cos_a)
        y1 = int(CY - r1 * sin_a)
        pygame.draw.line(surf, BRASS_TICK, (x0, y0), (x1, y1), w)
        deg -= 3.0


def draw_bezel_unflown(surf):
    """Gunmetal annular sector from death angle (120.3°) to 0°."""
    d_start = DEATH_ANGLE_DEG
    d_end   = END_DEG
    draw_annular_sector(surf, 162, 174, d_start, d_end, GUNMETAL)
    # Inner keyline at R=163
    lay = pygame.Surface((W, H), pygame.SRCALPHA)
    draw_annular_arc(lay, 163, d_start, d_end, (*INK, 200), width=2, step=1)
    surf.blit(lay, (0, 0))


def draw_newbie_band(surf):
    """Red caution band between R=155 and R=160 from 180° to death angle.
    Fix 5: stops at DEATH_PHASE (0.184), not 0.20.
    """
    d_start = START_DEG
    d_end   = NEWBIE_END_DEG
    draw_annular_sector(surf, 155, 160, d_start, d_end, CAUTION_RED)
    lay = pygame.Surface((W, H), pygame.SRCALPHA)
    draw_annular_arc(lay, 155, d_start, d_end, (*INK, 200), width=2, step=1)
    draw_annular_arc(lay, 160, d_start, d_end, (*INK, 200), width=2, step=1)
    surf.blit(lay, (0, 0))


# ── jewel sockets ────────────────────────────────────────────────────────────

def draw_jewel(surf, x, y, filled=True, fill_color=None):
    """Draw a jewel or empty socket.

    Empty socket (Fix 3): 7px dark well, 2px (96,102,120) rim, 2px INK keyline.
    """
    ix, iy = int(x), int(y)
    if filled and fill_color:
        pygame.draw.circle(surf, fill_color, (ix, iy), 7)
        pygame.draw.circle(surf, (30, 24, 14), (ix, iy), 7, 2)
        # Specular pip
        px = ix + int(-7 * 0.35)
        py = iy + int(-7 * 0.35)
        pygame.draw.circle(surf, (255, 255, 255), (px, py), 2)
    else:
        # Fix 3: 7px dark well, 2px (96,102,120) rim, 2px INK keyline
        pygame.draw.circle(surf, (28, 32, 42), (ix, iy), 7)       # dark well
        pygame.draw.circle(surf, (96, 102, 120), (ix, iy), 7, 2)  # rim
        pygame.draw.circle(surf, INK, (ix, iy), 9, 2)             # INK keyline (outer)


def draw_geyser_jewel(surf):
    """Fix 1: GEYSER at p=0.167, computed with arc_pos at R=168 (default)."""
    gx, gy = arc_pos(GEYSER_PHASE)   # arc_pos uses R=168 by default
    draw_jewel(surf, gx, gy, filled=True, fill_color=(146, 232, 255))


def draw_empty_sockets(surf):
    """Fix 2: Only CLOWN, RAIN, SNOWSTORM — GENIE removed.
    Fix 3: CLOWN R=164, RAIN R=172, SNOWSTORM R=168.
    """
    # CLOWN: inner track R=164
    cx_c, cy_c = (CX + 164 * math.cos(math.radians(CLOWN_DEG)),
                  CY - 164 * math.sin(math.radians(CLOWN_DEG)))
    draw_jewel(surf, cx_c, cy_c, filled=False)

    # RAIN: outer track R=172 (within R=162–174 range, safe)
    cx_r, cy_r = (CX + 172 * math.cos(math.radians(RAIN_DEG)),
                  CY - 172 * math.sin(math.radians(RAIN_DEG)))
    draw_jewel(surf, cx_r, cy_r, filled=False)

    # SNOWSTORM: center R=168
    cx_s, cy_s = (CX + 168 * math.cos(math.radians(SNOW_DEG)),
                  CY - 168 * math.sin(math.radians(SNOW_DEG)))
    draw_jewel(surf, cx_s, cy_s, filled=False)


# ── death needle ─────────────────────────────────────────────────────────────

def draw_death_needle(surf):
    angle_rad = math.radians(DEATH_ANGLE_DEG)
    cos_a, sin_a = math.cos(angle_rad), -math.sin(angle_rad)   # screen y-down

    tip_x = CX + 160 * math.cos(angle_rad)
    tip_y = CY - 160 * math.sin(angle_rad)

    # Perpendicular direction
    perp_x = -math.sin(angle_rad)   # rotated 90°
    perp_y = -math.cos(angle_rad)

    # Hub is at (CX, CY), wide end 4px, tip 2px
    hw = 2.0   # half-width at hub
    tw = 1.0   # half-width at tip

    corners = [
        (CX + perp_x * hw, CY + perp_y * hw),
        (tip_x + perp_x * tw, tip_y + perp_y * tw),
        (tip_x - perp_x * tw, tip_y - perp_y * tw),
        (CX - perp_x * hw, CY - perp_y * hw),
    ]
    corners_i = [(int(x), int(y)) for x, y in corners]

    # Draw with INK outline first (2px wider)
    out_corners = [
        (CX + perp_x * (hw + 1), CY + perp_y * (hw + 1)),
        (tip_x + perp_x * (tw + 1), tip_y + perp_y * (tw + 1)),
        (tip_x - perp_x * (tw + 1), tip_y - perp_y * (tw + 1)),
        (CX - perp_x * (hw + 1), CY - perp_y * (hw + 1)),
    ]
    pygame.draw.polygon(surf, INK, [(int(x), int(y)) for x, y in out_corners])
    pygame.draw.polygon(surf, STEEL, corners_i)

    # Red tip: last 10px
    red_base_x = CX + (160 - 10) * math.cos(angle_rad)
    red_base_y = CY - (160 - 10) * math.sin(angle_rad)
    red_corners = [
        (red_base_x + perp_x * tw, red_base_y + perp_y * tw),
        (tip_x      + perp_x * tw, tip_y      + perp_y * tw),
        (tip_x      - perp_x * tw, tip_y      - perp_y * tw),
        (red_base_x - perp_x * tw, red_base_y - perp_y * tw),
    ]
    pygame.draw.polygon(surf, RED_TIP, [(int(x), int(y)) for x, y in red_corners])

    # Hub disc
    pygame.draw.circle(surf, INK,   (CX, CY), 9)
    pygame.draw.circle(surf, STEEL, (CX, CY), 7)


# ── DAY COMPLETE index ────────────────────────────────────────────────────────

def draw_day_complete(surf):
    """Gold index bar at p=1 (angle=0°). Fix 6: bare 'DAY' label removed."""
    y_dc = CY

    # Gold bar with INK outline
    pygame.draw.line(surf, INK,  (int(CX + 158), y_dc), (int(CX + 178), y_dc), 5)
    pygame.draw.line(surf, GOLD, (int(CX + 160), y_dc), (int(CX + 176), y_dc), 3)
    # Fix 6: 'DAY' text label removed — DAY COMPLETE is communicated by the gold bar


# ── chrome / UI ───────────────────────────────────────────────────────────────

def draw_chrome(surf):
    # Header band
    header = pygame.Surface((W, 66), pygame.SRCALPHA)
    header.fill((14, 10, 24, 230))
    surf.blit(header, (0, 0))

    # Fix 6: 1px GOLD rule at y=66
    alpha_line(surf, (*GOLD, 255), (0, 66), (W - 1, 66), 1)

    # Fix 6: "FLIGHT LOG" 16px GOLD at y=28
    draw_text(surf, "FLIGHT LOG", 16, center=(W // 2, 28), color=GOLD)

    # Fix 6: subhead includes 18.4% — "DAY 1  ·  PILLAR 25  ·  0:47  ·  18.4%" at y=50
    subhead = f"DAY {DAY_N}  ·  PILLAR {DEATH_PILLAR}  ·  0:{TIME_ALIVE:02d}  ·  18.4%"
    draw_text(surf, subhead, 11, center=(W // 2, 50), color=CREAM)

    # Death callout chip — Fix 6: P.25 removed from chip text
    chip_text = "ENDED · 18.4%"
    chip_w = font(9).size(chip_text)[0] + 20
    chip_h = 22
    chip_x = 96
    chip_y = 205

    chip_surf = pygame.Surface((chip_w, chip_h), pygame.SRCALPHA)
    pygame.draw.rect(chip_surf, (18, 15, 24, 220), chip_surf.get_rect(), border_radius=5)
    pygame.draw.rect(chip_surf, (*GOLD, 255),      chip_surf.get_rect(), width=2, border_radius=5)
    surf.blit(chip_surf, (chip_x, chip_y))
    draw_text(surf, chip_text, 9, center=(chip_x + chip_w // 2, chip_y + chip_h // 2),
              color=CREAM)

    # Leader line from chip to death needle position
    death_x_px, death_y_px = arc_pos(DEATH_PHASE)
    alpha_line(surf, (*GOLD, 90),
               (chip_x + chip_w // 2, chip_y + chip_h),
               (int(death_x_px), int(death_y_px) - 12), 1)

    # BACK button
    pr = pygame.Rect(0, 0, 80, 28)
    pr.center = (W // 2, 610)
    btn = pygame.Surface((pr.w, pr.h), pygame.SRCALPHA)
    pygame.draw.rect(btn, (30, 20, 10, 255), btn.get_rect(), border_radius=14)
    pygame.draw.rect(btn, (*GOLD, 255),      btn.get_rect(), width=2, border_radius=14)
    surf.blit(btn, pr.topleft)
    draw_text(surf, "BACK", 11, center=pr.center, color=GOLD)


# ── main render ───────────────────────────────────────────────────────────────

def render():
    surf = build_skybit_bg(W, H)

    # Draw order: bezel sectors, NEWBIE band, jewels, needle, chrome

    # 1. NEWBIE caution band (inside bezel, R=155–160), now truncated at DEATH_PHASE
    draw_newbie_band(surf)

    # 2. Bezel flown zone (brass, R=162–174, 180°→120.3°)
    draw_bezel_flown(surf)

    # 3. Bezel unflown zone (gunmetal, R=162–174, 120.3°→0°)
    draw_bezel_unflown(surf)

    # 4. GEYSER jewel (filled, now in flown brass zone at p=0.167)
    draw_geyser_jewel(surf)

    # 5. Empty jewel sockets (CLOWN, RAIN, SNOWSTORM — 3 sockets only)
    draw_empty_sockets(surf)

    # 6. Death needle
    draw_death_needle(surf)

    # 7. DAY COMPLETE index bar
    draw_day_complete(surf)

    # 8. Chrome / UI
    draw_chrome(surf)

    return surf


def main():
    surf = render()
    out_path = os.path.join(ROOT, "docs", "flight_log_arc", "weathered_dial", "round_2.png")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    pygame.image.save(surf, out_path)
    loaded = pygame.image.load(out_path)
    print(f"saved {out_path}  {loaded.get_size()}")
    assert loaded.get_size() == (360, 640), f"Wrong size: {loaded.get_size()}"


if __name__ == "__main__":
    main()
