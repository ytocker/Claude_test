"""Render the round-1 MONOCLE exploration sheet (3 variants).

Each column: product shot (eye_w=96) + on-Pip @22px (native) + ~6x zoom.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()

from game import parrot, store_skins
from variants import VARIANTS

CHOSEN = "A"   # implemented variant

BG = (28, 34, 52)          # navy store-card backdrop
PANEL = (40, 48, 70)
TXT = (236, 240, 248)
SUB = (170, 180, 200)
MARK = (255, 206, 80)


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


def main():
    font = pygame.font.SysFont("dejavusans", 18, bold=True)
    fsm = pygame.font.SysFont("dejavusans", 13)

    cols = len(VARIANTS)
    col_w = 230
    margin = 24
    head_h = 56
    prod_h = 176
    pip_h = 200
    sheet_w = margin * 2 + col_w * cols
    sheet_h = head_h + prod_h + pip_h + margin * 2

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(BG)

    title = font.render("SHADES — MONOCLE  ·  round 1", True, TXT)
    sheet.blit(title, (margin, 14))
    note = fsm.render("single front-eye lens + dangling chain  ·  product (96px)  +  on-Pip @22px (native + 6x)",
                      True, SUB)
    sheet.blit(note, (margin, 36))

    y0 = head_h + margin
    for i, (label, fn) in enumerate(VARIANTS):
        x0 = margin + i * col_w
        panel = pygame.Rect(x0 + 6, y0, col_w - 12, prod_h + pip_h - 8)
        pygame.draw.rect(sheet, PANEL, panel, border_radius=10)

        is_chosen = label.strip().startswith(CHOSEN)
        lab = font.render(label.strip(), True, MARK if is_chosen else TXT)
        sheet.blit(lab, (x0 + 18, y0 + 8))
        if is_chosen:
            tag = fsm.render("IMPLEMENTED", True, MARK)
            sheet.blit(tag, (x0 + 18, y0 + 30))
            pygame.draw.rect(sheet, MARK, panel, 2, border_radius=10)

        # Product shot, centred in the panel.
        prod = product(fn)
        prect = prod.get_rect(center=(x0 + col_w // 2, y0 + 56 + prod.get_height() // 2 - 8))
        sheet.blit(prod, prect.topleft)

        # On-Pip native + 6x.
        pip = on_pip(fn)
        py = y0 + prod_h + 18
        sheet.blit(pip, (x0 + 30, py + 24))
        cap1 = fsm.render("22px native", True, SUB)
        sheet.blit(cap1, (x0 + 24, py))

        zoom = 6
        big = pygame.transform.scale(pip, (pip.get_width() * zoom,
                                           pip.get_height() * zoom))
        # Crop around the head so the eyepiece fills the zoom tile.
        crop = pygame.Surface((150, 150), pygame.SRCALPHA)
        # Head centre in composite ~ (50, 40); outline pad +2.
        hx, hy = (50 + 2) * zoom, (40 + 2) * zoom
        crop.blit(big, (75 - hx, 75 - hy))
        bx = x0 + col_w - 150 - 14
        pygame.draw.rect(sheet, (22, 26, 40), (bx - 2, py + 22, 154, 154))
        sheet.blit(crop, (bx, py + 24))
        cap2 = fsm.render("6x", True, SUB)
        sheet.blit(cap2, (bx, py))

    out = "/home/user/skybit/docs/shades/shades_monocle/round_1.png"
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    main()
