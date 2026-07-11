"""STAMP v3 round-1: art in a postage-stamp inset with perforated rarity border."""
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
card.fill((12, 10, 18))

INSET = 28
MARGIN_BOTTOM = 48
stamp_x = INSET
stamp_y = INSET
stamp_w = W - INSET * 2
stamp_h = H - INSET - MARGIN_BOTTOM  # 124 px

# Art inside the stamp frame
art = build_kitsune(0)
art_h = int(stamp_h * 0.92)
art_w = int(art_h * 64 / 84)
art_big = pygame.transform.smoothscale(art, (art_w, art_h))
card.blit(art_big, (stamp_x + (stamp_w - art_w) // 2,
                     stamp_y + (stamp_h - art_h) // 2))

# Perforated border: GEM gold dots along all 4 stamp edges — border IS the rarity indicator
DOT_R, DOT_GAP = 5, 12
sx0, sy0 = stamp_x, stamp_y
sx1, sy1 = stamp_x + stamp_w, stamp_y + stamp_h

cx = sx0
while cx <= sx1:
    pygame.draw.circle(card, GEM, (cx, sy0), DOT_R)
    pygame.draw.circle(card, GEM, (cx, sy1), DOT_R)
    cx += DOT_GAP
cy = sy0 + DOT_GAP
while cy < sy1:
    pygame.draw.circle(card, GEM, (sx0, cy), DOT_R)
    pygame.draw.circle(card, GEM, (sx1, cy), DOT_R)
    cy += DOT_GAP

# Name and price centered below the stamp
fnt_name  = pygame.font.SysFont("DejaVu Sans", 20, bold=True)
fnt_price = pygame.font.SysFont("DejaVu Sans", 16, bold=True)
name_s  = fnt_name.render("KITSUNE", True, (255, 255, 255))
price_s = fnt_price.render("3 500", True, GEM)
ty = sy1 + 8
card.blit(name_s,  ((W - name_s.get_width()) // 2, ty))
card.blit(price_s, ((W - price_s.get_width()) // 2, ty + name_s.get_height() + 4))

# 16px rounded corners
corners = pygame.Surface((W, H), pygame.SRCALPHA)
corners.fill((0, 0, 0, 0))
pygame.draw.rect(corners, (255, 255, 255, 255), (0, 0, W, H), border_radius=16)
card.blit(corners, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

os.makedirs("docs/item_card_redesign_v3/stamp", exist_ok=True)
pygame.image.save(card, "docs/item_card_redesign_v3/stamp/round_1.png")

from PIL import Image
img = Image.open("docs/item_card_redesign_v3/stamp/round_1.png")
w, h = img.size
distinct = len(set(img.getdata()))
sz = os.path.getsize("docs/item_card_redesign_v3/stamp/round_1.png")
print(f"PIL: {w}x{h}, {distinct} distinct, {sz} bytes")
assert w == 324 and h == 200
assert distinct > 200
print("validation OK")
