"""Re-render the in-game placement frames committed alongside this file.

These are NOT design mock-ups — they go through the real game pipeline
(``game.world.World`` + ``game.hud.HUD.draw_play`` + the live
``game.lottery_slot.draw_reveal``) so the cabinet-vs-HUD layout matches
exactly what the player sees.

Run it whenever the cabinet position or the HUD changes and you want
to refresh the committed PNGs:

    python archive/lottery_design/render_in_game_placement.py

Outputs:
    screenshots/live_placement_jackpot.png    JACKPOT, 2 active buffs
    screenshots/live_placement_bust.png       BUST, 2 active buffs
    screenshots/live_placement_win.png        WIN, no active buffs
"""
from __future__ import annotations

import os
import pathlib
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(_HERE.parent.parent))

import pygame
pygame.init()
pygame.display.set_mode((360, 640))

from game.world import World
from game.hud import HUD
from game.lottery_slot import draw_reveal
from archive.lottery_design.render_lottery_variants import (
    _draw_backdrop, _draw_bird,
)


def _compose(*, tier, delta, with_buffs):
    w = World()
    w.ready_t = 0
    w.score = 537
    w.coin_count = 42
    if with_buffs:
        w.triple_timer = 5.0
        w.magnet_timer = 3.0
    hud = HUD()
    surf = pygame.Surface((360, 640))
    _draw_backdrop(surf)
    _draw_bird(surf)
    # Reveal frame, just past LOTTERY_REVEAL_TIME so the prize is locked.
    draw_reveal(surf, {"t": 1.10, "tier": tier, "delta": delta,
                       "x": 0, "y": 0, "applied": True})
    # HUD draws AFTER the lottery — mirrors scenes.py App._render order.
    hud.draw_play(surf, w, best=1234)
    return surf


def main():
    out = _HERE / "screenshots"
    out.mkdir(parents=True, exist_ok=True)
    frames = (
        ("live_placement_jackpot.png",
         dict(tier="JACKPOT", delta=+100, with_buffs=True)),
        ("live_placement_bust.png",
         dict(tier="BUST", delta=-50, with_buffs=True)),
        ("live_placement_win.png",
         dict(tier="WIN", delta=+15, with_buffs=False)),
    )
    for name, kwargs in frames:
        surf = _compose(**kwargs)
        path = out / name
        pygame.image.save(surf, path)
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
