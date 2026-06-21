"""Render the 5 UFO redesign concepts as REAL in-game frames, side by side.

Unlike round_N.png (a technical hero + 40px truth-test sheet), this drops each
concept into the actual staged gameplay scene (sky, mountains, pillars, coins,
ground) used by docs/showcase, with the live HUD overlaid, so the designs can be
compared exactly as they appear mid-play.

Run:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python docs/animals/ufo_redesign/_render_gameplay.py
"""
import os, sys, pathlib

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "docs" / "showcase"))
sys.path.insert(0, str(pathlib.Path(__file__).parent))

import pygame
import render_showcase as RS              # does pygame.init + a 1x1 display
from game.config import W, H
from game import parrot
from game.animal_ufo import _make_prebuilt_skin
from game.hud import HUD
from ufo_skins import CONCEPTS

OUT = pathlib.Path(__file__).parent / "gameplay_compare.png"


def _frame(world, base, hud, build_fn):
    """Draw one concept into a fresh copy of the staged scene + HUD."""
    builders = parrot._store_skin_builders()
    builders["skin_ufo"] = _make_prebuilt_skin(build_fn)   # hot-swap the dispatch
    full, _ = RS.render_look(world, base, "skin_ufo")
    try:
        hud.draw_play(full, world, best=world.score)
    except Exception:
        pass                                                # frame still valid
    return full


def main():
    world, base = RS.build_scene()
    world.score = 42                                        # a believable run score
    hud = HUD()

    pad, label_h, bg = 14, 40, (24, 26, 32)
    n = len(CONCEPTS)
    sheet = pygame.Surface((pad + n * (W + pad), label_h + H + pad))
    sheet.fill(bg)
    font = pygame.font.SysFont("Arial", 22, bold=True)

    for i, (name, build_fn) in enumerate(CONCEPTS):
        frame = _frame(world, base, hud, build_fn)
        x = pad + i * (W + pad)
        sheet.blit(frame, (x, label_h))
        lab = font.render(name, True, (240, 240, 245))
        sheet.blit(lab, (x + (W - lab.get_width()) // 2, (label_h - lab.get_height()) // 2))

    pygame.image.save(sheet, str(OUT))
    print("wrote", OUT, sheet.get_size())


if __name__ == "__main__":
    main()
