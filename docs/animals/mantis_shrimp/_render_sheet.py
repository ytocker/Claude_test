"""Round-2 review sheet for the production MANTIS SHRIMP skin.

One ship-ready design (the perfected v3 DUOTONE BRUISER), shown on BOTH a
bright-day and a night backdrop. Each backdrop carries:

  * hero 130px (cocked/level + punch poses), and
  * the in-game truth test: 40px down-sampled then NEAREST-NEIGHBOR x3 so the
    honest gameplay-pixel silhouette is visible (smoothscale flatters tiny
    detail that vanishes in motion).

Day uses the flat-duotone build; night uses the glow build so the eye-jewel +
club-tip night halos are reviewable in context. Headless (SDL dummy).
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

DAY = mantis.get_mantis_shrimp
NIGHT = mantis.get_mantis_shrimp_night

# ── layout ───────────────────────────────────────────────────────────────────
PAD = 18
HEADER_H = 70
HERO_PX = 130
GAME_PX = 40
MAG = 3

CARD_W, CARD_H = 520, 470

DAY_TOP = (150, 214, 240)
DAY_BOT = (214, 242, 250)
NIGHT_TOP = (18, 20, 46)
NIGHT_BOT = (40, 28, 60)
SHEET_TOP = (24, 26, 52)
SHEET_BOT = (40, 30, 60)
CARD_BG = (16, 17, 34)
CARD_EDGE = (60, 64, 110)
TEXT = (236, 238, 250)
SUB = (150, 156, 190)
GAME_PANEL = (12, 13, 28)

SHEET_W = PAD + 2 * (CARD_W + PAD)
SHEET_H = HEADER_H + PAD + (CARD_H + PAD)

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(SHEET_TOP[i] + (SHEET_BOT[i] - SHEET_TOP[i]) * t) for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

import random
rng = random.Random(11)
for _ in range(200):
    sx, sy = rng.randint(0, SHEET_W), rng.randint(0, SHEET_H)
    b = rng.randint(80, 200)
    pygame.draw.circle(sheet, (b, b, min(255, b + 30)), (sx, sy), rng.choice([1, 1, 2]))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 30, bold=True)
F_SUB = pygame.font.SysFont("Arial", 15)
F_NAME = pygame.font.SysFont("Arial", 20, bold=True)
F_FEAT = pygame.font.SysFont("Arial", 13)
F_TAG = pygame.font.SysFont("Arial", 12, bold=True)

sheet.blit(F_TITLE.render("Skybit — MANTIS SHRIMP skin · Round 2 (DUOTONE BRUISER, ship candidate)", True, TEXT), (PAD, 14))
sheet.blit(F_SUB.render(
    "Separated twin clubs · lead haymaker crosses the snout on the punch · jewel periscopes + banded mid-stripe · night glow on eyes+club-tips only.",
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


def _grad_panel(top, bot, w, h):
    p = pygame.Surface((w, h))
    for y in range(h):
        t = y / h
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(p, col, (0, y), (w, y))
    return p


def _card(cx, cy, title, getter, day):
    card = pygame.Rect(cx, cy, CARD_W, CARD_H)
    pygame.draw.rect(sheet, CARD_BG, card, border_radius=14)
    pygame.draw.rect(sheet, CARD_EDGE, card, 2, border_radius=14)
    sheet.blit(F_NAME.render(title, True, TEXT), (cx + 16, cy + 12))

    top, bot = (DAY_TOP, DAY_BOT) if day else (NIGHT_TOP, NIGHT_BOT)
    tag_col = (40, 60, 80) if day else SUB

    # Hero panel (left): cocked/level + punch poses on the biome sky.
    hero_panel = pygame.Rect(cx + 16, cy + 46, 250, 408)
    sheet.blit(_grad_panel(top, bot, hero_panel.w, hero_panel.h), hero_panel.topleft)
    pygame.draw.rect(sheet, CARD_EDGE, hero_panel, 1, border_radius=10)
    hero_cock = smooth(getter, 0, 0, HERO_PX)       # clubs cocked, level
    hero_punch = smooth(getter, 3, 0, HERO_PX)      # haymaker thrown
    sheet.blit(hero_cock, hero_cock.get_rect(center=(hero_panel.centerx, hero_panel.y + 110)))
    sheet.blit(hero_punch, hero_punch.get_rect(center=(hero_panel.centerx, hero_panel.y + 300)))
    sheet.blit(F_TAG.render("130px  COCKED / level", True, tag_col), (hero_panel.x + 8, hero_panel.y + 6))
    sheet.blit(F_TAG.render("130px  PUNCH (crosses snout)", True, tag_col), (hero_panel.x + 8, hero_panel.centery + 80))

    # Game panel (right): 40px smooth (top) + NEAREST x3 truth (bottom).
    game_panel = pygame.Rect(cx + 278, cy + 46, CARD_W - 278 - 16, 408)
    pygame.draw.rect(sheet, GAME_PANEL, game_panel, border_radius=10)

    g_cock = smooth(getter, 0, 0, GAME_PX)
    g_dive = smooth(getter, 3, -32, GAME_PX)
    sheet.blit(g_cock, g_cock.get_rect(center=(game_panel.x + 56, game_panel.y + 44)))
    sheet.blit(g_dive, g_dive.get_rect(center=(game_panel.x + 148, game_panel.y + 44)))
    sheet.blit(F_TAG.render("40px smooth (cock / punch+dive)", True, SUB), (game_panel.x + 10, game_panel.y + 86))

    n_cock = nearest40(getter, 0, 0, MAG)
    n_dive = nearest40(getter, 3, -32, MAG)
    sheet.blit(n_cock, n_cock.get_rect(center=(game_panel.x + 60, game_panel.y + 250)))
    sheet.blit(n_dive, n_dive.get_rect(center=(game_panel.x + 168, game_panel.y + 250)))
    sheet.blit(F_TAG.render("40px NEAREST x3  (cock / punch+dive)", True, (210, 200, 150)),
               (game_panel.x + 10, game_panel.bottom - 22))


_card(PAD, HEADER_H + PAD, "BRIGHT DAY  ·  flat duotone", DAY, day=True)
_card(PAD + CARD_W + PAD, HEADER_H + PAD, "NIGHT  ·  glow on eyes + club-tips", NIGHT, day=False)

out_path = os.path.join(_here, "round_2.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
