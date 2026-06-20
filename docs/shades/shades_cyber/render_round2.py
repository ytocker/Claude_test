"""Render round_2.png for shades_cyber: product @96 on dark grey + @22 on Pip.

Headless (SDL dummy) so it runs in CI/agents. The 22px-over-scarlet cells
are the decisive read — the rework lives or dies on whether the dark wedge
+ cyan edge-light hold there, so they get native + multiple zooms.
"""
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, "/home/user/skybit/docs/shades/shades_cyber")

import pygame  # noqa: E402
pygame.init()
pygame.font.init()
from draw import draw_shades  # noqa: E402

BG = (40, 44, 54)
W, H = 880, 520
sheet = pygame.Surface((W, H))
sheet.fill(BG)

font = pygame.font.SysFont("DejaVuSans", 20, bold=True)
small = pygame.font.SysFont("DejaVuSans", 14)
sheet.blit(font.render("Skybit SHADES — shades_cyber (CYBER VISOR)  ROUND 2",
                       True, (235, 240, 250)), (16, 14))
sheet.blit(small.render("dark wedge mass + cyan bottom edge-light (value sandwich)",
                        True, (170, 200, 215)), (16, 40))

# --- Product shot @ eye_w=96 on a dark-grey card -----------------------------
CARD = 280
card = pygame.Surface((CARD, CARD))
card.fill((52, 56, 68))
pygame.draw.rect(card, (84, 90, 108), card.get_rect(), 3)
draw_shades(card, CARD // 2, CARD // 2, 96, 1)
sheet.blit(card, (32, 70))
sheet.blit(small.render("product  eye_w=96  facing=1", True, (235, 240, 250)),
           (32, 70 + CARD + 8))

# Mirror to confirm facing flips cleanly.
card2 = pygame.Surface((CARD // 2, CARD // 2))
card2.fill((52, 56, 68))
pygame.draw.rect(card2, (84, 90, 108), card2.get_rect(), 2)
draw_shades(card2, CARD // 4, CARD // 4, 48, -1)
sheet.blit(card2, (32, 70 + CARD + 30))
sheet.blit(small.render("facing=-1", True, (235, 240, 250)),
           (32 + CARD // 2 + 10, 70 + CARD + 30 + 50))


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
px = 360
sheet.blit(small.render("in-game  eye_w=22 over ~24px scarlet head",
                        True, (235, 240, 250)), (px, 70))

sheet.blit(pip, (px + 40, 96))
sheet.blit(small.render("native", True, (235, 240, 250)), (px + 44, 96 + 60))

z4 = pygame.transform.scale(pip, (pip.get_width() * 4, pip.get_height() * 4))
sheet.blit(z4, (px, 180))
sheet.blit(small.render("x4 zoom", True, (235, 240, 250)),
           (px, 180 + z4.get_height() + 2))

z6 = pygame.transform.scale(pip, (pip.get_width() * 6, pip.get_height() * 6))
sheet.blit(z6, (px + 250, 180))
sheet.blit(small.render("x6 zoom (judge the value sandwich here)",
                        True, (235, 240, 250)), (px + 250, 180 + z6.get_height() + 2))

OUT = "/home/user/skybit/docs/shades/shades_cyber/round_2.png"
pygame.image.save(sheet, OUT)
print("wrote", OUT, sheet.get_size())
