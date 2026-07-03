import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from draw import draw_hat


_BG = (18, 14, 40)
_HEAD = (70, 66, 92)
_LABEL = (220, 218, 235)


def _seat(surf, cx, base_y, head_w, label, font):
    # Faint placeholder head so the cone's seating on a round crown is legible.
    r = head_w / 2
    pygame.draw.circle(surf, _HEAD, (int(cx), int(base_y + r)), int(r))
    draw_hat(surf, cx, base_y, head_w)
    txt = font.render(label, True, _LABEL)
    surf.blit(txt, (int(cx - txt.get_width() / 2), int(base_y + head_w + 10)))


def main():
    pygame.init()
    W, H = 560, 360
    surf = pygame.Surface((W, H))
    surf.fill(_BG)
    font = pygame.font.SysFont("Arial", 16)

    # Tall canvas: the cone tip rises ~1.4x head_w above base_y, so push base_y
    # low and give the largest hat plenty of headroom.
    base_y = 250
    cols = [(140, 80), (320, 40), (460, 18)]
    for cx, hw in cols:
        _seat(surf, cx, base_y, hw, f"head_w={hw}", font)

    title = font.render("PARTY HAT", True, _LABEL)
    surf.blit(title, (16, 12))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview.png")
    pygame.image.save(surf, out)
    print("saved", out)


if __name__ == "__main__":
    main()
