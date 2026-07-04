import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
pygame.init()

import tools.ninja_render as nr
import tools.pilot_candidates.design_4 as d

# Force a fresh flat-frame build so edits to the builder always re-render.
src = d.build

gp = nr.gameplay_panel(src, 220, 392)
hp = nr.hero_panel(src, 320)

# 40px NEAREST truth-read — the bar is "reads as modern jet fighter pilot with
# visor + oxygen mask at 40px". NEAREST (not smoothscale) so we judge the honest
# downscale a phone shows, not a blurred flatter.
frame = nr._frame(src, nr.FRAME_IDX, nr.TILT)
truth40 = pygame.transform.scale(frame, (40, 40))
truth = pygame.transform.scale(truth40, (200, 200))

from game.hud import _font, _GOLD_PALE
W = 220 + 320 + 200 + 40
H = 440
sheet = pygame.Surface((W, H))
sheet.fill((18, 16, 28))
sheet.blit(gp, (0, 28))
sheet.blit(hp, (230, 28))
sheet.blit(truth, (560, 28))
lbl = _font(18, True).render("D4 VIPER — R2", True, _GOLD_PALE)
sheet.blit(lbl, (10, 4))
bar = _font(13, False).render(
    "reads as modern jet fighter pilot with visor + oxygen mask at 40px",
    True, (210, 214, 224))
sheet.blit(bar, (10, H - 22))
tl = _font(12, False).render("40px NEAREST truth-read", True, (150, 154, 164))
sheet.blit(tl, (560, 232))

os.makedirs("docs/store_redesign/costume/pilot/design_4", exist_ok=True)
pygame.image.save(sheet, "docs/store_redesign/costume/pilot/design_4/round_2.png")
print("SAVED")
