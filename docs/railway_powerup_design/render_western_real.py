"""Render Western Trestle on a real game frame, at 4× resolution (1440×2560).

The trick to getting genuine resolution out of a 360×640 game (vs. a
nearest-neighbour blowup): render every "hero" element directly at the
target resolution and only smoothscale the atmospheric backdrop.

Pipeline:
  1. Compose sky + clouds + mountains + ground + sandstone pillars at
     native 360×640 using the real `game.draw` + `game.entities.Pipe`
     functions.
  2. Smoothscale that base 4× → 1440×2560. The result is a soft
     atmospheric backdrop; pillar silhouettes stay visually crisp
     because they're vector-style polygons that anti-alias cleanly.
  3. Build Pip at scale=4 using `parrot._build_frame_scaled` +
     `_add_outline_scaled` — the same supersample path the in-game
     GROW power-up uses to keep big-Pip sharp. Blit at the high-res
     bird centre.
  4. Paint the Western Trestle rail (ties, iron, spikes, dust) with
     thicknesses and coordinates scaled by 4 so every line is one
     full target-pixel thick.
  5. Build a "RAILS UP!" label at 4× font size, replicating the
     FloatText `style="powerup"` recipe (gradient fill + dark outline
     + 8 sparkles).

Run:  python docs/railway_powerup_design/render_western_real.py
"""
from __future__ import annotations

import math
import os
import random
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
W2, H2 = W * SCALE, H * SCALE  # 1440 × 2560

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


# ──────────────────────────────────────────────────────────────────────────────
# Base scene at native, then smoothscale up
# ──────────────────────────────────────────────────────────────────────────────

def build_base_native(pipes, palette, bucket) -> pygame.Surface:
    """Sky + clouds + mountains + ground + pillars — no rail, no bird."""
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


# ──────────────────────────────────────────────────────────────────────────────
# Hi-res Pip — bypasses the cached native-size frames
# ──────────────────────────────────────────────────────────────────────────────

def blit_hires_bird(surf, bird_cx_hi, bird_cy_hi):
    """Build Pip at SCALE× using parrot's existing supersample API.

    `_build_frame_scaled(angle, s)` is the same code path the GROW
    sprite uses (with s=_GROW_SS), so it's a supported way to get a
    high-resolution Pip without smoothscale-up blur.
    """
    frame = parrot._build_frame_scaled(0, SCALE)         # wing at rest
    outlined = parrot._add_outline_scaled(frame, SCALE)
    rect = outlined.get_rect(center=(bird_cx_hi, bird_cy_hi))
    surf.blit(outlined, rect.topleft)


# ──────────────────────────────────────────────────────────────────────────────
# Western Trestle rail — drawn at SCALE so every line is full target pixels
# ──────────────────────────────────────────────────────────────────────────────

def paint_rail_hires(surf, pipes):
    """Wooden ties + iron rails + spikes + rust + dust, all at SCALE×."""
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

    # Ties — every 8 game-px = 32 target-px. Thickness 4 game-px = 16 target-px.
    _ties(surf, pts, spacing=8 * SCALE, length=14 * SCALE,
          thickness=4 * SCALE, edge=pine_dk, body=pine, hi=pine_hi)

    # Twin iron rails — 6 game-px gauge means dy = ±3 game-px = ±12 target-px.
    for dy in (+3 * SCALE, -3 * SCALE):
        _line(surf, pts, iron_dk, 3 * SCALE, dy=dy)
    for dy in (+3 * SCALE, -3 * SCALE):
        _line(surf, pts, iron, 2 * SCALE, dy=dy)
    for dy in (+2 * SCALE, -4 * SCALE):
        _line(surf, pts, iron_hi, 1 * SCALE, dy=dy)

    # Dust trail behind Pip's feet — on the centre pipe's rail.
    mid = sorted(pipes, key=lambda p: p.x)[1]
    feet_x = int((mid.x + PIPE_W / 2) * SCALE)
    feet_y = int((mid.gap_y + mid.gap_h / 2) * SCALE)
    dust = pygame.Surface((W2, H2), pygame.SRCALPHA)
    rng = random.Random(7)
    for _ in range(10):
        dx = feet_x + rng.randint(-22, -2) * SCALE
        dy = feet_y + rng.randint(-3, 4) * SCALE
        r = rng.randint(2, 3) * SCALE
        a = rng.randint(110, 180)
        pygame.draw.circle(dust, (225, 200, 160, a), (dx, dy), r)
    surf.blit(dust, (0, 0))


def _line(surf, pts, color, thickness, *, dy=0):
    shifted = [(x, y + dy) for x, y in pts]
    pygame.draw.lines(surf, color, False, shifted, thickness)


def _sample(pts, t):
    segs, total = [], 0.0
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        d = math.hypot(x1 - x0, y1 - y0)
        segs.append((d, (x0, y0), (x1, y1)))
        total += d
    target = t * total
    acc = 0.0
    for d, p0, p1 in segs:
        if acc + d >= target:
            f = (target - acc) / max(1.0, d)
            return (int(p0[0] + (p1[0] - p0[0]) * f),
                    int(p0[1] + (p1[1] - p0[1]) * f))
        acc += d
    return pts[-1]


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


def _spikes(surf, pts, *, spacing, offset, radius, dark, hi):
    segs, total = [], 0.0
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        d = math.hypot(x1 - x0, y1 - y0)
        segs.append((d, (x0, y0), (x1, y1)))
        total += d
    n = max(1, int(total / spacing))
    for k in range(n + 1):
        rx, ry = _sample(pts, k / n)
        for sign in (-1, 1):
            pygame.draw.circle(surf, dark, (rx, ry + sign * offset), radius)
            pygame.draw.circle(surf, hi,
                               (rx - radius // 2, ry + sign * offset - radius // 2),
                               max(1, radius // 2))


# ──────────────────────────────────────────────────────────────────────────────
# "RAILS UP!" label — 4× font size, matches FloatText "powerup" style
# ──────────────────────────────────────────────────────────────────────────────

def paint_label_hires(surf, pipes):
    """Reimplements FloatText.draw(style="powerup") at SCALE× directly so
    the text isn't blurred by an upscale."""
    base_col = (220, 150, 80)
    text = "RAILS UP!"
    size = 24 * SCALE

    # Position: clear sky between pipes 1 and 2, slightly above the gap.
    label_x = int(((pipes[0].x + PIPE_W + pipes[1].x) / 2) * SCALE)
    label_y = int((pipes[1].gap_y - pipes[1].gap_h / 2 - 18) * SCALE)

    font = pygame.font.SysFont("Arial", size, bold=True)
    base = font.render(text, True, base_col)
    bw, bh = base.get_size()

    # Gradient fill — top 45% toward white, bottom = base.
    light = tuple(int(base_col[i] + (255 - base_col[i]) * 0.45) for i in range(3))
    grad = pygame.Surface((bw, bh), pygame.SRCALPHA)
    for y in range(bh):
        t = y / max(1, bh - 1)
        c = tuple(int(light[i] + (base_col[i] - light[i]) * t) for i in range(3))
        pygame.draw.line(grad, c, (0, y), (bw, y))
    body = base.copy()
    body.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    # Outline.
    dark = tuple(max(0, c // 4) for c in base_col)
    outline = font.render(text, True, dark)
    off = max(2, SCALE)
    for ox, oy in ((-off, 0), (off, 0), (0, -off), (0, off),
                   (-off + 1, -off + 1), (-off + 1, off - 1),
                   (off - 1, -off + 1), (off - 1, off - 1)):
        surf.blit(outline, (label_x - bw // 2 + ox, label_y - bh // 2 + oy))
    surf.blit(body, (label_x - bw // 2, label_y - bh // 2))

    # 8 sparkles around the label.
    cream = (250, 240, 215)
    rng = random.Random(hash(text) & 0xFFFF)
    for _ in range(8):
        sx = label_x + rng.randint(-bw, bw)
        sy = label_y + rng.randint(-bh, bh)
        r = rng.randint(3, 6) * SCALE // 2
        pygame.draw.circle(surf, cream, (sx, sy), r)
        pygame.draw.circle(surf, (255, 255, 255), (sx, sy),
                           max(1, r - SCALE // 2))


# ──────────────────────────────────────────────────────────────────────────────
# Driver
# ──────────────────────────────────────────────────────────────────────────────

def render_hires() -> pygame.Surface:
    phase = 0.78
    palette = biome.palette_for_phase(phase)
    bucket = biome.phase_bucket(phase)

    pipes = [Pipe(x, gy, gh) for (x, gy, gh) in PIPE_LAYOUT]
    for p in pipes:
        p.rail_active = True

    # 1) Native base.
    base = build_base_native(pipes, palette, bucket)
    # 2) Smoothscale up.
    big = pygame.transform.smoothscale(base, (W2, H2))
    # 3) Rail at 4×.
    paint_rail_hires(big, pipes)
    # 4) Pip at 4×.
    mid = pipes[1]
    bx = (mid.x + PIPE_W / 2) * SCALE
    by = (mid.gap_y + mid.gap_h / 2 - BIRD_R) * SCALE
    blit_hires_bird(big, int(bx), int(by))
    # 5) Label at 4×.
    paint_label_hires(big, pipes)
    return big


def main():
    surf = render_hires()
    out = os.path.join(HERE, "04_western_trestle_real.png")
    pygame.image.save(surf, out)
    print(f"wrote {out} ({surf.get_width()}x{surf.get_height()})")


if __name__ == "__main__":
    main()
