import os; os.environ.setdefault("SDL_VIDEODRIVER","dummy"); os.environ.setdefault("SDL_AUDIODRIVER","dummy")
import pygame; pygame.init()
import tools.ninja_render as nr
import tools.pilot_candidates.design_3 as d

src = d.build
gp = nr.gameplay_panel(src, 220, 392)
hp = nr.hero_panel(src, 320)
frame = nr._frame(src, nr.FRAME_IDX, nr.TILT)
# NEAREST both directions so the 40px truth-read shows the real downscaled pixels.
small = pygame.transform.scale(frame, (40, 40))
truth = pygame.transform.scale(small, (200, 200))

from game.hud import _font, _GOLD_PALE
W = 220+320+200+40; H = 452
sheet = pygame.Surface((W, H)); sheet.fill((18,16,28))
sheet.blit(gp, (0, 28)); sheet.blit(hp, (230, 28)); sheet.blit(truth, (560, 28))
lbl = _font(18, True).render("D3 RED BARON — R2", True, _GOLD_PALE)
sheet.blit(lbl, (10, 4))
tlab = _font(13, False).render("40px truth-read", True, (150, 150, 168))
sheet.blit(tlab, (560, 230))
bar = _font(14, False).render(
    "reads as Red Baron aristocrat ace with monocle + cross at 40px.",
    True, (210, 210, 224))
sheet.blit(bar, (10, H - 24))
os.makedirs("docs/store_redesign/costume/pilot/design_3", exist_ok=True)
pygame.image.save(sheet, "docs/store_redesign/costume/pilot/design_3/round_2.png")
print("SAVED")
