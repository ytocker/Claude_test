"""Render: sectional_chart Flight Log — Round 5"""
import os
import sys
import math
import random

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame

pygame.display.init()
pygame.display.set_mode((1, 1))
pygame.font.init()

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(ROOT, "game", "assets", "LiberationSans-Bold.ttf")
OUT_DIR = os.path.join(ROOT, "docs", "flight_log_screen", "sectional_chart")
os.makedirs(OUT_DIR, exist_ok=True)

# ── Canvas ────────────────────────────────────────────────────────────────────
SW, SH = 360, 640
surf = pygame.Surface((SW, SH))

# ── Color palette ─────────────────────────────────────────────────────────────
CHART_PAPER      = (248, 244, 232)
TERRAIN_LOW      = (179, 201, 168)
TERRAIN_MID      = (196, 176, 128)
TERRAIN_HILL     = (176, 144, 80)
TERRAIN_MTN      = (156, 120, 72)
TERRAIN_PEAK     = (220, 200, 160)
WATER            = (154, 200, 208)
URBAN            = (240, 232, 144)
MAGENTA          = (212, 0, 128)
MAGENTA_DARK     = (160, 0, 96)
FAA_BLUE         = (0, 80, 160)
RESTRICTED_PURPLE= (140, 60, 160)
MOA_BLUE         = (60, 120, 200)
SIGMET_RED       = (180, 40, 20)
ICING_BLUE       = (80, 140, 200)
DEATH_RED        = (172, 40, 32)
GOLD             = (240, 192, 64)
ROUTE_UNFLOWN_DASH = (200, 80, 150)
CREASE           = (200, 196, 180)
DARK_TEXT        = (20, 20, 40)

# ── Fonts ─────────────────────────────────────────────────────────────────────
def font(size):
    try:
        return pygame.font.Font(FONT_PATH, size)
    except Exception:
        return pygame.font.SysFont("sans", size)

F7  = font(7)
F8  = font(8)
F9  = font(9)
F10 = font(10)
F11 = font(11)

# ── Geometry helpers ──────────────────────────────────────────────────────────
ROUTE_X   = 180
Y_START   = 588   # phase 0.0 — bottom of chart (day start)
Y_END     = 40    # phase 1.0 — top of chart (day end)

def phase_y(p):
    return int(588 - p * 548)

DEATH_PHASE = 0.184
death_y     = phase_y(DEATH_PHASE)   # ≈ 487

PHASE_BOUNDARIES = [
    (0.000, "DAY"),
    (0.231, "GOLDEN HOUR"),
    (0.363, "SUNSET"),
    (0.513, "DUSK"),
    (0.644, "NIGHT"),
    (0.794, "PREDAWN"),
    (0.906, "SUNRISE"),
]

EVENTS = [
    (0.15, "GEYSR"),
    (0.41, "CL-41"),
    (0.44, "STORM"),
    (0.85, "SNOW"),
]

# Waypoint short names for labels
WPT_NAMES = {
    "GOLDEN HOUR": "GOLHR",
    "SUNSET":      "SUNST",
    "DUSK":        "DUSKK",
    "NIGHT":       "NYTIM",
    "PREDAWN":     "PREDN",
    "SUNRISE":     "SUNRS",
}

# ── Terrain bands ─────────────────────────────────────────────────────────────
# Compute phase-y boundaries for each band
# Ordered top-to-bottom (high phase → low phase)
band_phases = [p for p, _ in PHASE_BOUNDARIES]  # 0.000…0.906
# Band tops (y) go from large (bottom) to small (top) as phase increases
# Band bottom = phase_y(band_phases[i]), top = phase_y(band_phases[i+1])
# But since phase_y decreases as phase increases, bottom > top in pixel terms.

BAND_DEFS = [
    # (phase_start, phase_end, base_color, name)
    (0.000, 0.231, TERRAIN_LOW,  "DAY"),
    (0.231, 0.363, TERRAIN_MID,  "GOLDEN HR"),
    (0.363, 0.513, TERRAIN_HILL, "SUNSET"),
    (0.513, 0.644, TERRAIN_MTN,  "DUSK"),
    (0.644, 0.794, TERRAIN_PEAK, "NIGHT"),
    (0.794, 0.906, TERRAIN_MTN,  "PREDAWN"),
    (0.906, 1.000, TERRAIN_MID,  "SUNRISE"),
]

rng = random.Random(42)

def darker(col, factor=0.75):
    return tuple(max(0, int(c * factor)) for c in col)

def blend(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def draw_terrain_bands():
    for (ps, pe, base_col, name) in BAND_DEFS:
        y_bot = phase_y(ps)   # larger y (closer to bottom of screen)
        y_top = phase_y(pe)   # smaller y (closer to top of screen)
        if y_top >= y_bot:
            continue
        band_h = y_bot - y_top

        # Base fill
        pygame.draw.rect(surf, base_col, (0, y_top, SW, band_h))

        # ── Contour lines (wavy polylines) ──────────────────────────────────
        contour_col = darker(base_col, 0.82) + (40,)   # RGBA
        n_contours = rng.randint(8, 12)
        for _ in range(n_contours):
            cy = rng.randint(y_top + 2, y_bot - 2)
            pts = []
            x = 0
            while x <= SW:
                wave = rng.randint(-4, 4)
                pts.append((x, cy + wave))
                x += rng.randint(20, 45)
            pts.append((SW, cy + rng.randint(-4, 4)))
            if len(pts) >= 2:
                cs = pygame.Surface((SW, SH), pygame.SRCALPHA)
                pygame.draw.lines(cs, darker(base_col, 0.78) + (38,), False, pts, 1)
                surf.blit(cs, (0, 0))

        # ── Water bodies ────────────────────────────────────────────────────
        n_water = rng.randint(2, 3)
        for _ in range(n_water):
            wx = rng.randint(10, SW - 60)
            wy = rng.randint(y_top + 4, y_bot - 10)
            ww = rng.randint(28, 60)
            wh = rng.randint(8, 18)
            wr = min(wh // 2, 5)
            pygame.draw.rect(surf, WATER, (wx, wy, ww, wh), border_radius=wr)

        # ── Urban blobs (lower half only) ───────────────────────────────────
        if ps < 0.6:
            n_urban = rng.randint(1, 2)
            for _ in range(n_urban):
                ux = rng.randint(30, SW - 60)
                uy = rng.randint(y_top + 4, y_bot - 10)
                # small jagged polygon
                pts = []
                sides = rng.randint(5, 8)
                r = rng.randint(8, 18)
                for s in range(sides):
                    ang = 2 * math.pi * s / sides
                    jitter = rng.uniform(0.7, 1.3)
                    pts.append((
                        int(ux + r * jitter * math.cos(ang)),
                        int(uy + r * jitter * 0.6 * math.sin(ang))
                    ))
                pygame.draw.polygon(surf, URBAN, pts)

        # ── Forest dots (green bands only) ──────────────────────────────────
        if base_col in (TERRAIN_LOW, TERRAIN_MID):
            n_clusters = rng.randint(3, 6)
            for _ in range(n_clusters):
                cx = rng.randint(8, SW - 8)
                cy = rng.randint(y_top + 4, y_bot - 4)
                n_dots = rng.randint(4, 9)
                dot_col = darker(base_col, 0.70)
                for _ in range(n_dots):
                    dx = cx + rng.randint(-12, 12)
                    dy = cy + rng.randint(-6, 6)
                    r  = rng.randint(2, 3)
                    pygame.draw.circle(surf, dot_col, (dx, dy), r)


# ── VOR compass rose ──────────────────────────────────────────────────────────
def draw_vor_rose(cx, cy, color=MAGENTA):
    pygame.draw.circle(surf, color, (cx, cy), 14, 1)
    for i in range(8):
        ang = math.radians(i * 45)
        tick_len = 8 if i % 2 == 0 else 5
        ix = cx + int(14 * math.sin(ang))
        iy = cy - int(14 * math.cos(ang))
        ox = cx + int((14 + tick_len) * math.sin(ang))
        oy = cy - int((14 + tick_len) * math.cos(ang))
        pygame.draw.line(surf, color, (ix, iy), (ox, oy), 1)


# ── Intersection triangle ─────────────────────────────────────────────────────
def draw_intersection(x, y, color=MAGENTA):
    h = 7
    pts = [(x, y - h), (x + h, y + h // 2), (x - h, y + h // 2)]
    pygame.draw.polygon(surf, color, pts, 1)


# ── Draw everything ───────────────────────────────────────────────────────────

# 1. Chart paper base
surf.fill(CHART_PAPER)

# 2. Terrain bands
draw_terrain_bands()

# 3. Unflown wash (y=40 to death_y)
wash_h = death_y - 40
if wash_h > 0:
    wash = pygame.Surface((SW, wash_h), pygame.SRCALPHA)
    wash.fill((230, 225, 210, 175))
    surf.blit(wash, (0, 40))

# 4. Phase boundary lines + VOR roses + waypoint labels
for (p, name) in PHASE_BOUNDARIES:
    if p == 0.0:
        continue
    py = phase_y(p)

    # Thin horizontal crease line
    pygame.draw.line(surf, CREASE, (0, py), (SW, py), 1)

    # VOR rose
    draw_vor_rose(ROUTE_X, py)

    # Intersection triangle to the LEFT of route (avoid VOR rose collision)
    tri_x = ROUTE_X - 22
    tri_pts = [(tri_x, py + 8), (tri_x - 10, py - 6), (tri_x + 10, py - 6)]
    pygame.draw.polygon(surf, CHART_PAPER, tri_pts)
    pygame.draw.polygon(surf, MAGENTA, tri_pts, 1)

    # Waypoint label to the right side
    label = WPT_NAMES.get(name, name[:5])
    txt = F8.render(label, True, DARK_TEXT)
    surf.blit(txt, (198, py - txt.get_height() // 2))

# 5. Event markers
for (ep, ename) in EVENTS:
    ey = phase_y(ep)

    if ename == "GEYSR":
        # Restricted Area (R) — dashed purple circle
        ra_surf = pygame.Surface((SW, SH), pygame.SRCALPHA)
        r = 18
        # Draw 8 arc segments, skip every other → dashed effect
        for seg in range(8):
            if seg % 2 == 0:
                start_ang = math.radians(seg * 45)
                end_ang   = math.radians((seg + 1) * 45)
                pts = []
                for a in range(int(math.degrees(start_ang)), int(math.degrees(end_ang)) + 1, 3):
                    pts.append((
                        ROUTE_X + int(r * math.cos(math.radians(a))),
                        ey      + int(r * math.sin(math.radians(a)))
                    ))
                if len(pts) >= 2:
                    pygame.draw.lines(ra_surf, RESTRICTED_PURPLE + (220,), False, pts, 1)
        surf.blit(ra_surf, (0, 0))
        txt = F7.render("R-015", True, RESTRICTED_PURPLE)
        surf.blit(txt, (ROUTE_X + 22, ey - 8))

    elif ename == "CL-41":
        # MOA polygon (hexagon) — staggered LEFT to avoid STORM collision
        sym_cx = 150  # LEFT of route
        r = 20
        sides = 6
        poly_pts = []
        for s in range(sides):
            ang = math.radians(s * 60 - 90)
            poly_pts.append((
                sym_cx + int(r * math.cos(ang)),
                ey     + int(r * math.sin(ang))
            ))
        # Fill with alpha
        moa_surf = pygame.Surface((SW, SH), pygame.SRCALPHA)
        pygame.draw.polygon(moa_surf, MOA_BLUE + (40,), poly_pts)
        surf.blit(moa_surf, (0, 0))
        pygame.draw.polygon(surf, MOA_BLUE, poly_pts, 1)
        txt = F7.render("MOA", True, MOA_BLUE)
        surf.blit(txt, (116, ey - 6))

    elif ename == "STORM":
        # Convective SIGMET — 8-sided polygon — staggered LEFT
        sym_cx = 150  # LEFT of route
        r = 24
        sides = 8
        poly_pts = []
        jitter_rs = [24, 20, 26, 18, 24, 22, 28, 20]
        for s in range(sides):
            ang = math.radians(s * 45 - 90)
            jr = jitter_rs[s]
            poly_pts.append((
                sym_cx + int(jr * math.cos(ang)),
                ey     + int(jr * math.sin(ang))
            ))
        sig_surf = pygame.Surface((SW, SH), pygame.SRCALPHA)
        pygame.draw.polygon(sig_surf, SIGMET_RED + (35,), poly_pts)
        surf.blit(sig_surf, (0, 0))
        pygame.draw.polygon(surf, SIGMET_RED, poly_pts, 1)
        txt = F7.render("SIG", True, SIGMET_RED)
        surf.blit(txt, (116, ey - 6))

    elif ename == "SNOW":
        # Icing area — dashed rectangle + asterisk
        rx, ry, rw, rh = ROUTE_X - 20, ey - 10, 40, 20
        # Dashed rectangle: draw four sides with dashes
        def dash_line(x1, y1, x2, y2, col, dash=5, gap=4):
            total = math.hypot(x2 - x1, y2 - y1)
            dx = (x2 - x1) / total if total else 0
            dy = (y2 - y1) / total if total else 0
            pos = 0
            drawing = True
            while pos < total:
                seg = dash if drawing else gap
                end = min(pos + seg, total)
                if drawing:
                    pygame.draw.line(surf, col,
                        (int(x1 + dx * pos), int(y1 + dy * pos)),
                        (int(x1 + dx * end), int(y1 + dy * end)), 1)
                pos = end
                drawing = not drawing
        dash_line(rx, ry, rx + rw, ry, ICING_BLUE)
        dash_line(rx + rw, ry, rx + rw, ry + rh, ICING_BLUE)
        dash_line(rx + rw, ry + rh, rx, ry + rh, ICING_BLUE)
        dash_line(rx, ry + rh, rx, ry, ICING_BLUE)
        # Asterisk (6 lines at 60° spacing)
        ar = 4
        for i in range(6):
            ang = math.radians(i * 30)
            pygame.draw.line(surf, ICING_BLUE,
                (ROUTE_X, ey),
                (ROUTE_X + int(ar * math.cos(ang)), ey + int(ar * math.sin(ang))), 1)
        txt = F7.render("ICG", True, ICING_BLUE)
        surf.blit(txt, (ROUTE_X + 24, ey - 6))

# 6. Route lines
# Flown portion: solid magenta, (180,588) → (180,death_y)
pygame.draw.line(surf, MAGENTA, (ROUTE_X, Y_START), (ROUTE_X, death_y), 3)

# Unflown portion: dashed lighter magenta, (180,death_y) → (180,40)
y = death_y
while y > Y_END:
    y_seg_end = max(y - 6, Y_END)
    pygame.draw.line(surf, ROUTE_UNFLOWN_DASH, (ROUTE_X, y), (ROUTE_X, y_seg_end), 2)
    y -= 12

# 7. Death marker at (180, death_y)
# Hard red cap line across full canvas width
pygame.draw.line(surf, DEATH_RED, (0, death_y), (360, death_y), 2)
# Red X — enlarged arms (20px)
pygame.draw.line(surf, DEATH_RED, (ROUTE_X - 10, death_y - 10), (ROUTE_X + 10, death_y + 10), 3)
pygame.draw.line(surf, DEATH_RED, (ROUTE_X + 10, death_y - 10), (ROUTE_X - 10, death_y + 10), 3)
# Circle around X — enlarged radius 18
pygame.draw.circle(surf, DEATH_RED, (ROUTE_X, death_y), 18, 2)

# Annotation pill to the right — expanded 90×18px at font size 9
pill_x, pill_y, pill_w, pill_h = 196, death_y - 16, 90, 18
pygame.draw.rect(surf, DEATH_RED, (pill_x, pill_y, pill_w, pill_h), border_radius=4)
pill_txt = F9.render("TERRAIN CONTACT", True, (255, 255, 255))
surf.blit(pill_txt, (pill_x + (pill_w - pill_txt.get_width()) // 2,
                     pill_y + (pill_h - pill_txt.get_height()) // 2))

# "LAST FIX  0:47" below pill (moved down to avoid overlap)
fix_txt = F8.render("LAST FIX  0:47", True, DARK_TEXT)
surf.blit(fix_txt, (196, death_y + 6))

# 8. Chart fold creases (alpha)
crease_surf = pygame.Surface((SW, SH), pygame.SRCALPHA)
pygame.draw.line(crease_surf, (180, 175, 160, 60), (0, 210), (360, 200), 1)
pygame.draw.line(crease_surf, (180, 175, 160, 60), (0, 420), (360, 415), 1)
surf.blit(crease_surf, (0, 0))

# 9. Header (y=0→40)
header_col = (230, 220, 200)
pygame.draw.rect(surf, header_col, (0, 0, SW, 40))
# Title
title_txt = F9.render("VFR SECTIONAL CHART", True, DARK_TEXT)
surf.blit(title_txt, (8, 8))
# Scale
scale_txt = F8.render("1:500,000", True, DARK_TEXT)
surf.blit(scale_txt, (SW - 8 - scale_txt.get_width(), 8))
# Scale bar
pygame.draw.line(surf, DARK_TEXT, (8, 32), (90, 32), 2)
pygame.draw.line(surf, DARK_TEXT, (8, 28), (8, 36), 1)
pygame.draw.line(surf, DARK_TEXT, (90, 28), (90, 36), 1)
nm0 = F7.render("0 NM", True, DARK_TEXT)
nm50 = F7.render("50 NM", True, DARK_TEXT)
surf.blit(nm0, (8, 33))
surf.blit(nm50, (90 - nm50.get_width(), 33))

# 10. Footer (y=602→640)
footer_col = (230, 220, 200)
pygame.draw.rect(surf, footer_col, (0, 602, SW, 38))
# Stat strip — centered
info = F10.render("PILLAR 25  •  DAY 1  •  0:47  •  18% FLOWN", True, DARK_TEXT)
surf.blit(info, ((SW - info.get_width()) // 2, 607))
# BACK button — filled FAA-style, bottom-left
MUTED_MAGENTA = (168, 0, 128)
btn_rect = pygame.Rect(10, 614, 110, 20)
pygame.draw.rect(surf, MUTED_MAGENTA, btn_rect, border_radius=4)
back_txt = F11.render("◄ BACK", True, (250, 250, 250))
surf.blit(back_txt, (10 + (110 - back_txt.get_width()) // 2,
                     614 + (20 - back_txt.get_height()) // 2))

# ── Save ──────────────────────────────────────────────────────────────────────
out = os.path.join(OUT_DIR, "round_2.png")
pygame.image.save(surf, out)
print(f"saved {out}")
