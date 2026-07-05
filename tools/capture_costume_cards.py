"""All COSTUME item cards as they appear in the store, composed into one figure.

Each card is rendered via store_cards.render_card (the same call the store
uses at runtime) at live 162x100 resolution, then laid out in a labelled grid.

Run headless from repo root:
    SDL_VIDEODRIVER=dummy python tools/capture_costume_cards.py
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from game import store_catalog, store_cards
from game.hud import _font, _GOLD_PALE, _GOLD_DEEP

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "docs", "store_redesign", "costume", "basketball")
os.makedirs(OUT_DIR, exist_ok=True)

COLS     = 4
CARD_W   = store_cards.CARD_W   # 162
CARD_H   = store_cards.CARD_H   # 100
LABEL_H  = 38
GUTTER   = 14
MARGIN   = 32
TITLE_H  = 64

costumes = sorted(store_catalog.ids_of_group("costume"), key=store_catalog.cost)
rows = (len(costumes) + COLS - 1) // COLS

sheet_w = MARGIN * 2 + COLS * CARD_W + (COLS - 1) * GUTTER
sheet_h = TITLE_H + rows * (CARD_H + LABEL_H + GUTTER) + MARGIN
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((18, 16, 28))

title = _font(22, True).render("COSTUME STORE — ALL ITEM CARDS", True, _GOLD_PALE)
sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 18)))

name_f = _font(13, True)
cost_f = _font(11, False)

for idx, sid in enumerate(costumes):
    col = idx % COLS
    row = idx // COLS
    x = MARGIN + col * (CARD_W + GUTTER)
    y = TITLE_H + row * (CARD_H + LABEL_H + GUTTER)

    card = store_cards.render_card(sid, equipped=False, owned=False)
    sheet.blit(card, (x, y))

    # Highlight the basketball card with a coloured border
    if sid == "skin_basketball":
        pygame.draw.rect(sheet, (235, 180, 0),
                         pygame.Rect(x - 2, y - 2, CARD_W + 4, CARD_H + 4),
                         width=2)

    ly = y + CARD_H + 4
    nt = name_f.render(store_catalog.name(sid), True, _GOLD_PALE)
    sheet.blit(nt, nt.get_rect(midtop=(x + CARD_W // 2, ly)))
    ct = cost_f.render(f"{store_catalog.cost(sid):,} coins", True, (180, 172, 200))
    sheet.blit(ct, ct.get_rect(midtop=(x + CARD_W // 2, ly + 18)))

out = os.path.join(OUT_DIR, "costume_cards.png")
pygame.image.save(sheet, out)
print("SAVED", out, sheet.get_size())
