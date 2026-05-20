"""Render 5 comic-book-inspired add-on overlays for the SKATEBOARD
pickup celebration. Each variant stacks on TOP of the existing
SKATEBOARD! caption + POW! + corner-slashes + 14-spike starburst —
the goal is to extend the comic theme, not replace it.

  C1 — KAPOW chorus (4 onomatopoeia bursts in the corners)
  C2 — Halftone aura (Lichtenstein dot field radiating from Pip)
  C3 — Speech bubble ("SHRED!" from Pip's helmet)
  C4 — Lightning bolts + ZZAP! badge under the deck
  C5 — Comic panel frame with "NEW BOARD!" narration caption

Each variant saves:
  * <label>.png         — overlay alone on transparent + yellow
                          review border, 6× upscale for review
  * <label>_ingame.png  — full gameplay composite with Pip in
                          skateboard kit + existing pickup FX +
                          the variant overlay

Plus a horizontal contact sheet `00_contact_sheet.png`.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_skateboard_comic_addon_variants.py
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
    render_kapow_chorus_overlay,
    render_halftone_aura_overlay,
    render_speech_bubble_overlay,
    render_lightning_bolts_overlay,
    render_comic_panel_overlay,
)


_OUT = os.path.join(_REPO, "docs", "screenshots",
                    "skateboard_comic_addons")
os.makedirs(_OUT, exist_ok=True)


VARIANTS = [
    ("C1_kapow_chorus", render_kapow_chorus_overlay,
     "C1: KAPOW! / BAM! / SMASH! / WHAM! onomatopoeia chorus"),
    ("C2_halftone_aura", render_halftone_aura_overlay,
     "C2: Lichtenstein halftone-dot aura around Pip"),
    ("C3_speech_bubble", render_speech_bubble_overlay,
     "C3: SHRED! speech bubble from Pip's helmet"),
    ("C4_lightning_bolts", render_lightning_bolts_overlay,
     "C4: yellow lightning bolts + ZZAP! badge under the deck"),
    ("C5_comic_panel", render_comic_panel_overlay,
     "C5: comic-panel frame with NEW BOARD! caption box"),
]


def _overlay_zoom_png(overlay):
    """Overlay alone — 6× upscale of the part of the overlay around
    Pip so the add-on details read cleanly in review. Falls back to
    the full overlay if the contents land near a screen edge."""
    # Find the overlay's painted bbox (any non-transparent pixel).
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
    # Pre-composite onto dark navy so the colors read with their
    # outlines clearly.
    bg = pygame.Surface(bbox.size)
    bg.fill((22, 26, 42))
    bg.blit(sub, (0, 0))
    zoom = 4
    big = pygame.transform.scale(bg, (bbox.width * zoom,
                                       bbox.height * zoom))
    pygame.draw.rect(big, (255, 215, 0), big.get_rect(), 3)
    return big


def _ingame_png(overlay_fn):
    """Full gameplay frame with Pip mid-flight in skateboard kit, the
    existing pickup FX (caption + starburst), AND the variant overlay
    composited on top."""
    world = build_world()
    frame = render_play_scene(world)
    cx, cy = int(world.bird.x), int(world.bird.y)
    # Existing pickup FX — caption strip + 14-spike starburst.
    cap = render_caption_overlay(cx, cy, rng_seed=22)
    burst = render_starburst_surface(rng_seed=22)
    frame.blit(burst,
               burst.get_rect(center=(cx, cy)).topleft)
    frame.blit(cap, (0, 0))
    # Variant add-on overlay.
    addon = overlay_fn(cx, cy, rng_seed=22)
    frame.blit(addon, (0, 0))
    return frame


def main():
    saved = []
    for label, fn, caption in VARIANTS:
        # Overlay-only zoom (overlay rendered against neutral world cx/cy).
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

    # Contact sheet — uses the in-game composite for each variant so the
    # add-on can be evaluated in real context (over Pip + caption + burst).
    cell_w = saved[0][2].get_width() // 2  # half-size the gameplay frames
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
            "v5_powerups/docs/screenshots/skateboard_comic_addons")
    print()
    print(f"{base}/00_contact_sheet.png")
    for label, caption, _ in saved:
        print(f"{base}/{label}.png  -- {caption}")
        print(f"{base}/{label}_ingame.png")


if __name__ == "__main__":
    main()
