"""NEON WIRE v4 round-1: glowing inner rectangular neon-tube frame, dark base."""
import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))
from game.animal_kitsune import build_kitsune
from game.store_cards import coin_glyph

W, H = 324, 200
GEM  = (255, 202, 104)
GLOW = (255, 168,  58)
DEEP = (150,  92,  22)

card = pygame.Surface((W, H))
card.fill((6, 6, 20))

# ── Art: full-bleed behind frame ───────────────────────────────────────────────
art = build_kitsune(0)
art_h = int(H * 0.90)
art_w = int(art_h * 64 / 84)
art_big = pygame.transform.smoothscale(art, (art_w, art_h))
art_x = (W - art_w) // 2
art_y = (H - art_h) // 2
card.blit(art_big, (art_x, art_y))

# ── Neon wire frame ────────────────────────────────────────────────────────────
INSET  = 10    # gap from card edge to frame
FR     = 9     # corner radius of the frame
FX     = INSET
FY     = INSET
FW     = W - INSET * 2
FH     = H - INSET * 2

# Outer glow layers: expand outward from the frame rect
glow_layers = [(10, 20), (8, 38), (6, 60), (4, 90), (2, 130)]
for extra, alpha in glow_layers:
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.rect(s, (*GEM, alpha),
                     (FX - extra, FY - extra, FW + extra * 2, FH + extra * 2),
                     3, border_radius=FR + extra)
    card.blit(s, (0, 0))

# Main 2px GEM frame
pygame.draw.rect(card, GEM, (FX, FY, FW, FH), 2, border_radius=FR)
# Inner catch-light: bright top edge only (1px lighter inside top)
pygame.draw.line(card, (255, 252, 220), (FX + FR, FY + 1), (FX + FW - FR, FY + 1), 1)

# ── Corner diamond pips (top-left and bottom-right inner corners) ─────────────
PIP_R = 6
for px, py in [(FX + 18, FY + 18), (FX + FW - 18, FY + FH - 18)]:
    pip_pts = [(px, py - PIP_R), (px + PIP_R, py), (px, py + PIP_R), (px - PIP_R, py)]
    pygame.draw.polygon(card, GEM, pip_pts)
    pygame.draw.polygon(card, (255, 248, 220), pip_pts, 1)

# ── Bottom name strip inside frame ────────────────────────────────────────────
STRIP_H = 30
strip_y = FY + FH - STRIP_H
# Gradient fade top of strip
for i in range(STRIP_H):
    alpha = min(255, int(i / (STRIP_H * 0.5) * 220)) if i < STRIP_H * 0.5 else 220
    s = pygame.Surface((FW, 1), pygame.SRCALPHA)
    s.fill((8, 6, 22, alpha))
    card.blit(s, (FX, strip_y + i))

fnt_name  = pygame.font.SysFont("DejaVu Sans", 18, bold=True)
fnt_price = pygame.font.SysFont("DejaVu Sans", 15, bold=True)
name_s  = fnt_name.render("KITSUNE", True, (255, 255, 255))
price_s = fnt_price.render("3 500", True, GEM)
ty = strip_y + (STRIP_H - name_s.get_height()) // 2
card.blit(name_s, (FX + 14, ty))
px = FX + FW - price_s.get_width() - 14
coin_glyph(card, px - 18, ty + price_s.get_height() // 2, 8)
card.blit(price_s, (px, ty))

# Price coin-chip in top-right corner outside/inside frame
fnt_tiny = pygame.font.SysFont("DejaVu Sans", 10)
tier_s = fnt_tiny.render("LEGENDARY", True, (180, 120, 40))
card.blit(tier_s, (FX + FW - tier_s.get_width() - 22, FY + 8))

# ── Transparent corners ────────────────────────────────────────────────────────
card_alpha = pygame.Surface((W, H), pygame.SRCALPHA)
card_alpha.blit(card, (0, 0))
mask = pygame.Surface((W, H), pygame.SRCALPHA)
mask.fill((0, 0, 0, 0))
pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, W, H), border_radius=16)
card_alpha.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

os.makedirs("docs/item_card_redesign_v4/neon-wire", exist_ok=True)
pygame.image.save(card_alpha, "docs/item_card_redesign_v4/neon-wire/round_1.png")

from PIL import Image
img = Image.open("docs/item_card_redesign_v4/neon-wire/round_1.png")
w, h = img.size
distinct = len(set(img.getdata()))
sz = os.path.getsize("docs/item_card_redesign_v4/neon-wire/round_1.png")
print(f"PIL: {w}x{h}, {distinct} distinct, {sz} bytes")
assert w == 324 and h == 200
assert distinct > 200
print("validation OK")
