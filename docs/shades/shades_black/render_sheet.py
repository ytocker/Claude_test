"""Render the round-1 exploration sheet for BLACK SHADES (wayfarer)."""
import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, "/home/user/skybit")
sys.path.insert(0, "/home/user/skybit/docs/shades/shades_black")

import pygame
pygame.init()
from game import parrot, store_skins
import variants

CHOSEN = "A"  # implemented variant
VARS = [("A", variants.draw_shades_A, "Classic Wayfarer"),
        ("B", variants.draw_shades_B, "Chunky Block"),
        ("C", variants.draw_shades_C, "Sleek Cant")]


def on_pip(fn, angle=-10):
    comp = pygame.Surface((store_skins.COMPOSITE_W, store_skins.COMPOSITE_H), pygame.SRCALPHA)
    comp.blit(parrot._build_frame_bare(angle), (0, store_skins.PARROT_DY))
    fn(comp, 50, 40, 22, 1)
    return parrot._add_outline(comp)


def product(fn, c=160):
    s = pygame.Surface((c, c), pygame.SRCALPHA)
    fn(s, c // 2, c // 2, 96, 1)
    return parrot._add_outline(s)


def zoom(surf, k):
    return pygame.transform.scale(surf, (surf.get_width() * k, surf.get_height() * k))


pygame.font.init()
font = pygame.font.SysFont("DejaVuSans", 18, bold=True)
small = pygame.font.SysFont("DejaVuSans", 13)

COL_W = 360
TOP = 78
ROW_H = 720
BG = (118, 124, 140)
CHECK_A, CHECK_B = (128, 134, 150), (108, 114, 130)
sheet = pygame.Surface((COL_W * 3, TOP + ROW_H))
sheet.fill(BG)

title = font.render("Skybit SHADES — shades_black (wayfarer)  ROUND 1", True, (255, 255, 255))
sheet.blit(title, (16, 14))


def checker(w, h):
    p = pygame.Surface((w, h)); cs = 12
    for yy in range(0, h, cs):
        for xx in range(0, w, cs):
            p.fill(CHECK_A if (xx // cs + yy // cs) % 2 else CHECK_B, (xx, yy, cs, cs))
    return p


for i, (vid, fn, name) in enumerate(VARS):
    ox = i * COL_W
    chosen = vid == CHOSEN
    label = f"{vid} · {name}" + ("  [IMPLEMENTED]" if chosen else "")
    col = (255, 232, 120) if chosen else (255, 255, 255)
    sheet.blit(font.render(label, True, col), (ox + 16, 50))

    panel = checker(COL_W - 24, ROW_H)
    sheet.blit(panel, (ox + 12, TOP))

    y = TOP + 12
    # product shot
    prod = product(fn)
    sheet.blit(prod, (ox + (COL_W - prod.get_width()) // 2, y))
    y += prod.get_height() + 4
    sheet.blit(small.render("product  eye_w=96", True, (245, 245, 245)), (ox + 24, y))
    y += 26

    # on-pip native @22
    pip = on_pip(fn)
    sheet.blit(pip, (ox + 24, y))
    sheet.blit(small.render("on-Pip @22 native", True, (245, 245, 245)),
               (ox + 24 + pip.get_width() + 14, y + 20))
    y += pip.get_height() + 10

    # on-pip 6x zoom
    z = zoom(pip, 6)
    sheet.blit(z, (ox + (COL_W - z.get_width()) // 2, y))
    y += z.get_height() + 2
    sheet.blit(small.render("on-Pip @22  ×6 zoom", True, (245, 245, 245)), (ox + 24, y))

OUT = "/home/user/skybit/docs/shades/shades_black/round_1.png"
pygame.image.save(sheet, OUT)
print("wrote", OUT, sheet.get_size())
