"""Phase 5 showcase: equipped state v3 — BEFORE + 5 concept panels."""
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
CARD_W, CARD_H = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS  # 324×200
# Panel height matches charm_drop's taller canvas (pendant hangs below)
PANEL_W = CARD_W   # 324
PANEL_H = 240

BG = (8, 8, 20)

# ── BEFORE panel (stock equipped — green chip reference) ─────────────────
sc._card_cache.clear()
before_card = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
ri = sc.m(sc._INSET)
rect_card = pygame.Rect(ri, ri, CARD_W - 2 * ri, CARD_H - 2 * ri)
sc.draw_card(before_card, SID, rect_card, equipped=True, secret=False)
sc._card_cache.clear()

before_panel = pygame.Surface((PANEL_W, PANEL_H))
before_panel.fill(BG)
before_panel.blit(before_card, (0, 0))

# ── concept panels — crop concept panel (x=700, y=102) from round_2.png ──
# charm_drop panel is 240px tall (pendant extends below card); others 200px
CONCEPTS = [
    ("victory_sash",  "VICTORY SASH",  200),
    ("claw_setting",  "CLAW SETTING",  200),
    ("regalia_frame", "REGALIA FRAME", 200),
    ("charm_drop",    "CHARM DROP",    240),
    ("inset_plinth",  "INSET PLINTH",  200),
]

panels = [("BEFORE", before_panel)]
for slug, label, ph in CONCEPTS:
    path = os.path.join("docs/store_equipped_v3", slug, "round_2.png")
    img = pygame.image.load(path).convert()
    sub = img.subsurface(pygame.Rect(700, 102, PANEL_W, ph))
    panel = pygame.Surface((PANEL_W, PANEL_H))
    panel.fill(BG)
    panel.blit(sub, (0, 0))
    panels.append((label, panel))

# ── layout ────────────────────────────────────────────────────────────────
PAD   = 20
GAP   = 8
HDR_H = 40
FTR_H = 32
N     = len(panels)  # 6

sheet_w = PAD + N * PANEL_W + (N - 1) * GAP + PAD
sheet_h = PAD + HDR_H + PANEL_H + FTR_H + PAD

showcase = pygame.Surface((sheet_w, sheet_h))
showcase.fill(BG)

fh = hud_font(15, True)
fl = hud_font(11, True)

title = fh.render("store card — EQUIPPED state v3 · 5 design concepts",
                  True, (240, 224, 180))
showcase.blit(title, ((sheet_w - title.get_width()) // 2,
                       PAD + (HDR_H - title.get_height()) // 2))

y_panels = PAD + HDR_H
for i, (label, surf) in enumerate(panels):
    x = PAD + i * (PANEL_W + GAP)
    showcase.blit(surf, (x, y_panels))
    col = (170, 166, 190) if i == 0 else (255, 226, 120)
    t = fl.render(label, True, col)
    y_lbl = y_panels + PANEL_H + (FTR_H - t.get_height()) // 2
    showcase.blit(t, (x + (PANEL_W - t.get_width()) // 2, y_lbl))

out = "docs/store_equipped_v3/showcase.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(showcase, out)
print(f"saved {sheet_w}×{sheet_h} → {out}")
