"""Compose THE ULTRA round-2 review sheet: HERO NEAREST + gameplay + 40px
day/night truth read. Round 2 swaps the smooth hero for a NEAREST-magnified
hero so the reviewer judges the same hard-pixel edges the game shows.

Headless: SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python <this>.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from tools import ninja_render
from tools.soccer_candidates.design_5 import build

OUT = "docs/store_redesign/costume/soccer/design_5/round_2.png"
TITLE = "DESIGN 5 — THE ULTRA (Soccer fan: scarf + bobble hat)  round 2"


def _label(surf, text, x, y, size=18, color=(236, 238, 246)):
    font = pygame.font.SysFont("arial", size, bold=True)
    surf.blit(font.render(text, True, color), (x, y))


def _hero_nearest(box):
    """A clean product shot of Pip on a flat panel, magnified with NEAREST so the
    reviewer judges the true hard-edged pixels (no smoothscale softening)."""
    panel = pygame.Surface((box, box))
    panel.fill((22, 20, 32))
    frame = build(ninja_render.FRAME_IDX, 0.0)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = max(1, int((box * 0.82) / max(sw, sh)))
    big = pygame.transform.scale(frame, (sw * scale, sh * scale))     # NEAREST
    panel.blit(big, big.get_rect(center=(box // 2, box // 2)))
    return panel


def _truth_read(box):
    """The 40px-in-motion test: render the bird, NEAREST-shrink to a ~40px bird
    then magnify 3x on a day-bright and a night-dark swatch — the real read."""
    frame = build(ninja_render.FRAME_IDX, ninja_render.TILT)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    scale = 40.0 / max(sw, sh)
    small = pygame.transform.scale(
        frame, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    tile = pygame.Surface((48, 48), pygame.SRCALPHA)
    panel = pygame.Surface((box, box))
    panel.fill((30, 28, 40))
    half = box // 2
    pygame.draw.rect(panel, (150, 200, 235), (0, 0, half, box))        # day sky
    pygame.draw.rect(panel, (16, 18, 34), (half, 0, box - half, box))  # night sky
    for ox in (half // 2 - 20, half + half // 2 - 20):
        t = tile.copy()
        t.blit(small, small.get_rect(center=(24, 24)))
        big = pygame.transform.scale(t, (48 * 3, 48 * 3))             # NEAREST
        panel.blit(big, big.get_rect(center=(ox + 20, box // 2 + 8)))
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
    for x, name in zip(xs, ("HERO (NEAREST)", "IN-GAMEPLAY (day biome)",
                            "40px TRUTH READ  (day | night, 3x)")):
        _label(sheet, name, x, y + box + 6, size=15, color=(190, 194, 210))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(sheet, OUT)
    print("saved", OUT, sheet.get_size())


if __name__ == "__main__":
    main()
