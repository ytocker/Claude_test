"""LOWER-THIRD v3 round-2: wider rarity block, thicker rule, larger name, bigger art, transparent corners."""
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
BAND_H  = 32   # trimmed to give art zone 2 more device px
BLOCK_W = 24   # tripled (12 logical) so rarity block survives thumbnail downscale

card = pygame.Surface((W, H))
card.fill((10, 10, 20))

# Art: scaled to fill more of the art zone; centered in zone (not full H)
art_zone_h = H - BAND_H  # 168 device
art = build_kitsune(0)
art_h = int(art_zone_h * 0.95)  # 159 — pushes character to edges of art zone
art_w = int(art_h * 64 / 84)
art_big = pygame.transform.smoothscale(art, (art_w, art_h))
art_x = (W - art_w) // 2
art_y = (art_zone_h - art_h) // 2  # centered in art zone, not full card
card.blit(art_big, (art_x, art_y))

# Info band
band_y = H - BAND_H
pygame.draw.rect(card, (14, 12, 22), (0, band_y, W, BAND_H))
# 2px GEM rule at band top (doubled from r1 for readability at 1×)
pygame.draw.rect(card, GEM, (0, band_y, W, 2))
# Rarity block — wider (24px) spans only the band height; still distinguishes from MARQUEE STRIPE
pygame.draw.rect(card, GEM, (0, band_y + 2, BLOCK_W, BAND_H - 2))

# Name: 20pt (bumped from 18pt for ~1px more cap height at logical size), 1px dark outline
fnt_name  = pygame.font.SysFont("DejaVu Sans", 20, bold=True)
fnt_price = pygame.font.SysFont("DejaVu Sans", 16, bold=True)
name_s  = fnt_name.render("KITSUNE", True, (255, 255, 255))
price_s = fnt_price.render("3 500", True, GEM)
ty = band_y + (BAND_H - name_s.get_height()) // 2
# 1px shadow for legibility against art bleed at band top
for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
    card.blit(fnt_name.render("KITSUNE", True, (0, 0, 0)), (BLOCK_W + 8 + ox, ty + oy))
card.blit(name_s, (BLOCK_W + 8, ty))
card.blit(price_s, (W - price_s.get_width() - 8,
                     ty + (name_s.get_height() - price_s.get_height()) // 2))

# Transparent corners: copy to SRCALPHA then apply rounded mask
card_alpha = pygame.Surface((W, H), pygame.SRCALPHA)
card_alpha.blit(card, (0, 0))
corners = pygame.Surface((W, H), pygame.SRCALPHA)
corners.fill((0, 0, 0, 0))
pygame.draw.rect(corners, (255, 255, 255, 255), (0, 0, W, H), border_radius=16)
card_alpha.blit(corners, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

os.makedirs("docs/item_card_redesign_v3/lower-third", exist_ok=True)
pygame.image.save(card_alpha, "docs/item_card_redesign_v3/lower-third/round_2.png")

from PIL import Image
img = Image.open("docs/item_card_redesign_v3/lower-third/round_2.png")
w, h = img.size
distinct = len(set(img.getdata()))
sz = os.path.getsize("docs/item_card_redesign_v3/lower-third/round_2.png")
print(f"PIL: {w}x{h}, {distinct} distinct, {sz} bytes")
assert w == 324 and h == 200
assert distinct > 200
print("validation OK")
