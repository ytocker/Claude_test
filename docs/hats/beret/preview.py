import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
from draw import draw_hat

pygame.init()

BG = (18, 14, 40)
HEAD = (70, 66, 92)
LABEL = (210, 206, 230)

W, H = 520, 320
surf = pygame.Surface((W, H))
surf.fill(BG)

font = pygame.font.SysFont("dejavusans", 16)

# Three sizes across a row; band line seated low enough to show the full crown.
sizes = [80, 40, 18]
slots = [W * 0.25, W * 0.55, W * 0.80]
base_y = 200

for head_w, sx in zip(sizes, slots):
    r = head_w / 2
    cx = int(sx)
    # Faint grey placeholder head; top at base_y so the band wraps the crown.
    pygame.draw.circle(surf, HEAD, (cx, int(base_y + r)), int(r))
    draw_hat(surf, cx, base_y, head_w, facing=1)
    txt = font.render(f"head_w={head_w}", True, LABEL)
    surf.blit(txt, (cx - txt.get_width() // 2, int(base_y + r + 28)))

title = font.render("BERET", True, LABEL)
surf.blit(title, (16, 16))

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview.png")
pygame.image.save(surf, out)
print("saved", out)
