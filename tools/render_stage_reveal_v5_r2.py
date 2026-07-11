"""STAGE REVEAL v5 round-2: wide parted curtains reveal face+ears, gold fringe, pleat texture, no collision."""
import os, sys, math
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

card = pygame.Surface((W, H))
card.fill((6, 4, 16))

# ── Art: drawn FIRST so curtains drape on top ─────────────────────────────────
art = build_kitsune(0)
art_h = int(H * 0.86)
art_w = int(art_h * 64 / 84)
art_big = pygame.transform.smoothscale(art, (art_w, art_h))
art_x = (W - art_w) // 2
art_y = H - art_h - 2

soft_glow(card, W // 2, H // 2, 72, GEM, peak_alpha=50, layers=12)
card.blit(art_big, (art_x, art_y))

# ── Curtain polygons: wide parting at top so face/ears are fully revealed ─────
# Opening at the top must be ≥ art_w (~107px) so head+ears (centered at W//2) shows
# Inner top points set to x=100 / x=224 → 124px gap at top of curtains
# Curtains narrow slightly as they sweep down and to the side

# Left curtain: from top-left, sweeps right then curls back down-left
LEFT_PTS = [
    (0, 0),
    (100, 0),          # inner top: wide open (was 158 — hidden the face!)
    (W // 3 - 2, 28),  # inner mid: curves slightly inward
    (W // 5, int(H * 0.58)),
    (W // 10, int(H * 0.68)),
    (0, int(H * 0.54)),
]
# Right curtain: exact mirror
RIGHT_PTS = [(W - x, y) for x, y in LEFT_PTS]

def fill_curtain_gradient(surf, pts):
    """Scan-line GEM→DEEP gradient fill clipped to curtain polygon."""
    mask_s = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.polygon(mask_s, (255, 255, 255, 255), pts)
    min_y = min(p[1] for p in pts)
    max_y = max(p[1] for p in pts)
    span  = max(max_y - min_y, 1)
    for y in range(min_y, max_y + 1):
        t = (y - min_y) / span
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

# ── Pleat texture: vertical fold bands on each curtain ────────────────────────
pleat_s = pygame.Surface((W, H), pygame.SRCALPHA)
# Left curtain: 3 pleat bands — alternating bright/dark columns along drape dir
left_pleat_xs = [22, 44, 66]
for px in left_pleat_xs:
    for y in range(H):
        if 0 <= px < W:
            t = y / H
            bright = 0.5 + 0.5 * math.sin(y / 14.0)  # wave along drape
            a = int(40 * bright * (1 - t * 0.5))
            pygame.draw.line(pleat_s, (255, 252, 210, a), (px, y), (px + 1, y))
right_pleat_xs = [W - 22, W - 44, W - 66]
for px in right_pleat_xs:
    for y in range(H):
        t = y / H
        bright = 0.5 + 0.5 * math.sin(y / 14.0)
        a = int(40 * bright * (1 - t * 0.5))
        pygame.draw.line(pleat_s, (255, 252, 210, a), (px, y), (px + 1, y))
card.blit(pleat_s, (0, 0))

# ── Full-length gold fringe along BOTH inner curtain edges ────────────────────
# Left inner edge: from (100,0) down through (W//3-2, 28) to (W//5, H*0.58)
left_inner = [LEFT_PTS[1], LEFT_PTS[2], LEFT_PTS[3]]
right_inner = [RIGHT_PTS[1], RIGHT_PTS[2], RIGHT_PTS[3]]

fringe_s = pygame.Surface((W, H), pygame.SRCALPHA)
for pts_inner in [left_inner, right_inner]:
    for i in range(len(pts_inner) - 1):
        x0, y0 = pts_inner[i]
        x1, y1 = pts_inner[i + 1]
        # Multi-layer warm fringe
        pygame.draw.line(fringe_s, (255, 252, 210, 200), (x0, y0), (x1, y1), 2)
        pygame.draw.line(fringe_s, (*GEM, 100), (x0, y0), (x1, y1), 4)
card.blit(fringe_s, (0, 0))

# ── Diamond tassel below pill — at the curtain meeting point (just below pill) ─
# Pill occupies y=4..22; tassel hangs from y=26 so it doesn't collide
TASSEL_X, TASSEL_Y = W // 2, 32
TASSEL_R = 9
tassel_pts = [
    (TASSEL_X, TASSEL_Y - TASSEL_R),
    (TASSEL_X + TASSEL_R, TASSEL_Y),
    (TASSEL_X, TASSEL_Y + TASSEL_R),
    (TASSEL_X - TASSEL_R, TASSEL_Y),
]
pygame.draw.polygon(card, GEM, tassel_pts)
pygame.draw.polygon(card, (255, 252, 220), tassel_pts, 1)
# Short cord from top edge to tassel
pygame.draw.line(card, GEM, (W // 2, 22), (W // 2, TASSEL_Y - TASSEL_R), 1)
# Sparkle cross
sp = pygame.Surface((W, H), pygame.SRCALPHA)
sz = 6
pygame.draw.line(sp, (255, 252, 220, 200), (TASSEL_X, TASSEL_Y - sz), (TASSEL_X, TASSEL_Y + sz), 1)
pygame.draw.line(sp, (255, 252, 220, 200), (TASSEL_X - sz, TASSEL_Y), (TASSEL_X + sz, TASSEL_Y), 1)
card.blit(sp, (0, 0))

# 1px dark outline on curtain edges
pygame.draw.polygon(card, (40, 22, 6), LEFT_PTS, 1)
pygame.draw.polygon(card, (40, 22, 6), RIGHT_PTS, 1)

# ── Rarity pill: top-center (no overlap with tassel — tassel moved to y=32) ───
fnt_tier = pygame.font.SysFont("DejaVu Sans", 13, bold=True)
tier_s   = fnt_tier.render("LEGENDARY", True, (6, 4, 16))
PP, PH   = 6, tier_s.get_height() + 5
pill_w   = tier_s.get_width() + PP * 2
pill_x   = W // 2 - pill_w // 2
pill_y   = 4   # y=4..22 — tassel at y=23..41, no collision ✓

pill_surf = pygame.Surface((pill_w, PH), pygame.SRCALPHA)
pygame.draw.rect(pill_surf, (*GEM, 255), (0, 0, pill_w, PH), border_radius=PH // 2)
# 1px dark outline so pill lifts off any gold it overlaps
pygame.draw.rect(pill_surf, (30, 18, 4, 200), (0, 0, pill_w, PH), 1, border_radius=PH // 2)
for yy in range(PH // 2):
    a = int((1 - yy / (PH // 2)) * 100)
    pygame.draw.line(pill_surf, (255, 252, 220, a), (3, yy), (pill_w - 3, yy))
card.blit(pill_surf, (pill_x, pill_y))
card.blit(tier_s, (pill_x + PP, pill_y + 3))

# ── Footer ────────────────────────────────────────────────────────────────────
FOOTER_H = 32
band_y = H - FOOTER_H
for i in range(16):
    a = int(i / 16 * 240)
    s = pygame.Surface((W, 1), pygame.SRCALPHA)
    s.fill((6, 4, 16, a))
    card.blit(s, (0, band_y + i - 8))
pygame.draw.rect(card, (6, 4, 16), (0, band_y + 8, W, FOOTER_H))

fnt_name  = pygame.font.SysFont("DejaVu Sans", 22, bold=True)
fnt_price = pygame.font.SysFont("DejaVu Sans", 14, bold=True)
name_s  = fnt_name.render("KITSUNE", True, (255, 255, 255))
price_s = fnt_price.render("3 500", True, GEM)
ty = band_y + (FOOTER_H - name_s.get_height()) // 2
card.blit(name_s, (12, ty))

COIN_R   = 11
CHIP_PAD = 5
chip_w   = COIN_R * 2 + 5 + price_s.get_width() + CHIP_PAD * 2
chip_h   = price_s.get_height() + CHIP_PAD * 2 - 2
chip_x   = W - chip_w - 10
chip_y   = ty + (name_s.get_height() - chip_h) // 2
chip_surf = pygame.Surface((chip_w, chip_h), pygame.SRCALPHA)
pygame.draw.rect(chip_surf, (6, 4, 16, 230), (0, 0, chip_w, chip_h), border_radius=chip_h // 2)
pygame.draw.rect(chip_surf, (*GEM, 210), (0, 0, chip_w, chip_h), 1, border_radius=chip_h // 2)
card.blit(chip_surf, (chip_x, chip_y))
coin_glyph(card, chip_x + CHIP_PAD + COIN_R, chip_y + chip_h // 2, COIN_R)
card.blit(price_s, (chip_x + CHIP_PAD + COIN_R * 2 + 5, chip_y + CHIP_PAD - 1))

# ── Card edge rim + outer separation glow ────────────────────────────────────
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

os.makedirs("docs/item_card_redesign_v5/stage-reveal", exist_ok=True)
pygame.image.save(card_alpha, "docs/item_card_redesign_v5/stage-reveal/round_2.png")

from PIL import Image
img = Image.open("docs/item_card_redesign_v5/stage-reveal/round_2.png")
w, h = img.size
distinct = len(set(img.getdata()))
sz = os.path.getsize("docs/item_card_redesign_v5/stage-reveal/round_2.png")
print(f"PIL: {w}x{h}, {distinct} distinct, {sz} bytes")
assert w == 324 and h == 200 and distinct > 200
print("validation OK")
