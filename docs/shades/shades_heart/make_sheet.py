"""Render the round-1 review sheet for HEART SHADES.

Each variant shown as: product shot (eye_w=96) + on-Pip @22px native + ~6x zoom
of the head region (so 1px decisions at product size AND in-game are visible).
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import sys
import pygame
pygame.init()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from game import parrot, store_skins
from explore import VARIANTS

BG = (24, 28, 46)
CARD = (32, 38, 60)
INK = (236, 240, 248)
PICKED = (120, 230, 150)
MUTE = (170, 180, 200)

font = pygame.font.SysFont("dejavusans", 18, bold=True)
font_s = pygame.font.SysFont("dejavusans", 12)
font_t = pygame.font.SysFont("dejavusans", 22, bold=True)

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


def crop_nonempty(surf, pad=2):
    r = surf.get_bounding_rect()
    r.inflate_ip(pad * 2, pad * 2)
    r = r.clip(surf.get_rect())
    out = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
    out.blit(surf, (0, 0), r)
    return out


def checker(w, h, s=8):
    surf = pygame.Surface((w, h))
    a, b = (44, 50, 74), (36, 42, 64)
    for y in range(0, h, s):
        for x in range(0, w, s):
            surf.fill(a if (x // s + y // s) % 2 else b, (x, y, s, s))
    return surf


ROW_H = 220
PAD = 24
C0 = PAD + 6                 # product
C1 = PAD + 210               # native on-Pip
C2 = PAD + 400               # 6x zoom of cropped head
SHEET_W = C2 + 360 + PAD
SHEET_H = 88 + ROW_H * len(VARIANTS) + PAD

sheet = pygame.Surface((SHEET_W, SHEET_H))
sheet.fill(BG)

sheet.blit(font_t.render("SKYBIT SHADES  —  HEART SHADES  (shades_heart)   ·   round 1", True, INK), (PAD, 20))
sheet.blit(font_s.render(
    "product shot eye_w=96      |      on-Pip @22px native      |      on-Pip head ~6x zoom (in-game read)",
    True, MUTE), (PAD, 52))

for i, (label, fn) in enumerate(VARIANTS):
    y0 = 88 + i * ROW_H
    pygame.draw.rect(sheet, CARD, (PAD - 8, y0, SHEET_W - 2 * PAD + 16, ROW_H - 14), border_radius=10)

    is_pick = (i == IMPLEMENTED)
    sheet.blit(font.render(label, True, PICKED if is_pick else INK), (PAD, y0 + 10))
    if is_pick:
        sheet.blit(font_s.render("IMPLEMENTED  ->  draw.py", True, PICKED), (PAD, y0 + 34))
        pygame.draw.rect(sheet, PICKED, (PAD - 10, y0 - 2, SHEET_W - 2 * PAD + 20, ROW_H - 10),
                         2, border_radius=12)

    midy = y0 + ROW_H // 2

    # 1 · product shot
    prod = crop_nonempty(product(fn))
    sheet.blit(prod, (C0, midy - prod.get_height() // 2 + 6))

    # 2 · native on-Pip on a checker
    pip = crop_nonempty(on_pip(fn))
    chk = checker(pip.get_width() + 10, pip.get_height() + 10)
    bx, byy = C1, midy - chk.get_height() // 2
    sheet.blit(chk, (bx, byy))
    sheet.blit(pip, (bx + 5, byy + 5))
    pygame.draw.rect(sheet, (90, 100, 130), (bx, byy, chk.get_width(), chk.get_height()), 1)
    sheet.blit(font_s.render("native 22px", True, MUTE), (bx, byy + chk.get_height() + 4))

    # 3 · 6x zoom of the cropped head/shades region only
    full = on_pip(fn)
    # head sits near (50,40) in composite; crop a window around it then trim.
    win = full.subsurface(pygame.Rect(26, 16, 44, 44)).copy()
    win = crop_nonempty(win, pad=1)
    zoom = 6
    big = pygame.transform.scale(win, (win.get_width() * zoom, win.get_height() * zoom))
    zchk = checker(big.get_width(), big.get_height(), s=zoom)
    zx, zy = C2, midy - big.get_height() // 2
    sheet.blit(zchk, (zx, zy))
    sheet.blit(big, (zx, zy))
    pygame.draw.rect(sheet, (90, 100, 130), (zx, zy, big.get_width(), big.get_height()), 1)
    sheet.blit(font_s.render("~6x zoom (head)", True, MUTE), (zx, zy + big.get_height() + 4))

out = os.path.join(os.path.dirname(__file__), "round_1.png")
pygame.image.save(sheet, out)
print("wrote", out, sheet.get_size())
