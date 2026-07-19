#!/usr/bin/env python3
"""4-states card figure: Unaffordable | Affordable | Owned (gem) | Equipped"""
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pygame; pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
import game.store_data as sd
from game import store_catalog

sd.load()
SID = "skin_mummy"

CW, CH = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS   # 324 × 200
CARD_RECT = pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                        CW - 2 * sc.m(sc._INSET), CH - 2 * sc.m(sc._INSET))

BG    = (8, 8, 20)
GAP   = 16
MARGIN = 20
LABEL_H = 36
HEADER_H = 48

N = 4
canvas_w = MARGIN + N * CW + (N - 1) * GAP + MARGIN
canvas_h = MARGIN + HEADER_H + GAP + CH + GAP + LABEL_H + MARGIN

import pygame.font as pf
from PIL import Image, ImageDraw, ImageFont

# Render the 4 cards via pygame, then compose with PIL
cards = {}

cost = sc._cost(SID)
pal  = sc.RARITY[store_catalog.rarity(SID)]

# ── State 0: UNAFFORDABLE ────────────────────────────────────────────────────
_orig_balance = sd.balance
sd.balance = lambda: 0   # force unaffordable
s0 = pygame.Surface((CW, CH), pygame.SRCALPHA)
sc.draw_card(s0, SID, CARD_RECT, False, False, owned=False)
sd.balance = _orig_balance
cards["unaffordable"] = s0

# ── State 1: AFFORDABLE ──────────────────────────────────────────────────────
_orig_balance2 = sd.balance
sd.balance = lambda: 999_999   # force affordable
s1 = pygame.Surface((CW, CH), pygame.SRCALPHA)
sc.draw_card(s1, SID, CARD_RECT, False, False, owned=False)
sd.balance = _orig_balance2
cards["affordable"] = s1

# ── State 2: OWNED (top-left gem, no hang-tag) ───────────────────────────────
s2 = pygame.Surface((CW, CH), pygame.SRCALPHA)
_orig_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None
sc.draw_card(s2, SID, CARD_RECT, False, False, owned=False)
sc.state_chip = _orig_chip
# Mirror the rarity gem to top-left corner
gem_cx = CARD_RECT.x + sc.m(19)
gem_cy = CARD_RECT.y + sc.m(19)
gem_r  = sc.m(sc.GEM_R + 3)
sc.facet_gem(s2, gem_cx, gem_cy, gem_r, pal["gem"], pal["deep"])
cards["owned"] = s2

# ── State 3: EQUIPPED (check-tag + regalia frame) ────────────────────────────
s3 = pygame.Surface((CW, CH), pygame.SRCALPHA)
sc.draw_card(s3, SID, CARD_RECT, True, False, owned=False)
cards["equipped"] = s3

# ── Save each card surface to a temp PNG via pygame, load in PIL ──────────────
import tempfile
tmp_dir = tempfile.mkdtemp()

def surf_to_pil(surf, name):
    path = os.path.join(tmp_dir, f"{name}.png")
    pygame.image.save(surf, path)
    return Image.open(path).convert("RGB")

pil_cards = {k: surf_to_pil(v, k) for k, v in cards.items()}

# ── Compose PIL canvas ────────────────────────────────────────────────────────
canvas = Image.new("RGB", (canvas_w, canvas_h), BG)
draw   = ImageDraw.Draw(canvas)

try:
    font_hdr = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    font_lbl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
except Exception:
    font_hdr = ImageFont.load_default()
    font_lbl = font_hdr
    font_sub = font_hdr

GOLD  = (220, 190, 100)
CREAM = (200, 185, 140)
DIM   = (90, 85, 70)
GRN   = (140, 200, 140)

draw.text(
    (canvas_w // 2, MARGIN + HEADER_H // 2),
    "STORE CARD STATES",
    fill=GOLD, font=font_hdr, anchor="mm",
)

STATE_LABELS = [
    ("UNAFFORDABLE", "(grey price tag)"),
    ("AFFORDABLE",   "(cream price tag)"),
    ("OWNED",        "(gem badge — chosen)"),
    ("EQUIPPED",     "(check tag + frame)"),
]

for i, (key, (title, sub)) in enumerate(zip(
        ["unaffordable", "affordable", "owned", "equipped"], STATE_LABELS)):
    x0 = MARGIN + i * (CW + GAP)
    y0 = MARGIN + HEADER_H + GAP
    canvas.paste(pil_cards[key], (x0, y0))

    label_cy = y0 + CH + LABEL_H // 2
    title_col = GRN if key == "owned" else CREAM
    draw.text((x0 + CW // 2, label_cy - 9), title,  fill=title_col, font=font_lbl, anchor="mm")
    draw.text((x0 + CW // 2, label_cy + 9), sub,    fill=DIM,       font=font_sub, anchor="mm")

out_dir = "docs/store_owned_v2"
os.makedirs(out_dir, exist_ok=True)
out = os.path.join(out_dir, "states_figure.png")
canvas.save(out)
print(f"saved {out} ({canvas.width}x{canvas.height})")
