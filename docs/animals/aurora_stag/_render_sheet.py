"""Round-1 review sheet for the candidate AURORA STAG skins.

Renders each of the 5 variants at hero 130px AND at the in-game truth-test
scale (40px, level + dive tilt), plus a NEAREST-NEIGHBOR x3 magnification of
those 40px reads so the true gameplay-pixel silhouette is honest (smoothscale
flatters tiny detail that vanishes in motion). Night backdrop (the aurora
crown must sing on a dark sky). Headless (SDL dummy) so it runs in CI / on the
build box.
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
    "aurora_stag_skins", os.path.join(_here, "aurora_stag_skins.py"))
aurora_stag_skins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(aurora_stag_skins)

BUILDERS = aurora_stag_skins.BUILDERS

ORDER = [
    ("skin_aurora_stag_v1", "v1 · SPECTRUM CROWN",
     "branchy rack, green→violet→pink, dense stars, regal"),
    ("skin_aurora_stag_v2", "v2 · TWIN CURTAINS",
     "translucent green/violet drapery sheets, sparse stars"),
    ("skin_aurora_stag_v3", "v3 · WIDE RACK",
     "wide many-tined rack, pink/gold sunset aurora"),
    ("skin_aurora_stag_v4", "v4 · LYRE BEAMS",
     "two bold lyre arcs + tip stars, violet→green, fierce"),
    ("skin_aurora_stag_v5", "v5 · CONSTELLATION",
     "star-node lattice antlers joined by aurora lines"),
]

# ── layout ───────────────────────────────────────────────────────────────────
COLS = 2
ROWS = (len(ORDER) + COLS - 1) // COLS
CARD_W, CARD_H = 360, 250
PAD = 16
HEADER_H = 64
HERO_PX = 130
GAME_PX = 40
MAG = 3

NIGHT_TOP = (16, 18, 40)
NIGHT_BOT = (30, 22, 52)
CARD_BG = (12, 14, 30)
CARD_EDGE = (60, 64, 110)
LEG_EDGE = (170, 130, 230)                 # aurora-violet rim for legendary
TEXT = (236, 238, 250)
SUB = (150, 156, 190)
HERO_PANEL = (20, 22, 46)
GAME_PANEL = (8, 9, 22)

SHEET_W = PAD + COLS * (CARD_W + PAD)
SHEET_H = HEADER_H + PAD + ROWS * (CARD_H + PAD)

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(NIGHT_TOP[i] + (NIGHT_BOT[i] - NIGHT_TOP[i]) * t) for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

import random
rng = random.Random(11)
for _ in range(200):
    sx, sy = rng.randint(0, SHEET_W), rng.randint(0, SHEET_H)
    b = rng.randint(70, 200)
    pygame.draw.circle(sheet, (b, b, min(255, b + 40)), (sx, sy), rng.choice([1, 1, 2]))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 30, bold=True)
F_SUB = pygame.font.SysFont("Arial", 15)
F_NAME = pygame.font.SysFont("Arial", 18, bold=True)
F_FEAT = pygame.font.SysFont("Arial", 13)
F_TAG = pygame.font.SysFont("Arial", 12, bold=True)

sheet.blit(F_TITLE.render("Skybit — AURORA STAG (legendary) · Round 1", True, TEXT), (PAD, 14))
sheet.blit(F_SUB.render(
    "HERO 130px · 40px level & dive (smooth) · NEAREST-NEIGHBOR x3 magnified 40px (the honest gameplay read).",
    True, SUB), (PAD, 44))


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


for idx, (key, name, feat) in enumerate(ORDER):
    getter = BUILDERS[key]
    r, c = divmod(idx, COLS)
    cx = PAD + c * (CARD_W + PAD)
    cy = HEADER_H + PAD + r * (CARD_H + PAD)

    card = pygame.Rect(cx, cy, CARD_W, CARD_H)
    pygame.draw.rect(sheet, CARD_BG, card, border_radius=12)
    pygame.draw.rect(sheet, LEG_EDGE, card, 3, border_radius=12)

    sheet.blit(F_NAME.render(name, True, LEG_EDGE), (cx + 14, cy + 10))
    sheet.blit(F_FEAT.render("read: " + feat, True, SUB), (cx + 14, cy + 34))

    # Hero panel (left).
    hero_panel = pygame.Rect(cx + 12, cy + 56, 150, 178)
    pygame.draw.rect(sheet, HERO_PANEL, hero_panel, border_radius=10)
    hero = smooth(getter, 0, 0, HERO_PX)
    sheet.blit(hero, hero.get_rect(center=hero_panel.center))
    sheet.blit(F_TAG.render("130px", True, SUB),
               (hero_panel.x + 6, hero_panel.bottom - 18))

    # Game panel (right): smooth 40px reference (top) + NEAREST x3 (bottom).
    game_panel = pygame.Rect(cx + 170, cy + 56, 178, 178)
    pygame.draw.rect(sheet, GAME_PANEL, game_panel, border_radius=10)

    g_level = smooth(getter, 2, 0, GAME_PX)
    sheet.blit(g_level, g_level.get_rect(center=(game_panel.x + 44, game_panel.y + 30)))
    g_dive = smooth(getter, 1, -32, GAME_PX)
    sheet.blit(g_dive, g_dive.get_rect(center=(game_panel.x + 110, game_panel.y + 30)))
    sheet.blit(F_TAG.render("40px smooth", True, SUB),
               (game_panel.x + 8, game_panel.y + 54))

    n_level = nearest40(getter, 2, 0, MAG)
    sheet.blit(n_level, n_level.get_rect(center=(game_panel.x + 50, game_panel.y + 118)))
    n_dive = nearest40(getter, 1, -32, MAG)
    sheet.blit(n_dive, n_dive.get_rect(center=(game_panel.x + 128, game_panel.y + 118)))
    sheet.blit(F_TAG.render("40px NEAREST x3  (level / dive)", True, (210, 200, 150)),
               (game_panel.x + 8, game_panel.bottom - 18))

out_path = os.path.join(_here, "round_1.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
