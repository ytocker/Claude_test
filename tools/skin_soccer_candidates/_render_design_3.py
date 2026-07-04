import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
import sys
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from tools.skin_soccer_candidates.design_3 import build
from tools.ninja_render import gameplay_panel, hero_panel

out_dir = "/home/user/skybit/docs/store_redesign/costume/skin_soccer/design_3"
os.makedirs(out_dir, exist_ok=True)

# Panel ratio must keep the crop (height ~0.78*GH) narrower than GW=360,
# so width/height stays well below 360/499 — a portrait panel does this.
W, H = 180, 260
gp = gameplay_panel(build, W, H)
hp = hero_panel(build, 220)
sheet_h = max(H, 220)
sheet = pygame.Surface((W + 230, sheet_h), pygame.SRCALPHA)
sheet.blit(gp, (0, (sheet_h - H) // 2))
sheet.blit(hp, (W + 10, (sheet_h - 220) // 2))
pygame.image.save(sheet, f"{out_dir}/round_2.png")
print("Saved round_2.png")
