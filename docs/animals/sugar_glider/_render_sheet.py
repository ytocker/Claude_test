"""Round-1 review sheet for the candidate SUGAR GLIDER Store skins.

Renders all 5 variants at hero 130px AND at the in-game truth-test scale
(40px, level + dive tilt), each shown over BOTH a bright-day and a night sky
(this is a night-eyed creature that must still pop on day skies), plus a
NEAREST-NEIGHBOR x3 magnification of the 40px reads so the true gameplay-pixel
silhouette is honest (smoothscale flatters tiny detail that vanishes in
motion). Headless (SDL dummy) so it runs in CI / on the build box.
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
    "sugar_glider_skins", os.path.join(_here, "sugar_glider_skins.py"))
sg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sg)

BUILDERS = sg.BUILDERS

ORDER = [
    ("skin_sugar_glider_v1", "V1 · CLASSIC GREY KITE",
     "square kite + bold dorsal stripe + masked night-eyes"),
    ("skin_sugar_glider_v2", "V2 · CARAMEL ROUNDED-WING",
     "rounded leaf membrane + soft rust stripe + huge eyes"),
    ("skin_sugar_glider_v3", "V3 · WHITE-FACED BOLD-STRIPE",
     "thick black stripe forks into mask + white face"),
    ("skin_sugar_glider_v4", "V4 · TWILIGHT FLYING-SQUIRREL",
     "shape-led dark kite + glowing belly + glowing eyes"),
    ("skin_sugar_glider_v5", "V5 · SCALLOPED-EDGE SHOWPIECE",
     "dark-rimmed scalloped kite + bold stripe"),
]

# ── layout ───────────────────────────────────────────────────────────────────
COLS = 1
CARD_W, CARD_H = 760, 220
PAD = 16
HEADER_H = 66
HERO_PX = 130
GAME_PX = 40
MAG = 3

# Two test skies: bright day + night.
DAY_TOP = (150, 206, 240)
DAY_BOT = (208, 234, 246)
NIGHT_TOP = (24, 26, 52)
NIGHT_BOT = (40, 30, 60)

SHEET_BG_T = (18, 19, 32)
SHEET_BG_B = (32, 26, 44)
CARD_BG = (16, 17, 30)
CARD_EDGE = (70, 74, 120)
TEXT = (236, 238, 250)
SUB = (158, 164, 196)

SHEET_W = PAD + CARD_W + PAD
SHEET_H = HEADER_H + PAD + len(ORDER) * (CARD_H + PAD)

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(SHEET_BG_T[i] + (SHEET_BG_B[i] - SHEET_BG_T[i]) * t) for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 30, bold=True)
F_SUB = pygame.font.SysFont("Arial", 14)
F_NAME = pygame.font.SysFont("Arial", 19, bold=True)
F_FEAT = pygame.font.SysFont("Arial", 13)
F_TAG = pygame.font.SysFont("Arial", 12, bold=True)

sheet.blit(F_TITLE.render("Skybit — Sugar Glider Animal Skin · Round 1", True, TEXT), (PAD, 14))
sheet.blit(F_SUB.render(
    "HERO 130px · 40px level & dive (smooth) on DAY + NIGHT sky · NEAREST x3 magnified 40px (honest gameplay read). "
    "North star: lives or dies at 40px in motion.",
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


def sky_panel(rect, top, bot, *, stars=False):
    panel = pygame.Surface((rect.w, rect.h))
    for y in range(rect.h):
        t = y / rect.h
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(panel, col, (0, y), (rect.w, y))
    if stars:
        import random
        rng = random.Random(rect.x * 7 + rect.y)
        for _ in range(28):
            sx, sy = rng.randint(0, rect.w), rng.randint(0, rect.h)
            b = rng.randint(120, 220)
            pygame.draw.circle(panel, (b, b, min(255, b + 30)), (sx, sy), rng.choice([1, 1, 2]))
    rounded = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(rounded, (255, 255, 255), rounded.get_rect(), border_radius=10)
    panel = panel.convert_alpha()
    panel.blit(rounded, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    sheet.blit(panel, rect.topleft)


for idx, (key, name, feat) in enumerate(ORDER):
    getter = BUILDERS[key]
    cx = PAD
    cy = HEADER_H + PAD + idx * (CARD_H + PAD)

    card = pygame.Rect(cx, cy, CARD_W, CARD_H)
    pygame.draw.rect(sheet, CARD_BG, card, border_radius=12)
    pygame.draw.rect(sheet, CARD_EDGE, card, 2, border_radius=12)

    sheet.blit(F_NAME.render(name, True, TEXT), (cx + 14, cy + 10))
    sheet.blit(F_FEAT.render("read: " + feat, True, SUB), (cx + 14, cy + 36))

    top_y = cy + 58
    ph = 150

    # 1 · Hero 130px on DAY sky.
    hero_day = pygame.Rect(cx + 12, top_y, 150, ph)
    sky_panel(hero_day, DAY_TOP, DAY_BOT)
    h = smooth(getter, 0, 0, HERO_PX)
    sheet.blit(h, h.get_rect(center=hero_day.center))
    sheet.blit(F_TAG.render("130px · day", True, (40, 60, 80)),
               (hero_day.x + 6, hero_day.bottom - 18))

    # 2 · Hero 130px on NIGHT sky.
    hero_night = pygame.Rect(hero_day.right + 10, top_y, 150, ph)
    sky_panel(hero_night, NIGHT_TOP, NIGHT_BOT, stars=True)
    sheet.blit(h, h.get_rect(center=hero_night.center))
    sheet.blit(F_TAG.render("130px · night", True, (200, 200, 230)),
               (hero_night.x + 6, hero_night.bottom - 18))

    # 3 · 40px smooth (level + dive) on day + night.
    g40 = pygame.Rect(hero_night.right + 10, top_y, 200, ph)
    pygame.draw.rect(sheet, (10, 11, 22), g40, border_radius=10)
    dp = pygame.Rect(g40.x + 6, g40.y + 6, 90, 64)
    sky_panel(dp, DAY_TOP, DAY_BOT)
    np_ = pygame.Rect(g40.x + 102, g40.y + 6, 90, 64)
    sky_panel(np_, NIGHT_TOP, NIGHT_BOT, stars=True)
    for panel, tilt, frame in ((dp, 0, 2), (np_, 0, 2)):
        lvl = smooth(getter, frame, tilt, GAME_PX)
        panel_rect = pygame.Rect(panel.x, panel.y, panel.w, panel.h)
        sheet.blit(lvl, lvl.get_rect(center=(panel_rect.x + 26, panel_rect.centery)))
        dive = smooth(getter, 1, -32, GAME_PX)
        sheet.blit(dive, dive.get_rect(center=(panel_rect.x + 64, panel_rect.centery)))
    sheet.blit(F_TAG.render("40px smooth · day / night", True, SUB),
               (g40.x + 6, g40.y + 78))
    sheet.blit(F_TAG.render("(level + dive each)", True, SUB),
               (g40.x + 6, g40.y + 96))

    # 4 · NEAREST x3 honest read (level + dive).
    nn = pygame.Rect(g40.right + 10, top_y, 244, ph)
    pygame.draw.rect(sheet, (10, 11, 22), nn, border_radius=10)
    n_level = nearest40(getter, 2, 0, MAG)
    sheet.blit(n_level, n_level.get_rect(center=(nn.x + 64, nn.y + 60)))
    n_dive = nearest40(getter, 1, -32, MAG)
    sheet.blit(n_dive, n_dive.get_rect(center=(nn.x + 172, nn.y + 60)))
    sheet.blit(F_TAG.render("40px NEAREST x3  (level / dive) — the honest read",
                            True, (210, 200, 150)), (nn.x + 8, nn.bottom - 20))

out_path = os.path.join(_here, "round_1.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
