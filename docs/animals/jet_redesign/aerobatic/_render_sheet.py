"""Round-1 review sheet for the AEROBATIC TEAM JET redesign candidates.

Renders each of the 5 variants at hero 130px AND at the in-game truth-test
scale (40px, level + dive) on BOTH a day and a night card, plus a NEAREST-
NEIGHBOR x3 magnification of the 40px reads so the true gameplay-pixel
silhouette is honest (smoothscale flatters tiny detail that vanishes in
motion). Headless (SDL dummy) so it runs in CI / on the build box.

The skin builds draw a FLAT, NOSE-RIGHT, UPRIGHT planform (the game applies
the inverted nose-up secret-skin spin later). To preview the real in-game
attitude, this sheet applies the production 205° spin to each frame before
scaling — mirroring game/animal_jet_fighter.build_jet_fighter's final rotate.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

import importlib.util
_here = os.path.dirname(__file__)
spec = importlib.util.spec_from_file_location(
    "aerobatic_skins", os.path.join(_here, "aerobatic_skins.py"))
aerobatic_skins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(aerobatic_skins)

BUILDERS = aerobatic_skins.BUILDERS

# Secret-skin attitude: the flat planform is spun to the cocky inverted
# nose-high pose the game uses, so the preview matches gameplay.
JET_SPIN = 205

ORDER = [
    ("v1_blue_angel",  "v1 · BLUE ANGEL", "navy gloss + GOLD nose/spine spear"),
    ("v2_thunderbird", "v2 · THUNDERBIRD", "white + red→blue ARROW down fuselage"),
    ("v3_red_arrow",   "v3 · RED ARROW", "all-red + white diamond + smoke puff"),
    ("v4_sunburst",    "v4 · SUNBURST RACER", "hard white/magenta split + bolt (swept)"),
    ("v5_gold_jacket", "v5 · GOLD JACKET", "black gloss + GOLD chevron wrap"),
]

# ── layout ───────────────────────────────────────────────────────────────────
COLS = 1
CARD_W, CARD_H = 760, 200
PAD = 16
HEADER_H = 64
HERO_PX = 130
GAME_PX = 40
MAG = 3

CARD_BG = (16, 17, 34)
CARD_EDGE = (190, 150, 70)               # gold rim (priciest skin)
TEXT = (236, 238, 250)
SUB = (150, 156, 190)
HERO_DAY = (150, 190, 232)               # bright day-sky panel
HERO_NIGHT = (22, 24, 50)                # night-sky panel
GAME_PANEL = (12, 13, 28)

SHEET_W = PAD + COLS * (CARD_W + PAD)
SHEET_H = HEADER_H + PAD + len(ORDER) * (CARD_H + PAD)

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int((26, 28, 56)[i] + ((44, 34, 64)[i] - (26, 28, 56)[i]) * t) for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

import random
rng = random.Random(11)
for _ in range(220):
    sx, sy = rng.randint(0, SHEET_W), rng.randint(0, SHEET_H)
    b = rng.randint(80, 200)
    pygame.draw.circle(sheet, (b, b, min(255, b + 30)), (sx, sy), rng.choice([1, 1, 2]))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 30, bold=True)
F_SUB = pygame.font.SysFont("Arial", 15)
F_NAME = pygame.font.SysFont("Arial", 19, bold=True)
F_FEAT = pygame.font.SysFont("Arial", 13)
F_TAG = pygame.font.SysFont("Arial", 12, bold=True)

sheet.blit(F_TITLE.render("Skybit — JET redesign · AEROBATIC TEAM JET · Round 1", True, TEXT), (PAD, 12))
sheet.blit(F_SUB.render(
    "HERO 130px (day & night) · 40px level/dive NEAREST x3 (honest gameplay read, day & night). Bold LIVERY = the tell.",
    True, SUB), (PAD, 42))


def _spun(getter, frame_idx, tilt):
    """Apply the in-game secret-skin spin so the preview matches gameplay."""
    s = getter(frame_idx, tilt)
    s = pygame.transform.rotate(s, JET_SPIN)
    rect = s.get_bounding_rect()
    if rect.w == 0 or rect.h == 0:
        rect = s.get_rect()
    return s.subsurface(rect).copy()


def smooth(getter, frame_idx, tilt, target_px):
    crop = _spun(getter, frame_idx, tilt)
    longest = max(crop.get_width(), crop.get_height())
    f = target_px / longest
    return pygame.transform.smoothscale(
        crop, (max(1, int(crop.get_width() * f)), max(1, int(crop.get_height() * f))))


def nearest40(getter, frame_idx, tilt, mag):
    small = smooth(getter, frame_idx, tilt, GAME_PX)
    return pygame.transform.scale(
        small, (small.get_width() * mag, small.get_height() * mag))


def _hero_panel(rect, bg, getter, label):
    pygame.draw.rect(sheet, bg, rect, border_radius=10)
    hero = smooth(getter, 0, 0, HERO_PX)
    sheet.blit(hero, hero.get_rect(center=rect.center))
    sheet.blit(F_TAG.render(label, True, (40, 40, 40) if bg[0] > 100 else SUB),
               (rect.x + 6, rect.bottom - 18))


def _game_panel(rect, getter, daynight):
    # Day reads on a bright sky, night on a dark sky — honest 40px contrast.
    bg = (118, 162, 212) if daynight == "DAY" else GAME_PANEL
    pygame.draw.rect(sheet, bg, rect, border_radius=10)
    g_level = smooth(getter, 2, 0, GAME_PX)
    sheet.blit(g_level, g_level.get_rect(center=(rect.x + 40, rect.y + 30)))
    g_dive = smooth(getter, 1, -32, GAME_PX)
    sheet.blit(g_dive, g_dive.get_rect(center=(rect.x + 98, rect.y + 30)))
    tag_col = (30, 30, 40) if daynight == "DAY" else SUB
    sheet.blit(F_TAG.render(daynight + " 40px", True, tag_col), (rect.x + 8, rect.y + 52))
    n_level = nearest40(getter, 2, 0, MAG)
    sheet.blit(n_level, n_level.get_rect(center=(rect.x + 46, rect.y + 116)))
    n_dive = nearest40(getter, 1, -32, MAG)
    sheet.blit(n_dive, n_dive.get_rect(center=(rect.x + 116, rect.y + 116)))
    sheet.blit(F_TAG.render("NEAREST x3 (level / dive)", True, (210, 200, 150)),
               (rect.x + 8, rect.bottom - 18))


for idx, (key, name, feat) in enumerate(ORDER):
    getter = BUILDERS[key]
    cx = PAD
    cy = HEADER_H + PAD + idx * (CARD_H + PAD)
    card = pygame.Rect(cx, cy, CARD_W, CARD_H)
    pygame.draw.rect(sheet, CARD_BG, card, border_radius=12)
    pygame.draw.rect(sheet, CARD_EDGE, card, 3, border_radius=12)

    sheet.blit(F_NAME.render(name, True, CARD_EDGE), (cx + 14, cy + 8))
    sheet.blit(F_FEAT.render("livery: " + feat, True, SUB), (cx + 14, cy + 32))

    top = cy + 52
    # Hero day + hero night.
    _hero_panel(pygame.Rect(cx + 14, top, 150, 132), HERO_DAY, getter, "130px DAY")
    _hero_panel(pygame.Rect(cx + 172, top, 150, 132), HERO_NIGHT, getter, "130px NIGHT")
    # Day game panel + night game panel (same GAME_PANEL bg; label distinguishes).
    _game_panel(pygame.Rect(cx + 332, top, 200, 132), getter, "DAY")
    _game_panel(pygame.Rect(cx + 544, top, 200, 132), getter, "NIGHT")

out_path = os.path.join(_here, "round_1.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
