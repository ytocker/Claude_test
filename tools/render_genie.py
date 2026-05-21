"""Render Genie Lamp icon + 3-offer post-activation scene.

Produces 3 PNGs under docs/screenshots/genie/:
  00_contact_sheet.png — icon zoom + activation scene side-by-side
  01_icon_zoom.png     — the in-world genie pickup at 4x scale
  02_three_wishes.png  — Pip just picked up a genie; 3 offer pickups
                          drifting in ahead of him at staggered y.

Run from repo root:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m tools.render_genie
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

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                       "docs", "screenshots", "genie")
os.makedirs(OUT_DIR, exist_ok=True)


def render_world(world, target):
    phase = world.biome_phase
    pal = _biome.palette_for_phase(phase)
    buckets = _biome.PHASE_BUCKETS
    bucket_f = (phase % 1.0) * buckets
    a = int(bucket_f) % buckets
    sky = get_sky_surface_biome(W, H, GROUND_Y, pal, a)
    target.blit(sky, (0, 0))
    for bx, by, sc, variant in (
            (40, 80, 0.9, 0), (220, 110, 1.0, 2), (110, 180, 0.8, 3)):
        draw_cloud(target, bx, by, sc, variant=variant)
    draw_mountains(target, world.bg_scroll, GROUND_Y, W,
                   pal["mtn_far"], pal["mtn_near"])
    draw_ground(target, GROUND_Y, W, H, world.bg_scroll,
                pal["ground_top"], pal["ground_mid"], (60, 40, 25))
    for p in world.pipes:
        p.draw(target)
    for m in world.powerups:
        m.draw(target)
    for p in world.particles:
        p.draw(target)
    world.bird.draw(target, flipped=False)
    for t in world.float_texts:
        t.draw(target)


def save(surf, name, label=None):
    out = surf.copy()
    if label:
        font = pygame.font.SysFont("Arial", 14, bold=True)
        img = font.render(label, True, (255, 255, 255))
        bg = pygame.Surface((img.get_width() + 12, img.get_height() + 6),
                            pygame.SRCALPHA)
        bg.fill((0, 0, 0, 150))
        out.blit(bg, (6, 6))
        out.blit(img, (12, 9))
    path = os.path.join(OUT_DIR, name)
    pygame.image.save(out, path)
    print(f"  saved {path}")
    return out


def make_contact_sheet(frames, name):
    margin = 10
    sw = W // 2 + 20
    sh = H // 2 + 10
    total_w = sw * len(frames) + margin * (len(frames) + 1)
    total_h = sh + margin * 2
    sheet = pygame.Surface((total_w, total_h))
    sheet.fill((24, 22, 36))
    for i, fr in enumerate(frames):
        small = pygame.transform.smoothscale(fr, (sw, sh))
        sheet.blit(small, (margin + i * (sw + margin), margin))
    path = os.path.join(OUT_DIR, name)
    pygame.image.save(sheet, path)
    print(f"  saved {path}")


def main():
    surf = pygame.Surface((W, H))
    frames = []

    # Frame 1: zoom on the genie icon alone (centred, big)
    random.seed(7)
    w = World()
    w.ready_t = 0
    icon = PowerUp(W // 2, H // 2 - 20, kind="genie")
    for _ in range(8):
        icon.update(1 / 60)
    render_world(w, surf)
    surf.blit(surf, (0, 0))  # noop
    icon.draw(surf)
    frames.append(save(surf, "01_icon_zoom.png", "1: genie pickup (in-world icon)"))

    # Frame 2: Pip just picked up a genie; 3 offers spawned ahead.
    random.seed(11)
    w = World()
    w.ready_t = 0
    w.score = 600  # unlock all variants
    surf2 = pygame.Surface((W, H))
    # Trigger genie activation; this populates self.powerups with 3 offers.
    w._activate_genie(PowerUp(w.bird.x, w.bird.y, kind="genie"))
    # Tick the offers so their pulse animations are off baseline.
    for p in w.powerups:
        for _ in range(8):
            p.update(1 / 60)
    # Tick float texts a moment so "GENIE!" is mid-flight.
    for t in w.float_texts:
        t.update(0.25)
    render_world(w, surf2)
    frames.append(save(surf2, "02_three_wishes.png",
                       "2: GENIE! → 3 unique offers drift in"))

    # Contact sheet
    make_contact_sheet(frames, "00_contact_sheet.png")
    print("\nDone. Output in:", OUT_DIR)


if __name__ == "__main__":
    main()
