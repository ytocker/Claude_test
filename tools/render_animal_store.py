"""Animal store tab — pixel-faithful page captures.

Drives the live App renderer with the ANIMALS tab active, captures every
page, and assembles them in a 2×2 grid so all 28 items (4 pages × 8 cards)
are visible in a single PNG.  Secret items show as ??? as the player would
see them before purchase.

Usage (from repo root):
    SDL_VIDEODRIVER=dummy python tools/render_animal_store.py
Output:
    docs/store_redesign/animal/animal_store_pages.png
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
pygame.init()

from game.scenes import App, STATE_STORE
from game.store import StoreScene
from game.hud import _font, _GOLD_PALE, _GOLD_DEEP

_ANIMALS_TAB = 2   # COSTUMES=0, PARROTS=1, ANIMALS=2, SHOES=3, …

app = App()
app._cooldown_t = 0.0
app._fetch_pending = False
app.store = StoreScene()
app.state = STATE_STORE
app.store.tab = _ANIMALS_TAB
app.store.view = "category"   # bypass the lagoon hub landing screen

pages = []
for p in range(app.store.n_pages):
    app.store.page = p
    app.store.update(0.0)
    app._render()
    pages.append(app.screen.copy())

# Assemble in a 2-column grid (2 pages per row → 2 rows for 4 pages)
pw, ph = pages[0].get_size()
COLS = 2
ROWS = -(-len(pages) // COLS)   # ceiling division
MARGIN, GUTTER, TITLE_H = 24, 20, 60
CAPTION_H = 24

sheet_w = MARGIN * 2 + COLS * pw + (COLS - 1) * GUTTER
sheet_h = TITLE_H + ROWS * (MARGIN + ph + CAPTION_H)

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill((18, 16, 28))

title_surf = _font(26, True).render(
    f"ANIMALS — STORE TAB  ({len(pages)} pages)", True, _GOLD_PALE)
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
out_path = os.path.join(out_dir, "animal_store_pages.png")
pygame.image.save(sheet, out_path)
print(f"Saved {out_path}  ({sheet.get_width()}×{sheet.get_height()}px, {len(pages)} pages)")
