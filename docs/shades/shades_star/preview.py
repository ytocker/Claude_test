"""Headless preview: STAR SHADES at product size and in-game size."""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame
pygame.init()

from draw import draw_shades

W, H = 520, 320
surf = pygame.Surface((W, H))

# Neutral grey backdrop for the product shot; a darker band for the in-game tile.
surf.fill((118, 122, 128))
pygame.draw.rect(surf, (40, 44, 52), (340, 0, W - 340, H))

font = pygame.font.SysFont("arial", 16, bold=True)

# Product shot, eye_w = 96, on neutral grey.
draw_shades(surf, 170, 150, 96, facing=1)
surf.blit(font.render("eye_w = 96", True, (20, 20, 20)), (120, 270))

# In-game: eye_w = 22 over Pip's scarlet head (~24px radius) with a dark eye dot.
for (px, py) in ((430, 110), (430, 210)):
    pygame.draw.circle(surf, (214, 38, 38), (px, py), 24)          # Pip's head
    pygame.draw.circle(surf, (20, 12, 12), (px + 6, py - 2), 4)    # eye dot
    draw_shades(surf, px + 6, py - 2, 22, facing=1)
surf.blit(font.render("eye_w = 22", True, (235, 235, 235)), (392, 270))

pygame.image.save(surf, os.path.join(os.path.dirname(__file__), "round_1.png"))
print("saved round_1.png")
