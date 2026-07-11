"""V3 showcase: 2 rows × 3 panels — BEFORE (current store card) + 5 v3 round-2 concepts."""
import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from PIL import Image, ImageDraw, ImageFont

CARD_W, CARD_H = 324, 200
PAD = 20
LABEL_H = 28
COLS, ROWS = 3, 2
PANEL_W = CARD_W + PAD * 2
PANEL_H = CARD_H + PAD * 2 + LABEL_H
OUT_W = PANEL_W * COLS
OUT_H = PANEL_H * ROWS

BG = (8, 8, 24)

showcase = Image.new("RGBA", (OUT_W, OUT_H), BG + (255,))
draw = ImageDraw.Draw(showcase)

try:
    font = ImageFont.truetype("/home/user/skybit/game/assets/DejaVuSans-Bold.ttf", 18)
except Exception:
    font = ImageFont.load_default()

def place_card(img_path, col, row, label):
    card_img = Image.open(img_path).convert("RGBA")
    if card_img.size != (CARD_W, CARD_H):
        card_img = card_img.resize((CARD_W, CARD_H), Image.LANCZOS)
    x = col * PANEL_W + PAD
    y = row * PANEL_H + PAD
    # Composite with alpha over BG
    bg_patch = Image.new("RGBA", (CARD_W, CARD_H), BG + (255,))
    bg_patch.paste(card_img, (0, 0), card_img)
    showcase.paste(bg_patch, (x, y))
    # Label
    lx = col * PANEL_W + PAD
    ly = row * PANEL_H + PAD + CARD_H + 4
    draw.text((lx + CARD_W // 2, ly + LABEL_H // 2), label, fill=(200, 200, 220), font=font, anchor="mm")

# BEFORE: render the existing store card
from game.store_cards import render_card
before = render_card("skin_kitsune", equipped=False, owned=True)
pygame.image.save(before, "/tmp/before_v3.png")
place_card("/tmp/before_v3.png", 0, 0, "BEFORE (current)")

# V3 round-2 concepts
slots = [
    ("docs/item_card_redesign_v3/diagonal-cut/round_2.png",  1, 0, "DIAGONAL CUT"),
    ("docs/item_card_redesign_v3/pill-badge/round_2.png",    2, 0, "PILL BADGE"),
    ("docs/item_card_redesign_v3/top-shelf/round_2.png",     0, 1, "TOP SHELF"),
    ("docs/item_card_redesign_v3/stamp/round_2.png",         1, 1, "STAMP"),
    ("docs/item_card_redesign_v3/lower-third/round_2.png",   2, 1, "LOWER THIRD"),
]
for path, col, row, label in slots:
    place_card(path, col, row, label)

os.makedirs("docs/item_card_redesign_v3", exist_ok=True)
showcase.save("docs/item_card_redesign_v3/showcase.png")

img = Image.open("docs/item_card_redesign_v3/showcase.png")
w, h = img.size
sz = os.path.getsize("docs/item_card_redesign_v3/showcase.png")
print(f"PIL: {w}x{h}, {sz} bytes")
assert w == OUT_W and h == OUT_H
print("validation OK")
