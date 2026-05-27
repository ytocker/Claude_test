"""5 plated knight armours (round 2): polished plate + MORE articulated plates,
right-facing helm, K7 shield at B3. EXPLORATION ONLY.

Run:  SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m tools.render_knight_plates
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from tools import render_revive_designs as R

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                   "docs", "screenshots", "revive_designs")
os.makedirs(OUT, exist_ok=True)

SHIELD_B3 = (0.92, 0.58, 0.36, 0.46)

# Shared polished-plate steel palette (the chosen A1).
STEEL = {
    "ol": (28, 32, 44), "d": (96, 106, 128), "mid": (176, 188, 210), "hi": (248, 252, 255),
    "brass": (214, 180, 104), "brass_hi": (255, 236, 176),
    "body_mult": (172, 184, 208), "body_add": (10, 14, 22),
    "sheen_top": (250, 253, 255), "sheen_bot": (70, 80, 100),
    "texture": None, "filigree": False,
}


def _spec(**plates):
    s = dict(STEEL)
    s["plates"] = plates
    return s


# (label, ARMOR spec) — all polished steel, varying the plate articulation.
ARMORS = [
    ("P1  breastplate + 2 lames", _spec(lames=2, pauldron=False, keel=True, rivets=True, tassets=False)),
    ("P2  + pauldron, 3 lames", _spec(lames=3, pauldron=True, keel=True, rivets=True, tassets=False)),
    ("P3  full harness", _spec(lames=3, pauldron=True, keel=True, rivets=True, tassets=True)),
    ("P4  heavy layered", _spec(lames=4, pauldron=True, keel=True, rivets=True, tassets=True)),
    ("P5  fluted + plates", dict(_spec(lames=3, pauldron=True, keel=True, rivets=True, tassets=True), texture="fluted")),
]

OUT_NAME = "knight_plates.png"


def main():
    pose = R._Pose(frame_t=1.0, vy=-90, y=300)
    sc = 0.6
    pw, ph = int(R.W * sc), int(R.H * sc)
    gap, title_h, chip_h = 12, 44, 26
    f = pygame.font.SysFont("Arial", 22, bold=True)
    lf = pygame.font.SysFont("Arial", 15, bold=True)
    sheet = pygame.Surface((pw * 5 + gap * 6, ph + title_h + gap + chip_h + gap))
    sheet.fill((16, 18, 26))
    sheet.blit(f.render("Knight plate armour — 5 versions (polished steel, right-facing helm, K7/B3)", True, (255, 232, 168)), (gap + 2, 11))

    saved = R.ARMOR
    R._SHIELD_POS = SHIELD_B3
    try:
        for i, (label, spec) in enumerate(ARMORS):
            R.ARMOR = spec
            frame = R.render_one("", R.build_knight, pose)
            small = pygame.transform.smoothscale(frame, (pw, ph))
            x = gap + i * (pw + gap)
            sheet.blit(small, (x, title_h))
            chip = lf.render(label, True, (255, 255, 255))
            bg = pygame.Surface((chip.get_width() + 12, chip.get_height() + 6), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 185))
            sheet.blit(bg, (x + 4, title_h + ph + 4))
            sheet.blit(chip, (x + 10, title_h + ph + 7))
    finally:
        R.ARMOR = saved

    out = os.path.join(OUT, OUT_NAME)
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
