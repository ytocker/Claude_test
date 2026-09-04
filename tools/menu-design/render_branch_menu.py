import os, sys
os.environ.setdefault("SDL_VIDEODRIVER","dummy"); os.environ.setdefault("SDL_AUDIODRIVER","dummy")
ROOT = sys.argv[1]; OUT = sys.argv[2]; PHASE = float(sys.argv[3])
sys.path.insert(0, ROOT); os.chdir(ROOT)
import pygame; pygame.init()
from game.scenes import App, STATE_MENU
from game.world import World
from game import biome as _biome
app = App(); app._cooldown_t = 0.0; app._fetch_pending = False
app.state = STATE_MENU; app.world = World()
for _ in range(40): app.world.world_idle_tick(1/60)
app.world.biome_time = PHASE * _biome.CYCLE_SECONDS
try: app.world.weather.wetness = 0.0
except Exception: pass
app.world.bird.frame_t = 0.0
fn = getattr(app, "_render", None) or getattr(app, "render", None) or getattr(app, "draw", None)
fn()
pygame.image.save(app.screen, OUT)
print("saved", OUT, "profile_rect=", getattr(app.hud, "menu_profile_rect", None),
      "start_rect=", getattr(app.hud, "menu_start_rect", None))
