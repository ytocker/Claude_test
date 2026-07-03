"""Store screenshots for the BASKETBALL skin — card view, team picker, confirm.

Three panels side by side:
  1. Store COSTUMES page 2 — shows the BASKETBALL card in context
  2. Team picker popup — the 4-swatch team chooser (THE WARRIOR pre-selected)
  3. Confirm modal — standard BUY step after picking THE WARRIOR

Run headless from repo root:
    SDL_VIDEODRIVER=dummy python tools/capture_basketball_store.py
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from game.scenes import App, STATE_STORE
from game.store import StoreScene
from game.hud import _font, _GOLD_PALE, _GOLD_DEEP

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "docs", "store_redesign", "costume", "basketball")
os.makedirs(OUT_DIR, exist_ok=True)


def _make_app() -> App:
    app = App()
    app._cooldown_t = 0.0
    app._fetch_pending = False
    app.store = StoreScene()
    app.state = STATE_STORE
    app.store.tab = 0     # COSTUMES tab
    app.store.page = 1    # page 2 — basketball is here
    return app


def _shot(app: App) -> pygame.Surface:
    app.store.update(0.0)
    app._render()
    return app.screen.copy()


# ── Panel 1: store page 2 showing the basketball card ────────────────────────
app = _make_app()
panel_store = _shot(app)

# ── Panel 2: team picker popup (THE WARRIOR pre-selected) ────────────────────
app2 = _make_app()
app2.store._variant_pick = "skin_basketball"
app2.store._variant_choice = 3  # THE WARRIOR highlighted
panel_picker = _shot(app2)

# ── Panel 3: confirm modal after picking THE WARRIOR ─────────────────────────
app3 = _make_app()
app3.store._variant_pick = None
app3.store._variant_choice = 3
app3.store._confirm = "skin_basketball"
panel_confirm = _shot(app3)

# ── Compose into one figure ───────────────────────────────────────────────────
W, H = panel_store.get_size()
TITLE_H = 72
LABEL_H = 46
GUTTER   = 20
MARGIN   = 28

labels = ["STORE — COSTUME TAB", "TEAM PICKER POPUP", "CONFIRM PURCHASE"]
panels = [panel_store, panel_picker, panel_confirm]
n = len(panels)

sheet_w = MARGIN * 2 + n * W + (n - 1) * GUTTER
sheet_h = TITLE_H + H + LABEL_H + MARGIN
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((18, 16, 28))

title_txt = _font(24, True).render(
    "BASKETBALL SKIN — STORE FLOW", True, _GOLD_PALE)
sheet.blit(title_txt, title_txt.get_rect(midtop=(sheet_w // 2, 18)))

label_f  = _font(14, True)
sublabel_f = _font(11, False)

for i, (panel, label) in enumerate(zip(panels, labels)):
    x = MARGIN + i * (W + GUTTER)
    y = TITLE_H
    pygame.draw.rect(sheet, (*_GOLD_DEEP, 255),
                     pygame.Rect(x - 2, y - 2, W + 4, H + 4), width=2)
    sheet.blit(panel, (x, y))
    lt = label_f.render(label, True, _GOLD_PALE)
    sheet.blit(lt, lt.get_rect(midtop=(x + W // 2, y + H + 8)))

out = os.path.join(OUT_DIR, "store_screens.png")
pygame.image.save(sheet, out)
print("SAVED", out, sheet.get_size())
