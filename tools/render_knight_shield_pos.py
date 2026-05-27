"""Compare 5 placements of the knight's K7 chest shield — on the most
visible RIGHT (front) side of the parrot. EXPLORATION ONLY.

Run:  SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m tools.render_knight_shield_pos
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

# Round 2 of placement: variant B pushed FAR right, partially on the body.
# (label, fx, fy, w-frac, h-frac)
OPTIONS = [
    ("B1  far right", 0.82, 0.60, 0.38, 0.48),
    ("B2  further right", 0.88, 0.60, 0.38, 0.48),
    ("B3  body edge", 0.92, 0.58, 0.36, 0.46),
    ("B4  far right, low + large", 0.85, 0.66, 0.44, 0.54),
    ("B5  far right, large", 0.90, 0.62, 0.44, 0.54),
]
OUT_NAME = "knight_shield_far_right.png"


def main():
    pose = R._Pose(frame_t=1.0, vy=-60, y=300)
    sc = 0.56
    pw, ph = int(R.W * sc), int(R.H * sc)
    gap, title_h = 10, 40
    f = pygame.font.SysFont("Arial", 22, bold=True)
    lf = pygame.font.SysFont("Arial", 14, bold=True)
    sheet = pygame.Surface((pw * 5 + gap * 6, ph + title_h + gap * 2 + 24))
    sheet.fill((16, 18, 26))
    sheet.blit(f.render("Knight K7 shield — far right, partially on the body (5 versions)", True, (255, 232, 168)), (gap + 2, 9))
    for i, (label, fx, fy, wf, hf) in enumerate(OPTIONS):
        R._SHIELD_POS = (fx, fy, wf, hf)
        frame = R.render_one("", R.build_knight, pose)
        small = pygame.transform.smoothscale(frame, (pw, ph))
        x = gap + i * (pw + gap)
        sheet.blit(small, (x, title_h))
        chip = lf.render(label, True, (255, 255, 255))
        bg = pygame.Surface((chip.get_width() + 10, chip.get_height() + 6), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 180))
        sheet.blit(bg, (x + 4, title_h + ph + 4))
        sheet.blit(chip, (x + 9, title_h + ph + 7))
    out = os.path.join(OUT, OUT_NAME)
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
