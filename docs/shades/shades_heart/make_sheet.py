"""Render the round-1 review sheet for HEART SHADES.

Each variant shown as: product shot (eye_w=96) + on-Pip @22px native + ~6x zoom.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import sys
import pygame
pygame.init()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from game import parrot, store_skins
from explore import VARIANTS

BG = (24, 28, 46)        # navy store-card backdrop (the real card colour family)
CARD = (32, 38, 60)
INK = (236, 240, 248)
ACC = (255, 120, 175)
PICKED = (120, 230, 150)

font = pygame.font.SysFont("dejavusans", 18, bold=True)
font_s = pygame.font.SysFont("dejavusans", 13)
font_t = pygame.font.SysFont("dejavusans", 22, bold=True)

# Which variant we implemented as the canonical draw_shades.
IMPLEMENTED = 0  # A · HOT PINK


def on_pip(draw_shades, angle=-10):
    comp = pygame.Surface((store_skins.COMPOSITE_W, store_skins.COMPOSITE_H), pygame.SRCALPHA)
    comp.blit(parrot._build_frame_bare(angle), (0, store_skins.PARROT_DY))
    draw_shades(comp, 50, 40, 22, 1)
    return parrot._add_outline(comp)


def product(draw_shades, c=160):
    s = pygame.Surface((c, c), pygame.SRCALPHA)
    draw_shades(s, c // 2, c // 2, 96, 1)
    return parrot._add_outline(s)


def checker(w, h, s=8):
    surf = pygame.Surface((w, h))
    a, b = (44, 50, 74), (36, 42, 64)
    for y in range(0, h, s):
        for x in range(0, w, s):
            surf.fill(a if (x // s + y // s) % 2 else b, (x, y, s, s))
    return surf


ROW_H = 240
PAD = 24
COLS_X = [PAD, PAD + 200, PAD + 200 + 200, PAD + 200 + 200 + 260]
SHEET_W = COLS_X[-1] + 360 + PAD
SHEET_H = 90 + ROW_H * len(VARIANTS) + PAD

sheet = pygame.Surface((SHEET_W, SHEET_H))
sheet.fill(BG)

title = font_t.render("SKYBIT SHADES  —  HEART SHADES  (shades_heart)   ·   round 1", True, INK)
sheet.blit(title, (PAD, 22))
sub = font_s.render("product shot eye_w=96   |   on-Pip @22px native   |   on-Pip @22px ~6x zoom", True, (170, 180, 200))
sheet.blit(sub, (PAD, 54))

for i, (label, fn) in enumerate(VARIANTS):
    y0 = 90 + i * ROW_H
    pygame.draw.rect(sheet, CARD, (PAD - 8, y0 - 4, SHEET_W - 2 * PAD + 16, ROW_H - 16),
                     border_radius=10)

    is_pick = (i == IMPLEMENTED)
    lab_col = PICKED if is_pick else INK
    sheet.blit(font.render(label, True, lab_col), (PAD, y0 + 8))
    if is_pick:
        tag = font_s.render("IMPLEMENTED  ->  draw.py", True, PICKED)
        sheet.blit(tag, (PAD, y0 + 32))
        pygame.draw.rect(sheet, PICKED, (PAD - 10, y0 - 6, SHEET_W - 2 * PAD + 20, ROW_H - 12),
                         2, border_radius=12)

    cy = y0 + 60

    # 1 · product shot on navy
    prod = product(fn)
    pr = prod.get_rect()
    px, py = COLS_X[0] + 6, cy + (160 - pr.h) // 2
    sheet.blit(prod, (px, py))

    # 2 · on-Pip native @22px (on a checker so alpha is honest)
    pip = on_pip(fn)
    chk = checker(pip.get_width() + 8, pip.get_height() + 8)
    bx, byy = COLS_X[1] + 30, cy + (160 - chk.get_height()) // 2
    sheet.blit(chk, (bx, byy))
    sheet.blit(pip, (bx + 4, byy + 4))
    pygame.draw.rect(sheet, (90, 100, 130), (bx, byy, chk.get_width(), chk.get_height()), 1)
    sheet.blit(font_s.render("native", True, (170, 180, 200)), (bx, byy + chk.get_height() + 4))

    # 3 · on-Pip 6x zoom
    zoom = 6
    big = pygame.transform.scale(pip, (pip.get_width() * zoom, pip.get_height() * zoom))
    zx, zy = COLS_X[2] + 6, cy + (170 - big.get_height()) // 2
    # frame the zoom on a checker too
    zchk = checker(big.get_width(), big.get_height(), s=zoom * 2)
    sheet.blit(zchk, (zx, zy))
    sheet.blit(big, (zx, zy))
    pygame.draw.rect(sheet, (90, 100, 130), (zx, zy, big.get_width(), big.get_height()), 1)
    sheet.blit(font_s.render("~6x zoom", True, (170, 180, 200)), (zx, zy + big.get_height() + 4))

out = os.path.join(os.path.dirname(__file__), "round_1.png")
pygame.image.save(sheet, out)
print("wrote", out, sheet.get_size())
