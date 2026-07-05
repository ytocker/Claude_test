import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
pygame.init()

import tools.ninja_render as nr
import tools.pilot_candidates.design_1 as d

src = d.build
gp = nr.gameplay_panel(src, 220, 392)
hp = nr.hero_panel(src, 320)
frame = nr._frame(src, nr.FRAME_IDX, nr.TILT)
# NEAREST double-scale (40px truth read): does the natural macaw still read as a
# red-headed bird wearing a captain's cap + gold-ringed cuff at gameplay size?
truth = pygame.transform.scale(pygame.transform.scale(frame, (40, 40)), (200, 200))

from game.hud import _font, _GOLD_PALE
W = 220 + 320 + 200 + 40
H = 460
sheet = pygame.Surface((W, H))
sheet.fill((18, 16, 28))
sheet.blit(gp, (0, 28))
sheet.blit(hp, (230, 28))
sheet.blit(truth, (560, 28))
lbl = _font(18, True).render("D1 CAPTAIN — R3 (no recolor)", True, _GOLD_PALE)
sheet.blit(lbl, (10, 4))
tlbl = _font(13, True).render("40px truth-read: red macaw in a captain costume?", True, _GOLD_PALE)
sheet.blit(tlbl, (560, 232))
os.makedirs("docs/store_redesign/costume/pilot/design_1", exist_ok=True)
pygame.image.save(sheet, "docs/store_redesign/costume/pilot/design_1/round_3.png")
print("SAVED")
