"""Custom-drawn knight (genie-style full redraw): 5 armour finishes, a zoom, and
a gameplay GIF (Pip flaps twice). EXPLORATION ONLY.

Run:  SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m tools.render_knight_custom
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
GUL = (170, 46, 50); GOLD = (210, 168, 70)

# Five STRUCTURALLY-distinct knights — different helm + weapon + shield + cape,
# not just a recolour.
STEEL = dict(ol=(20, 24, 34), lo=(84, 96, 120), mid=(168, 180, 204), hi=(248, 252, 255),
             brass=(214, 180, 104), brass_hi=(255, 236, 176), fluted=False, surcoat=None, filigree=False)


def _d(**over):
    d = dict(STEEL); d.update(over); return d


FINISHES = [
    ("D1  Crusader · great helm · sword", _d(
        helm="greathelm", weapon="sword", shield="heater_k7", plume=(170, 44, 48))),
    ("D2  Paladin · winged crest · spear", _d(
        helm="winged", weapon="spear", shield="round", cape=(54, 96, 178),
        mid=(176, 188, 210), hi=(250, 253, 255), filigree=True, plume=(236, 236, 244))),
    ("D3  Jouster · frog-mouth · lance", _d(
        helm="frogmouth", weapon="lance", shield="bouche",
        ol=(12, 16, 30), lo=(46, 56, 88), mid=(96, 112, 156), hi=(200, 216, 250), plume=(210, 176, 70))),
    ("D4  Raider · houndskull · axe", _d(
        helm="houndskull", weapon="axe", shield="kite", cape=(56, 110, 70),
        plume=(54, 132, 78))),
    ("D5  Black Knight · horned · mace", _d(
        helm="horned", weapon="mace", shield="heater_saltire", cape=(28, 28, 36),
        ol=(8, 9, 14), lo=(40, 42, 54), mid=(86, 90, 104), hi=(190, 196, 212),
        brass=(232, 196, 110), brass_hi=(255, 236, 170), fluted=True, plume=(150, 40, 44))),
]


def _grid_sheet(title, out_name):
    pose = R._Pose(frame_t=1.0, vy=-90, y=300)
    sc = 0.6
    pw, ph = int(R.W * sc), int(R.H * sc)
    gap, title_h, chip_h = 12, 44, 26
    f = pygame.font.SysFont("Arial", 21, bold=True)
    lf = pygame.font.SysFont("Arial", 15, bold=True)
    sheet = pygame.Surface((pw * 5 + gap * 6, ph + title_h + gap + chip_h + gap))
    sheet.fill((16, 18, 26))
    sheet.blit(f.render(title, True, (255, 232, 168)), (gap + 2, 11))
    saved = R.ARMOR
    R._SHIELD_POS = SHIELD_B3
    try:
        for i, (label, spec) in enumerate(FINISHES):
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
    out = os.path.join(OUT, out_name)
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet.get_width()}x{sheet.get_height()})")


def _zoom(out_name):
    pose = R._Pose(frame_t=1.0, vy=-90, y=300)
    tile, gap, lh = 300, 8, 26
    f = pygame.font.SysFont("Arial", 14, bold=True)
    sheet = pygame.Surface((tile * 5 + gap * 6, tile + lh + gap * 2))
    sheet.fill((16, 18, 26))
    saved = R.ARMOR
    R._SHIELD_POS = SHIELD_B3
    try:
        for i, (label, spec) in enumerate(FINISHES):
            R.ARMOR = spec
            frame = R.render_one("", R.build_knight, pose)
            crop = frame.subsurface(pygame.Rect(55, 150, 250, 240)).copy()
            big = pygame.transform.smoothscale(crop, (tile, tile))
            x = gap + i * (tile + gap)
            sheet.blit(big, (x, gap))
            sheet.blit(f.render(label.split("·")[0].strip(), True, (255, 232, 168)), (x + 6, tile + gap + 4))
    finally:
        R.ARMOR = saved
    out = os.path.join(OUT, out_name)
    pygame.image.save(sheet, out)
    print(f"saved {out}")


def _gif(spec, out_name):
    saved = R.ARMOR
    R._SHIELD_POS = SHIELD_B3
    try:
        R.ARMOR = spec
        frames = [R.render_one("KNIGHT", R.build_knight, p) for p in R._poses()]
    finally:
        R.ARMOR = saved
    R._save_gif(frames, os.path.join(OUT, out_name), fps=22)
    print(f"saved {out_name}")


def main():
    _grid_sheet("Knight — 5 DISTINCT designs (helm · weapon · shield · cape all differ)", "knight_custom.png")
    _zoom("knight_custom_zoom.png")
    _gif(FINISHES[0][1], "knight_custom.gif")


if __name__ == "__main__":
    main()
