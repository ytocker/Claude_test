"""VELVET CROWN v4 round-2: fix crown gold (GEM→DEEP gradient, no BLEND_ADD blowout), tip sparkles."""
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
card.fill((10, 6, 18))

# ── Velvet top zone gradient (top 55px) ───────────────────────────────────────
TOP_H = 55
for y in range(TOP_H):
    t = y / TOP_H
    r = int(20 * (1 - t) + 10 * t)
    g = int(4  * (1 - t) + 2  * t)
    b = int(28 * (1 - t) + 18 * t)
    pygame.draw.line(card, (r, g, b), (0, y), (W, y))

# ── 5-tooth crown ─────────────────────────────────────────────────────────────
CX, CY_TOP = W // 2, 7    # nudged up 3px for more art room
CW, CH = 76, 44           # slightly wider

def crown_polygon(cx, top_y, cw, ch):
    base_y = top_y + ch
    bh     = top_y + int(ch * 0.52)
    return [
        (cx - cw // 2,          base_y),
        (cx - cw // 2,          bh),
        (cx - int(cw * 0.38),   top_y + int(ch * 0.14)),
        (cx - int(cw * 0.24),   bh),
        (cx - int(cw * 0.11),   top_y + int(ch * 0.06)),
        (cx - 4,                 top_y + int(ch * 0.38)),
        (cx,                     top_y),
        (cx + 4,                 top_y + int(ch * 0.38)),
        (cx + int(cw * 0.11),   top_y + int(ch * 0.06)),
        (cx + int(cw * 0.24),   bh),
        (cx + int(cw * 0.38),   top_y + int(ch * 0.14)),
        (cx + cw // 2,          bh),
        (cx + cw // 2,          base_y),
    ]

crown_pts = crown_polygon(CX, CY_TOP, CW, CH)

# ── Crown fill: proper GEM→DEEP vertical gradient (NO BLEND_ADD) ──────────────
# Draw crown on a temp surface, then fill row-by-row clipped to polygon bbox
crown_mask = pygame.Surface((W, H), pygame.SRCALPHA)
pygame.draw.polygon(crown_mask, (255, 255, 255, 255), crown_pts)

for y in range(CY_TOP, CY_TOP + CH + 2):
    t = (y - CY_TOP) / CH
    # Top: bright warm gold; Bottom: burnished deep
    cr = int(255 * (1 - t) + 150 * t)
    cg = int(220 * (1 - t) + 92  * t)
    cb = int(80  * (1 - t) + 22  * t)
    row_s = pygame.Surface((W, 1), pygame.SRCALPHA)
    row_s.fill((cr, cg, cb, 255))
    # Clip to crown mask using BLEND_RGBA_MIN
    row_clip = pygame.Surface((W, 1), pygame.SRCALPHA)
    row_clip.blit(row_s, (0, 0))
    row_clip.blit(crown_mask, (0, -y), special_flags=pygame.BLEND_RGBA_MIN)
    card.blit(row_clip, (0, y))

# 1px dark outline
pygame.draw.polygon(card, (60, 35, 8), crown_pts, 2)

# Catch-light: ONLY the 5 tooth tips (2px highlight, not full polygon)
def get_tooth_tips(pts):
    # Indices of peaks in the crown polygon (tallest y-values = smallest y coords)
    return [pts[2], pts[4], pts[6], pts[8], pts[10]]

for tx, ty in get_tooth_tips(crown_pts):
    hl_s = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.circle(hl_s, (255, 252, 230, 200), (tx, ty), 3)
    card.blit(hl_s, (0, 0))

# 4-point sparkle on each tooth tip
for tx, ty in get_tooth_tips(crown_pts):
    sp = pygame.Surface((W, H), pygame.SRCALPHA)
    sz = 6
    pygame.draw.line(sp, (255, 252, 220, 220), (tx, ty - sz), (tx, ty + sz), 1)
    pygame.draw.line(sp, (255, 252, 220, 220), (tx - sz, ty), (tx + sz, ty), 1)
    card.blit(sp, (0, 0))

# Strong glow halo around crown — lifted to peak_alpha 90
soft_glow(card, CX, CY_TOP + CH // 2, 46, GEM, peak_alpha=90, layers=12)

# ── Art: fills the zone below crown ───────────────────────────────────────────
ART_TOP = CY_TOP + CH - 2
NAME_H  = 32

art = build_kitsune(0)
art_h = H - ART_TOP - NAME_H
# Wider art: increase aspect ratio from 64/84 to fill more width
art_w = int(art_h * 64 / 84 * 1.15)
art_big = pygame.transform.smoothscale(art, (art_w, art_h))
art_x = (W - art_w) // 2
art_y = ART_TOP + (H - ART_TOP - NAME_H - art_h) // 2
card.blit(art_big, (art_x, art_y))

# Strong GEM bloom behind art
soft_glow(card, W // 2, ART_TOP + (H - ART_TOP - NAME_H) // 2, 64, GEM, peak_alpha=50, layers=12)
card.blit(art_big, (art_x, art_y))

# ── Bottom nameplate ───────────────────────────────────────────────────────────
band_y = H - NAME_H
for i in range(14):
    alpha = int(i / 14 * 230)
    s = pygame.Surface((W, 1), pygame.SRCALPHA)
    s.fill((10, 8, 20, alpha))
    card.blit(s, (0, band_y + i - 7))
pygame.draw.rect(card, (10, 8, 20), (0, band_y + 7, W, NAME_H))

fnt_name  = pygame.font.SysFont("DejaVu Sans", 18, bold=True)
fnt_price = pygame.font.SysFont("DejaVu Sans", 15, bold=True)
name_s  = fnt_name.render("KITSUNE", True, (255, 255, 255))
price_s = fnt_price.render("3 500", True, GEM)
ty = band_y + (NAME_H - name_s.get_height()) // 2
card.blit(name_s, (14, ty))

# Fixed coin+price binding: coin sits flush left of first digit
px = W - price_s.get_width() - 14
py = ty + (name_s.get_height() - price_s.get_height()) // 2
coin_glyph(card, px - 12, py + price_s.get_height() // 2, 8)
card.blit(price_s, (px, py))

# ── Card edge rim ─────────────────────────────────────────────────────────────
rim_surf = pygame.Surface((W, H), pygame.SRCALPHA)
pygame.draw.rect(rim_surf, (*DEEP, 150), (0, 0, W, H), 1, border_radius=16)
card.blit(rim_surf, (0, 0))

# ── Transparent corners ────────────────────────────────────────────────────────
card_alpha = pygame.Surface((W, H), pygame.SRCALPHA)
card_alpha.blit(card, (0, 0))
mask = pygame.Surface((W, H), pygame.SRCALPHA)
mask.fill((0, 0, 0, 0))
pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, W, H), border_radius=16)
card_alpha.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

os.makedirs("docs/item_card_redesign_v4/velvet-crown", exist_ok=True)
pygame.image.save(card_alpha, "docs/item_card_redesign_v4/velvet-crown/round_2.png")

from PIL import Image
img = Image.open("docs/item_card_redesign_v4/velvet-crown/round_2.png")
w, h = img.size
distinct = len(set(img.getdata()))
sz = os.path.getsize("docs/item_card_redesign_v4/velvet-crown/round_2.png")
print(f"PIL: {w}x{h}, {distinct} distinct, {sz} bytes")
assert w == 324 and h == 200
assert distinct > 200
print("validation OK")
