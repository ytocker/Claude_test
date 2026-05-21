"""Render 5 variants of the SCORE display painted in the D5 halftone
comic style, each placed differently relative to the SKATEBOARD!
caption strip. The chosen D5 KAPOW chorus + the SKATEBOARD! caption +
starburst are all drawn for context. The native glass-pill score is
SUPPRESSED in these renders to show how the comic score takes its
place during the effect.

  E1 — Compact halftone burst upper-right (smallest)
  E2 — Big halftone burst centred at top, replaces the pill outright
  E3 — Medium burst centred BELOW the SKATEBOARD! caption strip
  E4 — Upper-right burst with "SCORE" label stacked above the number
  E5 — Side-by-side composite (small SCORE chip + bigger number chip)

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_skateboard_score_d5_variants.py
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
    render_caption_overlay,
    render_starburst_surface,
    render_kapow_halftone_filled_overlay,
    render_skateboard_score_e1,
    render_skateboard_score_e2,
    render_skateboard_score_e3,
    render_skateboard_score_e4,
    render_skateboard_score_e5,
)


_OUT = os.path.join(_REPO, "docs", "screenshots",
                    "skateboard_score_d5")
os.makedirs(_OUT, exist_ok=True)


SAMPLE_SCORE = 127


VARIANTS = [
    ("E1_compact_top_right", render_skateboard_score_e1,
     "E1: compact halftone burst upper-right"),
    ("E2_big_top_center",    render_skateboard_score_e2,
     "E2: BIG halftone burst centred at top (replaces the pill)"),
    ("E3_below_caption",     render_skateboard_score_e3,
     "E3: medium burst centred BELOW the SKATEBOARD! caption"),
    ("E4_score_label_stack", render_skateboard_score_e4,
     "E4: SCORE label stacked above the number"),
    ("E5_side_by_side",      render_skateboard_score_e5,
     "E5: small SCORE chip + bigger number chip side-by-side"),
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


def _ingame_persistent_png(score_fn):
    """PERSISTENT-phase gameplay frame — what the player sees for
    most of the skateboard duration: SKATEBOARD! caption strip +
    the variant's comic SCORE. The starburst (~2.3s) and KAPOW
    chorus (~2.5s) have faded by then, so the score sits cleanly.
    This is the layout you're picking among."""
    world = build_world()
    frame = render_play_scene(world)
    cx, cy = int(world.bird.x), int(world.bird.y)
    cap = render_caption_overlay(cx, cy, rng_seed=22)
    frame.blit(cap, (0, 0))
    score_overlay = score_fn(SAMPLE_SCORE)
    frame.blit(score_overlay, (0, 0))
    return frame


def _ingame_initial_png(score_fn):
    """INITIAL-burst gameplay frame — the busy first ~2.5 s with
    starburst + chorus + caption + score all on screen. Use this to
    sanity-check that the score is still LEGIBLE through the burst,
    not as the home position you're picking."""
    world = build_world()
    frame = render_play_scene(world)
    cx, cy = int(world.bird.x), int(world.bird.y)
    burst = render_starburst_surface(rng_seed=22)
    frame.blit(burst, burst.get_rect(center=(cx, cy)).topleft)
    cap = render_caption_overlay(cx, cy, rng_seed=22)
    frame.blit(cap, (0, 0))
    chorus = render_kapow_halftone_filled_overlay(cx, cy, rng_seed=22)
    frame.blit(chorus, (0, 0))
    score_overlay = score_fn(SAMPLE_SCORE)
    frame.blit(score_overlay, (0, 0))
    return frame


def main():
    saved = []
    for label, fn, caption in VARIANTS:
        overlay = fn(SAMPLE_SCORE)
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
    for idx, (label, caption, ingame) in enumerate(saved):
        x = 12 + idx * (cell_w + gap)
        small = pygame.transform.smoothscale(ingame, (cell_w, cell_h))
        sheet.blit(small, (x, 12))
        band = _label_band(cell_w, label, caption, height=band_h)
        sheet.blit(band, (x, 12 + cell_h))
    sheet_path = os.path.join(_OUT, "00_contact_sheet.png")
    pygame.image.save(sheet, sheet_path)
    print(f"saved {sheet_path}")

    base = ("https://raw.githubusercontent.com/ytocker/skybit/"
            "v5_powerups/docs/screenshots/skateboard_score_d5")
    print()
    print(f"{base}/00_contact_sheet.png")
    for label, caption, _ in saved:
        print(f"{base}/{label}.png  -- {caption}")
        print(f"{base}/{label}_persistent.png   -- long-term look")
        print(f"{base}/{label}_initial.png      -- initial burst look")


if __name__ == "__main__":
    main()
