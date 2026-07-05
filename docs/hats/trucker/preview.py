import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pathlib
import pygame

from draw import draw_hat

NAVY = (18, 14, 40)
HEAD = (70, 66, 92)         # faint grey placeholder head
HEAD_HI = (88, 84, 112)
LABEL = (210, 214, 230)


def main():
    pygame.init()
    pygame.font.init()

    sizes = [80, 40, 18]
    pad = 50
    cell_w = 170
    W = pad + cell_w * len(sizes) + pad
    H = 230
    surf = pygame.Surface((W, H))
    surf.fill(NAVY)

    font = pygame.font.SysFont("sans", 16, bold=True)

    base_y = 150
    for i, head_w in enumerate(sizes):
        cx = pad + cell_w * i + cell_w // 2
        r = head_w / 2

        # Faint placeholder head — radius head_w/2, top at base_y.
        pygame.draw.circle(surf, HEAD, (cx, int(base_y + r)), int(r))
        pygame.draw.circle(surf, HEAD_HI, (cx, int(base_y + r)), int(r), 1)

        draw_hat(surf, cx, base_y, head_w, facing=1)

        lbl = font.render(f"head_w = {head_w}", True, LABEL)
        surf.blit(lbl, lbl.get_rect(center=(cx, H - 22)))

    out = pathlib.Path(__file__).parent / "preview.png"
    pygame.image.save(surf, str(out))
    print(f"saved {out}")


if __name__ == "__main__":
    main()
