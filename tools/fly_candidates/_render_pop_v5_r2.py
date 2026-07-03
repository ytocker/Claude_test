import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, "/home/user/skybit")
import pygame
pygame.init()
from tools.fly_candidates.pop_v5 import build

# 4-frame hero panels over a dusk-sky swatch to check read against a busy sky.
def sky(surf):
    r = surf.get_rect()
    for y in range(r.height):
        t = y / r.height
        c = (int(150 + 70 * t), int(190 + 20 * t), int(240 - 40 * t))
        pygame.draw.line(surf, c, (0, y), (r.width, y))

panels = []
for fi in range(4):
    fr = build(fi, 0.0)
    hp = pygame.Surface((180, 180), pygame.SRCALPHA)
    sky(hp)
    pygame.draw.rect(hp, (17, 17, 17), hp.get_rect(), 3, border_radius=14)
    bb = fr.get_bounding_rect()
    fr2 = fr.subsurface(bb).copy() if (bb.width and bb.height) else fr
    sw, sh = fr2.get_size()
    scale = (180 * 0.80) / max(sw, sh)
    fr2 = pygame.transform.smoothscale(
        fr2, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    hp.blit(fr2, fr2.get_rect(center=(90, 90)))
    panels.append(hp)

# 40px NEAREST truth strip — the real in-game read.
truth = pygame.Surface((4 * 60 + 10, 70), pygame.SRCALPHA)
truth.fill((28, 30, 38))
for fi in range(4):
    fr = build(fi, 0.0)
    bb = fr.get_bounding_rect()
    fr2 = fr.subsurface(bb).copy() if (bb.width and bb.height) else fr
    sw, sh = fr2.get_size()
    scale = 40.0 / max(sw, sh)
    fr40 = pygame.transform.scale(
        fr2, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    truth.blit(fr40, fr40.get_rect(center=(fi * 60 + 35, 35)))

sheet = pygame.Surface((4 * 188 + 8, 188 + 82), pygame.SRCALPHA)
sheet.fill((18, 18, 24))
for i, p in enumerate(panels):
    sheet.blit(p, (8 + i * 188, 8))
sheet.blit(truth, (8, 196))

out = "/home/user/skybit/docs/store_redesign/animal/fly/pop_v5/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("Saved", out)
