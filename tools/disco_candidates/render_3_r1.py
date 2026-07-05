"""Compose the D3 ROLLER GROOVE round-1 review sheet.

Three reads side by side so the costume is judged the way it ships: a clean
NEAREST-upscaled hero product shot, Pip mid-flight in a real daytime biome, and
the 40px truth read on day + night (the "lives or dies at 40px in motion" bar).

Headless: SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m tools.disco_candidates.render_3_r1
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from tools import ninja_render
from tools.disco_candidates.design_3 import build

OUT = "docs/store_redesign/costume/disco/design_3/round_1.png"
TITLE = "D3 ROLLER GROOVE — R1"


def _label(surf, text, x, y, size=18, color=(236, 238, 246)):
    font = pygame.font.SysFont("arial", size, bold=True)
    surf.blit(font.render(text, True, color), (x, y))


def _hero_nearest(box):
    """Clean large product shot, NEAREST integer upscale so the pixel art is
    judged crisp (not smoothed)."""
    frame = build(ninja_render.FRAME_IDX, 0.0)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = max(1, int((box * 0.80) / max(sw, sh)))
    big = pygame.transform.scale(frame, (sw * scale, sh * scale))
    panel = pygame.Surface((box, box), pygame.SRCALPHA)
    pygame.draw.rect(panel, (22, 20, 32), panel.get_rect(), border_radius=14)
    panel.blit(big, big.get_rect(center=(box // 2, box // 2)))
    return panel


def _truth_read(box):
    """The 40px-in-motion test: shrink to ~40px on NEAREST then magnify 3x so
    the reviewer judges the real on-screen read on day + night."""
    frame = build(ninja_render.FRAME_IDX, ninja_render.TILT)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = 40.0 / max(sw, sh)
    small = pygame.transform.scale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    panel = pygame.Surface((box, box))
    panel.fill((30, 28, 40))
    half = box // 2
    pygame.draw.rect(panel, (150, 200, 235), (0, 0, half, box))        # day sky
    pygame.draw.rect(panel, (16, 18, 34), (half, 0, box - half, box))  # night sky
    for ox in (half // 2, half + half // 2):
        tile = pygame.Surface((48, 48), pygame.SRCALPHA)
        tile.blit(small, small.get_rect(center=(24, 24)))
        big = pygame.transform.scale(tile, (48 * 3, 48 * 3))
        panel.blit(big, big.get_rect(center=(ox, box // 2 + 8)))
    return panel


def main():
    box = 360
    gw = int(box * 9 / 16)
    hero = _hero_nearest(box)
    gameplay = ninja_render.gameplay_panel(build, gw, box)
    truth = _truth_read(box)

    pad = 18
    head = 56
    cap = 30
    widths = [box, gw, box]
    W = pad * (len(widths) + 1) + sum(widths)
    H = head + box + cap + pad
    sheet = pygame.Surface((W, H))
    sheet.fill((18, 17, 26))
    _label(sheet, TITLE, pad, 16, size=22)

    xs = []
    x = pad
    for w in widths:
        xs.append(x)
        x += w + pad
    y = head
    for x, panel in zip(xs, (hero, gameplay, truth)):
        sheet.blit(panel, (x, y))
    for x, name in zip(xs, ("HERO PRODUCT SHOT (NEAREST 3x)", "IN-GAMEPLAY (day biome)",
                            "40px TRUTH READ  (day | night, 3x)")):
        _label(sheet, name, x, y + box + 6, size=15, color=(190, 194, 210))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(sheet, OUT)
    print("saved", OUT, sheet.get_size())


if __name__ == "__main__":
    main()
