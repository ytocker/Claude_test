import os; os.environ.setdefault("SDL_VIDEODRIVER","dummy"); os.environ.setdefault("SDL_AUDIODRIVER","dummy")
import pygame; pygame.init()
import tools.ninja_render as nr
import tools.pilot_candidates.design_2 as d
from game import biome
from game.draw import get_sky_surface_biome
from game.config import W as GW, H as GH, GROUND_Y

src = d.build


def truth_read(phase, box=200, px=40):
    """40px NEAREST truth-read of the bird over a real biome sky patch, so the
    silhouette + costume read can be judged at gameplay size on day/night."""
    palette = biome.palette_for_phase(phase)
    sky = get_sky_surface_biome(GW, GH, GROUND_Y, palette, 0)
    frame = nr._frame(src, nr.FRAME_IDX, nr.TILT)
    patch = pygame.Surface((60, 60))
    patch.blit(sky, (0, 0), (150, 240, 60, 60))          # a mid-sky crop
    patch.blit(frame, frame.get_rect(center=(30, 30)))
    small = pygame.transform.scale(patch, (px, px))       # NEAREST downscale
    return pygame.transform.scale(small, (box, box))      # NEAREST upscale


gp = nr.gameplay_panel(src, 220, 392)
hp = nr.hero_panel(src, 320)
day = truth_read(0.0)
night = truth_read(0.64375)

from game.hud import _font, _GOLD_PALE
W = 220 + 320 + 200 + 30
H = 470
sheet = pygame.Surface((W, H)); sheet.fill((18, 16, 28))
sheet.blit(gp, (0, 40))
sheet.blit(hp, (230, 40))
sheet.blit(day, (560, 40))
sheet.blit(night, (560, 250))

lbl = _font(18, True).render("D2 ACE — R3 (natural parrot + kit)", True, _GOLD_PALE)
sheet.blit(lbl, (10, 8))
bar = _font(13, False).render(
    "red head / blue wing / yellow beak kept — leather helmet, brow goggles, cream scarf on top",
    True, (210, 200, 220))
sheet.blit(bar, (10, 448))
sheet.blit(_font(12, True).render("40px DAY", True, _GOLD_PALE), (560, 24))
sheet.blit(_font(12, True).render("40px NIGHT", True, _GOLD_PALE), (560, 234))

os.makedirs("docs/store_redesign/costume/pilot/design_2", exist_ok=True)
pygame.image.save(sheet, "docs/store_redesign/costume/pilot/design_2/round_3.png")
print("SAVED")
