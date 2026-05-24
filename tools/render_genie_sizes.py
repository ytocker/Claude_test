"""Render the genie at 5 candidate SIZES, each positioned BELOW the
score UI (the score backdrop spans y=64..120), with the appear-poof
burst blooming around it. Lets us pick how big the genie should be.

Outputs (docs/screenshots/genie_size/):
    size_1.png .. size_5.png   — each option full-size on a real frame
    sizes_compare.png          — 5-up contact sheet of all options

Run from repo root:
    SDL_VIDEODRIVER=dummy python -m tools.render_genie_sizes
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
                       "docs", "screenshots", "genie_size")
os.makedirs(OUT_DIR, exist_ok=True)

# Genie native sprite is 320×460. The score backdrop spans y=64..120, so
# each size is positioned with its TOP edge ~8 px below the pill (y≈128)
# — the genie centre is therefore TOP + (460*scale)/2, keeping the head
# clear of the score chrome no matter how big it gets.
NATIVE_H = 460
TOP_Y    = 128
GX       = 180          # screen-centre x, clear of HUD chrome

# 5 increasingly large options. Current live size is 0.34 (≈109 px wide);
# all five here are bigger so the genie reads as a hero character.
#   0.42 → 134×193   0.48 → 154×221   0.54 → 173×248
#   0.60 → 192×276   0.66 → 211×304
SIZE_OPTIONS = [
    ("1  scale 0.42  (134 px wide)", 0.42),
    ("2  scale 0.48  (154 px wide)", 0.48),
    ("3  scale 0.54  (173 px wide)", 0.54),
    ("4  scale 0.60  (192 px wide)", 0.60),
    ("5  scale 0.66  (211 px wide)", 0.66),
]


def render_world(world, target):
    """Paint background + entities so the frame reads as real gameplay.
    Mirrors the render order in game/scenes.py, HUD on top."""
    phase = world.biome_phase
    pal = _biome.palette_for_phase(phase)
    buckets = _biome.PHASE_BUCKETS
    a = int((phase % 1.0) * buckets) % buckets
    target.blit(get_sky_surface_biome(W, H, GROUND_Y, pal, a), (0, 0))
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
    if not hasattr(render_world, "_hud"):
        render_world._hud = HUD()
    render_world._hud.draw_play(target, world, best=0, paused=False)


def setup_world():
    random.seed(7)
    w = World()
    w.ready_t = 0
    w.biome_time = _biome.CYCLE_SECONDS * 0.10   # bright morning sky
    w.score = 1234                               # show a real score pill
    for _ in range(20):
        w.weather.update(1 / 60, w.biome_phase)
    return w


def render_size(label, scale):
    """Fresh world → trigger genie → override its size + below-score
    position → tick to the fully-materialised HOLD state (before the
    cast beat, so no offers clutter the frame) → re-poof so the appear
    burst blooms around the full-size genie → render."""
    w = setup_world()
    w._activate_genie(PowerUp(w.bird.x, w.bird.y, kind="genie"))
    gy = TOP_Y + (NATIVE_H * scale) / 2.0
    if w.genie_actors:
        g = w.genie_actors[0]
        g.x = GX
        g.y = gy
        g._display_scale = scale
    BIRD_Y = H * 0.42
    # Rise completes at 0.85; cast fires at 1.10. Tick to ~0.95 so the
    # genie is full-size + steady but hasn't conjured the 3 offers yet.
    for _ in range(57):
        w.bird.y = BIRD_Y; w.bird.vy = 0
        w.update(1 / 60.0)
    # Re-fire the appear poof so the burst is mid-bloom in the shot.
    if w.genie_actors:
        w.genie_actors[0]._spawn_appear_poof()
    for _ in range(6):
        w.bird.y = BIRD_Y; w.bird.vy = 0
        w.update(1 / 60.0)
    w.bird.y = BIRD_Y

    surf = pygame.Surface((W, H))
    render_world(w, surf)
    # A thin guide line at the score-pill bottom (y=120) so reviewers can
    # see each option clears the chrome, plus a label chip.
    pygame.draw.line(surf, (255, 255, 255, 0), (0, 120), (W, 120), 1)
    font = pygame.font.SysFont("Arial", 13, bold=True)
    txt = font.render(label, True, (255, 255, 255))
    bg = pygame.Surface((txt.get_width() + 12, txt.get_height() + 6),
                        pygame.SRCALPHA)
    bg.fill((0, 0, 0, 165))
    surf.blit(bg, (6, H - 30))
    surf.blit(txt, (12, H - 27))
    return surf


def main():
    frames = [render_size(lbl, sc) for lbl, sc in SIZE_OPTIONS]
    for i, fr in enumerate(frames, 1):
        pygame.image.save(fr, os.path.join(OUT_DIR, f"size_{i}.png"))

    # Comparison sheet: 5 across in one row.
    cols = 5
    margin = 10
    sw, sh = W // 2, H // 2
    sheet_w = sw * cols + margin * (cols + 1)
    sheet_h = sh + margin * 2
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((20, 22, 30))
    for i, fr in enumerate(frames):
        small = pygame.transform.smoothscale(fr, (sw, sh))
        sheet.blit(small, (margin + i * (sw + margin), margin))
    out = os.path.join(OUT_DIR, "sizes_compare.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet_w}x{sheet_h})")
    print("saved size_1.png .. size_5.png in", OUT_DIR)


if __name__ == "__main__":
    main()
