#!/usr/bin/env python3
"""Figure: 4 card states (2×2 grid) + buy-confirmation popup, side by side."""
import os, sys, tempfile
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pygame; pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
import game.store_data as sd
import game.store_catalog as catalog
from game.config import W, H
from game.store import StoreScene

sd.load()
SID    = "skin_mummy"
CW, CH = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS   # 324 × 200
RECT   = pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                     CW - 2 * sc.m(sc._INSET), CH - 2 * sc.m(sc._INSET))
pal    = sc.RARITY[catalog.rarity(SID)]

tmp = tempfile.mkdtemp()

def surf_to_pil(surf, name):
    from PIL import Image
    path = os.path.join(tmp, f"{name}.png")
    pygame.image.save(surf, path)
    return Image.open(path).convert("RGB")


# ── Render 4 card states ──────────────────────────────────────────────────────

def card(label, equipped, owned, balance=None):
    sc._card_cache.clear()
    if balance is not None:
        _orig = sd.balance; sd.balance = lambda: balance
    s = pygame.Surface((CW, CH), pygame.SRCALPHA)
    sc.draw_card(s, SID, RECT, equipped, False, owned=owned)
    if balance is not None:
        sd.balance = _orig
    sc._card_cache.clear()
    return surf_to_pil(s, label)

cards = {
    "unaffordable": card("unaffordable", False, False, balance=0),
    "affordable":   card("affordable",   False, False, balance=999_999),
    "owned":        card("owned",        False, True),
    "equipped":     card("equipped",     True,  False),
}

GRID = [
    ("unaffordable", "UNAFFORDABLE", "(grey price tag)"),
    ("affordable",   "AFFORDABLE",   "(cream price tag)"),
    ("owned",        "OWNED",        "(gem badge)"),
    ("equipped",     "EQUIPPED",     "(check tag + frame)"),
]


# ── Render buy-confirmation popup via StoreScene (exact in-game rendering) ────

POP_W, POP_H = 200, 340

def render_popup(affordable):
    """Render the popup exactly as the game does: full store scene, popup on top,
    then crop the popup region."""
    _orig_balance = sd.balance
    sd.balance = lambda: (999_999 if affordable else 0)
    sc._card_cache.clear()

    scene = StoreScene()
    scene.view     = "category"
    scene._confirm = SID

    screen = pygame.Surface((W, H))
    scene.render(screen)

    sd.balance = _orig_balance
    sc._card_cache.clear()

    # Crop the popup region (same calculation as _draw_confirm)
    px = (W - POP_W) // 2
    py = (H - POP_H) // 2
    path = os.path.join(tmp, f"screen_{'aff' if affordable else 'unaff'}.png")
    pygame.image.save(screen, path)
    from PIL import Image
    im = Image.open(path).convert("RGB")
    return im.crop((px, py, px + POP_W, py + POP_H))

popup_affordable   = render_popup(affordable=True)
popup_unaffordable = render_popup(affordable=False)


# ── Compose PIL canvas ────────────────────────────────────────────────────────
from PIL import Image, ImageDraw, ImageFont

try:
    font_hdr = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
    font_lbl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    font_sec = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
except Exception:
    font_hdr = font_lbl = font_sub = font_sec = ImageFont.load_default()

BG    = (8,  8,  20)
GOLD  = (220, 190, 100)
CREAM = (200, 185, 140)
DIM   = (90,  85,  70)
GRN   = (140, 200, 140)
CYAN  = (130, 200, 200)

MARGIN  = 20
GAP     = 10
LABEL_H = 36
HDR_H   = 44
DIVIDER = 28      # gap between card grid and popup columns
SEC_H   = 22      # section sub-header height

POP_W_D, POP_H_D = 200, 340   # popup display size

# Card grid: 2 cols × 2 rows
CARD_GRID_COLS = 2
CARD_GRID_ROWS = 2
GRID_W = CARD_GRID_COLS * CW + (CARD_GRID_COLS - 1) * GAP
GRID_H = CARD_GRID_ROWS * (CH + LABEL_H) + (CARD_GRID_ROWS - 1) * GAP

# Two popups side by side (affordable + unaffordable)
POP_PAIR_W = 2 * POP_W_D + GAP
POP_PAIR_H = SEC_H + GAP + POP_H_D

CONTENT_H = max(GRID_H, POP_PAIR_H)

canvas_w = MARGIN + GRID_W + DIVIDER + POP_PAIR_W + MARGIN
canvas_h = MARGIN + HDR_H + GAP + SEC_H + GAP + CONTENT_H + MARGIN

canvas = Image.new("RGB", (canvas_w, canvas_h), BG)
draw   = ImageDraw.Draw(canvas)

# Header
draw.text((canvas_w // 2, MARGIN + HDR_H // 2),
          "STORE CARD — ALL STATES + BUY POPUP",
          fill=GOLD, font=font_hdr, anchor="mm")

content_y = MARGIN + HDR_H + GAP

# ── Section headers ──────────────────────────────────────────────────────────
cards_x0    = MARGIN
popups_x0   = MARGIN + GRID_W + DIVIDER

draw.text((cards_x0 + GRID_W // 2,  content_y + SEC_H // 2),
          "CARD STATES", fill=CREAM, font=font_sec, anchor="mm")
draw.text((popups_x0 + POP_PAIR_W // 2, content_y + SEC_H // 2),
          "BUY POPUP (AFFORDABLE / NOT ENOUGH COINS)",
          fill=CREAM, font=font_sec, anchor="mm")

grid_y = content_y + SEC_H + GAP

# ── 2×2 card grid ────────────────────────────────────────────────────────────
for idx, (key, title, sub) in enumerate(GRID):
    col = idx % 2
    row = idx // 2
    x0  = cards_x0 + col * (CW + GAP)
    y0  = grid_y   + row * (CH + LABEL_H + GAP)
    canvas.paste(cards[key], (x0, y0))
    label_cy = y0 + CH + LABEL_H // 2
    title_col = GRN if key == "owned" else CREAM
    draw.text((x0 + CW // 2, label_cy - 9), title, fill=title_col, font=font_lbl, anchor="mm")
    draw.text((x0 + CW // 2, label_cy + 9), sub,   fill=DIM,        font=font_sub, anchor="mm")

# ── Popup pair ────────────────────────────────────────────────────────────────
pop_y = grid_y
for i, (pop_img, label) in enumerate([
        (popup_affordable,   "AFFORDABLE"),
        (popup_unaffordable, "NOT ENOUGH COINS")]):
    px = popups_x0 + i * (POP_W_D + GAP)
    canvas.paste(pop_img, (px, pop_y))
    draw.text((px + POP_W_D // 2, pop_y + POP_H_D + 12),
              label, fill=CYAN, font=font_sub, anchor="mm")

out_dir = "docs/store_owned_v2"
os.makedirs(out_dir, exist_ok=True)
out = os.path.join(out_dir, "card_states_and_popup_v2.png")
canvas.save(out)
print(f"saved {out} ({canvas.width}x{canvas.height})")
