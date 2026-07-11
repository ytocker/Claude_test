"""Combined showcase: BEFORE + 5 v2 + 5 v3 round-2 concepts. 4 rows × 3 cols, 324×200 per cell."""
import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from PIL import Image, ImageDraw, ImageFont

CARD_W, CARD_H = 324, 200
PAD_X, PAD_Y = 20, 20
LABEL_H = 30
SECTION_H = 26   # height of the v2/v3 section divider row
COLS = 3
BG  = (8, 8, 24)
DIV = (30, 28, 52)  # divider strip colour

# Build layout: two sections (V2 and V3), each 2 rows × 3 cols, BEFORE in slot (0,0) of V2 section
PANEL_W = CARD_W + PAD_X * 2
PANEL_H = CARD_H + PAD_Y * 2 + LABEL_H

# Total height: header section label + 2 panels + section label + 2 panels
OUT_W = PANEL_W * COLS
OUT_H = SECTION_H + PANEL_H * 2 + SECTION_H + PANEL_H * 2

canvas = Image.new("RGBA", (OUT_W, OUT_H), BG + (255,))
draw = ImageDraw.Draw(canvas)

try:
    font_label = ImageFont.truetype("/home/user/skybit/game/assets/DejaVuSans-Bold.ttf", 16)
    font_sect  = ImageFont.truetype("/home/user/skybit/game/assets/DejaVuSans-Bold.ttf", 14)
except Exception:
    font_label = ImageFont.load_default()
    font_sect  = font_label

def draw_section_header(y, text):
    draw.rectangle([(0, y), (OUT_W, y + SECTION_H)], fill=DIV)
    draw.text((OUT_W // 2, y + SECTION_H // 2), text, fill=(180, 160, 240), font=font_sect, anchor="mm")

def place_card(img_path, col, row_in_section, section_y_offset, label, scale_up=False):
    card_img = Image.open(img_path).convert("RGBA")
    if scale_up:
        card_img = card_img.resize((CARD_W, CARD_H), Image.LANCZOS)
    # Composite card over BG patch
    bg_patch = Image.new("RGBA", (CARD_W, CARD_H), BG + (255,))
    bg_patch.paste(card_img, (0, 0), card_img)
    x = col * PANEL_W + PAD_X
    y = section_y_offset + row_in_section * PANEL_H + PAD_Y
    canvas.paste(bg_patch, (x, y))
    # Label centered below card
    lx = col * PANEL_W + PANEL_W // 2
    ly = y + CARD_H + LABEL_H // 2 + 4
    draw.text((lx, ly), label, fill=(190, 185, 220), font=font_label, anchor="mm")

# --- V2 SECTION ---
v2_y = 0
draw_section_header(v2_y, "ROUND 2  ·  V2 CONCEPTS")
v2_cards_y = v2_y + SECTION_H

# Render the current store card (162×100 logical) and scale up to 324×200
from game.store_cards import render_card as _rc
before = _rc("skin_kitsune", equipped=False, owned=True)
pygame.image.save(before, "/tmp/before_combined.png")
place_card("/tmp/before_combined.png", 0, 0, v2_cards_y, "CURRENT STORE CARD", scale_up=True)

v2_slots = [
    ("docs/item_card_redesign_v2/marquee-stripe/round_2.png",  1, 0, "MARQUEE STRIPE"),
    ("docs/item_card_redesign_v2/triband/round_2.png",         2, 0, "TRIBAND"),
    ("docs/item_card_redesign_v2/lateral-split/round_2.png",   0, 1, "LATERAL SPLIT"),
    ("docs/item_card_redesign_v2/matte-frame/round_2.png",     1, 1, "MATTE FRAME"),
    ("docs/item_card_redesign_v2/radial-spotlight/round_2.png",2, 1, "RADIAL SPOTLIGHT"),
]
for path, col, row, label in v2_slots:
    place_card(path, col, row, v2_cards_y, label)

# --- V3 SECTION ---
v3_y = v2_cards_y + PANEL_H * 2
draw_section_header(v3_y, "ROUND 3  ·  V3 CONCEPTS")
v3_cards_y = v3_y + SECTION_H

v3_slots = [
    ("docs/item_card_redesign_v3/diagonal-cut/round_2.png",  0, 0, "DIAGONAL CUT"),
    ("docs/item_card_redesign_v3/pill-badge/round_2.png",    1, 0, "PILL BADGE"),
    ("docs/item_card_redesign_v3/top-shelf/round_2.png",     2, 0, "TOP SHELF"),
    ("docs/item_card_redesign_v3/stamp/round_2.png",         0, 1, "STAMP"),
    ("docs/item_card_redesign_v3/lower-third/round_2.png",   1, 1, "LOWER THIRD"),
]
for path, col, row, label in v3_slots:
    place_card(path, col, row, v3_cards_y, label)

os.makedirs("docs/item_card_redesign_v3", exist_ok=True)
canvas.save("docs/item_card_redesign_v3/showcase_combined.png")

img = Image.open("docs/item_card_redesign_v3/showcase_combined.png")
w, h = img.size
sz = os.path.getsize("docs/item_card_redesign_v3/showcase_combined.png")
print(f"PIL: {w}x{h}, {sz} bytes")
assert w == OUT_W and h == OUT_H
print("validation OK")
