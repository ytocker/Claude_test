import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
from draw import draw_hat

pygame.init()

NAVY = (18, 14, 40)
HEAD = (70, 66, 96)
TEXT = (210, 214, 230)

W, H = 520, 460
surf = pygame.Surface((W, H))
surf.fill(NAVY)

font = pygame.font.SysFont("sans", 16)

sizes = [80, 40, 18]
# Spread the three columns; baseline low so the tall toque has headroom.
centers = [120, 290, 430]
base_y = 360

for head_w, cx in zip(sizes, centers):
    r = head_w / 2
    # Faint placeholder head: a circle whose top sits at base_y.
    pygame.draw.circle(surf, HEAD, (cx, int(base_y + r)), int(r))
    draw_hat(surf, cx, base_y, head_w, facing=1)
    label = font.render(f"head_w={head_w}", True, TEXT)
    surf.blit(label, (cx - label.get_width() // 2, base_y + head_w + 30))

title = font.render("CHEF TOQUE", True, (255, 255, 255))
surf.blit(title, (20, 20))

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview.png")
pygame.image.save(surf, out)
print("saved", out)
