"""Render gameplay screenshots showing the SKATEBOARD trick-name
bubbles in various scenarios — single trick, paired tricks, full
combo stack, and a mid-fade snapshot. Each scenario is a full
in-game frame with Pip in the skateboard kit, the SKATEBOARD!
caption, the E3 halftone score, and the trick bubble(s) stacked at
the right-of-score anchor.

Outputs under docs/screenshots/skateboard_trick_bubbles/, plus a
horizontal contact sheet labelled with each scenario.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_trick_bubble_scenarios.py
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
                    "skateboard_trick_bubbles")
os.makedirs(_OUT, exist_ok=True)


SAMPLE_SCORE = 127


def _frame(tricks, *, caption_t=6.0, age_first=0.0, seed=7):
    """Build a full gameplay frame with Pip in skateboard kit, the
    caption + E3 score, and the given list of trick labels spawned
    in order (each appended on top of the prior — same behaviour as
    in the live game when tricks chain quickly). `caption_t` lets
    you sit anywhere on the caption-fade timeline. `age_first` (s)
    bumps the OLDEST bubble's lifetime down by that amount so we
    can show a stack mid-fade with later bubbles still bright."""
    _random.seed(seed)
    world = build_world()
    world.ready_t = 0
    world.score = SAMPLE_SCORE
    # build_world already activates skateboard; force caption_t so we
    # can dial the fade however we want.
    world.skateboard_caption_t = caption_t
    for label in tricks:
        world._spawn_trick_bubble(label)
    if age_first and world.trick_bubbles:
        world.trick_bubbles[0].life = max(
            0.05, world.trick_bubbles[0].life - age_first)
        if len(world.trick_bubbles) >= 2:
            world.trick_bubbles[1].life = max(
                0.2, world.trick_bubbles[1].life - age_first * 0.6)
    frame = render_play_scene(world)
    # Caption overlay first (matches scenes.py — caption is drawn
    # right after the play scene, BEFORE the HUD layer, so the
    # HUD-rendered score can overlay it).
    FADE = 0.8
    if caption_t > FADE:
        a = 255
    elif caption_t > 0:
        x = 1.0 - caption_t / FADE
        a = int(255 * (1.0 - x) ** 2)
    else:
        a = 0
    if a > 0 and world.skateboard_caption_overlay is not None:
        cap = world.skateboard_caption_overlay.copy()
        cap.set_alpha(a)
        lift_y = getattr(world, "_skateboard_lift_y", 0)
        frame.blit(cap, (0, -lift_y))
    HUD().draw_play(frame, world, best=0)
    # Pip is always in front of any SKATEBOARD-effect graphic — same
    # convention scenes.py applies during STATE_PLAY when
    # skateboard_active.
    if world.bird.skateboard_active and world.bird.alive:
        world.bird.draw(frame, 0, 0, flipped=False)
    return frame


SCENARIOS = [
    ("01_single_kickflip",
     ["KICKFLIP!"], 6.0, 0.0,
     "Single trick — KICKFLIP! (cyan)"),
    ("02_single_backflip",
     ["BACKFLIP!"], 6.0, 0.0,
     "Single trick — BACKFLIP! (green)"),
    ("03_single_popshuvit",
     ["POP SHUVIT!"], 6.0, 0.0,
     "Single trick — POP SHUVIT! (pink)"),
    ("04_single_grind",
     ["NOSE GRIND!"], 6.0, 0.0,
     "Single grind — NOSE GRIND! (gold)"),
    ("05_pair_kick_back",
     ["KICKFLIP!", "BACKFLIP!"], 6.0, 0.0,
     "Pair — KICKFLIP! then BACKFLIP! stacks on top"),
    ("06_pair_heel_pop",
     ["HEELFLIP!", "POP SHUVIT!"], 6.0, 0.0,
     "Pair — HEELFLIP! then POP SHUVIT! (purple + pink)"),
    ("07_combo_four",
     ["KICKFLIP!", "BACKFLIP!", "HEELFLIP!", "POP SHUVIT!"],
     6.0, 0.0,
     "Combo of 4 flips stacked"),
    ("08_full_stack_six",
     ["KICKFLIP!", "BACKFLIP!", "HEELFLIP!", "POP SHUVIT!",
      "NOSE GRIND!", "TAIL GRIND!"],
     6.0, 0.0,
     "All 6 trick bubbles stacked (max chaos)"),
    ("09_combo_midfade",
     ["KICKFLIP!", "BACKFLIP!", "POP SHUVIT!"],
     6.0, 1.1,
     "3-stack mid-fade — oldest bubble half-gone, newest crisp"),
    ("10_caption_endfade",
     ["KICKFLIP!", "BACKFLIP!"], 0.4, 0.0,
     "Caption fading out at end of effect; bubbles still up"),
]


def main():
    saved = []
    for label, tricks, cap_t, age, caption in SCENARIOS:
        frame = _frame(tricks, caption_t=cap_t, age_first=age)
        path = os.path.join(_OUT, f"{label}.png")
        pygame.image.save(frame, path)
        saved.append((label, caption, frame))
        print(f"saved {path}")

    # Contact sheet — 2 rows of 5 cells.
    cell_w = saved[0][2].get_width() // 2
    cell_h = saved[0][2].get_height() // 2
    band_h = 56
    gap = 12
    cols = 5
    rows = (len(saved) + cols - 1) // cols
    sheet_w = cols * cell_w + (cols - 1) * gap + 24
    sheet_h = rows * (cell_h + band_h) + (rows - 1) * gap + 24
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((10, 12, 24))
    for idx, (label, caption, frame) in enumerate(saved):
        col = idx % cols
        row = idx // cols
        x = 12 + col * (cell_w + gap)
        y = 12 + row * (cell_h + band_h + gap)
        small = pygame.transform.smoothscale(frame, (cell_w, cell_h))
        sheet.blit(small, (x, y))
        band = _label_band(cell_w, label, caption, height=band_h)
        sheet.blit(band, (x, y + cell_h))
    sheet_path = os.path.join(_OUT, "00_contact_sheet.png")
    pygame.image.save(sheet, sheet_path)
    print(f"saved {sheet_path}")

    base = ("https://raw.githubusercontent.com/ytocker/skybit/"
            "v5_powerups/docs/screenshots/skateboard_trick_bubbles")
    print()
    print(f"{base}/00_contact_sheet.png")
    for label, caption, _ in saved:
        print(f"{base}/{label}.png  -- {caption}")


if __name__ == "__main__":
    main()
