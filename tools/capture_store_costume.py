"""Headless capture of the real COSTUME store tab (every page) plus a live
gameplay frame. Drives the actual ``App._render`` per scene state so each shot
is pixel-faithful to what ships. Output lands in
``docs/store_redesign/costume/`` (under tools/+docs, excluded from the bundle).
Run from repo root: ``SDL_VIDEODRIVER=dummy python tools/capture_store_costume.py``.
"""
import os
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

import sys
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

import pygame
pygame.init()

from game.config import H
from game.scenes import App, STATE_STORE, STATE_PLAY
from game.world import World
from game.store import StoreScene

OUT_DIR = os.path.join(_ROOT, "docs", "store_redesign", "costume")
os.makedirs(OUT_DIR, exist_ok=True)


def save(app, name):
    pygame.image.save(app.screen, os.path.join(OUT_DIR, name + ".png"))
    print(f"  saved {name}.png")


def sim_play(seconds=3.0, dt=1 / 60):
    """A short, gentle live run so pillars/coins/ground populate the frame."""
    w = World()
    w.ready_t = 0.0
    w.flap()
    for _ in range(int(seconds / dt)):
        if w.bird.y > H * 0.42:
            w.flap()
        w.update(dt)
        if w.game_over:
            break
    return w


app = App()
app._cooldown_t = 0.0          # set by input handlers in-game; needed by _render
app._fetch_pending = False

# ── Store: COSTUMES tab (index 0), one shot per page ─────────────────────────
app.store = StoreScene()
app.state = STATE_STORE
app.store.tab = 0              # COSTUMES
n_pages = app.store.n_pages
for p in range(n_pages):
    app.store.page = p
    app.store.update(0.0)
    app._render()
    save(app, f"store_costume_page{p + 1}")

# ── Gameplay: a plain live frame ─────────────────────────────────────────────
app.world = sim_play()
app.state = STATE_PLAY
app._render()
save(app, "gameplay")

print("done")
