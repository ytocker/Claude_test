"""SUIT FRAME v5 round-1: playing card anatomy — corner diamond pips + GEM inner border."""
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
card.fill((10, 5, 22))   # deep navy-burgundy

# ── Corner pip helper ──────────────────────────────────────────────────────────
def draw_pip(surf, cx, cy, r):
    pts = [(cx, cy-r), (cx+r, cy), (cx, cy+r), (cx-r, cy)]
    pygame.draw.polygon(surf, GEM, pts)
    pygame.draw.polygon(surf, (255, 248, 220), pts, 1)

PIP_R   = 10
CI      = 20    # corner inset — distance from card edge to pip center

# 4 corner pips
for cx, cy in [(CI, CI), (W-CI, CI), (CI, H-CI), (W-CI, H-CI)]:
    draw_pip(card, cx, cy, PIP_R)

# Arm lines and small tip pips extending from each corner pip inward
ARM_LEN = 22
SMALL_R  = 4
arm_s = pygame.Surface((W, H), pygame.SRCALPHA)
corners = [
    (CI, CI,     +1, +1),   # top-left: arms go right & down
    (W-CI, CI,   -1, +1),   # top-right: arms go left & down
    (CI, H-CI,   +1, -1),   # bottom-left: arms go right & up
    (W-CI, H-CI, -1, -1),   # bottom-right: arms go left & up
]
for cx, cy, dx, dy in corners:
    x0h, y0h = cx + dx*(PIP_R+2), cy               # horizontal arm start
    x1h, y1h = cx + dx*(PIP_R+2+ARM_LEN), cy       # horizontal arm end
    pygame.draw.line(arm_s, (*GEM, 170), (x0h, y0h), (x1h, y1h), 2)
    x0v, y0v = cx, cy + dy*(PIP_R+2)               # vertical arm start
    x1v, y1v = cx, cy + dy*(PIP_R+2+ARM_LEN)       # vertical arm end
    pygame.draw.line(arm_s, (*GEM, 170), (x0v, y0v), (x1v, y1v), 2)
    # Small pip at arm tips
    draw_pip(arm_s, x1h, y1h, SMALL_R)
    draw_pip(arm_s, x1v, y1v, SMALL_R)
card.blit(arm_s, (0, 0))

# ── Inner border: sits just inside the corner pip zone ────────────────────────
FOOTER_H = 32
INSET    = CI + PIP_R + ARM_LEN + 8
IBX, IBY = INSET, INSET
IBW, IBH = W - INSET * 2, H - INSET - FOOTER_H - 4

# 5-layer feathered glow expanding outward from border
for extra, alpha in [(8,18), (6,35), (4,58), (2,90), (1,130)]:
    gs = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.rect(gs, (*GEM, alpha),
                     (IBX-extra, IBY-extra, IBW+extra*2, IBH+extra*2), 2)
    card.blit(gs, (0, 0))
pygame.draw.rect(card, GEM, (IBX, IBY, IBW, IBH), 2)
pygame.draw.line(card, (255, 252, 220), (IBX+2, IBY+1), (IBX+IBW-2, IBY+1), 1)

# ── Art: center of inner border zone, GEM bloom behind ────────────────────────
ART_CX = W // 2
ART_CY = IBY + IBH // 2
soft_glow(card, ART_CX, ART_CY, 58, GEM, peak_alpha=45, layers=10)

art = build_kitsune(0)
art_h = IBH - 6
art_w = int(art_h * 64 / 84)
art_big = pygame.transform.smoothscale(art, (art_w, art_h))
card.blit(art_big, (ART_CX - art_w//2, IBY + 3))

# ── Rarity pill: centered at very top between corner pips ─────────────────────
fnt_tier = pygame.font.SysFont("DejaVu Sans", 12, bold=True)
tier_s   = fnt_tier.render("LEGENDARY", True, (10, 5, 22))
PP, PH   = 5, tier_s.get_height() + 4
pill_w   = tier_s.get_width() + PP * 2
pill_x   = W//2 - pill_w//2
pill_y   = 5

pill_surf = pygame.Surface((pill_w, PH), pygame.SRCALPHA)
pygame.draw.rect(pill_surf, (*GEM, 255), (0, 0, pill_w, PH), border_radius=PH//2)
for yy in range(PH//2):
    a = int((1 - yy/(PH//2)) * 90)
    pygame.draw.line(pill_surf, (255, 252, 220, a), (2, yy), (pill_w-2, yy))
card.blit(pill_surf, (pill_x, pill_y))
card.blit(tier_s, (pill_x + PP, pill_y + 2))

# ── Footer: dark strip, name left, price chip right ───────────────────────────
band_y = H - FOOTER_H
for i in range(14):
    a = int(i/14 * 230)
    s = pygame.Surface((W, 1), pygame.SRCALPHA)
    s.fill((8, 4, 18, a))
    card.blit(s, (0, band_y + i - 7))
pygame.draw.rect(card, (8, 4, 18), (0, band_y+7, W, FOOTER_H))

fnt_name  = pygame.font.SysFont("DejaVu Sans", 20, bold=True)
fnt_price = pygame.font.SysFont("DejaVu Sans", 14, bold=True)
name_s    = fnt_name.render("KITSUNE", True, (255, 255, 255))
price_s   = fnt_price.render("3 500", True, GEM)
ty = band_y + (FOOTER_H - name_s.get_height()) // 2
card.blit(name_s, (12, ty))

COIN_R = 10
CHIP_PAD = 4
chip_w = COIN_R*2 + 5 + price_s.get_width() + CHIP_PAD*2
chip_h = price_s.get_height() + CHIP_PAD*2 - 2
chip_x = W - chip_w - 10
chip_y = ty + (name_s.get_height() - chip_h)//2
chip_surf = pygame.Surface((chip_w, chip_h), pygame.SRCALPHA)
pygame.draw.rect(chip_surf, (8,4,18,220), (0,0,chip_w,chip_h), border_radius=chip_h//2)
pygame.draw.rect(chip_surf, (*GEM,200), (0,0,chip_w,chip_h), 1, border_radius=chip_h//2)
card.blit(chip_surf, (chip_x, chip_y))
coin_glyph(card, chip_x+CHIP_PAD+COIN_R, chip_y+chip_h//2, COIN_R)
card.blit(price_s, (chip_x+CHIP_PAD+COIN_R*2+5, chip_y+CHIP_PAD-1))

# ── 1px card rim ──────────────────────────────────────────────────────────────
rim = pygame.Surface((W, H), pygame.SRCALPHA)
pygame.draw.rect(rim, (*DEEP,160), (0,0,W,H), 1, border_radius=16)
card.blit(rim, (0,0))

# ── Transparent corners ────────────────────────────────────────────────────────
card_alpha = pygame.Surface((W, H), pygame.SRCALPHA)
card_alpha.blit(card, (0, 0))
mask = pygame.Surface((W, H), pygame.SRCALPHA)
mask.fill((0, 0, 0, 0))
pygame.draw.rect(mask, (255,255,255,255), (0,0,W,H), border_radius=16)
card_alpha.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MIN)

os.makedirs("docs/item_card_redesign_v5/suit-frame", exist_ok=True)
pygame.image.save(card_alpha, "docs/item_card_redesign_v5/suit-frame/round_1.png")

from PIL import Image
img = Image.open("docs/item_card_redesign_v5/suit-frame/round_1.png")
w, h = img.size
distinct = len(set(img.getdata()))
sz = os.path.getsize("docs/item_card_redesign_v5/suit-frame/round_1.png")
print(f"PIL: {w}x{h}, {distinct} distinct, {sz} bytes")
assert w == 324 and h == 200 and distinct > 200
print("validation OK")
