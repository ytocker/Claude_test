"""LOWER-THIRD v3 round-1: full-bleed art, solid bottom band with small rarity color block."""
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
BAND_H  = 36   # info band height (device px)
BLOCK_W = 12   # rarity block spans band height only, NOT full card height

card = pygame.Surface((W, H))
card.fill((10, 10, 20))

# Art: dominant full-bleed
art = build_kitsune(0)
art_h = int(H * 0.90)
art_w = int(art_h * 64 / 84)
art_big = pygame.transform.smoothscale(art, (art_w, art_h))
art_x = (W - art_w) // 2
art_y = (H - BAND_H - art_h) // 2
card.blit(art_big, (art_x, art_y))

# Info band
band_y = H - BAND_H
pygame.draw.rect(card, (14, 12, 22), (0, band_y, W, BAND_H))
pygame.draw.line(card, GEM, (0, band_y), (W, band_y), 1)
# Rarity color block — anchored to band, not full card height (differs from MARQUEE STRIPE)
pygame.draw.rect(card, GEM, (0, band_y + 1, BLOCK_W, BAND_H - 1))

fnt_name  = pygame.font.SysFont("DejaVu Sans", 18, bold=True)
fnt_price = pygame.font.SysFont("DejaVu Sans", 16, bold=True)
name_s  = fnt_name.render("KITSUNE", True, (255, 255, 255))
price_s = fnt_price.render("3 500", True, GEM)
ty = band_y + (BAND_H - name_s.get_height()) // 2
card.blit(name_s,  (BLOCK_W + 8, ty))
card.blit(price_s, (W - price_s.get_width() - 8,
                     ty + (name_s.get_height() - price_s.get_height()) // 2))

# 16px rounded corners
corners = pygame.Surface((W, H), pygame.SRCALPHA)
corners.fill((0, 0, 0, 0))
pygame.draw.rect(corners, (255, 255, 255, 255), (0, 0, W, H), border_radius=16)
card.blit(corners, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

os.makedirs("docs/item_card_redesign_v3/lower-third", exist_ok=True)
pygame.image.save(card, "docs/item_card_redesign_v3/lower-third/round_1.png")

from PIL import Image
img = Image.open("docs/item_card_redesign_v3/lower-third/round_1.png")
w, h = img.size
distinct = len(set(img.getdata()))
sz = os.path.getsize("docs/item_card_redesign_v3/lower-third/round_1.png")
print(f"PIL: {w}x{h}, {distinct} distinct, {sz} bytes")
assert w == 324 and h == 200
assert distinct > 200
print("validation OK")
