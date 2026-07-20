"""Phase 5 showcase: store_confirm_shelf_v1

Panels (left → right):
  0  BEFORE  — current live _draw_confirm (option-B base, no redesign)
  A  frost-slab-toggle   round_2.png  left (affordable) panel
  B  neon-arch-cta       round_2.png  left (affordable) panel
  C  gem-facet-verdict   round_2.png  left (affordable) panel
  D  coin-ledger-plaque  round_2.png  left (affordable) panel
  E  wax-seal-verdict    round_2.png  left (affordable) panel

Output: docs/store_confirm_shelf_v1/showcase.png
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

# ── 1. Render BEFORE using live _draw_confirm ────────────────────────────────

SID       = "skin_tempest"
PRICE     = store_catalog.cost(SID)

_orig_balance = store_data.balance

# Monkey-patch balance → affordable
store_data.balance = lambda: max(PRICE, 99999)

scene = store_mod.StoreScene.__new__(store_mod.StoreScene)
scene._confirm        = SID
scene._confirm_panel  = None
scene.confirm_yes_rect = None
scene.confirm_no_rect  = None

surf_before = pygame.Surface((W, H))
surf_before.fill((8, 8, 20))
scene._draw_confirm(surf_before)

store_data.balance = _orig_balance   # restore

# Popup is centred at ((W-POP_W)//2, (H-POP_H)//2) = (80, 150)
POP_W, POP_H = 200, 340
bx = (W - POP_W) // 2   # 80
by = (H - POP_H) // 2   # 150

raw_before = pygame.image.tostring(surf_before, "RGB")
img_before  = Image.frombytes("RGB", (W, H), raw_before)
before_crop = img_before.crop((bx, by, bx + POP_W, by + POP_H))   # 200×340

# ── 2. Load each round_2.png and crop the affordable (left) panel ────────────
# Each sheet: MARGIN=18, HDR_H=36, POP_W=200, POP_H=340
# Left panel box: (18, 54) → (218, 394)

SLUGS = [
    ("A", "frost-slab-toggle",  "FROST SLAB"),
    ("B", "neon-arch-cta",      "NEON ARCH"),
    ("C", "gem-facet-verdict",  "GEM FACET"),
    ("D", "coin-ledger-plaque", "COIN LEDGER"),
    ("E", "wax-seal-verdict",   "WAX SEAL"),
]

BASE = "docs/store_confirm_shelf_v1"


def _crop_affordable(slug):
    path = os.path.join(BASE, slug, "round_2.png")
    img  = Image.open(path)
    # left panel: x=18, y=54, w=200, h=340
    return img.crop((18, 54, 218, 394))   # 200×340


# ── 3. Canvas ────────────────────────────────────────────────────────────────

PANEL_W, PANEL_H = 200, 355
MARGIN   = 20
GAP      = 8
HDR_H    = 40
FOOT_H   = 32

N = 1 + len(SLUGS)   # BEFORE + 5 concepts

CANVAS_W = MARGIN + N * PANEL_W + (N - 1) * GAP + MARGIN
CANVAS_H = MARGIN + HDR_H + GAP + PANEL_H + FOOT_H + MARGIN

canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), (8, 8, 20))
draw   = ImageDraw.Draw(canvas)

try:
    fnt_hdr   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    fnt_lbl   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11)
    fnt_badge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)
    fnt_foot  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",      9)
except Exception:
    fnt_hdr = fnt_lbl = fnt_badge = fnt_foot = ImageFont.load_default()

def _paste_panel(panel_img, col_i, badge_id, footer_line1, footer_line2, is_before=False):
    px = MARGIN + col_i * (PANEL_W + GAP)
    py = MARGIN + HDR_H + GAP

    # Scale 200×340 → 200×355
    p = panel_img.resize((PANEL_W, PANEL_H), Image.LANCZOS)
    canvas.paste(p, (px, py))

    # ID badge (dark pill, top-left of panel)
    btext = badge_id
    bw = int(fnt_badge.getlength(btext)) + 8
    bh = 17
    bx, by_ = px + 5, py + 5
    draw.rounded_rectangle([bx, by_, bx + bw, by_ + bh], radius=4,
                            fill=(24, 22, 38))
    draw.text((bx + 4, by_ + bh // 2), btext, fill=(230, 225, 245),
              font=fnt_badge, anchor="lm")

    # Footer
    fy1 = py + PANEL_H + 6
    fy2 = fy1 + 14
    cx  = px + PANEL_W // 2
    col1 = (255, 220, 100) if is_before else (200, 195, 235)
    draw.text((cx, fy1), footer_line1, fill=col1,       font=fnt_lbl,  anchor="mm")
    draw.text((cx, fy2), footer_line2, fill=(130,125,155), font=fnt_foot, anchor="mm")

# Global header
hx = CANVAS_W // 2
hy = MARGIN + HDR_H // 2
draw.text((hx, hy - 8), "STORE CONFIRM — SHELF REDESIGN",
          fill=(210, 205, 240), font=fnt_hdr, anchor="mm")
draw.text((hx, hy + 8), "BEFORE + 5 concepts · AFFORDABLE STATE",
          fill=(130, 125, 155), font=fnt_lbl, anchor="mm")

# BEFORE panel
_paste_panel(before_crop, 0, "0", "BEFORE", "current in-game", is_before=True)

# Concept panels
for i, (badge, slug, label) in enumerate(SLUGS):
    crop = _crop_affordable(slug)
    _paste_panel(crop, i + 1, badge, label, "FINAL", is_before=False)

OUT = "docs/store_confirm_shelf_v1/showcase.png"
canvas.save(OUT)
print(f"Saved {OUT}  ({CANVAS_W}×{CANVAS_H})")
