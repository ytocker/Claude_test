"""Render the round-1 review sheet for shades_white.

For each of the 3 variants: a product shot (eye_w~96), Pip @22px native,
and Pip @22px ~6x zoom. Run headless:
    SDL_VIDEODRIVER=dummy python docs/shades/shades_white/render_sheet.py
"""
import os
import sys

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")))

import pygame
pygame.init()

from game import parrot, store_skins  # noqa: E402
from variants import VARIANTS, PICKED  # noqa: E402


def on_pip(draw_shades, angle=-10):
    comp = pygame.Surface((store_skins.COMPOSITE_W, store_skins.COMPOSITE_H),
                          pygame.SRCALPHA)
    comp.blit(parrot._build_frame_bare(angle), (0, store_skins.PARROT_DY))
    draw_shades(comp, 50, 40, 22, 1)
    return parrot._add_outline(comp)


def product(draw_shades, c=160):
    s = pygame.Surface((c, c), pygame.SRCALPHA)
    draw_shades(s, c // 2, c // 2, 96, 1)
    return parrot._add_outline(s)


# ── sheet layout ──────────────────────────────────────────────────────────────
BG = (32, 36, 52)
PANEL = (44, 49, 70)
INK = (236, 240, 250)
SUB = (150, 158, 178)
GOLD = (255, 210, 90)

font = pygame.font.SysFont("dejavusans", 18, bold=True)
small = pygame.font.SysFont("dejavusans", 13)
tag = pygame.font.SysFont("dejavusans", 12, bold=True)

COL_W = 380
ROW_H = 240
MARGIN = 24
HEAD = 70
sheet_w = COL_W * len(VARIANTS) + MARGIN * 2
sheet_h = HEAD + ROW_H + MARGIN * 2
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title = font.render("Skybit SHADES — WHITE RETRO  (shades_white)  ·  Round 1",
                    True, INK)
sheet.blit(title, (MARGIN, 20))
sub = small.render(
    "80s/90s white-plastic frames, smoke lens.  Product (eye_w=96) + on-Pip "
    "@22px native & 6x.  Gold tag = implemented.", True, SUB)
sheet.blit(sub, (MARGIN, 46))


def checker(surf, rect, a=(58, 63, 86), b=(50, 55, 78), s=8):
    for y in range(rect.top, rect.bottom, s):
        for x in range(rect.left, rect.right, s):
            c = a if ((x // s + y // s) % 2 == 0) else b
            surf.fill(c, pygame.Rect(x, y, s, s).clip(rect))


for i, (name, fn) in enumerate(VARIANTS):
    x0 = MARGIN + i * COL_W
    panel = pygame.Rect(x0 + 8, HEAD, COL_W - 16, ROW_H)
    is_pick = (name == PICKED)
    pygame.draw.rect(sheet, PANEL, panel, border_radius=12)
    if is_pick:
        pygame.draw.rect(sheet, GOLD, panel, width=3, border_radius=12)

    label = tag.render(name, True, GOLD if is_pick else INK)
    sheet.blit(label, (panel.x + 14, panel.y + 10))
    if is_pick:
        pick = tag.render("IMPLEMENTED", True, GOLD)
        sheet.blit(pick, (panel.right - pick.get_width() - 14, panel.y + 10))

    # Product shot (left).
    prod = product(fn)
    prect = pygame.Rect(panel.x + 16, panel.y + 36, 110, 110)
    checker(sheet, prect)
    pygame.draw.rect(sheet, (70, 76, 100), prect, width=1)
    pr = prod.get_rect(center=prect.center)
    sheet.blit(prod, pr)
    sheet.blit(small.render("product 96px", True, SUB),
               (prect.x, prect.bottom + 4))

    # On-Pip native @22 (middle).
    pip = on_pip(fn)
    nrect = pygame.Rect(prect.right + 18, panel.y + 60, pip.get_width() + 8,
                        pip.get_height() + 8)
    checker(sheet, nrect)
    sheet.blit(pip, (nrect.x + 4, nrect.y + 4))
    sheet.blit(small.render("Pip 1x", True, SUB), (nrect.x, nrect.bottom + 4))

    # On-Pip 6x zoom (right), centred on the eye/head so the shades fill it.
    z = 6
    zoom = pygame.transform.scale(
        pip, (pip.get_width() * z, pip.get_height() * z))
    zrect = pygame.Rect(nrect.right + 16, panel.y + 30,
                        COL_W - (nrect.right - panel.x) - 40, ROW_H - 60)
    checker(sheet, zrect)
    pygame.draw.rect(sheet, (70, 76, 100), zrect, width=1)
    sheet.set_clip(zrect)
    # Eye sits at composite (50,40); add the build's PARROT_DY-independent
    # outline pad (~2px) before scaling, and centre that point in the panel.
    eye_x = (50 + 2) * z
    eye_y = (40 + 2) * z
    sheet.blit(zoom, (zrect.centerx - eye_x, zrect.centery - eye_y))
    sheet.set_clip(None)
    sheet.blit(small.render("Pip 6x (eye)", True, SUB),
               (zrect.x, zrect.bottom + 4))


out = os.path.join(os.path.dirname(__file__), "round_1.png")
pygame.image.save(sheet, out)
print("wrote", out, sheet.get_size())
