import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
from draw import draw_hat

pygame.init()

NAVY = (18, 14, 40)
HEAD = (70, 70, 86)
TEXT = (210, 210, 220)

W, H = 520, 320
surf = pygame.Surface((W, H))
surf.fill(NAVY)

font = pygame.font.SysFont("dejavusans", 16)
title = pygame.font.SysFont("dejavusans", 20, bold=True)
surf.blit(title.render("BEANIE", True, TEXT), (20, 16))

sizes = [80, 40, 18]
slots = [130, 290, 420]
base_y = 200

for head_w, sx in zip(sizes, slots):
    r = head_w / 2
    # Faint placeholder head so the seating reads clearly.
    pygame.draw.circle(surf, HEAD, (sx, int(base_y + r)), int(r))
    draw_hat(surf, sx, base_y, head_w, facing=1)
    label = font.render(f"head_w={head_w}", True, TEXT)
    surf.blit(label, (sx - label.get_width() // 2, base_y + int(r) + 24))

out = os.path.join(os.path.dirname(__file__), "preview.png")
pygame.image.save(surf, out)
print("saved", out)
