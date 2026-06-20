"""Round-1 review sheet for the candidate FLYING TOASTER store skin.

Renders each of the 5 variants at hero 130px AND at the in-game truth-test
scale (40px, level + dive tilt) with a NEAREST-NEIGHBOR x3 magnification of
the 40px reads — the honest gameplay-pixel silhouette (smoothscale flatters
tiny detail that vanishes in motion). Each card shows the 40px reads on BOTH
a DAY sky and a NIGHT sky so the chrome/gold contrast is verified for the
full biome cycle. Headless (SDL dummy) so it runs in CI / on the build box.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

import importlib.util
_here = os.path.dirname(__file__)
spec = importlib.util.spec_from_file_location(
    "toaster_skins", os.path.join(_here, "toaster_skins.py"))
toaster_skins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(toaster_skins)

BUILDERS = toaster_skins.BUILDERS

ORDER = [
    ("v1 · After Dark Classic (chrome)", "chrome box + 2 gold toast + white feather wings"),
    ("v2 · Cream Retro Diner (face)",    "cream enamel + gold toast + googly eyes"),
    ("v3 · Copper Steampunk (1 toast)",  "copper box + one TALL gold slice + brass dial"),
    ("v4 · Mint Kawaii (face)",          "mint box + gold toast + big shiny eyes"),
    ("v5 · Noir Chrome (modern)",        "black/chrome + glowing slot + gold toast"),
]

# ── layout ───────────────────────────────────────────────────────────────────
COLS = 2
ROWS = (len(ORDER) + COLS - 1) // COLS
CARD_W, CARD_H = 520, 270
PAD = 18
HEADER_H = 66
HERO_PX = 130
GAME_PX = 40
MAG = 3

# Day + night sky swatches lifted from the game's biome feel.
DAY_TOP = (118, 196, 236)
DAY_BOT = (224, 232, 200)
NIGHT_TOP = (22, 26, 54)
NIGHT_BOT = (44, 32, 62)

SHEET_BG_TOP = (18, 20, 40)
SHEET_BG_BOT = (34, 26, 52)
CARD_BG = (16, 17, 34)
CARD_EDGE = (188, 150, 72)               # premium gold rim (ultra-premium skin)
TEXT = (238, 240, 250)
SUB = (154, 160, 192)

SHEET_W = PAD + COLS * (CARD_W + PAD)
SHEET_H = HEADER_H + PAD + ROWS * (CARD_H + PAD)

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(SHEET_BG_TOP[i] + (SHEET_BG_BOT[i] - SHEET_BG_TOP[i]) * t)
                for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

import random
rng = random.Random(11)
for _ in range(180):
    sx, sy = rng.randint(0, SHEET_W), rng.randint(0, SHEET_H)
    b = rng.randint(70, 190)
    pygame.draw.circle(sheet, (b, b, min(255, b + 30)), (sx, sy),
                       rng.choice([1, 1, 2]))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 30, bold=True)
F_SUB = pygame.font.SysFont("Arial", 15)
F_NAME = pygame.font.SysFont("Arial", 19, bold=True)
F_FEAT = pygame.font.SysFont("Arial", 13)
F_TAG = pygame.font.SysFont("Arial", 12, bold=True)

sheet.blit(F_TITLE.render("Skybit — FLYING TOASTER (skin_toaster) · Round 1",
                          True, CARD_EDGE), (PAD, 14))
sheet.blit(F_SUB.render(
    "HERO 130px · 40px NEAREST x3 (level / dive) on DAY and NIGHT skies — the honest gameplay read. "
    "Tell: chrome body + gold toast + little wings.",
    True, SUB), (PAD, 46))


def _crop(getter, frame_idx, tilt):
    s = getter(frame_idx, tilt)
    rect = s.get_bounding_rect()
    if rect.w == 0 or rect.h == 0:
        rect = s.get_rect()
    return s.subsurface(rect).copy()


def smooth(getter, frame_idx, tilt, target_px):
    crop = _crop(getter, frame_idx, tilt)
    longest = max(crop.get_width(), crop.get_height())
    f = target_px / longest
    return pygame.transform.smoothscale(
        crop, (max(1, int(crop.get_width() * f)),
               max(1, int(crop.get_height() * f))))


def nearest40(getter, frame_idx, tilt, mag):
    small = smooth(getter, frame_idx, tilt, GAME_PX)
    return pygame.transform.scale(
        small, (small.get_width() * mag, small.get_height() * mag))


def _sky(rect, top, bot):
    """A small vertical-gradient sky tile for the 40px reads."""
    s = pygame.Surface((rect.w, rect.h))
    for y in range(rect.h):
        t = y / max(1, rect.h)
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(s, col, (0, y), (rect.w, y))
    return s


for idx, (key, feat) in enumerate(ORDER):
    getter = BUILDERS[key]
    r, c = divmod(idx, COLS)
    cx = PAD + c * (CARD_W + PAD)
    cy = HEADER_H + PAD + r * (CARD_H + PAD)

    card = pygame.Rect(cx, cy, CARD_W, CARD_H)
    pygame.draw.rect(sheet, CARD_BG, card, border_radius=12)
    pygame.draw.rect(sheet, CARD_EDGE, card, 2, border_radius=12)

    sheet.blit(F_NAME.render(key, True, TEXT), (cx + 14, cy + 10))
    sheet.blit(F_FEAT.render("read: " + feat, True, SUB), (cx + 14, cy + 36))

    # Hero panel (left) on a night sky.
    hero_panel = pygame.Rect(cx + 12, cy + 58, 150, 198)
    sheet.blit(_sky(hero_panel, NIGHT_TOP, NIGHT_BOT), hero_panel)
    pygame.draw.rect(sheet, CARD_EDGE, hero_panel, 1, border_radius=10)
    hero = smooth(getter, 0, 0, HERO_PX)
    sheet.blit(hero, hero.get_rect(center=hero_panel.center))
    sheet.blit(F_TAG.render("130px", True, (220, 224, 240)),
               (hero_panel.x + 6, hero_panel.bottom - 18))

    # Right: a 2x2 grid — DAY row + NIGHT row, each level + dive (NEAREST x3).
    grid_x = cx + 174
    grid_y = cy + 58
    cell_w, cell_h = 168, 96
    rows = (("DAY", DAY_TOP, DAY_BOT), ("NIGHT", NIGHT_TOP, NIGHT_BOT))
    for ri, (label, top, bot) in enumerate(rows):
        cell = pygame.Rect(grid_x, grid_y + ri * (cell_h + 6),
                           cell_w * 2 + 6, cell_h)
        sheet.blit(_sky(cell, top, bot), cell)
        pygame.draw.rect(sheet, (90, 94, 120), cell, 1, border_radius=8)
        n_level = nearest40(getter, 2, 0, MAG)
        sheet.blit(n_level, n_level.get_rect(
            center=(cell.x + 84, cell.centery)))
        n_dive = nearest40(getter, 1, -32, MAG)
        sheet.blit(n_dive, n_dive.get_rect(
            center=(cell.x + 250, cell.centery)))
        txt_col = (40, 50, 60) if label == "DAY" else (220, 224, 240)
        sheet.blit(F_TAG.render(label + "  · 40px NEAREST x3 · level / dive",
                                True, txt_col), (cell.x + 6, cell.y + 4))

out_path = os.path.join(_here, "round_1.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
