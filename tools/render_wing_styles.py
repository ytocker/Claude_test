"""Compare 5 placements of the knight's wing armour — pauldron, vambrace,
plated (full metal wing), lames (articulated fan), half-plate. Each is a
sculpted steel wing rooted at the shoulder that flaps with the animation.
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
    ("W1  pauldron cap", "pauldron"),
    ("W2  pauldron + vambrace", "vambrace"),
    ("W3  feather-plates", "plated"),
    ("W4  lame fan", "lames"),
    ("W5  half-plate", "half"),
]
FLAP_STYLE = "plated"   # which style to show across all 4 flap frames


def _chip(sheet, lf, label, x, y):
    chip = lf.render(label, True, (255, 255, 255))
    bg = pygame.Surface((chip.get_width() + 12, chip.get_height() + 6), pygame.SRCALPHA)
    bg.fill((0, 0, 0, 190))
    sheet.blit(bg, (x, y)); sheet.blit(chip, (x + 6, y + 3))


def main():
    pose = R._Pose(frame_t=1.0, vy=-60, y=300)
    n = len(OPTIONS)
    tile, gap, title_h, zh = 230, 8, 40, 300
    f = pygame.font.SysFont("Arial", 22, bold=True)
    lf = pygame.font.SysFont("Arial", 14, bold=True)
    sheet = pygame.Surface((tile * n + gap * (n + 1), title_h + zh + gap * 2 + 24))
    sheet.fill((16, 18, 26))
    sheet.blit(f.render("Knight wing armour — 5 placements (sculpted steel, flaps)", True, (255, 232, 168)), (gap + 2, 9))
    saved = R._WING_STYLE
    try:
        for i, (label, style) in enumerate(OPTIONS):
            R._WING_STYLE = style
            frame = R.render_one("", R.build_knight, pose)
            crop = frame.subsurface(pygame.Rect(30, 120, 300, 240)).copy()
            big = pygame.transform.smoothscale(crop, (tile, zh))
            x = gap + i * (tile + gap)
            sheet.blit(big, (x, title_h))
            _chip(sheet, lf, label, x + 4, title_h + zh + 4)
    finally:
        R._WING_STYLE = saved
    out = os.path.join(OUT, "knight_wing_styles.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet.get_width()}x{sheet.get_height()})")

    # 4-frame flap strip for one style to verify the articulation
    fstrip = pygame.Surface((tile * 4 + gap * 5, title_h + zh + gap * 2 + 24))
    fstrip.fill((16, 18, 26))
    fstrip.blit(f.render(f"Wing flap check — '{FLAP_STYLE}' across frames 0-3", True, (255, 232, 168)), (gap + 2, 9))
    saved = R._WING_STYLE
    try:
        R._WING_STYLE = FLAP_STYLE
        for fi in range(4):
            pose_f = R._Pose(frame_t=float(fi), vy=-60, y=300)
            frame = R.render_one("", R.build_knight, pose_f)
            crop = frame.subsurface(pygame.Rect(30, 120, 300, 240)).copy()
            big = pygame.transform.smoothscale(crop, (tile, zh))
            x = gap + fi * (tile + gap)
            fstrip.blit(big, (x, title_h))
            _chip(fstrip, lf, f"frame {fi}", x + 4, title_h + zh + 4)
    finally:
        R._WING_STYLE = saved
    out2 = os.path.join(OUT, "knight_wing_flap.png")
    pygame.image.save(fstrip, out2)
    print(f"saved {out2}  ({fstrip.get_width()}x{fstrip.get_height()})")


if __name__ == "__main__":
    main()
