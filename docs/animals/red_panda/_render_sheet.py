"""Round-1 review sheet for the candidate RED PANDA Store skin.

Renders each variant at hero 130px AND at the in-game truth-test scale (40px,
level + dive tilt), plus a NEAREST-NEIGHBOR x3 magnification of those 40px
reads so the true gameplay-pixel silhouette is honest (smoothscale flatters
tiny detail that vanishes in motion). Each card is shown over BOTH a night and
a bright-day swatch behind the 40px reads so the cream mask + ringed tail are
checked against the two sky extremes. Headless (SDL dummy) so it runs in CI.
"""
import importlib.util
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")))

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

_here = os.path.dirname(__file__)
spec = importlib.util.spec_from_file_location(
    "red_panda_skins", os.path.join(_here, "red_panda_skins.py"))
red_panda_skins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(red_panda_skins)

BUILDERS = red_panda_skins.BUILDERS

ORDER = [
    ("v1 Cozy Curl",      "cream/rust ringed C-arc + broad mask"),
    ("v2 Reaching Leaper", "long upward tail whip + forward lean"),
    ("v3 Big-Tail Hero",  "giant ringed banana arc over the back"),
    ("v4 Chibi Round",    "huge-eyed mask face + chunky comma tail"),
    ("v5 Foxy Bandit",    "pointed ears + bandit mask + white tail-tip"),
]

# ── layout ───────────────────────────────────────────────────────────────────
COLS = 2
ROWS = (len(ORDER) + COLS - 1) // COLS
CARD_W, CARD_H = 480, 250
PAD = 16
HEADER_H = 64
HERO_PX = 130
GAME_PX = 40
MAG = 3

NIGHT_TOP = (24, 26, 52)
NIGHT_BOT = (40, 30, 60)
DAY_TOP = (140, 200, 246)
DAY_BOT = (206, 232, 250)
CARD_BG = (16, 17, 34)
CARD_EDGE = (60, 64, 110)
TEXT = (236, 238, 250)
SUB = (150, 156, 190)
HERO_PANEL = (28, 30, 56)
GAME_PANEL = (12, 13, 28)

SHEET_W = PAD + COLS * (CARD_W + PAD)
SHEET_H = HEADER_H + PAD + ROWS * (CARD_H + PAD)

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(NIGHT_TOP[i] + (NIGHT_BOT[i] - NIGHT_TOP[i]) * t)
               for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

rng = random.Random(7)
for _ in range(160):
    sx, sy = rng.randint(0, SHEET_W), rng.randint(0, SHEET_H)
    b = rng.randint(80, 200)
    pygame.draw.circle(sheet, (b, b, min(255, b + 30)), (sx, sy),
                       rng.choice([1, 1, 2]))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 30, bold=True)
F_SUB = pygame.font.SysFont("Arial", 15)
F_NAME = pygame.font.SysFont("Arial", 18, bold=True)
F_FEAT = pygame.font.SysFont("Arial", 13)
F_TAG = pygame.font.SysFont("Arial", 12, bold=True)

sheet.blit(F_TITLE.render("Skybit — RED PANDA Store Skin · Round 1", True, TEXT),
           (PAD, 14))
sheet.blit(F_SUB.render(
    "HERO 130px (night) · 40px level & dive over NIGHT + DAY · NEAREST x3 magnified "
    "40px (the honest gameplay read).", True, SUB), (PAD, 46))


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
    small = smooth(getter, frame_idx, tilt, GAME_PX)
    return pygame.transform.scale(
        small, (small.get_width() * mag, small.get_height() * mag))


def _grad_swatch(rect, top, bot):
    sw = pygame.Surface((rect.w, rect.h))
    for y in range(rect.h):
        t = y / max(1, rect.h)
        c = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(sw, c, (0, y), (rect.w, y))
    sheet.blit(sw, rect.topleft)


for idx, (key, feat) in enumerate(ORDER):
    getter = BUILDERS[key]
    r, c = divmod(idx, COLS)
    cx = PAD + c * (CARD_W + PAD)
    cy = HEADER_H + PAD + r * (CARD_H + PAD)

    card = pygame.Rect(cx, cy, CARD_W, CARD_H)
    pygame.draw.rect(sheet, CARD_BG, card, border_radius=12)
    pygame.draw.rect(sheet, CARD_EDGE, card, 2, border_radius=12)

    sheet.blit(F_NAME.render(key, True, TEXT), (cx + 14, cy + 10))
    sheet.blit(F_FEAT.render("read: " + feat, True, SUB), (cx + 14, cy + 34))

    # Hero panel (left).
    hero_panel = pygame.Rect(cx + 12, cy + 56, 150, 178)
    pygame.draw.rect(sheet, HERO_PANEL, hero_panel, border_radius=10)
    hero = smooth(getter, 0, 0, HERO_PX)
    sheet.blit(hero, hero.get_rect(center=hero_panel.center))
    sheet.blit(F_TAG.render("130px", True, SUB),
               (hero_panel.x + 6, hero_panel.bottom - 18))

    # Game panel (right): night row (top) + day row (bottom), each with
    # smooth-40 reference and NEAREST x3 truth.
    game_panel = pygame.Rect(cx + 170, cy + 56, 298, 178)
    pygame.draw.rect(sheet, GAME_PANEL, game_panel, border_radius=10)

    # NIGHT swatch + reads.
    night_sw = pygame.Rect(game_panel.x + 6, game_panel.y + 6,
                           game_panel.w - 12, 78)
    _grad_swatch(night_sw, NIGHT_TOP, (60, 44, 80))
    g_lvl = smooth(getter, 2, 0, GAME_PX)
    sheet.blit(g_lvl, g_lvl.get_rect(center=(night_sw.x + 34, night_sw.y + 38)))
    g_div = smooth(getter, 1, -32, GAME_PX)
    sheet.blit(g_div, g_div.get_rect(center=(night_sw.x + 78, night_sw.y + 38)))
    n_lvl = nearest40(getter, 2, 0, MAG)
    sheet.blit(n_lvl, n_lvl.get_rect(center=(night_sw.x + 150, night_sw.y + 38)))
    n_div = nearest40(getter, 1, -32, MAG)
    sheet.blit(n_div, n_div.get_rect(center=(night_sw.x + 236, night_sw.y + 38)))
    sheet.blit(F_TAG.render("NIGHT  40 / 40 / x3 lvl / x3 dive", True,
                            (210, 210, 230)), (night_sw.x + 4, night_sw.y + 2))

    # DAY swatch + reads.
    day_sw = pygame.Rect(game_panel.x + 6, game_panel.y + 90,
                         game_panel.w - 12, 80)
    _grad_swatch(day_sw, DAY_TOP, DAY_BOT)
    g_lvl = smooth(getter, 2, 0, GAME_PX)
    sheet.blit(g_lvl, g_lvl.get_rect(center=(day_sw.x + 34, day_sw.y + 40)))
    g_div = smooth(getter, 1, -32, GAME_PX)
    sheet.blit(g_div, g_div.get_rect(center=(day_sw.x + 78, day_sw.y + 40)))
    n_lvl = nearest40(getter, 2, 0, MAG)
    sheet.blit(n_lvl, n_lvl.get_rect(center=(day_sw.x + 150, day_sw.y + 40)))
    n_div = nearest40(getter, 1, -32, MAG)
    sheet.blit(n_div, n_div.get_rect(center=(day_sw.x + 236, day_sw.y + 40)))
    sheet.blit(F_TAG.render("DAY  40 / 40 / x3 lvl / x3 dive", True,
                            (40, 50, 70)), (day_sw.x + 4, day_sw.y + 2))

out_path = os.path.join(_here, "round_1.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
