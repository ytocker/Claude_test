"""Review-sheet harness for the eight SKATER center glyphs.

Registers the bespoke glyphs into the production badge builder
(`ai._GLYPHS.update(GLYPHS)`) and renders each at HERO size (220px) and at the
true 44px row size, labelled, on a dark plate — so the art-director can judge
both the engraved detail and the row-size legibility from one image.

Run:  SDL_VIDEODRIVER=dummy python tools/emblems/render_skater.py
Out:  docs/emblems/skater/sheet.png

Exploration only — game/ is untouched; this only mutates the in-process glyph
table of an imported module.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

import game.achievement_icons as ai           # noqa: E402
from tools.emblems.skater import GLYPHS       # noqa: E402

ai._GLYPHS.update(GLYPHS)

# Ordered by family so the sheet reads the three escalation ladders + the
# standalone combo top-to-bottom.
ENTRIES = [
    ("board_meeting", "Board Meeting", "board-catch L0 — grounded board + spark"),
    ("sponsored",     "Sponsored",     "board-catch L2 — sponsor star sticker"),
    ("going_pro",     "Going Pro",     "board-catch L4 — airborne ollie + crown"),
    ("trickster",     "Trickster",     "rotation L1 — half-spin kickflip arc"),
    ("trick_legend",  "Trick Legend",  "rotation L4 — full 360 ring + crown"),
    ("grinder",       "Grinder",       "rail L1 — board on rail + grind-sparks"),
    ("rail_baron",    "Rail Baron",    "rail L4 — mine-cart on rail + crown"),
    ("full_combo",    "Full Combo",    "four dots in a chevron + combo-arc"),
]

HERO = 220
ROW = 44
BG = (26, 28, 36)


def _font(sz, bold=True):
    return pygame.font.SysFont("dejavusans", sz, bold=bold)


def main():
    cols = 4
    rows = 2
    cell_w = HERO + 60
    cell_h = HERO + 110
    margin = 36
    sheet_w = margin * 2 + cols * cell_w
    sheet_h = 96 + rows * cell_h + 40

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(BG)

    f_title = _font(34)
    f_lbl = _font(22)
    f_small = _font(16, bold=False)
    f_tag = _font(14, bold=False)

    sheet.blit(f_title.render("Skybit — SKATER emblems (gold)  hero + 44px row size",
                              True, (244, 226, 170)), (margin, 28))

    for i, (key, label, tag) in enumerate(ENTRIES):
        col = i % cols
        row = i // cols
        x = margin + col * cell_w
        y = 96 + row * cell_h

        hero = ai.get_badge(key, HERO, True, False, "gold")
        sheet.blit(hero, (x, y))

        # true-44px chip set against the same dark plate, to the right & below
        chip = ai.get_badge(key, ROW, True, False, "gold")
        cx_chip = x + HERO - ROW - 6
        cy_chip = y + 6
        pygame.draw.rect(sheet, (14, 15, 22),
                         (cx_chip - 6, cy_chip - 6, ROW + 12, ROW + 12),
                         border_radius=8)
        sheet.blit(chip, (cx_chip, cy_chip))
        sheet.blit(f_tag.render("44px", True, (150, 155, 168)),
                   (cx_chip - 2, cy_chip + ROW + 8))

        sheet.blit(f_lbl.render(label, True, (240, 240, 248)), (x + 2, y + HERO + 8))
        sheet.blit(f_small.render(tag, True, (170, 174, 188)), (x + 2, y + HERO + 36))

    # A tight 44px strip along the bottom so the four-silhouette-families read
    # is judged side-by-side at the real footprint.
    sy = 96 + rows * cell_h + 4
    sheet.blit(f_small.render("row strip @44px:", True, (180, 184, 196)), (margin, sy - 2))
    sx = margin + 150
    for key, _, _ in ENTRIES:
        sheet.blit(ai.get_badge(key, ROW, True, False, "gold"), (sx, sy - 8))
        sx += ROW + 14

    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..",
                                           "docs", "emblems", "skater"))
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "sheet.png")
    pygame.image.save(sheet, out)
    print("wrote", out, sheet.get_size())


if __name__ == "__main__":
    main()
