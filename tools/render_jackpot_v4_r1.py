"""JACKPOT COUNTER v4 round-1: slot-machine left column with large price, art right zone."""
import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))
from game.animal_kitsune import build_kitsune
from game.store_cards import soft_glow, coin_glyph

W, H = 324, 200
GEM  = (255, 202, 104)
GLOW = (255, 168,  58)
DEEP = (150,  92,  22)

card = pygame.Surface((W, H))
card.fill((10, 8, 20))

COL_W = 120   # left column width (37% of 324)

# ── Left counter column ────────────────────────────────────────────────────────
# Deep velvet fill
pygame.draw.rect(card, (10, 8, 22), (0, 0, COL_W, H))

# Faint GEM radial bloom inside column (centered)
soft_glow(card, COL_W // 2, H // 2, 50, GEM, peak_alpha=30, layers=8)

# Coin glyph above price number
COIN_CY = H // 2 - 34
coin_glyph(card, COL_W // 2, COIN_CY, 14)

# Price number: large, GEM color
fnt_price_big = pygame.font.SysFont("DejaVu Sans", 30, bold=True)
price_s = fnt_price_big.render("3 500", True, GEM)
px_num = (COL_W - price_s.get_width()) // 2
py_num = H // 2 - 6
card.blit(price_s, (px_num, py_num))

# Bright catch-light: 1px white highlight at top edge of price text
price_hl = fnt_price_big.render("3 500", True, (255, 252, 210))
# Shift 1px up for "engraved" catch-light
card.blit(price_hl, (px_num, py_num - 1), special_flags=pygame.BLEND_ADD)

# Tiny rarity word below price
fnt_tiny = pygame.font.SysFont("DejaVu Sans", 10)
tier_s = fnt_tiny.render("LEGENDARY", True, (180, 120, 40))
tx = (COL_W - tier_s.get_width()) // 2
card.blit(tier_s, (tx, py_num + price_s.get_height() + 6))

# ── Glowing divider line ───────────────────────────────────────────────────────
glow_levels = [(8, 20), (6, 40), (4, 70), (2, 110), (1, 180)]
for extra, alpha in glow_levels:
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.line(s, (*GEM, alpha),
                     (COL_W, 0), (COL_W, H), extra * 2 + 1)
    card.blit(s, (0, 0))
pygame.draw.line(card, GEM, (COL_W, 0), (COL_W, H), 2)

# ── Right zone: art with atmospheric GEM bloom ────────────────────────────────
RIGHT_CX = COL_W + (W - COL_W) // 2  # 222
RIGHT_CY = H // 2 - 8

soft_glow(card, RIGHT_CX, RIGHT_CY, 76, GEM, peak_alpha=45, layers=14)

art = build_kitsune(0)
art_h = int(H * 0.92)
art_w = int(art_h * 64 / 84)
art_big = pygame.transform.smoothscale(art, (art_w, art_h))
art_x = COL_W + (W - COL_W - art_w) // 2
art_y = (H - art_h) // 2
card.blit(art_big, (art_x, art_y))

# ── Name strip: bottom of right zone ──────────────────────────────────────────
NAME_H = 30
name_y = H - NAME_H
for i in range(NAME_H):
    alpha = min(255, int(i / (NAME_H * 0.45) * 220)) if i < NAME_H * 0.45 else 220
    s = pygame.Surface((W - COL_W, 1), pygame.SRCALPHA)
    s.fill((10, 8, 22, alpha))
    card.blit(s, (COL_W, name_y + i))

fnt_name = pygame.font.SysFont("DejaVu Sans", 18, bold=True)
name_s = fnt_name.render("KITSUNE", True, (255, 255, 255))
ny = name_y + (NAME_H - name_s.get_height()) // 2
card.blit(name_s, (COL_W + 10, ny))

# ── Transparent corners ────────────────────────────────────────────────────────
card_alpha = pygame.Surface((W, H), pygame.SRCALPHA)
card_alpha.blit(card, (0, 0))
mask = pygame.Surface((W, H), pygame.SRCALPHA)
mask.fill((0, 0, 0, 0))
pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, W, H), border_radius=16)
card_alpha.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

os.makedirs("docs/item_card_redesign_v4/jackpot", exist_ok=True)
pygame.image.save(card_alpha, "docs/item_card_redesign_v4/jackpot/round_1.png")

from PIL import Image
img = Image.open("docs/item_card_redesign_v4/jackpot/round_1.png")
w, h = img.size
distinct = len(set(img.getdata()))
sz = os.path.getsize("docs/item_card_redesign_v4/jackpot/round_1.png")
print(f"PIL: {w}x{h}, {distinct} distinct, {sz} bytes")
assert w == 324 and h == 200
assert distinct > 200
print("validation OK")
