"""ROULETTE ARC v5 round-1: partial roulette wheel arc across top ~35%, art fills lower zone."""
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
card.fill((10, 6, 20))

# ── Wheel geometry ─────────────────────────────────────────────────────────────
WCX   = W // 2
WCY   = -40           # center sits above card top
R_OUT = 152
R_IN  = 90

# Arc spans 160° total: from 10° to 170° (clockwise from top = 0°)
# In pygame coords (y-down), 0° is right. We want arc centered on bottom of wheel.
# "bottom" of wheel = pointing down = 90° from right = math.pi/2.
# Arc from 90°-80° to 90°+80° = 10° to 170° from right.
ARC_START_DEG = 10    # degrees from right (pygame convention)
ARC_END_DEG   = 170
N_SEGS        = 9

seg_span = (ARC_END_DEG - ARC_START_DEG) / N_SEGS

def arc_pts(cx, cy, r_inner, r_outer, start_deg, end_deg, n_arc=12):
    """Polygon for a roulette segment (trapezoid curved on outer/inner edges)."""
    pts = []
    # Outer arc (start → end)
    for i in range(n_arc + 1):
        a = math.radians(start_deg + (end_deg - start_deg) * i / n_arc)
        pts.append((cx + math.cos(a) * r_outer, cy + math.sin(a) * r_outer))
    # Inner arc (end → start)
    for i in range(n_arc + 1):
        a = math.radians(end_deg - (end_deg - start_deg) * i / n_arc)
        pts.append((cx + math.cos(a) * r_inner, cy + math.sin(a) * r_inner))
    return pts

# ── Draw segments ──────────────────────────────────────────────────────────────
seg_numbers = ["7", "3", "11", "1", "9", "5", "15", "2", "8"]

for i in range(N_SEGS):
    s_deg = ARC_START_DEG + i * seg_span
    e_deg = s_deg + seg_span
    pts   = arc_pts(WCX, WCY, R_IN, R_OUT, s_deg, e_deg)

    # Alternating GEM / DEEP fill
    if i % 2 == 0:
        fill_col = GEM
        txt_col  = (10, 6, 20)
    else:
        fill_col = DEEP
        txt_col  = GEM

    seg_s = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.polygon(seg_s, (*fill_col, 255), pts)
    card.blit(seg_s, (0, 0))

    # 1px dark divider line
    div_s = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.polygon(div_s, (0, 0, 0, 180), pts, 1)
    card.blit(div_s, (0, 0))

    # Segment number at centroid (mid angle, mid radius)
    mid_a   = math.radians((s_deg + e_deg) / 2)
    mid_r   = (R_IN + R_OUT) / 2
    tx = int(WCX + math.cos(mid_a) * mid_r)
    ty = int(WCY + math.sin(mid_a) * mid_r)
    fnt_seg = pygame.font.SysFont("DejaVu Sans", 13, bold=True)
    num_s   = fnt_seg.render(seg_numbers[i], True, txt_col)
    # Rotate ~perpendicular to radial direction for readability
    rot_angle = math.degrees(mid_a) + 90
    num_rot = pygame.transform.rotate(num_s, -rot_angle)
    card.blit(num_rot, (tx - num_rot.get_width() // 2, ty - num_rot.get_height() // 2))

# ── Outer rim: near-white catch-light arc + 4-layer glow ─────────────────────
for extra, alpha in [(12, 14), (8, 28), (5, 50), (2, 80)]:
    gs = pygame.Surface((W, H), pygame.SRCALPHA)
    arc_out_pts = arc_pts(WCX, WCY, R_OUT, R_OUT + extra, ARC_START_DEG, ARC_END_DEG, 40)
    pygame.draw.polygon(gs, (*GEM, alpha), arc_out_pts)
    card.blit(gs, (0, 0))

# 1px near-white catch-light on outermost arc
cl_s = pygame.Surface((W, H), pygame.SRCALPHA)
for i in range(80):
    a = math.radians(ARC_START_DEG + (ARC_END_DEG - ARC_START_DEG) * i / 79)
    x = int(WCX + math.cos(a) * (R_OUT + 1))
    y = int(WCY + math.sin(a) * (R_OUT + 1))
    if 0 <= x < W and 0 <= y < H:
        pygame.draw.circle(cl_s, (255, 252, 220, 200), (x, y), 1)
card.blit(cl_s, (0, 0))

# ── Inner boundary: 2px GEM arc separating wheel from art zone ───────────────
inner_s = pygame.Surface((W, H), pygame.SRCALPHA)
pygame.draw.circle(inner_s, (*GEM, 220), (WCX, WCY), R_IN, 2)
# Clip to card bounds
inner_clip = pygame.Surface((W, H), pygame.SRCALPHA)
inner_clip.blit(inner_s, (0, 0))
card.blit(inner_clip, (0, 0))

# ── Art: fills from inner arc down, with GEM bloom ────────────────────────────
# The inner arc at y = WCY + R_IN when x=CX → bottom of arc on-card
art_top_y = WCY + R_IN - 4
ART_ZONE_H = H - art_top_y - 34   # minus footer

art = build_kitsune(0)
art_h = int(ART_ZONE_H * 1.05)
art_w = int(art_h * 64 / 84)
art_big = pygame.transform.smoothscale(art, (art_w, art_h))
art_x = (W - art_w) // 2
art_y = art_top_y + (ART_ZONE_H - art_h) // 2

art_cy = art_top_y + ART_ZONE_H // 2
soft_glow(card, W // 2, art_cy, 60, GEM, peak_alpha=45, layers=10)
card.blit(art_big, (art_x, art_y))

# ── Rarity pill: just below inner arc ─────────────────────────────────────────
fnt_tier = pygame.font.SysFont("DejaVu Sans", 11, bold=True)
tier_s   = fnt_tier.render("LEGENDARY", True, (10, 6, 20))
PP, PH   = 4, tier_s.get_height() + 4
pill_w   = tier_s.get_width() + PP * 2
pill_x   = W // 2 - pill_w // 2
# Float inside the dark band just below the wheel
pill_y   = art_top_y + 4

pill_surf = pygame.Surface((pill_w, PH), pygame.SRCALPHA)
pygame.draw.rect(pill_surf, (*GEM, 255), (0, 0, pill_w, PH), border_radius=PH // 2)
for yy in range(PH // 2):
    a = int((1 - yy / (PH // 2)) * 80)
    pygame.draw.line(pill_surf, (255, 252, 220, a), (2, yy), (pill_w - 2, yy))
card.blit(pill_surf, (pill_x, pill_y))
card.blit(tier_s, (pill_x + PP, pill_y + 2))

# ── Footer: dark strip, name + price chip ─────────────────────────────────────
FOOTER_H = 32
band_y = H - FOOTER_H
for i in range(14):
    a = int(i / 14 * 230)
    s = pygame.Surface((W, 1), pygame.SRCALPHA)
    s.fill((8, 5, 18, a))
    card.blit(s, (0, band_y + i - 7))
pygame.draw.rect(card, (8, 5, 18), (0, band_y + 7, W, FOOTER_H))

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
pygame.draw.rect(chip_surf, (8, 5, 18, 220), (0, 0, chip_w, chip_h), border_radius=chip_h // 2)
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

os.makedirs("docs/item_card_redesign_v5/roulette", exist_ok=True)
pygame.image.save(card_alpha, "docs/item_card_redesign_v5/roulette/round_1.png")

from PIL import Image
img = Image.open("docs/item_card_redesign_v5/roulette/round_1.png")
w, h = img.size
distinct = len(set(img.getdata()))
sz = os.path.getsize("docs/item_card_redesign_v5/roulette/round_1.png")
print(f"PIL: {w}x{h}, {distinct} distinct, {sz} bytes")
assert w == 324 and h == 200 and distinct > 200
print("validation OK")
