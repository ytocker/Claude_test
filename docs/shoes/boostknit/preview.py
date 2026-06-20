import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from draw import draw_shoe

_NAVY = (18, 14, 40)
_LABEL = (220, 216, 235)


def _tile(surf, font, label, bw, bh, ox, oy):
    """Render one shoe in a padded, labelled cell on the navy sheet."""
    pad = 14
    pygame.draw.rect(surf, (30, 24, 58), (ox, oy, bw + pad * 2, bh + pad * 2 + 16))
    draw_shoe(surf, ox + pad, oy + pad, bw, bh, facing=1)
    txt = font.render(label, True, _LABEL)
    surf.blit(txt, (ox + pad, oy + pad + bh + 4))


def main():
    pygame.init()
    sizes = [("120x72", 120, 72), ("48x30", 48, 30), ("16x11", 16, 11)]
    font = pygame.font.SysFont("monospace", 12)

    W, H = 360, 140
    sheet = pygame.Surface((W, H))
    sheet.fill(_NAVY)

    ox = 16
    for label, bw, bh in sizes:
        _tile(sheet, font, label, bw, bh, ox, 24)
        ox += bw + 48

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview.png")
    pygame.image.save(sheet, out)
    print(out)


if __name__ == "__main__":
    main()
