"""Animal store tab — revealed mystery items (presentation only).

Same as render_animal_store.py but patches store_data.is_owned to return
True for every item so secret cards show their real art instead of ???.
No production code is touched; game store behaviour is unchanged.

Usage (from repo root):
    SDL_VIDEODRIVER=dummy python tools/render_animal_store_revealed.py
Output:
    docs/store_redesign/animal/animal_store_pages_revealed.png
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
pygame.init()

from game import store_data, store_cards
from game.scenes import App, STATE_STORE
from game.store import StoreScene
from game.hud import _font, _GOLD_PALE, _GOLD_DEEP

# Reveal all items for this presentation render.
_real_is_owned = store_data.is_owned
store_data.is_owned = lambda sid: True
store_cards.clear_cache()

_ANIMALS_TAB = 2   # COSTUMES=0, PARROTS=1, ANIMALS=2, …

app = App()
app._cooldown_t = 0.0
app._fetch_pending = False
app.store = StoreScene()
app.state = STATE_STORE
app.store.tab = _ANIMALS_TAB
app.store.view = "category"

pages = []
for p in range(app.store.n_pages):
    app.store.page = p
    app.store.update(0.0)
    app._render()
    pages.append(app.screen.copy())

# Restore
store_data.is_owned = _real_is_owned
store_cards.clear_cache()

# Assemble 2×2 grid
pw, ph = pages[0].get_size()
COLS = 2
ROWS = -(-len(pages) // COLS)
MARGIN, GUTTER, TITLE_H = 24, 20, 60
CAPTION_H = 24

sheet_w = MARGIN * 2 + COLS * pw + (COLS - 1) * GUTTER
sheet_h = TITLE_H + ROWS * (MARGIN + ph + CAPTION_H)

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((18, 16, 28))

title_surf = _font(26, True).render(
    f"ANIMALS — ALL REVEALED  ({len(pages)} pages)", True, _GOLD_PALE)
sheet.blit(title_surf, title_surf.get_rect(midtop=(sheet_w // 2, 14)))

for i, pg in enumerate(pages):
    col = i % COLS
    row = i // COLS
    x = MARGIN + col * (pw + GUTTER)
    y = TITLE_H + row * (MARGIN + ph + CAPTION_H)
    pygame.draw.rect(sheet, (*_GOLD_DEEP, 255),
                     pygame.Rect(x - 2, y - 2, pw + 4, ph + 4), width=2)
    sheet.blit(pg, (x, y))
    cap = _font(13, True).render(
        f"PAGE {i + 1} / {len(pages)}", True, (180, 172, 200))
    sheet.blit(cap, cap.get_rect(midtop=(x + pw // 2, y + ph + 5)))

out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "docs", "store_redesign", "animal")
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "animal_store_pages_revealed.png")
pygame.image.save(sheet, out_path)
print(f"Saved {out_path}  ({sheet.get_width()}×{sheet.get_height()}px)")
