"""Compose the GLINTWING (design_4) review sheet: a hero product shot, an
in-gameplay day-biome panel, a 4-frame flap strip showing the opposing wing
beat, and a 40px NEAREST truth read (day | night, 3 poses).

Scratch exploration; nothing here touches production art.

Headless: SDL_VIDEODRIVER=dummy python tools/bee_candidates/_render_design_4.py
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from tools import ninja_render
from tools.bee_candidates.design_4 import build

OUT = "docs/store_redesign/animal/bee/design_4/round_2.png"
TITLE = "DESIGN 4 — GLINTWING  (dragonfly: needle body + huge compound eyes + 4 glassy X-wings)"


def _label(surf, text, x, y, size=18, color=(236, 238, 246)):
    font = pygame.font.SysFont("arial", size, bold=True)
    surf.blit(font.render(text, True, color), (x, y))


def _flap_strip(box):
    """The four flap frames side by side on a soft panel — shows the fore/hind
    opposing beat that a single hero pose can't."""
    panel = pygame.Surface((box, box // 4 + 10))
    panel.fill((26, 30, 34))
    cell = box // 4
    for i in range(4):
        frame = build(i, 6.0)
        bb = frame.get_bounding_rect()
        frame = frame.subsurface(bb).copy()
        sw, sh = frame.get_size()
        scale = (cell * 0.86) / max(sw, sh)
        frame = pygame.transform.smoothscale(
            frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
        cx = cell // 2 + i * cell
        panel.blit(frame, frame.get_rect(center=(cx, (box // 4 + 10) // 2)))
    return panel


def _truth_read(box):
    """40px-in-motion test: NEAREST-shrink to a ~40px bird then magnify 3x so
    the real on-screen read is judged over a day | night split, 3 poses."""
    frames = [build(fi, t) for fi, t in
              ((ninja_render.FRAME_IDX, ninja_render.TILT), (0, -8.0), (3, 22.0))]
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
    pygame.draw.rect(panel, (150, 200, 235), (0, 0, half, box))
    pygame.draw.rect(panel, (16, 18, 34), (half, 0, box - half, box))
    for row, small in enumerate(smalls):
        tile = pygame.Surface((48, 48), pygame.SRCALPHA)
        tile.blit(small, small.get_rect(center=(24, 24)))
        big = pygame.transform.scale(tile, (48 * 3, 48 * 3))
        ry = 20 + row * (box - 30) // 3
        for cx in (half // 2, half + half // 2):
            panel.blit(big, big.get_rect(center=(cx, ry + 60)))
    return panel


def main():
    box = 320
    gw = int(box * 9 / 16)
    pad = 18
    head = 54

    hero = ninja_render.hero_panel(build, box)
    gameplay = ninja_render.gameplay_panel(build, gw, box)
    truth = _truth_read(box)
    strip = _flap_strip(box)

    widths = [box, gw, box]
    captions = ("HERO PRODUCT SHOT", "IN-GAMEPLAY (day biome)",
                "40px TRUTH READ  (day | night, 3 poses)")

    W = pad * (len(widths) + 1) + sum(widths)
    H = head + box + 28 + strip.get_height() + 40 + pad
    sheet = pygame.Surface((W, H))
    sheet.fill((18, 17, 26))
    _label(sheet, TITLE, pad, 16, size=20)

    x = pad
    for panel, cap in zip((hero, gameplay, truth), captions):
        sheet.blit(panel, (x, head))
        _label(sheet, cap, x, head + box + 4, size=13, color=(190, 194, 210))
        x += panel.get_width() + pad

    sy = head + box + 28
    _label(sheet, "FLAP STRIP  (frames 0-3 — forewings & hindwings beat in opposition)",
           pad, sy - 2, size=13, color=(190, 194, 210))
    sheet.blit(strip, (pad, sy + 18))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(sheet, OUT)
    print("saved", OUT, sheet.get_size())


if __name__ == "__main__":
    main()
