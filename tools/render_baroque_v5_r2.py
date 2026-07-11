"""BAROQUE v5 round-2: trellis clipped to inside border, dark pill with gold rim, lifted base, cool bloom."""
import os, sys, math
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))
from game.animal_kitsune import build_kitsune
from tools.card_helpers import soft_glow, real_coin_icon

W, H = 324, 200
GEM  = (255, 202, 104)
GLOW = (255, 168,  58)
DEEP = (150,  92,  22)

# ── Card base: lifted warm dark, clearly above obsidian (8,8,24) ──────────────
card = pygame.Surface((W, H))
for y in range(H):
    t = y / H
    r = int(22 * (1 - t) + 14 * t)
    g = int(12 * (1 - t) +  7 * t)
    b = int(36 * (1 - t) + 24 * t)
    pygame.draw.line(card, (r, g, b), (0, y), (W, y))

BDR_INSET = 18   # border rectangle inset
BR        = 12   # border-radius

# ── Art: centered with COOL bloom so fox warmth pops ──────────────────────────
ART_CX = W // 2
ART_CY = H // 2 - 12
art = build_kitsune(0)
art_h = int((H - 44) * 0.94)
art_w = int(art_h * 64 / 84)
art_big = pygame.transform.smoothscale(art, (art_w, art_h))

# Cool/neutral aura so the warm fox separates from GEM gold frame
soft_glow(card, ART_CX, ART_CY, 72, (160, 140, 220), peak_alpha=50, layers=12)
soft_glow(card, ART_CX, ART_CY, 45, GEM, peak_alpha=25, layers=6)
card.blit(art_big, (ART_CX - art_w // 2, ART_CY - art_h // 2))

# ── Diagonal diamond trellis — full card ──────────────────────────────────────
TRELLIS_SPACING = 16
trellis_full = pygame.Surface((W, H), pygame.SRCALPHA)
for offset in range(-H, W + H, TRELLIS_SPACING):
    pygame.draw.line(trellis_full, (*GEM, 28), (offset, 0), (offset + H, H))
for offset in range(0, W + H + H, TRELLIS_SPACING):
    pygame.draw.line(trellis_full, (*GEM, 28), (offset, 0), (offset - H, H))
card.blit(trellis_full, (0, 0))

# ── Corner flourishes: at outer card corners, arms form the frame ─────────────
LARGE_PIP_R = 10
SMALL_PIP_R = 5
ARM_LEN     = 46
FLOU_INSET  = 16   # at card rounded-corner arc centers — same position as outer rim

def draw_diamond(surf, cx, cy, r, color=GEM, outline=(255, 248, 220)):
    pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
    pygame.draw.polygon(surf, color, pts)
    pygame.draw.polygon(surf, outline, pts, 1)

corners = [
    (FLOU_INSET, FLOU_INSET,                    +1, +1),
    (W - FLOU_INSET, FLOU_INSET,                -1, +1),
    (FLOU_INSET, H - FLOU_INSET,                +1, -1),
    (W - FLOU_INSET, H - FLOU_INSET,            -1, -1),
]

fl_s = pygame.Surface((W, H), pygame.SRCALPHA)
for cx, cy, dx, dy in corners:
    # 2px dark backing ring so pip lifts off the GEM border
    backing_pts = [(cx, cy - LARGE_PIP_R - 2), (cx + LARGE_PIP_R + 2, cy),
                   (cx, cy + LARGE_PIP_R + 2), (cx - LARGE_PIP_R - 2, cy)]
    pygame.draw.polygon(fl_s, (20, 10, 30, 200), backing_pts)
    draw_diamond(fl_s, cx, cy, LARGE_PIP_R)
    # Arms extending inward
    ax1 = cx + dx * (LARGE_PIP_R + 3 + ARM_LEN)
    ay1 = cy + dy * (LARGE_PIP_R + 3 + ARM_LEN)
    pygame.draw.line(fl_s, (*GEM, 190), (cx + dx * (LARGE_PIP_R + 3), cy), (ax1, cy), 2)
    pygame.draw.line(fl_s, (*GEM, 190), (cx, cy + dy * (LARGE_PIP_R + 3)), (cx, ay1), 2)
    draw_diamond(fl_s, ax1, cy, SMALL_PIP_R)
    draw_diamond(fl_s, cx, ay1, SMALL_PIP_R)

# ── Rarity pill: DARK FILL + gold rim + gold text (lifts off the gold border) ──
fnt_tier = pygame.font.SysFont("DejaVu Sans", 13, bold=True)
tier_s   = fnt_tier.render("LEGENDARY", True, GEM)
PP, PH   = 7, tier_s.get_height() + 6
pill_w   = tier_s.get_width() + PP * 2
pill_x   = W // 2 - pill_w // 2
# Pill sits above the border, with clear air between it and the frame
pill_y   = FLOU_INSET - PH // 2   # centered on the corner arm height at top

pill_surf = pygame.Surface((pill_w, PH), pygame.SRCALPHA)
pygame.draw.rect(pill_surf, (14, 7, 26, 240), (0, 0, pill_w, PH), border_radius=PH // 2)
pygame.draw.rect(pill_surf, (*GEM, 220), (0, 0, pill_w, PH), 1, border_radius=PH // 2)
# Subtle inner top-sheen on dark pill
for yy in range(PH // 3):
    a = int((1 - yy / (PH // 3)) * 60)
    pygame.draw.line(pill_surf, (255, 252, 220, a), (3, yy), (pill_w - 3, yy))
card.blit(pill_surf, (pill_x, pill_y))
card.blit(tier_s, (pill_x + PP, pill_y + 3))

# ── Nameplate: anchored to bottom corner ornaments ────────────────────────────
_small_pip_y = H - FLOU_INSET - (LARGE_PIP_R + 3 + ARM_LEN)  # = 125
FOOTER_H  = 28
_center   = (_small_pip_y + H) // 2                          # = 162
band_y    = _center - FOOTER_H // 2                          # = 148
INNER_BOT = band_y + FOOTER_H                               # = 176
for i in range(14):
    a = int(i / 14 * 210)
    s = pygame.Surface((W, 1), pygame.SRCALPHA)
    s.fill((12, 7, 22, a))
    card.blit(s, (0, band_y + i - 7))
pygame.draw.rect(card, (12, 7, 22), (0, band_y + 7, W, INNER_BOT - band_y - 7))

fnt_name  = pygame.font.SysFont("DejaVu Sans", 22, bold=True)
fnt_price = pygame.font.SysFont("DejaVu Sans", 17, bold=True)
name_s  = fnt_name.render("KITSUNE", True, (255, 255, 255))
price_s = fnt_price.render("3 500", True, (255, 232, 140))   # bright warm gold
ty = band_y + (FOOTER_H - name_s.get_height()) // 2
card.blit(name_s, (FLOU_INSET + LARGE_PIP_R + 2, ty))

COIN_R = 14                                              # parrot legible at display scale
GAP_CT = 7
chip_w = 5 + COIN_R * 2 + GAP_CT + price_s.get_width() + 5
chip_h = COIN_R * 2 + 8                                 # coin-driven: 36 px
chip_x = W - FLOU_INSET - LARGE_PIP_R - 2 - chip_w     # right edge at x=296
chip_y = ty + (name_s.get_height() - chip_h) // 2
# ── 1. Outer glow: BLEND_ADD at ga 17→100, effective RGB add up to (100,79,41) ──
for gi in range(6, 0, -1):
    gs = pygame.Surface((chip_w + gi * 6, chip_h + gi * 6), pygame.SRCALPHA)
    ga = int(100 * (1 - (gi - 1) / 6))
    pygame.draw.rect(gs, (*GEM, ga), (0, 0, chip_w + gi*6, chip_h + gi*6),
                     border_radius=(chip_h + gi*6) // 2)
    card.blit(gs, (chip_x - gi*3, chip_y - gi*3), special_flags=pygame.BLEND_ADD)
# ── 2. Chip body: top-lit dark gradient clipped to pill ──
chip_surf = pygame.Surface((chip_w, chip_h), pygame.SRCALPHA)
for yy in range(chip_h):
    t = yy / max(1, chip_h - 1)
    chip_surf.fill((int(20*(1-t)+8*t), int(11*(1-t)+5*t), int(36*(1-t)+18*t), 252),
                   (0, yy, chip_w, 1))
pmask = pygame.Surface((chip_w, chip_h), pygame.SRCALPHA)
pygame.draw.rect(pmask, (255, 255, 255, 255), (0, 0, chip_w, chip_h), border_radius=chip_h // 2)
chip_surf.blit(pmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
# ── 3. Top sheen: top 40%, power-2 curve, peak 120 ──
for yy in range(int(chip_h * 0.4)):
    a = int((1 - yy / (chip_h * 0.4)) ** 2 * 120)
    pygame.draw.line(chip_surf, (255, 248, 210, a),
                     (chip_h // 2, yy), (chip_w - chip_h // 2, yy))
# ── 4. Three concentric borders: outer gold, dark bevel, inner gold catch ──
pygame.draw.rect(chip_surf, (*GEM, 255),  (0, 0, chip_w,   chip_h),   2, border_radius=chip_h // 2)
pygame.draw.rect(chip_surf, (*DEEP, 210), (2, 2, chip_w-4, chip_h-4), 1, border_radius=chip_h // 2 - 1)
pygame.draw.rect(chip_surf, (*GEM, 90),   (4, 4, chip_w-8, chip_h-8), 1, border_radius=chip_h // 2 - 2)
card.blit(chip_surf, (chip_x, chip_y))
# ── 5. Coin: strong halo + exact game parrot coin at r=14 ──
coin_cx = chip_x + 5 + COIN_R
coin_cy = chip_y + chip_h // 2
soft_glow(card, coin_cx, coin_cy, COIN_R + 12, GEM, peak_alpha=130, layers=8)
real_coin_icon(card, coin_cx, coin_cy, COIN_R)
# ── 6. Price numeral: vertically centered in chip ──
text_y = chip_y + (chip_h - price_s.get_height()) // 2
card.blit(price_s, (chip_x + 5 + COIN_R * 2 + GAP_CT, text_y))

# Corner flourishes drawn last so they sit on top of the nameplate
card.blit(fl_s, (0, 0))

# ── Transparent corners ────────────────────────────────────────────────────────
card_alpha = pygame.Surface((W, H), pygame.SRCALPHA)
card_alpha.blit(card, (0, 0))
mask = pygame.Surface((W, H), pygame.SRCALPHA)
mask.fill((0, 0, 0, 0))
pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, W, H), border_radius=16)
card_alpha.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

os.makedirs("docs/item_card_redesign_v5/baroque", exist_ok=True)
pygame.image.save(card_alpha, "docs/item_card_redesign_v5/baroque/round_2.png")

from PIL import Image
img = Image.open("docs/item_card_redesign_v5/baroque/round_2.png")
w, h = img.size
distinct = len(set(img.getdata()))
sz = os.path.getsize("docs/item_card_redesign_v5/baroque/round_2.png")
print(f"PIL: {w}x{h}, {distinct} distinct, {sz} bytes")
assert w == 324 and h == 200 and distinct > 200
print("validation OK")
