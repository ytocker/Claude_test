"""Smoke test for the shared cloak_base (scratch). Composes the cloak with the
shared paint_skeleton over a day + night strip and a 40px truth read."""
import os
import pygame

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
pygame.init()
pygame.display.set_mode((1, 1))

from tools.skeleton_candidates import _v4_xray_base as XB
from game import store_skins

ANGLES = [-22, -8, 6, 18]
SKY_DAY = (150, 200, 235)
SKY_NIGHT = (18, 22, 44)


def compose(angle):
    comp = pygame.Surface((store_skins.COMPOSITE_W, store_skins.COMPOSITE_H),
                          pygame.SRCALPHA)
    comp.blit(XB.cloak_base(angle, XB.P_FLESH), (0, store_skins.PARROT_DY))
    XB.paint_skeleton(comp, angle, style=XB.DEFAULT_STYLE)
    from game.parrot import _add_outline
    return _add_outline(comp)


def strip(bg, scale):
    cells = []
    for a in ANGLES:
        frame = compose(a)
        cell = pygame.Surface(frame.get_size())
        cell.fill(bg)
        cell.blit(frame, (0, 0))
        cell = pygame.transform.scale(
            cell, (cell.get_width() * scale, cell.get_height() * scale))
        cells.append(cell)
    w = sum(c.get_width() for c in cells) + 8 * (len(cells) - 1)
    h = max(c.get_height() for c in cells)
    out = pygame.Surface((w, h))
    out.fill((30, 30, 30))
    x = 0
    for c in cells:
        out.blit(c, (x, 0))
        x += c.get_width() + 8
    return out


def truth_40(bg):
    """Each frame downscaled so the parrot reads ~40px tall, NEAREST."""
    cells = []
    for a in ANGLES:
        frame = compose(a)
        small = pygame.transform.smoothscale(frame, (43, 67))
        cell = pygame.Surface(small.get_size())
        cell.fill(bg)
        cell.blit(small, (0, 0))
        cell = pygame.transform.scale(cell, (small.get_width() * 4,
                                             small.get_height() * 4))
        cells.append(cell)
    w = sum(c.get_width() for c in cells) + 8 * (len(cells) - 1)
    h = max(c.get_height() for c in cells)
    out = pygame.Surface((w, h))
    out.fill((30, 30, 30))
    x = 0
    for c in cells:
        out.blit(c, (x, 0))
        x += c.get_width() + 8
    return out


day = strip(SKY_DAY, 4)
night = strip(SKY_NIGHT, 4)
t40 = truth_40(SKY_DAY)
W = max(day.get_width(), night.get_width(), t40.get_width())
H = day.get_height() + night.get_height() + t40.get_height() + 24
out = pygame.Surface((W, H))
out.fill((30, 30, 30))
out.blit(day, (0, 0))
out.blit(night, (0, day.get_height() + 12))
out.blit(t40, (0, day.get_height() + night.get_height() + 24))
path = "/tmp/claude-0/-home-user-skybit/2849fef3-03a4-549b-80ce-612a8b6de8eb/scratchpad/cloak_smoke.png"
pygame.image.save(out, path)
print("wrote", path)
