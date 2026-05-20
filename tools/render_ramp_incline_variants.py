"""Render 5 SKATEBOARD ramp incline candidates side-by-side.

Each candidate shows a ramp perched on a real pillar (crown
vegetation hidden), Pip mid-slide, dust trail spawning. Saves
individual frames and a contact sheet so the user can pick an
incline that feels right.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_ramp_incline_variants.py
"""

import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import GROUND_Y, BIRD_X, BIRD_R, PIPE_W, W, H
from game.world import World
from game.entities import PowerUp, Pipe, Ramp
from tools.render_helmet_side_view_variants import (
    render_play_scene, _label_band,
)


_OUT = os.path.join(_REPO, "docs", "screenshots", "ramp_incline")
os.makedirs(_OUT, exist_ok=True)


# 5 incline options, height-to-width ratio from gentle to extreme.
INCLINE_VARIANTS = [
    ("A1_gentle",    38, 22, "A1: 38×22 — ratio 0.58 (current gentlest)"),
    ("A2_moderate",  34, 26, "A2: 34×26 — ratio 0.76"),
    ("A3_steep",     30, 30, "A3: 30×30 — ratio 1.00 (square wedge)"),
    ("A4_very_steep", 26, 34, "A4: 26×34 — ratio 1.31"),
    ("A5_extreme",   22, 38, "A5: 22×38 — ratio 1.73 (near-vertical kicker)"),
]


def render_one(label, ramp_w, ramp_h):
    random.seed(7)
    w = World()
    w.ready_t = 0
    for _ in range(40):
        w.world_idle_tick(1 / 60)
    w._activate_skateboard(PowerUp(0, 0, kind="skateboard"))

    # Place a pipe + ramp clearly RIGHT of Pip so the wedge is
    # unobstructed in the screenshot. Bird stays at its idle hover
    # position on the left — we render it but it doesn't cover
    # the ramp.
    pipe = Pipe(220, 360, 130)
    w.pipes = [pipe]
    pipe.has_ramp = True
    gap_bot = pipe.gap_y + pipe.gap_h / 2
    rx = pipe.x + max(0, (PIPE_W - ramp_w) // 2)
    w.ramps = [Ramp(rx, ramp_w, ramp_h, base_y=gap_bot)]
    # Hold Pip a little above mid-screen so he's visible but not
    # near the ramp.
    w.bird.y = H * 0.38
    w.bird.vy = 0

    frame = render_play_scene(w)
    # render_play_scene doesn't include ramps; draw them + the bird
    # explicitly so they're visible.
    for r in w.ramps:
        r.draw(frame)
    w.bird.draw(frame, 0, 0)
    return frame


def main():
    saved = []
    for label, rw, rh, caption in INCLINE_VARIANTS:
        frame = render_one(label, rw, rh)
        path = os.path.join(_OUT, f"{label}.png")
        pygame.image.save(frame, path)
        saved.append((label, caption, frame))
        print(f"saved {path}")

    # Horizontal contact sheet — 5 cells, label band under each.
    cell_w, cell_h = saved[0][2].get_size()
    band_h = 56
    gap = 12
    sheet_w = 5 * cell_w + 4 * gap + 24
    sheet_h = cell_h + band_h + 24
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((10, 12, 24))
    for idx, (label, caption, frame) in enumerate(saved):
        x = 12 + idx * (cell_w + gap)
        sheet.blit(frame, (x, 12))
        band = _label_band(cell_w, label, caption, height=band_h)
        sheet.blit(band, (x, 12 + cell_h))
    sheet_path = os.path.join(_OUT, "00_contact_sheet.png")
    pygame.image.save(sheet, sheet_path)
    print(f"saved {sheet_path}")

    base = ("https://raw.githubusercontent.com/ytocker/skybit/"
            "v5_powerups/docs/screenshots/ramp_incline")
    print()
    print(f"{base}/00_contact_sheet.png")
    for label, caption, _ in saved:
        print(f"{base}/{label}.png  -- {caption}")


if __name__ == "__main__":
    main()
