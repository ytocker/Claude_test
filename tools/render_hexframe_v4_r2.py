"""HEXFRAME v4 round-2: gold rarity pill, lifted card body, vertex sparkles, price chip."""
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
# Lifted body so card reads as discrete chip vs. obsidian grid
card.fill((18, 14, 30))

# ── Hexagon geometry (pointy-top) ─────────────────────────────────────────────
R   = 70           # slightly smaller than r1 (was 74) → buys more text room below
HCX = W // 2       # 162
HCY = H // 2 - 12  # 88 — shifted up further to free bottom text space

def hex_verts(cx, cy, r):
    angles = [90, 30, -30, -90, -150, 150]
    return [(int(cx + r * math.cos(math.radians(a))),
             int(cy - r * math.sin(math.radians(a)))) for a in angles]

pts = hex_verts(HCX, HCY, R)

# Warm bloom inside hex — lifted to peak_alpha 55 for casino flash
soft_glow(card, HCX, HCY, 58, GEM, peak_alpha=55, layers=10)

# Art: scaled to fill inside hex
art = build_kitsune(0)
art_h = min(int(R * 1.85), int(R * 2 - 8))
art_w = int(art_h * 64 / 84)
art_big = pygame.transform.smoothscale(art, (art_w, art_h))
art_x = HCX - art_w // 2
art_y = HCY - art_h // 2
card.blit(art_big, (art_x, art_y))

# ── Hex glow border ────────────────────────────────────────────────────────────
glow_layers = [(10, 18), (8, 32), (6, 50), (4, 75), (2, 110)]
for extra, alpha in glow_layers:
    gpts = hex_verts(HCX, HCY, R + extra)
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.polygon(s, (*GEM, alpha), gpts, 3)
    card.blit(s, (0, 0))

pygame.draw.polygon(card, GEM, pts, 3)
pygame.draw.polygon(card, (255, 252, 220), pts, 1)

# ── Vertex sparkles (3 on top half) — casino flash ───────────────────────────
SPARKLE_PTS = hex_verts(HCX, HCY, R)
for i, (sx, sy) in enumerate(SPARKLE_PTS):
    if sy < HCY:   # only top-half vertices (indices 0,1,5)
        # 4-point cross sparkle
        size = 5
        s_surf = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.line(s_surf, (*GEM, 230), (sx, sy - size), (sx, sy + size), 2)
        pygame.draw.line(s_surf, (*GEM, 230), (sx - size, sy), (sx + size, sy), 2)
        pygame.draw.line(s_surf, (255, 252, 240, 180), (sx - 2, sy - 2), (sx + 2, sy + 2), 1)
        pygame.draw.line(s_surf, (255, 252, 240, 180), (sx + 2, sy - 2), (sx - 2, sy + 2), 1)
        card.blit(s_surf, (0, 0))

# ── Info area below the hex ───────────────────────────────────────────────────
INFO_Y = HCY + R + 6   # ≈ 164

fnt_name  = pygame.font.SysFont("DejaVu Sans", 18, bold=True)
name_s    = fnt_name.render("KITSUNE", True, (255, 255, 255))

available = H - INFO_Y - 4
ty = INFO_Y + (available - name_s.get_height()) // 2

# Name centered under hex
nx = HCX - name_s.get_width() // 2
card.blit(name_s, (nx, ty))

# Price: dark rounded chip with 1px gold rim + enlarged coin glyph
fnt_price = pygame.font.SysFont("DejaVu Sans", 14, bold=True)
price_s   = fnt_price.render("3 500", True, GEM)
COIN_R    = 11
CHIP_PAD  = 5
chip_content_w = COIN_R * 2 + 6 + price_s.get_width()
chip_w = chip_content_w + CHIP_PAD * 2
chip_h = price_s.get_height() + CHIP_PAD * 2 - 2
chip_x = W - chip_w - 8
chip_y = INFO_Y + (available - chip_h) // 2

# Chip background + gold rim
chip_surf = pygame.Surface((chip_w, chip_h), pygame.SRCALPHA)
pygame.draw.rect(chip_surf, (12, 10, 24, 230), (0, 0, chip_w, chip_h), border_radius=chip_h // 2)
pygame.draw.rect(chip_surf, (*GEM, 200), (0, 0, chip_w, chip_h), 1, border_radius=chip_h // 2)
card.blit(chip_surf, (chip_x, chip_y))
coin_glyph(card, chip_x + CHIP_PAD + COIN_R, chip_y + chip_h // 2, COIN_R)
card.blit(price_s, (chip_x + CHIP_PAD + COIN_R * 2 + 6, chip_y + CHIP_PAD - 1))

# ── Rarity pill badge: top-center above hex ───────────────────────────────────
fnt_tier = pygame.font.SysFont("DejaVu Sans", 12, bold=True)
tier_s   = fnt_tier.render("LEGENDARY", True, (14, 10, 24))
PILL_PAD = 4
pill_w = tier_s.get_width() + PILL_PAD * 2
pill_h = tier_s.get_height() + PILL_PAD
pill_x = HCX - pill_w // 2
pill_y = HCY - R - pill_h - 6

pill_surf = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
pygame.draw.rect(pill_surf, (*GEM, 255), (0, 0, pill_w, pill_h), border_radius=pill_h // 2)
# Catch-light: near-white top half of pill
for yy in range(pill_h // 2):
    a = int((1 - yy / (pill_h // 2)) * 80)
    pygame.draw.line(pill_surf, (255, 252, 220, a), (2, yy), (pill_w - 2, yy))
card.blit(pill_surf, (pill_x, pill_y))
card.blit(tier_s, (pill_x + PILL_PAD, pill_y + PILL_PAD // 2))

# ── Card edge rim: 1px warm tinted so card separates from obsidian grid ───────
rim_surf = pygame.Surface((W, H), pygame.SRCALPHA)
pygame.draw.rect(rim_surf, (*DEEP, 160), (0, 0, W, H), 1, border_radius=16)
card.blit(rim_surf, (0, 0))

# ── Transparent corners ────────────────────────────────────────────────────────
card_alpha = pygame.Surface((W, H), pygame.SRCALPHA)
card_alpha.blit(card, (0, 0))
mask = pygame.Surface((W, H), pygame.SRCALPHA)
mask.fill((0, 0, 0, 0))
pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, W, H), border_radius=16)
card_alpha.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

os.makedirs("docs/item_card_redesign_v4/hexframe", exist_ok=True)
pygame.image.save(card_alpha, "docs/item_card_redesign_v4/hexframe/round_2.png")

from PIL import Image
img = Image.open("docs/item_card_redesign_v4/hexframe/round_2.png")
w, h = img.size
distinct = len(set(img.getdata()))
sz = os.path.getsize("docs/item_card_redesign_v4/hexframe/round_2.png")
print(f"PIL: {w}x{h}, {distinct} distinct, {sz} bytes")
assert w == 324 and h == 200
assert distinct > 200
print("validation OK")
