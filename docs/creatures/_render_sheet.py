"""Round-2 review sheet for the candidate animal Store skins.

Renders each creature at hero 130px AND at the in-game truth-test scale
(40px, level + dive tilt), plus a NEAREST-NEIGHBOR magnification of those
40px reads so the true gameplay-pixel silhouette is honest (smoothscale
flatters tiny detail that vanishes in motion). Headless (SDL dummy) so it
runs in CI / on the build box.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

# Import after the dummy driver is set so the parrot module can build surfaces.
import importlib.util
_here = os.path.dirname(__file__)
spec = importlib.util.spec_from_file_location(
    "creature_skins", os.path.join(_here, "creature_skins.py"))
creature_skins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(creature_skins)

BUILDERS = creature_skins.BUILDERS

# Gacha showpieces lead the sheet so the two fixed creatures are prominent.
ORDER = [
    ("skin_dragon", "DRAGON  (gacha)", "horns clear wing → snout → tail spikes"),
    ("skin_phoenix", "PHOENIX  (gacha)", "fat flame crest + fire gradient"),
    ("skin_bat", "BAT", "membrane span + clear eyes/ears"),
    ("skin_owl", "OWL", "facial disc + huge eyes"),
    ("skin_toucan", "TOUCAN", "oversized orange beak"),
    ("skin_penguin", "PENGUIN", "black/white split + beak"),
    ("skin_flamingo", "FLAMINGO", "pink S-neck + bent beak"),
    ("skin_eagle", "BALD EAGLE", "white head + hooked beak"),
    ("skin_bee", "BEE", "gold/black stripes"),
]

# ── layout ───────────────────────────────────────────────────────────────────
COLS = 3
ROWS = (len(ORDER) + COLS - 1) // COLS
CARD_W, CARD_H = 360, 250
PAD = 16
HEADER_H = 60
HERO_PX = 130
GAME_PX = 40
MAG = 3                                  # nearest-neighbor magnification of the 40px reads

NIGHT_TOP = (24, 26, 52)
NIGHT_BOT = (40, 30, 60)
CARD_BG = (16, 17, 34)
CARD_EDGE = (60, 64, 110)
GACHA_EDGE = (190, 150, 70)               # gold rim for the two showpieces
TEXT = (236, 238, 250)
SUB = (150, 156, 190)
HERO_PANEL = (28, 30, 56)
GAME_PANEL = (12, 13, 28)

SHEET_W = PAD + COLS * (CARD_W + PAD)
SHEET_H = HEADER_H + PAD + ROWS * (CARD_H + PAD)

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(NIGHT_TOP[i] + (NIGHT_BOT[i] - NIGHT_TOP[i]) * t) for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

# Scattered stars on the backdrop.
import random
rng = random.Random(7)
for _ in range(160):
    sx, sy = rng.randint(0, SHEET_W), rng.randint(0, SHEET_H)
    b = rng.randint(80, 200)
    pygame.draw.circle(sheet, (b, b, min(255, b + 30)), (sx, sy), rng.choice([1, 1, 2]))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 30, bold=True)
F_SUB = pygame.font.SysFont("Arial", 15)
F_NAME = pygame.font.SysFont("Arial", 18, bold=True)
F_FEAT = pygame.font.SysFont("Arial", 13)
F_TAG = pygame.font.SysFont("Arial", 12, bold=True)

sheet.blit(F_TITLE.render("Skybit — Animal Store Skins · Round 2", True, TEXT), (PAD, 14))
sheet.blit(F_SUB.render(
    "HERO 130px · 40px level & dive (smooth) · NEAREST-NEIGHBOR x3 magnified 40px (the honest gameplay read). Gacha leads.",
    True, SUB), (PAD, 44))


def _crop(getter, frame_idx, tilt):
    s = getter(frame_idx, tilt)
    rect = s.get_bounding_rect()
    if rect.w == 0 or rect.h == 0:
        rect = s.get_rect()
    return s.subsurface(rect).copy()


def smooth(getter, frame_idx, tilt, target_px):
    """Smoothscaled read — flattering hero / reference scale."""
    crop = _crop(getter, frame_idx, tilt)
    longest = max(crop.get_width(), crop.get_height())
    f = target_px / longest
    return pygame.transform.smoothscale(
        crop, (max(1, int(crop.get_width() * f)), max(1, int(crop.get_height() * f))))


def nearest40(getter, frame_idx, tilt, mag):
    """The truth test: smoothscale DOWN to the true 40px gameplay pixels
    (down-sampling needs interpolation to be honest), then magnify back up
    with NEAREST-NEIGHBOR so we inspect exactly those gameplay pixels with
    no extra smoothing."""
    small = smooth(getter, frame_idx, tilt, GAME_PX)
    return pygame.transform.scale(
        small, (small.get_width() * mag, small.get_height() * mag))


for idx, (key, name, feat) in enumerate(ORDER):
    getter = BUILDERS[key]
    r, c = divmod(idx, COLS)
    cx = PAD + c * (CARD_W + PAD)
    cy = HEADER_H + PAD + r * (CARD_H + PAD)

    is_gacha = "gacha" in name
    card = pygame.Rect(cx, cy, CARD_W, CARD_H)
    pygame.draw.rect(sheet, CARD_BG, card, border_radius=12)
    pygame.draw.rect(sheet, GACHA_EDGE if is_gacha else CARD_EDGE,
                     card, 3 if is_gacha else 2, border_radius=12)

    # Name + feature.
    sheet.blit(F_NAME.render(name, True, GACHA_EDGE if is_gacha else TEXT),
               (cx + 14, cy + 10))
    sheet.blit(F_FEAT.render("read: " + feat, True, SUB), (cx + 14, cy + 34))

    # Hero panel (left).
    hero_panel = pygame.Rect(cx + 12, cy + 56, 150, 178)
    pygame.draw.rect(sheet, HERO_PANEL, hero_panel, border_radius=10)
    hero = smooth(getter, 0, 0, HERO_PX)
    sheet.blit(hero, hero.get_rect(center=hero_panel.center))
    sheet.blit(F_TAG.render("130px", True, SUB),
               (hero_panel.x + 6, hero_panel.bottom - 18))

    # Game panel (right) — smooth 40px reference (top) + NEAREST x3 truth (bottom).
    game_panel = pygame.Rect(cx + 170, cy + 56, 178, 178)
    pygame.draw.rect(sheet, GAME_PANEL, game_panel, border_radius=10)

    # Row 1: smooth 40px level + dive (reference).
    g_level = smooth(getter, 2, 0, GAME_PX)
    sheet.blit(g_level, g_level.get_rect(center=(game_panel.x + 44, game_panel.y + 30)))
    g_dive = smooth(getter, 1, -32, GAME_PX)
    sheet.blit(g_dive, g_dive.get_rect(center=(game_panel.x + 110, game_panel.y + 30)))
    sheet.blit(F_TAG.render("40px smooth", True, SUB),
               (game_panel.x + 8, game_panel.y + 54))

    # Row 2: NEAREST-NEIGHBOR x3 magnified level + dive (the honest read).
    n_level = nearest40(getter, 2, 0, MAG)
    sheet.blit(n_level, n_level.get_rect(center=(game_panel.x + 50, game_panel.y + 118)))
    n_dive = nearest40(getter, 1, -32, MAG)
    sheet.blit(n_dive, n_dive.get_rect(center=(game_panel.x + 128, game_panel.y + 118)))
    sheet.blit(F_TAG.render("40px NEAREST x3  (level / dive)", True, (210, 200, 150)),
               (game_panel.x + 8, game_panel.bottom - 18))

out_path = os.path.join(_here, "round_2.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
