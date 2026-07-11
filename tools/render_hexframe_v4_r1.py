"""HEXFRAME v4 round-1: regular hexagonal art boundary with glowing GEM border."""
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

card = pygame.Surface((W, H))
card.fill((8, 6, 18))

# ── Hexagon geometry (pointy-top) ─────────────────────────────────────────────
R   = 74          # center-to-vertex, device px
HCX = W // 2      # 162
HCY = H // 2 - 8  # 92 — shifted up slightly

def hex_verts(cx, cy, r):
    """Pointy-top hex: vertices at 90, 30, -30, -90, -150, 150 degrees."""
    angles = [90, 30, -30, -90, -150, 150]
    return [(int(cx + r * math.cos(math.radians(a))),
             int(cy - r * math.sin(math.radians(a)))) for a in angles]

pts = hex_verts(HCX, HCY, R)

# Faint warm bloom inside hex before art
soft_glow(card, HCX, HCY, 60, GEM, peak_alpha=35, layers=10)

# Art: scaled to fill inside hex
art = build_kitsune(0)
art_h = min(int(R * 1.85), int(R * 2 - 8))   # slightly under hex height
art_w = int(art_h * 64 / 84)
art_big = pygame.transform.smoothscale(art, (art_w, art_h))
art_x = HCX - art_w // 2
art_y = HCY - art_h // 2
card.blit(art_big, (art_x, art_y))

# ── Hex glow border: 6 expanding stroke layers ────────────────────────────────
glow_layers = [(10, 18), (8, 32), (6, 50), (4, 75), (2, 110), (0, 0)]
for extra, alpha in glow_layers[:-1]:
    gpts = hex_verts(HCX, HCY, R + extra)
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.polygon(s, (*GEM, alpha), gpts, 3)
    card.blit(s, (0, 0))

# Solid 3px GEM outline
pygame.draw.polygon(card, GEM, pts, 3)
# Catch-light: thin near-white highlight inside top edge only
pygame.draw.polygon(card, (255, 252, 220), pts, 1)

# ── Info area below the hex ───────────────────────────────────────────────────
# Hex bottom vertex is at HCY + R = 92 + 74 = 166 device px
# Card height 200 → available 34px below hex for text
INFO_Y = HCY + R + 4  # ≈ 170

fnt_name  = pygame.font.SysFont("DejaVu Sans", 16, bold=True)
fnt_price = pygame.font.SysFont("DejaVu Sans", 14, bold=True)
name_s  = fnt_name.render("KITSUNE", True, (255, 255, 255))
price_s = fnt_price.render("3 500", True, GEM)

# Horizontal nameplate: name left-center, coin+price right
available = H - INFO_Y - 4
ty = INFO_Y + (available - max(name_s.get_height(), price_s.get_height())) // 2
card.blit(name_s, (HCX - HCX // 2, ty))

px = W - price_s.get_width() - 14
coin_glyph(card, px - 18, ty + price_s.get_height() // 2, 8)
card.blit(price_s, (px, ty))

# Tiny rarity word top-right
fnt_tiny = pygame.font.SysFont("DejaVu Sans", 10)
tier_s = fnt_tiny.render("LEGENDARY", True, DEEP)
card.blit(tier_s, (W - tier_s.get_width() - 10, 10))

# ── Transparent corners ────────────────────────────────────────────────────────
card_alpha = pygame.Surface((W, H), pygame.SRCALPHA)
card_alpha.blit(card, (0, 0))
mask = pygame.Surface((W, H), pygame.SRCALPHA)
mask.fill((0, 0, 0, 0))
pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, W, H), border_radius=16)
card_alpha.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

os.makedirs("docs/item_card_redesign_v4/hexframe", exist_ok=True)
pygame.image.save(card_alpha, "docs/item_card_redesign_v4/hexframe/round_1.png")

from PIL import Image
img = Image.open("docs/item_card_redesign_v4/hexframe/round_1.png")
w, h = img.size
distinct = len(set(img.getdata()))
sz = os.path.getsize("docs/item_card_redesign_v4/hexframe/round_1.png")
print(f"PIL: {w}x{h}, {distinct} distinct, {sz} bytes")
assert w == 324 and h == 200
assert distinct > 200
print("validation OK")
