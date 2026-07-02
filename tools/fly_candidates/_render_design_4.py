import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
from tools.fly_candidates.design_4 import build

panels = []
for fi in range(4):
    fr = build(fi, 0.0)
    hp = pygame.Surface((180, 180), pygame.SRCALPHA)
    pygame.draw.rect(hp, (8, 8, 12), hp.get_rect(), border_radius=14)
    bb = fr.get_bounding_rect()
    fr2 = fr.subsurface(bb).copy() if (bb.width and bb.height) else fr
    sw, sh = fr2.get_size()
    scale = (180 * 0.82) / max(sw, sh)
    fr2 = pygame.transform.smoothscale(fr2, (max(1, int(sw*scale)), max(1, int(sh*scale))))
    hp.blit(fr2, fr2.get_rect(center=(90, 90)))
    panels.append(hp)

# 40px NEAREST truth strip — the real "lives or dies at 40px" read.
truth_surf = pygame.Surface((4*50+10, 60), pygame.SRCALPHA)
truth_surf.fill((8, 8, 12))
for fi in range(4):
    fr = build(fi, 0.0)
    h = int(40 * fr.get_height() / fr.get_width())
    fr40 = pygame.transform.scale(fr, (40, h))   # nearest-neighbour
    truth_surf.blit(fr40, (fi*50+5, (60-h)//2))

sheet = pygame.Surface((4*188+8, 188+68), pygame.SRCALPHA)
sheet.fill((8, 8, 12))
for i, p in enumerate(panels):
    sheet.blit(p, (8+i*188, 8))
sheet.blit(truth_surf, (8, 196))

os.makedirs("/home/user/skybit/docs/store_redesign/animal/fly/design_4", exist_ok=True)
pygame.image.save(sheet, "/home/user/skybit/docs/store_redesign/animal/fly/design_4/round_2.png")
print("Saved round_2.png")
