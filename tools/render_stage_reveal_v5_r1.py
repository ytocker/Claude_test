"""STAGE REVEAL v5 round-1: gold velvet curtains sweep from top corners, art revealed on stage."""
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
card.fill((6, 4, 16))   # deep stage backdrop

# ── Art: draw FIRST behind curtains ───────────────────────────────────────────
art = build_kitsune(0)
art_h = int(H * 0.86)
art_w = int(art_h * 64 / 84)
art_big = pygame.transform.smoothscale(art, (art_w, art_h))
art_x = (W - art_w) // 2
art_y = H - art_h - 2

soft_glow(card, W // 2, H // 2, 72, GEM, peak_alpha=55, layers=12)
card.blit(art_big, (art_x, art_y))

# ── Curtain polygons ──────────────────────────────────────────────────────────
# Left curtain: sweeps from top-left corner, inner edge angled inward
LEFT_PTS = [
    (0, 0),
    (W // 2 - 14, 0),
    (W // 2 - 4,  22),
    (W // 3,      int(H * 0.60)),
    (W // 10,     int(H * 0.70)),
    (0,           int(H * 0.56)),
]
# Right curtain: mirror of left on x-axis
RIGHT_PTS = [(W - x, y) for x, y in LEFT_PTS]

# Build a clipping mask for each curtain to scan-line fill with gradient
def fill_curtain_gradient(surf, pts, flip_x=False):
    """Fill polygon scan-line with GEM→DEEP vertical gradient."""
    mask_s = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.polygon(mask_s, (255, 255, 255, 255), pts)

    min_y = min(p[1] for p in pts)
    max_y = max(p[1] for p in pts)
    span  = max(max_y - min_y, 1)

    for y in range(min_y, max_y + 1):
        t = (y - min_y) / span
        # Bright warm gold top → burnished DEEP bottom
        cr = int(255 * (1 - t) + 150 * t)
        cg = int(218 * (1 - t) +  92 * t)
        cb = int(80  * (1 - t) +  22 * t)
        row_s = pygame.Surface((W, 1), pygame.SRCALPHA)
        row_s.fill((cr, cg, cb, 255))
        row_clip = pygame.Surface((W, 1), pygame.SRCALPHA)
        row_clip.blit(row_s, (0, 0))
        row_clip.blit(mask_s, (0, -y), special_flags=pygame.BLEND_RGBA_MIN)
        surf.blit(row_clip, (0, y))

fill_curtain_gradient(card, LEFT_PTS)
fill_curtain_gradient(card, RIGHT_PTS)

# 1px dark outline on curtain edges
pygame.draw.polygon(card, (40, 22, 6), LEFT_PTS, 1)
pygame.draw.polygon(card, (40, 22, 6), RIGHT_PTS, 1)

# Catch-light: bright line along each curtain's inner (right/left) edge
# Left curtain inner edge: from (W//2-14, 0) to (W//2-4, 22)
cl_s = pygame.Surface((W, H), pygame.SRCALPHA)
pygame.draw.line(cl_s, (255, 252, 220, 180),
                 (W // 2 - 14, 0), (W // 2 - 4, 22), 1)
pygame.draw.line(cl_s, (255, 252, 220, 180),
                 (W // 2 + 14, 0), (W // 2 + 4, 22), 1)
card.blit(cl_s, (0, 0))

# Fold-shadow lines on curtain faces (diagonal across each curtain)
shadow_s = pygame.Surface((W, H), pygame.SRCALPHA)
# Left curtain shadow fold
pygame.draw.line(shadow_s, (0, 0, 0, 50),
                 (W // 6, 0), (W // 10, int(H * 0.70)), 3)
# Right curtain shadow fold
pygame.draw.line(shadow_s, (0, 0, 0, 50),
                 (W * 5 // 6, 0), (W * 9 // 10, int(H * 0.70)), 3)
card.blit(shadow_s, (0, 0))

# ── Diamond tassel where curtains meet at top-center ──────────────────────────
TASSEL_X, TASSEL_Y = W // 2, 20
TASSEL_R = 10
tassel_pts = [
    (TASSEL_X, TASSEL_Y - TASSEL_R),
    (TASSEL_X + TASSEL_R, TASSEL_Y),
    (TASSEL_X, TASSEL_Y + TASSEL_R),
    (TASSEL_X - TASSEL_R, TASSEL_Y),
]
pygame.draw.polygon(card, GEM, tassel_pts)
pygame.draw.polygon(card, (255, 252, 220), tassel_pts, 1)
# Sparkle cross on tassel
sp = pygame.Surface((W, H), pygame.SRCALPHA)
sz = 8
pygame.draw.line(sp, (255, 252, 220, 200), (TASSEL_X, TASSEL_Y - sz), (TASSEL_X, TASSEL_Y + sz), 1)
pygame.draw.line(sp, (255, 252, 220, 200), (TASSEL_X - sz, TASSEL_Y), (TASSEL_X + sz, TASSEL_Y), 1)
card.blit(sp, (0, 0))

# Tassel hang cord — short vertical line above tassel
pygame.draw.line(card, (*GEM,), (W // 2, 0), (W // 2, TASSEL_Y - TASSEL_R), 1)

# ── Rarity pill: centered at very top (straddles top edge) ────────────────────
fnt_tier = pygame.font.SysFont("DejaVu Sans", 12, bold=True)
tier_s   = fnt_tier.render("LEGENDARY", True, (6, 4, 16))
PP, PH   = 5, tier_s.get_height() + 4
pill_w   = tier_s.get_width() + PP * 2
pill_x   = W // 2 - pill_w // 2
pill_y   = 4

pill_surf = pygame.Surface((pill_w, PH), pygame.SRCALPHA)
pygame.draw.rect(pill_surf, (*GEM, 255), (0, 0, pill_w, PH), border_radius=PH // 2)
for yy in range(PH // 2):
    a = int((1 - yy / (PH // 2)) * 90)
    pygame.draw.line(pill_surf, (255, 252, 220, a), (2, yy), (pill_w - 2, yy))
card.blit(pill_surf, (pill_x, pill_y))
card.blit(tier_s, (pill_x + PP, pill_y + 2))

# ── Footer nameplate ───────────────────────────────────────────────────────────
FOOTER_H = 32
band_y = H - FOOTER_H
for i in range(14):
    a = int(i / 14 * 230)
    s = pygame.Surface((W, 1), pygame.SRCALPHA)
    s.fill((6, 4, 16, a))
    card.blit(s, (0, band_y + i - 7))
pygame.draw.rect(card, (6, 4, 16), (0, band_y + 7, W, FOOTER_H))

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

os.makedirs("docs/item_card_redesign_v5/stage-reveal", exist_ok=True)
pygame.image.save(card_alpha, "docs/item_card_redesign_v5/stage-reveal/round_1.png")

from PIL import Image
img = Image.open("docs/item_card_redesign_v5/stage-reveal/round_1.png")
w, h = img.size
distinct = len(set(img.getdata()))
sz = os.path.getsize("docs/item_card_redesign_v5/stage-reveal/round_1.png")
print(f"PIL: {w}x{h}, {distinct} distinct, {sz} bytes")
assert w == 324 and h == 200 and distinct > 200
print("validation OK")
