import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from draw import draw_hat

pygame.init()

_BG = (18, 14, 40)
_HEAD = (78, 74, 96)
_LABEL = (220, 220, 230)


def _seat(surf, font, head_w, slot_cx, label_y, base_y):
    r = head_w / 2
    # Faint placeholder head so the cap is shown actually worn.
    pygame.draw.circle(surf, _HEAD, (int(slot_cx), int(base_y + r)), int(r))
    draw_hat(surf, slot_cx, base_y, head_w, facing=1)
    label = font.render(f"head_w = {head_w}", True, _LABEL)
    surf.blit(label, (slot_cx - label.get_width() // 2, label_y))


def main():
    W, H = 520, 320
    surf = pygame.Surface((W, H))
    surf.fill(_BG)
    font = pygame.font.SysFont("dejavusans", 16)

    sizes = [80, 40, 18]
    slots = [W * 0.25, W * 0.55, W * 0.82]
    base_y = 170  # crown-top baseline shared across the row

    for head_w, scx in zip(sizes, slots):
        _seat(surf, font, head_w, scx, H - 40, base_y)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview.png")
    pygame.image.save(surf, out)
    print("saved", out)


if __name__ == "__main__":
    main()
