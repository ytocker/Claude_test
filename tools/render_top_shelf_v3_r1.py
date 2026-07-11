"""TOP-SHELF v3 round-1: prominent rarity-colored shelf at top carries item name."""
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
SHELF_H = 56  # device px — name lives here, not a thin strip

card = pygame.Surface((W, H))
card.fill((10, 8, 18))

# Shelf: solid rarity fill — eye lands on name first, tier reads from shelf color
pygame.draw.rect(card, DEEP, (0, 0, W, SHELF_H))

fnt_name = pygame.font.SysFont("DejaVu Sans", 26, bold=True)
name_s = fnt_name.render("KITSUNE", True, (255, 255, 255))
card.blit(name_s, (12, (SHELF_H - name_s.get_height()) // 2))

# Diamond pip top-right of shelf — secondary rarity token
pip_cx, pip_cy = W - 22, SHELF_H // 2
pip_r = 9
pts = [(pip_cx, pip_cy - pip_r), (pip_cx + pip_r, pip_cy),
       (pip_cx, pip_cy + pip_r), (pip_cx - pip_r, pip_cy)]
pygame.draw.polygon(card, GEM, pts)
pygame.draw.polygon(card, (100, 60, 10), pts, 1)

# Art below shelf: kitsune dominant
art = build_kitsune(0)
art_h = int((H - SHELF_H) * 0.90)
art_w = int(art_h * 64 / 84)
art_big = pygame.transform.smoothscale(art, (art_w, art_h))
art_x = (W - art_w) // 2
art_y = SHELF_H + ((H - SHELF_H) - art_h) // 2
card.blit(art_big, (art_x, art_y))

# Price chip: bottom-right over art
fnt_price = pygame.font.SysFont("DejaVu Sans", 16, bold=True)
price_s = fnt_price.render("3 500", True, GEM)
pad = 6
chip_w = price_s.get_width() + pad * 2
chip_h = price_s.get_height() + pad
chip_x = W - chip_w - 8
chip_y = H - chip_h - 8
chip_surf = pygame.Surface((chip_w, chip_h), pygame.SRCALPHA)
pygame.draw.rect(chip_surf, (14, 12, 22, 220), (0, 0, chip_w, chip_h), border_radius=4)
chip_surf.blit(price_s, (pad, pad // 2))
card.blit(chip_surf, (chip_x, chip_y))

# 16px rounded corners
corners = pygame.Surface((W, H), pygame.SRCALPHA)
corners.fill((0, 0, 0, 0))
pygame.draw.rect(corners, (255, 255, 255, 255), (0, 0, W, H), border_radius=16)
card.blit(corners, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

os.makedirs("docs/item_card_redesign_v3/top-shelf", exist_ok=True)
pygame.image.save(card, "docs/item_card_redesign_v3/top-shelf/round_1.png")

from PIL import Image
img = Image.open("docs/item_card_redesign_v3/top-shelf/round_1.png")
w, h = img.size
distinct = len(set(img.getdata()))
sz = os.path.getsize("docs/item_card_redesign_v3/top-shelf/round_1.png")
print(f"PIL: {w}x{h}, {distinct} distinct, {sz} bytes")
assert w == 324 and h == 200
assert distinct > 200
print("validation OK")
