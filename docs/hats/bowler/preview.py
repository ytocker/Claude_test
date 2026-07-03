import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from draw import draw_hat

NAVY = (18, 14, 40)
HEAD = (70, 66, 92)
LABEL = (210, 206, 230)


def main():
    pygame.init()
    W, H = 560, 320
    surf = pygame.Surface((W, H))
    surf.fill(NAVY)

    font = pygame.font.SysFont("dejavusans", 16)

    sizes = [80, 40, 18]
    slot_w = W // len(sizes)
    base_y = 200

    for i, head_w in enumerate(sizes):
        cx = slot_w * i + slot_w // 2

        # Faint placeholder head: circle of radius head_w/2 with its top at base_y.
        r = head_w / 2.0
        head_cy = base_y + r
        pygame.draw.circle(surf, HEAD, (int(cx), int(head_cy)), int(r), 1)

        draw_hat(surf, cx, base_y, head_w, facing=1)

        label = font.render(f"head_w={head_w}", True, LABEL)
        surf.blit(label, (cx - label.get_width() // 2, 270))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview.png")
    pygame.image.save(surf, out)
    print("saved", out)


if __name__ == "__main__":
    main()
