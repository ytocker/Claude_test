import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from draw import draw_hat

pygame.init()

BG = (18, 14, 40)
HEAD = (70, 66, 96)
LABEL = (220, 220, 235)

sizes = [80, 40, 18]
W, H = 520, 320
surf = pygame.Surface((W, H))
surf.fill(BG)

font = pygame.font.SysFont("arial", 16)

# Spread three seats across the row; each gets a faint placeholder head so the
# crown/seat alignment is judged against a real round skull.
slots = [(130, 200), (300, 210), (430, 215)]

for (cx, base_y), hw in zip(slots, sizes):
    r = hw * 0.5
    pygame.draw.circle(surf, HEAD, (cx, int(base_y + r)), int(r))
    draw_hat(surf, cx, base_y, hw, facing=1)
    txt = font.render(f"head_w={hw}", True, LABEL)
    surf.blit(txt, (cx - txt.get_width() // 2, base_y + int(r) + 16))

title = pygame.font.SysFont("arial", 20, bold=True).render(
    "SNAPBACK", True, LABEL
)
surf.blit(title, (20, 16))

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview.png")
pygame.image.save(surf, out)
print("saved", out)
