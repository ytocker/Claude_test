"""Render 5 variants of the "SKATE [score] BOARD!" layout — same
live banner design (red gradient plate + yellow-orange text + ink
outline), split into two halves with the D5 score burst nested
between them.

  I1 — Inward V: plates tilt TOWARD score (V apex up)
  I2 — Outward Λ: plates tilt AWAY from score (apex down)
  I3 — Tight + compact: smaller score, narrow gap
  I4 — Wide + big score: large score, wide gap
  I5 — Staggered: SKATE slightly lower, BOARD slightly higher
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
    render_caption_i1_inward_v,
    render_caption_i2_outward_lambda,
    render_caption_i3_tight_compact,
    render_caption_i4_wide_big_score,
    render_caption_i5_staggered,
)


_OUT = os.path.join(_REPO, "docs", "screenshots",
                    "skateboard_caption_i")
os.makedirs(_OUT, exist_ok=True)


SAMPLE_SCORE = 127


VARIANTS = [
    ("I1_inward_v",       render_caption_i1_inward_v,
     "I1: plates tilt INWARD toward score — V apex up"),
    ("I2_outward_lambda", render_caption_i2_outward_lambda,
     "I2: plates tilt OUTWARD away from score — apex down"),
    ("I3_tight_compact",  render_caption_i3_tight_compact,
     "I3: tight gap + smaller score — compact composition"),
    ("I4_wide_big_score", render_caption_i4_wide_big_score,
     "I4: wide gap + BIG score — score is the star"),
    ("I5_staggered",      render_caption_i5_staggered,
     "I5: SKATE lower / BOARD higher — diagonal bracket"),
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
            "v5_powerups/docs/screenshots/skateboard_caption_i")
    print()
    print(f"{base}/00_contact_sheet.png")
    for label, caption, _ in saved:
        print(f"{base}/{label}.png  -- {caption}")
        print(f"{base}/{label}_persistent.png   -- long-term look")
        print(f"{base}/{label}_initial.png      -- initial-burst look")


if __name__ == "__main__":
    main()
