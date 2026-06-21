"""Round-1 review sheet for the SCI-FI ENERGY FIGHTER jet redesign.

Renders each of the 5 sub-takes at hero 130px AND at the in-game truth-test
scale (40px), with NEAREST-NEIGHBOR x3 magnification of the 40px reads so the
true gameplay-pixel silhouette is honest (smoothscale flatters tiny detail
that vanishes in motion). Each variant is shown on BOTH a DAY sky and a NIGHT
sky — a neon-glow tell must survive on a bright sky too, not only on black.
Headless (SDL dummy) so it runs in CI / on the build box.
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
    "scifi_skins", os.path.join(_here, "scifi_skins.py"))
scifi_skins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scifi_skins)

VARIANTS = scifi_skins.VARIANTS

# ── layout ───────────────────────────────────────────────────────────────────
CARD_W, CARD_H = 700, 250
PAD = 16
HEADER_H = 64
HERO_PX = 130
GAME_PX = 40
MAG = 3

BG_TOP = (16, 18, 30)
BG_BOT = (30, 22, 40)
CARD_BG = (14, 15, 28)
CARD_EDGE = (70, 64, 110)
TEXT = (236, 238, 250)
SUB = (150, 156, 190)

# Day sky vs night sky swatches for the truth panels.
DAY_TOP = (150, 200, 240)
DAY_BOT = (210, 226, 240)
NIGHT_TOP = (20, 22, 46)
NIGHT_BOT = (38, 28, 58)

SHEET_W = PAD + CARD_W + PAD
SHEET_H = HEADER_H + PAD + len(VARIANTS) * (CARD_H + PAD)

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(BG_TOP[i] + (BG_BOT[i] - BG_TOP[i]) * t) for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

import random
rng = random.Random(11)
for _ in range(120):
    sx, sy = rng.randint(0, SHEET_W), rng.randint(0, SHEET_H)
    b = rng.randint(70, 180)
    pygame.draw.circle(sheet, (b, b, min(255, b + 40)), (sx, sy), rng.choice([1, 1, 2]))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 30, bold=True)
F_SUB = pygame.font.SysFont("Arial", 15)
F_NAME = pygame.font.SysFont("Arial", 18, bold=True)
F_FEAT = pygame.font.SysFont("Arial", 13)
F_TAG = pygame.font.SysFont("Arial", 12, bold=True)

sheet.blit(F_TITLE.render("Skybit — SCI-FI ENERGY FIGHTER jet redesign · Round 1", True, TEXT), (PAD, 12))
sheet.blit(F_SUB.render(
    "HERO 130px · 40px NEAREST x3 (level / dive) on DAY and NIGHT skies — the honest gameplay read. 5 sub-takes on one concept.",
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


def _sky(rect, top, bot):
    s = pygame.Surface((rect.w, rect.h))
    for y in range(rect.h):
        t = y / max(1, rect.h)
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(s, col, (0, y), (rect.w, y))
    return s


for idx, (name, getter, feat) in enumerate(VARIANTS):
    cx = PAD
    cy = HEADER_H + PAD + idx * (CARD_H + PAD)
    card = pygame.Rect(cx, cy, CARD_W, CARD_H)
    pygame.draw.rect(sheet, CARD_BG, card, border_radius=12)
    pygame.draw.rect(sheet, CARD_EDGE, card, 2, border_radius=12)

    sheet.blit(F_NAME.render(name, True, TEXT), (cx + 14, cy + 10))
    sheet.blit(F_FEAT.render("read: " + feat, True, SUB), (cx + 14, cy + 34))

    # Hero panel (left) on night.
    hero_panel = pygame.Rect(cx + 12, cy + 56, 150, 178)
    sky = _sky(hero_panel, NIGHT_TOP, NIGHT_BOT)
    sheet.blit(sky, hero_panel.topleft)
    pygame.draw.rect(sheet, (50, 48, 80), hero_panel, 1, border_radius=10)
    hero = smooth(getter, 0, 0, HERO_PX)
    sheet.blit(hero, hero.get_rect(center=hero_panel.center))
    sheet.blit(F_TAG.render("130px hero", True, SUB),
               (hero_panel.x + 6, hero_panel.bottom - 18))

    # Two truth panels: DAY (mid) and NIGHT (right), each level + dive NEAREST x3.
    def truth_panel(px, top, bot, label):
        panel = pygame.Rect(px, cy + 56, 256, 178)
        sky = _sky(panel, top, bot)
        sheet.blit(sky, panel.topleft)
        pygame.draw.rect(sheet, (50, 48, 80), panel, 1, border_radius=10)
        n_level = nearest40(getter, 2, 0, MAG)
        sheet.blit(n_level, n_level.get_rect(center=(panel.x + 70, panel.y + 80)))
        n_dive = nearest40(getter, 1, -32, MAG)
        sheet.blit(n_dive, n_dive.get_rect(center=(panel.x + 180, panel.y + 80)))
        lab_col = (30, 40, 60) if label == "DAY" else (210, 200, 150)
        sheet.blit(F_TAG.render(label + " · 40px NEAREST x3  (level / dive)", True, lab_col),
                   (panel.x + 8, panel.bottom - 18))

    truth_panel(cx + 172, DAY_TOP, DAY_BOT, "DAY")
    truth_panel(cx + 172 + 264, NIGHT_TOP, NIGHT_BOT, "NIGHT")

out_path = os.path.join(_here, "round_1.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
