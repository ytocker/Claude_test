import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from draw import draw_shoe

_NAVY = (18, 14, 40)


def _label(surf, font, text, cx, y):
    img = font.render(text, True, (210, 210, 220))
    surf.blit(img, (cx - img.get_width() // 2, y))


def main():
    pygame.init()
    pygame.font.init()
    font = pygame.font.SysFont("monospace", 12)

    sizes = [(120, 72), (48, 30), (16, 11)]
    pad = 28
    cell_w = max(w for w, _ in sizes) + 40
    surf = pygame.Surface((cell_w * len(sizes), 150))
    surf.fill(_NAVY)

    cx = cell_w // 2
    for (w, h) in sizes:
        bx = cx - w // 2
        by = 50
        # Faint box so we can see fit within the spec box at each scale.
        pygame.draw.rect(surf, (40, 34, 70), (bx, by, w, h), 1)
        draw_shoe(surf, bx, by, w, h, facing=1)
        # House outline approximation the caller would add, to sanity-check fit.
        _label(surf, font, f"{w}x{h}", cx, by + max(h, 34) + 14)
        cx += cell_w

    # One mirrored thumbnail to confirm facing=-1 symmetry.
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview.png")
    pygame.image.save(surf, out)
    print("saved", out)


if __name__ == "__main__":
    main()
