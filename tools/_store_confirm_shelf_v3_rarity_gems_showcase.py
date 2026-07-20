"""Phase 5 showcase — rarity-gems shelf placement, 5 concepts.

Panels (left to right):
  0  BEFORE   c-orig-bg/round_4.png affordable crop
  A  shelf-corners
  B  lip-bookends
  C  mid-wall-brackets
  D  bottom-overhang
  E  tri-cluster

Canvas: (8,8,20) bg, 200x340 panels, 8px gaps, 20px margins,
        40px header, 32px footer.
Output -> docs/store_confirm_shelf_v3/rarity-gems/showcase.png
"""
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.join(os.path.dirname(__file__), "..")

BG   = (8, 8, 20)
PW, PH = 200, 340
GAP    = 8
MARGIN = 20
HDR_H  = 40
FTR_H  = 32

PANELS = [
    ("0",  "BEFORE",            "docs/store_confirm_shelf_v3/c-orig-bg/round_4.png",                    (18, 54, 218, 394)),
    ("A",  "shelf-corners",     "docs/store_confirm_shelf_v3/rarity-gems/shelf-corners/round_2.png",    (20, 60, 220, 400)),
    ("B",  "lip-bookends",      "docs/store_confirm_shelf_v3/rarity-gems/lip-bookends/round_2.png",     (12, 60, 212, 400)),
    ("C",  "mid-wall-brackets", "docs/store_confirm_shelf_v3/rarity-gems/mid-wall-brackets/round_2.png",(20, 40, 220, 380)),
    ("D",  "bottom-overhang",   "docs/store_confirm_shelf_v3/rarity-gems/bottom-overhang/round_2.png",  (12, 56, 212, 396)),
    ("E",  "tri-cluster",       "docs/store_confirm_shelf_v3/rarity-gems/tri-cluster/round_2.png",      (12, 56, 212, 396)),
]

N = len(PANELS)
CANVAS_W = MARGIN + N * PW + (N - 1) * GAP + MARGIN
CANVAS_H = MARGIN + HDR_H + PH + FTR_H + MARGIN

canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), BG)
draw   = ImageDraw.Draw(canvas)

try:
    fnt_hdr  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    fnt_ftr  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    fnt_badg = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)
except Exception:
    fnt_hdr = fnt_ftr = fnt_badg = ImageFont.load_default()

# Header
draw.text(
    (CANVAS_W // 2, MARGIN + HDR_H // 2),
    "Rarity Gems — shelf placement concepts",
    fill=(220, 215, 248),
    font=fnt_hdr,
    anchor="mm",
)

for i, (badge, slug, rel_path, crop) in enumerate(PANELS):
    px = MARGIN + i * (PW + GAP)
    py = MARGIN + HDR_H

    # Load and crop panel
    src = Image.open(os.path.join(BASE, rel_path))
    panel = src.crop(crop)
    if panel.size != (PW, PH):
        panel = panel.resize((PW, PH), Image.LANCZOS)
    canvas.paste(panel, (px, py))

    # ID badge — dark pill, top-left corner of panel
    bx, by = px + 5, py + 5
    bw = int(fnt_badg.getlength(badge)) + 8
    bh = 17
    # lavender outline
    draw.rounded_rectangle([bx - 1, by - 1, bx + bw + 1, by + bh + 1],
                            radius=5, fill=(170, 160, 220))
    # dark fill
    draw.rounded_rectangle([bx, by, bx + bw, by + bh],
                            radius=4, fill=(24, 22, 38))
    draw.text((bx + 4, by + bh // 2), badge,
              fill=(230, 225, 245), font=fnt_badg, anchor="lm")

    # Footer
    fy = py + PH + 6
    draw.text((px + PW // 2, fy + FTR_H // 2 - 4), slug,
              fill=(180, 175, 210) if badge != "0" else (140, 145, 165),
              font=fnt_ftr, anchor="mm")

OUT = os.path.abspath(os.path.join(BASE,
      "docs", "store_confirm_shelf_v3", "rarity-gems", "showcase.png"))
canvas.save(OUT)
print(f"Saved {OUT}  ({CANVAS_W}x{CANVAS_H})")

# Verification: each panel's BUY-area center must be non-background
print("\n=== Panel center checks ===")
for i, (badge, slug, _, _) in enumerate(PANELS):
    px = MARGIN + i * (PW + GAP)
    py = MARGIN + HDR_H
    # BUY button center in panel coords: BUY_CX=58, BTN_CY=302
    cx, cy = px + 58, py + 302
    p = canvas.getpixel((cx, cy))
    status = "ok" if p != BG else "WARN bg"
    print(f"  {badge} ({badge}) BUY-center ({cx},{cy}): {p}  {status}")
