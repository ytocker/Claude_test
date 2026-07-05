"""Round-1 exploration sheet for SHADES style `shades_3d` (3D anaglyph
glasses). Stamps the 3 variants, each as a big product shot (eye_w=96) plus
the on-Pip overlay at the true in-game eye_w=22 — shown native AND at ~6x
zoom where single-pixel reads matter. Headless (SDL dummy).

Run:  SDL_VIDEODRIVER=dummy python docs/shades/shades_3d/render_sheet.py
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from game import parrot, store_skins  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import variants  # noqa: E402


# Marked (*) is the variant chosen for docs/shades/shades_3d/draw.py.
VARIANTS = [
    ("V1 cardboard *", variants.draw_shades_cardboard, True),
    ("V2 plastic",     variants.draw_shades_plastic,   False),
    ("V3 glitch",      variants.draw_shades_glitch,    False),
]


def on_pip(draw_shades, angle=-10):
    comp = pygame.Surface((store_skins.COMPOSITE_W, store_skins.COMPOSITE_H),
                          pygame.SRCALPHA)
    comp.blit(parrot._build_frame_bare(angle), (0, store_skins.PARROT_DY))
    draw_shades(comp, 50, 40, 22, 1)
    return parrot._add_outline(comp)


def product_shot(draw_shades, canvas=160):
    surf = pygame.Surface((canvas, canvas), pygame.SRCALPHA)
    draw_shades(surf, canvas // 2, canvas // 2, 96, 1)
    return parrot._add_outline(surf)


def _checker(surf, rect, a=(54, 60, 78), b=(44, 50, 66), s=8):
    for y in range(rect.top, rect.bottom, s):
        for x in range(rect.left, rect.right, s):
            c = a if ((x // s + y // s) % 2 == 0) else b
            surf.fill(c, (x, y, min(s, rect.right - x), min(s, rect.bottom - y)))


def main():
    pygame.font.init()
    font = pygame.font.SysFont("Arial", 17, bold=True)
    small = pygame.font.SysFont("Arial", 14, bold=True)
    tiny = pygame.font.SysFont("Arial", 11)

    CELL_W, CELL_H = 430, 250
    MARGIN = 24
    TITLE_H = 52
    sheet_w = MARGIN * 2 + CELL_W
    sheet_h = TITLE_H + MARGIN + len(VARIANTS) * CELL_H + MARGIN

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((30, 34, 48))
    sheet.blit(font.render(
        "SKYBIT SHADES  ·  shades_3d (anaglyph 3D)  ·  round 1  ·  "
        "RED=ear  CYAN=beak  ·  * = implemented",
        True, (235, 240, 250)), (MARGIN, 18))

    for i, (label, fn, picked) in enumerate(VARIANTS):
        x = MARGIN
        y = TITLE_H + MARGIN + i * CELL_H
        cell = pygame.Rect(x, y, CELL_W, CELL_H - 12)
        pygame.draw.rect(sheet, (40, 45, 62), cell, border_radius=10)
        edge = (255, 214, 90) if picked else (70, 78, 100)
        pygame.draw.rect(sheet, edge, cell, 2 if picked else 1, border_radius=10)

        # Product shot (checkered) — eye_w=96.
        prod = product_shot(fn)
        prod_rect = pygame.Rect(cell.left + 10, cell.top + 28, 180, 180)
        _checker(sheet, prod_rect)
        sheet.blit(prod, prod.get_rect(center=prod_rect.center).topleft)
        sheet.blit(tiny.render("product  eye_w=96", True, (180, 188, 206)),
                   (prod_rect.left, prod_rect.bottom + 2))

        # On-Pip @22px — native.
        pip = on_pip(fn)
        nat_rect = pygame.Rect(prod_rect.right + 14, cell.top + 28, 96, 180)
        _checker(sheet, nat_rect, a=(48, 54, 72), b=(40, 46, 62))
        sheet.blit(pip, pip.get_rect(center=nat_rect.center).topleft)
        sheet.blit(tiny.render("on-Pip  native", True, (180, 188, 206)),
                   (nat_rect.left, nat_rect.bottom + 2))

        # On-Pip @22px — ~6x zoom (true in-game scale, judged big).
        zoom = pygame.transform.rotozoom(pip, 0, 6.0)
        z_rect = pygame.Rect(nat_rect.right + 14, cell.top + 28,
                             CELL_W - (nat_rect.right + 14 - cell.left) - 14, 180)
        _checker(sheet, z_rect, a=(48, 54, 72), b=(40, 46, 62))
        prev = sheet.get_clip()
        sheet.set_clip(z_rect)
        # Centre the head (~comp x=50,y=40) of the zoomed sprite in the panel.
        zw, zh = zoom.get_size()
        head = (int(50 / store_skins.COMPOSITE_W * zw),
                int(40 / store_skins.COMPOSITE_H * zh))
        sheet.blit(zoom, (z_rect.centerx - head[0], z_rect.centery - head[1]))
        sheet.set_clip(prev)
        pygame.draw.rect(sheet, (70, 78, 100), z_rect, 1)
        sheet.blit(tiny.render("on-Pip  ~6x zoom", True, (180, 188, 206)),
                   (z_rect.left, z_rect.bottom + 2))

        # Label.
        lab_c = (255, 224, 120) if picked else (220, 226, 240)
        sheet.blit(small.render(label, True, lab_c),
                   (cell.left + 10, cell.top + 6))

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "round_1.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path, sheet.get_size())


if __name__ == "__main__":
    main()
