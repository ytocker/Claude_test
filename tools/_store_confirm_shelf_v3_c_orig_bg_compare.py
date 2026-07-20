"""Comparison: BEFORE | C twilight-vault | C* hybrid (C chip+buttons, original shelf)

Output: docs/store_confirm_shelf_v3/c-orig-bg/comparison.png
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
from PIL import Image, ImageDraw, ImageFont
import game.store_data as store_data
import game.store_catalog as store_catalog

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H
import game.store as store_mod

# BEFORE: render live _draw_confirm
SID   = "skin_tempest"
PRICE = store_catalog.cost(SID)
_orig = store_data.balance
store_data.balance = lambda: max(PRICE, 99999)
scene = store_mod.StoreScene.__new__(store_mod.StoreScene)
scene._confirm = SID; scene._confirm_panel = None
scene.confirm_yes_rect = None; scene.confirm_no_rect = None
surf_before = pygame.Surface((W, H))
surf_before.fill((8, 8, 20))
scene._draw_confirm(surf_before)
store_data.balance = _orig
bx = (W - 200) // 2; by = (H - 340) // 2
raw = pygame.image.tostring(surf_before, "RGB")
img_before = Image.frombytes("RGB", (W, H), raw).crop((bx, by, bx+200, by+340))

BASE = "docs/store_confirm_shelf_v3"


def _crop_affordable(slug):
    return Image.open(os.path.join(BASE, slug, "round_2.png")).crop((18, 54, 218, 394))


img_c  = _crop_affordable("twilight-vault")
img_c2 = Image.open(os.path.join(BASE, "c-orig-bg", "round_3.png")).crop((18, 54, 218, 394))

PANEL_W, PANEL_H = 200, 355
MARGIN = 20; GAP = 12; HDR_H = 40; FOOT_H = 36
N = 3

CANVAS_W = MARGIN + N * PANEL_W + (N-1) * GAP + MARGIN
CANVAS_H = MARGIN + HDR_H + GAP + PANEL_H + FOOT_H + MARGIN

canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), (8, 8, 20))
draw   = ImageDraw.Draw(canvas)

try:
    fnt_hdr   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    fnt_lbl   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11)
    fnt_badge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)
    fnt_foot  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9)
except Exception:
    fnt_hdr = fnt_lbl = fnt_badge = fnt_foot = ImageFont.load_default()

hx = CANVAS_W // 2; hy = MARGIN + HDR_H // 2
draw.text((hx, hy - 8), "CONCEPT C — HYBRID: C BUTTONS + ORIGINAL SHELF",
          fill=(210, 205, 240), font=fnt_hdr, anchor="mm")
draw.text((hx, hy + 8), "BEFORE  ·  C (twilight-vault)  ·  C** (C chip + original buttons + shelf)",
          fill=(130, 125, 155), font=fnt_lbl, anchor="mm")


def _panel(img, col_i, badge, line1, line2, badge_col=(200, 190, 240)):
    px = MARGIN + col_i * (PANEL_W + GAP)
    py = MARGIN + HDR_H + GAP
    p  = img.resize((PANEL_W, PANEL_H), Image.LANCZOS)
    canvas.paste(p, (px, py))

    bw = int(fnt_badge.getlength(badge)) + 10
    bh = 19
    bx_, by_ = px + 5, py + 5
    draw.rounded_rectangle([bx_-1, by_-1, bx_+bw+1, by_+bh+1], radius=5, fill=badge_col)
    draw.rounded_rectangle([bx_, by_, bx_+bw, by_+bh], radius=4, fill=(24, 22, 38))
    draw.text((bx_+5, by_+bh//2), badge, fill=(236, 228, 255), font=fnt_badge, anchor="lm")

    fy1 = py + PANEL_H + 6; fy2 = fy1 + 16
    cx_ = px + PANEL_W // 2
    draw.text((cx_, fy1), line1, fill=(200, 195, 235), font=fnt_lbl, anchor="mm")
    draw.text((cx_, fy2), line2, fill=(130, 125, 155), font=fnt_foot, anchor="mm")


_panel(img_before, 0, "0",  "BEFORE",           "current in-game", (180, 170, 220))
_panel(img_c,      1, "C",  "TWILIGHT VAULT",    "teal shelf",      (100, 200, 200))
_panel(img_c2,     2, "C**","C** CARD-BODY CHIP","indigo shelf",    (200, 190, 240))

# Separator lines between panels
for i in range(1, N):
    sep_x = MARGIN + i * (PANEL_W + GAP) - GAP // 2
    draw.line([(sep_x, MARGIN + HDR_H), (sep_x, CANVAS_H - MARGIN)],
              fill=(50, 48, 70), width=1)

OUT = os.path.join(BASE, "c-orig-bg", "comparison.png")
canvas.save(OUT)
print(f"Saved {OUT}  ({CANVAS_W}x{CANVAS_H})")

verify = Image.open(OUT)
for i, (badge, bx_off) in enumerate([("0", 78), ("C", 78+PANEL_W+GAP), ("C*", 78+2*(PANEL_W+GAP))]):
    py_ = MARGIN + HDR_H + GAP
    buy_y = py_ + round(302 * 355 / 340)
    px_val = verify.getpixel((bx_off, buy_y))
    ok = px_val != (8, 8, 20)
    print(f"  {badge} BUY center ({bx_off},{buy_y}) = {px_val}  {'OK' if ok else 'WARN'}")
