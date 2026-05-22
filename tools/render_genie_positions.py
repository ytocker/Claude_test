"""Render the genie cast moment with multiple (position, size) options
so we can pick the one that fits best in the gameplay frame.

Output: docs/screenshots/genie_cinematic/positions_v1.png — a 6-up
contact sheet showing each option in a real gameplay context (with
clouds, mountains, ground, parrot, and the 3 conjured powerups).

Run from repo root:
    SDL_VIDEODRIVER=dummy python -m tools.render_genie_positions
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import random
import pygame

pygame.init()
pygame.display.set_mode((360, 640))

from game.config import W, H, GROUND_Y
from game import biome as _biome
from game.draw import (
    get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground,
)
from game.world import World
from game.entities import PowerUp
from game.hud import HUD


OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                       "docs", "screenshots", "genie_cinematic")
os.makedirs(OUT_DIR, exist_ok=True)


# Position + size options to compare. Each is (label, gx, gy, scale).
# gx/gy are world coords (= screen coords); scale is the display
# multiplier applied to the 320×460 native sprite.
#   320 × 0.20 ≈  64 × 92  px on screen  (~18% of W)
#   320 × 0.24 ≈  77 × 110 px on screen  (~21% of W)
#   320 × 0.28 ≈  90 × 129 px on screen  (~25% of W)
#   320 × 0.32 = 102 × 147 px on screen  (~28% of W)  ← current
POSITION_OPTIONS = [
    # (label,                       gx,  gy,  scale)
    ("1: top-LEFT corner, small",    70,  78, 0.22),
    ("2: top-RIGHT corner, small",  300,  78, 0.22),
    ("3: below score, central, sm", 180, 170, 0.22),
    ("4: mid-LEFT, near parrot",     90, 230, 0.24),
    ("5: mid-RIGHT, opposite",      290, 230, 0.24),
    ("6: top-RIGHT, slightly big",  290, 100, 0.28),
]


def render_world_at_cast(world, target):
    """Paint background + entities so the frame reads as real
    gameplay. Mirrors the render order in game/scenes.py."""
    phase = world.biome_phase
    pal = _biome.palette_for_phase(phase)
    buckets = _biome.PHASE_BUCKETS
    bucket_f = (phase % 1.0) * buckets
    a = int(bucket_f) % buckets
    sky = get_sky_surface_biome(W, H, GROUND_Y, pal, a)
    target.blit(sky, (0, 0))
    for bx, by, sc, variant in (
            (20, 90, 0.9, 0), (220, 130, 1.0, 2), (90, 200, 0.8, 3)):
        draw_cloud(target, bx, by, sc, variant=variant)
    draw_mountains(target, world.bg_scroll, GROUND_Y, W,
                   pal["mtn_far"], pal["mtn_near"])
    draw_ground(target, GROUND_Y, W, H, world.bg_scroll,
                pal["ground_top"], pal["ground_mid"], (60, 40, 25))
    for p in world.pipes:
        p.draw(target)
    for c in world.coins:
        c.draw(target)
    for m in world.powerups:
        m.draw(target)
    for p in world.particles:
        p.draw(target)
    for g in world.genie_actors:
        g.draw(target)
    world.bird.draw(target, flipped=False)
    for t in world.float_texts:
        t.draw(target)
    world.weather.draw(target)
    # Draw the HUD (score pill, coins pill, buff bars) on top so we
    # can see whether the genie clashes with the score chrome.
    if not hasattr(render_world_at_cast, "_hud"):
        render_world_at_cast._hud = HUD()
    render_world_at_cast._hud.draw_play(target, world, best=0,
                                        paused=False)


def setup_world():
    random.seed(11)
    w = World()
    w.ready_t = 0
    w.biome_time = _biome.CYCLE_SECONDS * 0.10
    for _ in range(20):
        w.weather.update(1 / 60, w.biome_phase)
    return w


def render_with_position(label, gx, gy, scale):
    """Build a fresh world, trigger genie pickup, override the
    GenieCharacter's spawn (gx, gy) and display_scale, then advance
    to just after the cast moment so the 3 poofs are visible."""
    w = setup_world()
    w._activate_genie(PowerUp(w.bird.x, w.bird.y, kind="genie"))
    # Override position + size on the freshly-spawned genie. Position
    # was set by world._activate_genie; we move the genie before any
    # frames tick.
    if w.genie_actors:
        g = w.genie_actors[0]
        g.x = gx
        g.y = gy
        g._display_scale = scale
    # Tick to just after the cast moment (cast fires at t=1.10) so
    # the 3 poofs are visible mid-bloom. Pin the bird's y to its
    # normal hover height each tick so the headless render doesn't
    # show it drifting to the ground under gravity (the player
    # would be tap-flapping in a real session).
    BIRD_Y = H * 0.42
    for _ in range(int(60 * 1.25)):
        w.bird.y = BIRD_Y
        w.bird.vy = 0
        w.update(1 / 60.0)
    w.bird.y = BIRD_Y
    surf = pygame.Surface((W, H))
    render_world_at_cast(w, surf)
    # Add the label as a top-left chip so the sheet reads cleanly
    font = pygame.font.SysFont("Arial", 13, bold=True)
    txt = font.render(label, True, (255, 255, 255))
    bg = pygame.Surface((txt.get_width() + 12, txt.get_height() + 6),
                        pygame.SRCALPHA)
    bg.fill((0, 0, 0, 160))
    surf.blit(bg, (6, 6))
    surf.blit(txt, (12, 9))
    return surf


def main():
    frames = []
    for option in POSITION_OPTIONS:
        frames.append(render_with_position(*option))
    # Contact sheet: 3 columns × 2 rows
    cols, rows = 3, 2
    margin = 12
    sw = W // 2
    sh = H // 2
    sheet_w = sw * cols + margin * (cols + 1)
    sheet_h = sh * rows + margin * (rows + 1)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((20, 22, 30))
    for i, fr in enumerate(frames):
        col, row = i % cols, i // cols
        small = pygame.transform.smoothscale(fr, (sw, sh))
        sheet.blit(small,
                   (margin + col * (sw + margin),
                    margin + row * (sh + margin)))
    out = os.path.join(OUT_DIR, "positions_v1.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet_w}x{sheet_h})")
    # Also save each option full-size
    for opt, fr in zip(POSITION_OPTIONS, frames):
        idx = POSITION_OPTIONS.index(opt) + 1
        path = os.path.join(OUT_DIR, f"position_{idx}_v1.png")
        pygame.image.save(fr, path)


if __name__ == "__main__":
    main()
