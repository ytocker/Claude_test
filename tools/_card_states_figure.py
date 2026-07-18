"""Four card states side by side: unaffordable, affordable, owned, equipped."""
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
import game.store_data as sd
from game.hud import _font as hud_font

sd.load()

SID = "skin_mummy"
PANEL_W, PANEL_H = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS
ri   = sc.m(sc._INSET)
rect = pygame.Rect(ri, ri, PANEL_W - 2 * ri, PANEL_H - 2 * ri)
BG    = (8, 8, 20)
GOLD  = (236, 202, 116)
CREAM = (250, 246, 232)
DIM   = (160, 155, 135)

import game.store_catalog as cat
PRICE = cat.cost(SID)


def _render(equipped, owned, balance_override):
    _orig_balance = sd.balance
    sd.balance = lambda: balance_override
    sc._card_cache.clear()
    surf = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    sc.draw_card(surf, SID, rect, equipped=equipped, secret=False, owned=owned)
    sd.balance = _orig_balance
    sc._card_cache.clear()
    return surf


# (label, sub-label, equipped, owned, balance)
STATES = [
    ("UNAFFORDABLE", f"balance < {PRICE:,}G",  False, False, PRICE - 1),
    ("AFFORDABLE",   f"balance ≥ {PRICE:,}G",  False, False, PRICE),
    ("OWNED",        "already purchased",       False, True,  PRICE),
    ("EQUIPPED",     "active / selected",       True,  True,  PRICE),
]

panels = [_render(eq, ow, bal) for _, _, eq, ow, bal in STATES]

# ── Canvas ────────────────────────────────────────────────────────────────────
N      = len(panels)
PAD    = 20
GAP    = 16
HDR_H  = 48
LBL_H  = 32
FTR_H  = 38
width  = PAD + N * PANEL_W + (N - 1) * GAP + PAD
height = PAD + HDR_H + LBL_H + PANEL_H + FTR_H + PAD

canvas = pygame.Surface((width, height))
canvas.fill(BG)

title_f = hud_font(22, True)
tt = title_f.render("item card · four states", True, GOLD)
canvas.blit(tt, tt.get_rect(midtop=(width // 2, PAD // 2 + 4)))

lbl_f = hud_font(15, True)
sub_f = hud_font(12, False)
panel_y = PAD + HDR_H + LBL_H

for i, ((label, sublabel, *_), panel) in enumerate(zip(STATES, panels)):
    px  = PAD + i * (PANEL_W + GAP)
    mid = px + PANEL_W // 2

    lt = lbl_f.render(label, True, GOLD)
    canvas.blit(lt, lt.get_rect(midbottom=(mid, panel_y - 6)))
    canvas.blit(panel, (px, panel_y))

    st = sub_f.render(sublabel, True, DIM)
    canvas.blit(st, st.get_rect(midtop=(mid, panel_y + PANEL_H + 6)))

OUT = "docs/store_equipped_v3_2_checkmarks/card_states_v2.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(canvas, OUT)
print(f"saved {width}×{height} → {OUT}")
