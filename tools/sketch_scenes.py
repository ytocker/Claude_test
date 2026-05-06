"""Render representative still PNGs for candidate dynamic background scenes.

Each PNG is one frame, drawn on top of the real Skybit backdrop (sky, biome,
parallax clouds, mountains, ground) at the appropriate biome phase. Animations
are represented as a single evocative frame.

Run:
    python tools/sketch_scenes.py
"""
import os, sys, pathlib, math, random
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import pygame
pygame.init()
pygame.display.set_mode((1, 1))   # needed for fonts / image.save

from game.config import W, H, GROUND_Y
from game.world import World
from game import biome as _biome
from game.draw import (
    get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground,
)

CYCLE = _biome.CYCLE_SECONDS

OUT_DIR = pathlib.Path(__file__).parent.parent / "docs" / "scene_sketches"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def _phase_to_time(phase: float) -> float:
    return ((phase - 0.04) % 1.0) * CYCLE


def _make_world(phase: float, sim_ticks: int = 60) -> World:
    """Build a World, advance it briefly so parallax scroll is non-zero,
    then pin biome_time to the requested phase for the final frame."""
    world = World()
    world.biome_time = _phase_to_time(phase)
    world.ready_t = 0.0
    dt = 1 / 60
    for tick in range(sim_ticks):
        if tick % 24 == 0:
            world.bird.flap()
        world.update(dt)
    world.biome_time = _phase_to_time(phase)
    return world


def _draw_backdrop(surf: pygame.Surface, world: World) -> None:
    """Sky + clouds + mountains + ground — mirrors scenes._draw_background.
    Lifted from tools/biome_snapshots.py:117-146."""
    palette = world.biome_palette
    buckets = _biome.PHASE_BUCKETS
    bf = (world.biome_phase % 1.0) * buckets
    a = int(bf) % buckets
    b = (a + 1) % buckets
    t = bf - int(bf)
    pal_a = _biome.palette_for_phase(a / buckets)
    pal_b = _biome.palette_for_phase(b / buckets)
    sky_a = get_sky_surface_biome(W, H, GROUND_Y, pal_a, a)
    sky_b = get_sky_surface_biome(W, H, GROUND_Y, pal_b, b)
    sky_a.set_alpha(None)
    surf.blit(sky_a, (0, 0))
    if t > 0:
        sky_b.set_alpha(int(t * 255))
        surf.blit(sky_b, (0, 0))
        sky_b.set_alpha(None)

    scroll = world.bg_scroll
    cloud_phase = 1.5
    for i, (bx, by, sc, variant) in enumerate((
            (20, 90, 0.9, 0), (180, 140, 1.1, 2),
            (60, 220, 0.8, 3), (230, 60, 0.7, 1),
            (320, 180, 0.9, 4))):
        ox = ((bx - scroll * (0.04 + 0.02 * i)) % (W + 160)) - 80
        draw_cloud(surf, ox, by + math.sin(cloud_phase * 0.3 + i) * 3,
                   sc, variant=variant)
    draw_mountains(surf, scroll, GROUND_Y, W, palette['mtn_far'], palette['mtn_near'])
    draw_ground(surf, GROUND_Y, W, H, scroll,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))


# ──────────────── Scene primitives ────────────────

def draw_shooting_stars(surf: pygame.Surface, palette: dict) -> None:
    """Faint starfield + one bright shooting streak across the upper sky."""
    rnd = random.Random(101)
    star_alpha = int(palette.get('star_alpha', 200))
    star_layer = pygame.Surface((W, H), pygame.SRCALPHA)
    for _ in range(36):
        sx = rnd.randint(0, W - 1)
        sy = rnd.randint(8, GROUND_Y - 220)
        a = rnd.randint(int(star_alpha * 0.4), star_alpha)
        star_layer.set_at((sx, sy), (255, 255, 255, a))
    surf.blit(star_layer, (0, 0))

    # Streak: diagonal upper-right → lower-left, 24 fading segments.
    streak = pygame.Surface((W, H), pygame.SRCALPHA)
    x0, y0 = 290, 60
    x1, y1 = 200, 130
    segs = 24
    for i in range(segs):
        u0 = i / segs
        u1 = (i + 1) / segs
        a = int(255 * (1.0 - u0) ** 1.6)
        if a <= 4:
            continue
        sx = int(x0 + (x1 - x0) * u0)
        sy = int(y0 + (y1 - y0) * u0)
        ex = int(x0 + (x1 - x0) * u1)
        ey = int(y0 + (y1 - y0) * u1)
        pygame.draw.line(streak, (255, 250, 230, a), (sx, sy), (ex, ey), 2)
    # Bright head
    pygame.draw.circle(streak, (255, 255, 240, 255), (x0, y0), 3)
    pygame.draw.circle(streak, (255, 240, 200, 90),  (x0, y0), 7)
    surf.blit(streak, (0, 0), special_flags=pygame.BLEND_RGB_ADD)


def draw_v_flock(surf: pygame.Surface, palette: dict) -> None:
    """Distant V-formation of birds at mid-far parallax depth."""
    base_color = palette.get('mtn_far', (90, 90, 110))
    silhouette = (max(0, base_color[0] - 60),
                  max(0, base_color[1] - 60),
                  max(0, base_color[2] - 60))

    cx, cy = int(W * 0.55), int(H * 0.40)
    sx, sy = 14, 11  # horizontal/vertical spacing
    # 7 birds: leader at (cx,cy), trailing in two rearward-spreading lines.
    offsets = [
        (0, 0),
        (-sx,    sy),   ( sx,   sy),
        (-2*sx,  2*sy), ( 2*sx, 2*sy),
        (-3*sx,  3*sy), ( 3*sx, 3*sy),
    ]
    for ox, oy in offsets:
        bx, by = cx + ox, cy + oy
        # Tiny chevron: two 2-px diagonal strokes meeting at a point.
        pygame.draw.line(surf, silhouette, (bx - 6, by + 2), (bx, by - 2), 2)
        pygame.draw.line(surf, silhouette, (bx + 6, by + 2), (bx, by - 2), 2)


def draw_lighthouse(surf: pygame.Surface, palette: dict) -> None:
    """Tiny lighthouse silhouette on far hill with a sweeping beam cone."""
    # Tower silhouette
    tower_x = int(W * 0.78)
    tower_top_y = GROUND_Y - 28
    tower_w = 5
    tower_h = 18
    pygame.draw.rect(surf, (15, 15, 25),
                     (tower_x - tower_w // 2, tower_top_y, tower_w, tower_h))
    # Cap (slightly wider)
    pygame.draw.rect(surf, (15, 15, 25),
                     (tower_x - tower_w // 2 - 2, tower_top_y - 3,
                      tower_w + 4, 3))
    # Lamp
    lamp_y = tower_top_y - 1
    pygame.draw.circle(surf, (255, 200, 120), (tower_x, lamp_y), 1)

    # Beam — additive cone reaching up-and-left.
    # Single thin polygon with very low alpha so it reads as atmospheric
    # light catching mist, not a solid spotlight.
    beam = pygame.Surface((W, H), pygame.SRCALPHA)
    beam_len = 220
    spread = math.radians(7)
    angle = math.radians(215)  # pointing up and to the left
    tip_a_x = tower_x + math.cos(angle - spread) * beam_len
    tip_a_y = lamp_y + math.sin(angle - spread) * beam_len
    tip_b_x = tower_x + math.cos(angle + spread) * beam_len
    tip_b_y = lamp_y + math.sin(angle + spread) * beam_len

    # Hand-paint the cone in slim slices, each slice darker toward the
    # tip. Use standard alpha blending (NOT additive) so it reads as a
    # soft atmospheric haze rather than a saturated spotlight.
    slices = 18
    for k in range(slices):
        u0 = k / slices
        u1 = (k + 1) / slices
        a = max(0, int(60 * (1.0 - u0) ** 1.8))
        if a <= 2:
            continue
        a0x = tower_x + (tip_a_x - tower_x) * u0
        a0y = lamp_y  + (tip_a_y - lamp_y)  * u0
        a1x = tower_x + (tip_a_x - tower_x) * u1
        a1y = lamp_y  + (tip_a_y - lamp_y)  * u1
        b0x = tower_x + (tip_b_x - tower_x) * u0
        b0y = lamp_y  + (tip_b_y - lamp_y)  * u0
        b1x = tower_x + (tip_b_x - tower_x) * u1
        b1y = lamp_y  + (tip_b_y - lamp_y)  * u1
        pygame.draw.polygon(beam, (255, 235, 190, a),
                            [(a0x, a0y), (a1x, a1y),
                             (b1x, b1y), (b0x, b0y)])
    surf.blit(beam, (0, 0))  # standard alpha blend, no BLEND_RGB_ADD
    # Lamp bloom — small additive pop at the lamp itself
    glow = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.circle(glow, (255, 220, 160, 70), (tower_x, lamp_y), 3)
    pygame.draw.circle(glow, (255, 180, 120, 35), (tower_x, lamp_y), 6)
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_RGB_ADD)


def draw_fireflies(surf: pygame.Surface, palette: dict) -> None:
    """Cluster of glowing yellow-green dots in the foliage band at dusk."""
    rnd = random.Random(202)
    layer = pygame.Surface((W, H), pygame.SRCALPHA)
    for _ in range(22):
        x = rnd.randint(20, W - 20)
        y = rnd.randint(GROUND_Y - 70, GROUND_Y - 12)
        # Outer bloom
        pygame.draw.circle(layer, (180, 240, 140, 50), (x, y), 6)
        pygame.draw.circle(layer, (210, 255, 160, 90), (x, y), 3)
        # Bright core
        pygame.draw.circle(layer, (240, 255, 200, 220), (x, y), 1)
    surf.blit(layer, (0, 0), special_flags=pygame.BLEND_RGB_ADD)


def draw_fireworks(surf: pygame.Surface, palette: dict) -> None:
    """Three small bursts low on the horizon — distant, not full-screen."""
    bursts = [
        (80,  GROUND_Y - 95,  (255, 180,  90)),
        (180, GROUND_Y - 115, (255, 120, 180)),
        (280, GROUND_Y - 80,  (180, 220, 255)),
    ]
    layer = pygame.Surface((W, H), pygame.SRCALPHA)
    for cx, cy, col in bursts:
        rays = 14
        radius = 18
        for i in range(rays):
            ang = (i / rays) * math.tau
            ex = cx + math.cos(ang) * radius
            ey = cy + math.sin(ang) * radius
            # Per-ray fade: brighter near center, dim at tip
            for step, a in ((0.0, 235), (0.45, 160), (0.85, 60)):
                px = cx + (ex - cx) * step
                py = cy + (ey - cy) * step
                pygame.draw.circle(layer, (*col, a), (int(px), int(py)), 1)
        # White-hot core
        pygame.draw.circle(layer, (255, 255, 240, 240), (cx, cy), 2)
        pygame.draw.circle(layer, (*col, 90),           (cx, cy), 5)
    surf.blit(layer, (0, 0), special_flags=pygame.BLEND_RGB_ADD)


def draw_aurora(surf: pygame.Surface, palette: dict) -> None:
    """Soft sinusoidal green→violet ribbon across the upper sky."""
    layer = pygame.Surface((W, H), pygame.SRCALPHA)
    band_h = 90
    for x in range(0, W, 2):
        baseline = 110 + 30 * math.sin(x * 0.025)
        # Color blend across x
        u = x / W
        r = int(120 * (1 - u) + 180 * u)
        g = int(255 * (1 - u) + 140 * u)
        b = int(180 * (1 - u) + 255 * u)
        for k in range(band_h):
            v = k / band_h
            # Bell curve alpha: 0 → ~110 mid → 0
            a = int(110 * math.sin(v * math.pi))
            if a <= 0:
                continue
            y = int(baseline + k - band_h // 2)
            if 0 <= y < H:
                layer.set_at((x, y),     (r, g, b, a))
                if x + 1 < W:
                    layer.set_at((x + 1, y), (r, g, b, a))
    surf.blit(layer, (0, 0), special_flags=pygame.BLEND_RGB_ADD)


# ──────────────── Driver ────────────────

SCENES = [
    ("01_shooting_stars", 0.62, draw_shooting_stars),
    ("02_v_flock",        0.18, draw_v_flock),
    ("03_lighthouse",     0.62, draw_lighthouse),
    ("04_fireflies",      0.48, draw_fireflies),
    ("05_fireworks",      0.62, draw_fireworks),
    ("06_aurora",         0.78, draw_aurora),
]


def main() -> None:
    for slug, phase, fn in SCENES:
        random.seed(42)  # deterministic backdrop variation
        world = _make_world(phase)
        surf = pygame.Surface((W, H))
        _draw_backdrop(surf, world)
        fn(surf, world.biome_palette)
        out = OUT_DIR / f"{slug}.png"
        pygame.image.save(surf, out)
        print(f"wrote {out}  phase={phase:.2f}")


if __name__ == "__main__":
    main()
