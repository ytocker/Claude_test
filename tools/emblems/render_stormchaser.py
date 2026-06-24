"""
Review harness for the STORMCHASER bespoke glyphs.

Renders each emblem as a hero (220px) + a row-size (44px) chip on a dark sheet,
labelled, grouped by the three tier pairs and the standalones, so the read +
crispness can be judged at the size the achievement screen actually uses.

Run:  SDL_VIDEODRIVER=dummy python tools/emblems/render_stormchaser.py
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pygame

pygame.init()
pygame.font.init()

import game.achievement_icons as ai
from tools.emblems.stormchaser import GLYPHS

# Author-time override: graft the bespoke glyphs onto the live table so
# get_badge stamps them through the real medallion construction.
ai._GLYPHS.update(GLYPHS)

# Grouped so the sheet reads as: tier pair, tier pair, tier pair, then standalones.
GROUPS = [
    ("Needle & Thread  (bead count 1 -> 3)",
     [("near_miss_5", "near_miss_5  -  Close Shave"),
      ("near_miss_15", "near_miss_15  -  Threadneedle")]),
    ("Ceiling Bonk  (arrow -> helmet, bar dents)",
     [("headbanger", "headbanger  -  Headbanger"),
      ("hard_head", "hard_head  -  Hard Head")]),
    ("Macaw Wing  (feather -> riveted iron)",
     [("flap_life", "flap_life  -  Tireless Wings"),
      ("iron_wings", "iron_wings  -  Iron Wings")]),
    ("Standalones  (distinct silhouettes)",
     [("marathon", "marathon  -  Long Haul"),
      ("storm_rider", "storm_rider  -  Storm Rider"),
      ("snowbird", "snowbird  -  Snowbird")]),
]

HERO = 220
CHIP = 44
BG = (22, 24, 32)
PANEL = (30, 33, 44)
TXT = (220, 224, 234)
HDR = (250, 214, 130)

pad = 26
cell_w = HERO + 40
cell_h = HERO + CHIP + 78
cols = 2
font = pygame.font.SysFont(None, 24, bold=True)
hfont = pygame.font.SysFont(None, 30, bold=True)
sfont = pygame.font.SysFont(None, 20)

# Compute layout height.
total_rows = 0
for _, items in GROUPS:
    total_rows += -(-len(items) // cols)  # ceil
sheet_w = pad * 2 + cols * cell_w
sheet_h = pad
for title, items in GROUPS:
    rows = -(-len(items) // cols)
    sheet_h += 44 + rows * cell_h + 18
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title_top = font.render("STORMCHASER emblems  -  hero 220px + row 44px  (tone=gold)",
                        True, HDR)
# (header drawn per group instead; keep a slim top margin)

y = pad
for title, items in GROUPS:
    htxt = hfont.render(title, True, HDR)
    sheet.blit(htxt, (pad, y))
    pygame.draw.line(sheet, (70, 76, 96), (pad, y + 34),
                     (sheet_w - pad, y + 34), 2)
    y += 44
    for idx, (key, label) in enumerate(items):
        col = idx % cols
        row = idx // cols
        cx0 = pad + col * cell_w
        cy0 = y + row * cell_h
        pygame.draw.rect(sheet, PANEL, (cx0, cy0, cell_w - 14, cell_h - 14),
                         border_radius=12)
        hero = ai.get_badge(key, HERO, True, False, "gold")
        sheet.blit(hero, (cx0 + (cell_w - 14 - HERO) // 2, cy0 + 12))
        chip = ai.get_badge(key, CHIP, True, False, "gold")
        chip_y = cy0 + 12 + HERO + 12
        sheet.blit(chip, (cx0 + 24, chip_y))
        # dormant chip beside the live one for contrast
        dchip = ai.get_badge(key, CHIP, False, False, "gold")
        sheet.blit(dchip, (cx0 + 24 + CHIP + 10, chip_y))
        lbl = font.render(label, True, TXT)
        sheet.blit(lbl, (cx0 + 24 + 2 * CHIP + 24, chip_y + 4))
        sub = sfont.render("44px live / dormant", True, (150, 156, 172))
        sheet.blit(sub, (cx0 + 24 + 2 * CHIP + 24, chip_y + 26))
    rows = -(-len(items) // cols)
    y += rows * cell_h + 18

out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                       "..", "..", "docs", "emblems", "stormchaser"))
os.makedirs(out_dir, exist_ok=True)
out = os.path.join(out_dir, "sheet.png")
pygame.image.save(sheet, out)
print(out)
