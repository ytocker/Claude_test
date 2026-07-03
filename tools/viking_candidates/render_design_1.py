"""Compose the STORMBEARD review sheet (hero + gameplay + 40px truth read).

Headless: SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python <this>.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from tools import ninja_render
from tools.viking_candidates.design_1 import build

OUT = "docs/store_redesign/costume/viking/design_1/round_2.png"
TITLE = "DESIGN 1 — STORMBEARD  (Classic Raider Berserker) · ROUND 2"


def _label(surf, text, x, y, size=18, color=(236, 238, 246)):
    font = pygame.font.SysFont("arial", size, bold=True)
    surf.blit(font.render(text, True, color), (x, y))


def _truth_read(box):
    """The 40px-in-motion test: render the gameplay frame, NEAREST shrink it to
    a ~40px bird then magnify 3x so the reviewer judges the real on-screen read.
    Three side-by-side reads per phase so day/night each show three poses."""
    frames = [build(fi, t) for fi, t in
              ((ninja_render.FRAME_IDX, ninja_render.TILT),
               (0, -8.0), (3, 22.0))]
    smalls = []
    for frame in frames:
        bb = frame.get_bounding_rect()
        frame = frame.subsurface(bb).copy()
        sw, sh = frame.get_size()
        scale = 40.0 / max(sw, sh)
        smalls.append(pygame.transform.scale(
            frame, (max(1, int(sw * scale)), max(1, int(sh * scale)))))

    panel = pygame.Surface((box, box))
    half = box // 2
    pygame.draw.rect(panel, (150, 200, 235), (0, 0, half, box))        # day sky
    pygame.draw.rect(panel, (16, 18, 34), (half, 0, box - half, box))  # night sky
    # three stacked rows × two phase columns.
    for row, small in enumerate(smalls):
        tile = pygame.Surface((48, 48), pygame.SRCALPHA)
        tile.blit(small, small.get_rect(center=(24, 24)))
        big = pygame.transform.scale(tile, (48 * 2, 48 * 2))
        ry = 28 + row * (box - 40) // 3
        for col, cx in enumerate((half // 2, half + half // 2)):
            panel.blit(big, big.get_rect(center=(cx, ry + 48)))
    return panel


def main():
    box = 360
    gw = int(box * 9 / 16)
    hero = ninja_render.hero_panel(build, box)
    gameplay = ninja_render.gameplay_panel(build, gw, box)
    truth = _truth_read(box)

    pad = 18
    head = 56
    widths = [box, gw, box]
    W = pad * (len(widths) + 1) + sum(widths)
    H = head + box + 30 + pad
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
    for x, name in zip(xs, ("HERO PRODUCT SHOT", "IN-GAMEPLAY (day biome)",
                            "40px TRUTH READ  (day | night, 3 poses)")):
        _label(sheet, name, x, y + box + 6, size=15, color=(190, 194, 210))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(sheet, OUT)
    print("saved", OUT, sheet.get_size())


if __name__ == "__main__":
    main()
