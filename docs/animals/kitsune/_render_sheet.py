"""Round-1 review sheet for the candidate KITSUNE skins.

Renders each of the 5 variants at hero 130px AND at the in-game truth-test
scale (40px, level + dive tilt), plus a NEAREST-NEIGHBOR x3 magnification of
those 40px reads so the true gameplay-pixel silhouette is honest (smoothscale
flatters tiny detail that vanishes in motion). On a NIGHT backdrop. Headless
(SDL dummy) so it runs in CI / on the build box.
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
    "kitsune_skins", os.path.join(_here, "kitsune_skins.py"))
kitsune_skins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kitsune_skins)

BUILDERS = kitsune_skins.BUILDERS

ORDER = [
    ("v1 TENKO ASCENDANT", "white celestial · 9 violet-tip tails · gold aura"),
    ("v2 KYUBI EMBER",     "russet · gold-fire tails · fierce pounce"),
    ("v3 CURLED ORACLE",   "seated regal · white-fire peacock fan · moon blaze"),
    ("v4 VIOLET WISP",     "implied fan + ghost wisps · violet-dominant"),
    ("v5 PRISM TENKO",     "gold→violet gradient fan · diamond blaze"),
]

COLS = 2
ROWS = (len(ORDER) + COLS - 1) // COLS
CARD_W, CARD_H = 380, 250
PAD = 16
HEADER_H = 64
HERO_PX = 130
GAME_PX = 40
MAG = 3

NIGHT_TOP = (18, 20, 44)
NIGHT_BOT = (42, 28, 58)
CARD_BG = (14, 15, 32)
CARD_EDGE = (190, 150, 70)               # gold rim — every kitsune is legendary
TEXT = (236, 238, 250)
SUB = (158, 150, 190)
HERO_PANEL = (24, 24, 50)
GAME_PANEL = (10, 11, 26)

SHEET_W = PAD + COLS * (CARD_W + PAD)
SHEET_H = HEADER_H + PAD + ROWS * (CARD_H + PAD)

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(NIGHT_TOP[i] + (NIGHT_BOT[i] - NIGHT_TOP[i]) * t) for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

import random
rng = random.Random(9)
for _ in range(180):
    sx, sy = rng.randint(0, SHEET_W), rng.randint(0, SHEET_H)
    b = rng.randint(80, 210)
    pygame.draw.circle(sheet, (b, b, min(255, b + 30)), (sx, sy), rng.choice([1, 1, 2]))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 30, bold=True)
F_SUB = pygame.font.SysFont("Arial", 15)
F_NAME = pygame.font.SysFont("Arial", 19, bold=True)
F_FEAT = pygame.font.SysFont("Arial", 13)
F_TAG = pygame.font.SysFont("Arial", 12, bold=True)

sheet.blit(F_TITLE.render("Skybit — KITSUNE (legendary showpiece) · Round 1", True, TEXT), (PAD, 14))
sheet.blit(F_SUB.render(
    "HERO 130px · 40px level & dive (smooth) · NEAREST x3 magnified 40px (the honest gameplay read). Tail-fan = the 'wings'.",
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
        crop, (max(1, int(crop.get_width() * f)), max(1, int(crop.get_height() * f))))


def nearest40(getter, frame_idx, tilt, mag):
    small = smooth(getter, frame_idx, tilt, GAME_PX)
    return pygame.transform.scale(
        small, (small.get_width() * mag, small.get_height() * mag))


for idx, (key, feat) in enumerate(ORDER):
    getter = BUILDERS[key]
    r, c = divmod(idx, COLS)
    cx = PAD + c * (CARD_W + PAD)
    cy = HEADER_H + PAD + r * (CARD_H + PAD)

    card = pygame.Rect(cx, cy, CARD_W, CARD_H)
    pygame.draw.rect(sheet, CARD_BG, card, border_radius=12)
    pygame.draw.rect(sheet, CARD_EDGE, card, 3, border_radius=12)

    sheet.blit(F_NAME.render(key, True, CARD_EDGE), (cx + 14, cy + 10))
    sheet.blit(F_FEAT.render(feat, True, SUB), (cx + 14, cy + 34))

    # Hero panel (left).
    hero_panel = pygame.Rect(cx + 12, cy + 56, 158, 178)
    pygame.draw.rect(sheet, HERO_PANEL, hero_panel, border_radius=10)
    hero = smooth(getter, 0, 0, HERO_PX)
    sheet.blit(hero, hero.get_rect(center=hero_panel.center))
    sheet.blit(F_TAG.render("130px  (down-pose, full fan)", True, SUB),
               (hero_panel.x + 6, hero_panel.bottom - 18))

    # Game panel (right).
    game_panel = pygame.Rect(cx + 178, cy + 56, 190, 178)
    pygame.draw.rect(sheet, GAME_PANEL, game_panel, border_radius=10)

    g_level = smooth(getter, 2, 0, GAME_PX)
    sheet.blit(g_level, g_level.get_rect(center=(game_panel.x + 48, game_panel.y + 30)))
    g_dive = smooth(getter, 1, -32, GAME_PX)
    sheet.blit(g_dive, g_dive.get_rect(center=(game_panel.x + 120, game_panel.y + 30)))
    sheet.blit(F_TAG.render("40px smooth", True, SUB),
               (game_panel.x + 8, game_panel.y + 54))

    n_level = nearest40(getter, 2, 0, MAG)
    sheet.blit(n_level, n_level.get_rect(center=(game_panel.x + 54, game_panel.y + 122)))
    n_dive = nearest40(getter, 1, -32, MAG)
    sheet.blit(n_dive, n_dive.get_rect(center=(game_panel.x + 136, game_panel.y + 122)))
    sheet.blit(F_TAG.render("40px NEAREST x3  (level / dive)", True, (210, 200, 150)),
               (game_panel.x + 8, game_panel.bottom - 18))

out_path = os.path.join(_here, "round_1.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
