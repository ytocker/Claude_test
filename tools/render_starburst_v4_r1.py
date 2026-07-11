"""STARBURST v4 round-1: geometric 16-ray starburst + radial bloom, dark footer band."""
import os, sys, math
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
FOOTER_H = 38

card = pygame.Surface((W, H))
card.fill((10, 6, 18))

# ── Starburst: 16 hard-edged polygon rays ─────────────────────────────────────
SCX, SCY = W // 2 + 12, H // 2 - 12   # slightly off-center for dynamism
N_RAYS = 16

def ray_triangle(cx, cy, angle_deg, length, half_w):
    a  = math.radians(angle_deg)
    p  = math.radians(angle_deg + 90)
    tip    = (cx + length * math.cos(a), cy - length * math.sin(a))
    base_l = (cx + half_w * math.cos(p), cy - half_w * math.sin(p))
    base_r = (cx - half_w * math.cos(p), cy + half_w * math.sin(p))
    return [(int(x), int(y)) for x, y in [base_l, tip, base_r]]

ray_surf = pygame.Surface((W, H), pygame.SRCALPHA)
for i in range(N_RAYS):
    angle  = 90 + i * (360.0 / N_RAYS)
    is_long = (i % 2 == 0)
    length  = 96 if is_long else 58
    half_w  = 4.5 if is_long else 2.5
    alpha   = 140 if is_long else 95
    color   = (*GEM, alpha) if is_long else (*GLOW, alpha)
    pts = ray_triangle(SCX, SCY, angle, length, half_w)
    pygame.draw.polygon(ray_surf, color, pts)
card.blit(ray_surf, (0, 0))

# Soft GEM radial bloom behind art
soft_glow(card, SCX, SCY, 68, GEM, peak_alpha=55, layers=12)

# ── Kitsune art ───────────────────────────────────────────────────────────────
art = build_kitsune(0)
art_h = int((H - FOOTER_H) * 0.95)
art_w = int(art_h * 64 / 84)
art_big = pygame.transform.smoothscale(art, (art_w, art_h))
art_x = (W - art_w) // 2
art_y = (H - FOOTER_H - art_h) // 2
card.blit(art_big, (art_x, art_y))

# ── Footer: gradient-fade top, dark band ──────────────────────────────────────
fade_rows = 16
for i in range(fade_rows):
    alpha = int(i / fade_rows * 255)
    s = pygame.Surface((W, 1), pygame.SRCALPHA)
    s.fill((12, 8, 22, alpha))
    card.blit(s, (0, H - FOOTER_H + i - fade_rows // 2))
pygame.draw.rect(card, (12, 8, 22), (0, H - FOOTER_H + fade_rows // 2, W, FOOTER_H))

# 1px GEM rule at band top
pygame.draw.line(card, GEM, (0, H - FOOTER_H), (W, H - FOOTER_H), 1)

# Name
fnt_name  = pygame.font.SysFont("DejaVu Sans", 20, bold=True)
fnt_price = pygame.font.SysFont("DejaVu Sans", 16, bold=True)
name_s  = fnt_name.render("KITSUNE", True, (255, 255, 255))
ty = H - FOOTER_H + (FOOTER_H - name_s.get_height()) // 2
card.blit(name_s, (14, ty))

# Price: coin glyph + number right-aligned
price_s = fnt_price.render("3 500", True, GEM)
px = W - price_s.get_width() - 14
py = ty + (name_s.get_height() - price_s.get_height()) // 2
coin_glyph(card, px - 20, py + price_s.get_height() // 2, 9)
card.blit(price_s, (px, py))

# ── Transparent corners ────────────────────────────────────────────────────────
card_alpha = pygame.Surface((W, H), pygame.SRCALPHA)
card_alpha.blit(card, (0, 0))
mask = pygame.Surface((W, H), pygame.SRCALPHA)
mask.fill((0, 0, 0, 0))
pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, W, H), border_radius=16)
card_alpha.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

os.makedirs("docs/item_card_redesign_v4/starburst", exist_ok=True)
pygame.image.save(card_alpha, "docs/item_card_redesign_v4/starburst/round_1.png")

from PIL import Image
img = Image.open("docs/item_card_redesign_v4/starburst/round_1.png")
w, h = img.size
distinct = len(set(img.getdata()))
sz = os.path.getsize("docs/item_card_redesign_v4/starburst/round_1.png")
print(f"PIL: {w}x{h}, {distinct} distinct, {sz} bytes")
assert w == 324 and h == 200
assert distinct > 200
print("validation OK")
