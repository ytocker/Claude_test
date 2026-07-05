"""Round-2 review sheet for SOCCER costume DESIGN 1 — THE STRIKER.

Composites a large NEAREST hero shot (integer upscale of the raw frame — no
smoothscale, so the pixels stay hard and the leg kit is judged honestly), an
in-gameplay panel, and a 40px "truth read" of the raw frame on both a day-bright
and a night-dark swatch. The downscale is where a costume lives or dies, so the
truth read is the real verdict on whether the lower silhouette still says
"soccer striker" (tall socks + boot wedges) and not "basketball" (baggy shorts +
sneakers).

Headless: SDL_VIDEODRIVER=dummy PYTHONPATH=. python tools/soccer_candidates/render_design_1_r2.py
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from tools.ninja_render import gameplay_panel, _frame, FRAME_IDX, TILT
from tools.soccer_candidates.design_1 import build

OUT = "docs/store_redesign/costume/soccer/design_1/round_2.png"


def _hero_nearest(box: int, target: int) -> pygame.Surface:
    """Large product shot built by NEAREST integer upscale of the RAW frame —
    no smoothscale anywhere — so the leg kit's pixels are judged crisp, not blurred."""
    panel = pygame.Surface((box, box), pygame.SRCALPHA)
    pygame.draw.rect(panel, (22, 20, 32), panel.get_rect(), border_radius=14)
    frame = _frame(build, FRAME_IDX, 0.0)
    bb = frame.get_bounding_rect()
    if bb.width and bb.height:
        frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    # Integer scale factor keeps the upscale a clean NEAREST pixel grid.
    factor = max(1, int((box * 0.82) / max(sw, sh)))
    big = pygame.transform.scale(frame, (sw * factor, sh * factor))
    panel.blit(big, big.get_rect(center=(box // 2, box // 2)))
    return panel


def _truth_read(box: int, bg) -> pygame.Surface:
    """Raw frame cropped to content, NEAREST-downscaled to ~40px on a flat
    swatch — exactly what the eye gets in-game at store-thumbnail scale."""
    panel = pygame.Surface((box, box))
    panel.fill(bg)
    frame = _frame(build, FRAME_IDX, TILT)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = 40 / max(sw, sh)
    small = pygame.transform.scale(  # NEAREST: the honest downscale
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    panel.blit(small, small.get_rect(center=(box // 2, box // 2)))
    return panel


def _label(surf, text, x, y, color=(235, 235, 240)):
    font = pygame.font.SysFont("dejavusans", 15, bold=True)
    surf.blit(font.render(text, True, (0, 0, 0)), (x + 1, y + 1))
    surf.blit(font.render(text, True, color), (x, y))


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    W, H = 760, 460
    sheet = pygame.Surface((W, H))
    sheet.fill((24, 22, 30))
    _label(sheet, "SOCCER — DESIGN 1: THE STRIKER  (round 2)", 18, 12, (255, 206, 84))

    # Large HERO shot — NEAREST integer upscale of the raw frame (no smoothscale).
    hero = _hero_nearest(320, 320)
    sheet.blit(hero, (18, 44))
    _label(sheet, "HERO  (NEAREST)", 22, 48)

    # In-gameplay panel (portrait crop matches the 360x640 canvas).
    gp = gameplay_panel(build, 230, 340)
    sheet.blit(gp, (440, 44))
    _label(sheet, "IN GAMEPLAY", 362, 48)

    # 40px truth reads on day-bright + night-dark swatches.
    ty = 376
    day = _truth_read(70, (150, 200, 235))
    night = _truth_read(70, (18, 16, 34))
    sheet.blit(day, (18, ty))
    sheet.blit(night, (96, ty))
    _label(sheet, "40px TRUTH READ  (day / night)", 176, ty + 8)
    _label(sheet, "Tall socks + boot wedges = SOCCER", 176, ty + 30, (180, 230, 180))
    _label(sheet, "NOT baggy shorts + sneakers", 176, ty + 50, (180, 230, 180))

    pygame.image.save(sheet, OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
