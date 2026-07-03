"""Headless preview: NY CAP at three sizes, each seated on a faint grey
placeholder head-circle, on a dark-navy field. Run with SDL_VIDEODRIVER=dummy."""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
from draw import draw_hat

pygame.init()

BG   = (18, 14, 40)
HEAD = (70, 72, 96)
TEXT = (210, 214, 230)

SIZES = [80, 40, 18]
PAD   = 60
W = PAD * (len(SIZES) + 1) + sum(s * 2 for s in SIZES) + 120
H = 320

surf = pygame.Surface((W, H))
surf.fill(BG)
font = pygame.font.SysFont("Arial", 16, bold=True)

# Lay the heads on a common baseline so the cap brims line up.
base_y = H * 0.62
x = PAD + 60
for head_w in SIZES:
    cx = x + head_w
    r = head_w / 2
    # Faint placeholder head: top of circle at base_y.
    head_cy = base_y + r
    pygame.draw.circle(surf, HEAD, (int(cx), int(head_cy)), int(r))

    draw_hat(surf, cx, base_y, head_w, facing=1)

    label = font.render(f"head_w={head_w}", True, TEXT)
    surf.blit(label, (int(cx - label.get_width() / 2), int(base_y + r * 2 + 16)))

    x += head_w * 2 + PAD + 40

title = font.render("NY CAP — navy crown + white interlocking serif NY (facing=1)", True, TEXT)
surf.blit(title, (PAD, 20))

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview.png")
pygame.image.save(surf, out)
print("saved", out)
