"""Render the 3 phases of the user's preferred SKATEBOARD layout:

  Phase A (t ~ 0.5 s) — PICKUP CELEBRATION
      Live render_caption_overlay (SKATEBOARD! plate + POW! + corner
      slashes), starburst around Pip, D5 KAPOW chorus.
      *Score is hidden* — caption owns the screen, no overlap.

  Phase B (t ~ 3.0 s) — TRANSITION
      Caption fading (alpha ~110), KAPOW chorus and starburst have
      already faded out. D5 score burst (E6 at y=92) just appearing
      at low alpha (~120). Brief crossfade so the player's eye
      transfers from caption to score.

  Phase C (t ~ 5.0 s) — PERSISTENT
      Caption fully gone. D5 score burst at y=92 at full alpha,
      visible for the rest of the 8 s skateboard duration.

Saves one ingame PNG per phase + a contact sheet labelled with the
phase + a short caption.
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
    render_skateboard_score_e6,
)


_OUT = os.path.join(_REPO, "docs", "screenshots",
                    "skateboard_phases")
os.makedirs(_OUT, exist_ok=True)


SAMPLE_SCORE = 127


def _blit_with_alpha(dst, src, alpha):
    s = src.copy()
    s.set_alpha(alpha)
    dst.blit(s, (0, 0))


def render_phase_a():
    """t ~ 0.5 s — caption + chorus + starburst at full alpha,
    NO score visible. Pickup celebration owns the screen."""
    world = build_world()
    frame = render_play_scene(world)
    cx, cy = int(world.bird.x), int(world.bird.y)
    burst = render_starburst_surface(rng_seed=22)
    frame.blit(burst, burst.get_rect(center=(cx, cy)).topleft)
    chorus = render_kapow_halftone_filled_overlay(cx, cy, rng_seed=22)
    frame.blit(chorus, (0, 0))
    cap = render_caption_overlay(cx, cy, rng_seed=22)
    frame.blit(cap, (0, 0))
    return frame


def render_phase_b():
    """t ~ 3.0 s — caption mid-fade (alpha ~110); starburst + chorus
    already gone; D5 score burst just appearing (alpha ~120). Brief
    crossfade so the player's eye transfers from caption to score."""
    world = build_world()
    frame = render_play_scene(world)
    cx, cy = int(world.bird.x), int(world.bird.y)
    cap = render_caption_overlay(cx, cy, rng_seed=22)
    _blit_with_alpha(frame, cap, 110)
    score = render_skateboard_score_e6(SAMPLE_SCORE)
    _blit_with_alpha(frame, score, 130)
    return frame


def render_phase_c():
    """t ~ 5.0 s — caption fully gone, D5 score burst at y=92 owns
    the slot. This is the long-term layout for the rest of the 8 s
    skateboard effect."""
    world = build_world()
    frame = render_play_scene(world)
    score = render_skateboard_score_e6(SAMPLE_SCORE)
    frame.blit(score, (0, 0))
    return frame


PHASES = [
    ("phase_A_caption_only",
     render_phase_a,
     "Phase A  (~0.5 s)  —  PICKUP CELEBRATION",
     "Caption + KAPOW chorus + starburst, score HIDDEN"),
    ("phase_B_transition",
     render_phase_b,
     "Phase B  (~3.0 s)  —  TRANSITION",
     "Caption mid-fade, D5 score burst appearing"),
    ("phase_C_score_persistent",
     render_phase_c,
     "Phase C  (~5.0 s)  —  PERSISTENT",
     "Caption gone, D5 score burst owns y=92 until effect ends"),
]


def main():
    saved = []
    for label, fn, line1, line2 in PHASES:
        frame = fn()
        path = os.path.join(_OUT, f"{label}.png")
        pygame.image.save(frame, path)
        saved.append((label, line1, line2, frame))
        print(f"saved {path}")

    cell_w = saved[0][3].get_width()
    cell_h = saved[0][3].get_height()
    band_h = 64
    gap = 16
    sheet_w = len(saved) * cell_w + (len(saved) - 1) * gap + 24
    sheet_h = cell_h + band_h + 24
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((10, 12, 24))
    for idx, (label, line1, line2, frame) in enumerate(saved):
        x = 12 + idx * (cell_w + gap)
        sheet.blit(frame, (x, 12))
        band = _label_band(cell_w, line1, line2, height=band_h)
        sheet.blit(band, (x, 12 + cell_h))
    sheet_path = os.path.join(_OUT, "00_phases_contact_sheet.png")
    pygame.image.save(sheet, sheet_path)
    print(f"saved {sheet_path}")

    base = ("https://raw.githubusercontent.com/ytocker/skybit/"
            "v5_powerups/docs/screenshots/skateboard_phases")
    print()
    print(f"{base}/00_phases_contact_sheet.png")
    for label, line1, line2, _ in saved:
        print(f"{base}/{label}.png  -- {line1}: {line2}")


if __name__ == "__main__":
    main()
