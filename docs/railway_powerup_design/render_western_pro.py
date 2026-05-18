"""Five polished iterations on the Western Trestle rail treatment.

All five render on top of REAL in-game frames (using game.draw,
game.entities, game.biome) — only the rail overlay differs. Each picks
its own biome phase so the lighting reinforces the material story:
brass under late golden hour, silver iron under moonlight, etc.

What "polished" means here, vs the first pass:
  - Rails built as 4-layer stacks (shadow + body + highlight + specular)
    instead of a single coloured line — gives metallic depth.
  - Ties spaced wider with less per-tile noise, so the rail reads as
    one continuous form rather than a stripe pattern.
  - Per-variant atmospheric accent (gold pinstripe, cyan rim glow,
    amber heat, brass rivets, watercolor wash) doing the heavy lifting
    instead of clutter.

Run:  python docs/railway_powerup_design/render_western_pro.py
Outputs 5 PNGs (2× upscaled) next to this script.
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

from game.config import W, H, GROUND_Y, PIPE_W  # noqa: E402
from game import biome  # noqa: E402
from game.draw import (  # noqa: E402
    get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground,
)
from game.entities import Pipe, Bird, FloatText  # noqa: E402

CLOUD_LAYOUT = (
    (20, 90, 0.9, 0), (180, 140, 1.1, 2),
    (60, 220, 0.8, 3), (230, 60, 0.7, 1),
    (320, 180, 0.9, 4),
)

PIPE_LAYOUT = (
    ( 50, 285, 170),
    (170, 235, 170),
    (290, 300, 170),
)


# ──────────────────────────────────────────────────────────────────────────────
# Shared scaffolding — biome-aware base frame, pipes, bird, rail polyline
# ──────────────────────────────────────────────────────────────────────────────

def base_frame(biome_phase: float):
    """Sky + clouds + mountains + ground at the requested biome phase."""
    palette = biome.palette_for_phase(biome_phase)
    bucket = biome.phase_bucket(biome_phase)
    surf = pygame.Surface((W, H))
    sky = get_sky_surface_biome(W, H, GROUND_Y, palette, bucket)
    surf.blit(sky, (0, 0))
    for bx, by, sc, variant in CLOUD_LAYOUT:
        draw_cloud(surf, bx, by, sc, variant=variant)
    draw_mountains(surf, 0.0, GROUND_Y, W,
                   palette['mtn_far'], palette['mtn_near'])
    draw_ground(surf, GROUND_Y, W, H, 0.0,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    return surf, palette


def setup_scene(palette):
    pipes = [Pipe(x, gy, gh) for (x, gy, gh) in PIPE_LAYOUT]
    for p in pipes:
        p.rail_active = True
        p.draw_called_palette = palette
    return pipes


def rail_polyline(pipes):
    """Same data scenes._draw_rails uses: left + right edge per pipe."""
    pipes_sorted = sorted(pipes, key=lambda p: p.x)
    pts = []
    for p in pipes_sorted:
        rail_y = int(p.gap_y + p.gap_h / 2)
        pts.append((int(p.x), rail_y))
        pts.append((int(p.x + PIPE_W), rail_y))
    return pts


def setup_bird(pipes):
    bird = Bird()
    mid = pipes[1]
    bird.x = mid.x + PIPE_W / 2
    bird.y = mid.gap_y + mid.gap_h / 2 - 14
    bird.vy = 0.0
    bird.frame_t = 1.0
    return bird


def paint_label(surf, pipes, color, *, text="RAILS UP!", size=24):
    """Real FloatText, positioned in the clear sky between pipes 1 and 2."""
    lx = (pipes[0].x + PIPE_W + pipes[1].x) / 2
    ly = pipes[1].gap_y - pipes[1].gap_h / 2 - 18
    label = FloatText(text, lx, ly, color,
                      size=size, life=1.3, vy=-30, style="powerup")
    label.draw(surf)


def save_2x(surf, out_path):
    big = pygame.transform.scale(surf, (W * 2, H * 2))
    pygame.image.save(big, out_path)


# ──────────────────────────────────────────────────────────────────────────────
# Polyline helpers (shared by every rail variant)
# ──────────────────────────────────────────────────────────────────────────────

def line_offset(surf, pts, color, thickness, *, dy=0, alpha=255):
    pts_off = [(x, y + dy) for x, y in pts]
    if alpha >= 255:
        pygame.draw.lines(surf, color, False, pts_off, thickness)
    else:
        layer = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.lines(layer, (*color, alpha), False, pts_off, thickness)
        surf.blit(layer, (0, 0))


def line_glow(surf, pts, color, thickness, *, dy=0, alpha=110):
    """Additive soft line — used for cyan moonlight rims and ember heat."""
    layer = pygame.Surface((W, H), pygame.SRCALPHA)
    pts_off = [(x, y + dy) for x, y in pts]
    pygame.draw.lines(layer, (*color, alpha), False, pts_off, thickness)
    surf.blit(layer, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


def sample_along(pts, t):
    segs = []
    total = 0.0
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


def each_along(pts, spacing):
    """Yield (cx, cy, nx, ny) tuples along the polyline at fixed spacing.

    nx, ny is the perpendicular unit vector (for placing ties perpendicular
    to the rail's local direction across the rail bridges).
    """
    segs = []
    total = 0.0
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        d = math.hypot(x1 - x0, y1 - y0)
        segs.append((d, (x0, y0), (x1, y1)))
        total += d
    n = max(1, int(total / spacing))
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
                yield cx, cy, -dy / seg_len, dx / seg_len
                break
            acc += d


def paint_ties(surf, pts, *, spacing, length, thickness,
               body, edge, hi=None, grain=False):
    """Perpendicular ties along the polyline with optional grain + highlight."""
    half = length / 2
    for cx, cy, nx, ny in each_along(pts, spacing):
        p0 = (int(cx + nx * half), int(cy + ny * half))
        p1 = (int(cx - nx * half), int(cy - ny * half))
        pygame.draw.line(surf, edge, p0, p1, thickness + 2)
        pygame.draw.line(surf, body, p0, p1, thickness)
        if hi is not None:
            hi0 = (int(cx + nx * half * 0.4), int(cy + ny * half * 0.4))
            hi1 = (int(cx - nx * half * 0.4), int(cy - ny * half * 0.4))
            pygame.draw.line(surf, hi, hi0, hi1, max(1, thickness - 2))
        if grain:
            g0 = (int(cx + nx * half * 0.7),
                  int(cy + ny * half * 0.7))
            g1 = (int(cx - nx * half * 0.7),
                  int(cy - ny * half * 0.7))
            pygame.draw.line(surf, edge, g0, g1, 1)


# ──────────────────────────────────────────────────────────────────────────────
# Variant 1 — PULLMAN (1920s premium walnut + polished brass + gold pinstripe)
# ──────────────────────────────────────────────────────────────────────────────

def paint_pullman(surf, pts):
    """Premium 1920s pullman aesthetic.

    Visual story: deep walnut ties spaced like a vintage carriage's
    footplate, brass rails built up in 4 layers for proper metallic
    body, hairline gold pinstripe under the rails as decorative trim,
    small brass finials at the rail's endpoints.
    """
    walnut_dk = ( 35,  20,  10)
    walnut    = ( 95,  55,  30)
    walnut_hi = (155, 105,  65)

    brass_dk  = (105,  60,  20)
    brass     = (200, 145,  55)
    brass_hi  = (245, 200, 110)
    brass_sp  = (255, 235, 175)
    gold_pin  = (220, 175,  70)

    # Ties — wide spacing, satin grain.
    paint_ties(surf, pts, spacing=12, length=16, thickness=5,
               body=walnut, edge=walnut_dk, hi=walnut_hi, grain=True)

    # 4-layer brass rail (drop shadow + body + highlight + specular).
    line_offset(surf, pts, brass_dk, 4, dy=2)
    line_offset(surf, pts, brass,    3, dy=0)
    line_offset(surf, pts, brass_hi, 2, dy=-1)
    line_offset(surf, pts, brass_sp, 1, dy=-1)

    # Hairline gold pinstripe — single 1px line below the rail.
    line_offset(surf, pts, gold_pin, 1, dy=5)

    # Brass end-cap finials at the very first and last points.
    for cx, cy in (pts[0], pts[-1]):
        _draw_finial(surf, cx, cy, brass_dk, brass, brass_hi)


def _draw_finial(surf, cx, cy, dk, body, hi):
    """Tiny scroll-cap ornament at rail end-points."""
    pygame.draw.circle(surf, dk, (cx, cy), 3)
    pygame.draw.circle(surf, body, (cx, cy), 2)
    pygame.draw.circle(surf, hi, (cx - 1, cy - 1), 1)


# ──────────────────────────────────────────────────────────────────────────────
# Variant 2 — MIDNIGHT LIMITED (night biome, moonlit silver iron, cyan rim)
# ──────────────────────────────────────────────────────────────────────────────

def paint_midnight(surf, pts):
    """Moonlit iron rail under a night sky.

    Visual story: rails are silvery iron rim-lit with cool cyan moonlight.
    Ties are muted dark wood that disappears into shadow. A soft cyan
    halo underneath the rail anchors the levitation/energy read in a
    palette that won't clash with the night biome.
    """
    tie_dk = (15, 15, 25)
    tie    = (45, 45, 60)

    iron_dk = (25,  30,  45)
    iron    = (90, 100, 130)
    iron_hi = (185, 200, 225)
    cyan    = ( 70, 200, 240)
    cyan_hi = (180, 240, 255)

    # Soft cyan underglow — three nested additive lines.
    line_glow(surf, pts, cyan, 11, dy=0, alpha=22)
    line_glow(surf, pts, cyan, 7,  dy=0, alpha=45)
    line_glow(surf, pts, cyan, 4,  dy=0, alpha=80)

    # Muted ties (almost a silhouette).
    paint_ties(surf, pts, spacing=14, length=14, thickness=3,
               body=tie, edge=tie_dk)

    # Iron rail stack — cool palette.
    line_offset(surf, pts, iron_dk, 4, dy=2)
    line_offset(surf, pts, iron,    3, dy=0)
    line_offset(surf, pts, iron_hi, 1, dy=-1)

    # Cyan moonlight rim along the top edge of the rail.
    line_glow(surf, pts, cyan_hi, 1, dy=-2, alpha=210)

    # Pinpoint moon-sparkles at the bridge midpoints.
    for t in (0.18, 0.5, 0.82):
        sx, sy = sample_along(pts, t)
        pygame.draw.circle(surf, cyan_hi, (sx, sy - 2), 2)


# ──────────────────────────────────────────────────────────────────────────────
# Variant 3 — EMBER FORGE (rails glow red-hot, amber heat + rising sparks)
# ──────────────────────────────────────────────────────────────────────────────

def paint_ember(surf, pts):
    """Active-state read: the rail just got powered up and is molten.

    Visual story: dark iron jacket holds in a glowing amber/red core.
    Heat radiates upward into the sky as faint orange sparks. Ties are
    charred near-black so they read as scorched wood under the heat.
    """
    char    = ( 25,  18,  15)
    charcoal = (55, 35, 25)
    iron_dk = ( 40,  25,  20)
    ember_dk = (180,  55,  20)
    ember   = (240, 110,  35)
    amber   = (255, 180,  60)
    amber_hi = (255, 230, 160)

    # Heat haze — wide soft amber additive glow underneath.
    line_glow(surf, pts, ember, 15, dy=4, alpha=18)
    line_glow(surf, pts, ember, 9,  dy=2, alpha=40)
    line_glow(surf, pts, amber, 5,  dy=0, alpha=80)

    # Charred ties.
    paint_ties(surf, pts, spacing=12, length=14, thickness=4,
               body=charcoal, edge=char)

    # Rail stack — dark iron jacket containing a molten amber core.
    line_offset(surf, pts, iron_dk, 5, dy=2)
    line_offset(surf, pts, ember_dk, 4, dy=1)
    line_offset(surf, pts, ember,    3, dy=0)
    line_offset(surf, pts, amber,    2, dy=-1)
    line_offset(surf, pts, amber_hi, 1, dy=-2)

    # Rising sparks — pinpoint amber dots above the rail.
    rng = random.Random(13)
    sparks = pygame.Surface((W, H), pygame.SRCALPHA)
    for _ in range(40):
        t = rng.random()
        rx, ry = sample_along(pts, t)
        sx = rx + rng.randint(-3, 3)
        sy = ry - rng.randint(2, 30)
        r = rng.randint(1, 2)
        a = max(80, 220 - (ry - sy) * 5)
        pygame.draw.circle(sparks, (*amber_hi, a), (sx, sy), r)
    surf.blit(sparks, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


# ──────────────────────────────────────────────────────────────────────────────
# Variant 4 — ONYX VAULT (matte black ties + gunmetal rails + brass rivets)
# ──────────────────────────────────────────────────────────────────────────────

def paint_onyx(surf, pts):
    """Restrained, premium, "vault-grade" finish.

    Visual story: matte-black hardwood ties (think obsidian) carry
    gunmetal rails. The only warm accent is the brass rivets at each
    tie. Reads as expensive minimalism — the rail is the focal point,
    everything else gets out of its way.
    """
    black_dk = ( 10,  10,  12)
    black    = ( 30,  30,  38)
    black_hi = ( 70,  70,  82)

    gun_dk = ( 40,  42,  50)
    gun    = (100, 105, 118)
    gun_hi = (195, 200, 215)
    gun_sp = (245, 248, 255)

    brass_dk = (110,  70,  25)
    brass    = (220, 165,  60)
    brass_hi = (255, 225, 135)

    # Subtle 1-px slate shadow under the rail line — sells the depth.
    line_offset(surf, pts, (15, 15, 18), 5, dy=3, alpha=200)

    # Matte-black ties — single soft highlight along the upper edge.
    paint_ties(surf, pts, spacing=14, length=15, thickness=4,
               body=black, edge=black_dk, hi=black_hi)

    # Gunmetal rail stack.
    line_offset(surf, pts, gun_dk, 4, dy=1)
    line_offset(surf, pts, gun,    3, dy=0)
    line_offset(surf, pts, gun_hi, 2, dy=-1)
    line_offset(surf, pts, gun_sp, 1, dy=-1)

    # Brass rivets at every tie centre.
    for cx, cy, _, _ in each_along(pts, 14):
        pygame.draw.circle(surf, brass_dk, (cx, cy), 3)
        pygame.draw.circle(surf, brass, (cx, cy), 2)
        pygame.draw.circle(surf, brass_hi, (cx - 1, cy - 1), 1)


# ──────────────────────────────────────────────────────────────────────────────
# Variant 5 — STORYBOOK (watercolor painterly: soft edges, hand-drawn feel)
# ──────────────────────────────────────────────────────────────────────────────

def paint_storybook(surf, pts):
    """Ghibli-painterly take: warm hand-drawn rail with watercolor wash.

    Visual story: ties are stubby brushstrokes that imperfectly stack
    along the rail. The rail itself is a warm sienna with a soft cream
    halo around it, like an inked drawing washed with a pastel layer.
    Reads gentler and more inviting than the metallic variants — picks
    up the game's tropical-arcade tone instead of fighting it.
    """
    ink       = ( 55,  25,  10)
    sienna_dk = (130,  60,  20)
    sienna    = (190, 105,  40)
    sienna_hi = (240, 170,  90)
    cream     = (255, 235, 195)

    # Soft cream halo — narrower than before so the rail silhouette
    # stays crisp instead of bleeding into a fluffy band.
    halo = pygame.Surface((W, H), pygame.SRCALPHA)
    for w, a in ((9, 18), (5, 35)):
        pts_off = [(x, y + 1) for x, y in pts]
        pygame.draw.lines(halo, (*cream, a), False, pts_off, w)
    surf.blit(halo, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # Hand-drawn ties — single bold ink-and-wash stroke per tie, with
    # a brighter sienna highlight on the upper half so each tie reads
    # as a discrete brushstroke instead of a soft blob.
    rng = random.Random(91)
    half = 7
    for cx, cy, nx, ny in each_along(pts, 13):
        jx0 = cx + nx * half + rng.randint(-1, 1)
        jy0 = cy + ny * half + rng.randint(-1, 1)
        jx1 = cx - nx * half + rng.randint(-1, 1)
        jy1 = cy - ny * half + rng.randint(-1, 1)
        pygame.draw.line(surf, ink, (int(jx0), int(jy0)),
                         (int(jx1), int(jy1)), 5)
        pygame.draw.line(surf, sienna_dk, (int(jx0), int(jy0)),
                         (int(jx1), int(jy1)), 3)
        pygame.draw.line(surf, sienna_hi,
                         (int(cx + nx * half * 0.5),
                          int(cy + ny * half * 0.5 - 1)),
                         (int(cx - nx * half * 0.5),
                          int(cy - ny * half * 0.5 - 1)), 1)

    # Rail — full sienna stack with crisp ink outline and a single
    # cream specular pixel-line so it reads as painted, not metallic.
    line_offset(surf, pts, ink, 5, dy=2)
    line_offset(surf, pts, sienna_dk, 4, dy=1)
    line_offset(surf, pts, sienna, 3, dy=0)
    line_offset(surf, pts, sienna_hi, 2, dy=-1)
    line_offset(surf, pts, cream, 1, dy=-2)


# ──────────────────────────────────────────────────────────────────────────────
# Drivers
# ──────────────────────────────────────────────────────────────────────────────

def render(out_path, *, biome_phase, paint_rail, label_color, label_size=24):
    surf, palette = base_frame(biome_phase)
    pipes = setup_scene(palette)
    for p in pipes:
        p.draw(surf, palette)
    pts = rail_polyline(pipes)
    paint_rail(surf, pts)
    bird = setup_bird(pipes)
    bird.draw(surf)
    paint_label(surf, pipes, label_color, size=label_size)
    save_2x(surf, out_path)


def main():
    variants = [
        ("04a_pullman.png",   0.78, paint_pullman,   (220, 175,  70)),
        ("04b_midnight.png",  0.65, paint_midnight,  ( 70, 200, 240)),
        ("04c_ember.png",     0.55, paint_ember,     (255, 180,  60)),
        ("04d_onyx.png",      0.05, paint_onyx,      (220, 165,  60)),
        ("04e_storybook.png", 0.30, paint_storybook, (235, 165,  85)),
    ]
    for name, phase, paint, col in variants:
        out = os.path.join(HERE, name)
        render(out, biome_phase=phase, paint_rail=paint, label_color=col)
        print(f"  wrote {name}")
    print(f"\n5 polished Western Trestle variants saved to {HERE}")


if __name__ == "__main__":
    main()
