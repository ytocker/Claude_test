"""Round-1 review sheet for the WIDE GLIDER paper-plane redesign.

Renders each of the 5 takes (plus the CURRENT production dollar-dart for
comparison) at hero 130px AND at the in-game truth-test scale: 40px NEAREST x3
magnified, level + dive, on BOTH a day sky and a night sky. The 40px NEAREST
read is the honest gameplay silhouette (smoothscale flatters tiny detail that
vanishes in motion); day+night proves the baked self-rim holds value on either
backdrop. Headless (SDL dummy) so it runs in CI / on the build box.
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
    "glider_wide_skins", os.path.join(_here, "glider_wide_skins.py"))
glider_wide_skins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(glider_wide_skins)

# Current production dart, for an apples-to-apples "different silhouette" check.
from game import animal_paper_plane as prod

ORDER = [
    ("__current__", "CURRENT  (dollar dart)", "narrow forward triangle"),
    ("glider_wide_v1", "V1 · WIDE DELTA", "broad delta · white paper"),
    ("glider_wide_v2", "V2 · SQUARE HARRIER", "stubby box · manila + strip"),
    ("glider_wide_v3", "V3 · SWEPT GLIDER", "raked sweep · pale blue"),
    ("glider_wide_v4", "V4 · WINGLET DELTA", "up-folded wingtips · white"),
    ("glider_wide_v5", "V5 · KEEL GLIDER", "bold fuselage ridge · manila"),
]


def _getter(key):
    if key == "__current__":
        return prod.get_paper_plane
    return glider_wide_skins.BUILDERS[key]


# layout
COLS = 3
ROWS = (len(ORDER) + COLS - 1) // COLS
CARD_W, CARD_H = 384, 268
PAD = 16
HEADER_H = 64
HERO_PX = 130
GAME_PX = 40
MAG = 3

# Day + night skies sampled to mirror the game's biome interpolation poles.
DAY_TOP, DAY_BOT = (150, 198, 238), (206, 226, 240)
NIGHT_TOP, NIGHT_BOT = (24, 26, 52), (44, 34, 64)
SHEET_TOP, SHEET_BOT = (20, 22, 44), (36, 28, 56)
CARD_BG = (16, 17, 34)
CARD_EDGE = (60, 64, 110)
CURRENT_EDGE = (120, 124, 150)
TEXT = (236, 238, 250)
SUB = (150, 156, 190)

SHEET_W = PAD + COLS * (CARD_W + PAD)
SHEET_H = HEADER_H + PAD + ROWS * (CARD_H + PAD)

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(SHEET_TOP[i] + (SHEET_BOT[i] - SHEET_TOP[i]) * t) for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 30, bold=True)
F_SUB = pygame.font.SysFont("Arial", 15)
F_NAME = pygame.font.SysFont("Arial", 18, bold=True)
F_FEAT = pygame.font.SysFont("Arial", 13)
F_TAG = pygame.font.SysFont("Arial", 11, bold=True)

sheet.blit(F_TITLE.render("Skybit — PAPER PLANE redesign · WIDE GLIDER · Round 1",
                          True, TEXT), (PAD, 12))
sheet.blit(F_SUB.render(
    "HERO 130px · 40px NEAREST x3 (level / dive) on DAY and NIGHT — the honest gameplay read. Current dart leads for contrast.",
    True, SUB), (PAD, 44))


def _vgrad(w, h, top, bot):
    s = pygame.Surface((w, h))
    for y in range(h):
        t = y / max(1, h - 1)
        s.fill(tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)),
               (0, y, w, 1))
    return s


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
    getter = _getter(key)
    r, c = divmod(idx, COLS)
    cx = PAD + c * (CARD_W + PAD)
    cy = HEADER_H + PAD + r * (CARD_H + PAD)

    is_current = key == "__current__"
    card = pygame.Rect(cx, cy, CARD_W, CARD_H)
    pygame.draw.rect(sheet, CARD_BG, card, border_radius=12)
    pygame.draw.rect(sheet, CURRENT_EDGE if is_current else CARD_EDGE,
                     card, 2, border_radius=12)

    sheet.blit(F_NAME.render(name, True, CURRENT_EDGE if is_current else TEXT),
               (cx + 14, cy + 10))
    sheet.blit(F_FEAT.render(feat, True, SUB), (cx + 14, cy + 34))

    # Hero panel (left) on a soft day sky so folds read in colour.
    hero_panel = pygame.Rect(cx + 12, cy + 58, 150, 196)
    sheet.blit(_vgrad(hero_panel.w, hero_panel.h, DAY_TOP, DAY_BOT),
               hero_panel.topleft)
    pygame.draw.rect(sheet, CARD_EDGE, hero_panel, 1, border_radius=10)
    hero = smooth(getter, 0, 0, HERO_PX)
    sheet.blit(hero, hero.get_rect(center=hero_panel.center))
    sheet.blit(F_TAG.render("130px", True, (40, 50, 70)),
               (hero_panel.x + 6, hero_panel.bottom - 16))

    # Right block: a DAY column and a NIGHT column, each with NEAREST x3
    # level + dive — the truth read on both skies.
    bx = cx + 170
    col_w, col_h = 100, 196
    for j, (label, top, bot, txt) in enumerate((
            ("DAY", DAY_TOP, DAY_BOT, (40, 50, 70)),
            ("NIGHT", NIGHT_TOP, NIGHT_BOT, (210, 214, 240)))):
        panel = pygame.Rect(bx + j * (col_w + 8), cy + 58, col_w, col_h)
        sheet.blit(_vgrad(panel.w, panel.h, top, bot), panel.topleft)
        if label == "NIGHT":
            import random
            rng = random.Random(idx * 7 + 3)
            for _ in range(26):
                sx = panel.x + rng.randint(2, panel.w - 2)
                sy = panel.y + rng.randint(2, panel.h - 2)
                b = rng.randint(120, 220)
                pygame.draw.circle(sheet, (b, b, min(255, b + 24)), (sx, sy), 1)
        pygame.draw.rect(sheet, CARD_EDGE, panel, 1, border_radius=10)
        sheet.blit(F_TAG.render(label, True, txt), (panel.x + 6, panel.y + 4))

        n_level = nearest40(getter, 2, 0, MAG)
        sheet.blit(n_level, n_level.get_rect(center=(panel.centerx, panel.y + 66)))
        n_dive = nearest40(getter, 1, -32, MAG)
        sheet.blit(n_dive, n_dive.get_rect(center=(panel.centerx, panel.y + 138)))
        sheet.blit(F_TAG.render("40px x3", True, txt),
                   (panel.x + 6, panel.bottom - 30))
        sheet.blit(F_TAG.render("level / dive", True, txt),
                   (panel.x + 6, panel.bottom - 16))

out_path = os.path.join(_here, "round_1.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
