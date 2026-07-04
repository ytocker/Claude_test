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

# Thumbnail strip: the candidate down-sampled to 40px (and 24px) — the read at
# these sizes is what the critique is judged on, so render it beside the heroes.
frame = build(2, 10.0)
th40 = pygame.transform.smoothscale(frame, (40, 40 * frame.get_height() // frame.get_width()))
th24 = pygame.transform.smoothscale(frame, (24, 24 * frame.get_height() // frame.get_width()))

sheet = pygame.Surface((W + 280, max(H, 180)), pygame.SRCALPHA)
sheet.fill((18, 20, 30, 255))
sheet.blit(gp, (0, 0))
sheet.blit(hp, (W + 10, (max(H, 180) - 180) // 2))
sheet.blit(th40, th40.get_rect(center=(W + 220, 60)))
sheet.blit(th24, th24.get_rect(center=(W + 220, 130)))
pygame.image.save(sheet, f"{out_dir}/round_2.png")
print("Saved round_2.png")
