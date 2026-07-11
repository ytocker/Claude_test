"""PILL-BADGE v3 round-2: thicker border + outer glow halo, larger text, price in warm-white, transparent corners."""
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
card.fill((10, 10, 20))

# Art: kitsune dominant, full-bleed
art = build_kitsune(0)
art_h = int(H * 0.90)
art_w = int(art_h * 64 / 84)
art_big = pygame.transform.smoothscale(art, (art_w, art_h))
art_x = (W - art_w) // 2
art_y = (H - art_h) // 2
card.blit(art_big, (art_x, art_y))

pill_w, pill_h = 220, 44
pill_x = (W - pill_w) // 2
pill_y = H - pill_h - 12
pill_r = pill_h // 2

# Outer glow halo: drawn BEFORE the pill so pill sits on top
glow_w, glow_h = pill_w + 10, pill_h + 10
glow_surf = pygame.Surface((glow_w, glow_h), pygame.SRCALPHA)
glow_r = (glow_h) // 2
pygame.draw.rect(glow_surf, (*GLOW, 50), (0, 0, glow_w, glow_h), 4, border_radius=glow_r)
pygame.draw.rect(glow_surf, (*GEM, 30), (2, 2, glow_w - 4, glow_h - 4), 2, border_radius=glow_r - 2)
card.blit(glow_surf, (pill_x - 5, pill_y - 5))

# Pill chip: thicker 4px border (2px logical) for visibility at thumbnail scale
pill_surf = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
pygame.draw.rect(pill_surf, (18, 14, 28, 220), (0, 0, pill_w, pill_h), border_radius=pill_r)
pygame.draw.rect(pill_surf, (*GEM, 255), (0, 0, pill_w, pill_h), 4, border_radius=pill_r)
card.blit(pill_surf, (pill_x, pill_y))

# Name: 20pt white bold (7px logical cap height) — slightly larger than r1
fnt_name  = pygame.font.SysFont("DejaVu Sans", 20, bold=True)
# Price: 16pt warm-white (reserve GEM gold for the border/glow rarity signal)
fnt_price = pygame.font.SysFont("DejaVu Sans", 16, bold=True)
name_s  = fnt_name.render("KITSUNE", True, (255, 255, 255))
price_s = fnt_price.render("3 500", True, (245, 238, 210))  # warm near-white, not GEM
half = pill_h // 2
card.blit(name_s,  (pill_x + (pill_w - name_s.get_width()) // 2,
                     pill_y + (half - name_s.get_height()) // 2))
card.blit(price_s, (pill_x + (pill_w - price_s.get_width()) // 2,
                     pill_y + half + (half - price_s.get_height()) // 2))

# Transparent corners: copy to SRCALPHA then apply rounded mask
card_alpha = pygame.Surface((W, H), pygame.SRCALPHA)
card_alpha.blit(card, (0, 0))
corners = pygame.Surface((W, H), pygame.SRCALPHA)
corners.fill((0, 0, 0, 0))
pygame.draw.rect(corners, (255, 255, 255, 255), (0, 0, W, H), border_radius=16)
card_alpha.blit(corners, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

os.makedirs("docs/item_card_redesign_v3/pill-badge", exist_ok=True)
pygame.image.save(card_alpha, "docs/item_card_redesign_v3/pill-badge/round_2.png")

from PIL import Image
img = Image.open("docs/item_card_redesign_v3/pill-badge/round_2.png")
w, h = img.size
distinct = len(set(img.getdata()))
sz = os.path.getsize("docs/item_card_redesign_v3/pill-badge/round_2.png")
print(f"PIL: {w}x{h}, {distinct} distinct, {sz} bytes")
assert w == 324 and h == 200
assert distinct > 200
print("validation OK")
