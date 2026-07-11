"""SUIT FRAME v5 round-2: art bleeds BEHIND inner border, warm gradient fill, wider bloom, bigger pill."""
import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))
from game.animal_kitsune import build_kitsune
from tools.card_helpers import soft_glow, coin_glyph

W, H = 324, 200
GEM  = (255, 202, 104)
GLOW = (255, 168,  58)
DEEP = (150,  92,  22)

# ── Card base: warm aubergine gradient, clearly distinct from obsidian (8,8,24) ─
card = pygame.Surface((W, H))
for y in range(H):
    t = y / H
    r = int(28 * (1 - t) + 14 * t)
    g = int(10 * (1 - t) +  5 * t)
    b = int(30 * (1 - t) + 22 * t)
    pygame.draw.line(card, (r, g, b), (0, y), (W, y))

# ── Art drawn FIRST so inner border + pips overlay it ─────────────────────────
# Art bleeds well beyond the inner border zone — fills most of the card height
art = build_kitsune(0)
art_h = H - 32 - 4    # from near-top to above footer, no margin restriction
art_w = int(art_h * 64 / 84 * 1.30)   # widen 1.30× for landscape fill
art_big = pygame.transform.smoothscale(art, (art_w, art_h))
art_x = (W - art_w) // 2
art_y = 4

# Wide warm bloom to fill flanks (radius 130 to reach inner border edges)
soft_glow(card, W // 2, art_y + art_h // 2, 130, GEM, peak_alpha=40, layers=14)
# Cooler burgundy backing behind fox so gold pops as accent
bg_s = pygame.Surface((W, H), pygame.SRCALPHA)
pygame.draw.ellipse(bg_s, (60, 20, 50, 80), (W // 2 - 80, art_y + 20, 160, art_h - 30))
card.blit(bg_s, (0, 0))

card.blit(art_big, (art_x, art_y))

# ── Corner pip helper ──────────────────────────────────────────────────────────
def draw_pip(surf, cx, cy, r, color=GEM, outline=(255, 248, 220)):
    pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
    pygame.draw.polygon(surf, color, pts)
    pygame.draw.polygon(surf, outline, pts, 1)

PIP_R   = 10
CI      = 16    # tighter corner inset — pips closer to card edge
FOOTER_H = 32

# Keep variables for pill positioning (inner border removed — corner ornaments only)
INSET = CI + PIP_R + 4
IBX, IBY = INSET, INSET
IBW, IBH = W - INSET * 2, H - INSET - FOOTER_H - 4

# ── Corner ornaments overlay the art and border ───────────────────────────────
ARM_LEN = 22
SMALL_R = 4
pip_s = pygame.Surface((W, H), pygame.SRCALPHA)
corners_deco = [
    (CI, CI,         +1, +1),
    (W - CI, CI,     -1, +1),
    (CI, H - CI,     +1, -1),
    (W - CI, H - CI, -1, -1),
]
for cx, cy, dx, dy in corners_deco:
    draw_pip(pip_s, cx, cy, PIP_R)
    # Arm lines with slight alpha so they don't overpower art
    pygame.draw.line(pip_s, (*GEM, 190),
                     (cx + dx * (PIP_R + 2), cy),
                     (cx + dx * (PIP_R + 2 + ARM_LEN), cy), 2)
    pygame.draw.line(pip_s, (*GEM, 190),
                     (cx, cy + dy * (PIP_R + 2)),
                     (cx, cy + dy * (PIP_R + 2 + ARM_LEN)), 2)
    draw_pip(pip_s, cx + dx * (PIP_R + 2 + ARM_LEN), cy, SMALL_R)
    draw_pip(pip_s, cx, cy + dy * (PIP_R + 2 + ARM_LEN), SMALL_R)
card.blit(pip_s, (0, 0))

# ── Rarity pill: centered top, sits atop the top inner border line ─────────────
fnt_tier = pygame.font.SysFont("DejaVu Sans", 14, bold=True)
tier_s   = fnt_tier.render("LEGENDARY", True, (14, 6, 24))
PP, PH   = 7, tier_s.get_height() + 6
pill_w   = tier_s.get_width() + PP * 2
pill_x   = W // 2 - pill_w // 2
pill_y   = IBY - PH // 2 - 1   # straddles the top border line

pill_surf = pygame.Surface((pill_w, PH), pygame.SRCALPHA)
pygame.draw.rect(pill_surf, (*GEM, 255), (0, 0, pill_w, PH), border_radius=PH // 2)
for yy in range(PH // 2):
    a = int((1 - yy / (PH // 2)) * 100)
    pygame.draw.line(pill_surf, (255, 252, 220, a), (3, yy), (pill_w - 3, yy))
card.blit(pill_surf, (pill_x, pill_y))
card.blit(tier_s, (pill_x + PP, pill_y + 3))

# ── Footer: dark gradient strip, name + price chip ────────────────────────────
band_y = H - FOOTER_H
for i in range(16):
    a = int(i / 16 * 240)
    s = pygame.Surface((W, 1), pygame.SRCALPHA)
    s.fill((10, 4, 18, a))
    card.blit(s, (0, band_y + i - 8))
pygame.draw.rect(card, (10, 4, 18), (0, band_y + 8, W, FOOTER_H))

fnt_name  = pygame.font.SysFont("DejaVu Sans", 22, bold=True)
fnt_price = pygame.font.SysFont("DejaVu Sans", 14, bold=True)
name_s    = fnt_name.render("KITSUNE", True, (255, 255, 255))
price_s   = fnt_price.render("3 500", True, GEM)    # narrow-space separator
ty = band_y + (FOOTER_H - name_s.get_height()) // 2
card.blit(name_s, (12, ty))

COIN_R   = 11
CHIP_PAD = 5
chip_w   = COIN_R * 2 + 5 + price_s.get_width() + CHIP_PAD * 2
chip_h   = price_s.get_height() + CHIP_PAD * 2 - 2
chip_x   = W - chip_w - 10
chip_y   = ty + (name_s.get_height() - chip_h) // 2
chip_surf = pygame.Surface((chip_w, chip_h), pygame.SRCALPHA)
pygame.draw.rect(chip_surf, (10, 4, 18, 230), (0, 0, chip_w, chip_h), border_radius=chip_h // 2)
pygame.draw.rect(chip_surf, (*GEM, 210), (0, 0, chip_w, chip_h), 1, border_radius=chip_h // 2)
card.blit(chip_surf, (chip_x, chip_y))
coin_glyph(card, chip_x + CHIP_PAD + COIN_R, chip_y + chip_h // 2, COIN_R)
card.blit(price_s, (chip_x + CHIP_PAD + COIN_R * 2 + 5, chip_y + CHIP_PAD - 1))

# ── Outer separation glow + 2px warmer rim (separates from obsidian grid) ─────
outer_s = pygame.Surface((W, H), pygame.SRCALPHA)
pygame.draw.rect(outer_s, (*DEEP, 50), (-3, -3, W + 6, H + 6), 5, border_radius=20)
card.blit(outer_s, (0, 0))
rim = pygame.Surface((W, H), pygame.SRCALPHA)
pygame.draw.rect(rim, (*DEEP, 200), (0, 0, W, H), 2, border_radius=16)
card.blit(rim, (0, 0))

# ── Transparent corners ────────────────────────────────────────────────────────
card_alpha = pygame.Surface((W, H), pygame.SRCALPHA)
card_alpha.blit(card, (0, 0))
mask = pygame.Surface((W, H), pygame.SRCALPHA)
mask.fill((0, 0, 0, 0))
pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, W, H), border_radius=16)
card_alpha.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

os.makedirs("docs/item_card_redesign_v5/suit-frame", exist_ok=True)
pygame.image.save(card_alpha, "docs/item_card_redesign_v5/suit-frame/round_2.png")

from PIL import Image
img = Image.open("docs/item_card_redesign_v5/suit-frame/round_2.png")
w, h = img.size
distinct = len(set(img.getdata()))
sz = os.path.getsize("docs/item_card_redesign_v5/suit-frame/round_2.png")
print(f"PIL: {w}x{h}, {distinct} distinct, {sz} bytes")
assert w == 324 and h == 200 and distinct > 200
print("validation OK")
