"""Render an 8-frame contact sheet of the full lightning storm-jolt
sequence: pre-strike idle, 3 background bolts, real strike with
X-Ray Sparks skeleton flicker, scorch wisps aftermath. Saved to
docs/screenshots/lightning_sequence.png.

Run from repo root:
    SDL_VIDEODRIVER=dummy python -m tools.render_lightning_sequence
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import random
import pygame
pygame.init()
pygame.display.set_mode((360, 640))

random.seed(1)

from game.config import W, H, GROUND_Y
from game.world import World
from game.weather import rain_intensity as _rain_intensity
from game import biome as _biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground
from game.hud import HUD


OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                       "docs", "screenshots")
os.makedirs(OUT_DIR, exist_ok=True)


def render_world(world, target):
    """Paint sky → mountains → ground → pipes → coins → particles →
    bird → genie_actors → float-texts → weather → lightning bolt.
    Mirrors `App._render` minus the HUD chrome so the lightning
    visuals show cleanly."""
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
    world.bird.draw(target, flipped=False)
    for g in world.genie_actors:
        g.draw(target)
    for t in world.float_texts:
        t.draw(target)
    world.weather.draw(target)
    # Lightning bolt: scenes._draw_lightning_bolt paints between
    # weather and bird normally; here we keep it last so the bolt is
    # clearly on top of the rain streaks + flash.
    from game.scenes import _draw_lightning_bolt
    _draw_lightning_bolt(target, world.lightning_strike)


def setup_world():
    w = World()
    w.ready_t = 0
    w.weather.phase = w.biome_phase
    # Pin the bird's y so headless render doesn't have it dropping to
    # the ground under gravity (player would be tap-flapping live).
    BIRD_Y = H * 0.42
    w.bird.y = BIRD_Y
    w.bird.vy = 0
    w.coin_count = 100
    # Push the weather sim forward a few frames so the rain streaks
    # have populated the canvas
    for _ in range(30):
        w.weather.update(1 / 60, w.biome_phase)
    return w, BIRD_Y


def advance(w, bird_y, seconds, n_frames_to_render=0, hold_lightning=False):
    """Tick the world forward by `seconds`. Optionally hold the
    lightning bolt's `life` at its initial value so it doesn't
    decay (used to capture the FRESH moment of a bolt for the
    contact sheet)."""
    n_steps = int(seconds * 60)
    for _ in range(n_steps):
        w.bird.y = bird_y
        w.bird.vy = 0
        w.update(1 / 60.0)
        if hold_lightning and w.lightning_strike is not None:
            w.lightning_strike["life"] = w.lightning_strike["life_max"]


def main():
    panels = []
    labels = []

    # 1) idle pre-strike — heavy rain, no bolt yet. Drop weather a
    #    little below trigger so no strike is in progress.
    w, by = setup_world()
    advance(w, by, 0.4)
    surf = pygame.Surface((W, H))
    render_world(w, surf)
    panels.append(surf)
    labels.append("1: pre-strike (heavy rain)")

    # 2-4) background bolts 1, 2, 3 — kick off the buildup, freeze on
    #      each fresh bolt
    w, by = setup_world()
    w._storm_jolt_lockout = 0
    w._start_storm_buildup()
    # Frame just after bg #1 fires (life still ≈ life_max)
    advance(w, by, 0.04, hold_lightning=True)
    surf = pygame.Surface((W, H))
    render_world(w, surf)
    panels.append(surf)
    labels.append("2: bg bolt 1 (left)")

    # Advance to bg #2
    advance(w, by, 0.60 - 0.04, hold_lightning=False)
    advance(w, by, 0.04, hold_lightning=True)
    surf = pygame.Surface((W, H))
    render_world(w, surf)
    panels.append(surf)
    labels.append("3: bg bolt 2 (right)")

    # Advance to bg #3
    advance(w, by, 0.60 - 0.04, hold_lightning=False)
    advance(w, by, 0.04, hold_lightning=True)
    surf = pygame.Surface((W, H))
    render_world(w, surf)
    panels.append(surf)
    labels.append("4: bg bolt 3 (left)")

    # 5) real strike — capture mid-flash with skeleton VISIBLE
    advance(w, by, 0.70 - 0.04, hold_lightning=False)
    advance(w, by, 0.04, hold_lightning=True)
    # At this point bird.skeleton_flash_t was just set to 0.50; the
    # strobe modulo evaluates (elapsed=0.04 → bucket 0 → skeleton)
    surf = pygame.Surface((W, H))
    render_world(w, surf)
    panels.append(surf)
    labels.append("5: STRIKE — skeleton X-ray")

    # 6) real strike — same strike, advance to a frame where the
    #    strobe shows the NORMAL sprite (odd bucket)
    advance(w, by, 0.12, hold_lightning=True)   # bucket 1
    surf = pygame.Surface((W, H))
    render_world(w, surf)
    panels.append(surf)
    labels.append("6: STRIKE — normal flicker")

    # 7) post-strike — skeleton flash ended, scorch wisps active
    advance(w, by, 0.45, hold_lightning=False)
    surf = pygame.Surface((W, H))
    render_world(w, surf)
    panels.append(surf)
    labels.append("7: scorch wisps")

    # 8) settle
    advance(w, by, 0.30, hold_lightning=False)
    surf = pygame.Surface((W, H))
    render_world(w, surf)
    panels.append(surf)
    labels.append("8: settle")

    # ── Contact sheet ───────────────────────────────────────────
    cols, rows = 4, 2
    margin = 10
    label_h = 22
    cell_h = H + label_h + 4
    sheet_w = W * cols + margin * (cols + 1)
    sheet_h = cell_h * rows + margin * (rows + 1)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((22, 24, 32))
    font = pygame.font.SysFont("Arial", 13, bold=True)
    for i, (pnl, lab) in enumerate(zip(panels, labels)):
        col = i % cols
        row = i // cols
        x = margin + col * (W + margin)
        y = margin + row * (cell_h + margin)
        pygame.draw.rect(sheet, (60, 65, 80),
                         (x - 2, y - 2, W + 4, H + 4), 2)
        sheet.blit(pnl, (x, y))
        text = font.render(lab, True, (240, 240, 245))
        sheet.blit(text, (x + (W - text.get_width()) // 2,
                          y + H + 4))
    out = os.path.join(OUT_DIR, "lightning_sequence.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
