"""Render round_1.png for shades_black: product shot @96 + in-game @22 on Pip."""
import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, "/home/user/skybit/docs/shades/shades_black")

import pygame
pygame.init()
pygame.font.init()
from draw import draw_shades

BG = (118, 124, 140)
W, H = 800, 460
sheet = pygame.Surface((W, H))
sheet.fill(BG)

font = pygame.font.SysFont("DejaVuSans", 20, bold=True)
small = pygame.font.SysFont("DejaVuSans", 14)
sheet.blit(font.render("Skybit SHADES — shades_black (wayfarer)  ROUND 1",
                       True, (255, 255, 255)), (16, 14))

# --- Product shot @ eye_w=96 on a neutral grey card --------------------------
CARD = 280
card = pygame.Surface((CARD, CARD))
card.fill((150, 154, 166))
pygame.draw.rect(card, (96, 100, 112), card.get_rect(), 3)
draw_shades(card, CARD // 2, CARD // 2, 96, 1)
sheet.blit(card, (40, 70))
sheet.blit(small.render("product  eye_w=96  facing=1", True, (245, 245, 245)),
           (40, 70 + CARD + 8))

# Mirror to confirm facing flips cleanly.
card2 = pygame.Surface((CARD, CARD))
card2.fill((150, 154, 166))
pygame.draw.rect(card2, (96, 100, 112), card2.get_rect(), 3)
draw_shades(card2, CARD // 2, CARD // 2, 96, -1)
sheet.blit(pygame.transform.scale(card2, (CARD // 2, CARD // 2)), (40, 360))
sheet.blit(small.render("facing=-1", True, (245, 245, 245)), (40, 360 + 142))


def pip_head(eye_w):
    """Simple scarlet head (~24px) with a dark eye dot, shades over the eye."""
    s = 56
    surf = pygame.Surface((s, s), pygame.SRCALPHA)
    cx, cy = s // 2, s // 2
    pygame.draw.circle(surf, (224, 48, 52), (cx, cy), 24)        # scarlet head
    pygame.draw.circle(surf, (170, 28, 34), (cx, cy), 24, 2)     # rim shade
    pygame.draw.circle(surf, (20, 18, 22), (cx + 4, cy - 2), 3)  # eye dot
    draw_shades(surf, cx + 4, cy - 2, eye_w, 1)
    return surf


# --- In-game read @ eye_w=22 over Pip's head ---------------------------------
pip = pip_head(22)
px = 380
sheet.blit(pip, (px + 60, 90))
sheet.blit(small.render("in-game  eye_w=22  (native size)", True, (245, 245, 245)),
           (px, 160))

for k, label, y in ((4, "x4 zoom", 200), (8, "x8 zoom", 200)):
    pass
z4 = pygame.transform.scale(pip, (pip.get_width() * 4, pip.get_height() * 4))
sheet.blit(z4, (px, 190))
sheet.blit(small.render("x4 zoom", True, (245, 245, 245)), (px, 190 + z4.get_height() + 2))

z8 = pygame.transform.scale(pip, (pip.get_width() * 5, pip.get_height() * 5))
sheet.blit(z8, (px + 240, 190))
sheet.blit(small.render("x5 zoom", True, (245, 245, 245)), (px + 240, 190 + z8.get_height() + 2))

OUT = "/home/user/skybit/docs/shades/shades_black/round_1.png"
pygame.image.save(sheet, OUT)
print("wrote", OUT, sheet.get_size())
