"""Render 5 lift-amount variants of the SKATEBOARD effect graphics —
banner + score + timer bar + trick bubbles all shift up by N pixels
for the user to pick the best vertical position.

  L0 — original (no lift, baseline)
  L1 — lift 10 px
  L2 — lift 18 px
  L3 — lift 26 px
  L4 — lift 34 px
  L5 — lift 42 px

(6 frames total — 5 lift options plus the baseline at the start.)

Each frame: Pip mid-flight in skateboard kit, the SKATEBOARD!
banner, the E3 halftone score, the timer bar, and a 4-bubble
trick stack — all shifted up uniformly by the lift amount.

Outputs under docs/screenshots/skateboard_lift_variants/ +
horizontal contact sheet.
"""

import os
import random as _random
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
from game.entities import PowerUp
from game.hud import HUD


_OUT = os.path.join(_REPO, "docs", "screenshots",
                    "skateboard_lift_variants")
os.makedirs(_OUT, exist_ok=True)


SAMPLE_SCORE = 127
TRICKS = ["KICKFLIP!", "BACKFLIP!", "POP SHUVIT!", "HEELFLIP!"]
LIFTS = [0, 10, 18, 26, 34, 42]


def render_lift(lift):
    _random.seed(7)
    world = build_world()
    world.ready_t = 0
    world.score = SAMPLE_SCORE
    world.skateboard_caption_t = 6.0
    world._skateboard_lift_y = lift
    for label in TRICKS:
        world._spawn_trick_bubble(label)
    frame = render_play_scene(world)
    # Caption first (matches scenes.py order); blitted at the world's
    # lift offset.
    cap = world.skateboard_caption_overlay.copy()
    frame.blit(cap, (0, -lift))
    HUD().draw_play(frame, world, best=0)
    return frame


def main():
    saved = []
    for lift in LIFTS:
        frame = render_lift(lift)
        label = f"L{lift:02d}_lift_{lift}px"
        path = os.path.join(_OUT, f"{label}.png")
        pygame.image.save(frame, path)
        caption = (f"Lift {lift} px"
                    + (" (baseline)" if lift == 0 else ""))
        saved.append((label, caption, frame))
        print(f"saved {path}")

    cell_w = saved[0][2].get_width() // 2
    cell_h = saved[0][2].get_height() // 2
    band_h = 56
    gap = 12
    cols = len(saved)
    sheet_w = cols * cell_w + (cols - 1) * gap + 24
    sheet_h = cell_h + band_h + 24
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((10, 12, 24))
    for idx, (label, caption, frame) in enumerate(saved):
        x = 12 + idx * (cell_w + gap)
        small = pygame.transform.smoothscale(frame, (cell_w, cell_h))
        sheet.blit(small, (x, 12))
        band = _label_band(cell_w, label, caption, height=band_h)
        sheet.blit(band, (x, 12 + cell_h))
    sheet_path = os.path.join(_OUT, "00_contact_sheet.png")
    pygame.image.save(sheet, sheet_path)
    print(f"saved {sheet_path}")

    base = ("https://raw.githubusercontent.com/ytocker/skybit/"
            "v5_powerups/docs/screenshots/skateboard_lift_variants")
    print()
    print(f"{base}/00_contact_sheet.png")
    for label, caption, _ in saved:
        print(f"{base}/{label}.png  -- {caption}")


if __name__ == "__main__":
    main()
