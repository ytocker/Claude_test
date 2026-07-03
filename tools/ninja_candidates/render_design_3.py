"""Compose the IRON RONIN review sheet: hero shot + in-gameplay crop + a 40px
truth read (NEAREST-shrink to 40px, magnified 3x). Save under docs/.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

import importlib.util

_here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "design_3", os.path.join(_here, "design_3.py"))
design_3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(design_3)

from tools import ninja_render

CONCEPT = "IRON RONIN  ·  Armored Samurai-Ninja"
OUT = "/home/user/skybit/docs/store_redesign/costume/ninja/design_3/round_1.png"

BG = (18, 16, 24)
PANEL = (28, 26, 38)
INK = (236, 238, 246)
SUB = (150, 154, 168)


def _font(sz, bold=False):
    return pygame.font.SysFont("arial", sz, bold=bold)


def _label(surf, text, x, y, col=INK, sz=15, bold=False):
    surf.blit(_font(sz, bold).render(text, True, col), (x, y))


# gameplay_panel crops to GH*0.78 tall; the crop must stay within the 360-wide
# canvas, so the panel aspect (w/h) is held at/below 0.72.
GP_W, GP_H = 230, 320


def truth_read(build, native=40, mag=3):
    """NEAREST-neighbor shrink to `native`px then magnify — the 'does it survive
    gameplay size' acid test. Pulled from the hero crop so it isolates the bird
    (not the sky) at true gameplay sprite scale."""
    hero = ninja_render.hero_panel(build, 200, bg=(20, 18, 28))
    small = pygame.transform.scale(hero, (native, native))     # NEAREST
    return pygame.transform.scale(small, (native * mag, native * mag))


def main():
    build = design_3.build

    hero = ninja_render.hero_panel(build, 320)
    gp = ninja_render.gameplay_panel(build, GP_W, GP_H)
    tr = truth_read(build)

    pad = 24
    top = 86
    hero_w = hero.get_width()
    gp_w = gp.get_width()
    tr_w = tr.get_width()
    # Last column carries a long caption; give it room so the label isn't clipped.
    cols_w = hero_w + gp_w + max(tr_w, 250) + pad * 3
    W = pad * 2 + cols_w
    H = top + max(hero.get_height(), gp.get_height(), tr.get_height()) + 78

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    _label(sheet, CONCEPT, pad, 20, INK, 26, bold=True)
    _label(sheet, "design_3 · round_1 · red-lacquer sode + crescent maedate + "
                  "fanged menpo · exploration (live skin_ninja untouched)",
           pad, 54, SUB, 13)

    x = pad
    y = top
    sheet.blit(hero, (x, y))
    _label(sheet, "HERO  (product shot)", x, y + hero.get_height() + 8, SUB, 13)
    x += hero_w + pad

    sheet.blit(gp, (x, y))
    _label(sheet, "IN GAMEPLAY  (daytime biome)", x, y + gp.get_height() + 8,
           SUB, 13)
    x += gp_w + pad

    # Center the (smaller) truth read against the 300px columns.
    ty = y + (gp.get_height() - tr.get_height()) // 2
    sheet.blit(tr, (x, ty))
    _label(sheet, "40px TRUTH READ  (NEAREST ÷ then ×3)", x,
           y + gp.get_height() + 8, SUB, 13)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(sheet, OUT)
    print("saved", OUT, sheet.get_size())


if __name__ == "__main__":
    main()
