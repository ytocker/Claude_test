"""Render the STAR SHADES round-2 rework sheet.

The hard bar is the 22px read over Pip's scarlet head: the five points must be
COUNTABLE. So the sheet leads with the in-game size (native + a big nearest-
neighbour zoom of just the eye) and keeps the eye_w=96 product shot as the
glam reference. Headless (SDL dummy) so it runs under agents/CI.

Run:  SDL_VIDEODRIVER=dummy python docs/shades/shades_star/render_round2.py
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game import parrot, store_skins        # noqa: E402
import draw as star                          # noqa: E402


def on_pip(angle=-10):
    comp = pygame.Surface((store_skins.COMPOSITE_W, store_skins.COMPOSITE_H),
                          pygame.SRCALPHA)
    comp.blit(parrot._build_frame_bare(angle), (0, store_skins.PARROT_DY))
    star.draw_shades(comp, 50, 40, 22, 1)
    return parrot._add_outline(comp)


def product(c=160):
    s = pygame.Surface((c, c), pygame.SRCALPHA)
    star.draw_shades(s, c // 2, c // 2, 96, 1)
    return parrot._add_outline(s)


def _checker(surf, rect, a=(54, 60, 78), b=(44, 50, 66), s=8):
    for y in range(rect.top, rect.bottom, s):
        for x in range(rect.left, rect.right, s):
            c = a if ((x // s + y // s) % 2 == 0) else b
            surf.fill(c, (x, y, min(s, rect.right - x), min(s, rect.bottom - y)))


def main():
    pygame.font.init()
    title_f = pygame.font.SysFont("Arial", 22, bold=True)
    label_f = pygame.font.SysFont("Arial", 16, bold=True)
    small_f = pygame.font.SysFont("Arial", 13)

    MARGIN = 26
    TITLE_H = 56
    sheet_w = MARGIN * 2 + 900
    sheet_h = TITLE_H + MARGIN + 470 + MARGIN
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((28, 32, 46))
    sheet.blit(title_f.render(
        "SKYBIT — STAR SHADES (shades_star)  ·  round 2 REWORK  ·  "
        "gold rim · fat points · electric-blue glass  ·  must count 5 pts @22px",
        True, (236, 242, 252)), (MARGIN, 18))

    prod = product()
    pip = on_pip()

    # --- Product shot @96 (checkered backdrop) ---------------------------
    pr = pygame.Rect(MARGIN, TITLE_H + MARGIN, 300, 300)
    _checker(sheet, pr)
    sheet.blit(prod, prod.get_rect(center=pr.center).topleft)
    pygame.draw.rect(sheet, (74, 82, 104), pr, 1)
    sheet.blit(label_f.render("PRODUCT  eye_w=96", True, (224, 230, 244)),
               (pr.left, pr.bottom + 6))

    # --- On a ~24px scarlet head, native @22 -----------------------------
    # Pip's head is ~24px; the overlay must sit on that warm scarlet, not on a
    # neutral swatch, so the value-contrast claim is honest.
    nx = pr.right + 40
    nr = pygame.Rect(nx, TITLE_H + MARGIN, 130, 130)
    _checker(sheet, nr, a=(150, 26, 30), b=(132, 22, 26), s=10)  # scarlet head tone
    sheet.blit(pip, pip.get_rect(center=nr.center).topleft)
    pygame.draw.rect(sheet, (74, 82, 104), nr, 1)
    sheet.blit(label_f.render("ON PIP  native 22px", True, (224, 230, 244)),
               (nr.left, nr.bottom + 6))

    # --- Big nearest-neighbour zoom of just the eye ----------------------
    # _add_outline pads by 3, so composite eye (50,40) lands at ~(53,43).
    # Centre between the two lenses and widen the crop so BOTH stars and all
    # their points sit fully inside the zoom (the near lens sits ~+5px of the
    # far one).
    ex, ey = 56, 43
    crop = 42
    head = pygame.Surface((crop, crop), pygame.SRCALPHA)
    head.blit(pip, (-(ex - crop // 2), -(ey - crop // 2)))
    Z = 8
    zoom = pygame.transform.scale(head, (crop * Z, crop * Z))
    zr = zoom.get_rect(topleft=(nr.right + 40, TITLE_H + MARGIN))
    # Scarlet backing behind the zoom too so the read is judged in context.
    sheet.fill((150, 26, 30), zr)
    sheet.blit(zoom, zr.topleft)
    pygame.draw.rect(sheet, (255, 214, 90), zr, 2)
    sheet.blit(label_f.render(f"~{Z}x EYE — count the 5 points", True,
               (255, 226, 120)), (zr.left, zr.bottom + 6))

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "round_2.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path, sheet.get_size())


if __name__ == "__main__":
    main()
