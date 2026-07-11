"""ROULETTE ARC v5 round-2: upright segment numbers, pill above arc, lifted card base, wheel higher."""
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

# ── Card base: lifted warm gradient, clearly above obsidian (8,8,24) ──────────
card = pygame.Surface((W, H))
for y in range(H):
    t = y / H
    r = int(22 * (1 - t) + 12 * t)
    g = int(12 * (1 - t) +  6 * t)
    b = int(34 * (1 - t) + 22 * t)
    pygame.draw.line(card, (r, g, b), (0, y), (W, y))

# ── Wheel geometry ─────────────────────────────────────────────────────────────
WCX   = W // 2
WCY   = -22    # raised from -40 so more ring is visible, arc reads as wheel curve
R_OUT = 152
R_IN  = 90

ARC_START_DEG = 10
ARC_END_DEG   = 170
N_SEGS        = 9
seg_span      = (ARC_END_DEG - ARC_START_DEG) / N_SEGS

def arc_pts(cx, cy, r_inner, r_outer, start_deg, end_deg, n_arc=12):
    pts = []
    for i in range(n_arc + 1):
        a = math.radians(start_deg + (end_deg - start_deg) * i / n_arc)
        pts.append((cx + math.cos(a) * r_outer, cy + math.sin(a) * r_outer))
    for i in range(n_arc + 1):
        a = math.radians(end_deg - (end_deg - start_deg) * i / n_arc)
        pts.append((cx + math.cos(a) * r_inner, cy + math.sin(a) * r_inner))
    return pts

seg_numbers = ["7", "3", "11", "1", "9", "5", "15", "2", "8"]

for i in range(N_SEGS):
    s_deg = ARC_START_DEG + i * seg_span
    e_deg = s_deg + seg_span
    pts   = arc_pts(WCX, WCY, R_IN, R_OUT, s_deg, e_deg)

    if i % 2 == 0:
        fill_col = GEM
        txt_col  = (10, 6, 20)
    else:
        fill_col = DEEP
        txt_col  = GEM

    seg_s = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.polygon(seg_s, (*fill_col, 255), pts)
    card.blit(seg_s, (0, 0))

    div_s = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.polygon(div_s, (0, 0, 0, 180), pts, 1)
    card.blit(div_s, (0, 0))

    # Number: ALWAYS UPRIGHT (no rotation) — placed at segment centroid if on-card
    mid_a = math.radians((s_deg + e_deg) / 2)
    mid_r = (R_IN + R_OUT) / 2
    tx = int(WCX + math.cos(mid_a) * mid_r)
    ty = int(WCY + math.sin(mid_a) * mid_r)
    # Only draw if centroid is inside card with margin
    if 4 <= tx <= W - 4 and 4 <= ty <= H - 4:
        fnt_seg = pygame.font.SysFont("DejaVu Sans", 12, bold=True)
        num_s   = fnt_seg.render(seg_numbers[i], True, txt_col)
        card.blit(num_s, (tx - num_s.get_width() // 2, ty - num_s.get_height() // 2))

# ── Outer rim glow + catch-light ──────────────────────────────────────────────
for extra, alpha in [(14, 12), (10, 26), (6, 48), (3, 78)]:
    gs = pygame.Surface((W, H), pygame.SRCALPHA)
    arc_out_pts = arc_pts(WCX, WCY, R_OUT, R_OUT + extra, ARC_START_DEG, ARC_END_DEG, 40)
    pygame.draw.polygon(gs, (*GEM, alpha), arc_out_pts)
    card.blit(gs, (0, 0))

cl_s = pygame.Surface((W, H), pygame.SRCALPHA)
for i in range(80):
    a = math.radians(ARC_START_DEG + (ARC_END_DEG - ARC_START_DEG) * i / 79)
    x = int(WCX + math.cos(a) * (R_OUT + 1))
    y = int(WCY + math.sin(a) * (R_OUT + 1))
    if 0 <= x < W and 0 <= y < H:
        pygame.draw.circle(cl_s, (255, 252, 220, 200), (x, y), 1)
card.blit(cl_s, (0, 0))

# ── 2px GEM inner arc boundary ────────────────────────────────────────────────
inner_s = pygame.Surface((W, H), pygame.SRCALPHA)
pygame.draw.circle(inner_s, (*GEM, 220), (WCX, WCY), R_IN, 2)
card.blit(inner_s, (0, 0))

# ── Art zone: from below inner arc ────────────────────────────────────────────
art_top_y = WCY + R_IN + 2   # bottom of inner arc on-card
FOOTER_H  = 32
ART_ZONE_H = H - art_top_y - FOOTER_H

art = build_kitsune(0)
art_h = int(ART_ZONE_H * 1.05)
art_w = int(art_h * 64 / 84)
art_big = pygame.transform.smoothscale(art, (art_w, art_h))
art_x = (W - art_w) // 2
art_y = art_top_y + (ART_ZONE_H - art_h) // 2

art_cy = art_top_y + ART_ZONE_H // 2
# Neutral-cool bloom so fox warmth pops against it
soft_glow(card, W // 2, art_cy, 60, (160, 140, 220), peak_alpha=40, layers=8)
soft_glow(card, W // 2, art_cy, 40, GEM, peak_alpha=30, layers=6)
card.blit(art_big, (art_x, art_y))

# ── Rarity pill: anchored to inner arc as a tab, above the art ───────────────
# Sits between inner arc and art — clear structural anchor, not floating on art
fnt_tier = pygame.font.SysFont("DejaVu Sans", 11, bold=True)
tier_s   = fnt_tier.render("LEGENDARY", True, (10, 6, 20))
PP, PH   = 5, tier_s.get_height() + 4
pill_w   = tier_s.get_width() + PP * 2

# Make pill look like a "wheel marker tab" sitting on the inner arc
pill_x   = W // 2 - pill_w // 2
pill_y   = art_top_y - PH // 2   # straddles the inner arc line

pill_surf = pygame.Surface((pill_w, PH), pygame.SRCALPHA)
pygame.draw.rect(pill_surf, (*GEM, 255), (0, 0, pill_w, PH), border_radius=PH // 2)
pygame.draw.rect(pill_surf, (20, 12, 4, 220), (0, 0, pill_w, PH), 1, border_radius=PH // 2)
for yy in range(PH // 2):
    a = int((1 - yy / (PH // 2)) * 90)
    pygame.draw.line(pill_surf, (255, 252, 220, a), (2, yy), (pill_w - 2, yy))
card.blit(pill_surf, (pill_x, pill_y))
card.blit(tier_s, (pill_x + PP, pill_y + 2))

# ── Footer ────────────────────────────────────────────────────────────────────
band_y = H - FOOTER_H
for i in range(14):
    a = int(i / 14 * 230)
    s = pygame.Surface((W, 1), pygame.SRCALPHA)
    s.fill((10, 6, 20, a))
    card.blit(s, (0, band_y + i - 7))
pygame.draw.rect(card, (10, 6, 20), (0, band_y + 7, W, FOOTER_H))

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
pygame.draw.rect(chip_surf, (10, 6, 20, 230), (0, 0, chip_w, chip_h), border_radius=chip_h // 2)
pygame.draw.rect(chip_surf, (*GEM, 210), (0, 0, chip_w, chip_h), 1, border_radius=chip_h // 2)
card.blit(chip_surf, (chip_x, chip_y))
coin_glyph(card, chip_x + CHIP_PAD + COIN_R, chip_y + chip_h // 2, COIN_R)
card.blit(price_s, (chip_x + CHIP_PAD + COIN_R * 2 + 5, chip_y + CHIP_PAD - 1))

# ── ID badge: "D" top-left ────────────────────────────────────────────────────
fnt_id   = pygame.font.SysFont("DejaVu Sans", 13, bold=True)
id_s     = fnt_id.render("D", True, GEM)
BP       = 5
badge_w  = id_s.get_width() + BP * 2
badge_h  = id_s.get_height() + BP * 2 - 2
badge_sf = pygame.Surface((badge_w, badge_h), pygame.SRCALPHA)
pygame.draw.rect(badge_sf, (8, 5, 18, 200), (0, 0, badge_w, badge_h), border_radius=badge_h // 2)
pygame.draw.rect(badge_sf, (*GEM, 210), (0, 0, badge_w, badge_h), 1, border_radius=badge_h // 2)
card.blit(badge_sf, (8, 8))
card.blit(id_s, (8 + BP, 8 + BP - 1))

# ── Card edge rim + outer glow ────────────────────────────────────────────────
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

os.makedirs("docs/item_card_redesign_v5/roulette", exist_ok=True)
pygame.image.save(card_alpha, "docs/item_card_redesign_v5/roulette/round_2.png")

from PIL import Image
img = Image.open("docs/item_card_redesign_v5/roulette/round_2.png")
w, h = img.size
distinct = len(set(img.getdata()))
sz = os.path.getsize("docs/item_card_redesign_v5/roulette/round_2.png")
print(f"PIL: {w}x{h}, {distinct} distinct, {sz} bytes")
assert w == 324 and h == 200 and distinct > 200
print("validation OK")
