"""5 cohesive ARMOUR styles for the in-game knight (K7 shield at B3).
EXPLORATION ONLY — render tool → one comparison sheet on git.

Run:  SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m tools.render_knight_armor
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

# B3 placement, locked in by the user.
SHIELD_B3 = (0.92, 0.58, 0.36, 0.46)

# (label, ARMOR spec). Each is one homogeneous metal treatment over the whole
# body — recolour + sheen + a single texture pass + matching helm/sword tints.
ARMORS = [
    ("A1  polished plate", {
        "ol": (28, 32, 44), "d": (96, 106, 128), "mid": (176, 188, 210), "hi": (248, 252, 255),
        "brass": (214, 180, 104), "brass_hi": (255, 236, 176),
        "body_mult": (172, 184, 208), "body_add": (10, 14, 22),
        "sheen_top": (250, 253, 255), "sheen_bot": (70, 80, 100),
        "texture": None, "filigree": False,
    }),
    ("A2  blued steel", {
        "ol": (16, 20, 34), "d": (44, 54, 84), "mid": (96, 112, 156), "hi": (196, 212, 248),
        "brass": (208, 174, 98), "brass_hi": (255, 232, 168),
        "body_mult": (92, 108, 152), "body_add": (6, 10, 24),
        "sheen_top": (206, 220, 252), "sheen_bot": (24, 30, 56),
        "texture": None, "filigree": False,
    }),
    ("A3  scale mail", {
        "ol": (24, 28, 38), "d": (78, 86, 106), "mid": (150, 162, 186), "hi": (236, 244, 255),
        "brass": (208, 174, 98), "brass_hi": (255, 232, 168),
        "body_mult": (140, 150, 174), "body_add": (6, 9, 16),
        "sheen_top": (236, 242, 254), "sheen_bot": (44, 50, 66),
        "texture": "scale", "filigree": False,
    }),
    ("A4  fluted (Gothic)", {
        "ol": (26, 30, 42), "d": (84, 92, 114), "mid": (162, 174, 198), "hi": (242, 248, 255),
        "brass": (212, 178, 102), "brass_hi": (255, 234, 172),
        "body_mult": (156, 168, 192), "body_add": (8, 12, 20),
        "sheen_top": (244, 249, 255), "sheen_bot": (52, 60, 78),
        "texture": "fluted", "filigree": False,
    }),
    ("A5  gilded royal", {
        "ol": (40, 30, 12), "d": (118, 92, 40), "mid": (210, 174, 92), "hi": (255, 240, 184),
        "brass": (255, 226, 150), "brass_hi": (255, 248, 214),
        "body_mult": (200, 168, 92), "body_add": (24, 14, 0),
        "sheen_top": (255, 246, 206), "sheen_bot": (96, 70, 24),
        "texture": "fluted", "filigree": True,
    }),
]

OUT_NAME = "knight_armor.png"


def main():
    pose = R._Pose(frame_t=1.0, vy=-90, y=300)
    sc = 0.6
    pw, ph = int(R.W * sc), int(R.H * sc)
    gap, title_h, chip_h = 12, 44, 26
    f = pygame.font.SysFont("Arial", 22, bold=True)
    lf = pygame.font.SysFont("Arial", 15, bold=True)
    sheet = pygame.Surface((pw * 5 + gap * 6, ph + title_h + gap + chip_h + gap))
    sheet.fill((16, 18, 26))
    sheet.blit(f.render("Knight armour — 5 cohesive styles (K7 shield, B3)", True, (255, 232, 168)), (gap + 2, 11))

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
