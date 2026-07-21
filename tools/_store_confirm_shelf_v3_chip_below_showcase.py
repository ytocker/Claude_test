"""Phase 5 showcase: chip-below layout options (BEFORE + A–E)."""
from PIL import Image, ImageDraw, ImageFont
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PANELS = [
    ("0", "BEFORE",       "docs/store_confirm_shelf_v3/c-orig-bg/round_4.png"),
    ("A", "full-raise",   "docs/store_confirm_shelf_v3/chip-below/full-raise/round_2.png"),
    ("B", "buttons-lift", "docs/store_confirm_shelf_v3/chip-below/buttons-lift/round_2.png"),
    ("C", "slim-buttons", "docs/store_confirm_shelf_v3/chip-below/slim-buttons/round_2.png"),
    ("D", "shelf-notch",  "docs/store_confirm_shelf_v3/chip-below/shelf-notch/round_2.png"),
    ("E", "shelf-expands","docs/store_confirm_shelf_v3/chip-below/shelf-expands/round_2.png"),
]

CROP = (18, 54, 218, 394)   # → 200 × 340
PW, PH = 200, 340
GAP = 8
MARGIN = 20
HEADER_H = 40
FOOTER_H = 32

N = len(PANELS)
W = MARGIN + N * PW + (N - 1) * GAP + MARGIN
H = MARGIN + HEADER_H + GAP + PH + FOOTER_H + MARGIN

BG      = (8, 8, 20)
PILL_BG = (24, 22, 38, 220)
PILL_OUT= (170, 160, 220)
CREAM   = (230, 225, 245)
TITLE_C = (210, 205, 240)
FOOT_C  = (160, 155, 190)

def load_panel(path, crop):
    img = Image.open(os.path.join(BASE, path)).convert("RGB")
    return img.crop(crop).resize((PW, PH), Image.LANCZOS)

def draw_badge(draw, x, y, label, font):
    pad_x, pad_y = 7, 4
    tw = font.getlength(label)
    bw = int(tw) + pad_x * 2
    bh = 12 + pad_y * 2
    rx = 4
    draw.rounded_rectangle([x, y, x + bw, y + bh], radius=rx, fill=PILL_BG, outline=PILL_OUT, width=1)
    draw.text((x + pad_x, y + pad_y - 1), label, font=font, fill=CREAM)

def main():
    canvas = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(canvas)

    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        font_foot  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        font_badge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)
    except Exception:
        font_title = ImageFont.load_default()
        font_foot  = font_title
        font_badge = font_title

    title = "Chip below buttons — layout options"
    tw = draw.textlength(title, font=font_title)
    draw.text(((W - tw) / 2, MARGIN + (HEADER_H - 16) // 2), title, font=font_title, fill=TITLE_C)

    panels_y = MARGIN + HEADER_H + GAP

    for i, (badge_id, slug, rel_path) in enumerate(PANELS):
        px = MARGIN + i * (PW + GAP)
        panel = load_panel(rel_path, CROP)
        canvas.paste(panel, (px, panels_y))
        draw.rectangle([px, panels_y, px + PW - 1, panels_y + PH - 1],
                       outline=(50, 48, 70), width=1)
        draw_badge(draw, px + 5, panels_y + 5, badge_id, font_badge)
        fy = panels_y + PH + 6
        fw = draw.textlength(slug, font=font_foot)
        draw.text((px + (PW - fw) / 2, fy), slug, font=font_foot, fill=FOOT_C)

    out_dir = os.path.join(BASE, "docs/store_confirm_shelf_v3/chip-below")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "showcase.png")
    canvas.save(out)
    print(f"Saved {out}  ({W}×{H})")
    img = Image.open(out)
    print(f"PIL verify: size={img.size}")

if __name__ == "__main__":
    main()
