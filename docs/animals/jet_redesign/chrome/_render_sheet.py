"""Round-2 review sheet for the RETRO CHROME jet (single production build).

V3 · BLUE-ANGEL TRIM converged to one ship-ready `build_chrome`. The sheet is
a focused hero (130px) plus the in-game truth-test at 40px (smooth + NEAREST
x3, level + dive) on BOTH day and night — because the north star is "reads
CHROME at 40px on day AND night". NEAREST x3 is the honest gameplay-pixel read
(smoothscale flatters tiny detail that vanishes in motion). Headless (SDL
dummy) so it runs in CI / on the build box.

The build draws nose-RIGHT, upright, level. The secret skin flies inverted
nose-up in game, so the sheet applies the production 205° spin to every read —
what the reviewer sees is the true in-game attitude.
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
    "chrome_skins", os.path.join(_here, "chrome_skins.py"))
chrome_skins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chrome_skins)

getter = chrome_skins.BUILDERS["skin_chrome"]

# The secret skin flies inverted nose-up; bake that spin into every read so the
# sheet shows the true in-game attitude rather than the flat planform.
GAME_SPIN = 205

# ── layout ───────────────────────────────────────────────────────────────────
PAD = 18
HEADER_H = 70
HERO_PX = 130
GAME_PX = 40
MAG = 3

BG_TOP = (20, 22, 40)
BG_BOT = (34, 28, 52)
CARD_BG = (16, 17, 34)
CARD_EDGE = (96, 102, 140)
TEXT = (236, 238, 250)
SUB = (152, 158, 192)

DAY_TOP = (150, 200, 240)
DAY_BOT = (206, 230, 248)
NIGHT_TOP = (18, 20, 46)
NIGHT_BOT = (34, 26, 56)

CARD_W, CARD_H = 700, 470
SHEET_W = PAD + CARD_W + PAD
SHEET_H = HEADER_H + PAD + CARD_H + PAD

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(BG_TOP[i] + (BG_BOT[i] - BG_TOP[i]) * t) for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 28, bold=True)
F_SUB = pygame.font.SysFont("Arial", 14)
F_NAME = pygame.font.SysFont("Arial", 20, bold=True)
F_FEAT = pygame.font.SysFont("Arial", 13)
F_TAG = pygame.font.SysFont("Arial", 12, bold=True)

sheet.blit(F_TITLE.render("Skybit — Secret JET FIGHTER · RETRO CHROME · Round 2 (ship-ready)", True, TEXT), (PAD, 14))
sheet.blit(F_SUB.render(
    "V3 · BLUE-ANGEL TRIM converged to one production build. Value-band chrome · single blue spine · V4 anti-glare panel · dark belly. HERO 130px · 40px smooth + NEAREST x3 (level / dive) · DAY and NIGHT.",
    True, SUB), (PAD, 46))


def _grad_rect(target, rect, top, bot, radius=10):
    g = pygame.Surface((rect.w, rect.h))
    for y in range(rect.h):
        t = y / max(1, rect.h)
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(g, col, (0, y), (rect.w, y))
    mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=radius)
    g = g.convert_alpha()
    g.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    target.blit(g, rect.topleft)


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


LEVEL = GAME_SPIN
DIVE = GAME_SPIN - 32

cx, cy = PAD, HEADER_H + PAD
card = pygame.Rect(cx, cy, CARD_W, CARD_H)
pygame.draw.rect(sheet, CARD_BG, card, border_radius=14)
pygame.draw.rect(sheet, CARD_EDGE, card, 2, border_radius=14)

sheet.blit(F_NAME.render("V3 · BLUE-ANGEL TRIM — production", True, TEXT), (cx + 16, cy + 12))
sheet.blit(F_FEAT.render(
    "value-band chrome (hot top / hard break / dark belly) · single blue spine on the break · V4 anti-glare matte · saturated canopy dot · swept · big bubble",
    True, SUB), (cx + 16, cy + 38))

# ── Hero: two big 130px reads on a split day | night ground ──
hero_panel = pygame.Rect(cx + 16, cy + 64, 300, 200)
_grad_rect(sheet, pygame.Rect(hero_panel.x, hero_panel.y, hero_panel.w // 2, hero_panel.h),
           DAY_TOP, DAY_BOT)
_grad_rect(sheet, pygame.Rect(hero_panel.x + hero_panel.w // 2, hero_panel.y,
                              hero_panel.w - hero_panel.w // 2, hero_panel.h),
           NIGHT_TOP, NIGHT_BOT)
hero_day = smooth(0, LEVEL, HERO_PX)
sheet.blit(hero_day, hero_day.get_rect(center=(hero_panel.x + hero_panel.w // 4, hero_panel.centery)))
hero_night = smooth(0, LEVEL, HERO_PX)
sheet.blit(hero_night, hero_night.get_rect(center=(hero_panel.x + 3 * hero_panel.w // 4, hero_panel.centery)))
sheet.blit(F_TAG.render("HERO 130px   day | night", True, (40, 44, 60)),
           (hero_panel.x + 8, hero_panel.bottom - 20))

# ── Hero detail callout (right of hero): a single 130px dive on day ──
det_panel = pygame.Rect(cx + 332, cy + 64, 352, 200)
_grad_rect(sheet, det_panel, DAY_TOP, DAY_BOT)
hero_dive = smooth(1, DIVE, HERO_PX)
sheet.blit(hero_dive, hero_dive.get_rect(center=det_panel.center))
sheet.blit(F_TAG.render("HERO 130px   DAY dive — belly-to-sky contrast check", True, (40, 44, 60)),
           (det_panel.x + 8, det_panel.bottom - 20))

# ── Truth-test rows: DAY then NIGHT, each smooth 40px + NEAREST x3 (level/dive) ──
rx = cx + 16
rw = CARD_W - 32
for ri, (label, top, bot, txt) in enumerate((
        ("DAY", DAY_TOP, DAY_BOT, (40, 44, 60)),
        ("NIGHT", NIGHT_TOP, NIGHT_BOT, (200, 206, 235)))):
    ry = cy + 276 + ri * 92
    panel = pygame.Rect(rx, ry, rw, 86)
    _grad_rect(sheet, panel, top, bot)
    sheet.blit(F_TAG.render(label, True, txt), (panel.x + 8, panel.y + 5))
    sheet.blit(F_TAG.render("40px smooth (level / dive)          NEAREST x3 — honest gameplay read (level / dive)", True, txt),
               (panel.x + 120, panel.y + 5))

    g_level = smooth(2, LEVEL, GAME_PX)
    sheet.blit(g_level, g_level.get_rect(center=(panel.x + 60, panel.y + 50)))
    g_dive = smooth(1, DIVE, GAME_PX)
    sheet.blit(g_dive, g_dive.get_rect(center=(panel.x + 130, panel.y + 50)))

    n_level = nearest40(2, LEVEL, MAG)
    sheet.blit(n_level, n_level.get_rect(center=(panel.x + 360, panel.y + 50)))
    n_dive = nearest40(1, DIVE, MAG)
    sheet.blit(n_dive, n_dive.get_rect(center=(panel.x + 560, panel.y + 50)))

out_path = os.path.join(_here, "round_2.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
