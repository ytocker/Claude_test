"""Catalog figure of every ANIMALS-category store card.

Crops each real store item card (via StoreScene.item_rects) out of the live
App._render and tiles all of them in one labeled grid, so the whole ANIMALS
inventory is visible at a glance. Secret items are shown REVEALED (their art +
name) with a MYSTERY tag — in the live store they read as masked ??? until
bought.

Pure capture, no production art touched, no save written. Run headless:
``SDL_VIDEODRIVER=dummy python tools/capture_store_animals_cards.py``.
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import sys
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

import pygame
pygame.init()

from game import store_catalog, store_data
from game.scenes import App, STATE_STORE
from game.store import StoreScene, _GROUP_TAB, _PER_PAGE
from game.hud import _font, _GOLD_PALE, _GOLD_DEEP

OUT_DIR = os.path.join(_ROOT, "docs", "store_redesign", "animal", "sun")
os.makedirs(OUT_DIR, exist_ok=True)

ANIMAL_TAB = _GROUP_TAB["animal"]
IDS = sorted(store_catalog.ids_of_group("animal"), key=store_catalog.cost)
SCALE = 1.7


def _reveal_all_owned() -> None:
    """Mark every animal item owned in-memory (never saved) so secret cards
    render revealed instead of masked ???."""
    st = store_data._ensure()
    have = set(st.get("owned", []))
    st["owned"] = list(have | set(IDS))
    # give variant skins a deterministic look for the catalog
    st.setdefault("skin_variants", {})
    for sid in ("skin_sun", "skin_jet_fighter"):
        if sid in IDS:
            st["skin_variants"][sid] = 0
    for mod in ("animal_sun", "animal_jet_fighter"):
        try:
            __import__("game." + mod, fromlist=["sync_from_store"]).sync_from_store()
        except Exception:
            pass


def _grab_cards() -> dict:
    """sid -> upscaled card Surface, cropped from the real store render."""
    _reveal_all_owned()
    app = App()
    app._cooldown_t = 0.0
    app._fetch_pending = False
    app.store = StoreScene()
    app.state = STATE_STORE
    app.store.view = "category"
    app.store.tab = ANIMAL_TAB
    cards = {}
    for p in range((len(IDS) + _PER_PAGE - 1) // _PER_PAGE):
        app.store.page = p
        app.store.update(0.0)
        app._render()
        for sid, r in app.store.item_rects.items():
            pad = 5
            rect = pygame.Rect(r.x - pad, r.y - pad, r.w + pad * 2, r.h + pad * 2)
            rect.clamp_ip(app.screen.get_rect())
            card = app.screen.subsurface(rect).copy()
            cards[sid] = pygame.transform.smoothscale(
                card, (int(rect.w * SCALE), int(rect.h * SCALE)))
    return cards


def main() -> str:
    cards = _grab_cards()
    cw, ch = next(iter(cards.values())).get_size()
    COLS = 4
    rows = (len(IDS) + COLS - 1) // COLS
    MARGIN, GUTX, GUTY, TITLE_H, LABEL_H = 30, 26, 34, 86, 30
    cell_w, cell_h = cw, ch + LABEL_H
    sheet_w = MARGIN * 2 + COLS * cell_w + (COLS - 1) * GUTX
    sheet_h = TITLE_H + MARGIN + rows * cell_h + (rows - 1) * GUTY + MARGIN
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 16, 28))

    title = _font(30, True).render("ANIMALS CATEGORY — ALL STORE CARDS (28 skins, by price)",
                                   True, _GOLD_PALE)
    sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 16)))
    sub = _font(14, True).render(
        "Secret items shown revealed (they read as masked  ??? MYSTERY  in the live store until bought).",
        True, (190, 182, 210))
    sheet.blit(sub, sub.get_rect(midtop=(sheet_w // 2, 52)))

    name_font = _font(14, True)
    for idx, sid in enumerate(IDS):
        col, row = idx % COLS, idx // COLS
        x = MARGIN + col * (cell_w + GUTX)
        y = TITLE_H + MARGIN + row * (cell_h + GUTY)
        sheet.blit(cards[sid], (x, y))
        secret = store_catalog.is_secret(sid)
        nm = store_catalog.name(sid) + ("  · ???" if secret else "")
        col_c = (255, 210, 90) if secret else _GOLD_PALE
        lbl = name_font.render(nm, True, col_c)
        sheet.blit(lbl, lbl.get_rect(midtop=(x + cw // 2, y + ch + 5)))

    out = os.path.join(OUT_DIR, "animals_category_cards.png")
    pygame.image.save(sheet, out)
    print("SAVED", out, sheet.get_size())
    return out


if __name__ == "__main__":
    main()
