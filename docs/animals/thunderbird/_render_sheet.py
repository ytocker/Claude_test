"""Round-1 review sheet for the candidate THUNDERBIRD skins.

Renders each of the 5 variants at hero 130px AND at the in-game truth-test
scale (40px, level + dive), plus a NEAREST-NEIGHBOR x3 magnification of those
40px reads so the honest gameplay-pixel silhouette is visible (smoothscale
flatters tiny lightning detail that vanishes in motion). NIGHT backdrop so the
electric glow + flash-core read against a dark sky. Headless (SDL dummy) so it
runs in CI / on the build box.
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
    "thunderbird_skins", os.path.join(_here, "thunderbird_skins.py"))
thunderbird_skins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(thunderbird_skins)

BUILDERS = thunderbird_skins.BUILDERS

ORDER = [
    ("skin_thunderbird_v1", "v1 · STORM-RAPTOR", "cloud feathers + curved plumes + wingtip forks"),
    ("skin_thunderbird_v2", "v2 · THUNDERHEAD", "sharp feathers + fierce glowing eyes + brow-bolt"),
    ("skin_thunderbird_v3", "v3 · STORM GOD", "purple full aura + wing veins + fan crest"),
    ("skin_thunderbird_v4", "v4 · LIGHTNING-SNAKE", "formline eye + 2 horns + bolts hang BELOW wings"),
    ("skin_thunderbird_v5", "v5 · WHITE-FLASH", "mohawk + white-core fork fires DOWN on the clap"),
]

COLS = 2
ROWS = (len(ORDER) + COLS - 1) // COLS
CARD_W, CARD_H = 460, 250
PAD = 16
HEADER_H = 64
HERO_PX = 130
GAME_PX = 40
MAG = 3

NIGHT_TOP = (18, 20, 44)
NIGHT_BOT = (32, 26, 56)
CARD_BG = (14, 15, 32)
CARD_EDGE = (70, 90, 140)
LEG_EDGE = (190, 150, 70)              # gold rim — legendary
TEXT = (236, 238, 250)
SUB = (150, 168, 200)
HERO_PANEL = (24, 28, 54)
GAME_PANEL = (10, 11, 26)

SHEET_W = PAD + COLS * (CARD_W + PAD)
SHEET_H = HEADER_H + PAD + ROWS * (CARD_H + PAD)

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(NIGHT_TOP[i] + (NIGHT_BOT[i] - NIGHT_TOP[i]) * t) for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

import random
rng = random.Random(11)
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

sheet.blit(F_TITLE.render("Skybit — THUNDERBIRD (legendary) · Round 1", True, TEXT), (PAD, 14))
sheet.blit(F_SUB.render(
    "HERO 130px · 40px level & dive (smooth) · NEAREST-NEIGHBOR x3 of the 40px reads (the honest gameplay silhouette). Night sky.",
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


for idx, (key, name, feat) in enumerate(ORDER):
    getter = BUILDERS[key]
    r, c = divmod(idx, COLS)
    cx = PAD + c * (CARD_W + PAD)
    cy = HEADER_H + PAD + r * (CARD_H + PAD)

    card = pygame.Rect(cx, cy, CARD_W, CARD_H)
    pygame.draw.rect(sheet, CARD_BG, card, border_radius=12)
    pygame.draw.rect(sheet, LEG_EDGE, card, 3, border_radius=12)

    sheet.blit(F_NAME.render(name, True, LEG_EDGE), (cx + 14, cy + 10))
    sheet.blit(F_FEAT.render("read: " + feat, True, SUB), (cx + 14, cy + 35))

    # Hero panel (left) — shows frame 0 (down-stroke = the thunderclap frame).
    hero_panel = pygame.Rect(cx + 12, cy + 58, 170, 178)
    pygame.draw.rect(sheet, HERO_PANEL, hero_panel, border_radius=10)
    hero = smooth(getter, 0, 0, HERO_PX)
    sheet.blit(hero, hero.get_rect(center=hero_panel.center))
    sheet.blit(F_TAG.render("130px (down-stroke)", True, SUB),
               (hero_panel.x + 6, hero_panel.bottom - 18))

    # Game panel (right) — 40px smooth (top) + NEAREST x3 (bottom).
    game_panel = pygame.Rect(cx + 190, cy + 58, 256, 178)
    pygame.draw.rect(sheet, GAME_PANEL, game_panel, border_radius=10)

    # Row 1: smooth 40px — frame 0 (down/clap, level) + frame 2 (level, dive).
    g_level = smooth(getter, 0, 0, GAME_PX)
    sheet.blit(g_level, g_level.get_rect(center=(game_panel.x + 60, game_panel.y + 32)))
    g_dive = smooth(getter, 1, -32, GAME_PX)
    sheet.blit(g_dive, g_dive.get_rect(center=(game_panel.x + 160, game_panel.y + 32)))
    sheet.blit(F_TAG.render("40px smooth (clap / dive)", True, SUB),
               (game_panel.x + 8, game_panel.y + 58))

    # Row 2: NEAREST x3 — clap (down-stroke) + up-pose, to show the thunderclap
    # beat varying across frames.
    n_clap = nearest40(getter, 0, 0, MAG)
    sheet.blit(n_clap, n_clap.get_rect(center=(game_panel.x + 64, game_panel.y + 124)))
    n_up = nearest40(getter, 3, 0, MAG)
    sheet.blit(n_up, n_up.get_rect(center=(game_panel.x + 180, game_panel.y + 124)))
    sheet.blit(F_TAG.render("40px NEAREST x3  (clap / up-pose)", True, (210, 200, 150)),
               (game_panel.x + 8, game_panel.bottom - 18))

out_path = os.path.join(_here, "round_1.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
