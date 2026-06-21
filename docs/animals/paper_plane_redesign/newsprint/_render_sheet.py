"""Round-1 review sheet — NEWSPRINT / COMIC paper-plane skin candidates.

Each of the 5 sub-takes is rendered as:
  * a HERO read at 130px (smoothscaled, flattering), and
  * the in-game truth test at 40px — level + dive tilt — on BOTH a DAY sky and a
    NIGHT sky, magnified back up with NEAREST-NEIGHBOR so the honest gameplay
    pixels are inspected with no extra smoothing.

The day/night split is the load-bearing test for this concept: light-grey
newsprint must hold its ONE bold black tell against a bright day sky AND a dark
night sky. Headless (SDL dummy) so it runs in CI / on the build box.
"""
import importlib.util
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

_here = os.path.dirname(__file__)
spec = importlib.util.spec_from_file_location(
    "newsprint_skins", os.path.join(_here, "newsprint_skins.py"))
newsprint_skins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(newsprint_skins)

VARIANTS = newsprint_skins.VARIANTS
ORDER = list(VARIANTS.items())

# ── layout ───────────────────────────────────────────────────────────────────
HERO_PX = 130
GAME_PX = 40
MAG = 3

CARD_W, CARD_H = 560, 220
PAD = 16
HEADER_H = 64

# Day sky (Skybit warm daylight) + night sky (deep blue) gradients for the
# in-game truth panels.
DAY_TOP, DAY_BOT = (150, 200, 240), (224, 232, 214)
NIGHT_TOP, NIGHT_BOT = (24, 26, 52), (44, 34, 64)

SHEET_BG_TOP, SHEET_BG_BOT = (30, 32, 46), (18, 19, 30)
CARD_BG = (24, 25, 38)
CARD_EDGE = (70, 74, 110)
TEXT = (238, 240, 250)
SUB = (150, 156, 190)
HERO_PANEL = (40, 42, 60)

SHEET_W = PAD + CARD_W + PAD
SHEET_H = HEADER_H + PAD + len(ORDER) * (CARD_H + PAD)

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(SHEET_BG_TOP[i] + (SHEET_BG_BOT[i] - SHEET_BG_TOP[i]) * t)
                for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 28, bold=True)
F_SUB = pygame.font.SysFont("Arial", 14)
F_NAME = pygame.font.SysFont("Arial", 19, bold=True)
F_TAG = pygame.font.SysFont("Arial", 12, bold=True)

sheet.blit(F_TITLE.render(
    "Skybit — PAPER PLANE redesign · NEWSPRINT / COMIC · Round 1", True, TEXT),
    (PAD, 14))
sheet.blit(F_SUB.render(
    "HERO 130px · 40px NEAREST x3 (level / dive) on DAY and NIGHT skies — the "
    "honest gameplay read. One bold black tell must survive both.",
    True, SUB), (PAD, 44))


def _grad_panel(rect, top, bot):
    surf = pygame.Surface((rect.w, rect.h))
    for y in range(rect.h):
        t = y / rect.h
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(surf, col, (0, y), (rect.w, y))
    return surf


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
        crop, (max(1, int(crop.get_width() * f)),
               max(1, int(crop.get_height() * f))))


def nearest40(getter, frame_idx, tilt, mag):
    """Truth test: smoothscale DOWN to true 40px gameplay pixels, then magnify
    back up with NEAREST-NEIGHBOR — exactly those pixels, no extra smoothing."""
    small = smooth(getter, frame_idx, tilt, GAME_PX)
    return pygame.transform.scale(
        small, (small.get_width() * mag, small.get_height() * mag))


for idx, (name, getter) in enumerate(ORDER):
    cx = PAD
    cy = HEADER_H + PAD + idx * (CARD_H + PAD)
    card = pygame.Rect(cx, cy, CARD_W, CARD_H)
    pygame.draw.rect(sheet, CARD_BG, card, border_radius=12)
    pygame.draw.rect(sheet, CARD_EDGE, card, 2, border_radius=12)

    sheet.blit(F_NAME.render(name, True, TEXT), (cx + 14, cy + 10))

    # Hero panel (left).
    hero_panel = pygame.Rect(cx + 12, cy + 42, 150, 162)
    pygame.draw.rect(sheet, HERO_PANEL, hero_panel, border_radius=10)
    hero = smooth(getter, 0, 0, HERO_PX)
    sheet.blit(hero, hero.get_rect(center=hero_panel.center))
    sheet.blit(F_TAG.render("130px hero", True, SUB),
               (hero_panel.x + 6, hero_panel.bottom - 18))

    # Two truth panels: DAY (mid) + NIGHT (right), each level + dive at NEAREST x3.
    for j, (label, top, bot) in enumerate(
            (("DAY", DAY_TOP, DAY_BOT), ("NIGHT", NIGHT_TOP, NIGHT_BOT))):
        px = cx + 174 + j * 196
        panel = pygame.Rect(px, cy + 42, 184, 162)
        pygame.draw.rect(sheet, (10, 10, 18), panel.inflate(4, 4), border_radius=10)
        sheet.blit(_grad_panel(panel, top, bot), panel.topleft)
        sub_text = (40, 40, 50) if label == "DAY" else (200, 206, 230)
        sheet.blit(F_TAG.render(label + " · 40px NEAREST x3", True, sub_text),
                   (panel.x + 8, panel.y + 6))

        n_level = nearest40(getter, 2, 0, MAG)
        sheet.blit(n_level, n_level.get_rect(
            center=(panel.x + 52, panel.y + 92)))
        n_dive = nearest40(getter, 1, -32, MAG)
        sheet.blit(n_dive, n_dive.get_rect(
            center=(panel.x + 132, panel.y + 92)))
        sheet.blit(F_TAG.render("level / dive", True, sub_text),
                   (panel.x + 8, panel.bottom - 18))

out_path = os.path.join(_here, "round_1.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
