"""Compose the BOOGIE NIGHTS (Disco D1) round-4 review sheet.

Gameplay crop (left) + clean hero shot (middle) + a 40px NEAREST "truth read"
on day/night swatches (right), so the reviewer judges the real on-screen size.

Headless: SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
    python -m tools.disco_candidates.render_1_r4
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

import tools.ninja_render as nr
from tools.disco_candidates.design_1 import build

OUT = "docs/store_redesign/costume/disco/design_1/round_4.png"
TITLE = "D1 BOOGIE NIGHTS — R4 (jacket + medallion on forward chest)"


def _label(surf, text, x, y, size=18, color=(236, 238, 246)):
    font = pygame.font.SysFont("arial", size, bold=True)
    surf.blit(font.render(text, True, color), (x, y))


def _truth_read(box):
    """40px-in-motion test: crop the bird to content, NEAREST-shrink to a ~40px
    tall sprite, then magnify 3x on day + night swatches."""
    frame = build(nr.FRAME_IDX, nr.TILT)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = 40.0 / max(sw, sh)
    small = pygame.transform.scale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    panel = pygame.Surface((box, box))
    half = box // 2
    pygame.draw.rect(panel, (150, 200, 235), (0, 0, half, box))         # day sky
    pygame.draw.rect(panel, (16, 18, 34), (half, 0, box - half, box))   # night sky
    for ox in (half // 2, half + half // 2):
        tile = pygame.Surface((48, 48), pygame.SRCALPHA)
        tile.blit(small, small.get_rect(center=(24, 24)))
        big = pygame.transform.scale(tile, (144, 144))
        panel.blit(big, big.get_rect(center=(ox, box // 2 + 8)))
    return panel


def main():
    box = 360
    gw = int(box * 9 / 16)
    hero = nr.hero_panel(build, box)
    gameplay = nr.gameplay_panel(build, gw, box)
    truth = _truth_read(box)

    pad = 18
    head = 56
    widths = [gw, box, box]
    W = pad * (len(widths) + 1) + sum(widths)
    H = head + box + 30 + pad
    sheet = pygame.Surface((W, H))
    sheet.fill((18, 17, 26))
    _label(sheet, TITLE, pad, 16, size=22)

    xs, x = [], pad
    for w in widths:
        xs.append(x)
        x += w + pad
    y = head
    for x, panel in zip(xs, (gameplay, hero, truth)):
        sheet.blit(panel, (x, y))
    for x, name in zip(xs, ("IN-GAMEPLAY (day biome)", "HERO PRODUCT SHOT",
                            "40px TRUTH READ  (day | night, 3x)")):
        _label(sheet, name, x, y + box + 6, size=15, color=(190, 194, 210))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(sheet, OUT)
    print("saved", OUT, sheet.get_size())


if __name__ == "__main__":
    main()
