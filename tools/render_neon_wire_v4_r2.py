"""NEON WIRE v4 round-2: wider art bleed, lifted base, stronger glow, price chip, larger name."""
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
# Lifted base so card separates from obsidian grid (was 6,6,20)
card.fill((14, 14, 34))

# ── Art: wider bleed — fills ~70% width, slight overlap behind frame ──────────
art = build_kitsune(0)
art_h = int(H * 0.94)
art_w = int(art_h * 64 / 84 * 1.50)   # wider than before so tails/ears reach frame
art_big = pygame.transform.smoothscale(art, (art_w, art_h))
art_x = (W - art_w) // 2
art_y = (H - art_h) // 2
card.blit(art_big, (art_x, art_y))

# Soft glow bloom behind art for depth
soft_glow(card, W // 2, H // 2, 72, GEM, peak_alpha=40, layers=10)
card.blit(art_big, (art_x, art_y))

# ── Neon wire frame ────────────────────────────────────────────────────────────
INSET  = 10
FR     = 9
FX     = INSET
FY     = INSET
FW     = W - INSET * 2
FH     = H - INSET * 2

# Outer glow layers
glow_layers = [(12, 16), (10, 28), (8, 45), (6, 65), (4, 95), (2, 130)]
for extra, alpha in glow_layers:
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.rect(s, (*GEM, alpha),
                     (FX - extra, FY - extra, FW + extra * 2, FH + extra * 2),
                     3, border_radius=FR + extra)
    card.blit(s, (0, 0))

# Main 2px GEM frame
pygame.draw.rect(card, GEM, (FX, FY, FW, FH), 2, border_radius=FR)
# Inner catch-light: bright top edge
pygame.draw.line(card, (255, 252, 220), (FX + FR, FY + 1), (FX + FW - FR, FY + 1), 1)

# ── Corner diamond pips ────────────────────────────────────────────────────────
PIP_R = 6
for px, py in [(FX + 18, FY + 18), (FX + FW - 18, FY + FH - 18)]:
    pip_pts = [(px, py - PIP_R), (px + PIP_R, py), (px, py + PIP_R), (px - PIP_R, py)]
    pygame.draw.polygon(card, GEM, pip_pts)
    pygame.draw.polygon(card, (255, 248, 220), pip_pts, 1)

# ── Bottom name strip inside frame ────────────────────────────────────────────
STRIP_H = 34
strip_y = FY + FH - STRIP_H
for i in range(STRIP_H):
    alpha = min(255, int(i / (STRIP_H * 0.5) * 230)) if i < STRIP_H * 0.5 else 230
    s = pygame.Surface((FW, 1), pygame.SRCALPHA)
    s.fill((10, 10, 28, alpha))
    card.blit(s, (FX, strip_y + i))

# Name: 20pt bold with 1px gold under-glow for hero-legibility
fnt_name = pygame.font.SysFont("DejaVu Sans", 20, bold=True)
name_s   = fnt_name.render("KITSUNE", True, (255, 255, 255))
ty = strip_y + (STRIP_H - name_s.get_height()) // 2
# Gold under-glow
name_glow = fnt_name.render("KITSUNE", True, GEM)
ng_surf = pygame.Surface(name_glow.get_size(), pygame.SRCALPHA)
ng_surf.blit(name_glow, (0, 0))
ng_surf.set_alpha(80)
card.blit(ng_surf, (FX + 14, ty + 1))
card.blit(name_s, (FX + 14, ty))

# ── Price: dark chip with 1px gold rim, coin at 10px ─────────────────────────
fnt_price = pygame.font.SysFont("DejaVu Sans", 15, bold=True)
price_s   = fnt_price.render("3 500", True, GEM)
COIN_R    = 10
CHIP_PAD  = 4
chip_content_w = COIN_R * 2 + 4 + price_s.get_width()
chip_w = chip_content_w + CHIP_PAD * 2
chip_h = price_s.get_height() + CHIP_PAD * 2 - 2
chip_x = FX + FW - chip_w - 10
chip_y = strip_y + (STRIP_H - chip_h) // 2

chip_surf = pygame.Surface((chip_w, chip_h), pygame.SRCALPHA)
pygame.draw.rect(chip_surf, (10, 8, 28, 220), (0, 0, chip_w, chip_h), border_radius=chip_h // 2)
pygame.draw.rect(chip_surf, (*GEM, 200), (0, 0, chip_w, chip_h), 1, border_radius=chip_h // 2)
card.blit(chip_surf, (chip_x, chip_y))
coin_glyph(card, chip_x + CHIP_PAD + COIN_R, chip_y + chip_h // 2, COIN_R)
card.blit(price_s, (chip_x + CHIP_PAD + COIN_R * 2 + 4, chip_y + CHIP_PAD - 1))

# ── Rarity: gold pill badge in top-left pip area ─────────────────────────────
fnt_tier = pygame.font.SysFont("DejaVu Sans", 10, bold=True)
tier_s   = fnt_tier.render("LEGENDARY", True, (12, 8, 22))
PILL_PAD = 3
pill_w = tier_s.get_width() + PILL_PAD * 2
pill_h = tier_s.get_height() + PILL_PAD
pill_x = FX + 8
pill_y = FY + 8

pill_surf = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
pygame.draw.rect(pill_surf, (*GEM, 255), (0, 0, pill_w, pill_h), border_radius=pill_h // 2)
# Catch-light
for yy in range(pill_h // 2):
    a = int((1 - yy / (pill_h // 2)) * 80)
    pygame.draw.line(pill_surf, (255, 252, 220, a), (2, yy), (pill_w - 2, yy))
card.blit(pill_surf, (pill_x, pill_y))
card.blit(tier_s, (pill_x + PILL_PAD, pill_y + PILL_PAD // 2))

# ── Card-edge outer glow for grid separation ──────────────────────────────────
outer_s = pygame.Surface((W, H), pygame.SRCALPHA)
pygame.draw.rect(outer_s, (*DEEP, 80), (-2, -2, W + 4, H + 4), 4, border_radius=18)
card.blit(outer_s, (0, 0))

# ── Transparent corners ────────────────────────────────────────────────────────
card_alpha = pygame.Surface((W, H), pygame.SRCALPHA)
card_alpha.blit(card, (0, 0))
mask = pygame.Surface((W, H), pygame.SRCALPHA)
mask.fill((0, 0, 0, 0))
pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, W, H), border_radius=16)
card_alpha.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

os.makedirs("docs/item_card_redesign_v4/neon-wire", exist_ok=True)
pygame.image.save(card_alpha, "docs/item_card_redesign_v4/neon-wire/round_2.png")

from PIL import Image
img = Image.open("docs/item_card_redesign_v4/neon-wire/round_2.png")
w, h = img.size
distinct = len(set(img.getdata()))
sz = os.path.getsize("docs/item_card_redesign_v4/neon-wire/round_2.png")
print(f"PIL: {w}x{h}, {distinct} distinct, {sz} bytes")
assert w == 324 and h == 200
assert distinct > 200
print("validation OK")
