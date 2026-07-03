import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from draw import draw_shoe

NAVY = (18, 14, 40)


def _label(surf, font, text, cx, ty):
    img = font.render(text, True, (210, 214, 230))
    surf.blit(img, (cx - img.get_width() // 2, ty))


def main():
    pygame.init()
    font = pygame.font.SysFont("monospace", 12)

    sizes = [(120, 72), (48, 30), (16, 11)]
    pad = 22
    gap = 30
    label_h = 18

    total_w = pad * 2 + sum(w for w, _ in sizes) + gap * (len(sizes) - 1)
    total_h = pad * 2 + label_h + max(h for _, h in sizes) + 16

    surf = pygame.Surface((total_w, total_h))
    surf.fill(NAVY)

    cx = pad
    base_y = pad + label_h
    row_bottom = base_y + max(h for _, h in sizes)
    for w, h in sizes:
        # ground line a couple px under the tallest so all sit on one floor
        y = row_bottom - h
        draw_shoe(surf, cx, y, w, h, facing=1)
        _label(surf, font, "%dx%d" % (w, h), cx + w // 2, pad)
        cx += w + gap

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview.png")
    pygame.image.save(surf, out)
    print("saved", out)


if __name__ == "__main__":
    main()
