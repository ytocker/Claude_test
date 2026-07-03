"""Render the SOLAR WAR CHIEF round-1 review sheet.

Stitches the four judging panels the brief calls for (daytime gameplay crop,
dark hero shot, 40px NEAREST truth, natural-size 4-frame filmstrip) into one
PNG under docs/. Scratch tooling — not shipped in the bundle.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from tools import ninja_render
from tools.thunderbird_candidates.design_3 import build

FONT = pygame.font.SysFont("Arial", 14, bold=True)
SMALL = pygame.font.SysFont("Arial", 11)
BG = (18, 16, 22)


def label(surf, text, x, y, color=(240, 232, 220)):
    surf.blit(FONT.render(text, True, color), (x, y))


def main():
    gp = ninja_render.gameplay_panel(build, 220, 320)
    hero = ninja_render.hero_panel(build, 220)

    # 40px NEAREST truth of the canonical mid-flight pose.
    truth = build(2, 10.0)
    tw = 40
    th = max(1, int(truth.get_height() * tw / truth.get_width()))
    truth40 = pygame.transform.scale(truth, (tw, th))          # NEAREST
    truth40x = pygame.transform.scale(truth40, (tw * 4, th * 4))  # blown up 4x, still nearest

    # 4-frame filmstrip at natural size.
    frames = [build(i, 0.0) for i in range(4)]

    pad = 16
    top_h = max(gp.get_height(), hero.get_height()) + 40
    strip_h = max(f.get_height() for f in frames) + 40
    truth_h = truth40x.get_height() + 60
    sheet_w = pad * 3 + gp.get_width() + hero.get_width()
    fw_total = sum(f.get_width() + 10 for f in frames)
    sheet_w = max(sheet_w, pad * 2 + fw_total, pad * 2 + truth40x.get_width() + 200)
    sheet_h = pad + 20 + top_h + strip_h + truth_h + pad

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(BG)

    label(sheet, "SOLAR WAR CHIEF  —  thunderbird design_3  —  round 2",
          pad, pad, (255, 200, 90))

    y0 = pad + 28
    sheet.blit(gp, (pad, y0 + 20))
    label(sheet, "Gameplay (daytime)", pad, y0)
    hx = pad * 2 + gp.get_width()
    sheet.blit(hero, (hx, y0 + 20))
    label(sheet, "Hero (dark bg)", hx, y0)

    y1 = y0 + top_h
    label(sheet, "4-frame filmstrip (natural size)", pad, y1)
    fx = pad
    for i, f in enumerate(frames):
        sheet.blit(f, (fx, y1 + 22))
        SMALL_c = SMALL.render(f"f{i}", True, (200, 200, 200))
        sheet.blit(SMALL_c, (fx, y1 + 22 + f.get_height()))
        fx += f.get_width() + 14

    y2 = y1 + strip_h
    label(sheet, "40px NEAREST truth (build(2, 10.0), shown 1x and 4x)", pad, y2)
    sheet.blit(truth40, (pad, y2 + 24))
    sheet.blit(truth40x, (pad + 80, y2 + 24))

    out = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "..",
        "docs", "store_redesign", "animal", "thunderbird", "design_3", "round_2.png"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())


if __name__ == "__main__":
    main()
