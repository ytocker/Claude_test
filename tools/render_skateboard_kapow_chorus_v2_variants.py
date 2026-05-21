"""Render 5 sub-variants of the C1 KAPOW chorus, exploring different
ways to vary the same idea (word vocabulary, size hierarchy,
arrangement, sticker styling, halftone fill).

  D1 — Skate slang   (RAD! / GNARLY! / SICK! / SHRED!)
  D2 — Hierarchy     (one big KABOOM! + 3 smaller satellites)
  D3 — Radial ring   (6 bursts evenly placed in a circle around Pip)
  D4 — Sticker style (each burst as a punk skate-deck sticker)
  D5 — Halftone fill (Lichtenstein dot pattern inside each burst)

Same render pattern as render_skateboard_comic_addon_variants.py —
each variant saves zoom + ingame + a contact sheet under
docs/screenshots/skateboard_kapow_chorus_v2/.
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
    render_kapow_skate_slang_overlay,
    render_kapow_hierarchy_overlay,
    render_kapow_radial_ring_overlay,
    render_kapow_sticker_overlay,
    render_kapow_halftone_filled_overlay,
)


_OUT = os.path.join(_REPO, "docs", "screenshots",
                    "skateboard_kapow_chorus_v2")
os.makedirs(_OUT, exist_ok=True)


VARIANTS = [
    ("D1_skate_slang",    render_kapow_skate_slang_overlay,
     "D1: RAD! / GNARLY! / SICK! / SHRED! skate slang vocabulary"),
    ("D2_hierarchy",      render_kapow_hierarchy_overlay,
     "D2: one BIG KABOOM! + 3 smaller satellite bursts"),
    ("D3_radial_ring",    render_kapow_radial_ring_overlay,
     "D3: 6 bursts in a circle around Pip, radially aligned"),
    ("D4_sticker_style",  render_kapow_sticker_overlay,
     "D4: punk skate-deck stickers with white border + drop shadow"),
    ("D5_halftone_fill",  render_kapow_halftone_filled_overlay,
     "D5: each burst FILLED with Lichtenstein halftone dot pattern"),
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


def _ingame_png(overlay_fn):
    world = build_world()
    frame = render_play_scene(world)
    cx, cy = int(world.bird.x), int(world.bird.y)
    cap = render_caption_overlay(cx, cy, rng_seed=22)
    burst = render_starburst_surface(rng_seed=22)
    frame.blit(burst, burst.get_rect(center=(cx, cy)).topleft)
    frame.blit(cap, (0, 0))
    addon = overlay_fn(cx, cy, rng_seed=22)
    frame.blit(addon, (0, 0))
    return frame


def main():
    saved = []
    for label, fn, caption in VARIANTS:
        world = build_world()
        cx, cy = int(world.bird.x), int(world.bird.y)
        overlay = fn(cx, cy, rng_seed=22)
        zoom = _overlay_zoom_png(overlay)
        ingame = _ingame_png(fn)
        zoom_path = os.path.join(_OUT, f"{label}.png")
        ingame_path = os.path.join(_OUT, f"{label}_ingame.png")
        pygame.image.save(zoom, zoom_path)
        pygame.image.save(ingame, ingame_path)
        saved.append((label, caption, ingame))
        print(f"saved {zoom_path}")
        print(f"saved {ingame_path}")

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
            "v5_powerups/docs/screenshots/skateboard_kapow_chorus_v2")
    print()
    print(f"{base}/00_contact_sheet.png")
    for label, caption, _ in saved:
        print(f"{base}/{label}.png  -- {caption}")
        print(f"{base}/{label}_ingame.png")


if __name__ == "__main__":
    main()
