"""Round-1 review sheet for the candidate GRIFFIN skin (5 variants).

Renders each variant at hero 130px AND at the in-game truth-test scale (40px,
level + dive tilt), plus a NEAREST-NEIGHBOR magnification of those 40px reads so
the true gameplay-pixel silhouette is honest (smoothscale flatters tiny detail
that vanishes in motion). Each variant is shown over BOTH a night and a
bright-day backdrop strip so the read survives both skies. Headless (SDL dummy)
so it runs in CI / on the build box.
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
    "griffin_skins", os.path.join(_here, "griffin_skins.py"))
griffin_skins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(griffin_skins)

BUILDERS = griffin_skins.BUILDERS

ORDER = [
    ("skin_griffin_v1", "V1 · HERALDIC REGAL", "white head + diagonal feather→fur split + big tuft"),
    ("skin_griffin_v2", "V2 · FIERCE RAPTOR", "all-gold head + wide open wings + small tuft"),
    ("skin_griffin_v3", "V3 · MANED TWO-TONE", "vertical feather|fur seam + lion mane collar"),
    ("skin_griffin_v4", "V4 · SOARING WIDE-WING", "huge wingspan + tucked two-tone body"),
    ("skin_griffin_v5", "V5 · CUB CHIBI", "big pale head + giant fluffy tail tuft"),
]

# ── layout ───────────────────────────────────────────────────────────────────
COLS = 2
ROWS = (len(ORDER) + COLS - 1) // COLS
CARD_W, CARD_H = 430, 270
PAD = 18
HEADER_H = 64
HERO_PX = 130
GAME_PX = 40
MAG = 3

NIGHT_TOP = (24, 26, 52)
NIGHT_BOT = (40, 30, 60)
DAY_TOP = (140, 200, 246)
DAY_BOT = (206, 234, 250)
CARD_BG = (16, 17, 34)
CARD_EDGE = (190, 150, 70)               # gold rim — griffin is top-tier
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

import random
rng = random.Random(11)
for _ in range(180):
    sx, sy = rng.randint(0, SHEET_W), rng.randint(0, SHEET_H)
    b = rng.randint(80, 200)
    pygame.draw.circle(sheet, (b, b, min(255, b + 30)), (sx, sy), rng.choice([1, 1, 2]))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 30, bold=True)
F_SUB = pygame.font.SysFont("Arial", 15)
F_NAME = pygame.font.SysFont("Arial", 19, bold=True)
F_FEAT = pygame.font.SysFont("Arial", 13)
F_TAG = pygame.font.SysFont("Arial", 12, bold=True)

sheet.blit(F_TITLE.render("Skybit — GRIFFIN Skin · Round 1", True, TEXT), (PAD, 14))
sheet.blit(F_SUB.render(
    "HERO 130px · 40px level & dive (day + night) · NEAREST-NEIGHBOR x3 (honest gameplay read). Tell = feather→fur split.",
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


def _grad_panel(rect, top, bot):
    p = pygame.Surface((rect.w, rect.h))
    for y in range(rect.h):
        t = y / max(1, rect.h)
        c = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(p, c, (0, y), (rect.w, y))
    s2 = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(s2, (255, 255, 255, 255), s2.get_rect(), border_radius=10)
    p2 = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    p2.blit(p, (0, 0))
    p2.blit(s2, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    sheet.blit(p2, rect.topleft)


for idx, (key, name, feat) in enumerate(ORDER):
    getter = BUILDERS[key]
    r, c = divmod(idx, COLS)
    cx = PAD + c * (CARD_W + PAD)
    cy = HEADER_H + PAD + r * (CARD_H + PAD)

    card = pygame.Rect(cx, cy, CARD_W, CARD_H)
    pygame.draw.rect(sheet, CARD_BG, card, border_radius=12)
    pygame.draw.rect(sheet, CARD_EDGE, card, 3, border_radius=12)

    sheet.blit(F_NAME.render(name, True, CARD_EDGE), (cx + 14, cy + 10))
    sheet.blit(F_FEAT.render("read: " + feat, True, SUB), (cx + 14, cy + 34))

    # Hero panel (left) — half night / half day so colour reads on both.
    hero_panel = pygame.Rect(cx + 12, cy + 58, 160, 196)
    _grad_panel(pygame.Rect(hero_panel.x, hero_panel.y, hero_panel.w, hero_panel.h // 2),
                NIGHT_TOP, NIGHT_BOT)
    _grad_panel(pygame.Rect(hero_panel.x, hero_panel.y + hero_panel.h // 2,
                            hero_panel.w, hero_panel.h - hero_panel.h // 2),
                DAY_TOP, DAY_BOT)
    hero = smooth(getter, 0, 0, HERO_PX)
    sheet.blit(hero, hero.get_rect(center=hero_panel.center))
    sheet.blit(F_TAG.render("130px", True, (230, 230, 235)),
               (hero_panel.x + 6, hero_panel.bottom - 18))

    # Game panel (right): smooth 40px (day + night) + NEAREST x3 truth.
    game_panel = pygame.Rect(cx + 182, cy + 58, 234, 196)
    pygame.draw.rect(sheet, GAME_PANEL, game_panel, border_radius=10)

    # Row 1: smooth 40px level over NIGHT, dive over DAY.
    nrect = pygame.Rect(game_panel.x + 8, game_panel.y + 8, 100, 58)
    drect = pygame.Rect(game_panel.x + 122, game_panel.y + 8, 100, 58)
    _grad_panel(nrect, NIGHT_TOP, NIGHT_BOT)
    _grad_panel(drect, DAY_TOP, DAY_BOT)
    g_level = smooth(getter, 2, 0, GAME_PX)
    sheet.blit(g_level, g_level.get_rect(center=nrect.center))
    g_dive = smooth(getter, 1, -32, GAME_PX)
    sheet.blit(g_dive, g_dive.get_rect(center=drect.center))
    sheet.blit(F_TAG.render("40px  night-level / day-dive", True, SUB),
               (game_panel.x + 8, game_panel.y + 70))

    # Row 2: NEAREST-NEIGHBOR x3 magnified level + dive (the honest read).
    n_level = nearest40(getter, 2, 0, MAG)
    sheet.blit(n_level, n_level.get_rect(center=(game_panel.x + 62, game_panel.y + 134)))
    n_dive = nearest40(getter, 1, -32, MAG)
    sheet.blit(n_dive, n_dive.get_rect(center=(game_panel.x + 172, game_panel.y + 134)))
    sheet.blit(F_TAG.render("40px NEAREST x3  (level / dive)", True, (210, 200, 150)),
               (game_panel.x + 8, game_panel.bottom - 18))

out_path = os.path.join(_here, "round_1.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
