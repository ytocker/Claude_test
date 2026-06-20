import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
from draw import draw_hat

pygame.init()

NAVY = (18, 14, 40)
HEAD = (70, 66, 92)
LABEL = (210, 214, 230)

sizes = [80, 40, 18]
W, H = 520, 260
surf = pygame.Surface((W, H))
surf.fill(NAVY)

font = pygame.font.SysFont("sans", 16)

# Even horizontal spacing; each head seated so its open top is visible.
xs = [120, 290, 430]
baseline = 150

for head_w, cx in zip(sizes, xs):
    r = head_w * 0.5
    head_cy = baseline + r
    # Faint placeholder head circle (top at baseline) so the open visor top reads.
    pygame.draw.circle(surf, HEAD, (cx, int(head_cy)), int(r))
    draw_hat(surf, cx, baseline, head_w, facing=1)
    lbl = font.render(f"head_w={head_w}", True, LABEL)
    surf.blit(lbl, (cx - lbl.get_width() // 2, baseline + head_w + 18))

title = font.render("VISOR", True, (255, 255, 255))
surf.blit(title, (16, 14))

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview.png")
pygame.image.save(surf, out)
print("saved", out)
