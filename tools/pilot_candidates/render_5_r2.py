import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
pygame.init()

import tools.ninja_render as nr
import tools.pilot_candidates.design_5 as d

src = d.build
gp = nr.gameplay_panel(src, 220, 392)
hp = nr.hero_panel(src, 320)
frame = nr._frame(src, nr.FRAME_IDX, nr.TILT)
# NEAREST double-scale so the 40px truth-read shows the real downsampled pixels.
truth = pygame.transform.scale(pygame.transform.scale(frame, (40, 40)), (200, 200))

from game.hud import _font, _GOLD_PALE
W = 220 + 320 + 200 + 40
H = 470
sheet = pygame.Surface((W, H))
sheet.fill((18, 16, 28))
sheet.blit(gp, (0, 28))
sheet.blit(hp, (230, 28))
sheet.blit(truth, (560, 28))
lbl = _font(18, True).render("D5 BUSH RUNNER — R2", True, _GOLD_PALE)
sheet.blit(lbl, (10, 4))
tag = _font(13, False).render("40px TRUTH-READ (nearest)", True, (170, 176, 190))
sheet.blit(tag, (560, 232))
bar = _font(15, True).render(
    "reads as bush/barnstormer pilot with rolled map at 40px.",
    True, _GOLD_PALE)
sheet.blit(bar, (10, 438))
os.makedirs("docs/store_redesign/costume/pilot/design_5", exist_ok=True)
pygame.image.save(sheet, "docs/store_redesign/costume/pilot/design_5/round_2.png")
print("SAVED")
