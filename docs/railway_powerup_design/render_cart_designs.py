"""Five mine-cart designs for the RAILS UP! power-up.

Mechanic: cart wheels grip the rail, Pip rides inside, the cart auto-
scrolls fast forward through the rail segment (~5 pillars). Each render
shows the cart on the centre rail with Pip's head and shoulders above
the rim — same staged scene as 04_western_trestle_real.png so the
designs can be compared apples-to-apples.

Run:  python docs/railway_powerup_design/render_cart_designs.py
"""
from __future__ import annotations

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H, GROUND_Y, PIPE_W, BIRD_R  # noqa: E402
from game import biome, parrot  # noqa: E402
from game.draw import (  # noqa: E402
    get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground,
)
from game.entities import Pipe  # noqa: E402

SCALE = 4
W2, H2 = W * SCALE, H * SCALE

PIPE_LAYOUT = (
    ( 50, 285, 170),
    (170, 235, 170),
    (290, 300, 170),
)

CLOUD_LAYOUT = (
    (20, 90, 0.9, 0), (180, 140, 1.1, 2),
    (60, 220, 0.8, 3), (230, 60, 0.7, 1),
    (320, 180, 0.9, 4),
)

# Cart geometry (game-px; multiply by SCALE for target-px).
WHEEL_R    = 5 * SCALE     # wheel radius, target-px (20)
WHEEL_DX   = 15 * SCALE    # half wheel-base
CART_W     = 42 * SCALE    # cart body width
CART_H     = 18 * SCALE    # cart body height
PIP_LIFT   = 30 * SCALE    # how far above the rail Pip's sprite-centre sits

WHITE = (255, 255, 255)


# ──────────────────────────────────────────────────────────────────────────────
# Shared base scene + rail (duplicated from render_western_real.py — kept
# explicit so this file is self-contained and easy to iterate)
# ──────────────────────────────────────────────────────────────────────────────

def build_base_native(pipes, palette, bucket):
    surf = pygame.Surface((W, H))
    sky = get_sky_surface_biome(W, H, GROUND_Y, palette, bucket)
    surf.blit(sky, (0, 0))
    for bx, by, sc, var in CLOUD_LAYOUT:
        draw_cloud(surf, bx, by, sc, variant=var)
    draw_mountains(surf, 0.0, GROUND_Y, W,
                   palette['mtn_far'], palette['mtn_near'])
    draw_ground(surf, GROUND_Y, W, H, 0.0,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    for p in pipes:
        p.draw(surf, palette)
    return surf


def _line(surf, pts, color, thickness, *, dy=0):
    pygame.draw.lines(surf, color, False,
                      [(x, y + dy) for x, y in pts], thickness)


def _ties(surf, pts, *, spacing, length, thickness, edge, body, hi):
    segs, total = [], 0.0
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        d = math.hypot(x1 - x0, y1 - y0)
        segs.append((d, (x0, y0), (x1, y1)))
        total += d
    n = max(1, int(total / spacing))
    half = length / 2
    for k in range(n + 1):
        target = (k / n) * total
        acc = 0.0
        for d, p0, p1 in segs:
            if acc + d >= target:
                f = (target - acc) / max(1.0, d)
                cx = int(p0[0] + (p1[0] - p0[0]) * f)
                cy = int(p0[1] + (p1[1] - p0[1]) * f)
                dx = p1[0] - p0[0]
                dy = p1[1] - p0[1]
                seg_len = max(1.0, math.hypot(dx, dy))
                nx = -dy / seg_len
                ny = dx / seg_len
                a = (int(cx + nx * half), int(cy + ny * half))
                b = (int(cx - nx * half), int(cy - ny * half))
                pygame.draw.line(surf, edge, a, b, thickness + 2)
                pygame.draw.line(surf, body, a, b, thickness)
                h0 = (int(cx + nx * half * 0.55),
                      int(cy + ny * half * 0.55))
                h1 = (int(cx - nx * half * 0.55),
                      int(cy - ny * half * 0.55))
                pygame.draw.line(surf, hi, h0, h1, max(1, thickness - 2))
                break
            acc += d


def paint_rail_hires(surf, pipes):
    pts = []
    for p in sorted(pipes, key=lambda p: p.x):
        rail_y = int((p.gap_y + p.gap_h / 2) * SCALE)
        pts.append((int(p.x * SCALE), rail_y))
        pts.append((int((p.x + PIPE_W) * SCALE), rail_y))

    pine_dk  = ( 70,  45,  25)
    pine     = (135,  90,  50)
    pine_hi  = (180, 130,  75)
    iron_dk  = ( 50,  45,  45)
    iron     = (110, 100,  95)
    iron_hi  = (190, 180, 175)

    _ties(surf, pts, spacing=8 * SCALE, length=14 * SCALE,
          thickness=4 * SCALE, edge=pine_dk, body=pine, hi=pine_hi)
    for dy in (+3 * SCALE, -3 * SCALE):
        _line(surf, pts, iron_dk, 3 * SCALE, dy=dy)
    for dy in (+3 * SCALE, -3 * SCALE):
        _line(surf, pts, iron, 2 * SCALE, dy=dy)
    for dy in (+2 * SCALE, -4 * SCALE):
        _line(surf, pts, iron_hi, 1 * SCALE, dy=dy)


def blit_hires_bird(surf, cx, cy):
    frame = parrot._build_frame_scaled(0, SCALE)
    outlined = parrot._add_outline_scaled(frame, SCALE)
    rect = outlined.get_rect(center=(cx, cy))
    surf.blit(outlined, rect.topleft)


def paint_label_hires(surf, pipes):
    base_col = (220, 150, 80)
    text = "RAILS UP!"
    size = 24 * SCALE
    label_x = int(((pipes[0].x + PIPE_W + pipes[1].x) / 2) * SCALE)
    label_y = int((pipes[1].gap_y - pipes[1].gap_h / 2 - 18) * SCALE)
    font = pygame.font.SysFont("Arial", size, bold=True)
    base = font.render(text, True, base_col)
    bw, bh = base.get_size()
    light = tuple(int(base_col[i] + (255 - base_col[i]) * 0.45) for i in range(3))
    grad = pygame.Surface((bw, bh), pygame.SRCALPHA)
    for y in range(bh):
        t = y / max(1, bh - 1)
        c = tuple(int(light[i] + (base_col[i] - light[i]) * t) for i in range(3))
        pygame.draw.line(grad, c, (0, y), (bw, y))
    body = base.copy()
    body.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    dark = tuple(max(0, c // 4) for c in base_col)
    outline = font.render(text, True, dark)
    off = max(2, SCALE)
    for ox, oy in ((-off, 0), (off, 0), (0, -off), (0, off),
                   (-off + 1, -off + 1), (-off + 1, off - 1),
                   (off - 1, -off + 1), (off - 1, off - 1)):
        surf.blit(outline, (label_x - bw // 2 + ox, label_y - bh // 2 + oy))
    surf.blit(body, (label_x - bw // 2, label_y - bh // 2))


# ──────────────────────────────────────────────────────────────────────────────
# Shared cart-drawing helpers
# ──────────────────────────────────────────────────────────────────────────────

def draw_spoked_wheel(surf, cx, cy, r, *, tire, hub, spoke,
                      spoke_count=8, rim_thickness=None):
    """Solid tire ring + hub disc + N spokes radiating outward."""
    if rim_thickness is None:
        rim_thickness = max(2, r // 4)
    pygame.draw.circle(surf, tire, (cx, cy), r)
    pygame.draw.circle(surf, hub, (cx, cy), r - rim_thickness)
    for i in range(spoke_count):
        ang = (i / spoke_count) * math.tau
        ex = cx + int(math.cos(ang) * (r - rim_thickness // 2))
        ey = cy + int(math.sin(ang) * (r - rim_thickness // 2))
        pygame.draw.line(surf, spoke, (cx, cy), (ex, ey), max(2, r // 6))
    # Centre cap
    pygame.draw.circle(surf, spoke, (cx, cy), max(2, r // 4))


def draw_motion_streaks(surf, cx, cy, length, *, color, count=5):
    """Horizontal speed lines trailing behind the cart (drawn to the left)."""
    layer = pygame.Surface((W2, H2), pygame.SRCALPHA)
    for i in range(count):
        y = cy - length // 3 + i * (length // (count * 2)) - length // 8
        x_start = cx - length + (i % 2) * (length // 5)
        x_end = cx - length // 4
        a = 60 + (i * 25) % 100
        thickness = max(2, SCALE - i // 3)
        pygame.draw.line(layer, (*color, a),
                         (x_start, y), (x_end, y), thickness)
    surf.blit(layer, (0, 0))


# ──────────────────────────────────────────────────────────────────────────────
# Cart variant 1 — MINE CART CLASSIC (Donkey Kong style)
# ──────────────────────────────────────────────────────────────────────────────

def paint_mine_cart(surf, cx, rail_y, *, layer):
    """Trapezoidal iron bucket with rivets + 2 large 8-spoke wheels."""
    iron_dk = ( 40,  30,  28)
    iron    = ( 95,  75,  65)
    iron_hi = (175, 155, 140)
    rivet   = (210, 190, 170)
    rust    = (140,  60,  20)

    if layer == "wheels":
        for dx in (-WHEEL_DX, +WHEEL_DX):
            draw_spoked_wheel(surf, cx + dx, rail_y - WHEEL_R, WHEEL_R,
                              tire=iron_dk, hub=iron, spoke=iron_hi,
                              spoke_count=8)
        return

    # Body: trapezoidal bucket (wider at top).
    top_w = CART_W
    bot_w = int(CART_W * 0.78)
    body_top = rail_y - 2 * WHEEL_R - CART_H
    body_bot = rail_y - 2 * WHEEL_R

    pts_outer = [
        (cx - top_w // 2,     body_top),
        (cx + top_w // 2,     body_top),
        (cx + bot_w // 2,     body_bot),
        (cx - bot_w // 2,     body_bot),
    ]
    pygame.draw.polygon(surf, iron_dk, pts_outer)
    inset = 3 * SCALE
    pts_inner = [
        (cx - top_w // 2 + inset, body_top + inset),
        (cx + top_w // 2 - inset, body_top + inset),
        (cx + bot_w // 2 - inset, body_bot - inset),
        (cx - bot_w // 2 + inset, body_bot - inset),
    ]
    pygame.draw.polygon(surf, iron, pts_inner)
    # Top rim — bright iron stripe.
    pygame.draw.rect(surf, iron_hi,
                     pygame.Rect(cx - top_w // 2, body_top,
                                 top_w, 2 * SCALE))
    pygame.draw.rect(surf, iron_dk,
                     pygame.Rect(cx - top_w // 2, body_top - SCALE,
                                 top_w, SCALE))
    # Rivets — four corners + two middle, square instead of round.
    rsize = 2 * SCALE
    for rx, ry in (
        (cx - top_w // 2 + 4 * SCALE, body_top + 4 * SCALE),
        (cx + top_w // 2 - 4 * SCALE - rsize, body_top + 4 * SCALE),
        (cx - top_w // 2 + 4 * SCALE, body_bot - 4 * SCALE - rsize),
        (cx + top_w // 2 - 4 * SCALE - rsize, body_bot - 4 * SCALE - rsize),
    ):
        pygame.draw.rect(surf, rivet, pygame.Rect(rx, ry, rsize, rsize))
    # Subtle rust streak hint at bottom.
    pygame.draw.line(surf, rust,
                     (cx - bot_w // 2 + 6 * SCALE, body_bot - 2),
                     (cx + bot_w // 2 - 6 * SCALE, body_bot - 2),
                     max(1, SCALE // 2))


# ──────────────────────────────────────────────────────────────────────────────
# Cart variant 2 — WOODEN WAGON (pine planks + iron bands)
# ──────────────────────────────────────────────────────────────────────────────

def paint_wagon(surf, cx, rail_y, *, layer):
    """Rectangular wooden cart with vertical pine planks + iron hoops."""
    pine_dk = ( 70,  45,  25)
    pine    = (135,  90,  50)
    pine_hi = (180, 130,  75)
    iron_dk = ( 40,  35,  30)
    iron    = (110, 100,  95)
    iron_hi = (180, 170, 160)

    if layer == "wheels":
        for dx in (-WHEEL_DX, +WHEEL_DX):
            # Wooden wheel with iron tire.
            cy = rail_y - WHEEL_R
            pygame.draw.circle(surf, iron_dk, (cx + dx, cy), WHEEL_R)
            pygame.draw.circle(surf, iron, (cx + dx, cy), WHEEL_R - SCALE)
            pygame.draw.circle(surf, pine_dk, (cx + dx, cy), WHEEL_R - 2 * SCALE)
            pygame.draw.circle(surf, pine, (cx + dx, cy),
                               WHEEL_R - 2 * SCALE - SCALE // 2)
            # Spokes — 6 wooden bars
            for i in range(6):
                ang = (i / 6) * math.tau
                ex = cx + dx + int(math.cos(ang) * (WHEEL_R - 2 * SCALE))
                ey = cy + int(math.sin(ang) * (WHEEL_R - 2 * SCALE))
                pygame.draw.line(surf, pine_dk, (cx + dx, cy),
                                 (ex, ey), max(2, SCALE - 1))
            pygame.draw.circle(surf, iron_dk, (cx + dx, cy), SCALE)
        return

    body_top = rail_y - 2 * WHEEL_R - CART_H
    body_bot = rail_y - 2 * WHEEL_R
    body_w = CART_W

    # Outline / shadow
    pygame.draw.rect(surf, pine_dk,
                     pygame.Rect(cx - body_w // 2 - SCALE,
                                 body_top - SCALE,
                                 body_w + 2 * SCALE,
                                 CART_H + 2 * SCALE))
    # Plank body
    pygame.draw.rect(surf, pine,
                     pygame.Rect(cx - body_w // 2, body_top, body_w, CART_H))
    # Plank seams — vertical lines every 6 game-px.
    plank_w = 6 * SCALE
    n = body_w // plank_w
    for i in range(1, n):
        px = cx - body_w // 2 + i * plank_w
        pygame.draw.line(surf, pine_dk,
                         (px, body_top + SCALE),
                         (px, body_bot - SCALE), max(1, SCALE // 2))
        pygame.draw.line(surf, pine_hi,
                         (px + max(1, SCALE // 2), body_top + SCALE),
                         (px + max(1, SCALE // 2), body_bot - SCALE), 1)
    # Iron hoops — two horizontal bands.
    hoop_h = 3 * SCALE
    for band_y in (body_top + 2 * SCALE,
                   body_bot - 2 * SCALE - hoop_h):
        pygame.draw.rect(surf, iron_dk,
                         pygame.Rect(cx - body_w // 2 - SCALE, band_y,
                                     body_w + 2 * SCALE, hoop_h))
        pygame.draw.rect(surf, iron,
                         pygame.Rect(cx - body_w // 2 - SCALE, band_y + SCALE,
                                     body_w + 2 * SCALE, hoop_h - 2 * SCALE))
        pygame.draw.line(surf, iron_hi,
                         (cx - body_w // 2 - SCALE, band_y + SCALE),
                         (cx + body_w // 2 + SCALE, band_y + SCALE), 1)


# ──────────────────────────────────────────────────────────────────────────────
# Cart variant 3 — COAL HOPPER (inverted trapezoid + 4 wheels)
# ──────────────────────────────────────────────────────────────────────────────

def paint_hopper(surf, cx, rail_y, *, layer):
    """Wide hopper with sloped sides + 4 small wheels in 2 pairs."""
    iron_dk = ( 30,  28,  35)
    iron    = ( 75,  72,  85)
    iron_hi = (165, 160, 175)
    rivet   = (210, 200, 215)

    small_r = int(WHEEL_R * 0.7)
    if layer == "wheels":
        for dx in (-WHEEL_DX - 4 * SCALE, -WHEEL_DX + 4 * SCALE,
                   +WHEEL_DX - 4 * SCALE, +WHEEL_DX + 4 * SCALE):
            draw_spoked_wheel(surf, cx + dx, rail_y - small_r, small_r,
                              tire=iron_dk, hub=iron, spoke=iron_hi,
                              spoke_count=6,
                              rim_thickness=max(2, small_r // 4))
        return

    top_w = CART_W + 6 * SCALE
    bot_w = int(CART_W * 0.55)
    body_top = rail_y - 2 * small_r - CART_H - 2 * SCALE
    body_bot = rail_y - 2 * small_r

    pts_outer = [
        (cx - top_w // 2, body_top),
        (cx + top_w // 2, body_top),
        (cx + bot_w // 2, body_bot),
        (cx - bot_w // 2, body_bot),
    ]
    pygame.draw.polygon(surf, iron_dk, pts_outer)
    inset = 3 * SCALE
    pts_inner = [
        (cx - top_w // 2 + inset, body_top + inset),
        (cx + top_w // 2 - inset, body_top + inset),
        (cx + bot_w // 2 - inset, body_bot - inset),
        (cx - bot_w // 2 + inset, body_bot - inset),
    ]
    pygame.draw.polygon(surf, iron, pts_inner)
    # Top rim — bold iron stripe.
    pygame.draw.rect(surf, iron_hi,
                     pygame.Rect(cx - top_w // 2, body_top,
                                 top_w, 2 * SCALE))
    # Rivets along the top rim — five evenly-spaced squares.
    rsize = 2 * SCALE
    for k in range(5):
        rx = cx - top_w // 2 + 4 * SCALE + k * ((top_w - 8 * SCALE) // 4)
        pygame.draw.rect(surf, rivet,
                         pygame.Rect(rx, body_top + 4 * SCALE, rsize, rsize))


# ──────────────────────────────────────────────────────────────────────────────
# Cart variant 4 — SPEEDSTER (sleek racing cart + motion streaks)
# ──────────────────────────────────────────────────────────────────────────────

def paint_speedster(surf, cx, rail_y, *, layer):
    """Aerodynamic teardrop cart with racing stripe + speed lines."""
    red_dk  = (110,  20,  20)
    red     = (200,  45,  45)
    red_hi  = (255, 110,  90)
    cream   = (250, 240, 215)
    chrome  = (180, 175, 170)
    chrome_dk = ( 50,  48,  48)

    small_r = int(WHEEL_R * 0.85)
    if layer == "wheels":
        # Motion streaks BEHIND the cart first (left side).
        draw_motion_streaks(surf, cx - CART_W // 2, rail_y - WHEEL_R,
                            length=18 * SCALE, color=cream, count=6)
        for dx in (-WHEEL_DX, +WHEEL_DX):
            # Chrome wheel with red brake disc.
            cy = rail_y - small_r
            pygame.draw.circle(surf, chrome_dk, (cx + dx, cy), small_r)
            pygame.draw.circle(surf, chrome, (cx + dx, cy), small_r - SCALE)
            pygame.draw.circle(surf, red_dk, (cx + dx, cy), small_r - 2 * SCALE)
            pygame.draw.circle(surf, red, (cx + dx, cy),
                               small_r - 2 * SCALE - SCALE // 2)
            pygame.draw.circle(surf, chrome, (cx + dx, cy), SCALE)
        return

    # Teardrop body: a wide ellipse, full cart height so Pip sits in it
    # (not perched above it).
    body_w = CART_W + 6 * SCALE
    body_h = CART_H
    body_top = rail_y - 2 * small_r - body_h
    rect = pygame.Rect(cx - body_w // 2, body_top, body_w, body_h)
    pygame.draw.ellipse(surf, red_dk, rect.inflate(2 * SCALE, 2 * SCALE))
    pygame.draw.ellipse(surf, red, rect)
    # Cream racing stripe — horizontal band along the body's midline.
    stripe = pygame.Rect(rect.left + 2 * SCALE,
                         body_top + body_h // 2 - SCALE,
                         rect.width - 4 * SCALE, 2 * SCALE)
    pygame.draw.rect(surf, cream, stripe)
    # Bright highlight along the body top — sells the polished finish.
    hi = pygame.Rect(rect.left + 4 * SCALE, body_top + 2 * SCALE,
                     rect.width - 8 * SCALE, max(1, SCALE))
    pygame.draw.rect(surf, red_hi, hi)
    # Number "1" decal on the side.
    try:
        f = pygame.font.SysFont("Arial", 8 * SCALE, bold=True)
        txt = f.render("1", True, cream)
        surf.blit(txt, (cx + 8 * SCALE,
                        body_top + body_h // 2 - txt.get_height() // 2))
    except Exception:
        pass


# ──────────────────────────────────────────────────────────────────────────────
# Cart variant 5 — TROPICAL POD (pineapple shell + leafy crown)
# ──────────────────────────────────────────────────────────────────────────────

def paint_tropical(surf, cx, rail_y, *, layer):
    """Half-pineapple shell with diamond-crosshatched skin + green leaves."""
    skin_dk = (155, 100,  20)
    skin    = (230, 175,  55)
    skin_hi = (255, 220, 110)
    leaf_dk = ( 25,  90,  35)
    leaf    = ( 80, 170,  60)
    leaf_hi = (170, 230, 120)
    wood_dk = ( 70,  45,  25)
    wood    = (140, 100,  55)

    small_r = int(WHEEL_R * 0.9)
    body_w = CART_W + 2 * SCALE
    body_h = int(CART_H * 1.05)
    body_top = rail_y - 2 * small_r - body_h
    body_bot = rail_y - 2 * small_r

    if layer == "wheels":
        # Wheels.
        for dx in (-WHEEL_DX, +WHEEL_DX):
            cy = rail_y - small_r
            pygame.draw.circle(surf, wood_dk, (cx + dx, cy), small_r)
            pygame.draw.circle(surf, wood, (cx + dx, cy), small_r - SCALE)
            for i in range(8):
                ang = (i / 8) * math.tau
                ex = cx + dx + int(math.cos(ang) * (small_r - SCALE))
                ey = cy + int(math.sin(ang) * (small_r - SCALE))
                pygame.draw.line(surf, wood_dk, (cx + dx, cy),
                                 (ex, ey), max(2, SCALE - 1))
            pygame.draw.circle(surf, wood_dk, (cx + dx, cy), SCALE)
        # Leaves — drawn BEFORE Pip so they sit behind his head, not over it.
        leaves_cy = body_top + SCALE
        for dx_l, h_l, tilt_l in (
            (-14 * SCALE, 10 * SCALE, -38),
            (-10 * SCALE,  8 * SCALE, -22),
            ( 10 * SCALE,  8 * SCALE,  22),
            ( 14 * SCALE, 10 * SCALE,  38),
        ):
            leaf_surf = pygame.Surface((8 * SCALE, h_l), pygame.SRCALPHA)
            pygame.draw.polygon(leaf_surf, leaf_dk,
                                [(4 * SCALE, 0), (8 * SCALE, h_l),
                                 (0, h_l)])
            pygame.draw.polygon(leaf_surf, leaf,
                                [(4 * SCALE, SCALE),
                                 (8 * SCALE - SCALE, h_l - SCALE),
                                 (SCALE, h_l - SCALE)])
            pygame.draw.line(leaf_surf, leaf_hi,
                             (4 * SCALE, SCALE),
                             (4 * SCALE, h_l - 2 * SCALE), 1)
            rotated = pygame.transform.rotozoom(leaf_surf, tilt_l, 1.0)
            rr = rotated.get_rect(midbottom=(cx + dx_l, leaves_cy))
            surf.blit(rotated, rr.topleft)
        return
    rect = pygame.Rect(cx - body_w // 2, body_top, body_w, body_h)
    # Outline + body.
    pygame.draw.ellipse(surf, skin_dk, rect.inflate(2 * SCALE, 2 * SCALE))
    pygame.draw.ellipse(surf, skin, rect)
    # Highlight crescent on the upper-left of the shell.
    hi_rect = pygame.Rect(rect.left + 4 * SCALE, body_top + 2 * SCALE,
                          rect.width - 8 * SCALE, body_h // 2)
    pygame.draw.ellipse(surf, skin_hi, hi_rect)
    pygame.draw.ellipse(surf, skin, hi_rect.inflate(0, -body_h // 4))
    # Crosshatched diamond pattern — pineapple skin scales.
    diag = pygame.Surface(rect.size, pygame.SRCALPHA)
    for offset in range(-body_w, body_w * 2, 4 * SCALE):
        pygame.draw.line(diag, (*skin_dk, 140),
                         (offset, 0), (offset + body_h, body_h), 1)
        pygame.draw.line(diag, (*skin_dk, 140),
                         (offset + body_h, 0), (offset, body_h), 1)
    # Mask to the ellipse so the hatching only shows on the shell.
    mask = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.ellipse(mask, (255, 255, 255, 255), mask.get_rect())
    diag.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(diag, rect.topleft)


# ──────────────────────────────────────────────────────────────────────────────
# Driver
# ──────────────────────────────────────────────────────────────────────────────

def render_variant(out_path, paint_cart, *, biome_phase=0.78):
    palette = biome.palette_for_phase(biome_phase)
    bucket = biome.phase_bucket(biome_phase)
    pipes = [Pipe(x, gy, gh) for (x, gy, gh) in PIPE_LAYOUT]
    for p in pipes:
        p.rail_active = True

    base = build_base_native(pipes, palette, bucket)
    big = pygame.transform.smoothscale(base, (W2, H2))
    paint_rail_hires(big, pipes)

    mid = pipes[1]
    cx = int((mid.x + PIPE_W / 2) * SCALE)
    rail_y_hi = int((mid.gap_y + mid.gap_h / 2) * SCALE)

    paint_cart(big, cx, rail_y_hi, layer="wheels")
    # Pip rides inside, lifted to sit on top of the cart wheels.
    bird_y_hi = rail_y_hi - PIP_LIFT - 2 * SCALE
    blit_hires_bird(big, cx, bird_y_hi)
    paint_cart(big, cx, rail_y_hi, layer="body")

    paint_label_hires(big, pipes)
    pygame.image.save(big, out_path)


def main():
    variants = [
        ("cart_01_mine.png",     paint_mine_cart),
        ("cart_02_wagon.png",    paint_wagon),
        ("cart_03_hopper.png",   paint_hopper),
        ("cart_04_speedster.png", paint_speedster),
        ("cart_05_tropical.png", paint_tropical),
    ]
    for name, paint in variants:
        out = os.path.join(HERE, name)
        render_variant(out, paint)
        print(f"  wrote {name}")
    print(f"\n5 cart designs saved to {HERE}")


if __name__ == "__main__":
    main()
