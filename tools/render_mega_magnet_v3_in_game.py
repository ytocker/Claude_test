"""Render the chosen Mega Magnet active-field (V3: 2.0× + 5 rings)
over a real in-game scene, paired with the regular Magnet field.

Builds the world via game.world.World, advances it with
world_idle_tick so pipes scroll into frame, then renders the exact
in-game layer order (background → pipes → weather → coins → bird →
field). Field uses the same parametric renderer from
render_mega_magnet_effect_candidates.py so the regular cell stays
verbatim with game/scenes.py.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_mega_magnet_v3_in_game.py
"""

import math
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

_OUT = os.path.join(_REPO, "docs", "mega_magnet_effects")
os.makedirs(_OUT, exist_ok=True)

pygame.init()
pygame.font.init()

from game.config import W, H, GROUND_Y, MAGNET_RADIUS  # noqa: E402
from game import biome as _biome  # noqa: E402
from game.draw import (  # noqa: E402
    get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground,
)
from game.world import World  # noqa: E402
from game.entities import Coin, Pipe  # noqa: E402


# ── field renderer (copied parametric form from effect-candidates tool) ─────


DEFAULT_RINGS = (
    (1.00, 0.0,  180, 3, 1.00, (255, 220, 100)),
    (0.78, 0.6,  140, 2, 0.85, (255, 195,  60)),
    (0.55, 1.2,  100, 2, 0.70, (235, 165,  35)),
)

V3_RINGS = (
    (1.00, 0.0,  170, 3, 1.00, (255, 220, 100)),
    (0.88, 0.3,  155, 2, 0.94, (255, 210,  90)),
    (0.76, 0.6,  140, 2, 0.88, (255, 200,  70)),
    (0.64, 0.9,  125, 2, 0.82, (250, 190,  55)),
    (0.52, 1.2,  110, 2, 0.75, (240, 175,  45)),
    (0.40, 1.5,   95, 2, 0.68, (225, 160,  35)),
    (0.28, 1.8,   80, 2, 0.60, (210, 145,  25)),
)


def draw_field(surf, cx, cy, t_pulse_phase, rad, rings,
               glow_alpha_peak=72, width_mul=1):
    t_pulse = t_pulse_phase * 5.5
    field = pygame.Surface((int(rad * 2 + 8), int(rad * 2 + 8)),
                           pygame.SRCALPHA)
    lcx, lcy = int(rad + 4), int(rad + 4)
    BREATH = 0.30
    s_outer = math.sin(t_pulse + 0.0)
    u_outer = (s_outer + 1) / 2
    outer_factor = 1.0 - BREATH * (1.0 - u_outer)
    glow_rad = rad * outer_factor
    GLOW_COL = (245, 175, 40)
    for i in range(18, 0, -1):
        r = int(glow_rad * i / 18)
        inner_t = i / 18
        bell = math.exp(-((inner_t - 0.85) ** 2) / 0.15)
        a = int(glow_alpha_peak * bell)
        if a > 0:
            pygame.draw.circle(field, (*GLOW_COL, a), (lcx, lcy), r)
    AA_COL = (255, 240, 180)
    for rfac, phase, alpha, width, breath_scale, ring_col in rings:
        amp = BREATH * breath_scale
        s = math.sin(t_pulse + phase)
        u = (s + 1) / 2
        rr = int(rad * rfac * (1.0 - amp * (1.0 - u)))
        w = max(1, int(width * width_mul))
        pygame.draw.circle(field, (*AA_COL, alpha // 3),
                           (lcx, lcy), rr + 1, w)
        pygame.draw.circle(field, (*AA_COL, alpha // 3),
                           (lcx, lcy), rr - 1, w)
        pygame.draw.circle(field, (*ring_col, alpha),
                           (lcx, lcy), rr, w)
    surf.blit(field, (cx - lcx, cy - lcy))


# ── scene helpers (verbatim from tools/take_screenshots.py) ─────────────────


def draw_bg(surf, scroll=0, phase=0.62):
    buckets = _biome.PHASE_BUCKETS
    bucket_f = (phase % 1.0) * buckets
    a = int(bucket_f) % buckets
    b = (a + 1) % buckets
    t = bucket_f - int(bucket_f)
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
    for i, (bx, by, sc, variant) in enumerate(
            ((20, 90, 0.9, 0), (180, 140, 1.1, 2),
             (60, 220, 0.8, 3), (230, 60, 0.7, 1),
             (320, 180, 0.9, 4))):
        ox = ((bx - scroll * (0.04 + 0.02 * i)) % (W + 160)) - 80
        draw_cloud(surf, ox, by + math.sin(1.2 + i) * 3, sc, variant=variant)
    pal = pal_a
    draw_mountains(surf, scroll, GROUND_Y, W, pal['mtn_far'], pal['mtn_near'])
    draw_ground(surf, GROUND_Y, W, H, scroll, pal['ground_top'],
                pal['ground_mid'], (60, 40, 25))


# ── world setup — settle a representative play frame ────────────────────────


def build_settled_world(seed=11, ticks=60):
    """Spin up a World, idle-tick briefly for clouds/biome to settle,
    then place pipes + coins explicitly so the scene reads at a glance."""
    random.seed(seed)
    world = World()
    for _ in range(ticks):
        world.world_idle_tick(1 / 60)
    # Replace the off-screen seed pipes with two visible ones flanking
    # the bird so the field's footprint reads against real pillar geometry.
    from game.config import PIPE_W
    world.pipes = [
        Pipe(40 - PIPE_W // 2, 220, 130),       # left edge
        Pipe(280, 360, 130),                    # right side
    ]
    # Coins scattered around the bird — inside and just outside the 2×
    # field so the magnet's purpose reads at a glance.
    bx, by = world.bird.x, world.bird.y
    world.coins = []
    for dx, dy in ((+95, -60), (+55, +50), (-35, -70),
                   (-75, +45), (+115, +20), (-95, -20),
                   (+135, -40), (-115, +10)):
        world.coins.append(Coin(bx + dx, by + dy))
    # Keep the magnet visibly active so the field renders.
    world.magnet_timer = 6.0
    return world


def render_play_scene(world):
    """Real in-game layer order (background → pipes → weather → coins →
    bird), excluding the field. The field is composited by the caller
    so we can swap in different sizes against an identical scene."""
    surf = pygame.Surface((W, H))
    draw_bg(surf, scroll=world.bg_scroll, phase=getattr(world, "biome_phase", 0.62))
    pipe_palette = world.biome_palette
    kfc_active = getattr(world.bird, "kfc_active", False)
    for p in world.pipes:
        p.draw(surf, pipe_palette, kfc_visual=kfc_active)
    world.weather.draw(surf)
    triple_active = world.triple_timer > 0
    for c in world.coins:
        c.draw(surf, kfc_active=kfc_active, triple_active=triple_active)
    for m in world.powerups:
        m.draw(surf)
    world.bird.draw(surf, 0, 0)
    return surf


# ── compositing ─────────────────────────────────────────────────────────────


PULSE = 0.45  # field's "exhale" peak so rings are most visible


def _label(surf, x, y, w, h, line1, line2=None):
    band = pygame.Surface((w, h), pygame.SRCALPHA)
    band.fill((0, 0, 0, 210))
    pygame.draw.line(band, (255, 215, 0), (0, 0), (w, 0), 1)
    f1 = pygame.font.SysFont(None, 26)
    t1 = f1.render(line1, True, (255, 240, 200))
    band.blit(t1, t1.get_rect(midtop=(w // 2, 6)))
    if line2:
        f2 = pygame.font.SysFont(None, 18)
        t2 = f2.render(line2, True, (180, 200, 220))
        band.blit(t2, t2.get_rect(midtop=(w // 2, 34)))
    surf.blit(band, (x, y))


def main():
    world = build_settled_world()
    cx, cy = int(world.bird.x), int(world.bird.y)

    # REGULAR — verbatim regular field over the real scene.
    reg_scene = render_play_scene(world)
    draw_field(reg_scene, cx, cy, PULSE,
               rad=MAGNET_RADIUS, rings=DEFAULT_RINGS)
    pygame.image.save(reg_scene,
                      os.path.join(_OUT, "v3_in_game_regular.png"))

    # MEGA V3 — 2.0× scale + 5 rings.
    mega_scene = render_play_scene(world)
    draw_field(mega_scene, cx, cy, PULSE,
               rad=MAGNET_RADIUS * 2.0, rings=V3_RINGS)
    pygame.image.save(mega_scene,
                      os.path.join(_OUT, "v3_in_game_mega.png"))

    # Side-by-side comparison with a label band underneath.
    BAND_H = 56
    composite = pygame.Surface((W * 2 + 4, H + BAND_H))
    composite.fill((5, 10, 20))
    composite.blit(reg_scene, (0, 0))
    composite.blit(mega_scene, (W + 4, 0))
    _label(composite, 0, H, W, BAND_H,
           "REGULAR", f"r = {MAGNET_RADIUS:.0f}px (game/scenes.py)")
    _label(composite, W + 4, H, W, BAND_H,
           "MEGA — V3 (2.0× + 7 rings)",
           f"r = {MAGNET_RADIUS * 2.0:.0f}px, 7 nested rings")
    pygame.image.save(composite,
                      os.path.join(_OUT, "v3_in_game_compare.png"))

    print(f"wrote 3 in-game frames to {_OUT}")


if __name__ == "__main__":
    main()
