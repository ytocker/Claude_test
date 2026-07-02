import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, "/home/user/skybit")
import importlib
import pygame
pygame.init()
import tools.fly_candidates.pop_v2 as m
importlib.reload(m)
build = m.build


def sky(surf, top, bot):
    r = surf.get_rect()
    for y in range(r.height):
        t = y / r.height
        c = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(surf, c, (0, y), (r.width, y))


DAY = ((150, 200, 240), (210, 230, 230))
NIGHT = ((14, 18, 40), (34, 40, 74))          # night-biome dusk-blue field

panels = []
for fi in range(4):
    fr = build(fi, 0.0)
    hp = pygame.Surface((180, 180), pygame.SRCALPHA)
    sky(hp, *DAY)
    pygame.draw.rect(hp, (17, 17, 17), hp.get_rect(), 3, border_radius=14)
    bb = fr.get_bounding_rect()
    fr2 = fr.subsurface(bb).copy() if (bb.width and bb.height) else fr
    sw, sh = fr2.get_size()
    scale = (180 * 0.80) / max(sw, sh)
    fr2 = pygame.transform.smoothscale(
        fr2, (max(1, int(sw * scale)), max(1, int(sh * scale))))
    hp.blit(fr2, fr2.get_rect(center=(90, 90)))
    panels.append(hp)


def truth_strip(bg):
    strip = pygame.Surface((4 * 60 + 10, 70), pygame.SRCALPHA)
    strip.fill(bg)
    for fi in range(4):
        fr = build(fi, 0.0)
        bb = fr.get_bounding_rect()
        fr2 = fr.subsurface(bb).copy() if (bb.width and bb.height) else fr
        sw, sh = fr2.get_size()
        scale = 40.0 / max(sw, sh)
        fr40 = pygame.transform.scale(
            fr2, (max(1, int(sw * scale)), max(1, int(sh * scale))))
        strip.blit(fr40, fr40.get_rect(center=(fi * 60 + 35, 35)))
    return strip

# Two 40px NEAREST truth strips — the real in-game read on a lit day sky AND on
# the night biome, the survivability check the R1 sheet was missing.
day_strip = truth_strip((176, 214, 235))
night_strip = truth_strip((22, 27, 52))

sheet = pygame.Surface((4 * 188 + 8, 188 + 82 * 2), pygame.SRCALPHA)
sheet.fill((18, 18, 24))
for i, p in enumerate(panels):
    sheet.blit(p, (8 + i * 188, 8))
sheet.blit(day_strip, (8, 196))
sheet.blit(night_strip, (8 + 4 * 60 + 24, 196))

out = "/home/user/skybit/docs/store_redesign/animal/fly/pop_v2/round_2.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("Saved", out)
