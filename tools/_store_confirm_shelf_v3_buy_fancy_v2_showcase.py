"""Phase 5 showcase: buy-fancy-v2 BUY-button spectacular effects

Panels (left → right):
  0  BEFORE  — C** round_4 (deep-card base, affordable panel)
  A  gem-crown         round_2.png
  B  starburst-radiance round_2.png
  C  confetti-scatter   round_2.png
  D  gem-letters        round_2.png
  E  legendary-aura     round_2.png

Output: docs/store_confirm_shelf_v3/buy-fancy-v2/showcase.png
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
from PIL import Image, ImageDraw, ImageFont

pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

BASE_V3  = "docs/store_confirm_shelf_v3"
BASE_BF2 = os.path.join(BASE_V3, "buy-fancy-v2")

CROP = (18, 54, 218, 394)   # affordable left panel crop from 444×412 sheet → 200×340

# ── BEFORE panel: C** round_4 ─────────────────────────────────────────────────
before_img = Image.open(os.path.join(BASE_V3, "c-orig-bg", "round_4.png")).crop(CROP)

# ── Concept panels ─────────────────────────────────────────────────────────────
CONCEPTS = [
    ("A", "gem-crown",          "GEM CROWN"),
    ("B", "starburst-radiance", "STARBURST RADIANCE"),
    ("C", "confetti-scatter",   "CONFETTI SCATTER"),
    ("D", "gem-letters",        "GEM LETTERS"),
    ("E", "legendary-aura",     "LEGENDARY AURA"),
]

concept_imgs = []
for badge, slug, _ in CONCEPTS:
    path = os.path.join(BASE_BF2, slug, "round_3.png")
    img  = Image.open(path).crop(CROP)
    concept_imgs.append(img)

# ── Canvas ─────────────────────────────────────────────────────────────────────
PANEL_W, PANEL_H = 200, 355
MARGIN   = 20
GAP      = 8
HDR_H    = 40
FOOT_H   = 32

N = 1 + len(CONCEPTS)

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

# Global header
hx = CANVAS_W // 2
hy = MARGIN + HDR_H // 2
draw.text((hx, hy - 8), "BUY BUTTON SPECTACULAR EFFECTS — v2 (r3)",
          fill=(210, 205, 240), font=fnt_hdr, anchor="mm")
draw.text((hx, hy + 8), "BEFORE (C** base)  ·  A–E final rounds  ·  AFFORDABLE STATE",
          fill=(130, 125, 155), font=fnt_lbl, anchor="mm")


def _paste_panel(panel_img, col_i, badge_id, footer_line1, footer_line2, is_before=False):
    px = MARGIN + col_i * (PANEL_W + GAP)
    py = MARGIN + HDR_H + GAP

    p = panel_img.resize((PANEL_W, PANEL_H), Image.LANCZOS)
    canvas.paste(p, (px, py))

    # Badge pill — top-left corner
    btext = badge_id
    bw = int(fnt_badge.getlength(btext)) + 10
    bh = 19
    bx_, by_ = px + 5, py + 5
    draw.rounded_rectangle([bx_ - 1, by_ - 1, bx_ + bw + 1, by_ + bh + 1],
                            radius=5, fill=(200, 190, 240))
    draw.rounded_rectangle([bx_, by_, bx_ + bw, by_ + bh],
                            radius=4, fill=(24, 22, 38))
    draw.text((bx_ + 5, by_ + bh // 2), btext,
              fill=(236, 228, 255), font=fnt_badge, anchor="lm")

    # Footer
    fy1 = py + PANEL_H + 6
    fy2 = fy1 + 14
    cx  = px + PANEL_W // 2
    col1 = (255, 220, 100) if is_before else (200, 195, 235)
    draw.text((cx, fy1), footer_line1, fill=col1,            font=fnt_lbl,  anchor="mm")
    draw.text((cx, fy2), footer_line2, fill=(130, 125, 155), font=fnt_foot, anchor="mm")


# BEFORE panel
_paste_panel(before_img, 0, "0", "BEFORE", "C** base", is_before=True)

# Concept panels
for i, ((badge, slug, label), img) in enumerate(zip(CONCEPTS, concept_imgs)):
    _paste_panel(img, i + 1, badge, label, "FINAL")

# Separator lines
for i in range(1, N):
    sep_x = MARGIN + i * (PANEL_W + GAP) - GAP // 2
    draw.line([(sep_x, MARGIN + HDR_H), (sep_x, CANVAS_H - MARGIN)],
              fill=(50, 48, 70), width=1)

OUT = os.path.join(BASE_BF2, "showcase.png")
canvas.save(OUT)
print(f"Saved {OUT}  ({CANVAS_W}×{CANVAS_H})")

# PIL verification — BUY button center per panel
BUY_CX_1X  = 58
BTN_CY_355 = round(302 * 355 / 340)
print(f"\n=== PIL verification (BUY button center, y≈{BTN_CY_355}) ===")
verify = Image.open(OUT)
all_ok = True
all_panels = [("0", "BEFORE")] + [(b, s) for b, s, _ in CONCEPTS]
for i, (badge, slug) in enumerate(all_panels):
    px = MARGIN + i * (PANEL_W + GAP)
    py = MARGIN + HDR_H + GAP
    sx = px + BUY_CX_1X
    sy = py + BTN_CY_355
    px_val = verify.getpixel((sx, sy))
    ok = px_val != (8, 8, 20)
    all_ok = all_ok and ok
    print(f"  {badge}: ({sx},{sy}) = {px_val}  {'OK' if ok else 'WARN: background'}")
print(f"All non-background: {'YES' if all_ok else 'SOME FAILED'}")
