"""Render Pip at each biome phase so the day→night→sunrise lighting
change is visible side-by-side.

Produces 8 PNGs under docs/screenshots/biome_lighting/:
  00_contact_sheet.png — all 7 phases in a row
  01_day.png ... 07_sunrise.png

Run from repo root:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m tools.render_biome_lighting
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((360, 640))

from game.config import W, H, GROUND_Y
from game import biome as _biome
from game.draw import (
    get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground,
)
from game.world import World

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                       "docs", "screenshots", "biome_lighting")
os.makedirs(OUT_DIR, exist_ok=True)


PHASES = (
    ("01_day.png",         0.00, "DAY"),
    ("02_golden_hour.png", 0.23, "GOLDEN HOUR"),
    ("03_sunset.png",      0.36, "SUNSET"),
    ("04_dusk.png",        0.51, "DUSK"),
    ("05_night.png",       0.64, "NIGHT"),
    ("06_predawn.png",     0.79, "PREDAWN"),
    ("07_sunrise.png",     0.91, "SUNRISE"),
)


def render_phase(world, target, phase):
    """Sky / clouds / mountains / ground / Pip / pipes at the given phase."""
    world.biome_time = _biome.CYCLE_SECONDS * phase
    pal = _biome.palette_for_phase(phase)
    buckets = _biome.PHASE_BUCKETS
    bucket_f = (phase % 1.0) * buckets
    a = int(bucket_f) % buckets
    sky = get_sky_surface_biome(W, H, GROUND_Y, pal, a)
    target.blit(sky, (0, 0))
    for bx, by, sc, variant in (
            (40, 80, 0.9, 0), (220, 110, 1.0, 2), (110, 180, 0.8, 3)):
        draw_cloud(target, bx, by, sc, variant=variant)
    draw_mountains(target, 0, GROUND_Y, W,
                   pal["mtn_far"], pal["mtn_near"])
    draw_ground(target, GROUND_Y, W, H, 0,
                pal["ground_top"], pal["ground_mid"], (60, 40, 25))
    # Render an example pipe pair so the user can verify pillar tint vs Pip's tint.
    for p in world.pipes:
        p.draw(target, palette=pal)
    light = _biome.light_level_for_phase(phase)
    world.bird.draw(target, light_level=light)


def save(surf, name, label):
    out = surf.copy()
    font = pygame.font.SysFont("Arial", 13, bold=True)
    light = _biome.light_level_for_phase(float(label_to_phase[label]))
    txt = f"{label} (light={light:.2f})"
    img = font.render(txt, True, (255, 255, 255))
    bg = pygame.Surface((img.get_width() + 12, img.get_height() + 6),
                        pygame.SRCALPHA)
    bg.fill((0, 0, 0, 180))
    out.blit(bg, (6, 6))
    out.blit(img, (12, 9))
    path = os.path.join(OUT_DIR, name)
    pygame.image.save(out, path)
    print(f"  saved {path}")
    return out


def make_contact_sheet(frames, name):
    margin = 6
    sw = W // 2 + 30
    sh = H // 2 + 20
    total_w = sw * len(frames) + margin * (len(frames) + 1)
    total_h = sh + margin * 2
    sheet = pygame.Surface((total_w, total_h))
    sheet.fill((20, 20, 28))
    for i, fr in enumerate(frames):
        small = pygame.transform.smoothscale(fr, (sw, sh))
        sheet.blit(small, (margin + i * (sw + margin), margin))
    path = os.path.join(OUT_DIR, name)
    pygame.image.save(sheet, path)
    print(f"  saved {path}")


label_to_phase = {label: phase for (_, phase, label) in PHASES}


def main():
    surf = pygame.Surface((W, H))
    w = World()
    w.ready_t = 0
    # Seed one pipe in view so pillar lighting is visible alongside Pip.
    w._spawn_pipe(W // 2 - 30)
    frames = []
    for name, phase, label in PHASES:
        render_phase(w, surf, phase)
        frames.append(save(surf, name, label))
    make_contact_sheet(frames, "00_contact_sheet.png")
    print("\nDone. Output in:", OUT_DIR)


if __name__ == "__main__":
    main()
