"""Verification figure: the street-tree design removed from the sidewalk.

Dev-only, scratch — NOT part of the game. `_street_tree()` was deleted from
`game/foreground_promenade.py` (its style didn't match the rest of the
game), so this reconstructs its exact drawing code from git history
(commit cb68ca07, the last commit before the removal) purely to render a
reference figure of what was taken out. game/ is not touched.

    SDL_VIDEODRIVER=dummy PYTHONPATH=. python tools/_removed_street_tree.py
"""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import GROUND_Y                              # noqa: E402
from game import biome as _biome                              # noqa: E402
from game.foreground_promenade import _retint_person, _mix32   # noqa: E402
from game.foreground_props import _shade, _nightf              # noqa: E402
from tools._family_showcase import _font                       # noqa: E402


def _street_tree(surf, sx, pal, salt, slim=False):
    """Verbatim copy of the removed game/foreground_promenade.py function
    (commit cb68ca07) — reconstructed here only to render the reference
    figure, not reintroduced into the game."""
    night = _nightf(pal)
    h = _mix32(salt * 0x9E3779B1)
    form = 1 if slim else h % 3
    top = 506 + (h >> 4) % 13
    trunk = _retint_person((96, 68, 44), night)
    fol_d = _retint_person((44, 92, 54), night)
    fol_m = _retint_person((66, 122, 64), night)
    fol_l = _retint_person((96, 150, 78), night)
    by = GROUND_Y - 1
    pygame.draw.line(surf, trunk, (sx, by), (sx, top + 24), 3)
    pygame.draw.line(surf, _shade(trunk, -18), (sx + 1, by), (sx + 1, top + 28), 1)
    if form == 0:            # round crown
        pygame.draw.circle(surf, fol_d, (sx, top + 15), 15)
        pygame.draw.circle(surf, fol_m, (sx - 2, top + 12), 12)
        pygame.draw.circle(surf, fol_l, (sx - 5, top + 9), 7)
    elif form == 1:          # tiered conifer
        for i, (tw, yy) in enumerate(((28, 30), (21, 19), (14, 9))):
            c = (fol_d, fol_m, fol_l)[i]
            pygame.draw.polygon(surf, c, [(sx - tw // 2, top + yy),
                                          (sx + tw // 2, top + yy),
                                          (sx, top + yy - 13)])
    else:                    # twin-lobe scholar tree
        pygame.draw.ellipse(surf, fol_d, (sx - 16, top + 7, 20, 14))
        pygame.draw.ellipse(surf, fol_m, (sx - 4, top + 1, 20, 15))
        pygame.draw.ellipse(surf, fol_l, (sx - 8, top + 5, 12, 9))
        pygame.draw.line(surf, trunk, (sx, top + 22), (sx + 6, top + 9), 2)


# form 0 needs a salt whose h%3==0, form 2 needs h%3==2; form 1 is always
# reachable via slim=True regardless of salt. Found by brute-force search
# over small salts so each cell shows its OWN form, not a repeat.
def _salt_for_form(target):
    for salt in range(64):
        h = _mix32(salt * 0x9E3779B1)
        if h % 3 == target:
            return salt
    raise RuntimeError("no salt found")


CELLS = [
    ("round crown", _salt_for_form(0), False),
    ("tiered conifer (wide gap)", _salt_for_form(1), False),
    ("twin-lobe scholar tree", _salt_for_form(2), False),
    ("tiered conifer (slim, tight gap)", 0, True),
]


def main():
    out_dir = "docs/sidewalk_overhaul/removed"
    os.makedirs(out_dir, exist_ok=True)
    pal_day = _biome.palette_for_phase(0.30)
    pal_night = _biome.palette_for_phase(0.80)

    # _street_tree draws in absolute GROUND_Y-relative coordinates (canopy top
    # y ~486-518, trunk foot at GROUND_Y-1=594), so render onto a full-height
    # scratch canvas first, then crop the tree's own band into each panel.
    band_top, band_h = 480, GROUND_Y - 480 + 4
    cell_w, cell_h = 130, band_h + 30
    cols = len(CELLS)
    sheet = pygame.Surface((cols * cell_w, cell_h * 2 + 50))
    sheet.fill((24, 22, 30))
    f = _font(15, bold=True)
    lf = _font(11)
    sheet.blit(f.render("REMOVED — street-tree design (deleted from game/foreground_promenade.py)",
                        True, (230, 226, 214)), (8, 8))

    for row, (pal, row_label) in enumerate(((pal_day, "day"), (pal_night, "night"))):
        bg = (200, 210, 200) if row == 0 else (26, 30, 44)
        for col, (label, salt, slim) in enumerate(CELLS):
            cx = col * cell_w
            cy = 34 + row * cell_h
            scratch = pygame.Surface((cell_w - 4, GROUND_Y + 4))
            scratch.fill(bg)
            sx = (cell_w - 4) // 2
            _street_tree(scratch, sx, pal, salt, slim=slim)
            crop = scratch.subsurface(pygame.Rect(0, band_top, cell_w - 4, band_h))
            sheet.blit(crop, (cx + 2, cy))
            pygame.draw.rect(sheet, (80, 80, 96), (cx + 2, cy, cell_w - 4, band_h), 1)
            for i, line in enumerate(label.split(" (")):
                text = line.rstrip(")")
                sheet.blit(lf.render(text, True, (200, 202, 210)),
                          (cx + 4, cy + band_h + 2 + i * 12))
        sheet.blit(lf.render(row_label, True, (170, 174, 190)), (4, 34 + row * cell_h + 2))

    big = pygame.transform.scale(sheet, (sheet.get_width() * 2, sheet.get_height() * 2))
    path = os.path.join(out_dir, "street_tree_removed.png")
    pygame.image.save(big, path)
    print("saved", path, big.get_size())


if __name__ == "__main__":
    main()
