"""Phase 5 showcase: store_confirm_shelf_v3

Panels (left → right):
  0  BEFORE  — current live _draw_confirm
  A  jeweler-tray     round_2.png  left (affordable) panel
  B  slate-and-gold   round_2.png  left (affordable) panel
  C  twilight-vault   round_2.png  left (affordable) panel
  D  boutique-receipt round_2.png  left (affordable) panel
  E  royal-velvet     round_2.png  left (affordable) panel

Output: docs/store_confirm_shelf_v3/showcase.png
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
import game.store_cards as sc

# ── 1. Render BEFORE using live _draw_confirm ─────────────────────────────────

SID   = "skin_tempest"
PRICE = store_catalog.cost(SID)

_orig_balance = store_data.balance
store_data.balance = lambda: max(PRICE, 99999)

scene = store_mod.StoreScene.__new__(store_mod.StoreScene)
scene._confirm        = SID
scene._confirm_panel  = None
scene.confirm_yes_rect = None
scene.confirm_no_rect  = None

surf_before = pygame.Surface((W, H))
surf_before.fill((8, 8, 20))
scene._draw_confirm(surf_before)

store_data.balance = _orig_balance

POP_W, POP_H = 200, 340
bx = (W - POP_W) // 2
by = (H - POP_H) // 2

raw_before = pygame.image.tostring(surf_before, "RGB")
img_before  = Image.frombytes("RGB", (W, H), raw_before)
before_crop = img_before.crop((bx, by, bx + POP_W, by + POP_H))

# ── 2. Load each round_2.png and crop the affordable (left) panel ─────────────

SLUGS = [
    ("A", "jeweler-tray",     "JEWELER TRAY"),
    ("B", "slate-and-gold",   "SLATE AND GOLD"),
    ("C", "twilight-vault",   "TWILIGHT VAULT"),
    ("D", "boutique-receipt", "BOUTIQUE RECEIPT"),
    ("E", "royal-velvet",     "ROYAL VELVET"),
]

BASE = "docs/store_confirm_shelf_v3"


def _crop_affordable(slug):
    path = os.path.join(BASE, slug, "round_2.png")
    img  = Image.open(path)
    return img.crop((18, 54, 218, 394))


# ── 3. Canvas ─────────────────────────────────────────────────────────────────

PANEL_W, PANEL_H = 200, 355
MARGIN   = 20
GAP      = 8
HDR_H    = 40
FOOT_H   = 32

N = 1 + len(SLUGS)

CANVAS_W = MARGIN + N * PANEL_W + (N - 1) * GAP + MARGIN
CANVAS_H = MARGIN + HDR_H + GAP + PANEL_H + FOOT_H + MARGIN

canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), (8, 8, 20))
draw   = ImageDraw.Draw(canvas)

try:
    fnt_hdr   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    fnt_lbl   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11)
    fnt_badge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)
    fnt_foot  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",       9)
except Exception:
    fnt_hdr = fnt_lbl = fnt_badge = fnt_foot = ImageFont.load_default()


def _paste_panel(panel_img, col_i, badge_id, footer_line1, footer_line2, is_before=False):
    px = MARGIN + col_i * (PANEL_W + GAP)
    py = MARGIN + HDR_H + GAP

    p = panel_img.resize((PANEL_W, PANEL_H), Image.LANCZOS)
    canvas.paste(p, (px, py))

    btext = badge_id
    bw = int(fnt_badge.getlength(btext)) + 8
    bh = 17
    bx_, by_ = px + 5, py + 5
    draw.rounded_rectangle([bx_, by_, bx_ + bw, by_ + bh], radius=4,
                            fill=(24, 22, 38))
    draw.text((bx_ + 4, by_ + bh // 2), btext, fill=(230, 225, 245),
              font=fnt_badge, anchor="lm")

    fy1 = py + PANEL_H + 6
    fy2 = fy1 + 14
    cx  = px + PANEL_W // 2
    col1 = (255, 220, 100) if is_before else (200, 195, 235)
    draw.text((cx, fy1), footer_line1, fill=col1,        font=fnt_lbl,  anchor="mm")
    draw.text((cx, fy2), footer_line2, fill=(130, 125, 155), font=fnt_foot, anchor="mm")


# Global header
hx = CANVAS_W // 2
hy = MARGIN + HDR_H // 2
draw.text((hx, hy - 8), "STORE CONFIRM — BOLD BEVEL REDESIGN v3",
          fill=(210, 205, 240), font=fnt_hdr, anchor="mm")
draw.text((hx, hy + 8), "BEFORE + 5 concepts · AFFORDABLE STATE",
          fill=(130, 125, 155), font=fnt_lbl, anchor="mm")

# BEFORE panel
_paste_panel(before_crop, 0, "0", "BEFORE", "current in-game", is_before=True)

# Concept panels
for i, (badge, slug, label) in enumerate(SLUGS):
    crop = _crop_affordable(slug)
    _paste_panel(crop, i + 1, badge, label, "FINAL", is_before=False)

OUT = "docs/store_confirm_shelf_v3/showcase.png"
canvas.save(OUT)
print(f"Saved {OUT}  ({CANVAS_W}×{CANVAS_H})")

# PIL verification
BUY_CX_1X  = 58
BTN_CY_355 = round(302 * 355 / 340)
print(f"\n=== Showcase PIL verification (BUY button center per panel) ===")
verify_img = Image.open(OUT)
panels_ok = True
all_panels = [("0", "BEFORE", "BEFORE")] + [(b, s, l) for b, s, l in SLUGS]
for i, (badge, slug, label) in enumerate(all_panels):
    px = MARGIN + i * (PANEL_W + GAP)
    py = MARGIN + HDR_H + GAP
    sample_x = px + BUY_CX_1X
    sample_y = py + BTN_CY_355
    px_val = verify_img.getpixel((sample_x, sample_y))
    ok = px_val != (8, 8, 20)
    status = "OK" if ok else "WARN: background"
    panels_ok = panels_ok and ok
    print(f"  {badge}: ({sample_x},{sample_y}) = {px_val}  {status}")
print(f"All panels non-background: {'YES' if panels_ok else 'SOME FAILED'}")
