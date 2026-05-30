"""Genie chamber mock — the widened-gap pillar with the 3 offers
stacked vertically inside it, shown as real PlayScene frames.

Two fit options side by side:
  LEFT : 1.5x gap + column at +/-80  (tight)
  RIGHT: 1.6x gap + column at +/-70  (comfortable)

Pip is parked mid-approach so you can read the chamber as it would
appear scrolling toward him.

Output: docs/screenshots/icon_sizes/genie_chamber_mock.png
"""
from __future__ import annotations

import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(THIS_DIR))

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H, GAP_START
from game.scenes import App, STATE_PLAY
from game.entities import Pipe, PowerUp


# (label, gap_boost, column_half_span)
VARIANTS = (
    ("1.5x gap  +  column +/-80", 1.5, 80),
    ("1.6x gap  +  column +/-70", 1.6, 70),
)

CHAMBER_X = 235     # pillar x — visible, ahead of Pip (x=90), about to be entered
GAP_CENTER = 300    # vertical centre of the chamber gap

CARD_BG = (24, 26, 34)
LABEL   = (235, 235, 240)
SUB     = (165, 173, 185)


def _font(size, bold=False):
    return pygame.font.SysFont("Arial", size, bold=bold)


def _grab_frame(gap_boost, half_span) -> pygame.Surface:
    app = App()
    app.state = STATE_PLAY
    app.world.ready_t = 0
    app.world.bird.x = 90
    app.world.bird.y = GAP_CENTER          # Pip lined up with the gap centre
    app.world.bird.vy = 0
    app.world.pipes.clear()
    app.world.coins.clear()
    app.world.powerups.clear()

    gap_h = int(GAP_START * gap_boost)
    chamber = Pipe(CHAMBER_X, GAP_CENTER, gap_h)
    app.world.pipes.append(chamber)

    # 3 offers stacked in the gap, centred on the gap centre.
    for kind, dy in (("skateboard", -half_span),
                     ("poison", 0),
                     ("knight", half_span)):
        p = PowerUp(CHAMBER_X + 29, GAP_CENTER + dy, kind=kind)  # centre of pillar width
        p.is_genie_offer = True
        p.pulse = 0.0
        app.world.powerups.append(p)

    app._render()
    return app.screen.copy()


def main():
    out_dir = os.path.join(os.path.dirname(THIS_DIR),
                           "docs", "screenshots", "icon_sizes")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "genie_chamber_mock.png")

    PAD = 18
    COL_GAP = 24
    HEADER = 64
    CAP_H = 30

    frames = [(lbl, _grab_frame(boost, hs))
              for (lbl, boost, hs) in VARIANTS]

    sheet_w = PAD * 2 + len(frames) * (W + COL_GAP) - COL_GAP
    sheet_h = HEADER + H + CAP_H + PAD
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(CARD_BG)

    title = _font(22, bold=True).render(
        "GENIE chamber — 3 wishes stacked in a widened pillar gap",
        True, LABEL)
    sheet.blit(title, (PAD, 14))
    sub = _font(13).render(
        "Real PlayScene frames. Pip flies through the over-wide gap and "
        "picks one offer by altitude. SKATEBOARD top / POISON mid / KNIGHT bottom.",
        True, SUB)
    sheet.blit(sub, (PAD, 38))

    for i, (lbl, frame) in enumerate(frames):
        x = PAD + i * (W + COL_GAP)
        y = HEADER
        sheet.blit(frame, (x, y))
        pygame.draw.rect(sheet, (60, 66, 80), (x, y, W, H), 1)
        cap = _font(15, bold=True).render(lbl, True, LABEL)
        sheet.blit(cap, (x, y + H + 6))

    pygame.image.save(sheet, out_path)
    print(f"saved {out_path}  ({sheet_w}x{sheet_h})  "
          f"GAP_START={GAP_START}")


if __name__ == "__main__":
    main()
