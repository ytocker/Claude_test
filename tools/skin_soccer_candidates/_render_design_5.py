import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import sys
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from tools.skin_soccer_candidates.design_5 import build
from tools.ninja_render import gameplay_panel, hero_panel

out_dir = "/home/user/skybit/docs/store_redesign/costume/skin_soccer/design_5"
os.makedirs(out_dir, exist_ok=True)

# Keep the gameplay-crop aspect within GW: crop_h is ~0.78*GH, so w/h must
# stay under GW/crop_h or the harness's subsurface runs off the scene.
W, H = 130, 180
gp = gameplay_panel(build, W, H)
hp = hero_panel(build, 180)
sheet = pygame.Surface((W + 200, max(H, 180)), pygame.SRCALPHA)
sheet.blit(gp, (0, 0))
sheet.blit(hp, (W + 10, (max(H, 180) - 180) // 2))
pygame.image.save(sheet, f"{out_dir}/round_1.png")
print("Saved round_1.png")
