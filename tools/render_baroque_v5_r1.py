"""BAROQUE v5 round-1: diagonal diamond trellis BG + 4px GEM border + corner flourishes."""
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
card.fill((12, 8, 24))   # deep jewel-toned base

# ── Diagonal diamond trellis background ───────────────────────────────────────
TRELLIS_SPACING = 16
trellis_s = pygame.Surface((W, H), pygame.SRCALPHA)
# Lines at +45° (top-left → bottom-right)
for offset in range(-H, W + H, TRELLIS_SPACING):
    pygame.draw.line(trellis_s, (*GEM, 28),
                     (offset, 0), (offset + H, H))
# Lines at -45° (top-right → bottom-left)
for offset in range(0, W + H + H, TRELLIS_SPACING):
    pygame.draw.line(trellis_s, (*GEM, 28),
                     (offset, 0), (offset - H, H))
card.blit(trellis_s, (0, 0))

# ── Art: centered with GEM bloom (behind border) ──────────────────────────────
# Border inset determines art zone
BDR_INSET = 18   # border drawn at this inset
ART_CX = W // 2
ART_CY = H // 2 - 12   # nudge up slightly for footer room

soft_glow(card, ART_CX, ART_CY, 68, GEM, peak_alpha=50, layers=12)

art = build_kitsune(0)
art_h = int((H - 44) * 0.94)   # stays inside border minus footer
art_w = int(art_h * 64 / 84)
art_big = pygame.transform.smoothscale(art, (art_w, art_h))
card.blit(art_big, (ART_CX - art_w // 2, ART_CY - art_h // 2))

# ── GEM border: 4px + 5-layer outward glow ───────────────────────────────────
BR = 12
for extra, alpha in [(10, 14), (7, 28), (5, 48), (3, 75), (1, 110)]:
    gs = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.rect(gs, (*GEM, alpha),
                     (BDR_INSET - extra, BDR_INSET - extra,
                      W - (BDR_INSET - extra) * 2, H - (BDR_INSET - extra) * 2),
                     extra * 2, border_radius=BR + extra)
    card.blit(gs, (0, 0))
pygame.draw.rect(card, GEM,
                 (BDR_INSET, BDR_INSET, W - BDR_INSET * 2, H - BDR_INSET * 2),
                 4, border_radius=BR)
# Inner catch-light (1px near-white on top edge)
pygame.draw.line(card, (255, 252, 220),
                 (BDR_INSET + BR, BDR_INSET + 2),
                 (W - BDR_INSET - BR, BDR_INSET + 2), 1)

# ── Corner flourishes: large pip + 2 arm lines each with small tip pip ────────
LARGE_PIP_R = 9
SMALL_PIP_R = 4
ARM_LEN     = 22

def draw_diamond(surf, cx, cy, r, color=(255, 202, 104), outline=(255, 248, 220)):
    pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
    pygame.draw.polygon(surf, color, pts)
    pygame.draw.polygon(surf, outline, pts, 1)

corners = [
    (BDR_INSET, BDR_INSET,      +1, +1),   # top-left: arms go right + down
    (W - BDR_INSET, BDR_INSET,  -1, +1),   # top-right: arms go left + down
    (BDR_INSET, H - BDR_INSET,  +1, -1),   # bottom-left: arms go right + up
    (W - BDR_INSET, H - BDR_INSET, -1, -1),  # bottom-right: arms go left + up
]

fl_s = pygame.Surface((W, H), pygame.SRCALPHA)
for cx, cy, dx, dy in corners:
    draw_diamond(fl_s, cx, cy, LARGE_PIP_R)
    # Arm along x-axis (horizontal)
    ax0 = cx + dx * (LARGE_PIP_R + 3)
    ax1 = cx + dx * (LARGE_PIP_R + 3 + ARM_LEN)
    pygame.draw.line(fl_s, (*GEM, 180), (ax0, cy), (ax1, cy), 2)
    draw_diamond(fl_s, ax1, cy, SMALL_PIP_R)
    # Arm along y-axis (vertical)
    ay0 = cy + dy * (LARGE_PIP_R + 3)
    ay1 = cy + dy * (LARGE_PIP_R + 3 + ARM_LEN)
    pygame.draw.line(fl_s, (*GEM, 180), (cx, ay0), (cx, ay1), 2)
    draw_diamond(fl_s, cx, ay1, SMALL_PIP_R)
card.blit(fl_s, (0, 0))

# ── Rarity pill: top-center between corner flourishes ────────────────────────
fnt_tier = pygame.font.SysFont("DejaVu Sans", 12, bold=True)
tier_s   = fnt_tier.render("LEGENDARY", True, (12, 8, 24))
PP, PH   = 5, tier_s.get_height() + 4
pill_w   = tier_s.get_width() + PP * 2
pill_x   = W // 2 - pill_w // 2
pill_y   = BDR_INSET - PH // 2 - 2

pill_surf = pygame.Surface((pill_w, PH), pygame.SRCALPHA)
pygame.draw.rect(pill_surf, (*GEM, 255), (0, 0, pill_w, PH), border_radius=PH // 2)
for yy in range(PH // 2):
    a = int((1 - yy / (PH // 2)) * 90)
    pygame.draw.line(pill_surf, (255, 252, 220, a), (2, yy), (pill_w - 2, yy))
card.blit(pill_surf, (pill_x, pill_y))
card.blit(tier_s, (pill_x + PP, pill_y + 2))

# ── Footer: dark strip at bottom edge, name + price chip ──────────────────────
FOOTER_H = 32
band_y = H - FOOTER_H
for i in range(14):
    a = int(i / 14 * 230)
    s = pygame.Surface((W, 1), pygame.SRCALPHA)
    s.fill((10, 6, 20, a))
    card.blit(s, (0, band_y + i - 7))
pygame.draw.rect(card, (10, 6, 20), (0, band_y + 7, W, FOOTER_H))

fnt_name  = pygame.font.SysFont("DejaVu Sans", 20, bold=True)
fnt_price = pygame.font.SysFont("DejaVu Sans", 14, bold=True)
name_s  = fnt_name.render("KITSUNE", True, (255, 255, 255))
price_s = fnt_price.render("3 500", True, GEM)
ty = band_y + (FOOTER_H - name_s.get_height()) // 2
card.blit(name_s, (12, ty))

COIN_R   = 10
CHIP_PAD = 4
chip_w   = COIN_R * 2 + 5 + price_s.get_width() + CHIP_PAD * 2
chip_h   = price_s.get_height() + CHIP_PAD * 2 - 2
chip_x   = W - chip_w - 10
chip_y   = ty + (name_s.get_height() - chip_h) // 2
chip_surf = pygame.Surface((chip_w, chip_h), pygame.SRCALPHA)
pygame.draw.rect(chip_surf, (10, 6, 20, 220), (0, 0, chip_w, chip_h), border_radius=chip_h // 2)
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

os.makedirs("docs/item_card_redesign_v5/baroque", exist_ok=True)
pygame.image.save(card_alpha, "docs/item_card_redesign_v5/baroque/round_1.png")

from PIL import Image
img = Image.open("docs/item_card_redesign_v5/baroque/round_1.png")
w, h = img.size
distinct = len(set(img.getdata()))
sz = os.path.getsize("docs/item_card_redesign_v5/baroque/round_1.png")
print(f"PIL: {w}x{h}, {distinct} distinct, {sz} bytes")
assert w == 324 and h == 200 and distinct > 200
print("validation OK")
