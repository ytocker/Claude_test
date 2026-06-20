"""Round-2 review sheet for the converged THUNDERBIRD skin.

ONE production design. Renders it on TWO backdrops — a bright-day sky (the
mandatory legendary proof) and a night sky — each panel showing:
  * hero 130px (clap/down-stroke),
  * 40px smooth (clap + dive),
  * 40px NEAREST-NEIGHBOR x3 of the clap AND up/dive poses (the honest
    gameplay-pixel silhouette; smoothscale flatters tiny lightning detail that
    vanishes in motion).
Headless (SDL dummy) so it runs in CI / on the build box.
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

getter = thunderbird_skins.BUILDERS["skin_thunderbird"]

PAD = 16
HEADER_H = 70
CARD_W, CARD_H = 460, 250
COLS = 2

# day-sky proof is mandatory for a legendary; night proves the glow.
SKIES = [
    ("BRIGHT-DAY SKY", (150, 198, 244), (206, 230, 250), False),
    ("NIGHT SKY", (18, 20, 44), (32, 26, 56), True),
]

CARD_BG_DAY = (96, 150, 206)
CARD_BG_NIGHT = (14, 15, 32)
LEG_EDGE = (210, 168, 78)              # gold rim — legendary
HERO_PANEL_DAY = (132, 182, 226)
HERO_PANEL_NIGHT = (24, 28, 54)
GAME_PANEL_DAY = (118, 170, 218)
GAME_PANEL_NIGHT = (10, 11, 26)

SHEET_W = PAD + COLS * (CARD_W + PAD)
SHEET_H = HEADER_H + PAD + (CARD_H + PAD)

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(20 + (40 - 20) * t) for _ in range(1)) * 0
    col = (int(16 + 18 * t), int(18 + 14 * t), int(38 + 18 * t))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 28, bold=True)
F_SUB = pygame.font.SysFont("Arial", 14)
F_NAME = pygame.font.SysFont("Arial", 19, bold=True)
F_FEAT = pygame.font.SysFont("Arial", 13)
F_TAG = pygame.font.SysFont("Arial", 12, bold=True)

TEXT = (236, 238, 250)
SUB = (170, 186, 214)

sheet.blit(F_TITLE.render("Skybit — THUNDERBIRD (legendary) · Round 2 · STORM-RAPTOR", True, TEXT), (PAD, 12))
sheet.blit(F_SUB.render(
    "ONE converged design. v1 raptor + v4's single ASYMMETRIC under-wing fork (diagonal-outward). "
    "Hero 130px (clap) · 40px smooth · NEAREST x3 (clap / up-dive).",
    True, SUB), (PAD, 44))


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
    small = smooth(frame_idx, tilt, 40)
    return pygame.transform.scale(
        small, (small.get_width() * mag, small.get_height() * mag))


def gradient_panel(rect, top, bot):
    p = pygame.Surface((rect.w, rect.h))
    for y in range(rect.h):
        t = y / max(1, rect.h)
        c = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(p, c, (0, y), (rect.w, y))
    sheet.blit(p, rect.topleft)


import random

for idx, (sky_name, sky_top, sky_bot, is_night) in enumerate(SKIES):
    cx = PAD + idx * (CARD_W + PAD)
    cy = HEADER_H + PAD

    card = pygame.Rect(cx, cy, CARD_W, CARD_H)
    pygame.draw.rect(sheet, CARD_BG_DAY if not is_night else CARD_BG_NIGHT, card, border_radius=12)
    pygame.draw.rect(sheet, LEG_EDGE, card, 3, border_radius=12)

    name_col = LEG_EDGE
    sheet.blit(F_NAME.render(sky_name, True, name_col), (cx + 14, cy + 10))
    sheet.blit(F_FEAT.render("eye = brightest point · yellow fork carries colorblind read", True,
                             (40, 50, 70) if not is_night else SUB), (cx + 14, cy + 35))

    hero_panel = pygame.Rect(cx + 12, cy + 58, 170, 178)
    if is_night:
        pygame.draw.rect(sheet, HERO_PANEL_NIGHT, hero_panel, border_radius=10)
        rng = random.Random(7)
        for _ in range(40):
            sx = rng.randint(hero_panel.x + 4, hero_panel.right - 4)
            sy = rng.randint(hero_panel.y + 4, hero_panel.bottom - 4)
            b = rng.randint(120, 220)
            pygame.draw.circle(sheet, (b, b, min(255, b + 30)), (sx, sy), 1)
    else:
        gradient_panel(hero_panel, HERO_PANEL_DAY, (170, 208, 238))
    # _WING_ANGLES = (50,20,-10,-40) = up, mid-up, level, DOWN — so frame 3 is
    # the down-stroke (the thunderclap, biggest fork); frame 0 is the up-pose.
    hero = smooth(3, 0, 130)
    sheet.blit(hero, hero.get_rect(center=hero_panel.center))
    sheet.blit(F_TAG.render("130px (clap)", True, (30, 40, 60) if not is_night else SUB),
               (hero_panel.x + 6, hero_panel.bottom - 18))

    game_panel = pygame.Rect(cx + 190, cy + 58, 256, 178)
    if is_night:
        pygame.draw.rect(sheet, GAME_PANEL_NIGHT, game_panel, border_radius=10)
    else:
        gradient_panel(game_panel, GAME_PANEL_DAY, (160, 202, 234))

    tag_col = (30, 40, 60) if not is_night else SUB
    g_clap = smooth(3, 0, 40)
    sheet.blit(g_clap, g_clap.get_rect(center=(game_panel.x + 60, game_panel.y + 32)))
    g_dive = smooth(0, -32, 40)
    sheet.blit(g_dive, g_dive.get_rect(center=(game_panel.x + 160, game_panel.y + 32)))
    sheet.blit(F_TAG.render("40px smooth (clap / dive)", True, tag_col),
               (game_panel.x + 8, game_panel.y + 58))

    n_clap = nearest40(3, 0, 3)
    sheet.blit(n_clap, n_clap.get_rect(center=(game_panel.x + 64, game_panel.y + 124)))
    n_up = nearest40(0, -28, 3)
    sheet.blit(n_up, n_up.get_rect(center=(game_panel.x + 180, game_panel.y + 124)))
    sheet.blit(F_TAG.render("40px NEAREST x3  (clap / up-dive)", True,
                            (90, 60, 20) if not is_night else (210, 200, 150)),
               (game_panel.x + 8, game_panel.bottom - 18))

out_path = os.path.join(_here, "round_2.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
