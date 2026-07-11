"""v5 showcase: BEFORE (current store card) + 5 casino-style v5 round-2 concepts."""
import os, sys
sys.path.insert(0, "/home/user/skybit")
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from PIL import Image, ImageDraw, ImageFont

CARD_W, CARD_H = 324, 200
COLS = 3
GAP  = 18
TOP_PAD  = 60
BOT_PAD  = 32
SIDE_PAD = 24
LABEL_H  = 26

ROW_H = CARD_H + LABEL_H + GAP

TOTAL_W = SIDE_PAD * 2 + COLS * CARD_W + (COLS - 1) * GAP
TOTAL_H = TOP_PAD + ROW_H + GAP + ROW_H + GAP + ROW_H + BOT_PAD

BG = (8, 8, 24)

canvas = Image.new("RGBA", (TOTAL_W, TOTAL_H), BG + (255,))
draw   = ImageDraw.Draw(canvas)

try:
    font_big   = ImageFont.truetype("/home/user/skybit/game/assets/fonts/PressStart2P.ttf", 14)
    font_small = ImageFont.truetype("/home/user/skybit/game/assets/fonts/PressStart2P.ttf", 9)
except Exception:
    font_big   = ImageFont.load_default()
    font_small = font_big

GEM_COLOR = (255, 202, 104)

header = "ITEM CARD REDESIGN — v5 CASINO EDITION"
bbox = draw.textbbox((0, 0), header, font=font_big)
hw = bbox[2] - bbox[0]
draw.text(((TOTAL_W - hw) // 2, 18), header, fill=GEM_COLOR, font=font_big)

col_centers = [
    SIDE_PAD + CARD_W // 2,
    SIDE_PAD + CARD_W + GAP + CARD_W // 2,
    SIDE_PAD + (CARD_W + GAP) * 2 + CARD_W // 2,
]

def place_card(img_path, cx_center, row_y, label, scale_up=False):
    try:
        card_img = Image.open(img_path).convert("RGBA")
    except FileNotFoundError:
        card_img = Image.new("RGBA", (CARD_W, CARD_H), (60, 30, 60, 255))
    if scale_up and card_img.size != (CARD_W, CARD_H):
        card_img = card_img.resize((CARD_W, CARD_H), Image.LANCZOS)
    cx = cx_center - CARD_W // 2
    canvas.paste(card_img, (cx, row_y), card_img)
    lbbox = draw.textbbox((0, 0), label, font=font_small)
    lw = lbbox[2] - lbbox[0]
    draw.text((cx_center - lw // 2, row_y + CARD_H + 6), label, fill=GEM_COLOR, font=font_small)

# ── Row 0: BEFORE ─────────────────────────────────────────────────────────────
row0_y = TOP_PAD
# Generate the current store card as BEFORE reference
try:
    import pygame
    pygame.init()
    pygame.display.set_mode((1, 1))
    from game.store_cards import render_card
    before_surf = render_card('skin_kitsune', equipped=False, owned=False)
    # before_surf is 162×100; smoothscale to 324×200
    before_big = pygame.transform.smoothscale(before_surf, (CARD_W, CARD_H))
    os.makedirs("docs/item_card_redesign_v5", exist_ok=True)
    pygame.image.save(before_big, "docs/item_card_redesign_v5/before_current.png")
    place_card("docs/item_card_redesign_v5/before_current.png", col_centers[1], row0_y, "BEFORE (CURRENT)", scale_up=True)
except Exception:
    # Fallback: look for before card from v4 showcase
    place_card("docs/item_card_redesign_v4/before_current.png", col_centers[1], row0_y, "BEFORE (CURRENT)", scale_up=True)

# ── Row 1: suit-frame, coin-face, stage-reveal ────────────────────────────────
row1_y = row0_y + ROW_H + GAP
cards_row1 = [
    ("docs/item_card_redesign_v5/suit-frame/round_2.png",    "1 — SUIT FRAME"),
    ("docs/item_card_redesign_v5/coin-face/round_2.png",     "2 — COIN FACE"),
    ("docs/item_card_redesign_v5/stage-reveal/round_2.png",  "3 — STAGE REVEAL"),
]
for i, (path, label) in enumerate(cards_row1):
    place_card(path, col_centers[i], row1_y, label)

# ── Row 2: roulette, baroque (centered in 3-col grid) ────────────────────────
row2_y = row1_y + ROW_H + GAP
cards_row2 = [
    ("docs/item_card_redesign_v5/roulette/round_2.png", "4 — ROULETTE ARC"),
    ("docs/item_card_redesign_v5/baroque/round_2.png",  "5 — BAROQUE"),
]
offset_2 = (TOTAL_W - (CARD_W * 2 + GAP)) // 2 + CARD_W // 2
for i, (path, label) in enumerate(cards_row2):
    cx = offset_2 + i * (CARD_W + GAP)
    place_card(path, cx, row2_y, label)

os.makedirs("docs/item_card_redesign_v5", exist_ok=True)
out_path = "docs/item_card_redesign_v5/showcase_combined.png"
canvas.save(out_path)

img = Image.open(out_path)
w, h = img.size
sz = os.path.getsize(out_path)
print(f"Showcase: {w}x{h}, {sz} bytes")
assert w == TOTAL_W and h == TOTAL_H, f"Expected {TOTAL_W}x{TOTAL_H}, got {w}x{h}"
print("validation OK")
