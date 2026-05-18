"""Smoke-test the eased shrink transition.

Renders Pip once per 60-FPS frame across BOTH halves of the lifecycle:
  Row 1 — SHRINK     (scale eases 1.00 → SHRINK_SCALE over SHRINK_TRANSITION)
  Row 2 — UN-SHRINK  (scale eases SHRINK_SCALE → 1.00 over SHRINK_TRANSITION)

so the same easing logic drives both the activation and the
restore-after-expiry. Cell labels show the frame index and the current
shrink_scale. Run headless:

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

from game.config import SHRINK_TRANSITION, SHRINK_SCALE, FPS
from game.entities import Bird

DT          = 1.0 / FPS
TRANS_FRAMES = int(round(SHRINK_TRANSITION * FPS))     # 12 frames @ 60 FPS
HOLD_FRAMES  = 2                                       # locked-at-target tail
N_FRAMES     = TRANS_FRAMES + 1 + HOLD_FRAMES          # incl. t=0 start frame

CELL_W, CELL_H = 78, 110
PAD       = 4
LABEL_H   = 28
ROW_GAP   = 22
TITLE_H   = 22
BG        = (28, 38, 60)
BG_DEEP   = (14, 18, 32)
LBL       = (220, 230, 250)
TITLE_C   = (200, 220, 255)


def _tick_bird(activating: bool):
    """Build a Bird at the START of the transition for the given direction.
    Returns the bird; caller advances it with bird.update(DT) per frame."""
    bird = Bird()
    bird.x, bird.y = CELL_W // 2, CELL_H // 2 + 4
    bird.frame_t = 0.4
    bird.shrink_active = activating
    bird.shrink_scale = 1.0 if activating else SHRINK_SCALE
    bird.vy = 0
    return bird


def _cell(bird: Bird, label_top: str, label_bot: str) -> pygame.Surface:
    cell = pygame.Surface((CELL_W, CELL_H)).convert()
    cell.fill(BG)
    # Pinch the bird's y back so flapping idle doesn't drift across cells.
    bird.y = CELL_H // 2 + 4
    bird.draw(cell)
    font_top = pygame.font.SysFont(None, 14)
    font_bot = pygame.font.SysFont(None, 13)
    t = font_top.render(label_top, True, LBL)
    b = font_bot.render(label_bot, True, LBL)
    cell.blit(t, (CELL_W // 2 - t.get_width() // 2, CELL_H - 28))
    cell.blit(b, (CELL_W // 2 - b.get_width() // 2, CELL_H - 14))
    return cell


def _row(activating: bool, title: str) -> pygame.Surface:
    width  = PAD + (CELL_W + PAD) * N_FRAMES
    height = TITLE_H + CELL_H + PAD * 2
    row = pygame.Surface((width, height)).convert()
    row.fill(BG_DEEP)
    title_font = pygame.font.SysFont(None, 20, bold=True)
    title_surf = title_font.render(title, True, TITLE_C)
    row.blit(title_surf, (PAD + 2, 2))

    bird = _tick_bird(activating)
    for i in range(N_FRAMES):
        is_held = i > TRANS_FRAMES
        label_top = f"f={i:>2}  t={i * DT * 1000:>4.0f}ms"
        label_bot = f"scale={bird.shrink_scale:.3f}"
        if is_held:
            label_bot += "  (held)"
        cell = _cell(bird, label_top, label_bot)
        x = PAD + i * (CELL_W + PAD)
        row.blit(cell, (x, TITLE_H + PAD))
        # advance one 60-FPS frame for the NEXT cell
        bird.update(DT, gravity_sign=0)
    return row


def main():
    out_dir = os.path.join(_REPO, "docs", "shrink_pickup_variants")
    os.makedirs(out_dir, exist_ok=True)
    row_shrink = _row(activating=True,
                      title=f"SHRINK  (shrink_active=True, target={SHRINK_SCALE})")
    row_restore = _row(activating=False,
                       title="RESTORE  (shrink_active=False, target=1.000)")

    strip_w = max(row_shrink.get_width(), row_restore.get_width())
    strip_h = row_shrink.get_height() + ROW_GAP + row_restore.get_height()
    strip = pygame.Surface((strip_w, strip_h)).convert()
    strip.fill(BG_DEEP)
    strip.blit(row_shrink,  (0, 0))
    strip.blit(row_restore, (0, row_shrink.get_height() + ROW_GAP))

    path = os.path.join(out_dir, "transition_strip.png")
    pygame.image.save(strip, path)
    print(f"wrote {path}  ({N_FRAMES} frames × 2 rows)")


if __name__ == "__main__":
    main()
