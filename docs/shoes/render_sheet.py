"""Headless renderer for the SHOES exploration sheet (round 1).

Lays out, per shoe: the BIG product-shot icon, a 48px store thumbnail, and
Pip wearing the pair at 40px (level) + ~130px hero. Lead column is the
product shot — the truth test for "is this recognisably that model?".
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

# Make `from game import ...` resolve when run from anywhere.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

pygame.init()
pygame.display.set_mode((1, 1))

# docs/shoes is not a package; load the candidate module directly.
import importlib.util
_spec = importlib.util.spec_from_file_location(
    "shoe_skins", os.path.join(os.path.dirname(__file__), "shoe_skins.py"))
shoe_skins = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(shoe_skins)

ICONS = shoe_skins.ICONS
BUILDERS = shoe_skins.BUILDERS
NAMES = shoe_skins.NAMES
ORDER = list(shoe_skins._CORES.keys())

BG = (38, 44, 64)            # the navy store card the skins live on
PANEL = (28, 33, 50)
GRID = (54, 62, 88)
TEXT = (236, 238, 245)
SUB = (150, 160, 185)
ACCENT = (250, 200, 90)

pygame.font.init()
F_TITLE = pygame.font.SysFont("arial", 26, bold=True)
F_HEAD = pygame.font.SysFont("arial", 18, bold=True)
F_LABEL = pygame.font.SysFont("arial", 13)
F_SMALL = pygame.font.SysFont("arial", 11)


def scaled(surf, target_w):
    w, h = surf.get_size()
    s = target_w / w
    return pygame.transform.smoothscale(surf, (int(w * s), int(h * s)))


def pip_wearing(sid, px):
    """Render Pip wearing the shoes at a given pixel height, level flight."""
    frame = BUILDERS[sid](2, 0)  # frame 2 = level wing, tilt 0
    return scaled(frame, int(px * frame.get_width() / frame.get_height()))


# Row layout.
ROW_H = 168
COL_PROD = 30          # big product shot
COL_THUMB = 300        # 48px thumbnail (on a card)
COL_40 = 430           # Pip 40px
COL_130 = 560          # Pip 130px hero
SHEET_W = 760
HEADER_H = 96
SHEET_H = HEADER_H + ROW_H * len(ORDER) + 20

sheet = pygame.Surface((SHEET_W, SHEET_H))
sheet.fill(BG)

# Header.
sheet.blit(F_TITLE.render("SHOES — Pip's Sneaker Store  ·  Round 1",
                          True, TEXT), (24, 22))
sheet.blit(F_LABEL.render("Stylized procedural homages — silhouette + colorway, "
                          "no exact marks.  Toe points right.",
                          True, SUB), (24, 56))
# Column captions.
caps = [("PRODUCT SHOT (~120px)", COL_PROD + 10),
        ("48px THUMB", COL_THUMB - 6),
        ("PIP 40px", COL_40 - 6),
        ("PIP 130px HERO", COL_130 - 24)]
for cap, cx in caps:
    sheet.blit(F_SMALL.render(cap, True, ACCENT), (cx, HEADER_H - 18))

for i, sid in enumerate(ORDER):
    ry = HEADER_H + i * ROW_H
    # Row backdrop alternation.
    if i % 2 == 0:
        pygame.draw.rect(sheet, PANEL, (12, ry, SHEET_W - 24, ROW_H - 8),
                         border_radius=10)
    pygame.draw.line(sheet, GRID, (12, ry + ROW_H - 4),
                     (SHEET_W - 12, ry + ROW_H - 4), 1)

    cy = ry + 14
    # Name + id.
    sheet.blit(F_HEAD.render(NAMES[sid], True, TEXT), (COL_PROD, cy))
    sheet.blit(F_SMALL.render(sid, True, SUB), (COL_PROD, cy + 22))

    # 1) Big product shot.
    icon = ICONS[sid]
    big = scaled(icon, 240)
    sheet.blit(big, (COL_PROD, cy + 38))

    # 2) 48px thumbnail on a store-style card.
    card = pygame.Rect(COL_THUMB - 8, cy + 44, 64, 64)
    pygame.draw.rect(sheet, (22, 26, 42), card, border_radius=8)
    pygame.draw.rect(sheet, GRID, card, 1, border_radius=8)
    thumb = scaled(icon, 56)
    sheet.blit(thumb, thumb.get_rect(center=card.center))

    # 3) Pip 40px (level).
    p40 = pip_wearing(sid, 40)
    base40 = ry + ROW_H - 28
    sheet.blit(p40, p40.get_rect(midbottom=(COL_40 + 30, base40)).topleft)
    sheet.blit(F_SMALL.render("level", True, SUB), (COL_40 + 14, base40 + 2))

    # 4) Pip 130px hero.
    p130 = pip_wearing(sid, 130)
    sheet.blit(p130, p130.get_rect(midbottom=(COL_130 + 70, ry + ROW_H - 14))
               .topleft)

out = os.path.join(os.path.dirname(__file__), "round_1.png")
pygame.image.save(sheet, out)
print("wrote", out, sheet.get_size())
