"""Store-category figure for the new mystery SUN item.

Real, pixel-faithful captures of the ANIMALS store tab (App._render):
  * Row A — all 4 ANIMALS pages side by side (the current category; the SUN
    shows masked as ??? on page 3 like the other secret flyers).
  * Row B — page 3 with the SUN UNLOCKED, rendered once per rolled variant
    (CLASSIC / KAWAII), so you can see what the ??? reveals to.

Pure capture, no production art touched, no save written. Run headless:
``SDL_VIDEODRIVER=dummy python tools/capture_store_sun.py``.
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

from game import store_catalog, store_data, animal_sun
from game.scenes import App, STATE_STORE
from game.store import StoreScene, _GROUP_TAB, _PER_PAGE
from game.hud import _font, _GOLD_PALE, _GOLD_DEEP

try:
    from game import store_cards
except Exception:
    store_cards = None

OUT_DIR = os.path.join(_ROOT, "docs", "store_redesign", "animal", "sun")
os.makedirs(OUT_DIR, exist_ok=True)

ANIMAL_TAB = _GROUP_TAB["animal"]
SUN_IDS = sorted(store_catalog.ids_of_group("animal"), key=store_catalog.cost)
SUN_PAGE = SUN_IDS.index("skin_sun") // _PER_PAGE      # 0-based


def _new_app() -> App:
    app = App()
    app._cooldown_t = 0.0
    app._fetch_pending = False
    app.store = StoreScene()
    app.state = STATE_STORE
    app.store.view = "category"        # drill past the lagoon hub into the grid
    app.store.tab = ANIMAL_TAB
    return app


def _render_page(app: App, page: int) -> pygame.Surface:
    app.store.page = page
    app.store.update(0.0)
    app._render()
    return app.screen.copy()


def _set_sun_state(owned: bool, variant: int | None) -> None:
    """Mutate only the in-memory store state (never saved) so the card renders
    masked (unowned) or revealed to a chosen variant."""
    st = store_data._ensure()
    st["owned"] = [i for i in st.get("owned", []) if i != "skin_sun"]
    st.setdefault("skin_variants", {}).pop("skin_sun", None)
    if owned:
        st["owned"].append("skin_sun")
        if variant is not None:
            st["skin_variants"]["skin_sun"] = variant
    animal_sun.sync_from_store()
    if store_cards is not None:
        try:
            store_cards.clear_cache()
        except Exception:
            pass


def _sun_card(app: App, scale: float) -> pygame.Surface:
    """Crop the SUN's card out of the just-rendered page (using the store's own
    item_rects) and scale it up for a legible inset."""
    r = app.store.item_rects.get("skin_sun")
    pad = 6
    rect = pygame.Rect(r.x - pad, r.y - pad, r.w + pad * 2, r.h + pad * 2)
    rect.clamp_ip(app.screen.get_rect())
    card = app.screen.subsurface(rect).copy()
    return pygame.transform.smoothscale(
        card, (int(rect.w * scale), int(rect.h * scale)))


def main() -> str:
    # Row A — the whole ANIMALS tab, unowned (SUN masked as ???).
    _set_sun_state(owned=False, variant=None)
    app = _new_app()
    pages = [_render_page(app, p) for p in range(app.store.n_pages)]

    # Row B — the SUN card itself, zoomed, in its three store states.
    _set_sun_state(owned=False, variant=None)
    app = _new_app(); _render_page(app, SUN_PAGE)
    card_mystery = _sun_card(app, 2.4)
    cards = [("IN STORE  —  mystery ???", card_mystery)]
    for idx, name in ((0, "UNLOCKS TO  →  CLASSIC"), (1, "UNLOCKS TO  →  KAWAII")):
        _set_sun_state(owned=True, variant=idx)
        app = _new_app(); _render_page(app, SUN_PAGE)
        cards.append((name, _sun_card(app, 2.4)))
    _set_sun_state(owned=False, variant=None)   # restore masked

    pw, ph = pages[0].get_size()
    n = len(pages)
    cw, ch = cards[0][1].get_size()
    MARGIN, GUTTER, TITLE_H, SUBT_H = 30, 24, 92, 38
    row_a_w = n * pw + (n - 1) * GUTTER
    row_b_w = len(cards) * cw + (len(cards) - 1) * GUTTER
    sheet_w = MARGIN * 2 + max(row_a_w, row_b_w)
    sheet_h = TITLE_H + SUBT_H + ph + 28 + SUBT_H + ch + 30 + MARGIN
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((18, 16, 28))

    title = _font(30, True).render("ANIMALS — STORE TAB  ·  new mystery SUN (7,500)",
                                   True, _GOLD_PALE)
    sheet.blit(title, title.get_rect(midtop=(sheet_w // 2, 18)))
    sub = _font(15, True).render(
        "Row A — the current ANIMALS category, all 4 pages.  28 skins; the SUN joins the secret-flyer cluster on page 3.",
        True, (190, 182, 210))
    sheet.blit(sub, (MARGIN, TITLE_H - 18))

    x0 = (sheet_w - row_a_w) // 2
    y = TITLE_H + SUBT_H - 14
    for i, pg in enumerate(pages):
        x = x0 + i * (pw + GUTTER)
        border = (255, 210, 90) if i == SUN_PAGE else _GOLD_DEEP
        pygame.draw.rect(sheet, border,
                         pygame.Rect(x - 2, y - 2, pw + 4, ph + 4), width=2)
        sheet.blit(pg, (x, y))
        tag = f"PAGE {i + 1}/{n}" + ("  ← SUN here" if i == SUN_PAGE else "")
        cap = _font(14, True).render(tag, True,
                                     (255, 210, 90) if i == SUN_PAGE else (180, 172, 200))
        sheet.blit(cap, cap.get_rect(midtop=(x + pw // 2, y + ph + 5)))

    y2 = y + ph + 28
    sub2 = _font(15, True).render(
        "Row B — the SUN card itself: masked MYSTERY ??? until bought, then it reveals to whichever design the purchase rolled.",
        True, (190, 182, 210))
    sheet.blit(sub2, (MARGIN, y2))
    y2 += SUBT_H - 8
    x0b = (sheet_w - row_b_w) // 2
    for j, (name, card) in enumerate(cards):
        x = x0b + j * (cw + GUTTER)
        sheet.blit(card, (x, y2))
        cap = _font(15, True).render(name, True, (255, 224, 130))
        sheet.blit(cap, cap.get_rect(midtop=(x + cw // 2, y2 + ch + 6)))

    out = os.path.join(OUT_DIR, "store_category.png")
    pygame.image.save(sheet, out)
    print("SAVED", out, sheet.get_size())
    return out


if __name__ == "__main__":
    main()
