"""Render the real shipped menu, exactly as scenes.py draws STATE_MENU."""
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
from game.scenes import App, STATE_MENU, W, H
from game.world import World
from game import intro as _intro, foreground

PHASE = float(os.environ.get("PHASE", "0.0"))
OUT = os.environ["OUT"]

app = App()
app._cooldown_t = 0.0
app._fetch_pending = False
app.state = STATE_MENU
app.world = World()
for _ in range(40):
    app.world.world_idle_tick(1 / 60)
app.world.biome_time = PHASE * __import__("game.biome", fromlist=["x"]).CYCLE_SECONDS
app.world.weather.wetness = 0.0
app.world.bird.frame_t = 0.0

s = app.screen
app._draw_background(s)
foreground.draw_near_lane(s, app.world.bg_scroll, app.world.biome_palette,
                          app.world.biome_phase, app.world.biome_time)
house = _intro.get_sprite("skyhouse_post")
s.blit(house, (int(W * 0.30) - house.get_width() // 2,
               int(H * 0.42) - house.get_height() // 2))
app.world.bird.draw(s, 0, 0)
app.hud.draw_menu(s, 1 / 60, app.best)
pygame.image.save(s, OUT)
print("saved", OUT)
