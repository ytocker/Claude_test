"""Minimal 2-card side-by-side preview: Design 1 (Suit Frame) + Design 5 (Baroque)."""
import os
from PIL import Image, ImageDraw, ImageFont

CARD_W, CARD_H = 324, 200
GAP      = 18
SIDE_PAD = 20
TOP_PAD  = 40
BOT_PAD  = 24
LABEL_H  = 22

TOTAL_W = SIDE_PAD * 2 + CARD_W * 2 + GAP
TOTAL_H = TOP_PAD + CARD_H + LABEL_H + BOT_PAD

BG  = (8, 8, 24)
GEM = (255, 202, 104)

canvas = Image.new("RGBA", (TOTAL_W, TOTAL_H), BG + (255,))
draw   = ImageDraw.Draw(canvas)

try:
    font = ImageFont.truetype("/home/user/skybit/game/assets/fonts/PressStart2P.ttf", 9)
except Exception:
    font = ImageFont.load_default()

cards = [
    ("docs/item_card_redesign_v5/suit-frame/round_2.png", "1 — SUIT FRAME"),
    ("docs/item_card_redesign_v5/baroque/round_2.png",    "5 — BAROQUE"),
]

for i, (path, label) in enumerate(cards):
    x = SIDE_PAD + i * (CARD_W + GAP)
    try:
        img = Image.open(path).convert("RGBA")
    except FileNotFoundError:
        img = Image.new("RGBA", (CARD_W, CARD_H), (60, 30, 60, 255))
    canvas.paste(img, (x, TOP_PAD), img)
    bbox = draw.textbbox((0, 0), label, font=font)
    lw = bbox[2] - bbox[0]
    draw.text((x + (CARD_W - lw) // 2, TOP_PAD + CARD_H + 6), label, fill=GEM, font=font)

os.makedirs("docs/item_card_redesign_v5", exist_ok=True)
out = "docs/item_card_redesign_v5/preview_1_5.png"
canvas.save(out)

img = Image.open(out)
w, h = img.size
sz = os.path.getsize(out)
print(f"Preview: {w}x{h}, {sz} bytes")
assert w == TOTAL_W and h == TOTAL_H
print("validation OK")
