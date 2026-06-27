"""Soccer v4 D2 Goalkeeper — render sheet."""
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
import pygame
pygame.init()
import tools.ninja_render as nr
from tools.soccer_candidates.design_2 import build

gp = nr.gameplay_panel(build, 260, 420)
hero = nr.hero_panel(build, 200)
pip = build(2, 10.0)
day_bg = pygame.Surface((80, 100)); day_bg.fill((150, 196, 232))
night_bg = pygame.Surface((80, 100)); night_bg.fill((16, 18, 30))
t = pygame.transform.scale(pip, (40, 64)); day_bg.blit(t, (20, 18)); night_bg.blit(t, (20, 18))
PAD = 8; sheet = pygame.Surface((660, 440)); sheet.fill((18, 16, 28))
sheet.blit(gp, (PAD, PAD)); sheet.blit(hero, (PAD + 260 + PAD, PAD + 110))
sheet.blit(day_bg, (PAD + 260 + PAD + 200 + PAD, PAD + 100)); sheet.blit(night_bg, (PAD + 260 + PAD + 200 + PAD, PAD + 208))
os.makedirs("docs/store_redesign/costume/soccer/design_2", exist_ok=True)
out = "docs/store_redesign/costume/soccer/design_2/round_1.png"; pygame.image.save(sheet, out); print("SAVED", out)
