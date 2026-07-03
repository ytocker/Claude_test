"""Headless preview for the procedural grad cap.

Renders draw_hat at three sizes on a dark-navy field, each seated on a faint
grey placeholder head-circle, and writes preview.png.

Run: SDL_VIDEODRIVER=dummy python docs/hats/gradcap/preview.py
"""
import os
import sys
import pathlib

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from draw import draw_hat  # noqa: E402

NAVY  = (18, 14, 40)
HEAD  = (60, 58, 78)
LABEL = (200, 196, 220)

SIZES = [80, 40, 18]


def main():
    pygame.init()
    W, H = 560, 360
    surf = pygame.Surface((W, H))
    surf.fill(NAVY)

    font = pygame.font.SysFont("sans", 16, bold=True)

    # Three product shots in a row, baseline-aligned for an honest size compare.
    centres = [150, 320, 460]
    base_y = 230

    for head_w, cx in zip(SIZES, centres):
        r = head_w / 2
        # Faint placeholder head: circle whose TOP sits at base_y.
        pygame.draw.circle(surf, HEAD, (cx, int(base_y + r)), int(r))
        draw_hat(surf, cx, base_y, head_w, facing=1)

        lbl = font.render(f"head_w = {head_w}", True, LABEL)
        surf.blit(lbl, lbl.get_rect(center=(cx, base_y + head_w + 36)))

    title = font.render("GRAD CAP  -  procedural store hat (facing +1)",
                        True, LABEL)
    surf.blit(title, (20, 18))

    out = pathlib.Path(__file__).parent / "preview.png"
    pygame.image.save(surf, str(out))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
