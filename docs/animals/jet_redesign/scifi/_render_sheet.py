"""Round-2 review sheet for the SCI-FI ENERGY FIGHTER jet redesign.

Single converged production build (v5 · GOLD SOVEREIGN, refined to a cool
platinum/icy-cyan tech read). Renders the hero at 130px AND at the in-game
truth-test scale (40px), with NEAREST-NEIGHBOR x3 magnification of the 40px
reads so the true gameplay-pixel silhouette is honest (smoothscale flatters
tiny detail that vanishes in motion). Shown on BOTH a DAY sky and a NIGHT sky —
a neon-glow tell must survive on a bright sky too, not only on black. The dive
pose is included on both because resolving nose-direction in the inverted dive
was a round-2 punch-list item. Headless (SDL dummy) so it runs in CI.
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

getter = scifi_skins.get_scifi
feat = scifi_skins.VARIANTS[0][1] and scifi_skins.VARIANTS[0][2]

# ── layout ───────────────────────────────────────────────────────────────────
PAD = 18
HEADER_H = 70
HERO_PX = 130
GAME_PX = 40
MAG = 3

BG_TOP = (14, 18, 30)
BG_BOT = (22, 28, 44)
CARD_BG = (12, 15, 26)
CARD_EDGE = (60, 96, 130)
TEXT = (228, 240, 250)
SUB = (140, 168, 196)

# Day sky vs night sky swatches for the truth panels.
DAY_TOP = (150, 200, 240)
DAY_BOT = (214, 230, 244)
NIGHT_TOP = (18, 22, 46)
NIGHT_BOT = (34, 28, 56)

CARD_W = 980
CARD_H = 360
SHEET_W = PAD + CARD_W + PAD
SHEET_H = HEADER_H + PAD + CARD_H + PAD

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(BG_TOP[i] + (BG_BOT[i] - BG_TOP[i]) * t) for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

import random
rng = random.Random(7)
for _ in range(140):
    sx, sy = rng.randint(0, SHEET_W), rng.randint(0, SHEET_H)
    b = rng.randint(60, 170)
    pygame.draw.circle(sheet, (b, b, min(255, b + 50)), (sx, sy), rng.choice([1, 1, 2]))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 30, bold=True)
F_SUB = pygame.font.SysFont("Arial", 15)
F_NAME = pygame.font.SysFont("Arial", 20, bold=True)
F_FEAT = pygame.font.SysFont("Arial", 14)
F_TAG = pygame.font.SysFont("Arial", 13, bold=True)

sheet.blit(F_TITLE.render(
    "Skybit — SCI-FI ENERGY FIGHTER jet redesign · Round 2 (final convergence)", True, TEXT), (PAD, 14))
sheet.blit(F_SUB.render(
    "Single ship-ready build. HERO 130px + 40px NEAREST x3 (level / dive) on DAY and NIGHT — the honest gameplay read.",
    True, SUB), (PAD, 48))


def _crop(frame_idx, tilt):
    s = getter(frame_idx, tilt)
    rect = s.get_bounding_rect()
    if rect.w == 0 or rect.h == 0:
        rect = s.get_rect()
    return s.subsurface(rect).copy()


def smooth(frame_idx, tilt, target_px):
    crop = _crop(frame_idx, tilt)
    longest = max(crop.get_width(), crop.get_height())
    f = target_px / longest
    return pygame.transform.smoothscale(
        crop, (max(1, int(crop.get_width() * f)), max(1, int(crop.get_height() * f))))


def nearest40(frame_idx, tilt, mag):
    small = smooth(frame_idx, tilt, GAME_PX)
    return pygame.transform.scale(
        small, (small.get_width() * mag, small.get_height() * mag))


def _sky(rect, top, bot):
    s = pygame.Surface((rect.w, rect.h))
    for y in range(rect.h):
        t = y / max(1, rect.h)
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(s, col, (0, y), (rect.w, y))
    return s


cx = PAD
cy = HEADER_H + PAD
card = pygame.Rect(cx, cy, CARD_W, CARD_H)
pygame.draw.rect(sheet, CARD_BG, card, border_radius=14)
pygame.draw.rect(sheet, CARD_EDGE, card, 2, border_radius=14)

sheet.blit(F_NAME.render(scifi_skins.VARIANTS[0][0], True, TEXT), (cx + 16, cy + 12))
sheet.blit(F_FEAT.render("read: " + feat, True, SUB), (cx + 16, cy + 40))

PANEL_Y = cy + 66
PANEL_H = 270

# Hero panel (left) on night — the reference, smooth.
hero_panel = pygame.Rect(cx + 14, PANEL_Y, 200, PANEL_H)
sheet.blit(_sky(hero_panel, NIGHT_TOP, NIGHT_BOT), hero_panel.topleft)
pygame.draw.rect(sheet, (46, 70, 96), hero_panel, 1, border_radius=10)
hero = smooth(0, 0, HERO_PX)
sheet.blit(hero, hero.get_rect(center=hero_panel.center))
sheet.blit(F_TAG.render("130px hero (night)", True, SUB),
           (hero_panel.x + 8, hero_panel.bottom - 20))


def truth_panel(px, top, bot, label):
    panel = pygame.Rect(px, PANEL_Y, 360, PANEL_H)
    sheet.blit(_sky(panel, top, bot), panel.topleft)
    pygame.draw.rect(sheet, (46, 70, 96), panel, 1, border_radius=10)
    # Level (pose 2) + dive (pose 1 at -32° = inverted nose-up game spin).
    n_level = nearest40(2, 0, MAG)
    sheet.blit(n_level, n_level.get_rect(center=(panel.x + 100, panel.y + 120)))
    n_dive = nearest40(1, -32, MAG)
    sheet.blit(n_dive, n_dive.get_rect(center=(panel.x + 250, panel.y + 120)))
    lab_col = (26, 38, 58) if label == "DAY" else (210, 228, 244)
    sheet.blit(F_TAG.render(label + " · 40px NEAREST x3  (level / dive)", True, lab_col),
               (panel.x + 10, panel.bottom - 20))


truth_panel(cx + 226, DAY_TOP, DAY_BOT, "DAY")
truth_panel(cx + 226 + 372, NIGHT_TOP, NIGHT_BOT, "NIGHT")

out_path = os.path.join(_here, "round_2.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
