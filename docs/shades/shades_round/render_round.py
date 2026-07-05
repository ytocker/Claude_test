"""Round-1 exploration sheet for ROUND SHADES (Lennon).

Three variants, each shown as: product shot (eye_w=96), on-Pip @22px native,
and a ~6x zoom of the on-Pip head so the 1px-rim read can be judged honestly.

Run:  SDL_VIDEODRIVER=dummy python docs/shades/shades_round/render_round.py
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from game import parrot, store_skins  # noqa: E402
import variants  # noqa: E402


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


def _checker(surf, rect, a, b, s=8):
    for y in range(rect.top, rect.bottom, s):
        for x in range(rect.left, rect.right, s):
            c = a if ((x // s + y // s) % 2 == 0) else b
            surf.fill(c, (x, y, min(s, rect.right - x), min(s, rect.bottom - y)))


def main():
    out_name = sys.argv[1] if len(sys.argv) > 1 else "round_1"
    pygame.font.init()
    title_f = pygame.font.SysFont("Arial", 20, bold=True)
    lab_f = pygame.font.SysFont("Arial", 16, bold=True)
    small_f = pygame.font.SysFont("Arial", 12)

    CELL_W, CELL_H = 470, 230
    MARGIN = 26
    TITLE_H = 58
    sheet_w = MARGIN * 2 + CELL_W
    sheet_h = TITLE_H + MARGIN + len(variants.VARIANTS) * CELL_H + MARGIN

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((30, 34, 48))
    sheet.blit(title_f.render(
        "SKYBIT — ROUND SHADES (Lennon)  ·  round 1  ·  product @96  +  on-Pip @22px native & ~6x",
        True, (235, 240, 250)), (MARGIN, 18))

    for i, (label, fn, picked) in enumerate(variants.VARIANTS):
        x = MARGIN
        y = TITLE_H + MARGIN + i * CELL_H
        cell = pygame.Rect(x, y, CELL_W, CELL_H - 14)
        accent = (255, 214, 110) if picked else (70, 78, 100)
        pygame.draw.rect(sheet, (40, 45, 62), cell, border_radius=12)
        pygame.draw.rect(sheet, accent, cell, 3 if picked else 1,
                         border_radius=12)

        # Product shot (checkered, light + dark to test the rim on both).
        prod = product(fn)
        p_rect = pygame.Rect(cell.left + 12, cell.top + 12, 180, 180)
        _checker(sheet, p_rect, (60, 66, 86), (48, 54, 72))
        sheet.blit(prod, prod.get_rect(center=p_rect.center).topleft)

        # On-Pip native @22px.
        pip = on_pip(fn)
        n_rect = pygame.Rect(p_rect.right + 14, cell.top + 12, 96, 180)
        _checker(sheet, n_rect, (50, 56, 74), (42, 48, 64))
        sheet.blit(pip, pip.get_rect(center=(n_rect.centerx,
                                             n_rect.top + 56)).topleft)
        sheet.blit(small_f.render("native 22px", True, (200, 208, 224)),
                   (n_rect.left + 8, n_rect.bottom - 18))

        # On-Pip ~6x zoom — the honest small-size read.
        z_rect = pygame.Rect(n_rect.right + 14, cell.top + 12, 150, 180)
        _checker(sheet, z_rect, (50, 56, 74), (42, 48, 64))
        zoom = pygame.transform.scale_by(pip, 6)
        # Centre on the head (eye at comp (50,40)); crop region around it.
        head = pygame.Surface((150, 150), pygame.SRCALPHA)
        head.blit(zoom, (-(50 * 6) + 75, -(40 * 6) + 70))
        sheet.blit(head, head.get_rect(center=(z_rect.centerx,
                                               z_rect.centery - 6)).topleft)
        sheet.blit(small_f.render("~6x head", True, (200, 208, 224)),
                   (z_rect.left + 8, z_rect.bottom - 18))

        tag = "  [IMPLEMENTED]" if picked else ""
        sheet.blit(lab_f.render(label + tag, True,
                                accent if picked else (224, 230, 244)),
                   (cell.left + 12, cell.bottom + 1))

    out_path = os.path.join(_HERE, f"{out_name}.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path, sheet.get_size())


if __name__ == "__main__":
    main()
