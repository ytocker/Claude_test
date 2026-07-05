"""Render round_1.png for shades_white.

Left: product shot at eye_w=96 on neutral grey.
Right: eye_w=22 over a scarlet-red ~24px circle (Pip's head) with a dark eye
dot, shown native and zoomed. Run headless:
    SDL_VIDEODRIVER=dummy python docs/shades/shades_white/render_sheet.py
"""
import os
import pygame

pygame.init()

from draw import draw_shades  # noqa: E402  (run from this dir)

BG = (32, 36, 52)
GREY = (150, 154, 160)
SCARLET = (208, 38, 34)
EYE = (24, 18, 20)
INK = (236, 240, 250)
SUB = (150, 158, 178)

font = pygame.font.SysFont("dejavusans", 20, bold=True)
small = pygame.font.SysFont("dejavusans", 13)

W, H = 660, 360
sheet = pygame.Surface((W, H))
sheet.fill(BG)
sheet.blit(font.render("Skybit SHADES — WHITE RETRO  ·  Round 1", True, INK),
           (24, 18))
sheet.blit(small.render(
    "Chunky 80s white-plastic frames, smoke amber->rose glass.", True, SUB),
    (24, 46))

# Product shot on neutral grey, eye_w=96.
prect = pygame.Rect(40, 86, 220, 220)
pygame.draw.rect(sheet, GREY, prect, border_radius=10)
draw_shades(sheet, prect.centerx, prect.centery, 96, 1)
sheet.blit(small.render("product  eye_w=96", True, SUB), (prect.x, prect.bottom + 8))

# On-Pip native @22 over a scarlet head circle.
head_c = (360, 196)
pygame.draw.circle(sheet, SCARLET, head_c, 24)
pygame.draw.circle(sheet, EYE, head_c, 3)
draw_shades(sheet, head_c[0], head_c[1], 22, 1)
sheet.blit(small.render("Pip head  eye_w=22 (1x)", True, SUB), (head_c[0] - 40, head_c[1] + 40))

# Zoomed crop of the on-Pip render so the tiny frame reads.
z = 5
crop = pygame.Surface((80, 80), pygame.SRCALPHA)
pygame.draw.circle(crop, SCARLET, (40, 40), 24)
pygame.draw.circle(crop, EYE, (40, 40), 3)
draw_shades(crop, 40, 40, 22, 1)
zoom = pygame.transform.scale(crop, (80 * z, 80 * z))
zrect = pygame.Rect(450, 92, 170, 200)
pygame.draw.rect(sheet, (50, 55, 78), zrect, border_radius=8)
sheet.set_clip(zrect)
zr = zoom.get_rect(center=zrect.center)
sheet.blit(zoom, zr)
sheet.set_clip(None)
pygame.draw.rect(sheet, (70, 76, 100), zrect, width=1, border_radius=8)
sheet.blit(small.render("eye_w=22  (5x)", True, SUB), (zrect.x, zrect.bottom + 8))

out = os.path.join(os.path.dirname(__file__), "round_1.png")
pygame.image.save(sheet, out)
print("wrote", out, sheet.get_size())
