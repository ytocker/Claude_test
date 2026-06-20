"""Round-1 review sheet for the candidate CHAMELEON Store skins.

Renders each of the 5 variants at hero 130px AND at the in-game truth-test
scale (40px, level + dive tilt), plus a NEAREST-NEIGHBOR x3 magnification of
those 40px reads so the true gameplay-pixel silhouette is honest. Each card
shows the hero on BOTH a bright-day and a night swatch so the brief's "read
against bright-day AND night skies" gets tested at a glance. Headless (SDL
dummy) so it runs in CI / on the build box.
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
    "chameleon_skins", os.path.join(_here, "chameleon_skins.py"))
chameleon_skins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chameleon_skins)

BUILDERS = chameleon_skins.BUILDERS

ORDER = [
    ("v1 · Rainbow Prism",   "ROYGBIV band slides per frame; tall scalloped casque + big turret"),
    ("v2 · Neon Flush",      "green→pink→blue gradient rotates; sleek low casque, slim coil"),
    ("v3 · Spotted Panther", "blocky mood-spots cycle; white bars; tall triangular casque"),
    ("v4 · Veiled Casque",   "tall helmet hero; diagonal candy stripes scroll; modest turret"),
    ("v5 · Chibi Bubble",    "round body, ONE giant turret; mint↔coral pulse; loose coil"),
]

# ── layout ───────────────────────────────────────────────────────────────────
COLS = 1
CARD_W, CARD_H = 720, 232
PAD = 16
HEADER_H = 66
HERO_PX = 130
GAME_PX = 40
MAG = 3

DAY_TOP = (150, 206, 235)
DAY_BOT = (205, 232, 246)
NIGHT_TOP = (22, 24, 50)
NIGHT_BOT = (40, 30, 60)
CARD_BG = (16, 17, 34)
CARD_EDGE = (60, 64, 110)
TEXT = (236, 238, 250)
SUB = (150, 156, 190)
GAME_PANEL = (12, 13, 28)

ROWS = len(ORDER)
SHEET_W = PAD + COLS * (CARD_W + PAD)
SHEET_H = HEADER_H + PAD + ROWS * (CARD_H + PAD)

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(NIGHT_TOP[i] + (NIGHT_BOT[i] - NIGHT_TOP[i]) * t) for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

import random
rng = random.Random(11)
for _ in range(150):
    sx, sy = rng.randint(0, SHEET_W), rng.randint(0, SHEET_H)
    b = rng.randint(80, 200)
    pygame.draw.circle(sheet, (b, b, min(255, b + 30)), (sx, sy), rng.choice([1, 1, 2]))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 30, bold=True)
F_SUB = pygame.font.SysFont("Arial", 15)
F_NAME = pygame.font.SysFont("Arial", 19, bold=True)
F_FEAT = pygame.font.SysFont("Arial", 13)
F_TAG = pygame.font.SysFont("Arial", 12, bold=True)

sheet.blit(F_TITLE.render("Skybit — CHAMELEON Store Skin · Round 1", True, TEXT), (PAD, 14))
sheet.blit(F_SUB.render(
    "5 takes · HERO 130px on DAY + NIGHT swatches · 40px level/dive (smooth) · NEAREST x3 (honest gameplay read). 40px tell: coiled tail + swivel turret.",
    True, SUB), (PAD, 46))


def _swatch(top, bot, w, h):
    s = pygame.Surface((w, h))
    for y in range(h):
        t = y / h
        s.fill(tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)), (0, y, w, 1))
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


for idx, (key, feat) in enumerate(ORDER):
    getter = BUILDERS[key]
    cx = PAD
    cy = HEADER_H + PAD + idx * (CARD_H + PAD)

    card = pygame.Rect(cx, cy, CARD_W, CARD_H)
    pygame.draw.rect(sheet, CARD_BG, card, border_radius=12)
    pygame.draw.rect(sheet, CARD_EDGE, card, 2, border_radius=12)

    sheet.blit(F_NAME.render(key, True, TEXT), (cx + 14, cy + 10))
    sheet.blit(F_FEAT.render(feat, True, SUB), (cx + 14, cy + 36))

    # Hero on DAY swatch (left) + NIGHT swatch (right of it).
    panel_y = cy + 58
    day_p = pygame.Rect(cx + 12, panel_y, 158, 158)
    night_p = pygame.Rect(cx + 178, panel_y, 158, 158)
    sheet.blit(_swatch(DAY_TOP, DAY_BOT, day_p.w, day_p.h), day_p.topleft)
    sheet.blit(_swatch(NIGHT_TOP, NIGHT_BOT, night_p.w, night_p.h), night_p.topleft)
    pygame.draw.rect(sheet, CARD_EDGE, day_p, 1, border_radius=8)
    pygame.draw.rect(sheet, CARD_EDGE, night_p, 1, border_radius=8)

    hero = smooth(getter, 0, 0, HERO_PX)
    sheet.blit(hero, hero.get_rect(center=day_p.center))
    sheet.blit(hero, hero.get_rect(center=night_p.center))
    sheet.blit(F_TAG.render("130px DAY", True, (40, 60, 90)), (day_p.x + 6, day_p.bottom - 18))
    sheet.blit(F_TAG.render("130px NIGHT", True, SUB), (night_p.x + 6, night_p.bottom - 18))

    # Game panel (right) — smooth 40px reference + NEAREST x3 honest read,
    # across all 4 flap frames so the colour-shift shimmer is visible.
    game_panel = pygame.Rect(cx + 346, panel_y, CARD_W - 346 - 12, 158)
    pygame.draw.rect(sheet, GAME_PANEL, game_panel, border_radius=8)

    # Row 1: smooth 40px, all 4 flap frames level (shows the colour-shift) + 1 dive.
    sheet.blit(F_TAG.render("40px smooth · 4 flap frames (colour-shift) + dive", True, SUB),
               (game_panel.x + 8, game_panel.y + 6))
    for fi in range(4):
        g = smooth(getter, fi, 0, GAME_PX)
        sheet.blit(g, g.get_rect(center=(game_panel.x + 36 + fi * 50, game_panel.y + 42)))
    gd = smooth(getter, 1, -32, GAME_PX)
    sheet.blit(gd, gd.get_rect(center=(game_panel.x + 36 + 4 * 50 + 8, game_panel.y + 42)))

    # Row 2: NEAREST x3 honest read — level (down + up pose) + dive.
    sheet.blit(F_TAG.render("40px NEAREST x3 · down-pose / up-pose(tongue) / dive", True,
                            (210, 200, 150)), (game_panel.x + 8, game_panel.y + 72))
    n_down = nearest40(getter, 0, 0, MAG)
    sheet.blit(n_down, n_down.get_rect(center=(game_panel.x + 56, game_panel.y + 118)))
    n_up = nearest40(getter, 3, 0, MAG)
    sheet.blit(n_up, n_up.get_rect(center=(game_panel.x + 160, game_panel.y + 118)))
    n_dive = nearest40(getter, 1, -32, MAG)
    sheet.blit(n_dive, n_dive.get_rect(center=(game_panel.x + 264, game_panel.y + 118)))

out_path = os.path.join(_here, "round_1.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
