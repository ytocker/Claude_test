"""Phase 5: compose showcase.png from 5 round_2 concept panels for store_confirm_popup_v3."""
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from PIL import Image, ImageDraw, ImageFont

# Each entry: (slug, display title, subtitle)
# Sheet layout for all v3 concepts: affordable panel at (0, 30) in a 460x400 sheet.
# Crop: (ox, oy, ox+PANEL_W, oy+PANEL_H)
CONCEPTS = [
    ("coin-platform",  "COIN-PLATFORM",  "Cream plinth pedestal",   0, 30, 1),
    ("wide-oval",      "WIDE-OVAL",      "Stadium price oval",       0, 30, 1),
    ("arch-panel",     "ARCH-PANEL",     "Romanesque bell arch",     0, 30, 1),
    ("coin-tab",       "COIN-TAB",       "Folder-tab + bar",         0, 30, 1),
    ("segmented-bar",  "SEGMENTED-BAR",  "Machined triptych bar",    0, 30, 1),
]

PANEL_W, PANEL_H = 200, 355
GAP     = 8
MARGIN  = 20
HDR_H   = 40
FOOT_H  = 36

N = len(CONCEPTS)
CANVAS_W = MARGIN + N * PANEL_W + (N - 1) * GAP + MARGIN
CANVAS_H = MARGIN + HDR_H + GAP + PANEL_H + FOOT_H + MARGIN

BG    = (8,  8, 20)
GOLD  = (220, 190, 100)
CREAM = (200, 185, 140)
DIM   = (110, 105, 90)
CYAN  = (130, 200, 200)

try:
    fhdr = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
    flbl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11)
    fsub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9)
except Exception:
    fhdr = flbl = fsub = ImageFont.load_default()

canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), BG)
draw   = ImageDraw.Draw(canvas)

draw.text(
    (CANVAS_W // 2, MARGIN + HDR_H // 2),
    "STORE CONFIRM POPUP V3 — 5 CONCEPTS — ROUND 2  (AFFORDABLE STATE)",
    fill=GOLD, font=fhdr, anchor="mm",
)

feature_dir = os.path.join(os.path.dirname(__file__), "..", "docs", "store_confirm_popup_v3")
panel_top = MARGIN + HDR_H + GAP

for i, (slug, title, sub, ox, oy, scale) in enumerate(CONCEPTS):
    x0 = MARGIN + i * (PANEL_W + GAP)

    src = Image.open(os.path.join(feature_dir, slug, "round_2.png")).convert("RGB")

    if scale == 1:
        crop_h = min(PANEL_H, src.height - oy)
        crop = src.crop((ox, oy, ox + PANEL_W, oy + crop_h))
        if crop.height < PANEL_H:
            padded = Image.new("RGB", (PANEL_W, PANEL_H), BG)
            padded.paste(crop, (0, 0))
            crop = padded
    else:
        crop_h_2x = min(PANEL_H * scale, src.height - oy)
        crop_2x = src.crop((ox, oy, ox + PANEL_W * scale, oy + crop_h_2x))
        crop = crop_2x.resize((PANEL_W, PANEL_H), Image.LANCZOS)

    canvas.paste(crop, (x0, panel_top))

    draw.rectangle(
        [x0 - 1, panel_top - 1, x0 + PANEL_W, panel_top + PANEL_H],
        outline=(40, 38, 60),
    )

    foot_y = panel_top + PANEL_H + 4
    cx = x0 + PANEL_W // 2
    draw.text((cx, foot_y + 9),  title, fill=CREAM, font=flbl, anchor="mm")
    draw.text((cx, foot_y + 22), sub,   fill=DIM,   font=fsub, anchor="mm")
    draw.text((cx, foot_y + 33), "FINAL", fill=CYAN, font=fsub, anchor="mm")

out = os.path.join(feature_dir, "showcase.png")
canvas.save(out)
w, h = canvas.size
print(f"saved {out} ({w}×{h})")
