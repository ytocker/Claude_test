"""Round 2 review sheet for WARCHIEF (design_1) — same layout as round 1
(per palette: hero zoom + in-gameplay panel + 40px NEAREST truth read), re-run
after the contrast/value pass so the IRONCLAD face is judged against BLOODAXE.
Scratch exploration; nothing here touches production art.

Headless: SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python <this>.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from tools.viking_face_candidates import render_design_1 as r1

r1.OUT = "docs/store_redesign/costume/viking/face/design_1/round_2.png"
r1.TITLE = ("DESIGN 1 — WARCHIEF  (round 2: keyline-separated mustache + braids, "
            "value-lifted glare, brighter V-notch seam, gripped haft)")


if __name__ == "__main__":
    r1.main()
