import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
pygame.init()
import importlib
import sys
sys.path.insert(0, "/home/user/skybit")
import tools.ninja_render as nr
build = importlib.import_module("tools.basketball_candidates.design_1").build
os.makedirs("docs/store_redesign/costume/basketball/design_1", exist_ok=True)
panel = nr.gameplay_panel(build, 220, 392)
pygame.image.save(panel, "docs/store_redesign/costume/basketball/design_1/round_1.png")
print("SAVED")
