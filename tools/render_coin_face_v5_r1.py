"""COIN FACE v5 round-1: large gold coin dominates card — milled rim, GEM fill, art inside coin."""
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
card.fill((8, 6, 20))

# ── Coin geometry ──────────────────────────────────────────────────────────────
NAMEPLATE_H = 34
R      = 82
CX     = W // 2
CY     = (H - NAMEPLATE_H) // 2 + 4   # nudge coin slightly up

# ── GEM gradient fill inside coin (bright top → burnished deep) ───────────────
coin_fill = pygame.Surface((W, H), pygame.SRCALPHA)
for y in range(CY - R, CY + R + 1):
    dy = y - CY
    half_w = math.sqrt(max(0, R * R - dy * dy))
    if half_w < 1:
        continue
    t = (dy + R) / (2 * R)
    cr = int(255 * (1 - t) + 180 * t)
    cg = int(218 * (1 - t) + 120 * t)
    cb = int(90  * (1 - t) + 30  * t)
    pygame.draw.line(coin_fill, (cr, cg, cb, 255),
                     (int(CX - half_w), y), (int(CX + half_w), y))
card.blit(coin_fill, (0, 0))

# ── Art: centered in coin, masked to coin circle ──────────────────────────────
art = build_kitsune(0)
art_h = int(R * 1.88)   # fill coin height
art_w = int(art_h * 64 / 84)
art_big = pygame.transform.smoothscale(art, (art_w, art_h))
art_x = CX - art_w // 2
art_y = CY - art_h // 2

# Draw art clipped to coin circle using SRCALPHA mask
art_surf = pygame.Surface((W, H), pygame.SRCALPHA)
circle_mask = pygame.Surface((W, H), pygame.SRCALPHA)
circle_mask.fill((0, 0, 0, 0))
pygame.draw.circle(circle_mask, (255, 255, 255, 255), (CX, CY), R - 4)

# Soft bloom behind art (inside coin)
soft_glow(card, CX, CY, R - 10, GEM, peak_alpha=50, layers=10)

# Blit art, then clip to circle
art_surf.blit(art_big, (art_x, art_y))
art_surf.blit(circle_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
card.blit(art_surf, (0, 0))

# ── Outer glow ring behind milled rim ─────────────────────────────────────────
for extra, alpha in [(18, 12), (14, 25), (10, 45), (6, 70), (3, 100)]:
    gs = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.circle(gs, (*GEM, alpha), (CX, CY), R + extra, extra * 2)
    card.blit(gs, (0, 0))

# ── Milled rim: 60 radial tick segments, top-lit ─────────────────────────────
N_TICKS = 60
TICK_INNER = R - 2
TICK_OUTER = R + 9
rim_s = pygame.Surface((W, H), pygame.SRCALPHA)
for i in range(N_TICKS):
    angle = 2 * math.pi * i / N_TICKS - math.pi / 2
    # Brightness by y-position (cos of angle): top bright, bottom deep
    bright = (1 + math.cos(angle)) / 2   # 1.0 at top, 0.0 at bottom
    cr = int(255 * bright + 100 * (1 - bright))
    cg = int(248 * bright + 70  * (1 - bright))
    cb = int(220 * bright + 20  * (1 - bright))
    a  = int(220 * bright + 90  * (1 - bright))
    x0 = int(CX + math.cos(angle) * TICK_INNER)
    y0 = int(CY + math.sin(angle) * TICK_INNER)
    x1 = int(CX + math.cos(angle) * TICK_OUTER)
    y1 = int(CY + math.sin(angle) * TICK_OUTER)
    pygame.draw.line(rim_s, (cr, cg, cb, a), (x0, y0), (x1, y1), 2)
card.blit(rim_s, (0, 0))

# 1px catch-light arc at top of coin rim
cl_s = pygame.Surface((W, H), pygame.SRCALPHA)
for i in range(N_TICKS * 2):
    angle = 2 * math.pi * i / (N_TICKS * 2) - math.pi / 2
    if math.sin(angle) > 0:   # bottom half — skip
        continue
    bright = (1 + math.cos(angle)) / 2
    a = int(200 * bright)
    x = int(CX + math.cos(angle) * (TICK_OUTER + 1))
    y = int(CY + math.sin(angle) * (TICK_OUTER + 1))
    pygame.draw.circle(cl_s, (255, 252, 220, a), (x, y), 1)
card.blit(cl_s, (0, 0))

# ── Rarity pill: top-center above coin ────────────────────────────────────────
fnt_tier = pygame.font.SysFont("DejaVu Sans", 12, bold=True)
tier_s   = fnt_tier.render("LEGENDARY", True, (8, 6, 20))
PP, PH   = 5, tier_s.get_height() + 4
pill_w   = tier_s.get_width() + PP * 2
pill_x   = W // 2 - pill_w // 2
pill_y   = CY - R - TICK_OUTER - PH - 4

pill_surf = pygame.Surface((pill_w, PH), pygame.SRCALPHA)
pygame.draw.rect(pill_surf, (*GEM, 255), (0, 0, pill_w, PH), border_radius=PH // 2)
for yy in range(PH // 2):
    a = int((1 - yy / (PH // 2)) * 90)
    pygame.draw.line(pill_surf, (255, 252, 220, a), (2, yy), (pill_w - 2, yy))
card.blit(pill_surf, (pill_x, pill_y))
card.blit(tier_s, (pill_x + PP, pill_y + 2))

# ── Nameplate: dark strip bottom, name left + price chip right ────────────────
band_y = H - NAMEPLATE_H
for i in range(14):
    a = int(i / 14 * 230)
    s = pygame.Surface((W, 1), pygame.SRCALPHA)
    s.fill((6, 4, 16, a))
    card.blit(s, (0, band_y + i - 7))
pygame.draw.rect(card, (6, 4, 16), (0, band_y + 7, W, NAMEPLATE_H))

fnt_name  = pygame.font.SysFont("DejaVu Sans", 20, bold=True)
fnt_price = pygame.font.SysFont("DejaVu Sans", 14, bold=True)
name_s  = fnt_name.render("KITSUNE", True, (255, 255, 255))
price_s = fnt_price.render("3 500", True, GEM)
ty = band_y + (NAMEPLATE_H - name_s.get_height()) // 2
card.blit(name_s, (12, ty))

COIN_R   = 10
CHIP_PAD = 4
chip_w   = COIN_R * 2 + 5 + price_s.get_width() + CHIP_PAD * 2
chip_h   = price_s.get_height() + CHIP_PAD * 2 - 2
chip_x   = W - chip_w - 10
chip_y   = ty + (name_s.get_height() - chip_h) // 2
chip_surf = pygame.Surface((chip_w, chip_h), pygame.SRCALPHA)
pygame.draw.rect(chip_surf, (6, 4, 16, 220), (0, 0, chip_w, chip_h), border_radius=chip_h // 2)
pygame.draw.rect(chip_surf, (*GEM, 200), (0, 0, chip_w, chip_h), 1, border_radius=chip_h // 2)
card.blit(chip_surf, (chip_x, chip_y))
coin_glyph(card, chip_x + CHIP_PAD + COIN_R, chip_y + chip_h // 2, COIN_R)
card.blit(price_s, (chip_x + CHIP_PAD + COIN_R * 2 + 5, chip_y + CHIP_PAD - 1))

# ── Card edge rim ─────────────────────────────────────────────────────────────
rim = pygame.Surface((W, H), pygame.SRCALPHA)
pygame.draw.rect(rim, (*DEEP, 160), (0, 0, W, H), 1, border_radius=16)
card.blit(rim, (0, 0))

# ── Transparent corners ────────────────────────────────────────────────────────
card_alpha = pygame.Surface((W, H), pygame.SRCALPHA)
card_alpha.blit(card, (0, 0))
mask = pygame.Surface((W, H), pygame.SRCALPHA)
mask.fill((0, 0, 0, 0))
pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, W, H), border_radius=16)
card_alpha.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

os.makedirs("docs/item_card_redesign_v5/coin-face", exist_ok=True)
pygame.image.save(card_alpha, "docs/item_card_redesign_v5/coin-face/round_1.png")

from PIL import Image
img = Image.open("docs/item_card_redesign_v5/coin-face/round_1.png")
w, h = img.size
distinct = len(set(img.getdata()))
sz = os.path.getsize("docs/item_card_redesign_v5/coin-face/round_1.png")
print(f"PIL: {w}x{h}, {distinct} distinct, {sz} bytes")
assert w == 324 and h == 200 and distinct > 200
print("validation OK")
