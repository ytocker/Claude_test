"""VELVET CROWN v4 round-1: procedural 5-tooth gold crown above full-bleed art, dark nameplate."""
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
card.fill((10, 6, 18))

# ── Velvet top zone gradient (top 55px) ───────────────────────────────────────
TOP_H = 55
for y in range(TOP_H):
    t = y / TOP_H
    r = int(20 * (1 - t) + 10 * t)
    g = int(4  * (1 - t) + 2  * t)
    b = int(28 * (1 - t) + 18 * t)
    pygame.draw.line(card, (r, g, b), (0, y), (W, y))

# ── 5-tooth crown ─────────────────────────────────────────────────────────────
CX, CY_TOP = W // 2, 10   # crown top-center
CW, CH = 72, 42           # crown width × height (device px)

def crown_polygon(cx, top_y, cw, ch):
    base_y = top_y + ch
    bh     = top_y + int(ch * 0.52)  # valley shoulder height
    return [
        (cx - cw // 2,          base_y),           # bottom-left
        (cx - cw // 2,          bh),                # left wall
        (cx - int(cw * 0.38),   top_y + int(ch * 0.14)),  # left outer tooth
        (cx - int(cw * 0.24),   bh),                # valley L-outer/L-inner
        (cx - int(cw * 0.11),   top_y + int(ch * 0.06)),  # left inner tooth
        (cx - 4,                 top_y + int(ch * 0.38)),  # center valley (L)
        (cx,                     top_y),             # CENTER PEAK (tallest)
        (cx + 4,                 top_y + int(ch * 0.38)),  # center valley (R)
        (cx + int(cw * 0.11),   top_y + int(ch * 0.06)),  # right inner tooth
        (cx + int(cw * 0.24),   bh),                # valley R-inner/R-outer
        (cx + int(cw * 0.38),   top_y + int(ch * 0.14)),  # right outer tooth
        (cx + cw // 2,          bh),                # right wall
        (cx + cw // 2,          base_y),            # bottom-right
    ]

crown_pts = crown_polygon(CX, CY_TOP, CW, CH)

# GEM gradient fill via horizontal lines
crown_surf = pygame.Surface((W, H), pygame.SRCALPHA)
pygame.draw.polygon(crown_surf, (*GEM, 255), crown_pts)
card.blit(crown_surf, (0, 0))

# Gold gradient top→deep: re-fill top portion with brighter gold
bright_surf = pygame.Surface((W, H), pygame.SRCALPHA)
pygame.draw.polygon(bright_surf, (255, 240, 160, 200), crown_pts)
# Clip to top third of crown using a rect mask — simulates sheen on the teeth
for y in range(CY_TOP, CY_TOP + CH // 3):
    alpha = int((1 - (y - CY_TOP) / (CH // 3)) * 180)
    s_line = pygame.Surface((W, 1), pygame.SRCALPHA)
    s_line.fill((255, 248, 190, alpha))
    bright_surf.blit(s_line, (0, y), special_flags=pygame.BLEND_RGBA_MIN)
card.blit(bright_surf, (0, 0))

# 1px dark outline + 1px bright catch-light inside
pygame.draw.polygon(card, (60, 35, 8), crown_pts, 2)
pygame.draw.polygon(card, (255, 248, 220), crown_pts, 1)

# Glow halo behind/around crown
soft_glow(card, CX, CY_TOP + CH // 2, 44, GEM, peak_alpha=60, layers=10)

# ── Art: fills the zone below crown ───────────────────────────────────────────
ART_TOP = CY_TOP + CH - 4    # slightly overlap with crown base
NAME_H  = 32

art = build_kitsune(0)
art_h = H - ART_TOP - NAME_H
art_w = int(art_h * 64 / 84)
art_big = pygame.transform.smoothscale(art, (art_w, art_h))
art_x = (W - art_w) // 2
art_y = ART_TOP + (H - ART_TOP - NAME_H - art_h) // 2
card.blit(art_big, (art_x, art_y))

# Soft GEM bloom behind art
soft_glow(card, W // 2, ART_TOP + (H - ART_TOP - NAME_H) // 2, 60, GEM, peak_alpha=40, layers=10)
# Re-blit art on top of glow
card.blit(art_big, (art_x, art_y))

# ── Bottom nameplate ───────────────────────────────────────────────────────────
band_y = H - NAME_H
# Gradient-fade top
for i in range(14):
    alpha = int(i / 14 * 230)
    s = pygame.Surface((W, 1), pygame.SRCALPHA)
    s.fill((10, 8, 20, alpha))
    card.blit(s, (0, band_y + i - 7))
pygame.draw.rect(card, (10, 8, 20), (0, band_y + 7, W, NAME_H))

fnt_name  = pygame.font.SysFont("DejaVu Sans", 18, bold=True)
fnt_price = pygame.font.SysFont("DejaVu Sans", 15, bold=True)
name_s  = fnt_name.render("KITSUNE", True, (255, 255, 255))
price_s = fnt_price.render("3 500", True, GEM)
ty = band_y + (NAME_H - name_s.get_height()) // 2
card.blit(name_s, (14, ty))
px = W - price_s.get_width() - 14
coin_glyph(card, px - 18, ty + price_s.get_height() // 2, 8)
card.blit(price_s, (px, ty))

# ── Transparent corners ────────────────────────────────────────────────────────
card_alpha = pygame.Surface((W, H), pygame.SRCALPHA)
card_alpha.blit(card, (0, 0))
mask = pygame.Surface((W, H), pygame.SRCALPHA)
mask.fill((0, 0, 0, 0))
pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, W, H), border_radius=16)
card_alpha.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

os.makedirs("docs/item_card_redesign_v4/velvet-crown", exist_ok=True)
pygame.image.save(card_alpha, "docs/item_card_redesign_v4/velvet-crown/round_1.png")

from PIL import Image
img = Image.open("docs/item_card_redesign_v4/velvet-crown/round_1.png")
w, h = img.size
distinct = len(set(img.getdata()))
sz = os.path.getsize("docs/item_card_redesign_v4/velvet-crown/round_1.png")
print(f"PIL: {w}x{h}, {distinct} distinct, {sz} bytes")
assert w == 324 and h == 200
assert distinct > 200
print("validation OK")
