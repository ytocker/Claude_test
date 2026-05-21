"""Render 5 SKATEBOARD! caption "watermark behind the score"
variants. The caption text sits at the score's exact position
(y=92) but in a see-through style so the score on top stays
readable, while still announcing the powerup pickup.

  G1 — Hollow outline-only letters (just ink rings, transparent
       interior)
  G2 — Halftone-dot letters (Lichtenstein dots fill the glyph,
       matches the D5 chorus vocabulary)
  G3 — Faded ghost / watermark (full gradient text at ~110/255
       alpha)
  G4 — Striped letters (horizontal red+cream barber-pole shading)
  G5 — HUGE background slab (78pt SKATEBOARD! spanning the canvas,
       low alpha — the word is the backdrop, score is the centre)

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_skateboard_caption_g_variants.py
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
    render_caption_g1_hollow,
    render_caption_g2_halftone_text,
    render_caption_g3_ghost,
    render_caption_g4_striped,
    render_caption_g5_huge_bg,
)


_OUT = os.path.join(_REPO, "docs", "screenshots",
                    "skateboard_caption_g")
os.makedirs(_OUT, exist_ok=True)


SAMPLE_SCORE = 127


VARIANTS = [
    ("G1_hollow_outline",  render_caption_g1_hollow,
     "G1: hollow outline-only letters — sky shows through interiors"),
    ("G2_halftone_text",   render_caption_g2_halftone_text,
     "G2: Lichtenstein halftone dots fill each glyph"),
    ("G3_ghost_fade",      render_caption_g3_ghost,
     "G3: full-fill SKATEBOARD! at ~110/255 alpha (watermark)"),
    ("G4_striped",         render_caption_g4_striped,
     "G4: horizontal red+cream barber-pole stripes fill each glyph"),
    ("G5_huge_bg",         render_caption_g5_huge_bg,
     "G5: huge 78pt SKATEBOARD! spanning the canvas, low alpha"),
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
    """PERSISTENT-phase view: just the SKATEBOARD!-behind-score
    composite over the gameplay frame. The 14-spike starburst and
    KAPOW chorus have already faded, so what you see here is what
    the player looks at for most of the 8 s skateboard duration."""
    world = build_world()
    frame = render_play_scene(world)
    cx, cy = int(world.bird.x), int(world.bird.y)
    cap = caption_fn(cx, cy, SAMPLE_SCORE, rng_seed=22)
    frame.blit(cap, (0, 0))
    return frame


def _ingame_initial_png(caption_fn):
    """INITIAL-burst view: starburst + D5 chorus + the caption-with-
    score composite, so you can sanity-check legibility through the
    full pickup celebration."""
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
            "v5_powerups/docs/screenshots/skateboard_caption_g")
    print()
    print(f"{base}/00_contact_sheet.png")
    for label, caption, _ in saved:
        print(f"{base}/{label}.png  -- {caption}")
        print(f"{base}/{label}_persistent.png   -- long-term look")
        print(f"{base}/{label}_initial.png      -- initial-burst look")


if __name__ == "__main__":
    main()
