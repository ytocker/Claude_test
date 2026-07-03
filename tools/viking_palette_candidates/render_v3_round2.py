"""Compose the STORMGREY (v3) palette review sheet — round 2 (ITERATE pass).

Same four-panel layout render_v3 used (hero | day gameplay | night gameplay |
40px truth read day|night 3x) so the round-1 vs round-2 read is apples-to-apples.
This round warms the body off its cold lean, deepens the shield's iron frame, and
lifts the chest one steel value step — see v3.py round-2 notes.

Headless: SDL_VIDEODRIVER=dummy PYTHONPATH=/home/user/skybit python <this>.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from tools.viking_palette_candidates import render_v3

render_v3.OUT = "docs/store_redesign/costume/viking/palette/v3/round_2.png"
render_v3.TITLE = "VIKING PALETTE v3 — STORMGREY  (round 2 — warmed slate, framed shield)"


if __name__ == "__main__":
    render_v3.main()
