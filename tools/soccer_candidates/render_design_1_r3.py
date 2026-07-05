import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

import importlib
import tools.ninja_render as nr

m = importlib.import_module("tools.soccer_candidates.design_1")

panel = nr.gameplay_panel(m.build, 220, 380)
# 40px truth-read strip: shrink the panel hard, then scale back up so we judge
# whether the kit survives the downscale it actually ships at.
small = pygame.transform.scale(panel, (40, 70))

sheet = pygame.Surface((220 + 60, 380))
sheet.fill((18, 16, 28))
sheet.blit(panel, (0, 0))
sheet.blit(pygame.transform.scale(small, (56, 98)), (224, 141))

os.makedirs("docs/store_redesign/costume/soccer/design_1", exist_ok=True)
pygame.image.save(sheet, "docs/store_redesign/costume/soccer/design_1/round_3.png")
print("saved docs/store_redesign/costume/soccer/design_1/round_3.png")
