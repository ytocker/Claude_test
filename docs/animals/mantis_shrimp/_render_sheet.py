"""Round-1 review sheet for the candidate MANTIS SHRIMP skin.

Renders each of the 5 variants at hero 130px AND at the in-game truth-test
scale (40px, level + dive tilt), plus a NEAREST-NEIGHBOR x3 magnification of
those 40px reads so the true gameplay-pixel silhouette is honest (smoothscale
flatters tiny detail that vanishes in motion). Headless (SDL dummy) so it
runs in CI / on the build box.

The 40px reads use the PUNCH pose (frame 3, wing=-40) so the strike anim is
visible at gameplay scale — that's the moment the skin must sell.
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
    "mantis_shrimp_skins", os.path.join(_here, "mantis_shrimp_skins.py"))
mantis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mantis)

VARIANTS = mantis.VARIANTS
TELLS = mantis.VARIANT_TELLS
ORDER = list(VARIANTS.keys())

# ── layout ───────────────────────────────────────────────────────────────────
COLS = 3
ROWS = (len(ORDER) + COLS - 1) // COLS
CARD_W, CARD_H = 360, 250
PAD = 16
HEADER_H = 64
HERO_PX = 130
GAME_PX = 40
MAG = 3

# Two backdrops side by side at the hero so day + night reads are both honest.
DAY_TOP = (150, 214, 240)
DAY_BOT = (208, 240, 250)
NIGHT_TOP = (24, 26, 52)
NIGHT_BOT = (40, 30, 60)
CARD_BG = (16, 17, 34)
CARD_EDGE = (60, 64, 110)
TEXT = (236, 238, 250)
SUB = (150, 156, 190)
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

sheet.blit(F_TITLE.render("Skybit — MANTIS SHRIMP skin · Round 1", True, TEXT), (PAD, 12))
sheet.blit(F_SUB.render(
    "HERO 130px on DAY+NIGHT · 40px level & dive (PUNCH pose) · NEAREST x3 magnified 40px (honest gameplay read).",
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


def _grad_panel(top, bot, rect):
    p = pygame.Surface((rect.w, rect.h))
    for y in range(rect.h):
        t = y / rect.h
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(p, col, (0, y), (rect.w, y))
    return p


for idx, key in enumerate(ORDER):
    getter = VARIANTS[key]
    feat = TELLS[key]
    r, c = divmod(idx, COLS)
    cx = PAD + c * (CARD_W + PAD)
    cy = HEADER_H + PAD + r * (CARD_H + PAD)

    card = pygame.Rect(cx, cy, CARD_W, CARD_H)
    pygame.draw.rect(sheet, CARD_BG, card, border_radius=12)
    pygame.draw.rect(sheet, CARD_EDGE, card, 2, border_radius=12)

    sheet.blit(F_NAME.render(key, True, TEXT), (cx + 14, cy + 10))
    sheet.blit(F_FEAT.render("read: " + feat, True, SUB), (cx + 14, cy + 34))

    # Hero panel split day (top) / night (bottom) so both reads are honest.
    hero_panel = pygame.Rect(cx + 12, cy + 56, 150, 178)
    day_rect = pygame.Rect(hero_panel.x, hero_panel.y, hero_panel.w, hero_panel.h // 2)
    night_rect = pygame.Rect(hero_panel.x, hero_panel.centery, hero_panel.w, hero_panel.h // 2)
    sheet.blit(_grad_panel(DAY_TOP, DAY_BOT, day_rect), day_rect.topleft)
    sheet.blit(_grad_panel(NIGHT_TOP, NIGHT_BOT, night_rect), night_rect.topleft)
    pygame.draw.rect(sheet, CARD_EDGE, hero_panel, 1, border_radius=10)
    hero = smooth(getter, 3, 0, HERO_PX)        # punch pose
    sheet.blit(hero, hero.get_rect(center=hero_panel.center))
    sheet.blit(F_TAG.render("130px  day", True, (40, 60, 80)),
               (hero_panel.x + 6, hero_panel.y + 4))
    sheet.blit(F_TAG.render("night", True, SUB),
               (hero_panel.x + 6, hero_panel.bottom - 18))

    # Game panel: smooth 40px (top) + NEAREST x3 (bottom). cocked + punch poses.
    game_panel = pygame.Rect(cx + 170, cy + 56, 178, 178)
    pygame.draw.rect(sheet, GAME_PANEL, game_panel, border_radius=10)

    g_cocked = smooth(getter, 0, 0, GAME_PX)    # clubs back, level
    sheet.blit(g_cocked, g_cocked.get_rect(center=(game_panel.x + 44, game_panel.y + 30)))
    g_dive = smooth(getter, 3, -32, GAME_PX)    # punch, dive
    sheet.blit(g_dive, g_dive.get_rect(center=(game_panel.x + 110, game_panel.y + 30)))
    sheet.blit(F_TAG.render("40px smooth (cock / punch+dive)", True, SUB),
               (game_panel.x + 8, game_panel.y + 54))

    n_cocked = nearest40(getter, 0, 0, MAG)
    sheet.blit(n_cocked, n_cocked.get_rect(center=(game_panel.x + 50, game_panel.y + 118)))
    n_dive = nearest40(getter, 3, -32, MAG)
    sheet.blit(n_dive, n_dive.get_rect(center=(game_panel.x + 128, game_panel.y + 118)))
    sheet.blit(F_TAG.render("40px NEAREST x3  (cock / punch+dive)", True, (210, 200, 150)),
               (game_panel.x + 8, game_panel.bottom - 18))

out_path = os.path.join(_here, "round_1.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
