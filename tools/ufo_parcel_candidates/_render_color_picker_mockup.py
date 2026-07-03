"""Static mockup of the UFO colour-picker popup shown after purchase.

Shows the popup over a blurred gameplay background so the art-director can
evaluate it in context. Uses the exact same _draw_colour_picker() draw path
as the production StoreScene, so what you see here is pixel-identical to the
in-game popup.

Saves to docs/store_redesign/parcels/ufo/color_picker_mockup.png.
"""
import os, sys, types
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pygame
pygame.init()

from game.config import W, H, GROUND_Y
from game import biome, parrot
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground, draw_cloud
from game.entities import Pipe
from game import store_data
from game.store import StoreScene, _UFO_VARIANTS

store_data.load()

# ── Build the scene background ────────────────────────────────────────────────
scene   = pygame.Surface((W, H))
palette = biome.palette_for_phase(0.0)
scene.blit(get_sky_surface_biome(W, H, GROUND_Y, palette, 0), (0, 0))
for bx, by, sc, var in ((40, 90, 0.9, 0), (200, 130, 1.1, 2), (300, 70, 0.7, 1)):
    draw_cloud(scene, bx, by, sc, variant=var)
draw_mountains(scene, 40.0, GROUND_Y, W, palette["mtn_far"], palette["mtn_near"])
Pipe(x=12,  gap_y=250, gap_h=185).draw(scene, palette)
Pipe(x=200, gap_y=300, gap_h=170).draw(scene, palette)
draw_ground(scene, GROUND_Y, W, H, 40.0,
            palette["ground_top"], palette["ground_mid"], (60, 40, 25))
bf = parrot.get_skin_frame("skin_parrot", 2, 10.0)
scene.blit(bf, bf.get_rect(center=(96, 270)))

canvas = scene.copy()

# ── Fake StoreScene with just what _draw_colour_picker needs ─────────────────
store = types.SimpleNamespace(
    t               = 0.0,
    _selected_variant  = "sapphire",
    _cp_swatches    = [],
    _cp_yes_rect    = None,
    _cp_no_rect     = None,
    _cp_panel       = None,
    _ufo_swatch_surfs = None,
)
StoreScene._draw_colour_picker(store, canvas)

# ── Save ──────────────────────────────────────────────────────────────────────
out = os.path.join(os.path.dirname(__file__), "..", "..",
                   "docs", "store_redesign", "parcels", "ufo",
                   "color_picker_mockup.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"saved → {out}")
