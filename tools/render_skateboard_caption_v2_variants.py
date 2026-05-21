"""Render 5 SKATEBOARD! caption layouts that don't get covered by
the score. Each variant either parks the caption away from the
score band (F1/F3/F4) or combines caption + score into one composite
(F2/F5).

  F1 — Caption shrunk into the TOP-LEFT corner, POW! mirrors to
       top-right; entire top-center band stays clear for the score
  F2 — Combined wide banner: "SKATEBOARD!" + score number in one
       red plate across the top (no separate score overlay needed)
  F3 — Caption moved DOWN below the score's y=92 band (centred at
       y=150)
  F4 — Caption rotated 90° as a vertical ribbon down the LEFT edge
  F5 — Caption SPLIT in two halves ("SKATE" left, "BOARD!" right)
       with the D5 score burst wedged between them

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_skateboard_caption_v2_variants.py
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
    render_skateboard_score_e6,
    render_caption_v2_topleft,
    render_caption_v2_combined_banner,
    render_caption_v2_below_score,
    render_caption_v2_vertical_left,
    render_caption_v2_split_around,
)


_OUT = os.path.join(_REPO, "docs", "screenshots",
                    "skateboard_caption_v2")
os.makedirs(_OUT, exist_ok=True)


SAMPLE_SCORE = 127


# (label, caption_fn, combined, caption_text)
# combined=True means the caption fn already paints the score; no
# separate score overlay should be drawn for that variant.
VARIANTS = [
    ("F1_caption_topleft",      render_caption_v2_topleft,
     False, "F1: smaller SKATEBOARD! plate parked in the top-left"),
    ("F2_combined_banner",      render_caption_v2_combined_banner,
     True,  "F2: combined banner — SKATEBOARD! + score in one plate"),
    ("F3_caption_below_score",  render_caption_v2_below_score,
     False, "F3: caption moved DOWN to y=150 (below the score)"),
    ("F4_caption_vertical_left", render_caption_v2_vertical_left,
     False, "F4: caption rotated 90° as a vertical LEFT-edge ribbon"),
    ("F5_split_around_score",   render_caption_v2_split_around,
     True,  "F5: SKATE/BOARD! split around the centre score burst"),
]


def _caption_overlay_for(fn, combined):
    if combined:
        return fn(0, 0, SAMPLE_SCORE, rng_seed=22)
    return fn(0, 0, rng_seed=22)


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


def _ingame_persistent_png(caption_fn, combined):
    """PERSISTENT-phase view: caption variant + (if separate) the D5
    score E6 at its native y=92. Most of the skateboard effect
    looks like this — starburst + chorus have already faded."""
    world = build_world()
    frame = render_play_scene(world)
    cx, cy = int(world.bird.x), int(world.bird.y)
    if combined:
        cap = caption_fn(cx, cy, SAMPLE_SCORE, rng_seed=22)
        frame.blit(cap, (0, 0))
    else:
        score = render_skateboard_score_e6(SAMPLE_SCORE)
        frame.blit(score, (0, 0))
        cap = caption_fn(cx, cy, rng_seed=22)
        frame.blit(cap, (0, 0))
    return frame


def _ingame_initial_png(caption_fn, combined):
    """INITIAL-burst view with everything piled on so you can sanity-
    check the caption stays readable through the D5 chorus +
    starburst."""
    world = build_world()
    frame = render_play_scene(world)
    cx, cy = int(world.bird.x), int(world.bird.y)
    burst = render_starburst_surface(rng_seed=22)
    frame.blit(burst, burst.get_rect(center=(cx, cy)).topleft)
    chorus = render_kapow_halftone_filled_overlay(cx, cy, rng_seed=22)
    frame.blit(chorus, (0, 0))
    if combined:
        cap = caption_fn(cx, cy, SAMPLE_SCORE, rng_seed=22)
        frame.blit(cap, (0, 0))
    else:
        score = render_skateboard_score_e6(SAMPLE_SCORE)
        frame.blit(score, (0, 0))
        cap = caption_fn(cx, cy, rng_seed=22)
        frame.blit(cap, (0, 0))
    return frame


def main():
    saved = []
    for label, fn, combined, caption in VARIANTS:
        overlay = _caption_overlay_for(fn, combined)
        zoom = _overlay_zoom_png(overlay)
        persistent = _ingame_persistent_png(fn, combined)
        initial = _ingame_initial_png(fn, combined)
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
            "v5_powerups/docs/screenshots/skateboard_caption_v2")
    print()
    print(f"{base}/00_contact_sheet.png")
    for label, caption, _ in saved:
        print(f"{base}/{label}.png  -- {caption}")
        print(f"{base}/{label}_persistent.png   -- long-term look")
        print(f"{base}/{label}_initial.png      -- initial-burst look")


if __name__ == "__main__":
    main()
