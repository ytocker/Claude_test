"""Round-2 RAIDER (design_3) review sheet — same harness as round_1, retargeted
to round_2.png. Per palette (IRONCLAD then BLOODAXE): hero zoom + in-gameplay
panel + 40px NEAREST truth read. Scratch exploration; touches no production art.

Headless: SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python <this>.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from tools.viking_face_candidates import render_design_3 as r1
from tools.viking_face_candidates.design_3 import build_ironclad, build_bloodaxe

r1.OUT = "docs/store_redesign/costume/viking/face/design_3/round_2.png"
r1.TITLE = ("DESIGN 3 — RAIDER  R2  (blade reads as an axe + separated from horns; "
            "darker haft core vs beaded braid; legible grip + knot)")


if __name__ == "__main__":
    r1.main()
