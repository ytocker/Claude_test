"""Compose the WARCHIEF (design_1) review sheet: for EACH palette
(IRONCLAD then BLOODAXE) a hero zoom + an in-gameplay panel + a 40px NEAREST
truth read. Scratch exploration; nothing here touches production art.

Headless: SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python <this>.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from tools import ninja_render
from tools.viking_face_candidates.design_1 import build_ironclad, build_bloodaxe

OUT = "docs/store_redesign/costume/viking/face/design_1/round_1.png"
TITLE = "DESIGN 1 — WARCHIEF  (handlebar mustache + forked twin-braid beard + held bearded axe)"


def _label(surf, text, x, y, size=18, color=(236, 238, 246)):
    font = pygame.font.SysFont("arial", size, bold=True)
    surf.blit(font.render(text, True, color), (x, y))


def _truth_read(build, box):
    """The 40px-in-motion test: render the gameplay frame, NEAREST shrink it to a
    ~40px bird then magnify 3x so the real on-screen read is judged. Three poses
    over a day | night split."""
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
    for row, small in enumerate(smalls):
        tile = pygame.Surface((48, 48), pygame.SRCALPHA)
        tile.blit(small, small.get_rect(center=(24, 24)))
        big = pygame.transform.scale(tile, (48 * 3, 48 * 3))           # NEAREST x3
        ry = 20 + row * (box - 30) // 3
        for cx in (half // 2, half + half // 2):
            panel.blit(big, big.get_rect(center=(cx, ry + 60)))
    return panel


def _palette_row(build, sheet, y, box, gw):
    hero = ninja_render.hero_panel(build, box)
    gameplay = ninja_render.gameplay_panel(build, gw, box)
    truth = _truth_read(build, box)
    pad = 18
    xs, x = [], pad
    for w in (box, gw, box):
        xs.append(x)
        x += w + pad
    for x, panel in zip(xs, (hero, gameplay, truth)):
        sheet.blit(panel, (x, y))
    return xs


def main():
    box = 320
    gw = int(box * 9 / 16)
    pad = 18
    head = 50
    sub = 30
    widths = [box, gw, box]
    W = pad * (len(widths) + 1) + sum(widths)
    rowH = box + sub + 24
    H = head + 2 * rowH + pad
    sheet = pygame.Surface((W, H))
    sheet.fill((18, 17, 26))
    _label(sheet, TITLE, pad, 14, size=20)

    captions = ("HERO PRODUCT SHOT", "IN-GAMEPLAY (day biome)",
                "40px TRUTH READ  (day | night, 3 poses)")
    for ri, (build, pname) in enumerate(((build_ironclad, "IRONCLAD"),
                                         (build_bloodaxe, "BLOODAXE"))):
        y = head + ri * rowH
        _label(sheet, f"PALETTE: {pname}", pad, y - 4, size=16, color=(214, 196, 150))
        xs = _palette_row(build, sheet, y + 18, box, gw)
        for x, name in zip(xs, captions):
            _label(sheet, name, x, y + 18 + box + 4, size=13, color=(190, 194, 210))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(sheet, OUT)
    print("saved", OUT, sheet.get_size())


if __name__ == "__main__":
    main()
