"""STAMP v3 round-2: un-clip price, lifted body, GLOW dots vs GEM price, corner gem accents, transparent corners."""
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
# Lifted body value: slightly brighter than r1 so cards have a silhouette against obsidian (8,8,24)
card.fill((24, 20, 34))

INSET = 28
MARGIN_BOTTOM = 64  # more room for name + price with air beneath
stamp_x = INSET
stamp_y = INSET
stamp_w = W - INSET * 2         # 268
stamp_h = H - INSET - MARGIN_BOTTOM  # 108

# Art inside the stamp frame
art = build_kitsune(0)
art_h = int(stamp_h * 0.92)
art_w = int(art_h * 64 / 84)
art_big = pygame.transform.smoothscale(art, (art_w, art_h))
card.blit(art_big, (stamp_x + (stamp_w - art_w) // 2,
                     stamp_y + (stamp_h - art_h) // 2))

sx0, sy0 = stamp_x, stamp_y
sx1, sy1 = stamp_x + stamp_w, stamp_y + stamp_h

# Perforated border: GLOW color (orange-amber) — distinct from GEM gold reserved for price
DOT_R, DOT_GAP = 5, 12
cx = sx0
while cx <= sx1:
    pygame.draw.circle(card, GLOW, (cx, sy0), DOT_R)
    pygame.draw.circle(card, GLOW, (cx, sy1), DOT_R)
    cx += DOT_GAP
cy = sy0 + DOT_GAP
while cy < sy1:
    pygame.draw.circle(card, GLOW, (sx0, cy), DOT_R)
    pygame.draw.circle(card, GLOW, (sx1, cy), DOT_R)
    cy += DOT_GAP

# Corner gem accents: small 4-point diamonds at the 4 stamp corners — the "legendary" tier cue
def draw_corner_gem(surf, cx, cy, r=8):
    outer = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
    inner = [(cx, cy - r + 3), (cx + r - 3, cy), (cx, cy + r - 3), (cx - r + 3, cy)]
    pygame.draw.polygon(surf, GEM, outer)
    pygame.draw.polygon(surf, DEEP, inner)
    pygame.draw.polygon(surf, (0, 0, 0), outer, 1)

for gx, gy in [(sx0, sy0), (sx1, sy0), (sx0, sy1), (sx1, sy1)]:
    draw_corner_gem(card, gx, gy)

# Name and price vertically centered in the available zone below stamp
fnt_name  = pygame.font.SysFont("DejaVu Sans", 20, bold=True)
fnt_price = pygame.font.SysFont("DejaVu Sans", 16, bold=True)
name_s  = fnt_name.render("KITSUNE", True, (255, 255, 255))
price_s = fnt_price.render("3 500", True, GEM)
total_text_h = name_s.get_height() + 6 + price_s.get_height()
ty = sy1 + (H - sy1 - total_text_h) // 2
card.blit(name_s,  ((W - name_s.get_width()) // 2, ty))
card.blit(price_s, ((W - price_s.get_width()) // 2, ty + name_s.get_height() + 6))

# Transparent corners: copy to SRCALPHA then apply rounded mask
card_alpha = pygame.Surface((W, H), pygame.SRCALPHA)
card_alpha.blit(card, (0, 0))
corners = pygame.Surface((W, H), pygame.SRCALPHA)
corners.fill((0, 0, 0, 0))
pygame.draw.rect(corners, (255, 255, 255, 255), (0, 0, W, H), border_radius=16)
card_alpha.blit(corners, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

os.makedirs("docs/item_card_redesign_v3/stamp", exist_ok=True)
pygame.image.save(card_alpha, "docs/item_card_redesign_v3/stamp/round_2.png")

from PIL import Image
img = Image.open("docs/item_card_redesign_v3/stamp/round_2.png")
w, h = img.size
distinct = len(set(img.getdata()))
sz = os.path.getsize("docs/item_card_redesign_v3/stamp/round_2.png")
print(f"PIL: {w}x{h}, {distinct} distinct, {sz} bytes")
assert w == 324 and h == 200
assert distinct > 200
print("validation OK")
