import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from draw import draw_shoe

BG = (18, 14, 40)
LABEL = (210, 214, 230)


def _tile(label, w, h):
    pad_x, pad_top, pad_bot = 16, 24, 16
    surf = pygame.Surface((w + pad_x * 2, h + pad_top + pad_bot), pygame.SRCALPHA)
    surf.fill(BG)
    draw_shoe(surf, pad_x, pad_top, w, h, facing=1)
    font = pygame.font.SysFont("dejavusans", 12)
    txt = font.render(label, True, LABEL)
    surf.blit(txt, ((surf.get_width() - txt.get_width()) // 2, surf.get_height() - 14))
    return surf


def main():
    pygame.init()
    sizes = [("120x72", 120, 72), ("48x30", 48, 30), ("16x11", 16, 11)]
    tiles = [_tile(*s) for s in sizes]

    gap = 20
    total_w = sum(t.get_width() for t in tiles) + gap * (len(tiles) + 1)
    total_h = max(t.get_height() for t in tiles) + gap * 2
    sheet = pygame.Surface((total_w, total_h))
    sheet.fill(BG)

    cx = gap
    for t in tiles:
        sheet.blit(t, (cx, (total_h - t.get_height()) // 2))
        cx += t.get_width() + gap

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview.png")
    pygame.image.save(sheet, out)
    print("saved", out)


if __name__ == "__main__":
    main()
