import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
from draw import draw_shoe

NAVY = (18, 14, 40)
LABEL = (210, 210, 225)


def main():
    pygame.init()
    # High-tops rise above their box, so reserve vertical headroom per tile.
    sizes = [(120, 72), (48, 30), (16, 11)]
    pad = 28
    headroom = 30
    tile_w = max(w for w, _ in sizes) + pad * 2
    tile_h = max(h for _, h in sizes) + pad + headroom + 22
    canvas = pygame.Surface((tile_w * len(sizes), tile_h))
    canvas.fill(NAVY)

    font = pygame.font.SysFont("arial", 13)

    for i, (w, h) in enumerate(sizes):
        ox = i * tile_w
        # Ground line sits low in the tile; box top leaves room for the collar.
        bx = ox + (tile_w - w) // 2
        by = tile_h - 22 - h
        # Faint ground baseline for context.
        pygame.draw.line(canvas, (40, 34, 70),
                         (ox + pad // 2, by + h),
                         (ox + tile_w - pad // 2, by + h), 1)
        draw_shoe(canvas, bx, by, w, h, facing=1)
        label = font.render(f"{w}x{h}", True, LABEL)
        canvas.blit(label, (ox + (tile_w - label.get_width()) // 2,
                            tile_h - 18))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview.png")
    pygame.image.save(canvas, out)
    print(out)


if __name__ == "__main__":
    main()
