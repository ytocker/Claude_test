"""Round-1 review sheet for the candidate AXOLOTL Store skins.

Renders each of the 5 variants at hero 130px AND at the in-game truth-test
scale (40px, level + dive tilt), plus a NEAREST-NEIGHBOR x3 magnification of
those 40px reads so the true gameplay-pixel silhouette is honest. Each card is
split DAY (left) / NIGHT (right) behind the hero so the brief's "read against
bright-day AND night skies" is checkable at a glance. Headless (SDL dummy).
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

import importlib.util
_here = os.path.dirname(__file__)
spec = importlib.util.spec_from_file_location(
    "axolotl_skins", os.path.join(_here, "axolotl_skins.py"))
axolotl_skins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(axolotl_skins)

VARIANTS = axolotl_skins.VARIANTS
FEATURES = axolotl_skins.FEATURES

ORDER = list(VARIANTS.keys())

# ── layout ───────────────────────────────────────────────────────────────────
COLS = 3
ROWS = (len(ORDER) + COLS - 1) // COLS
CARD_W, CARD_H = 360, 250
PAD = 16
HEADER_H = 60
HERO_PX = 130
GAME_PX = 40
MAG = 3

BG_TOP = (28, 24, 40)
BG_BOT = (44, 30, 52)
CARD_BG = (18, 16, 30)
CARD_EDGE = (90, 70, 110)
TEXT = (240, 234, 246)
SUB = (172, 158, 190)

DAY_TOP = (150, 210, 245)            # bright-day sky
DAY_BOT = (210, 238, 250)
NIGHT_TOP = (20, 22, 48)             # night sky
NIGHT_BOT = (34, 26, 56)
GAME_PANEL = (14, 12, 24)

SHEET_W = PAD + COLS * (CARD_W + PAD)
SHEET_H = HEADER_H + PAD + ROWS * (CARD_H + PAD)

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(BG_TOP[i] + (BG_BOT[i] - BG_TOP[i]) * t) for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 30, bold=True)
F_SUB = pygame.font.SysFont("Arial", 15)
F_NAME = pygame.font.SysFont("Arial", 18, bold=True)
F_FEAT = pygame.font.SysFont("Arial", 13)
F_TAG = pygame.font.SysFont("Arial", 12, bold=True)

sheet.blit(F_TITLE.render("Skybit — AXOLOTL Store Skin · Round 1", True, TEXT),
           (PAD, 12))
sheet.blit(F_SUB.render(
    "HERO 130px (split DAY | NIGHT) · 40px level & dive (smooth) · NEAREST x3 magnified 40px (the honest gameplay read).",
    True, SUB), (PAD, 42))


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


def _grad_rect(target, rect, top, bot):
    for y in range(rect.height):
        t = y / max(1, rect.height)
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(target, col, (rect.x, rect.y + y),
                         (rect.right, rect.y + y))


for idx, key in enumerate(ORDER):
    getter = VARIANTS[key]
    feat = FEATURES[key]
    r, c = divmod(idx, COLS)
    cx = PAD + c * (CARD_W + PAD)
    cy = HEADER_H + PAD + r * (CARD_H + PAD)

    card = pygame.Rect(cx, cy, CARD_W, CARD_H)
    pygame.draw.rect(sheet, CARD_BG, card, border_radius=12)
    pygame.draw.rect(sheet, CARD_EDGE, card, 2, border_radius=12)

    sheet.blit(F_NAME.render(key, True, TEXT), (cx + 14, cy + 10))
    sheet.blit(F_FEAT.render("read: " + feat, True, SUB), (cx + 14, cy + 34))

    # Hero panel (left), split day/night so we judge both skies at once.
    hero_panel = pygame.Rect(cx + 12, cy + 56, 150, 178)
    half = hero_panel.copy()
    half.width //= 2
    _grad_rect(sheet, half, DAY_TOP, DAY_BOT)
    half2 = half.copy()
    half2.x += half.width
    _grad_rect(sheet, half2, NIGHT_TOP, NIGHT_BOT)
    # a few stars on the night half
    import random
    rng = random.Random(idx * 7 + 3)
    for _ in range(20):
        sx = rng.randint(half2.x, half2.right)
        sy = rng.randint(half2.y, half2.bottom)
        b = rng.randint(120, 220)
        pygame.draw.circle(sheet, (b, b, min(255, b + 30)), (sx, sy), 1)
    pygame.draw.rect(sheet, CARD_EDGE, hero_panel, 1, border_radius=10)

    hero = smooth(getter, 0, 0, HERO_PX)
    sheet.blit(hero, hero.get_rect(center=hero_panel.center))
    sheet.blit(F_TAG.render("130px  DAY|NIGHT", True, (40, 40, 60)),
               (hero_panel.x + 6, hero_panel.y + 4))

    # Game panel (right) — smooth 40px (top) + NEAREST x3 truth (bottom).
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
