"""Compose the IRON RONIN round-3 (final) review sheet: hero shot + in-gameplay
crop + a 40px NEAREST truth read sampled x3 (flat hero, gameplay-tilt, flap
frame). Save under docs/. Exploration only — production art untouched.
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

CONCEPT = "IRON RONIN  ·  Armored Samurai-Ninja  ·  round_3 (final)"
OUT = "/home/user/skybit/docs/store_redesign/costume/ninja/design_3/round_3.png"

BG = (18, 16, 24)
INK = (236, 238, 246)
SUB = (150, 154, 168)

GP_W, GP_H = 230, 320


def _font(sz, bold=False):
    return pygame.font.SysFont("arial", sz, bold=bold)


def _label(surf, text, x, y, col=INK, sz=15, bold=False):
    surf.blit(_font(sz, bold).render(text, True, col), (x, y))


def _truth(source, *, frame_idx, tilt, native=40, mag=3):
    """NEAREST-shrink a clean hero crop of the bird (in the given pose) to
    `native`px then magnify — the 'does it survive gameplay size' acid test."""
    hero = ninja_render.hero_panel(source, 200, frame_idx=frame_idx, tilt=tilt,
                                   bg=(20, 18, 28))
    small = pygame.transform.scale(hero, (native, native))     # NEAREST
    return pygame.transform.scale(small, (native * mag, native * mag))


def main():
    build = design_3.build

    hero = ninja_render.hero_panel(build, 320)
    gp = ninja_render.gameplay_panel(build, GP_W, GP_H)

    # Three independent truth reads: flat mid-flight, gameplay dive-tilt, and a
    # different flap frame, so the read is judged across the animation + tilt.
    reads = [
        ("flat", _truth(build, frame_idx=2, tilt=0.0)),
        ("dive-tilt 10°", _truth(build, frame_idx=2, tilt=10.0)),
        ("flap frame 0", _truth(build, frame_idx=0, tilt=6.0)),
    ]
    tr_w = reads[0][1].get_width()
    tr_h = reads[0][1].get_height()

    pad = 24
    top = 86
    tr_col_w = max(tr_w, 250)
    cols_w = hero.get_width() + gp.get_width() + tr_col_w + pad * 3
    W = pad * 2 + cols_w
    H = top + max(hero.get_height(), gp.get_height(),
                  len(reads) * tr_h + (len(reads) - 1) * 26) + 78

    sheet = pygame.Surface((W, H))
    sheet.fill(BG)

    _label(sheet, CONCEPT, pad, 20, INK, 26, bold=True)
    _label(sheet, "design_3 · round_3 · capped dark dome (no doughnut) + "
                  "subordinate crest + continuous gold do-lacing · exploration "
                  "(live skin_ninja untouched)",
           pad, 54, SUB, 13)

    x, y = pad, top
    sheet.blit(hero, (x, y))
    _label(sheet, "HERO  (product shot)", x, y + hero.get_height() + 8, SUB, 13)
    x += hero.get_width() + pad

    sheet.blit(gp, (x, y))
    _label(sheet, "IN GAMEPLAY  (daytime biome)", x, y + gp.get_height() + 8,
           SUB, 13)
    x += gp.get_width() + pad

    _label(sheet, "40px TRUTH READ ×3  (NEAREST ÷ then ×3)", x,
           y + gp.get_height() + 8, SUB, 13)
    ty = y
    for tag, img in reads:
        sheet.blit(img, (x, ty))
        _label(sheet, tag, x + img.get_width() + 8, ty + img.get_height() // 2 - 8,
               SUB, 12)
        ty += tr_h + 26

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(sheet, OUT)
    print("saved", OUT, sheet.get_size())


if __name__ == "__main__":
    main()
