"""Render 5 variants of the ONE-PIECE banner with SKATE + gap + BOARD!,
score nested in the gap. Same live red-plate design, but it stays
ONE CONTINUOUS plate — not two separate halves.

  J1 — Score fits inside the plate's gap (red wraps around it)
  J2 — Score is BIGGER than plate height, spikes punch above/below
  J3 — Compact: smaller everything (ribbon-like)
  J4 — Wide + big: taller plate so a big score fits inside
  J5 — Tilted opposite (-10°) — deck-sticker slapped on at an angle
"""

import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

pygame.init()
pygame.display.set_mode((1, 1))

from tools.render_helmet_side_view_variants import (
    build_world, render_play_scene, _label_band,
)
from game.skateboard_fx import (
    render_starburst_surface,
    render_kapow_halftone_filled_overlay,
    render_caption_j1_score_fits,
    render_caption_j2_score_punches_through,
    render_caption_j3_compact,
    render_caption_j4_wide_big_score,
    render_caption_j5_tilted,
)


_OUT = os.path.join(_REPO, "docs", "screenshots",
                    "skateboard_caption_j")
os.makedirs(_OUT, exist_ok=True)


SAMPLE_SCORE = 127


VARIANTS = [
    ("J1_score_fits",          render_caption_j1_score_fits,
     "J1: score fits IN the gap, red plate wraps around it"),
    ("J2_score_punches",       render_caption_j2_score_punches_through,
     "J2: score spikes punch ABOVE and BELOW the banner"),
    ("J3_compact",             render_caption_j3_compact,
     "J3: compact — small everything, ribbon-like"),
    ("J4_wide_big",            render_caption_j4_wide_big_score,
     "J4: taller plate + big score that still fits inside"),
    ("J5_tilted",              render_caption_j5_tilted,
     "J5: tilted -10° — deck sticker slapped on at an angle"),
]


def _overlay_zoom_png(overlay):
    mask = pygame.mask.from_surface(overlay, threshold=10)
    bbox_rects = mask.get_bounding_rects()
    if bbox_rects:
        bbox = bbox_rects[0]
        for r in bbox_rects[1:]:
            bbox = bbox.union(r)
        bbox = bbox.inflate(20, 20).clip(overlay.get_rect())
    else:
        bbox = overlay.get_rect()
    sub = overlay.subsurface(bbox).copy()
    bg = pygame.Surface(bbox.size)
    bg.fill((22, 26, 42))
    bg.blit(sub, (0, 0))
    zoom = 4
    big = pygame.transform.scale(bg, (bbox.width * zoom,
                                       bbox.height * zoom))
    pygame.draw.rect(big, (255, 215, 0), big.get_rect(), 3)
    return big


def _ingame_persistent_png(caption_fn):
    world = build_world()
    frame = render_play_scene(world)
    cx, cy = int(world.bird.x), int(world.bird.y)
    cap = caption_fn(cx, cy, SAMPLE_SCORE, rng_seed=22)
    frame.blit(cap, (0, 0))
    return frame


def _ingame_initial_png(caption_fn):
    world = build_world()
    frame = render_play_scene(world)
    cx, cy = int(world.bird.x), int(world.bird.y)
    burst = render_starburst_surface(rng_seed=22)
    frame.blit(burst, burst.get_rect(center=(cx, cy)).topleft)
    chorus = render_kapow_halftone_filled_overlay(cx, cy, rng_seed=22)
    frame.blit(chorus, (0, 0))
    cap = caption_fn(cx, cy, SAMPLE_SCORE, rng_seed=22)
    frame.blit(cap, (0, 0))
    return frame


def main():
    saved = []
    for label, fn, caption in VARIANTS:
        overlay = fn(0, 0, SAMPLE_SCORE, rng_seed=22)
        zoom = _overlay_zoom_png(overlay)
        persistent = _ingame_persistent_png(fn)
        initial = _ingame_initial_png(fn)
        zoom_path = os.path.join(_OUT, f"{label}.png")
        persistent_path = os.path.join(_OUT, f"{label}_persistent.png")
        initial_path = os.path.join(_OUT, f"{label}_initial.png")
        pygame.image.save(zoom, zoom_path)
        pygame.image.save(persistent, persistent_path)
        pygame.image.save(initial, initial_path)
        saved.append((label, caption, persistent))
        print(f"saved {zoom_path}")
        print(f"saved {persistent_path}")
        print(f"saved {initial_path}")

    cell_w = saved[0][2].get_width() // 2
    cell_h = saved[0][2].get_height() // 2
    band_h = 56
    gap = 12
    sheet_w = len(saved) * cell_w + (len(saved) - 1) * gap + 24
    sheet_h = cell_h + band_h + 24
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((10, 12, 24))
    for idx, (label, caption, persistent) in enumerate(saved):
        x = 12 + idx * (cell_w + gap)
        small = pygame.transform.smoothscale(persistent, (cell_w, cell_h))
        sheet.blit(small, (x, 12))
        band = _label_band(cell_w, label, caption, height=band_h)
        sheet.blit(band, (x, 12 + cell_h))
    sheet_path = os.path.join(_OUT, "00_contact_sheet.png")
    pygame.image.save(sheet, sheet_path)
    print(f"saved {sheet_path}")

    base = ("https://raw.githubusercontent.com/ytocker/skybit/"
            "v5_powerups/docs/screenshots/skateboard_caption_j")
    print()
    print(f"{base}/00_contact_sheet.png")
    for label, caption, _ in saved:
        print(f"{base}/{label}.png  -- {caption}")
        print(f"{base}/{label}_persistent.png   -- long-term look")
        print(f"{base}/{label}_initial.png      -- initial-burst look")


if __name__ == "__main__":
    main()
