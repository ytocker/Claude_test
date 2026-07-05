"""Round-2 review sheet for the FOLD-OVER FRONT diaper (design_5).

Hero product-shot + in-gameplay daytime panel + the make-or-break 40px NEAREST
truth-reads on BOTH day and navy night. At 40px you must read two chubby legs
poking out below a BANDED cream nappy carrying the hard fold-over seam.
"""
from __future__ import annotations
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

from tools.ninja_render import gameplay_panel, hero_panel
from tools.binky_diaper_candidates.design_5 import build as binky_build

FONT = pygame.font.SysFont("Arial", 16, bold=True)
SMALL = pygame.font.SysFont("Arial", 12)

DAY_SKY = (96, 178, 232)
NIGHT_SKY = (16, 18, 44)


def _label(surf, text, x, y, color=(240, 240, 240)):
    surf.blit(FONT.render(text, True, color), (x, y))


def _truth_read(sky, box, scale_px=40):
    frame = binky_build(2, 8.0)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy()
    sw, sh = frame.get_size()
    sc = scale_px / max(sw, sh)
    small = pygame.transform.scale(frame, (max(1, int(sw * sc)), max(1, int(sh * sc))))
    chip = pygame.Surface((box, box))
    chip.fill(sky)
    chip.blit(small, small.get_rect(center=(box // 2, box // 2)))
    return chip


def main():
    W, H = 920, 560
    sheet = pygame.Surface((W, H))
    sheet.fill((30, 28, 38))
    _label(sheet, "BINKY — FOLD-OVER FRONT diaper (design_5) — round 2", 20, 14,
           (255, 230, 180))

    hero = hero_panel(binky_build, 300, frame_idx=2, tilt=0.0, bg=(40, 38, 54))
    sheet.blit(hero, (20, 48))
    _label(sheet, "HERO", 20, 352)

    gp = gameplay_panel(binky_build, 250, 350)
    sheet.blit(gp, (340, 48))
    _label(sheet, "GAMEPLAY (day)", 340, 352)

    chip_box = 60
    mag = 4
    xs = 680
    day_chip = _truth_read(DAY_SKY, chip_box)
    day_big = pygame.transform.scale(day_chip, (chip_box * mag, chip_box * mag))
    sheet.blit(day_big, (xs, 48))
    _label(sheet, "40px DAY", xs, 48 + chip_box * mag + 4)
    sheet.blit(pygame.transform.scale(day_chip, (chip_box, chip_box)),
               (xs + chip_box * mag - chip_box, 48))

    ny = 48 + chip_box * mag + 34
    night_chip = _truth_read(NIGHT_SKY, chip_box)
    night_big = pygame.transform.scale(night_chip, (chip_box * mag, chip_box * mag))
    sheet.blit(night_big, (xs, ny))
    _label(sheet, "40px NAVY", xs, ny + chip_box * mag + 4)
    sheet.blit(pygame.transform.scale(night_chip, (chip_box, chip_box)),
               (xs + chip_box * mag - chip_box, ny))

    sheet.blit(SMALL.render(
        "Banded nappy: rear wrap + underside band + hard fold-over seam at y57; legs poke out below y61.",
        True, (200, 200, 210)), (20, H - 26))

    out = ("/home/user/skybit/docs/store_redesign/parrot/baby_parrot/"
           "diaper_redo/design_5/round_2.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out)


if __name__ == "__main__":
    main()
