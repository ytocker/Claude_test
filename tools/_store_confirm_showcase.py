"""Phase 5: compose showcase.png from 5 round_2 concept panels."""
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from PIL import Image, ImageDraw, ImageFont

CONCEPTS = [
    ("coin-tab",      "COIN-TAB",      "Split-pill price"),
    ("big-press",     "BIG-PRESS",     "Arcade dome cap"),
    ("buy-then-wear", "BUY-THEN-WEAR", "Pill + caption"),
    ("unlock-latch",  "UNLOCK-LATCH",  "Padlock pill"),
    ("coin-drop",     "COIN-DROP",     "Vending slot"),
]

PANEL_W, PANEL_H = 200, 355
GAP     = 8
MARGIN  = 20
HDR_H   = 40
FOOT_H  = 36

N = len(CONCEPTS)
CANVAS_W = MARGIN + N * PANEL_W + (N - 1) * GAP + MARGIN
CANVAS_H = MARGIN + HDR_H + GAP + PANEL_H + FOOT_H + MARGIN

BG      = (8,  8, 20)
GOLD    = (220,190,100)
CREAM   = (200,185,140)
DIM     = (110,105, 90)
CYAN    = (130,200,200)

try:
    fhdr = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
    flbl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11)
    fsub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9)
except Exception:
    fhdr = flbl = fsub = ImageFont.load_default()

canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), BG)
draw   = ImageDraw.Draw(canvas)

# Header
draw.text(
    (CANVAS_W // 2, MARGIN + HDR_H // 2),
    "STORE CONFIRM POPUP — BUY ACTION BUTTON  ·  5 CONCEPTS  ·  ROUND 2  (AFFORDABLE STATE)",
    fill=GOLD, font=fhdr, anchor="mm",
)

feature_dir = os.path.join(os.path.dirname(__file__), "..", "docs", "store_confirm_popup")

panel_top = MARGIN + HDR_H + GAP

for i, (slug, title, sub) in enumerate(CONCEPTS):
    x0 = MARGIN + i * (PANEL_W + GAP)

    # Load round_2.png and crop affordable (left) panel: popup starts at y=30 in the sheet
    src = Image.open(os.path.join(feature_dir, slug, "round_2.png")).convert("RGB")
    # Each sheet is 460×400; affordable popup (200×340) is at (0, 30)
    # Grab 200×355 including a sliver of the label row for context
    crop_y1 = min(30, src.height - PANEL_H)
    crop = src.crop((0, crop_y1, PANEL_W, crop_y1 + PANEL_H))
    if crop.width != PANEL_W or crop.height != PANEL_H:
        crop = crop.resize((PANEL_W, PANEL_H), Image.LANCZOS)

    canvas.paste(crop, (x0, panel_top))

    # Panel border
    draw.rectangle([x0 - 1, panel_top - 1, x0 + PANEL_W, panel_top + PANEL_H],
                   outline=(40, 38, 60))

    # Footer: slug + sub
    foot_y = panel_top + PANEL_H + 4
    cx = x0 + PANEL_W // 2
    draw.text((cx, foot_y + 9),  title, fill=CREAM, font=flbl, anchor="mm")
    draw.text((cx, foot_y + 22), sub,   fill=DIM,   font=fsub,  anchor="mm")
    draw.text((cx, foot_y + 33), "FINAL", fill=CYAN, font=fsub, anchor="mm")

out = os.path.join(feature_dir, "showcase.png")
canvas.save(out)
w, h = canvas.size
print(f"saved {out} ({w}×{h})")
