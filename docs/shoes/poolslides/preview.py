import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from draw import draw_shoe

_BG = (18, 14, 40)
_LABEL = (210, 210, 225)


def _tile(label, w, h):
    pad = 16
    surf = pygame.Surface((w + pad * 2, h + pad * 2 + 18))
    surf.fill(_BG)
    draw_shoe(surf, pad, pad, w, h, facing=1)
    font = pygame.font.SysFont("monospace", 12)
    txt = font.render(label, True, _LABEL)
    surf.blit(txt, (pad, h + pad + 4))
    return surf


def main():
    pygame.init()
    sizes = [("120x72", 120, 72), ("48x30", 48, 30), ("16x11", 16, 11)]
    tiles = [_tile(*s) for s in sizes]

    gap = 14
    total_w = sum(t.get_width() for t in tiles) + gap * (len(tiles) + 1)
    total_h = max(t.get_height() for t in tiles) + gap * 2
    sheet = pygame.Surface((total_w, total_h))
    sheet.fill(_BG)

    cxp = gap
    for t in tiles:
        sheet.blit(t, (cxp, gap))
        cxp += t.get_width() + gap

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview.png")
    pygame.image.save(sheet, out)
    print("saved", out)


if __name__ == "__main__":
    main()
