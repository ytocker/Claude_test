"""Smoke-test the eased SHRINK and GROW transitions side by side.

Both buffs share the same per-frame easing pipeline in Bird.update —
they just run in opposite directions across the 1.0 mark. This tool
renders Pip once per 60-FPS frame across each buff's full lifecycle
so reviewers can confirm the animations match in duration / frame
count and behave symmetrically:

  Row 1 — SHRINK             scale eases 1.000 → SHRINK_SCALE
  Row 2 — SHRINK → RESTORE   scale eases SHRINK_SCALE → 1.000
  Row 3 — GROW               scale eases 1.000 → GROW_SCALE
  Row 4 — GROW → RESTORE     scale eases GROW_SCALE → 1.000

Cell labels show the frame index, elapsed ms, and the live scale.
Run headless:

    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_shrink_transition_strip.py

Writes docs/shrink_pickup_variants/transition_strip.png.
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

from game.config import (
    SHRINK_TRANSITION, SHRINK_SCALE,
    GROW_TRANSITION, GROW_SCALE,
    FPS,
)
from game.entities import Bird

DT          = 1.0 / FPS
TRANS_FRAMES = int(round(SHRINK_TRANSITION * FPS))     # 12 @ 60 FPS
HOLD_FRAMES  = 2
N_FRAMES     = TRANS_FRAMES + 1 + HOLD_FRAMES

CELL_W, CELL_H = 82, 130            # taller cells — grow needs vertical room
PAD       = 4
ROW_GAP   = 18
TITLE_H   = 22
BG        = (28, 38, 60)
BG_DEEP   = (14, 18, 32)
LBL       = (220, 230, 250)
TITLE_C   = (200, 220, 255)


def _build_bird(buff: str, activating: bool) -> Bird:
    """Build a Bird at the START of the chosen buff's transition.
    `buff` ∈ {'shrink', 'grow'}; `activating` True for the on-arc and
    False for the restore-arc."""
    bird = Bird()
    bird.x, bird.y = CELL_W // 2, CELL_H // 2 + 8
    bird.frame_t = 0.4
    bird.vy = 0
    if buff == "shrink":
        bird.shrink_active = activating
        bird.shrink_scale = 1.0 if activating else SHRINK_SCALE
    else:
        bird.grow_active = activating
        bird.grow_scale = 1.0 if activating else GROW_SCALE
    return bird


def _live_scale(bird: Bird, buff: str) -> float:
    return bird.shrink_scale if buff == "shrink" else bird.grow_scale


def _cell(bird: Bird, label_top: str, label_bot: str) -> pygame.Surface:
    cell = pygame.Surface((CELL_W, CELL_H)).convert()
    cell.fill(BG)
    bird.y = CELL_H // 2 + 8
    bird.draw(cell)
    font_top = pygame.font.SysFont(None, 14)
    font_bot = pygame.font.SysFont(None, 13)
    t = font_top.render(label_top, True, LBL)
    b = font_bot.render(label_bot, True, LBL)
    cell.blit(t, (CELL_W // 2 - t.get_width() // 2, CELL_H - 28))
    cell.blit(b, (CELL_W // 2 - b.get_width() // 2, CELL_H - 14))
    return cell


def _row(buff: str, activating: bool, title: str) -> pygame.Surface:
    width  = PAD + (CELL_W + PAD) * N_FRAMES
    height = TITLE_H + CELL_H + PAD * 2
    row = pygame.Surface((width, height)).convert()
    row.fill(BG_DEEP)
    title_font = pygame.font.SysFont(None, 20, bold=True)
    title_surf = title_font.render(title, True, TITLE_C)
    row.blit(title_surf, (PAD + 2, 2))

    bird = _build_bird(buff, activating)
    for i in range(N_FRAMES):
        is_held = i > TRANS_FRAMES
        label_top = f"f={i:>2}  t={i * DT * 1000:>4.0f}ms"
        label_bot = f"scale={_live_scale(bird, buff):.3f}"
        if is_held:
            label_bot += "  (held)"
        cell = _cell(bird, label_top, label_bot)
        x = PAD + i * (CELL_W + PAD)
        row.blit(cell, (x, TITLE_H + PAD))
        bird.update(DT, gravity_sign=0)
    return row


def main():
    out_dir = os.path.join(_REPO, "docs", "shrink_pickup_variants")
    os.makedirs(out_dir, exist_ok=True)

    rows = (
        _row("shrink", True,
             f"SHRINK            shrink_active=True, target={SHRINK_SCALE:.3f}"),
        _row("shrink", False,
             "SHRINK → RESTORE  shrink_active=False, target=1.000"),
        _row("grow", True,
             f"GROW              grow_active=True,   target={GROW_SCALE:.3f}"),
        _row("grow", False,
             "GROW → RESTORE    grow_active=False,   target=1.000"),
    )

    strip_w = max(r.get_width() for r in rows)
    strip_h = sum(r.get_height() for r in rows) + ROW_GAP * (len(rows) - 1)
    strip = pygame.Surface((strip_w, strip_h)).convert()
    strip.fill(BG_DEEP)
    y = 0
    for r in rows:
        strip.blit(r, (0, y))
        y += r.get_height() + ROW_GAP

    path = os.path.join(out_dir, "transition_strip.png")
    pygame.image.save(strip, path)
    print(f"wrote {path}  ({N_FRAMES} frames × {len(rows)} rows)")


if __name__ == "__main__":
    main()
