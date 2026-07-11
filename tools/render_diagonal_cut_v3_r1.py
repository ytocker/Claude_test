"""DIAGONAL-CUT v3 round-1: lower-right info wedge filled with rarity color."""
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

# Lower-right info wedge — the diagonal edge IS the rarity signal (color varies by tier)
info_pts = [(int(W * 0.28), H), (W, int(H * 0.40)), (W, H)]
pygame.draw.polygon(card, DEEP, info_pts)

# Art: kitsune dominant, centered in the upper-left zone
art = build_kitsune(0)
art_h = int(H * 0.86)
art_w = int(art_h * 64 / 84)
art_big = pygame.transform.smoothscale(art, (art_w, art_h))
art_x = (int(W * 0.62) - art_w) // 2
art_y = (H - art_h) // 2
card.blit(art_big, (art_x, art_y))

# Name in the info wedge with drop shadow for contrast on DEEP
fnt = pygame.font.SysFont("DejaVu Sans", 20, bold=True)
shadow = (0, 0, 0)
name_s  = fnt.render("KITSUNE", True, (255, 255, 255))
name_sh = fnt.render("KITSUNE", True, shadow)
nx, ny = int(W * 0.52), int(H * 0.57)
card.blit(name_sh, (nx + 2, ny + 2))
card.blit(name_s,  (nx, ny))

fnt2 = pygame.font.SysFont("DejaVu Sans", 16, bold=True)
price_s  = fnt2.render("3 500", True, GEM)
price_sh = fnt2.render("3 500", True, shadow)
px, py = nx, ny + name_s.get_height() + 6
card.blit(price_sh, (px + 2, py + 2))
card.blit(price_s,  (px, py))

# 16px rounded corners
corners = pygame.Surface((W, H), pygame.SRCALPHA)
corners.fill((0, 0, 0, 0))
pygame.draw.rect(corners, (255, 255, 255, 255), (0, 0, W, H), border_radius=16)
card.blit(corners, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

os.makedirs("docs/item_card_redesign_v3/diagonal-cut", exist_ok=True)
pygame.image.save(card, "docs/item_card_redesign_v3/diagonal-cut/round_1.png")

from PIL import Image
img = Image.open("docs/item_card_redesign_v3/diagonal-cut/round_1.png")
w, h = img.size
distinct = len(set(img.getdata()))
sz = os.path.getsize("docs/item_card_redesign_v3/diagonal-cut/round_1.png")
print(f"PIL: {w}x{h}, {distinct} distinct, {sz} bytes")
assert w == 324 and h == 200
assert distinct > 200
print("validation OK")
