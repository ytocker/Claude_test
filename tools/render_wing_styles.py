"""Compare the two wing/shoulder armour finishes for the knight — articulated
lames vs. a single smooth dome — both matching the breastplate/helm plate look.
EXPLORATION ONLY.

Run:  SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m tools.render_wing_styles
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

OPTIONS = [
    ("W1  articulated lames", "lames"),
    ("W2  single smooth dome", "dome"),
]
OUT_NAME = "knight_wing_styles.png"


def main():
    pose = R._Pose(frame_t=1.0, vy=-60, y=300)
    sc = 0.62
    pw, ph = int(R.W * sc), int(R.H * sc)
    gap, title_h = 10, 40
    zh = 300                                            # zoom-crop tile height
    f = pygame.font.SysFont("Arial", 22, bold=True)
    lf = pygame.font.SysFont("Arial", 15, bold=True)
    n = len(OPTIONS)
    sheet = pygame.Surface((pw * n + gap * (n + 1), title_h + ph + zh + gap * 3 + 24))
    sheet.fill((16, 18, 26))
    sheet.blit(f.render("Knight wing armour — match the plate look (2 styles)", True, (255, 232, 168)), (gap + 2, 9))
    saved = R._WING_STYLE
    try:
        for i, (label, style) in enumerate(OPTIONS):
            R._WING_STYLE = style
            frame = R.render_one("", R.build_knight, pose)
            x = gap + i * (pw + gap)
            sheet.blit(pygame.transform.smoothscale(frame, (pw, ph)), (x, title_h))
            # zoom crop of the torso + wing region
            crop = frame.subsurface(pygame.Rect(40, 120, 300, 230)).copy()
            big = pygame.transform.smoothscale(crop, (pw, zh))
            sheet.blit(big, (x, title_h + ph + gap))
            chip = lf.render(label, True, (255, 255, 255))
            bg = pygame.Surface((chip.get_width() + 12, chip.get_height() + 6), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 190))
            sheet.blit(bg, (x + 4, title_h + ph + 4))
            sheet.blit(chip, (x + 10, title_h + ph + 7))
    finally:
        R._WING_STYLE = saved
    out = os.path.join(OUT, OUT_NAME)
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
