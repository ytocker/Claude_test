"""Render the Western Trestle rail treatment on top of an ACTUAL game frame.

Unlike `render_mockups.py` (which redraws simplified pillars/bird from
scratch), this script boots the real game modules — `game.draw` for sky
and ground, `game.entities.Pipe` for sandstone pillars with their
vegetation/ornament variants, `game.entities.Bird` for Pip — and only
overrides the rail visual on top.

The point: when we evaluate the Western Trestle look, we evaluate it
against the real game's art, not a stand-in.

Run:  python docs/railway_powerup_design/render_western_real.py
Outputs `04_western_trestle_real.png` next to this script (2× upscaled).
"""
from __future__ import annotations

import math
import os
import random
import sys

# Make the repo root importable so `from game.* import ...` resolves when
# this script runs from anywhere.
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

# Real game modules — these are the same imports scenes.py uses.
from game.config import W, H, GROUND_Y, PIPE_W, BIRD_X  # noqa: E402
from game import biome  # noqa: E402
from game.draw import (  # noqa: E402
    get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground,
)
from game.entities import Pipe, Bird, FloatText  # noqa: E402


def render_frame() -> pygame.Surface:
    """Compose one in-game frame at native 360×640, no upscaling yet."""
    surf = pygame.Surface((W, H))

    # Dusk biome phase — drives the warm sky/ground palette automatically,
    # so the "sunset wash" comes from the game's own biome system rather
    # than a hand-painted overlay.
    phase = 0.78  # late golden hour into dusk
    palette = biome.palette_for_phase(phase)
    bucket = biome.phase_bucket(phase)

    # Sky.
    sky = get_sky_surface_biome(W, H, GROUND_Y, palette, bucket)
    surf.blit(sky, (0, 0))

    # Background clouds — same layout block scenes._draw_background uses.
    for i, (bx, by, sc, variant) in enumerate((
            (20, 90, 0.9, 0), (180, 140, 1.1, 2),
            (60, 220, 0.8, 3), (230, 60, 0.7, 1),
            (320, 180, 0.9, 4))):
        draw_cloud(surf, bx, by, sc, variant=variant)

    # Mountains + ground.
    draw_mountains(surf, 0.0, GROUND_Y, W,
                   palette['mtn_far'], palette['mtn_near'])
    draw_ground(surf, GROUND_Y, W, H, 0.0,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))

    # 3 pillars — same staggered layout as the mockup script. Real Pipe
    # instances pick their pillar_variant deterministically from x/gap_y
    # so the silhouettes are stable.
    pipes = [
        Pipe( 50, 285, 170),
        Pipe(170, 235, 170),
        Pipe(290, 300, 170),
    ]
    for p in pipes:
        p.rail_active = True
        p.draw(surf, palette)

    # Bird at the centre pipe's rail height — same lock the real game's
    # _apply_rail_lock produces: feet on top of the lower pillar.
    bird = Bird()
    mid = pipes[1]
    bird.x = mid.x + PIPE_W / 2
    rail_y = mid.gap_y + mid.gap_h / 2
    bird.y = rail_y - 14  # BIRD_R = 14
    bird.vy = 0.0
    bird.frame_t = 1.0  # mid-flap frame (not idle)
    bird.draw(surf)

    # Western Trestle rail treatment, replacing the default _draw_rails.
    _draw_western_trestle_rails(surf, pipes)

    # RAILS UP! pickup label, using the real FloatText class so style
    # ("powerup" gradient + outline + sparkles) matches what the game
    # actually shows. Positioned in the clear gap between pipes 1 & 2 so
    # it doesn't collide with a pillar silhouette.
    label_x = (pipes[0].x + PIPE_W + pipes[1].x) / 2
    label_y = pipes[1].gap_y - pipes[1].gap_h / 2 - 18
    label = FloatText(
        "RAILS UP!", label_x, label_y,
        (220, 150, 80),  # warm amber for western theme
        size=24, life=1.3, vy=-30, style="powerup",
    )
    label.draw(surf)

    return surf


def _draw_western_trestle_rails(surf, pipes):
    """Weathered timber + iron grindrail across the 3 marked pillar tops.

    Builds the same rails-list scenes._draw_rails uses (sorted by x), then
    paints in this order so each layer overlays the previous cleanly:
      1. wooden ties (perpendicular planks, every ~14 game-px)
      2. dark-iron shadow polyline (gives the rail depth)
      3. mid-iron rail polyline
      4. light-iron highlight polyline (1 px above for specular)
      5. hex-headed spikes at every other tie
      6. rust patches scattered along the rail
      7. dust kick-up under Pip's centre-pipe feet
    """
    pipes_sorted = sorted(pipes, key=lambda p: p.x)
    rail_pts: list[tuple[int, int]] = []
    for p in pipes_sorted:
        rail_y = int(p.gap_y + p.gap_h / 2)
        rail_pts.append((int(p.x), rail_y))
        rail_pts.append((int(p.x + PIPE_W), rail_y))

    pine_dk  = ( 70,  45,  25)
    pine     = (135,  90,  50)
    pine_hi  = (180, 130,  75)
    iron_dk  = ( 50,  45,  45)
    iron     = (110, 100,  95)
    iron_hi  = (190, 180, 175)
    rust     = (170,  80,  35)

    # 1) Wooden ties.
    _draw_ties(surf, rail_pts, spacing=8,
               length=14, thickness=4,
               color_dk=pine_dk, color_hi=pine_hi, wood_grain=True)

    # 2-4) Two parallel iron rails (a 6-game-px gauge — narrow because
    # the pillars are only 58 px wide).
    for dy in (+3, -3):
        _draw_rail_polyline(surf, rail_pts, iron_dk, 3, dy=dy)
    for dy in (+3, -3):
        _draw_rail_polyline(surf, rail_pts, iron, 2, dy=dy)
    for dy in (+2, -4):
        _draw_rail_polyline(surf, rail_pts, iron_hi, 1, dy=dy)

    # 5) Hex spikes at tie ends, every other tie.
    _draw_spikes(surf, rail_pts, spacing=16, offset=5,
                 dark=iron_dk, hi=iron_hi)

    # 6) Rust patches — randomized along the rail so each render is
    # similar but not identical.
    rng = random.Random(31)
    for _ in range(14):
        rx, ry = _rail_lerp(rail_pts, rng.random())
        pygame.draw.circle(surf, rust, (rx, ry + 3), rng.randint(2, 3))

    # 7) Dust trail behind Pip's feet — sparse, low-opacity, drifting back.
    mid_pipe = pipes_sorted[len(pipes_sorted) // 2]
    feet_x = int(mid_pipe.x + PIPE_W / 2)
    feet_y = int(mid_pipe.gap_y + mid_pipe.gap_h / 2)
    rng = random.Random(7)
    dust_layer = pygame.Surface((W, H), pygame.SRCALPHA)
    for _ in range(10):
        dx = feet_x + rng.randint(-22, -2)   # behind (left of) the bird
        dy = feet_y + rng.randint(-3, 4)
        r = rng.randint(2, 3)
        a = rng.randint(90, 160)
        pygame.draw.circle(dust_layer, (225, 200, 160, a), (dx, dy), r)
    surf.blit(dust_layer, (0, 0))


def _draw_rail_polyline(surf, pts, color, thickness, *, dy=0):
    """Draw a polyline through every point, offset vertically by dy."""
    shifted = [(x, y + dy) for x, y in pts]
    pygame.draw.lines(surf, color, False, shifted, thickness)


def _rail_lerp(pts, t):
    """Sample (x, y) at parametric t∈[0,1] along the full polyline."""
    segs = []
    total = 0.0
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        d = math.hypot(x1 - x0, y1 - y0)
        segs.append(d)
        total += d
    target = t * total
    acc = 0.0
    for i, d in enumerate(segs):
        if acc + d >= target:
            f = (target - acc) / max(1.0, d)
            x0, y0 = pts[i]
            x1, y1 = pts[i + 1]
            return int(x0 + (x1 - x0) * f), int(y0 + (y1 - y0) * f)
        acc += d
    return pts[-1]


def _draw_ties(surf, pts, *, spacing, length, thickness,
               color_dk, color_hi, wood_grain=False):
    """Perpendicular ties along the polyline."""
    segs = []
    total = 0.0
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        d = math.hypot(x1 - x0, y1 - y0)
        segs.append(d)
        total += d
    n = max(1, int(total / spacing))
    for k in range(n + 1):
        t = k / n
        target = t * total
        acc = 0.0
        for i, d in enumerate(segs):
            if acc + d >= target:
                f = (target - acc) / max(1.0, d)
                x0, y0 = pts[i]
                x1, y1 = pts[i + 1]
                cx = int(x0 + (x1 - x0) * f)
                cy = int(y0 + (y1 - y0) * f)
                dx = x1 - x0
                dy = y1 - y0
                seg_len = max(1.0, math.hypot(dx, dy))
                nx = -dy / seg_len
                ny = dx / seg_len
                half = length / 2
                p0 = (int(cx + nx * half), int(cy + ny * half))
                p1 = (int(cx - nx * half), int(cy - ny * half))
                pygame.draw.line(surf, color_dk, p0, p1, thickness)
                hi0 = (int(cx + nx * half * 0.55),
                       int(cy + ny * half * 0.55))
                hi1 = (int(cx - nx * half * 0.55),
                       int(cy - ny * half * 0.55))
                pygame.draw.line(surf, color_hi, hi0, hi1,
                                 max(1, thickness - 2))
                break
            acc += d


def _draw_spikes(surf, pts, *, spacing, offset, dark, hi):
    """Small hex-headed spikes at tie ends, every `spacing` game-px."""
    segs = []
    total = 0.0
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        d = math.hypot(x1 - x0, y1 - y0)
        segs.append(d)
        total += d
    n = max(1, int(total / spacing))
    for k in range(n + 1):
        t = k / n
        rx, ry = _rail_lerp(pts, t)
        for off in (-offset, offset):
            pygame.draw.circle(surf, dark, (rx, ry + off), 2)
            pygame.draw.circle(surf, hi, (rx - 1, ry + off - 1), 1)


def main():
    surf = render_frame()
    # Upscale 2× with nearest-neighbour for a crisp pixel look on GitHub.
    big = pygame.transform.scale(surf, (W * 2, H * 2))
    out = os.path.join(HERE, "04_western_trestle_real.png")
    pygame.image.save(big, out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
