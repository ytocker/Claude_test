"""Scratch render harness — PIXEL SHADES round 1, 3 variants.

For each variant: a product shot (eye_w≈96) on a checker + on-Pip @22px native
+ a ~6x zoom of the Pip head, onto one labelled grid. Headless (SDL dummy).

Run:  SDL_VIDEODRIVER=dummy python docs/shades/shades_pixel/render_sheet.py
"""
import os
import sys
import importlib.util

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from game import parrot, store_skins  # noqa: E402

# Load the local draw module (not on the package path).
_spec = importlib.util.spec_from_file_location("shades_pixel_draw",
                                               os.path.join(_HERE, "draw.py"))
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

VARIANTS = [
    ("A · pure block", _mod.draw_shades_pure, False),
    ("B · top-glint row", _mod.draw_shades_glint, False),
    ("C · thug life  [CHOSEN — draw_shades]", _mod.draw_shades, True),
]


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


def _checker(surf, rect, a=(54, 60, 78), b=(44, 50, 66), s=8):
    for y in range(rect.top, rect.bottom, s):
        for x in range(rect.left, rect.right, s):
            col = a if ((x // s + y // s) % 2 == 0) else b
            surf.fill(col, (x, y, min(s, rect.right - x), min(s, rect.bottom - y)))


def main():
    pygame.font.init()
    font = pygame.font.SysFont("Arial", 18, bold=True)
    small = pygame.font.SysFont("Arial", 14, bold=True)
    tiny = pygame.font.SysFont("Arial", 11)

    CELL_W, CELL_H = 560, 250
    MARGIN, TITLE_H = 24, 52
    sheet_w = MARGIN * 2 + CELL_W
    sheet_h = TITLE_H + MARGIN + len(VARIANTS) * CELL_H + MARGIN

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((30, 34, 48))
    sheet.blit(font.render(
        "SKYBIT — PIXEL SHADES (shades_pixel)  ·  round 1  ·  product @96  +  on-Pip @22 (native + ~6x)",
        True, (235, 240, 250)), (MARGIN, 18))

    for i, (label, fn, chosen) in enumerate(VARIANTS):
        x = MARGIN
        y = TITLE_H + MARGIN + i * CELL_H
        cell = pygame.Rect(x, y, CELL_W, CELL_H - 16)
        border = (255, 210, 90) if chosen else (70, 78, 100)
        pygame.draw.rect(sheet, (40, 45, 62), cell, border_radius=10)
        pygame.draw.rect(sheet, border, cell, 2 if chosen else 1, border_radius=10)

        col = (255, 210, 90) if chosen else (222, 228, 240)
        sheet.blit(small.render(label, True, col), (cell.left + 12, cell.top + 8))

        # Product shot.
        pr_rect = pygame.Rect(cell.left + 12, cell.top + 30, 180, 180)
        _checker(sheet, pr_rect)
        pygame.draw.rect(sheet, (70, 78, 100), pr_rect, 1)
        prod = product(fn)
        sheet.blit(prod, prod.get_rect(center=pr_rect.center).topleft)
        sheet.blit(tiny.render("product · eye_w=96", True, (200, 206, 220)),
                   (pr_rect.left, pr_rect.bottom + 2))

        pip = on_pip(fn)
        # On-Pip native @22.
        nat_rect = pygame.Rect(pr_rect.right + 16, cell.top + 30, 96, 130)
        _checker(sheet, nat_rect, a=(48, 54, 72), b=(40, 46, 62))
        pygame.draw.rect(sheet, (70, 78, 100), nat_rect, 1)
        sheet.blit(pip, pip.get_rect(center=nat_rect.center).topleft)
        sheet.blit(tiny.render("native @22", True, (200, 206, 220)),
                   (nat_rect.left, nat_rect.bottom + 2))

        # On-Pip ~6x zoom.
        z_rect = pygame.Rect(nat_rect.right + 12, cell.top + 30, 200, 200)
        _checker(sheet, z_rect, a=(48, 54, 72), b=(40, 46, 62))
        pygame.draw.rect(sheet, (70, 78, 100), z_rect, 1)
        zoom = pygame.transform.scale_by(pip, 6)
        sheet.blit(zoom, zoom.get_rect(center=z_rect.center).topleft)
        sheet.blit(tiny.render("~6x zoom (in-game read)", True, (200, 206, 220)),
                   (z_rect.left, z_rect.bottom + 2))

    out = os.path.join(_HERE, "round_1.png")
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    main()
