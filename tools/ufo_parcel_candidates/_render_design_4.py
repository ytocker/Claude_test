import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pygame; pygame.init()
import importlib.util
spec = importlib.util.spec_from_file_location("design_4",
    os.path.join(os.path.dirname(__file__), "design_4.py"))
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
from _render_shared import render_sheet
render_sheet(mod.build,
    "UFO PARCEL — DESIGN 4: NEON NIGHT-DINER  (round 1)",
    "/home/user/skybit/docs/store_redesign/parcels/ufo/design_4/round_1.png")
