"""Headless preview for the Santa hat — renders draw_hat at three sizes on a
faint grey placeholder head, on dark navy, to docs/hats/santa/preview.png."""
import os
import pathlib

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from draw import draw_hat

NAVY = (18, 14, 40)
HEAD_GREY = (70, 66, 96)
LABEL = (220, 222, 235)

SIZES = [80, 40, 18]


def main():
    pygame.init()
    W, H = 480, 280
    surf = pygame.Surface((W, H))
    surf.fill(NAVY)

    font = pygame.font.SysFont("Arial", 16, bold=True)

    # Evenly spaced columns; each head sits at a shared baseline so the trim
    # lines line up for comparison.
    centers_x = [120, 270, 390]
    base_y = 175

    for head_w, cx in zip(SIZES, centers_x):
        r = head_w / 2
        # Faint grey placeholder head circle (top at base_y).
        pygame.draw.circle(surf, HEAD_GREY, (cx, int(base_y + r)), int(r))
        draw_hat(surf, cx, base_y, head_w, facing=1)
        label = font.render(f"head_w={head_w}", True, LABEL)
        surf.blit(label, label.get_rect(center=(cx, base_y + r + r + 22)))

    title = font.render("SANTA HAT", True, LABEL)
    surf.blit(title, (16, 14))

    out = pathlib.Path(__file__).parent / "preview.png"
    pygame.image.save(surf, str(out))
    print(f"saved {out}")


if __name__ == "__main__":
    main()
