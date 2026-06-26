"""Render all 5 sports candidate review sheets (hero + gameplay + 40px truth).

Headless: SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python <this>.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import importlib
import pygame
pygame.init()

from tools import ninja_render

DESIGNS = {
    1: "DESIGN 1 — THE STRIKER (Soccer)  round 1",
    2: "DESIGN 2 — THE BALLER (Basketball)  round 1",
    3: "DESIGN 3 — THE GRIDIRON (Am. Football)  round 1",
    4: "DESIGN 4 — THE SLUGGER (Baseball)  round 1",
    5: "DESIGN 5 — THE ACE (Tennis)  round 1",
}


def _label(surf, text, x, y, size=18, color=(236, 238, 246)):
    font = pygame.font.SysFont("arial", size, bold=True)
    surf.blit(font.render(text, True, color), (x, y))


def _truth_read(build, box):
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
    pygame.draw.rect(panel, (150, 200, 235), (0, 0, half, box))
    pygame.draw.rect(panel, (16, 18, 34), (half, 0, box - half, box))
    for ox in (half // 2 - 20, half + half // 2 - 20):
        t = tile.copy()
        t.blit(small, small.get_rect(center=(24, 24)))
        big = pygame.transform.scale(t, (48 * 3, 48 * 3))
        panel.blit(big, big.get_rect(center=(ox + 20, box // 2 + 8)))
    return panel


def render(n, title):
    build = importlib.import_module(f"tools.sports_candidates.design_{n}").build
    box = 360
    gw = int(box * 9 / 16)
    hero = ninja_render.hero_panel(build, box)
    gameplay = ninja_render.gameplay_panel(build, gw, box)
    truth = _truth_read(build, box)
    pad, head, cap = 18, 56, 30
    widths = [box, gw, box]
    W = pad * (len(widths) + 1) + sum(widths)
    H = head + box + cap + pad
    sheet = pygame.Surface((W, H))
    sheet.fill((18, 17, 26))
    _label(sheet, title, pad, 16, size=22)
    xs, x = [], pad
    for w in widths:
        xs.append(x); x += w + pad
    y = head
    for x, panel in zip(xs, (hero, gameplay, truth)):
        sheet.blit(panel, (x, y))
    for x, name in zip(xs, ("HERO PRODUCT SHOT", "IN-GAMEPLAY (day biome)",
                            "40px TRUTH READ  (day | night, 3x)")):
        _label(sheet, name, x, y + box + 6, size=15, color=(190, 194, 210))
    out = f"docs/store_redesign/costume/sports/design_{n}/round_1.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out)


if __name__ == "__main__":
    for n, title in DESIGNS.items():
        render(n, title)
