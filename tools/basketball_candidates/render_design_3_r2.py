"""Compose the RETRO '90s design_3 round-2 review sheet.

Panels: HERO NEAREST (clean product shot), IN GAMEPLAY (day biome), and the
40px truth read split into a DAY tile and a NIGHT tile — the on-screen size the
costume actually has to survive, magnified so the reviewer can read it.

Headless: SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python <this>.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from tools import ninja_render
from tools.basketball_candidates.design_3 import build

OUT = "docs/store_redesign/costume/basketball/design_3/round_2.png"
TITLE = "BASKETBALL · DESIGN 3 — THE RETRO '90s (short-shorts)  round 2"


def _label(surf, text, x, y, size=18, color=(236, 238, 246)):
    font = pygame.font.SysFont("arial", size, bold=True)
    surf.blit(font.render(text, True, color), (x, y))


def _hero_nearest(box):
    """HERO NEAREST: the bird scaled up on a flat card with NEAREST (no smoothing)
    so every drawn pixel of the costume is judged honestly, not blurred."""
    frame = build(ninja_render.FRAME_IDX, 0.0)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = (box * 0.78) / max(sw, sh)
    big = pygame.transform.scale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    panel = pygame.Surface((box, box), pygame.SRCALPHA)
    pygame.draw.rect(panel, (22, 20, 32), panel.get_rect(), border_radius=14)
    panel.blit(big, big.get_rect(center=(box // 2, box // 2)))
    return panel


def _truth_tile(box, sky):
    """One 40px-on-NEAREST tile over a flat sky, magnified 3x."""
    frame = build(ninja_render.FRAME_IDX, ninja_render.TILT)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = 40.0 / max(sw, sh)
    small = pygame.transform.scale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    panel = pygame.Surface((box, box))
    panel.fill(sky)
    tile = pygame.Surface((48, 48), pygame.SRCALPHA)
    tile.blit(small, small.get_rect(center=(24, 24)))
    big = pygame.transform.scale(tile, (48 * 3, 48 * 3))
    panel.blit(big, big.get_rect(center=(box // 2, box // 2)))
    return panel


def main():
    box = 360
    gw = int(box * 9 / 16)
    half = box // 2 - 6

    hero = _hero_nearest(box)
    gameplay = ninja_render.gameplay_panel(build, gw, box)
    day = _truth_tile(half, (150, 200, 235))
    night = _truth_tile(half, (16, 18, 34))

    # Stack day+night tiles into one truth column the width of a hero box.
    truth = pygame.Surface((box, box))
    truth.fill((30, 28, 40))
    truth.blit(day, ((box - half) // 2, 6))
    truth.blit(night, ((box - half) // 2, 12 + half))
    _label(truth, "40px DAY", (box - half) // 2 + 6, 10, size=13)
    _label(truth, "40px NIGHT", (box - half) // 2 + 6, 16 + half, size=13)

    pad = 18
    head = 56
    cap = 26
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
    for x, name in zip(xs, ("HERO NEAREST (product shot)",
                            "IN-GAMEPLAY (day biome)",
                            "40px TRUTH READ  (day | night, 3x)")):
        _label(sheet, name, x, y + box + 6, size=15, color=(190, 194, 210))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(sheet, OUT)
    print("saved", OUT, sheet.get_size())


if __name__ == "__main__":
    main()
