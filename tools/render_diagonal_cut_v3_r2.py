"""DIAGONAL-CUT v3 round-2: GEM rim along diagonal for legendary read, name fully in dark zone, transparent corners."""
import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))
from game.animal_kitsune import build_kitsune

W, H = 324, 200
GEM  = (255, 202, 104)
GLOW = (255, 168,  58)
DEEP = (150,  92,  22)

card = pygame.Surface((W, H))
card.fill((10, 8, 18))

# Lower-right info wedge — DEEP fill
info_pts = [(int(W * 0.28), H), (W, int(H * 0.40)), (W, H)]
pygame.draw.polygon(card, DEEP, info_pts)

# GEM rim-light along the diagonal edge — the legendary cue that survives downscale
pygame.draw.line(card, GEM, (int(W * 0.28), H), (W, int(H * 0.40)), 3)
# Inner glow line
pygame.draw.line(card, GLOW, (int(W * 0.28) + 2, H - 1), (W - 1, int(H * 0.40) + 2), 1)

# Art: kitsune dominant, constrained to left dark zone so it clears the diagonal
art = build_kitsune(0)
art_h = int(H * 0.86)
art_w = int(art_h * 64 / 84)
art_big = pygame.transform.smoothscale(art, (art_w, art_h))
art_x = (int(W * 0.55) - art_w) // 2
art_y = (H - art_h) // 2
card.blit(art_big, (art_x, art_y))

# Name: anchored well into the dark base, no glyph crossing the diagonal
# At x=int(W*0.44)=142, diagonal y ≈ 80 + 120*(142-324)/(90-324) ≈ 80+93 = 173 — name top at 50% = 100, safely above 173
fnt = pygame.font.SysFont("DejaVu Sans", 20, bold=True)
nx, ny = int(W * 0.44), int(H * 0.50)
name_s = fnt.render("KITSUNE", True, (255, 255, 255))
# 2px soft outline for legibility against any background
for ox, oy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
    card.blit(fnt.render("KITSUNE", True, (0, 0, 0)), (nx + ox, ny + oy))
card.blit(name_s, (nx, ny))

# Price: 18pt, same zone, below name
fnt2 = pygame.font.SysFont("DejaVu Sans", 18, bold=True)
price_s = fnt2.render("3 500", True, GEM)
px, py = nx, ny + name_s.get_height() + 6
for ox, oy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
    card.blit(fnt2.render("3 500", True, (0, 0, 0)), (px + ox, py + oy))
card.blit(price_s, (px, py))

# Transparent corners: copy to SRCALPHA then apply rounded mask
card_alpha = pygame.Surface((W, H), pygame.SRCALPHA)
card_alpha.blit(card, (0, 0))
corners = pygame.Surface((W, H), pygame.SRCALPHA)
corners.fill((0, 0, 0, 0))
pygame.draw.rect(corners, (255, 255, 255, 255), (0, 0, W, H), border_radius=16)
card_alpha.blit(corners, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

os.makedirs("docs/item_card_redesign_v3/diagonal-cut", exist_ok=True)
pygame.image.save(card_alpha, "docs/item_card_redesign_v3/diagonal-cut/round_2.png")

from PIL import Image
img = Image.open("docs/item_card_redesign_v3/diagonal-cut/round_2.png")
w, h = img.size
distinct = len(set(img.getdata()))
sz = os.path.getsize("docs/item_card_redesign_v3/diagonal-cut/round_2.png")
print(f"PIL: {w}x{h}, {distinct} distinct, {sz} bytes")
assert w == 324 and h == 200
assert distinct > 200
print("validation OK")
