"""Round-2 final sheet for SHADES style `shades_3d` (anaglyph 3D, plastic
frame). One design only. Shows the eye_w=96 product shot, then the in-game
eye_w=22 read where the gag has to survive — laid over a ~24px SCARLET head
disc (the camouflage worst-case the critique called out) AND on full Pip —
each native plus ~6x zoom. Headless (SDL dummy).

Run:  SDL_VIDEODRIVER=dummy python docs/shades/shades_3d/render_round2.py
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
from game.draw import BIRD_RED, BIRD_RED_D  # scarlet head tone  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import draw as final  # the shipped single design  # noqa: E402


def product_shot(canvas=160):
    surf = pygame.Surface((canvas, canvas), pygame.SRCALPHA)
    final.draw_shades(surf, canvas // 2, canvas // 2, 96, 1)
    return parrot._add_outline(surf)


def on_pip(angle=-10):
    comp = pygame.Surface((store_skins.COMPOSITE_W, store_skins.COMPOSITE_H),
                          pygame.SRCALPHA)
    comp.blit(parrot._build_frame_bare(angle), (0, store_skins.PARROT_DY))
    final.draw_shades(comp, 50, 40, 22, 1)
    return parrot._add_outline(comp)


def on_scarlet_head():
    # Worst case for camouflage: the red lens sitting on bare scarlet skin.
    s = pygame.Surface((64, 64), pygame.SRCALPHA)
    pygame.draw.circle(s, BIRD_RED_D, (32, 33), 14)
    pygame.draw.circle(s, BIRD_RED, (32, 32), 13)
    final.draw_shades(s, 32, 30, 22, 1)
    return s


def _checker(surf, rect, a=(54, 60, 78), b=(44, 50, 66), s=8):
    for y in range(rect.top, rect.bottom, s):
        for x in range(rect.left, rect.right, s):
            c = a if ((x // s + y // s) % 2 == 0) else b
            surf.fill(c, (x, y, min(s, rect.right - x), min(s, rect.bottom - y)))


def _panel(sheet, rect, sprite, head, caption, font, zoom=1.0,
           a=(48, 54, 72), b=(40, 46, 62)):
    # `head` is the glasses centre in the UN-zoomed sprite's own pixel space.
    base_w, base_h = sprite.get_size()
    _checker(sheet, rect, a=a, b=b)
    if zoom != 1.0:
        sprite = pygame.transform.rotozoom(sprite, 0, zoom)
    prev = sheet.get_clip()
    sheet.set_clip(rect)
    hx = int(head[0] / base_w * sprite.get_width())
    hy = int(head[1] / base_h * sprite.get_height())
    sheet.blit(sprite, (rect.centerx - hx, rect.centery - hy))
    sheet.set_clip(prev)
    pygame.draw.rect(sheet, (70, 78, 100), rect, 1)
    sheet.blit(font.render(caption, True, (180, 188, 206)),
               (rect.left, rect.bottom + 2))


def main():
    pygame.font.init()
    title = pygame.font.SysFont("Arial", 18, bold=True)
    tiny = pygame.font.SysFont("Arial", 11)

    MARGIN = 24
    TITLE_H = 56
    PANEL = 188
    GAP = 14
    panels = 5
    sheet_w = MARGIN * 2 + PANEL * panels + GAP * (panels - 1)
    sheet_h = TITLE_H + PANEL + 28 + MARGIN

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((30, 34, 48))
    sheet.blit(title.render(
        "SKYBIT SHADES  ·  shades_3d (anaglyph 3D, plastic frame)  ·  round 2  "
        "·  RED=ear  CYAN=beak  ·  dark frame divides the lenses",
        True, (235, 240, 250)), (MARGIN, 18))

    prod = product_shot()
    pip = on_pip()
    head = on_scarlet_head()

    x = MARGIN
    y = TITLE_H

    # 1. Product shot, eye_w=96.
    r = pygame.Rect(x, y, PANEL, PANEL)
    _checker(sheet, r)
    sheet.blit(prod, prod.get_rect(center=r.center).topleft)
    pygame.draw.rect(sheet, (70, 78, 100), r, 1)
    sheet.blit(tiny.render("product  eye_w=96", True, (180, 188, 206)),
               (r.left, r.bottom + 2))
    x += PANEL + GAP

    # 2 + 3. Over a ~24px scarlet head — the camouflage test (native + zoom).
    r = pygame.Rect(x, y, PANEL, PANEL)
    _panel(sheet, r, head, (32, 30), "scarlet head  native", tiny,
           a=(58, 50, 64), b=(50, 44, 56))
    x += PANEL + GAP
    r = pygame.Rect(x, y, PANEL, PANEL)
    _panel(sheet, r, head, (32, 30), "scarlet head  ~7x zoom", tiny, zoom=7.0,
           a=(58, 50, 64), b=(50, 44, 56))
    x += PANEL + GAP

    # 4 + 5. On full Pip @22px (native + zoom).
    r = pygame.Rect(x, y, PANEL, PANEL)
    _panel(sheet, r, pip, (50, 40), "on-Pip  native", tiny)
    x += PANEL + GAP
    r = pygame.Rect(x, y, PANEL, PANEL)
    _panel(sheet, r, pip, (50, 40), "on-Pip  ~6x zoom", tiny, zoom=6.0)

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "round_2.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path, sheet.get_size())


if __name__ == "__main__":
    main()
