"""Compose the design_2 (CRIMSON FANG) ROUND 3 review sheet: hero shot +
in-gameplay panel + a NEAREST-neighbour 40px "truth read" magnified 3x.
Final ship-ready polish pass — headless only, reuses the ninja_render harness.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from tools import ninja_render
from tools.ninja_candidates.design_2 import build

OUT = "docs/store_redesign/costume/ninja/design_2/round_3.png"
TITLE = "CRIMSON FANG — Blood Assassin Kunoichi  (ninja design_2 · round 3)"

BG = (16, 15, 24)
INK = (236, 238, 245)
SUB = (150, 154, 170)


def _font(sz, bold=False):
    return pygame.font.SysFont("arial,dejavusans", sz, bold=bold)


def _label(surf, text, x, y, sz=15, col=INK, bold=False):
    surf.blit(_font(sz, bold).render(text, True, col), (x, y))


def _truth_read(build_fn, px=40, mag=3):
    """Render the bird, shrink to px (NEAREST) then magnify (NEAREST) so the
    sheet shows exactly what the player clocks at 40px in motion."""
    frame = build_fn(ninja_render.FRAME_IDX, ninja_render.TILT)
    bb = frame.get_bounding_rect()
    if bb.width and bb.height:
        frame = frame.subsurface(bb).copy()
    w, h = frame.get_size()
    s = px / max(w, h)
    small = pygame.transform.scale(frame, (max(1, int(w * s)), max(1, int(h * s))))
    return pygame.transform.scale(
        small, (small.get_width() * mag, small.get_height() * mag))


def main():
    W, H = 700, 420
    sheet = pygame.Surface((W, H))
    sheet.fill(BG)
    _label(sheet, TITLE, 22, 16, sz=20, bold=True)
    _label(sheet, "polish: plate nudged up + dark divider so slit & plate read "
                  "as TWO marks · scarf tip verified clear of the obi", 22, 42,
           sz=13, col=SUB)

    # Hero product shot.
    box = 250
    hero = ninja_render.hero_panel(build, box, tilt=0.0)
    hx, hy = 22, 74
    sheet.blit(hero, (hx, hy))
    _label(sheet, "HERO", hx + 6, hy + box + 4, sz=13, col=SUB, bold=True)

    # In-gameplay panel (portrait crop, per the harness window).
    gw, gh = 180, 250
    gp = ninja_render.gameplay_panel(build, gw, gh)
    gx = hx + box + 24
    sheet.blit(gp, (gx, hy))
    pygame.draw.rect(sheet, (60, 60, 76), (gx, hy, gw, gh), 1)
    _label(sheet, "IN GAMEPLAY (daytime biome)", gx + 6, hy + gh + 4,
           sz=13, col=SUB, bold=True)

    # 40px truth read (NEAREST, x3).
    tr = _truth_read(build)
    tx = gx + gw + 24
    panel_w = W - tx - 22
    pygame.draw.rect(sheet, (30, 29, 42), (tx, hy, panel_w, box), border_radius=10)
    sheet.blit(tr, tr.get_rect(center=(tx + panel_w // 2, hy + box // 2)))
    _label(sheet, "40px TRUTH READ (x3, nearest)", tx + 4, hy + box + 4,
           sz=12, col=SUB, bold=True)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pygame.image.save(sheet, OUT)
    print("saved", OUT)


if __name__ == "__main__":
    main()
