"""Headless preview for the procedural BUCKET HAT.

Renders draw_hat at three head widths on dark navy, each seated on a faint
grey placeholder head-circle, and saves preview.png. Run headless:

    SDL_VIDEODRIVER=dummy python docs/hats/buckethat/preview.py
"""
import os
import pathlib
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from draw import draw_hat  # noqa: E402

NAVY = (18, 14, 40)
HEAD = (70, 66, 92)        # faint grey placeholder head
LABEL = (210, 206, 230)


def main():
    pygame.init()
    W, H = 520, 300
    surf = pygame.Surface((W, H))
    surf.fill(NAVY)
    font = pygame.font.SysFont("sans", 16, bold=True)

    sizes = [80, 40, 18]
    centers = [130, 300, 430]
    base_y = 185

    for head_w, cx in zip(sizes, centers):
        # Faint placeholder head: circle of radius head_w/2 with TOP at base_y.
        r = head_w / 2
        head_cy = base_y + r
        pygame.draw.circle(surf, HEAD, (cx, int(head_cy)), int(r))
        # The hat (caller would add the outer outline in-game; omitted here).
        draw_hat(surf, cx, base_y, head_w, facing=1)
        label = font.render(f"head_w={head_w}", True, LABEL)
        surf.blit(label, label.get_rect(center=(cx, 250)))

    title = font.render("BUCKET HAT", True, LABEL)
    surf.blit(title, title.get_rect(center=(W // 2, 28)))

    out = pathlib.Path(__file__).parent / "preview.png"
    pygame.image.save(surf, str(out))
    print(f"saved {out}")


if __name__ == "__main__":
    main()
