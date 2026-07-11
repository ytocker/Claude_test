"""JACKPOT COUNTER v4 round-2: larger name (26pt), 40pt price body GEM (no blowout), wider divider."""
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
# Lifted panel base ~15% for grid separation (was 10,8,20)
card.fill((22, 16, 34))

COL_W = 120

# ── Left counter column ────────────────────────────────────────────────────────
# Slightly deeper velvet fill vs. card body
pygame.draw.rect(card, (14, 10, 26), (0, 0, COL_W, H))

# Faint GEM radial bloom inside column
soft_glow(card, COL_W // 2, H // 2, 50, GEM, peak_alpha=30, layers=8)

# Coin glyph above price number
COIN_CY = H // 2 - 40
coin_glyph(card, COL_W // 2, COIN_CY, 14)

# Price number: LARGE 40pt — price is the VISUAL HERO
# Body stays GEM; no BLEND_ADD catch-light (was blowing to white)
fnt_price_big = pygame.font.SysFont("DejaVu Sans", 40, bold=True)
price_s = fnt_price_big.render("3 500", True, GEM)
px_num = (COL_W - price_s.get_width()) // 2
py_num = H // 2 - 4
card.blit(price_s, (px_num, py_num))

# Subtle top-edge catch-light: only 1px highlight on very top of price text
# Use a thin line instead of full additive blit so gold doesn't blow to white
hl_surf = pygame.Surface((price_s.get_width(), 2), pygame.SRCALPHA)
hl_surf.fill((255, 252, 210, 100))
card.blit(hl_surf, (px_num, py_num))

# Rarity word: GEM-tinted (not muddy brown), lettersp via wider font
fnt_tiny = pygame.font.SysFont("DejaVu Sans", 11, bold=True)
tier_s = fnt_tiny.render("LEGENDARY", True, GEM)
tx = (COL_W - tier_s.get_width()) // 2
card.blit(tier_s, (tx, py_num + price_s.get_height() + 4))

# ── Glowing divider: wider outer layers + 3 marquee bulb dots ────────────────
# Wider glow (was 8/6/4/2/1 → 14/10/7/4/2)
glow_levels = [(14, 15), (10, 30), (7, 55), (4, 100), (2, 160)]
for extra, alpha in glow_levels:
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.line(s, (*GEM, alpha),
                     (COL_W, 0), (COL_W, H), extra * 2 + 1)
    card.blit(s, (0, 0))
pygame.draw.line(card, GEM, (COL_W, 0), (COL_W, H), 2)

# 3 evenly-spaced marquee bulb dots on the divider for slot-machine cue
BULB_YS = [H // 4, H // 2, H * 3 // 4]
for by in BULB_YS:
    b_surf = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.circle(b_surf, (255, 252, 200, 220), (COL_W, by), 5)
    pygame.draw.circle(b_surf, (*GEM, 100), (COL_W, by), 9)
    card.blit(b_surf, (0, 0))

# ── Right zone: art with atmospheric GEM bloom ────────────────────────────────
RIGHT_CX = COL_W + (W - COL_W) // 2
RIGHT_CY = H // 2 - 8

soft_glow(card, RIGHT_CX, RIGHT_CY, 76, GEM, peak_alpha=45, layers=14)

art = build_kitsune(0)
art_h = int(H * 0.92)
art_w = int(art_h * 64 / 84)
art_big = pygame.transform.smoothscale(art, (art_w, art_h))
art_x = COL_W + (W - COL_W - art_w) // 2
art_y = (H - art_h) // 2
card.blit(art_big, (art_x, art_y))

# ── Name strip: 26pt bold with 1px dark outline ───────────────────────────────
NAME_H = 34
name_y = H - NAME_H
for i in range(NAME_H):
    alpha = min(255, int(i / (NAME_H * 0.45) * 230)) if i < NAME_H * 0.45 else 230
    s = pygame.Surface((W - COL_W, 1), pygame.SRCALPHA)
    s.fill((14, 10, 26, alpha))
    card.blit(s, (COL_W, name_y + i))

fnt_name = pygame.font.SysFont("DejaVu Sans", 26, bold=True)
name_s = fnt_name.render("KITSUNE", True, (255, 255, 255))
# 1px dark outline for readability against art
name_outline = fnt_name.render("KITSUNE", True, (0, 0, 0))
ny = name_y + (NAME_H - name_s.get_height()) // 2
for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
    card.blit(name_outline, (COL_W + 10 + dx, ny + dy))
card.blit(name_s, (COL_W + 10, ny))

# ── Card edge rim: 1px GEM rim so tile pops from grid ─────────────────────────
rim_surf = pygame.Surface((W, H), pygame.SRCALPHA)
pygame.draw.rect(rim_surf, (*DEEP, 160), (0, 0, W, H), 1, border_radius=16)
card.blit(rim_surf, (0, 0))

# ── Transparent corners ────────────────────────────────────────────────────────
card_alpha = pygame.Surface((W, H), pygame.SRCALPHA)
card_alpha.blit(card, (0, 0))
mask = pygame.Surface((W, H), pygame.SRCALPHA)
mask.fill((0, 0, 0, 0))
pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, W, H), border_radius=16)
card_alpha.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

os.makedirs("docs/item_card_redesign_v4/jackpot", exist_ok=True)
pygame.image.save(card_alpha, "docs/item_card_redesign_v4/jackpot/round_2.png")

from PIL import Image
img = Image.open("docs/item_card_redesign_v4/jackpot/round_2.png")
w, h = img.size
distinct = len(set(img.getdata()))
sz = os.path.getsize("docs/item_card_redesign_v4/jackpot/round_2.png")
print(f"PIL: {w}x{h}, {distinct} distinct, {sz} bytes")
assert w == 324 and h == 200
assert distinct > 200
print("validation OK")
